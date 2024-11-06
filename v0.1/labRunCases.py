# This file contains all the running cases required to execute the lab report. Comment/uncomment if different experiments are required.

import numpy
from quasiSteadyRun import steadyCase
import random

# Base variables
base_trueWindAngle = 45  # true wind angle in degrees (centreline of boat to prevailing wind, 0 is directly upwind)
base_TWS = 5             # True wind speed in ms-1
base_mainsheet = 12      # Sheeting angle in degrees
base_kicker = 1440       # Kicker tension (N)
base_cunningham = 480    # Cunningham tension (N)
base_outhaulT = 510      # Outhaul tension (N)

# Limit variables
TWA_lim = [20,90]
TWS_cases = [1,3,5,7,9,10]
mainsheet_lim = [0,45]
kicker_lim = [0, 2400]
cunningham_lim = [0, 800]
outhaulT_lim = [250,1000]

npoints = 15        # Number of points per graph

case = 2            # Experiment case selection

# Case 1 - fixed wind speed and true wind angle.
# Optimise individual parameters for maximum VMG
# Parameters go from minimum to maximum possible values, with fixed steps - 15 points per parameter/graph

varlist = ['mainsheet','kicker','cunningham','outhaulT']
outDict = dict()
if case == 1:
    for variable in varlist:
        outDict.update({variable:dict()})
        if variable == 'mainsheet':
            failures = 0
            for step in range(0,npoints+1):
                varyMain = mainsheet_lim[0]+(step/npoints)*(mainsheet_lim[1]-mainsheet_lim[0])
                attempts = 0
                convergedState = False
                while not convergedState and attempts < 1:
                    Vb,thetaA,convergedState,outDict[variable][step],times,iterations = steadyCase(base_trueWindAngle,base_TWS,varyMain,base_kicker,base_cunningham,base_outhaulT,False,True,'csvs\\EX1_mainsheet%.0f' % varyMain,False)
                    attempts +=1
                if attempts > 0 and not convergedState:
                    failures+=1
                if failures > 5:
                    break
        if variable == 'kicker': 
            failures = 0
            for step in range(0,npoints+1):
                varyKick = kicker_lim[0]+(step/npoints)*(kicker_lim[1]-kicker_lim[0])
                attempts = 0
                convergedState = False
                while not convergedState and attempts < 1:
                    Vb,thetaA,convergedState,outDict[variable][step],times,iterations = steadyCase(base_trueWindAngle,base_TWS,base_mainsheet,varyKick,base_cunningham,base_outhaulT,False,True,'csvs\\EX1_kicker%.0f' % varyKick,False)
                    attempts +=1
                if attempts > 0 and not convergedState:
                    failures+=1
                if failures > 5:
                    break
        if variable == 'cunningham': 
            failures = 0
            for step in range(0,npoints+1):
                varyCunn = cunningham_lim[0]+(step/npoints)*(cunningham_lim[1]-cunningham_lim[0])
                attempts = 0
                convergedState = False
                while not convergedState and attempts < 1:
                    Vb,thetaA,convergedState,outDict[variable][step],times,iterations = steadyCase(base_trueWindAngle,base_TWS,base_mainsheet,base_kicker,varyCunn,base_outhaulT,False,True,'csvs\\EX1_cunningham%.0f' % varyCunn,False)
                    attempts +=1
                if attempts > 0 and not convergedState:
                    failures+=1
                if failures > 5:
                    break
        if variable == 'outhaulT':
            failures = 0
            for step in range(0,npoints+1):
                varyOutH = outhaulT_lim[0]+(step/npoints)*(outhaulT_lim[1]-outhaulT_lim[0])
                attempts = 0
                convergedState = False
                while not convergedState and attempts < 1:
                    Vb,thetaA,convergedState,outDict[variable][step],times,iterations = steadyCase(base_trueWindAngle,base_TWS,base_mainsheet,base_kicker,base_cunningham,varyOutH,False,True,'csvs\\EX1_outhaul%.0f' % varyOutH,False)
                    attempts +=1
                if attempts > 0 and not convergedState:
                    failures+=1
                if failures > 5:
                    break

    # Write csv
    outputFileName = 'C:\\Users\\matth\\Documents\\Inventor\\ILCA7\\Sail\\ILCA7_Sail7\\InCAD\\FEA\\PythonRuns\\Ex1_MAT8.csv'
    outputFile = open(outputFileName,"w")
    for variable in outDict:
        for step in range(0,npoints+1):
            printDict = outDict[variable][step]
            if step == 0 and variable == varlist[0]:
                for i in printDict[0:14]:
                    outputFile.write('%s,'% i)
                outputFile.write('\n')
            for i in printDict[14:28]:
                outputFile.write('%s,'% i)
            outputFile.write('\n')
        outputFile.write('\n')
    outputFile.close()
