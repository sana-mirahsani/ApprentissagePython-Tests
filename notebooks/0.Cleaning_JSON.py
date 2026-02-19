# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: PFE
#     language: python
#     name: python3
# ---

# # Preparation Workflow Overview:
# 1. Import Libraries
# 2. Cleaning JSON
# ____________________________________________
# **Explanation** 
#
# The goal of this part is to get the raw data in JSON format, cleaned them and transform it to CSV file. This code is the copy of Thomas code.
#
# File date_labels.json contains calendar week numbers, it aims to compute column 'seance', eg week 36 yields "semaine_1". This file must be verified each year.
#

# ## 1.Import Libraries

# +
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'

from src.data.constants import *
from src.data.cleaning import process_raw_data


# -


def execute_by_pipeline(filename, out_dir_interim, out_dir_raw):
    # check if the parameters are passed correctly
    assert filename is not None, "filename was not passed!"
    assert out_dir_interim is not None, "out_dir_interim missing"
    assert out_dir_raw is not None, "out_dir_raw missing"

    # define input and output file paths
    input_file = filename + ".json"
    output_file = filename +  "_clean"  + ".csv"

    # Process the raw data and save the cleaned data to the interim directory
    process_raw_data(input_file, output_file, out_dir_interim, out_dir_raw)


def execute_manually():
    # Define the path to the raw data file and the output directories (you can change them whatever you want)
    filename = "traces260105" # change this to the name of the file you want to process (without the .json extension)
    out_dir_interim = f"../data/interim/{filename}_20260205_093949"
    out_dir_raw = f"../data/raw/{filename}_20260205_093949"
    
    # input and output data for this notebook
    input_file = filename + ".json"
    output_file = filename +  "_clean"  + ".csv"

    # Process the raw data and save the cleaned data to the interim directory
    process_raw_data(input_file, output_file, out_dir_interim, out_dir_raw)


# + tags=["parameters"]
{
    "tags": [
        "parameters"
    ]
}
# Parameters
filename = None
out_dir_interim = None
out_dir_raw = None
run_mode = "interactive"

# +
# to check if a notebook is being run via papermill or directly in Jupyter, 
# we can check for the presence of the "PAPERMILL_EXECUTION" environment variable, 
# which is set by papermill when it executes a notebook. If this variable is present, 
# it means the notebook is being run via papermill; otherwise, it's being run directly in Jupyter.

try:
    run_mode
except NameError:
    run_mode = "interactive"

if run_mode == "pipeline":
    print("Running via Pipeline (papermill)")
    execute_by_pipeline(filename, out_dir_interim, out_dir_raw)
else:
    print("Running directly in Jupyter")
    execute_manually()


