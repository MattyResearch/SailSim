import os
import numpy

def op2ToAVL(bdffilename: str,op2filename: str,AVLfilename: str,iterationNumber:int,TWA:int,TWS:int,mainsheet:float,outhaul:float):
    # Read initial positions from BDF file
    cPath = "C:"
    pkg_path = os.path.join(cPath,'/Users/matth/Documents/University/RP3/pyNastran-main')

    sail_path = os.path.join(cPath,'/Users/matth/Documents/Inventor/ILCA7/Sail/ILCA7_Sail7/InCAD/FEA/PythonRuns')
    bdf_filename = os.path.join(sail_path,bdffilename)
    print('pkg_path ',pkg_path, '\n')
    print(bdf_filename)


    from pyNastran.bdf.bdf import BDF
    model = BDF()
    model.read_bdf(bdf_filename, encoding='latin1')

    #print(model.get_bdf_stats())

    #nodesXYZ = numpy.array(keyvallist)
    nodesXYZ = numpy.ones((model.nnodes,3),dtype=float)
    k=0
    for i in model.nodes.items():
        nodesXYZ[k][0:3]= model.nodes[i[1].nid].xyz
        k=k+1

    #print('%s' % nodesXYZ[0:5])
    pass
    # Read displacements from op2

    op2_filename = os.path.join(sail_path,op2filename)

    from pyNastran.op2.op2 import OP2
    results = OP2()
    results.read_op2(op2_filename)

    nodalDisp = results.displacements[1]
    disp_headers = nodalDisp.get_headers()
    #print('disp_headers = %s' % disp_headers)
    nnodes = nodalDisp.node_gridtype.shape[0]
    txyz = nodalDisp.data[0,:,:3]
    txyz_mag = numpy.linalg.norm(txyz,axis=1)

    # Validation that txyz can be extracted correctly

    #txyz_max = txyz.max()
    #txyz_mag_max = txyz_mag.max()
    #inid_max = numpy.where(txyz == txyz_max)[0]
    #inid_mag_max = numpy.where(txyz_mag == txyz_mag_max)[0]
    #all_nodes = nodalDisp.node_gridtype[:,0]
    #max_nodes = all_nodes[inid_max]
    #print('max displacement=%s max nodes=%s' % (txyz_max,max_nodes))
    #max_nodes = all_nodes[inid_mag_max]
    #print('max displacement magnitude=%s max nodes=%s' % (txyz_mag_max,max_nodes))

    # Calculate deformed co-ords (txyz only initially)
    cornerNodes = [560,555,559]
    cornerDisp = nodalDisp.data[0,cornerNodes,:3]

    #print('%s' % txyz[0:5])

    dfrmd_coords = nodesXYZ + txyz
    
    #print('%s' % dfrmd_coords[0:5])

    # Find apparent wind angle, wind speed, and twist of the wing required
    FResults = results.spc_forces[1]
    noWind = results.spc_forces[2]
    outhaulForces = model.loads[1][0]
    forcesOut = ([1,2,3])
    tangentChord = sum(FResults.data[0,:,2])-sum(noWind.data[0,:,2]) # sum of forces along chordline (+ve z is backwards)
    perpChord = sum(FResults.data[0,:,0])-sum(noWind.data[0,:,0]) # sum of forces perpendicular to chordline (+ve x is windward)
    forcesOut[2] = sum((FResults.data[0,:,0]-noWind.data[0,:,0])*nodesXYZ[:,1]/1000) # Sum the Aerodynamic Force*distance to find moments

    forcesOut[0] = tangentChord*numpy.cos(mainsheet*numpy.pi/180) + perpChord*numpy.sin(mainsheet*numpy.pi/180) # thrust
    forcesOut[1] = -tangentChord*numpy.sin(mainsheet*numpy.pi/180) + perpChord*numpy.cos(mainsheet*numpy.pi/180) # drag (leeward force)
    forcesOut[2] = forcesOut[2] # heeling moment

    if forcesOut[0] > 0:
        Vb = numpy.sqrt(forcesOut[0]/80)*2.57
    else:
        Vb = -numpy.sqrt(numpy.abs(forcesOut[0])/80)*2.57
    print("\nBoat Speed (ms-1) = %s\n\n" % Vb)
    if Vb > 3*TWS:
        print("*\n*\n*\n*\n*\n*\n*\n*\n*\n*\n*\n*\n*\n*\nBoatspeed too large - not converged*\n*\n*\n*\n*\n*\n*\n*\n*\n*\n*\n*\n*\n*\n")
        Vb =0.1
    alignedSpeed = Vb*numpy.cos(mainsheet*numpy.pi/180)+TWS*numpy.cos((TWA-mainsheet)*numpy.pi/180)
    normalSpeed = TWS*numpy.sin((TWA-mainsheet)*numpy.pi/180)-Vb*numpy.sin(mainsheet*numpy.pi/180)
    VApparent = numpy.sqrt(numpy.power(alignedSpeed,2)+numpy.power(normalSpeed,2))
    ThetaApparent = numpy.arctan(normalSpeed/alignedSpeed)*180/numpy.pi
    
    TWSTip = TWS*2 # Simple approximation for wind shear layer
    alignedSpeed = Vb*numpy.cos(mainsheet*numpy.pi/180)+TWSTip*numpy.cos((TWA-mainsheet)*numpy.pi/180)
    normalSpeed = TWSTip*numpy.sin((TWA-mainsheet)*numpy.pi/180)-Vb*numpy.sin(mainsheet*numpy.pi/180)
    VApparentTip = numpy.sqrt(numpy.power(alignedSpeed,2)+numpy.power(normalSpeed,2))
    ThetaApparentTip = numpy.arctan(normalSpeed/alignedSpeed)*180/numpy.pi
    ThetaDifference = ThetaApparentTip-ThetaApparent

    pass
    # Generate section cut co-ords (to generate camber line .dat file)
    from pyNastran.converters.avl.avl import AVL
    AVLPath = os.path.join(cPath,'/Users/matth/Documents/University/RP3/AVL')
    #prev_AVL = 'ilca7_%s.AVL' % iterationNumber-1
    #shutil.copy(os.path.join(AVLPath,prev_AVL),os.path.join(AVLPath,AVLfilename))
    AVLf = os.path.join(AVLPath, AVLfilename)
    AVLprev = os.path.join(AVLPath,'ilca7_%s.avl'% (iterationNumber-1))
    AVLwrite = AVL()
    if iterationNumber > 1:
        AVLwrite.read_avl(AVLprev)
    else:
        AVLwrite.read_avl(AVLf) # If an error occurs here, check the ilca7_1.avl file for corruption.

    AVLinputFile = open(AVLf, "w")

    headNode = 560
    headCoords = dfrmd_coords[headNode-1:headNode,:3]
    clewCoords = dfrmd_coords[555,:3]
    cutHeights = [0.02,(clewCoords[1]-1)/headCoords[:,1],(clewCoords[1]+300)/headCoords[:,1],0.5,0.9]
    Nspan = 2
    Sspace = [2,1,0,-2,-2]
    for sectionid in range(0,len(cutHeights)):
        #Section cut at z/b = 0.5 (half span)
        Nspan = 2
        #   Define the plane
        planeHeight = cutHeights[sectionid]
        n = [0,1,0]
        p0 = headCoords*planeHeight #p0 is a point on the plane, n is the plane normal vector

        #   Points are above the plane when p0->P dot n is greater than 0.
        a=0
        b=0
        above = numpy.zeros((model.nnodes,5),dtype=float)
        below = numpy.zeros((model.nnodes,5),dtype=float)

        for i in range(1,nnodes+1,1):
            if numpy.dot((dfrmd_coords[i-1:i][:]-p0),n)[0] >= 0:
                above[a][0:3] = dfrmd_coords[i-1][:]
                above[a][3:4] = numpy.dot((dfrmd_coords[i-1:i][:]-p0),n)
                above[a][4:5] = model.nodes[i].nid
                a=a+1
            else:
                below[b][0:3] = dfrmd_coords[i-1][:]
                below[b][3:4] = numpy.dot((dfrmd_coords[i-1:i][:]-p0),n)
                below[b][4:5] = model.nodes[i].nid
                b=b+1
        x = above.shape[0]
        rows = range(0,a)
        above = above[rows][:]

        x = below.shape[0]
        rows = range(0,b)
        below = below[rows][:]

        #   Find the closest n points to the plane (ensures all the whole aerofoil is selected)
        npoints=50
        maxdist = 150 #max distance from plane (mm)
        above = above[above[:,3].argsort()]
        closestAbove = above[0:npoints][:]
        if a == 0 | b == 0:
            Vb = 5000
            return dfrmd_coords, forcesOut, VApparent, ThetaApparent, VApparentTip, Vb
        delkey= list()
        for i in range(0,closestAbove[:,0].size):
            if abs(closestAbove[i,3]) > maxdist:
                delkey.append(i)
        closestAbove = numpy.delete(closestAbove,delkey,0)
        delkey.clear()

        below = below[(-below[:,3]).argsort()]
        closestBelow = below[0:npoints][:]
        for i in range(0,closestAbove[:,0].size):
            if abs(closestAbove[i,3]) > maxdist:
                delkey.append(i)
        closestBelow = numpy.delete(closestBelow,delkey,0)

        if closestBelow[:,0].size < 50 or closestAbove[:,0].size < 50:
            if int(numpy.floor(closestAbove[:,0].size*0.75)) < 1:
                npoints = 1
            else:
                npoints = closestAbove[:,0].size

        if closestAbove[:,0].size == 0 or closestBelow[:,0].size == 0:
            Vb = 5000
            return dfrmd_coords, forcesOut, VApparent, ThetaApparent, VApparentTip, Vb

        #   Once all the crossing vectors have been found, find the intersection co-ords
        pos=0
        l0 = numpy.zeros((1,3),dtype=float)
        p = numpy.zeros((npoints*2,3),dtype=float)
        for i in range(0,npoints):
            l0 = closestAbove[i][:3]
            # sort belowPoints by distance to the above node
            dist = numpy.zeros(closestBelow[:,0].size)
            for k in range(0,closestBelow[:,0].size):
                dist[k] = numpy.sqrt(sum(numpy.power((closestBelow[k][:3] - l0),[2,2,2])))
            closestNodes = closestBelow[dist.argsort()]
            if closestBelow[:,0].size < 2:
                closestNodes = numpy.zeros((2,3),dtype=float)
                closestNodes[0,:] = closestBelow[0,:3]
                closestNodes[1,:] = closestBelow[0,:3]
            for intsct in range(0,2):
                l = closestNodes[intsct][:3] - l0
                a = (numpy.dot((p0-l0),n))/numpy.dot(l,n) #a is the multiplier for the vector line equation p=l0+l*a, l0 is a point on the plane and l is the parallel vector
                p[pos] = l0+l*a
                pos=pos+1
        
        p = p[p[:,2].argsort()]
        # this next section of code is intended to cull any very close points, within a specified tolerance (mm), to avoid spline fitting issues in AVL
        culled = True
        while culled == True:
            chordcheck = 1
            culled = False
            while chordcheck < (p[:,2].size):
                if numpy.abs((p[chordcheck,2] - p[chordcheck-1,2])) < 20:
                    p = numpy.delete(p,chordcheck,0)
                    chordcheck = chordcheck-1
                    culled = True
                chordcheck = chordcheck+1

        ''' # This section is not required anymore - AVL leading edge interpretation has been solved
        # Check for small number of points in airfoil shape - add linear interpolation if required
        while p[:,0].size < 16:
            xzVal = numpy.zeros([p[:,0].size,3])
            for pointCounter in range(0,p[:,0].size-1):
                xzVal[pointCounter] = numpy.array([(p[pointCounter,0]+p[pointCounter+1,0])/2,(p[pointCounter,1]+p[pointCounter+1,1])/2,(p[pointCounter,2]+p[pointCounter+1,2])/2])
            p = numpy.append(p,xzVal,axis=0)
        # Rotation required to match AVL input
        # .dat file uses xyz co-ords
        p = p[p[:,2].argsort()]
        '''

        pOut = numpy.zeros((npoints*2,3),dtype=float)
        if p[:,0].size > 200:
            for i in range(1,201):
                pOut[i-1] = p[int(numpy.floor(p[:,0].size/200))*i-1,:3]
        else:
            pOut = p
        pass

        # Write co-ords to .dat file
        # Includes transformation: z-> x values for aerofoil, x values reflected in z=0 plane
        sectionPath = os.path.join(AVLPath, 'sect%s.dat' % sectionid)
        print(sectionPath)
        #fileOut = print('     %s    %s\n' % (pOut[:,2][:],-pOut[:,0][:]))
        sect1 = open(sectionPath, "w")

        for i in range(pOut[:,0].size-1,-1,-1):
            if pOut[:,2][i] == 0:
                outStringx = '0.000000' # required for the format of the .dat file
            else:
                outStringx = '%s' % pOut[:,2][i]
            outStringx = outStringx[:8] if len(outStringx) > 8 else outStringx
            if pOut[:,0][i] == 0:
                outStringy = '0.000000'
            else:
                outStringy = '%s' % -pOut[:,0][i]
            outStringy = outStringy[:8] if len(outStringy) > 8 else outStringy
            sect1.write('     %s    %s\n' % (outStringx,outStringy))
        for i in range(1,pOut[:,0].size):
            if pOut[:,2][i] == 0:
                if outStringx == '0.000000': # these two if statements check if we would be repeating a leading edge point, which leads to an uninterpretable .dat
                    i+=1
                else:
                    outStringx == '0.000000'
            else:
                outStringx = '%s' % pOut[:,2][i]
            outStringx = outStringx[:8] if len(outStringx) > 8 else outStringx
            if pOut[:,0][i] == 0:
                outStringy = '0.000000'
            else:
                outStringy = '%s' % -pOut[:,0][i]
            outStringy = outStringy[:8] if len(outStringy) > 8 else outStringy
            sect1.write('     %s    %s\n' % (outStringx,outStringy))
        sect1.close()

        # Implement yaw rate (due to wind shear layer AWA + due to lift correction) based on ThetaApparent and VApparent
        '''thetaTip = 4*ThetaApparentTip
        if thetaTip > 90:
            thetaTip = 90
        '''
        # Ainc is purely structural and due to the apparent wind angles. Wind shear layer is implemented as a yaw rate
        Ainc = (planeHeight-0.5)*(ThetaApparentTip-ThetaApparent)

        # Write .AVL file with section co-ords
        header = 'Sail \n'
        control = '#Mach\n%s\n#IYsym   IZsym   Zsym\n%s       %s        %.1g\n#Sref    Cref    Bref\n%.2g    %.2g    %.2g\n#Xref    Yref    Zref\n%.2g   %.2g  %.2g' % (AVLwrite.mach,AVLwrite.sym_iy,AVLwrite.sym_iz,AVLwrite.symz,AVLwrite.sref,AVLwrite.cref,AVLwrite.bcref,AVLwrite.xref,headCoords[0,1]*0.5/1000,AVLwrite.zref)#headCoords*0.5/1000
        surface1 = '\nSURFACE\nWing\n#Nchordwise  Cspace   Nspanwise   Sspace\n%s          %.1g                  \nANGLE\n%s\n' % (11, 1,0)
        if sectionid < 2:
            Nspan = 1
        if sectionid == 0:
            AVLinputFile.write('%s' % header)
            AVLinputFile.write('%s' % control)
            AVLinputFile.write('%s' % surface1)
            sectionadd = '%.2f   %.2f   %.2f   %.2f   %.2f %.2f %.2f' % (0,0,0,0,-0.5*(ThetaApparentTip-ThetaApparent),1, Sspace[sectionid])
            AVLinputFile.write('\nSECTION\n%s\nAFILE\n'%sectionadd+AVLPath+'/sect%s.dat' % sectionid)
        
        mastBend = True
        if mastBend:
            sectionadd = '%.2f   %.2f   %.2f   %.2f   %.2f %.2f %.2f' % (pOut[0,2]/1000,pOut[0,1]/1000,-pOut[0,0]/1000,abs(max(pOut[:,2])-min(pOut[:,2]))/1000,Ainc,Nspan, Sspace[sectionid]) # experimenting with mast bending unconstrained
        else:
            sectionadd = '%.2f   %.2f   %.2f   %.2f   %.2f %.2f %.2f' % (pOut[0,2]/1000,pOut[0,1]/1000,0,abs(max(pOut[:,2])-min(pOut[:,2]))/1000,Ainc,Nspan, Sspace[sectionid])
        AVLinputFile.write('\nSECTION\n%s\nAFILE\n'%sectionadd+AVLPath+'/sect%s.dat' % sectionid)
    #AVLinputFile.flush()
    #os.fsync(AVLinputFile.fileno())
    planeHeight = 1
    Ainc = (planeHeight-0.5)*(ThetaApparentTip-ThetaApparent)
    if mastBend:
        tipadd = '%.2f   %.2f   %.2f   %.2f   %.2f %.2f %.2f' % (headCoords[0,2]/1000,headCoords[0,1]/1000,-headCoords[0,0]/1000,0,Ainc,Nspan,Sspace[sectionid])
    else:
        tipadd = '%.2f   %.2f   %.2f   %.2f   %.2f %.2f %.2f' % (headCoords[0,2]/1000,headCoords[0,1]/1000,0,0,Ainc,Nspan,Sspace[sectionid])
    AVLinputFile.write('\nSECTION\n%s\nAFILE\n'%tipadd+AVLPath+'/sect%s.dat\n' % sectionid)
    AVLinputFile.close()

    ThetaApparent = 0.5*(ThetaApparent+ThetaApparentTip) # as seen by half span of sail
    if ThetaApparent > 50:
        print("***\n***\n***\n***\nLarge AoA, check convergence\n***\n***\n***\n***\n")
    #    ThetaApparent = 50
    print("\nBoat Speed = %s\n" % Vb)
    return dfrmd_coords, forcesOut, VApparent, ThetaApparent, VApparentTip, Vb
    pass
# Run this geometry in AVL
""" import subprocess as sp
AVLexe = os.path.join(AVLPath,'avl.exe')
try:
    ps = sp.Popen(AVLexe,stdin=sp.PIPE, stdout=None, stderr=None)
except OSError as e:
    print('error opening AVL.exe')

ps.stdin.write(b'load\n')
ps.stdin.write(b'pyNastranOut2 ')
ps.stdin.write(b"\n")
ps.stdin.write(b'oper'+b'\n')
ps.stdin.write(b'F'+b'\n')
ps.stdin.write(b'alpha20'+b'\n')
ps.stdin.write(b'I'+b'\n')
ps.stdin.write(b'X'+b'\n')
ps.stdin.write(b'FE'+b'\n')
ps.stdin.write(b'forcesOut.txt'+b'\n')
ps.stdin.write(b'\n')
ps.stdin.write(b'quit'+b'\n') """


# (Optional) Edit run case to perfectly trim leading edge

pass