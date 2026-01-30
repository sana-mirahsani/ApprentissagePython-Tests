import nbformat
from pathlib import Path
import json
from datetime import datetime

# Path to the executed notebook
notebook_path = "output_with_outputs.ipynb"

# Load notebook
nb = nbformat.read(notebook_path, as_version=4)

# Prepare output folder
run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = Path("results") / run_id
out_dir.mkdir(parents=True, exist_ok=True)

# Extract outputs
all_outputs = []

for i, cell in enumerate(nb.cells):
    if cell.cell_type == "code":
        cell_data = {
            "cell_index": i,
            "source": cell.source,
            "outputs": [],
        }
        for output in cell.get("outputs", []):
            # Handle different output types
            if output.output_type == "stream":
                cell_data["outputs"].append({
                    "type": "stream",
                    "name": output.name,
                    "text": output.text
                })
            elif output.output_type == "execute_result":
                cell_data["outputs"].append({
                    "type": "execute_result",
                    "data": output.data
                })
            elif output.output_type == "display_data":
                cell_data["outputs"].append({
                    "type": "display_data",
                    "data": output.data
                })
            elif output.output_type == "error":
                cell_data["outputs"].append({
                    "type": "error",
                    "ename": output.ename,
                    "evalue": output.evalue,
                    "traceback": output.traceback
                })
        all_outputs.append(cell_data)

# Save to JSON
with open(out_dir / "all_cell_outputs.json", "w", encoding="utf-8") as f:
    json.dump(all_outputs, f, indent=2, ensure_ascii=False)

print("All outputs saved in:", out_dir / "all_cell_outputs.json")
