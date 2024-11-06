import os
import numpy
import pyNastran

def AVLtxtToBDF(txtfilename: str,bdf_folderpath: str,bdffilename: str,iterationNumber: int,apparentWindSpeed: float,kicker: float, cunningham: float, outhaul: float):
    # Read initial displacement from BDF file
    cPath = "C:"
    pkg_path = os.path.join(cPath,'/Users/matth/Documents/University/RP3/pyNastran-main')

    #sail_path = os.path.join(cPath,'/Users/matth/Documents/Inventor/ILCA7/Sail/ILCA7_Sail5/InCAD/FEA/For MSC')
    bdf_filename = os.path.join(bdf_folderpath,bdffilename)
    print('pkg_path ',pkg_path, '\n')
    print(bdf_filename)


    from pyNastran.bdf.bdf import BDF
    model = BDF()
    model.read_bdf(bdf_filename, encoding='latin1')

    #print(model.get_bdf_stats())

    # Read AVL Force Outputs
    AVLPath = os.path.join(cPath,'/Users/matth/Documents/University/RP3/AVL')
    AVLforcesFile = os.path.join(AVLPath,txtfilename)
    aeroForces = open(AVLforcesFile, "r") # If this line gives an error - the AVL input file did not work
    avltext = aeroForces.readlines()
    # Define aerofoil discretisation
    surfaces = 1
    chordwise = 11
    spanwise = int((len(avltext)-19)/(chordwise+11))
    # Read .txt file
    forces = numpy.zeros((surfaces,spanwise,chordwise,7))
    headers = list()
    for surface in range(0,surfaces):
        if surface == 0:
            blockStart = 19
        else:
            blockStart = 19+(10+chordwise)*spanwise
        for strip in range(0,spanwise):
            headers = avltext[blockStart+9]
            for point in range(0,chordwise):
                tableRow = avltext[(blockStart+10+point)]
                forces[surface,strip,point,0] = tableRow[3:5]
                for column in range (0,6):
                    if tableRow[5+12*column:17+12*column] == '  **********':
                        forces[surface,strip,point,column+1]=0
                    else:
                        forces[surface,strip,point,column+1] = tableRow[5+12*column:17+12*column]

                '''if point == 0: # This is IMPORTANT +> numerically integrates dCp to Cp based on the size of each panel.
                    forces[surface,strip,point,6] = forces[surface,strip,point,6]*(forces[surface,strip,point,1])
                else:
                    forces[surface,strip,point,6] = forces[surface,strip,point,6]*(forces[surface,strip,point,1]-forces[surface,strip,point-1,1]) # Cp = dCp*(xcurrent-xprevious)'''
            blockStart = blockStart+11+chordwise


    # Generate matrix of points and Fx, Fy, Fz
    # Find interpolated values on Nastran grid (while loop) how to search for closest three points?

    #AVLarray = read_AVL_file # [x,y,z,Fx,Fy,Fz;...]
    BDFarray = model.nodes[913].xyz

    #gridPoints = scipy.spatial.KDTree()


    # Apply forces in BDF file

    bdffilename_out = 'ilca7_%s.BDF' % (iterationNumber+1)
    bdf_path_out = os.path.join(bdf_folderpath,bdffilename_out)

    # Add forces from AVL to BDF file (while loop)
    ids = list(model.element_ids)
    dist = list()
    nodes = numpy.zeros((4,4))
    pressapply = list(model.element_ids)
    delkey = []
    for elementid in model.element_ids:
        if model.elements[elementid].pid ==1:
            element = model.elements[elementid]
            avgnodeXYZ = [0,0,0]
            for i in range(0,4):
                try:
                    nodes[i,0] = element.node_ids[i]
                    nodes[i,1:4] = model.nodes[nodes[i,0]].xyz
                    elementtype = 4
                except:
                    nodes[i,0] = 0
                    elementtype = 3
            avgnodeXYZ = [sum(nodes[0:elementtype,1])/elementtype,sum(nodes[0:elementtype,2])/elementtype,sum(nodes[0:elementtype,3])/elementtype]
            # Search for nearest control point
            dist = numpy.zeros(forces[0,:,:,1].size)
            i=0
            cpxyz = numpy.zeros(3)
            for strip in range(0,spanwise):
                for cpoint in range(0,forces[0,strip,:,1].size):
                    cpxyz[0] = -forces[0,strip,:,3][cpoint]*1000
                    cpxyz[1] = forces[0,strip,:,2][cpoint]*1000
                    cpxyz[2] = forces[0,strip,:,1][cpoint]*1000
                    dist[i] = numpy.sqrt(sum((avgnodeXYZ[1:3]-cpxyz[1:3])**[2,2]))
                    i+=1
            closestpress1 = dist.argsort()[0]
            closestpress2 = dist.argsort()[1]
            totdist = dist[closestpress1]+dist[closestpress2]

            ''' Not required for p calculation
            if int(numpy.floor(closestpress/chordwise)) == 0:
                stripWidth = forces[0,int(numpy.floor(closestpress/chordwise))+1,0,2]-forces[0,int(numpy.floor(closestpress/chordwise)),0,2]
            else:
                stripWidth = forces[0,int(numpy.floor(closestpress/chordwise)),0,2]-forces[0,int(numpy.floor(closestpress/chordwise))-1,0,2]
            '''

            epress1 = (dist[closestpress2]/totdist)*(-0.000001*forces[0,int(numpy.floor(closestpress1/chordwise)),int(closestpress1-numpy.floor(closestpress1/chordwise)*chordwise),6]*0.5*1.225*(apparentWindSpeed**2))
            epress2 = (dist[closestpress1]/totdist)*(-0.000001*forces[0,int(numpy.floor(closestpress2/chordwise)),int(closestpress2-numpy.floor(closestpress2/chordwise)*chordwise),6]*0.5*1.225*(apparentWindSpeed**2))
            epress = epress1+epress2
            pressapply[elementid-1] = pyNastran.bdf.cards.loads.static_loads.PLOAD4(2,elementid,epress,None,None,0,None,'SURF',"Aero")
        else:
            try: # this is filthy but I can't figure out how to delete the pressures from the cbar elements any other way
                while model.elements[pressapply[elementid-1]].pid != 1:
                    del(pressapply[elementid-1])
            except:
                pass
    model.loads[2] = pressapply

    # Add control forces
    totalForce = numpy.sqrt(numpy.power((kicker/(5*numpy.sqrt(2))),2)+numpy.power(outhaul,2)) # corrects for moment arm and for angle of kicker attachment
    forceDirection = (numpy.array([0,-kicker/5,0])+numpy.array([0,0,outhaul]))/numpy.array([totalForce,totalForce,totalForce])
    
    model.loads[1] = [pyNastran.bdf.cards.loads.static_loads.FORCE(1,279,totalForce/3,forceDirection,0,"1")]
    model.loads[3] = [pyNastran.bdf.cards.loads.static_loads.FORCE(1,567,totalForce/3,forceDirection,0,"1")]
    model.loads[4] = [pyNastran.bdf.cards.loads.static_loads.FORCE(1,568,totalForce/3,forceDirection,0,"1")]

    model.loads[5] = [pyNastran.bdf.cards.loads.static_loads.FORCE(4,318,cunningham,[0,-1,0],0,"4")]

    model.load_combinations[3] = [pyNastran.bdf.cards.loads.static_loads.LOAD(3,1.,[1.,1.,1.],[1,2,4])]
    model.load_combinations[5] = [pyNastran.bdf.cards.loads.static_loads.LOAD(5,1.,[1.,1.],[1,4])]
    pass

    model.write_bdf(bdf_path_out)

