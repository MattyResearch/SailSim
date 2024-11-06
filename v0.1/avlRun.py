# Run this geometry in AVL
import os
import time
import subprocess as sp

def run_aero(AVLfilename: str,txtfilename: str,iterationNumber: int,ThetaApparent:int,VApparentTip:float):
    #yawRate = VApparent/(3*2.555)
    yawRate = 1/3 # this is the correct non-dimensional AVL input format
    cPath = "C:"
    AVLPath = os.path.join(cPath,'/Users/matth/Documents/University/RP3/AVL')
    AVLexe = os.path.join(AVLPath,'avl.exe')
    runStr = 'load\n'
    runStr +='C:/Users/matth/Documents/University/RP3/AVL/%s\n' % AVLfilename
    runStr +='oper\n'
    runStr +='F\n'
    runStr +='C:/Users/matth/Documents/University/RP3/AVL/pyRunCase\n'
    runStr +='Y\n'
    runStr +='Y\n'
    runStr +='%.4f\n' % yawRate
    runStr +='M\n'
    runStr +='V\n'
    runStr +='%.4f\n' % (VApparentTip/1.333333) # Refer to notes to understand why this is calculated from Vtip, and why yawRate is 0.333
    runStr +='\n'
    if ThetaApparent > 40:
        loop = 10
    else:
        loop = 1
    for initial in range(1,loop+1): # This loop allows AVL to converge to high AOA
        runStr +='A\n'
        runStr +='A\n'
        runStr +='%.4f\n' % (ThetaApparent*((initial+4)/(loop+4)))
        #runStr +='I\n'
        runStr +='X\n'
    runStr +='FE\n'
    runStr +='C:/Users/matth/Documents/University/RP3/AVL/%s\n' % txtfilename
    runStr +='O\n'
    runStr +='\n'   
    runStr +='quit\n'
    try:
        sp.PYDEVD_THREAD_DUMP_ON_WARN_EVALUATION_TIMEOUT = True
        ps = sp.run(AVLexe,input=runStr.encode(),capture_output=False,timeout=5)
    except:
        avlstate = 1
        print('Error opening AVL.exe')
        print("Avl failure.. retrying")
        return avlstate
    avlstate = 0
    return avlstate