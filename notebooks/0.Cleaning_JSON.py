# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
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
import pandas as pd
import json
from pathlib import Path

from src.data.constants import *
from src.data.cleaning import process_raw_data 

# Si on execute ce notebook via le pipeline, décommenter ci-dessous


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
# -

assert filename is not None, "filename was not passed!"
assert out_dir_interim is not None, "out_dir_interim missing"
assert out_dir_raw is not None, "out_dir_raw missing"

# This is when you run notebook alone, give the parameters manually

# +
# ici ajouter le filename pour exécution du notebook hors pipeline
#filename = "traces260105"

# +
# input and output data for this notebook
#out_dir_interim = "../data/interim/traces260105_20260205_093949"
#out_dir_raw = "../data/raw/traces260105_20260205_093949"
# -

# Fin des modifs à faire liées à l'exécution autonome / pipeline.


input_file = filename + ".json"
output_file = filename +  "_clean"  + ".csv"

# +

process_raw_data(input_file, output_file, out_dir_interim, out_dir_raw)
