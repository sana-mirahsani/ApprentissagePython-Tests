# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Preparation Workflow Overview:
# 1. Import Libraries
# 2. Load DataFrame : phase2_nettoyage_fichiere.csv
# 3. Anonymizing
# 4. Save new DataFrame : Final_nettoyage_2425.csv
# ____________________________________________
#
# **Explanation** 
#
# The goal is to anonymize the columns : **actor** and **binome** also the names of students in columns where they include these names and remove the comment in P_codeState and F_codeState. I used the same version as Thomas just change the part of spliting actor and binomes (because I already cleaned them so there is no need to split them), but since he used for and list, this code takes near 40 mins! of course it can be change and optimized, but for now it is not neccessary. This notebook is the final step of cleaning part, that's why the name of the csv file at the end is **Final_nettoyage_2425.csv**, after running this notebook simply you can go to the Ananlyze notebook.

# %% [markdown]
# ## 1.Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
from src.features import io_utils, data_anonymizing 
from src.data.constants import INTERIM_DATA_DIR

# %% [markdown]
# ## 2.Load DataFrame

# %%
df_clean = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase2_nettoyage_fichiere.csv')

# %% [markdown]
# ## 3.Anonymizing

# %%
# Apply : Start the anonymizing process (it takes 40 mins maximum)
data_anonymizing.anonymize_data(df_clean,'anonymized_data','anonymized_actor')

# %% [markdown]
# ## 4.Save new DataFrame

# %%
io_utils.write_csv(df_clean,INTERIM_DATA_DIR,'Final_nettoyage_2425.csv')
