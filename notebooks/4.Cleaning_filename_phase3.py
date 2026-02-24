# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: PFE
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Phase3 Workflow Overview:
# 1. Import Libraries
# 2. Load DataFrame : filename + "_filename_phase2_clean" + ".csv"
# 3. Bizzar indices
# 4. Save final dataframe : filename + "_filename_phase3_clean" + ".csv"
# 5. Analyse for year 2425
#
# _________________________________________________________
# **Explanation** 
# The goal of this notebook is to find and remove the bizzar indices from dataframe.
#
# #### What are these Bizzar indices?
#
# Some **filename_infere** entries are correct but don’t match the names in their **P_codeState**. This means the student renamed the file to a valid name, but it doesn’t match the original trace, and even the functions inside **P_codeState** show a different file name.
# <br>
#
# In phase 2 of nettoyage, the system first checks if the name matches the expected pattern. If it does, it returns the name without checking the **P_codeState** content, which is faster than inspecting each row’s content. Therefore, it’s clear that these names didn’t get updated when they should have.
#
# #### Three situations of Bizzar indices:
#
# **Note :These traces are only for Run.Test and these are the number of traces , NOT number of the students**
#
# - filename_impossible_to_find_index : It has a filename_infere but can't find the filename by P_codestate to check them 
# - filename_case1_index : The filename_infere it is not same as the name between <trace></trace> in P_codeState
# - filename_case2_index : The filename_infere it is not same as the name found by the functions in P_codeState
#
# #### Why we have the Bizzar indices? Shouldn't they be corrected in phase1 or 2 of nettoyage?
#
# The issue comes from the structure of the correct_filename_infere_in_subset function in data_cleaning. The function first checks if filename_infere matches the expected pattern (which includes all file names). If it matches, it returns the filename_infere without checking P_codeState. This works for most cases, but if a filename_infere is correct yet doesn’t match the name in P_codeState, the algorithm fails.
# <br>
#
# We could prioritize checking P_codeState, but that would be slow and unnecessary for traces that are already correct. Now that most of the data is cleaned, we can specifically check the filename_infere that don’t match P_codeState and fix them.
#
# #### What can we do about these Bizzar indices?
#
# The filename_infere found in case1 or case2 can be replaced with the name from either the trace or the function name in P_codeState. Since the P_codeState name is more reliable, we prefer to use it.
# <br>
#
# For entries in filename_impossible_to_find_index, where we can’t find the name from either the functions or the traces, we can’t recover them. These entries are removed to ensure the analysis is correct.

# %% [markdown]
# ## 1.Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'

import pandas as pd
import matplotlib.pyplot as plt

import importlib

from src.features import io_utils, data_cleaning, pipeline_utils

importlib.reload(io_utils)
importlib.reload(data_cleaning)
importlib.reload(pipeline_utils)

# %% tags=["parameters"]
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

# %%
try:
    run_mode
except NameError:
    run_mode = "interactive"

if run_mode == "pipeline":
    print("Running via Pipeline (papermill)")
    filename, out_dir_interim, _ = pipeline_utils.execute_by_pipeline(filename, out_dir_interim, out_dir_raw)
else:
    print("Running directly in Jupyter")
    filename = "traces260105"
    out_dir_interim = f"../data/interim/{filename}_20260205_093949"
    out_dir_raw = f"../data/raw/{filename}_20260205_093949"

    filename, out_dir_interim, _ = pipeline_utils.execute_manually(filename, out_dir_interim, out_dir_raw)

match filename:
    case "traces250102":
        from src.data.variable_constant_2425 import all_TP_functions_name_except_TP1_and_TPGAME, pattern_files_name, TP_NAME
        
    case "traces260105":
        from src.data.variable_constant_2526 import all_TP_functions_name_except_TP1_and_TPGAME, pattern_files_name, TP_NAME
       

# %% [markdown]
# Fin des modifs à faire liées à l'exécution autonome / pipeline.

# %%
# input and output data for this notebook
input_file = filename + "_filename_phase2_clean" + ".csv"
output_file = filename + "_filename_phase3_clean" + ".csv"

# %% [markdown]
# ## 2.Load DataFrame

# %%
df = io_utils.reading_dataframe(dir= out_dir_interim, file_name=input_file)

# %% [markdown]
# ## 3.Bizzar indices

# %% [markdown]
# ### 3.1 Extract these strange indices

# %%
# Create Dataframe
df_strange_filenames_Run_Test = pd.DataFrame(columns=['TP','filename_impossible_to_find_index', 'filename_case1','filename_case2']) 

# Fill dataframe only for Run.Test for each TP
for tp in TP_NAME:

    df, impossible_filename, filename_case1, filename_case2 = data_cleaning.find_strange_filename_infere(df, tp,'Run.Test',
                                                                                                         all_TP_functions_name_except_TP1_and_TPGAME ,
                                                                                                         pattern_files_name)
    
    # Append row to a new df
    df_strange_filenames_Run_Test = pd.concat([
        df_strange_filenames_Run_Test,
        pd.DataFrame({'TP': [tp], 'filename_impossible_to_find_index': [impossible_filename], 'filename_case1': [filename_case1], 'filename_case2': [filename_case2]})
    ], ignore_index=True)

df_strange_filenames_Run_Test

# %% [markdown]
# ### 3.2 Save bizzar indices into CSV

