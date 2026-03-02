# This file contains all functions to execute 
# In pipeline and manually

#------------------------------------------------
#                  Library
#------------------------------------------------
from pathlib import Path
#------------------------------------------------
#                 Functions
#------------------------------------------------
def execute_by_pipeline(filename, out_dir_interim, out_dir_raw):
    # check if the parameters are passed correctly
    assert filename is not None, "filename was not passed!"
    assert out_dir_interim is not None, "out_dir_interim missing"
    assert out_dir_raw is not None, "out_dir_raw missing"

    return filename, out_dir_interim, out_dir_raw

def execute_manually(filename , out_dir_interim, out_dir_raw):
    # Define the path to the raw data file and the output directories (you can change them whatever you want)
    
    file_path = Path(out_dir_interim)

    if file_path.exists():
        print("Directory is ok.")
    
    else:
        print("Directory doesn't exist.")

    file_path2 = Path(out_dir_raw)

    if file_path2.exists():
        print("Directory is ok.")
    
    else:
        print("Directory doesn't exist.")

    return filename, out_dir_interim, out_dir_raw