pass

Main_x1optimum = 12
Kicker_x1optimum = 1440
Cunningham_x1optimum = 480
Outhaul_x1optimum = 510
varlist = ['mainsheet_kicker']#,'mainsheet_outhaul','mainsheet_cunningham','outhaulT_kicker','TWA_mainsheet','TWA_kicker','TWS_kicker','TWS_mainsheet']

Main_20perc = [Main_x1optimum*0.8 if Main_x1optimum*0.8 > mainsheet_lim[0] else mainsheet_lim[0],Main_x1optimum*1.2 if Main_x1optimum*1.2 < mainsheet_lim[1] else mainsheet_lim[1]]
Kicker_20perc = [Kicker_x1optimum*0.8 if Kicker_x1optimum*0.8 > kicker_lim[0] else kicker_lim[0],Kicker_x1optimum*1.2 if Kicker_x1optimum*1.2 < kicker_lim[1] else kicker_lim[1]]
Cunn_20perc = [Cunningham_x1optimum*0.8 if Cunningham_x1optimum*0.8 > cunningham_lim[0] else cunningham_lim[0],Cunningham_x1optimum*1.2 if Cunningham_x1optimum*1.2 < cunningham_lim[1] else cunningham_lim[1]]
Outhaul_20perc = [Outhaul_x1optimum*0.8 if Outhaul_x1optimum*0.8 > outhaulT_lim[0] else outhaulT_lim[0],Outhaul_x1optimum*1.2 if Outhaul_x1optimum*1.2 < outhaulT_lim[1] else outhaulT_lim[1]]

