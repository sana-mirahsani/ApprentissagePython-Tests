#------------------------------------------------
# This script runs all cleaning parts in the correct order.
# Input : Raw data is Json format.
# Output : Cleaned data with filename and actors in CSV format.
#------------------------------------------------

#------------------------------------------------
#                  0.Library
#------------------------------------------------
import nbformat
import json
from pathlib import Path
from datetime import datetime
import papermill as pm

notebooks = ["0.Cleaning_JSON.ipynb", "1.Cleaning_actors.ipynb", "2.Cleaning_filename_phase1.ipynb", 
             "3.Cleaning_filename_phase2.ipynb", "4.Cleaning_filename_phase3.ipynb"] # all nb of cleaning

#------------------------------------------------
#      1.Prepare output folder
#------------------------------------------------
filename = str(input("Enter name of Raw data (ex:traces260105) : "))

# create folder for outputs of all cells in each notebook
parent_folder = Path("..") # go one folder up: "../"
run_id = filename + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir_result = parent_folder / "results" / run_id
out_dir_result.mkdir(parents=True, exist_ok=True) 

# create folder for data output of each notebook into data/interim
out_dir_interim = parent_folder / "data" / "interim" / filename
out_dir_interim.mkdir(parents=True, exist_ok=True) 

# create folder for raw data into data/raw
out_dir_raw = parent_folder / "data" / "raw" / filename
out_dir_raw.mkdir(parents=True, exist_ok=True) 

#------------------------------------------------
#      2.Run notebooks and extract outputs
#------------------------------------------------
for nb_path in notebooks:
    executed_nb_path = out_dir_result / f"{Path(nb_path).stem}_executed.ipynb"

    # Run notebook with Papermill
    pm.execute_notebook(
        input_path=nb_path,
        output_path=executed_nb_path,
        log_output=True
    )
    print("hello")
    # Extract outputs from executed notebook