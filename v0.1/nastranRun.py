import os

def run_analysis(bdf_folderpath: str,bdf_name: str):
    from pyNastran.utils.nastran_utils import run_nastran
    nastran_path = 'C:\\Program Files\\MSC.Software\\NaPa_SE\\20231\\Nastran\\bin\\nastran.exe'
    bdf_filepath = os.path.join(bdf_folderpath,bdf_name)
    run_nastran(bdf_filename=bdf_filepath, nastran_cmd=nastran_path, run_in_bdf_dir=True,keywords=['memorymax=3.0gb','bpool=0.05gb'])