# Case 2 takes the optimum (maximum VMG) values from experiment 1,
# And changes the independent variables (two of them) by +-20% to see how each of these variables affect each other
# To generate surface plots
failures = 0
if case == 2:
    npoints = 15
    for variable in varlist:
        varPts = npoints # required for TWS cases (limited to three wind speeds for computational time in Experiment 3)
        outDict.update({variable:dict()})
        timesTotal = numpy.array([0,0,0,0,0,0],float)
        timing = True

        if variable == 'mainsheet_kicker':
            timing = True
            for var1step in range(0,npoints+1):
                if var1step == 0:
                    outDict[variable] = {var1step:dict()}
                else:
                    outDict[variable][var1step] = {0:1.}
                failures = 0
                varyMain = Main_20perc[0]+(var1step/npoints)*(Main_20perc[1]-Main_20perc[0])
                for var2step in range(0,npoints+1):
                    varyKick = Kicker_20perc[0]+(var2step/npoints)*(Kicker_20perc[1]-Kicker_20perc[0])
                    convergedState = False
                    Vb,thetaA,convergedState,outDict[variable][var1step][var2step],times,iterations = steadyCase(base_trueWindAngle,base_TWS,varyMain,varyKick,base_cunningham,base_outhaulT,False,False,'',timing)
                    timesTotal[:5]+=times
                    timesTotal[5]+=iterations
                    if not convergedState:
                        failures+=1
                    
                    #if failures > 2:
                    #    break
                pass
            pass

        if variable == 'mainsheet_outhaul':
            for var1step in range(0,npoints+1):
                if var1step == 0:
                    outDict[variable] = {var1step:dict()}
                else:
                    outDict[variable][var1step] = {0:1.}
                failures = 0
                varyMain = Main_20perc[0]+(var1step/npoints)*(Main_20perc[1]-Main_20perc[0])
                for var2step in range(0,npoints+1):
                    varyOutH = Outhaul_20perc[0]+(var2step/npoints)*(Outhaul_20perc[1]-Outhaul_20perc[0])
                    convergedState = False
                    Vb,thetaA,convergedState,outDict[variable][var1step][var2step],times,iterations = steadyCase(base_trueWindAngle,base_TWS,varyMain,base_kicker,base_cunningham,varyOutH,False,False,'',timing)
                    timesTotal[:5]+=times
                    timesTotal[5]+=iterations
                    if not convergedState:
                        failures+=1
                    #if failures > 2:
                    #    break
                pass
            pass

        if variable == 'mainsheet_cunningham':
            for var1step in range(0,npoints+1):
                if var1step == 0:
                    outDict[variable] = {var1step:dict()}
                else:
                    outDict[variable][var1step] = {0:1.}
                failures = 0
                varyMain = Main_20perc[0]+(var1step/npoints)*(Main_20perc[1]-Main_20perc[0])
                for var2step in range(0,npoints+1):
                    varyCunn = Cunn_20perc[0]+(var2step/npoints)*(Cunn_20perc[1]-Cunn_20perc[0])
                    convergedState = False
                    Vb,thetaA,convergedState,outDict[variable][var1step][var2step],times,iterations = steadyCase(base_trueWindAngle,base_TWS,varyMain,base_kicker,varyCunn,base_outhaulT,False,False,'',timing)
                    timesTotal[:5]+=times
                    timesTotal[5]+=iterations
                    if not convergedState:
                        failures+=1
                    #if failures > 2:
                    #    break
                pass
            pass

        if variable == 'outhaulT_kicker':
            for var1step in range(0,npoints+1):
                if var1step == 0:
                    outDict[variable] = {var1step:dict()}
                else:
                    outDict[variable][var1step] = {0:1.}
                failures = 0
                varyOutH = Outhaul_20perc[0]+(var1step/npoints)*(Outhaul_20perc[1]-Outhaul_20perc[0])
                for var2step in range(0,npoints+1):
                    varyKick = Kicker_20perc[0]+(var2step/npoints)*(Kicker_20perc[1]-Kicker_20perc[0])
                    convergedState = False
                    Vb,thetaA,convergedState,outDict[variable][var1step][var2step],times,iterations = steadyCase(base_trueWindAngle,base_TWS,base_mainsheet,varyKick,base_cunningham,varyOutH,False,False,'',timing)
                    timesTotal[:5]+=times
                    timesTotal[5]+=iterations
                    if not convergedState:
                        failures+=1
                    #if failures > 2:
                    #    break
                pass
            pass

        if variable == 'TWS_kicker':
            varPts = 5
            for var1step in range(0,varPts+1):
                if var1step == 0:
                    outDict[variable] = {var1step:dict()}
                else:
                    outDict[variable][var1step] = {0:1.}
                failures = 0
                varyTWS = TWS_cases[var1step]
                for var2step in range(0,npoints+1):
                    varyKick = (var2step/npoints)*Kicker_20perc[1]
                    convergedState = False
                    Vb,thetaA,convergedState,outDict[variable][var1step][var2step],times,iterations = steadyCase(base_trueWindAngle,varyTWS,base_mainsheet,varyKick,base_cunningham,base_cunningham,False,False,'',timing)
                    timesTotal[:5]+=times
                    timesTotal[5]+=iterations
                    if not convergedState:
                        failures+=1
                    #if failures > 2:
                    #    break
                pass
            pass

        if variable == 'TWS_mainsheet':
            varPts = 5
            for var1step in range(0,6):
                if var1step == 0:
                    outDict[variable] = {var1step:dict()}
                else:
                    outDict[variable][var1step] = {0:1.}
                failures = 0
                varyTWS = TWS_cases[var1step]
                for var2step in range(0,npoints+1):
                    varyMain = Main_20perc[0]+(var2step/npoints)*(Main_20perc[1]-Main_20perc[0])
                    convergedState = False
                    Vb,thetaA,convergedState,outDict[variable][var1step][var2step],times,iterations = steadyCase(base_trueWindAngle,varyTWS,varyMain,base_kicker,base_cunningham,base_cunningham,False,False,'',timing)
                    timesTotal[:5]+=times
                    timesTotal[5]+=iterations
                    if not convergedState:
                        failures+=1
                    #if failures > 2:
                    #    break
                pass
            pass
        
        if variable == 'TWA_mainsheet':
            for var1step in range(0,npoints+1):
                if var1step == 0:
                    outDict[variable] = {var1step:dict()}
                else:
                    outDict[variable][var1step] = {0:1.}
                failures = 0
                varyTWA = TWA_lim[0]+(var1step/npoints)*(TWA_lim[1]-TWA_lim[0])
                for var2step in range(0,npoints+1):
                    varyMain = mainsheet_lim[0]+(var2step/npoints)*(mainsheet_lim[1]-mainsheet_lim[0])
                    convergedState = False
                    Vb,thetaA,convergedState,outDict[variable][var1step][var2step],times,iterations = steadyCase(varyTWA,base_TWS,varyMain,base_kicker,base_cunningham,base_outhaulT,False,False,'',timing)
                    timesTotal[:5]+=times
                    timesTotal[5]+=iterations
                    if not convergedState:
                        failures+=1
                    #if failures > 2:
                    #    break
                pass
            pass

        if variable == 'TWA_kicker':
            for var1step in range(0,npoints+1):
                if var1step == 0:
                    outDict[variable] = {var1step:dict()}
                else:
                    outDict[variable][var1step] = {0:1.}
                failures = 0
                varyTWA = TWA_lim[0]+(var1step/npoints)*(TWA_lim[1]-TWA_lim[0])
                for var2step in range(0,npoints+1):
                    varyKick = kicker_lim[0]+(var2step/npoints)*(kicker_lim[1]-kicker_lim[0])
                    convergedState = False
                    Vb,thetaA,convergedState,outDict[variable][var1step][var2step],times,iterations = steadyCase(varyTWA,base_TWS,base_mainsheet,varyKick,base_cunningham,base_outhaulT,False,False,'',timing)
                    timesTotal[:5]+=times
                    timesTotal[5]+=iterations
                    if not convergedState:
                        failures+=1
                    #if failures > 2:
                    #    break
                pass
            pass

        # Write csv for each variable separately
        outputFileName = 'D:\\Documents\\University\\Year 4\\RP3\\Results\\Experiment_2_Interactions\\EX2MAT8_%s_finer.csv' % variable
        outputFile = open(outputFileName,"w")
        for var1step in range(0,varPts+1):
            for var2step in range(0,npoints+1):
                printDict = outDict[variable][var1step][var2step]
                if var1step == 0 and var2step == 0:
                    for i in printDict[0:14]:
                        outputFile.write('%s,'% i)
                    outputFile.write('\n')
                for i in printDict[14:28]:
                    outputFile.write('%s,'% i)
                outputFile.write('\n')
        outputFile.write('\n')
        outputFile.close()

        if timing:
            timingFileName = 'D:\\Documents\\University\\Year 4\\RP3\\Results\\Experiment_2_Interactions\\EX2_Timing_%s.csv' % variable
            timingFile = open(timingFileName,"w")
            for i in timesTotal:
                timingFile.write('%s,'% i)
            timingFile.close()

