# SailSim v0.1
## Aeroelastic Sail Modelling

This program uses an iterative method to calculate sail performance in upwind modes.
__main__ can be found in quasiSteadyRun.py.

This was written with and made possible by Steve Doyle's pyNastran
See the following link for install instructions:
http://pynastran-git.readthedocs.io/en/latest/quick_start/Installation.html

The user must also have MSC Nastran installed (for v0.1 or earlier) and Athena Vortex Lattice (M. Drela, H. Youngren)
AVL information can be found here:
https://web.mit.edu/drela/Public/web/avl/

As this is still a prototype code, file location definitions are scattered throughout the code. Edit these to the appropriate locations:
## In quasiSteadyRun.py:
runfolder = Location of .BDF and .op2 files.

## In structureToAero.py:
pkg_path = location of pyNastran-main folder.
sail_path = location of sail model .BDF file.
AVLPath = location of the AVL executable, the .avl input files, and the .txt pressure data files.

## In aeroToStructure.py:
pkg_path = location of pyNastran-main folder. (Yes, there is repitition, it will be removed)
AVLPath = location of the AVL executable, the .avl input files, and the .txt pressure data files.

## In nastranRun.py:
nastran_path = location of nastran.exe

## In avlRun.py:
AVLPath = location of the AVL executable, the .avl input files, and the .txt pressure data files.


Before running quasiSteadyRun:
1. Pre-work MUST be done to ensure no errors this includes:
2. Run the initial state BDF in Nastran to get op2 output (required for structureToAero.py)
3.  Run the structureToAero to ensure a workable aero file is output. Rename to ilca7_1.AVL

   
The iterative method then uses the following algorithm:
1. Run structureToAero.py to interpret structure for AVL
2. Run avlRun to get pressures
3. Run aeroToStructure to apply pressures to structure
4. Run nastranRun to find displacements
5. Repeat until convergence - previous op2 file MUST be stored. Use two BDF objects.
