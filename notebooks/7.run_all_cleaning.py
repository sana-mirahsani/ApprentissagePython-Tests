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

notebooks_1 = ["0.Cleaning_JSON.ipynb", "1.Cleaning_actors.ipynb", "2.Cleaning_filename_phase1.ipynb", 
             "3.Cleaning_filename_phase2.ipynb", "4.Cleaning_filename_phase3.ipynb"] # all nb of cleaning

notebooks = ["0.Cleaning_JSON.ipynb", "1.Cleaning_actors.ipynb"]
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
out_dir_interim = parent_folder / "data" / "interim" / run_id
out_dir_interim.mkdir(parents=True, exist_ok=True) 

# create folder for raw data into data/raw
out_dir_raw = parent_folder / "data" / "raw" / run_id
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
        parameters={
        "filename": filename,
        "out_dir_interim": str(out_dir_interim),
        "out_dir_raw": str(out_dir_raw),
        "run_mode": "pipeline"
        },
        log_output=True
    )

    nb = nbformat.read(executed_nb_path, as_version=4)
    all_outputs = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            cell_data = {"cell_index": i, "source": cell.source, "outputs": []}
            for output in cell.get("outputs", []):
                if output.output_type == "stream":
                    cell_data["outputs"].append({"type": "stream", "name": output.name, "text": output.text})
                elif output.output_type in ["execute_result", "display_data"]:
                    cell_data["outputs"].append({"type": output.output_type, "data": output.data})
                elif output.output_type == "error":
                    cell_data["outputs"].append({
                        "type": "error",
                        "ename": output.ename,
                        "evalue": output.evalue,
                        "traceback": output.traceback
                    })
            all_outputs.append(cell_data)

    # Save outputs
    out_file = Path(out_dir_result) / f"{Path(nb_path).stem}_outputs.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_outputs, f, indent=2, ensure_ascii=False)
    print(f"Saved outputs for {nb_path} -> {out_file}")

    print("=================================================")
    

print("All notebooks executed and outputs saved in:", out_dir_result)