# Case 3 takes an input TWA, and calculates the optimum controls to maximise VMG
# TWA is the independent variable, the rest are to be optimised - heading up into the wind increases VMG


if case == 3:
    varlist = ['mainsheet','kicker','cunningham','outhaulT']
    npoints = 20
    printDictionary = {0:0}
    prevAngle_Velocity = 0
    prevMain_Angle = 0
    for point in range(0,npoints+1):
        TWA_case = TWA_lim[0]+(point/npoints)*(TWA_lim[1]-TWA_lim[0])
        
        TWS_input = 5
        main_input = 10
        kicker_input = 1440
        cunningham_input = 480
        outhaul_input = 510
        
        tryAgain = 0

        printDictionary.update({point:0})

        original_mainsheet_lim = [0,TWA_case]
        original_kicker_lim = [0, 2400]
        original_cunningham_lim = [0, 800]
        original_outhaulT_lim = [250,600]

        prev_best_case = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        TWA_lim = [20,90]
        TWS_cases = [1,5,10]
        mainsheet_lim = [0,TWA_case]
        kicker_lim = [0, 2400]
        cunningham_lim = [0, 800]
        outhaulT_lim = [250,600]

        loop = 0
        tolerance = 0.1

        optimum = False
        for variable in varlist:
            outDict.update({variable:dict()})
        while not optimum:
            Vb,thetaA,convergedState,input_Case_Run,times,iterations = steadyCase(TWA_case,TWS_input,main_input,kicker_input,cunningham_input,outhaul_input,False,False,'',False)
            input_VMG = input_Case_Run[27]
            while input_VMG < prev_best_case[27]: # if not an improvement, move variables back to previous converged case.
                print("*\n*\n*\n*\n*\n*\n*\n*\n*\nEdge Case found\n*\n*\n*\n*\n*\n*\n*\n*\n")
                printCase = prev_case_run

                main_input = (main_input+prev_best_case[16])*0.5
                kicker_input = (kicker_input+prev_best_case[17])*0.5
                cunningham_input = (cunningham_input+prev_best_case[18])*0.5
                outhaul_input = (outhaul_input+prev_best_case[19])*0.5

                Vb,thetaA,convergedState,input_Case_Run,times,iterations = steadyCase(TWA_case,TWS_input,main_input,kicker_input,cunningham_input,outhaul_input,False,False,'',False)
                input_VMG = input_Case_Run[27]
                outputFileName = 'D:\\Documents\\University\\Year 4\\RP3\\Results\\Experiment_3_Optimisation\\Ex3_Current_Operating_Point.csv'
                outputFile = open(outputFileName,"w")
                for i in input_Case_Run[0:14]:
                    outputFile.write('%s,'% i)
                outputFile.write('\n')
                for i in input_Case_Run[14:28]:
                    outputFile.write('%s,'% i)
                outputFile.write('\n')
                outputFile.close()
                print(outputFileName)

            if loop == 0:
                prev_best_case = input_Case_Run
            if input_VMG >= prev_best_case[27]:
                prev_best_case = input_Case_Run

            main_input = prev_best_case[16]
            kicker_input = prev_best_case[17]
            cunningham_input = prev_best_case[18]
            outhaul_input = prev_best_case[19]

            Main_Permutations = [prev_best_case[16]*(1-tolerance) if prev_best_case[16]*(1-tolerance) > mainsheet_lim[0] else mainsheet_lim[0], prev_best_case[16]*(1+tolerance) if prev_best_case[16]*(1+tolerance) < mainsheet_lim[1] else mainsheet_lim[1]]
            Kicker_Permutations = [prev_best_case[17]*(1-tolerance) if prev_best_case[17]*(1-tolerance) > kicker_lim[0] else kicker_lim[0], prev_best_case[17]*(1+tolerance) if prev_best_case[17]*(1+tolerance) < kicker_lim[1] else kicker_lim[1]]
            Cunningham_Permutations = [prev_best_case[18]*(1-tolerance) if prev_best_case[18]*(1-tolerance) > cunningham_lim[0] else cunningham_lim[0], prev_best_case[18]*(1+tolerance) if prev_best_case[18]*(1+tolerance) < cunningham_lim[1] else cunningham_lim[1]]
            Outhaul_Permutations = [prev_best_case[19]*(1-tolerance) if prev_best_case[19]*(1-tolerance) > outhaulT_lim[0] else outhaulT_lim[0], prev_best_case[19]*(1+tolerance) if prev_best_case[19]*(1+tolerance) < outhaulT_lim[1] else outhaulT_lim[1]]
            pass
            for i in [0,1]: # relaxing constraints if we have reached an edge - will only take effect in the next loop if we have not reached a maximum
                if Main_Permutations[i] == mainsheet_lim[i]:
                    mainsheet_lim[i] = original_mainsheet_lim[i]
                if Kicker_Permutations[i] == kicker_lim[i]:
                    kicker_lim[i] = original_kicker_lim[i]
                if Cunningham_Permutations[i] == cunningham_lim[i]:
                    cunningham_lim[i] = original_cunningham_lim[i]
                if Outhaul_Permutations[i] == outhaulT_lim[i]:
                    outhaulT_lim[i] = original_outhaulT_lim[i]

            prev_inputs = [TWA_case,TWS_input,main_input,kicker_input,cunningham_input,outhaul_input,False,False,''] # last known converge-able case
            printCase = input_Case_Run

            outputFileName = 'D:\\Documents\\University\\Year 4\\RP3\\Results\\Experiment_3_Optimisation\\Ex3_Current_Operating_Point.csv'
            outputFile = open(outputFileName,"w")
            for i in input_Case_Run[0:14]:
                outputFile.write('%s,'% i)
            outputFile.write('\n')
            for i in input_Case_Run[14:28]:
                outputFile.write('%s,'% i)
            outputFile.write('\n')
            outputFile.close()
            print(outputFileName)

            for variable in varlist:
                for permute in range(0,2):
                    if variable == 'mainsheet':
                        Vb,thetaA,convergedState,outDict[variable][permute],times,iterations = steadyCase(TWA_case,TWS_input,Main_Permutations[permute],prev_best_case[17],prev_best_case[18],prev_best_case[19],False,False,'',False) 
                    if variable == 'kicker':
                        Vb,thetaA,convergedState,outDict[variable][permute],times,iterations = steadyCase(TWA_case,TWS_input,prev_best_case[16],Kicker_Permutations[permute],prev_best_case[18],prev_best_case[19],False,False,'',False)
                    if variable == 'cunningham':
                        Vb,thetaA,convergedState,outDict[variable][permute],times,iterations = steadyCase(TWA_case,TWS_input,prev_best_case[16],prev_best_case[17],Cunningham_Permutations[permute],prev_best_case[19],False,False,'',False)
                    if variable == 'outhaulT':
                        Vb,thetaA,convergedState,outDict[variable][permute],times,iterations = steadyCase(TWA_case,TWS_input,prev_best_case[16],prev_best_case[17],prev_best_case[18],Outhaul_Permutations[permute],False,False,'',False)
                    if outDict[variable][permute][27] > prev_best_case[27]:
                        prev_best_case = outDict[variable][permute]
                    outputFileName = 'D:\\Documents\\University\\Year 4\\RP3\\Results\\Experiment_3_Optimisation\\Ex3_Current_Operating_Point.csv'
                    outputFile = open(outputFileName,"w")
                    for i in outDict[variable][permute][0:14]:
                        outputFile.write('%s,'% i)
                    outputFile.write('\n')
                    for i in outDict[variable][permute][14:28]:
                        outputFile.write('%s,'% i)
                    outputFile.write('\n')
                    outputFile.close()
                    print(outputFileName)

            

            if outDict['mainsheet'][0][27] <= prev_best_case[27] and outDict['mainsheet'][1][27] <= prev_best_case[27]:
                main_optimised = True
                main_input = prev_best_case[16]
            else:
                main_optimised = False
                if outDict['mainsheet'][0][27] < outDict['mainsheet'][1][27]:
                    mainsheet_lim = [prev_best_case[16],mainsheet_lim[1]]
                    main_input = (mainsheet_lim[0]+mainsheet_lim[1])*0.5
                    
                else:
                    mainsheet_lim = [mainsheet_lim[0],prev_best_case[16]]
                    main_input = (mainsheet_lim[0]+mainsheet_lim[1])*0.5
                    
            
            if outDict['kicker'][0][27] <= prev_best_case[27] and outDict['kicker'][1][27] <= prev_best_case[27]:
                kicker_optimised = True   
                kicker_input = prev_best_case[17]             
            else:
                kicker_optimised = False
                if outDict['kicker'][0][27] < outDict['kicker'][1][27]:
                    kicker_lim = [prev_best_case[17],kicker_lim[1]]
                    kicker_input = (kicker_lim[0]+kicker_lim[1])*0.5
                    
                else:
                    kicker_lim = [kicker_lim[0],prev_best_case[17]]
                    kicker_input = (kicker_lim[1]+kicker_lim[0])*0.5
                    

            if outDict['cunningham'][0][27] <= prev_best_case[27] and outDict['cunningham'][1][27] <= prev_best_case[27]:
                cunningham_optimised = True   
                cunningham_input = prev_best_case[18]             
            else:
                cunningham_optimised = False
                if outDict['cunningham'][0][27] < outDict['cunningham'][1][27]:
                    cunningham_lim = [prev_best_case[18],cunningham_lim[1]]
                    cunningham_input = (cunningham_lim[0]+cunningham_lim[1])*0.5
                    
                else:
                    cunningham_lim = [cunningham_lim[0],prev_best_case[18]]
                    cunningham_input = (cunningham_lim[1]+cunningham_lim[0])*0.5
                    

            if outDict['outhaulT'][0][27] <= prev_best_case[27] and outDict['outhaulT'][1][27] <= prev_best_case[27]:
                outhaul_optimised = True 
                outhaul_input = prev_best_case[19]              
            else:
                outhaul_optimised = False
                if outDict['outhaulT'][0][27] < outDict['outhaulT'][1][27]:
                    outhaulT_lim = [prev_best_case[19],outhaulT_lim[1]]
                    outhaul_input = (outhaulT_lim[0]+outhaulT_lim[1])*0.5
                    
                else:
                    outhaulT_lim = [outhaulT_lim[0],prev_best_case[19]]
                    outhaul_input = (outhaulT_lim[1]+outhaulT_lim[0])*0.5
                    
            prev_case_run = input_Case_Run
            
            if main_optimised and kicker_optimised and cunningham_optimised and outhaul_optimised:
                optimum = True
                printDictionary[point] = prev_best_case
                if isinstance(printDictionary[point][26], str):
                    optimum = False
                    main_input = random.uniform(original_mainsheet_lim[0],original_mainsheet_lim[1])
                    kicker_input = random.uniform(original_kicker_lim[0],original_kicker_lim[1])
                    outhaul_input = random.uniform(original_outhaulT_lim[0],original_outhaulT_lim[1])
                    cunningham_input = random.uniform(original_cunningham_lim[0],original_cunningham_lim[1])
                    mainsheet_lim = original_mainsheet_lim
                    kicker_lim = original_kicker_lim
                    outhaulT_lim = original_outhaulT_lim
                    cunningham_lim = original_cunningham_lim
                    tryAgain += 1
                elif printDictionary[point][26] < prevAngle_Velocity and tryAgain < 5: #or printDictionary[point][16] < prevMain_Angle:
                    optimum = False
                    main_input = random.uniform(original_mainsheet_lim[0],original_mainsheet_lim[1])
                    kicker_input = random.uniform(original_kicker_lim[0],original_kicker_lim[1])
                    outhaul_input = random.uniform(original_outhaulT_lim[0],original_outhaulT_lim[1])
                    cunningham_input = random.uniform(original_cunningham_lim[0],original_cunningham_lim[1])
                    mainsheet_lim = original_mainsheet_lim
                    kicker_lim = original_kicker_lim
                    outhaulT_lim = original_outhaulT_lim
                    cunningham_lim = original_cunningham_lim
                    tryAgain += 1
                if tolerance > 0.02 and optimum:
                    optimum = False
                    tolerance = tolerance - 0.04


            loop += 1

        outputFileName = 'D:\\Documents\\University\\Year 4\\RP3\\Results\\Experiment_3_Optimisation\\Ex3_MAT8_Optimum%s.csv' % point
        outputFile = open(outputFileName,"w")
        for i in printCase[0:14]:
            outputFile.write('%s,'% i)
        outputFile.write('\n')
        for i in printCase[14:28]:
            outputFile.write('%s,'% i)
        outputFile.write('\n')
        outputFile.close()
        print(outputFileName)

        prevAngle_Velocity = printCase[26]
        prevMain_Angle = printCase[16]
        
    outputFileName = 'D:\\Documents\\University\\Year 4\\RP3\\Results\\Experiment_3_Optimisation\\Ex3_MAT8_Optima7.csv'
    outputFile = open(outputFileName,"w")
    for point in range(0,npoints+1):
        if point == 0:
            for i in printDictionary[point][0:14]:
                outputFile.write('%s,'% i)
            outputFile.write('\n')
        for i in printDictionary[point][14:28]:
            outputFile.write('%s,'% i)
        outputFile.write('\n')
    outputFile.close()
    print(outputFileName)
pass    