# %%
# save the removed trace into a csv
io_utils.write_csv(df= df_strange_filenames_Run_Test, dir= out_dir_interim, file_name= 'bizzar_traces.csv')

# %% [markdown]
# ### 3.3 Calculate the percentage of bizzar indices before they are removed

# %%
# calculate the percentage of removing traces of each TP
all_percentage_removed = [] # save later for the plot

for tp in TP_NAME:

    total_traces_of_tp = (df['TP'] == tp).sum()
    total_traces_of_empty_filename = len(df_strange_filenames_Run_Test[df_strange_filenames_Run_Test['TP'] == tp]['filename_impossible_to_find_index'].iloc[0])
    total_traces_of_filename_case1 = len(df_strange_filenames_Run_Test[df_strange_filenames_Run_Test['TP'] == tp]['filename_case1'].iloc[0])
    total_traces_of_filename_case2 = len(df_strange_filenames_Run_Test[df_strange_filenames_Run_Test['TP'] == tp]['filename_case2'].iloc[0])

    total_traces_to_remove = total_traces_of_empty_filename 

    percentage_removed = (total_traces_to_remove / total_traces_of_tp) * 100
    all_percentage_removed.append(percentage_removed)

    print("---------------------------")
    print(tp)
    print(f"Total traces of empty_filename : {total_traces_of_empty_filename}")
    print(f"Total traces of filename_case1 : {total_traces_of_filename_case1}")
    print(f"Total traces of filename_case2 : {total_traces_of_filename_case2}")
    print(f"Total traces to remove : {total_traces_to_remove}")
    print(f"Total traces of TP : {total_traces_of_tp}")
    print(f"{percentage_removed:.2f}% of the rows will be removed.")

# %% [markdown]
# ### 3.4 Plot the percentage of removing bizzar indices
#
# The plot below shows the percentage of rows where filename_infere couldn’t be found in P_codeState and had to be removed for accurate analysis.

# %%
indices = TP_NAME

plt.figure(figsize=(10, 6))
plt.bar(indices, all_percentage_removed, color='coral')
plt.title('Percentage of Rows Removed')
plt.xlabel('Index')
plt.ylabel('Percentage Removed (%)')

# Add percentage labels above bars
for i, v in enumerate(all_percentage_removed):
    plt.text(i, v + 1, f"{v:.1f}%", ha='center')

plt.ylim(0, 10)
plt.show()

# %% [markdown]
# **Interpretation for year 2425** 
#
# As shown, the highest percentage is for TP1 at 2.5%, which is normal since semaine_1 was not concered in phase2. Notably, TP_GAME (the most critical case) requires only 1.2% of its rows to be removed. This suggests we can proceed with the removal without worrying about a significant impact on the results.

# %% [markdown]
# ### 3.5 Remove bizzar indices from dataframe

# %%
old_df_before_removing = df.copy() # save the original one just in case

# Before removing
len(df)

# %%
columns = ['filename_impossible_to_find_index', 'filename_case1', 'filename_case2']

for tp in TP_NAME:

    for column in columns:
        index_to_removed = df_strange_filenames_Run_Test[df_strange_filenames_Run_Test['TP'] == tp][column].iloc[0]

        if index_to_removed != []:
            df = df.drop(index=index_to_removed)

# %%
# After removing traces
len(df)

# %% [markdown]
# ## 4.Save final dataframe

# %%
io_utils.write_csv(df,out_dir_interim,output_file)

# %% [markdown]
# ## 5. Analyse for year 2425
#
# | Phase | Total_trace |Filled_trace | Correct_trace | Incorrect_trace | EmptyTotal_trace | OtherVerbsEmpty_trace | FilledBySandwich | BizzarIndices |
# |----------|----------|----------|----------|----------|----------|----------|----------| ----------|
# | Phase1   | 306,946   | 222,957  | 167,403  | 55,554  | 83,957  | 44,277 | 0 | 0 |
# | Phase2   | 304,838   |259,576  | 256,591  | 2,985     | 45,262  | 22,440 | 59,783 | 574 |
#
# **Explanation**
#
# - Phase :
#     In cleaning part (nettoyage) there are two phases, and each clean a part of data.
#
# - Total_trace :
#     Total number of filename_infere in dataframe. The reason that Total_trace is different in phase1 and phase2, is because there were 2,748 traces with the values ' ' in their seance column. Since there were useless (something like a bug) we deleted them from df but saved them in a csv file. (check DF[seance] == '' part)
#
# - Filled_trace :
#     Total number of filename_infere that are filled.
#
# - Correct_trace :
#     Total number of filename_infere that are correct (comparing to the real names of files)
#
# - Incorrect_trace :
#     Total number of filename_infere that are incorrect (comparing to the real names of files)
#
# - EmptyTotal_trace :
#     Total filename_infere that are empty after cleaning part (This number includes all verbs such as session.start/session.end/dockstringgenerate)
#
# - OtherVerbsEmpty_trace :
#     Total filename_infere of all verbs excluding session.start/session.end/dockstringgenerate which are still empty even after cleaning part.
#
# - FilledBySandwich :
#     Total filename_infere filled by method snadwich in phase2, obviously the total number is zero for phase1 because there is no sandwich method.
#
# - BizzarIndices :
#     Total number of Bizzar filename_infere (I already explain them before), they will be deleted from df.
