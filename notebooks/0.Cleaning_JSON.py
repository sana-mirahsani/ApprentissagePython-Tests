# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: PFE
#     language: python
#     name: python3
# ---

# # Preparation Workflow Overview:
# 1. Import Libraries
# 2. Load File (JSON) : traces260105_brutes.json
# 3. Clean JSON 
# 4. Convert JSON to DF
# 5. Save cleaned DataFrame : traces260105_clean.csv
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

# + tags=["parameters"]
# Parameters
filename = None
out_dir_interim = None
out_dir_raw = None
# -

assert filename is not None, "filename was not passed!"
assert out_dir_interim is not None, "out_dir_interim missing"
assert out_dir_raw is not None, "out_dir_raw missing"

# +

process_raw_data(filename + ".json", filename +  "_clean"  + ".csv", out_dir_interim, out_dir_raw)
