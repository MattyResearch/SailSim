import os
import numpy
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from nastranRun import run_analysis
from structureToAero import op2ToAVL
from avlRun import run_aero
from aeroToStructure import AVLtxtToBDF
import time
import shutil

# Independent variables
trueWindAngle = 44.5  # true wind angle in degrees (centreline of boat to prevailing wind, 0 is directly upwind)
TWS = 5             # True wind speed in ms-1
mainsheet = 8.124984       # Sheeting angle in degrees
kicker = 1746.8732160000004          # Kicker tension (N)
cunningham = 559.6800000000001      # Cunningham tension (N)
outhaulT = 422.83079999999995     # Outhaul tension (N)
timing = False      # are we timing the code run?

def steadyCase(trueWindAngle,TWS,mainsheet,kicker,cunningham,outhaulT,conPlot,writeOutput,fileInput,timing):
    # Define all file locations required
    start_time = time.perf_counter()
    times = numpy.array([0,0,0,0,0],float) # nastran,str2aero,AVL,aero2str,total
    runfolder = 'C:\\Users\\matth\\Documents\\Inventor\\ILCA7\\Sail\\ILCA7_Sail7\\InCAD\\FEA\\PythonRuns'
    if writeOutput == None:
        writeOutput=False
        while (fileInput == None or fileInput == '.csv'):
            if input("Write output to file? (Y or N):") in ["y","Y","yes","Yes","YES"]:
                writeOutput = True
                fileInput = input("Output filename (saved in .bdf folder):")    
            else:
                fileInput = ''
                break
    if '.csv' not in fileInput:
        fileInput+='.csv'
    outputFileName = os.path.join(runfolder,fileInput)
    if conPlot == None:
        conPlot = False
        if input("Convergence plot? (Y or N):") in ["y","Y","yes","Yes","YES"]:
            conPlot = True # Convergence plot marker

    max_iterations = 17
    tolerance = 10

    convergence_tracking = numpy.zeros([max_iterations])
    Vb_tracking = numpy.zeros([max_iterations])
    displacement_tracking = numpy.zeros([max_iterations])

    if conPlot:
        fig, ax1 = plt.subplots(1,2) # plot the convergence
        fig.set_figwidth(10)
        ax1[0].set_yscale('log')
        plt.show(block=False)

    for iterationNumber in range(1,max_iterations):
        # begins at 1, up to max of 100 (limit to avoid endless looping)
        bdffilename = 'ilca7_%s.BDF' % iterationNumber
        op2filename = 'ilca7_%s.op2' % iterationNumber
        AVLfilename = 'ilca7_%s.avl' % iterationNumber
        txtfilename = 'ilca7_%s.txt' % iterationNumber

        if timing:
            preFunc_time = time.perf_counter()
        run_analysis(bdf_folderpath=runfolder,bdf_name=bdffilename)
        if timing:
            times[0]+=time.perf_counter()-preFunc_time

        op21name = 'ilca7_%s.op2.1' % iterationNumber
        f061name = 'ilca7_%s.f06.1' % iterationNumber
        log1name = 'ilca7_%s.log.1' % iterationNumber
        f041name = 'ilca7_%s.f04.1' % iterationNumber
        if os.path.exists(os.path.join(runfolder,op21name)):
            os.remove(os.path.join(runfolder,op21name))
        if os.path.exists(os.path.join(runfolder,f061name)):
            os.remove(os.path.join(runfolder,f061name))
        if os.path.exists(os.path.join(runfolder,f041name)):
            os.remove(os.path.join(runfolder,f041name))
        if os.path.exists(os.path.join(runfolder,log1name)):
            os.remove(os.path.join(runfolder,log1name))

        if timing:
            preFunc_time = time.perf_counter()
        dfrmd_coords, forcesOut, VApparent, ThetaApparent, VApparentTip, boatspeed = op2ToAVL(bdffilename=bdffilename,op2filename=op2filename,AVLfilename=AVLfilename,iterationNumber=iterationNumber,TWA=trueWindAngle,TWS=TWS,mainsheet=mainsheet,outhaul=outhaulT)
        if timing:
            times[1] += time.perf_counter()-preFunc_time

        if boatspeed > 5*TWS:
            print("***\n***\n***\n***\nAVL failure - boatspeed too great\n***\n***\n***\n***\n")
            convergedState = False
            outputArray = 'TWA_deg','TWS_ms-1','Mainsheet_deg','Kicker_N','Cunningham_N','Outhaul_N','Thrust_N','Leeward_Force_N','AeroMoment_Nm','AWA_deg','AWS_ms-1','AoA_deg','Vb_ms-1','VMG_ms-1',trueWindAngle,TWS,mainsheet,kicker,cunningham,outhaulT,'NaN','NaN','NaN','NaN','NaN','NaN','NaN',0
            times[4] = time.perf_counter()-start_time
            return boatspeed,ThetaApparent,convergedState,outputArray,times,iterationNumber
        # Check convergence (Using RMS value). If no convergence, store dfrmd_coords to new variable
        difference = numpy.zeros([50,3])
        displaced = numpy.zeros([50,3])

        if iterationNumber == 1:
            prev_dfrmd_coords = numpy.zeros(dfrmd_coords.shape)
        for i in range(0,49):
            difference[i,:3] = dfrmd_coords[i*19,:3] - prev_dfrmd_coords[i*19,:3]
            displaced[i,:3] = dfrmd_coords[i*19,:3]
        if iterationNumber == 1:
            RMS = tolerance+1
        else:
            RMS = numpy.sqrt(sum(sum(difference**2))/difference[:,0].size)
        RMSdisp = numpy.sqrt(sum(sum(displaced**2))/displaced[:,0].size)
        displacement_tracking[iterationNumber-1] = RMSdisp
        convergence_tracking[iterationNumber-1] = RMS
        Vb_tracking[iterationNumber-1] = boatspeed*numpy.cos(trueWindAngle*numpy.pi/180)
        
        
        if conPlot:
            ax1[0].plot(numpy.array(range(1,iterationNumber+1)),convergence_tracking[:iterationNumber])
            ax1[0].plot(numpy.array(range(1,iterationNumber+1)),displacement_tracking[:iterationNumber])
            ax1[0].set_xlim(1, iterationNumber)
            ax1[0].set_ylim(min(0.1,min(convergence_tracking[:iterationNumber])), max([max(convergence_tracking),max(displacement_tracking)])+10)
            ax1[0].grid(True,'both','both')

            ax1[1].plot(numpy.array(range(1,iterationNumber+1)),Vb_tracking[:iterationNumber]) # plot VMG
            ax1[1].set_xlim(1,iterationNumber)
            ax1[1].set_ylim(0, max(Vb_tracking)*1.1)
            ax1[1].grid(True,'both','both')
            plt.draw()
            plt.pause(0.01)

        if convergence_tracking[iterationNumber-2] < tolerance and RMS < tolerance:
            break
        else: 
            prev_dfrmd_coords = dfrmd_coords
        print("\nRMS Displacement (mm) = %s\n\n" % RMS)
        
        avlstate = 1
        attempts = 0
        while avlstate == 1 and attempts < 2:
            if timing:
                preFunc_time = time.perf_counter()
            avlstate = run_aero(AVLfilename=AVLfilename,txtfilename=txtfilename,iterationNumber=iterationNumber,ThetaApparent=ThetaApparent,VApparentTip=VApparentTip)
            if timing:
                times[2]+=time.perf_counter()-preFunc_time
            attempts +=1
        if attempts == 2:
            print("***\n***\n***\n***\nAVL failure\n***\n***\n***\n***\n")
            convergedState = False
            outputArray = 'TWA_deg','TWS_ms-1','Mainsheet_deg','Kicker_N','Cunningham_N','Outhaul_N','Thrust_N','Leeward_Force_N','AeroMoment_Nm','AWA_deg','AWS_ms-1','AoA_deg','Vb_ms-1','VMG_ms-1',trueWindAngle,TWS,mainsheet,kicker,cunningham,outhaulT,'NaN','NaN','NaN','NaN','NaN','NaN','NaN',0
            times[4]=time.perf_counter()-start_time
            return boatspeed,ThetaApparent,convergedState,outputArray,times,iterationNumber

        if timing:
            preFunc_time = time.perf_counter()
        AVLtxtToBDF(txtfilename=txtfilename,bdf_folderpath=runfolder,bdffilename=bdffilename,iterationNumber=iterationNumber,apparentWindSpeed=VApparent,kicker=kicker,cunningham=cunningham,outhaul=outhaulT)
        if timing:
            times[3]+=time.perf_counter()-preFunc_time

    if iterationNumber == max_iterations-1:
        print("\n------------------\nFinal Solution Not Converged\n------------------")
        convergedState = False
        
    else:
        convergedState = True
        print("\n------------------\nFinal Solution Converged After %s Iterations\n------------------" % iterationNumber)
        print("\nThrust    Leeward Force    Moment\n%.2fN     %.2fN          %.2fNm" % (forcesOut[0],forcesOut[1],forcesOut[2]))
        print("\nApparent Wind Speed (ms-1)     Apparent Wind Angle (deg)       Sail AoA (deg)\n%s              %s              %s\n\nBoat Speed (ms-1)        VMG (ms-1)\n%s       %s" % (VApparent,(ThetaApparent+mainsheet),ThetaApparent,boatspeed,boatspeed*numpy.cos(trueWindAngle*numpy.pi/180)))
        if writeOutput:
            outputFile = open(outputFileName,"w")
            outputFile.write('TWA_deg,TWS_ms-1,Mainsheet_deg,Kicker_N,Cunningham_N,Outhaul_N,Thrust_N,Leeward_Force_N,AeroMoment_Nm,AWA_deg,AWS_ms-1,AoA_deg,Vb_ms-1,VMG_ms-1;\n%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s;'%(trueWindAngle,TWS,mainsheet,kicker,cunningham,outhaulT,forcesOut[0],forcesOut[1],forcesOut[2],(ThetaApparent+mainsheet),VApparent,ThetaApparent,boatspeed,boatspeed*numpy.cos(trueWindAngle*numpy.pi/180)))
            outputFile.close
            print("Written to file %s" % fileInput)
        # DO NOT copy the converged state to initialise the next run case.
        #shutil.move(os.path.join(runfolder,'ilca7_%s.bdf'%iterationNumber),os.path.join(runfolder,'ilca7_1.bdf'))

    print("\nRMS Displacement (mm) = %s" % RMS)
    if conPlot:
        ax1[0].set_xlabel('Iteration Number')
        ax1[0].set_ylabel('RMS Displacement (mm)')
        ax1[0].set_title("Convergence Plot")
        ax1[0].set_xticks(numpy.arange(1,iterationNumber+1,1))

        ax1[1].set_xlabel('Iteration Number')
        ax1[1].set_ylabel('VMG (ms-1)')
        ax1[1].set_title('VMG Convergence')
        ax1[1].set_xticks(numpy.arange(1,iterationNumber+1,1))

        if __name__ == '__main__':
            plt.show(block=True)
        else:
            plt.show(block=False)
    
    if convergedState:
        outputArray = 'TWA_deg','TWS_ms-1','Mainsheet_deg','Kicker_N','Cunningham_N','Outhaul_N','Thrust_N','Leeward_Force_N','AeroMoment_Nm','AWA_deg','AWS_ms-1','AoA_deg','Vb_ms-1','VMG_ms-1',trueWindAngle,TWS,mainsheet,kicker,cunningham,outhaulT,forcesOut[0],forcesOut[1],forcesOut[2],(ThetaApparent+mainsheet),VApparent,ThetaApparent,boatspeed,boatspeed*numpy.cos(trueWindAngle*numpy.pi/180)
    else:
        outputArray = 'TWA_deg','TWS_ms-1','Mainsheet_deg','Kicker_N','Cunningham_N','Outhaul_N','Thrust_N','Leeward_Force_N','AeroMoment_Nm','AWA_deg','AWS_ms-1','AoA_deg','Vb_ms-1','VMG_ms-1',trueWindAngle,TWS,mainsheet,kicker,cunningham,outhaulT,'NaN','NaN','NaN','NaN','NaN','NaN','NaN',0
    times[4]=time.perf_counter()-start_time
    return boatspeed,ThetaApparent,convergedState,outputArray,times,iterationNumber
    
pass
if __name__ == '__main__':  
    steadyCase(trueWindAngle,TWS,mainsheet,kicker,cunningham,outhaulT,None,None,None,timing)
# Consider person of 70kg -> 700N -> Lever arm of 3.4m from pivot point required.. Not realistic, however this does NOT take into account the stability of the hull
# Also need to consider a twist value for the aerofoil - to capture the wind shear layer.
'''
Algorithm to follow:

1. Pre-work MUST be done to ensure no errors this includes:
1.1. Run the initial state BDF in Nastran to get op2 output (required for structureToAero.py)
1.2. Run the structureToAero to ensure a workable aero file is output. Rename to ilca7_1.AVL

2. Run structureToAero.py to interpret structure for AVL
3. Run avlRun to get pressures
4. Run aeroToStructure to apply pressures to structure
5. Run nastranRun to find displacements
6. Repeat until convergence - previous op2 file MUST be stored. Use two BDF objects.
'''