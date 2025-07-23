# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Analyze Workflow Overview:
# 1. Import Libraries
# 2. Load DataFrame : phase2_nettoyage_fichiere.csv 
# 3. Bizzar indices
#

# %% [markdown]
# ## Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
from src.features import io_utils, data_testing
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant_2425 import TP_NAME
import matplotlib.pyplot as plt
import numpy as np
import difflib

# just for test
from src.data.variable_constant_2425 import all_TP_functions_name 
import re
from src.data.variable_constant_2425 import FILES_BY_TP
from src.features import data_cleaning

# just for test
# Global variable pattern
pattern = ''
for tp_name in FILES_BY_TP:

    file_name = '|'.join(tp_name)
    pattern = pattern +  file_name + '|'

pattern = pattern  + 'Irrelevant' 

# %% [markdown]
# ## Load DataFrame

# %%
df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase2_nettoyage_fichiere.csv')


# %% [markdown]
# ## Bizzar indices

# %% [markdown]
# **What are these Bizzar indices?**
#
# There are filename_infere that are correct but they are not as same as the name in their P_codeState; it means that the student changed the name of file into another name which is correct but not same as the name between traces or even when I look at the content of P_codeState, the functions shows another name of file. Since in phase2 nettoyage, it checks first if the name is in the pattern, if so return the name without checking the P_codeState (it's more efficase than checking the content of P_codeState for each row), so it is obvious these names didn't change eventhough they should have. These traces are in three situations:
#
# **Note :These traces are only for Run.Test and these are the number of traces , NOT number of the students**
#
# - filename_impossible_to_find_index : It has a filename_infere but can't find the filename by P_codestate to check them 
# - filename_case1_index : The filename_infere it is not same as the name between <trace></trace> in P_codeState
# - filename_case2_index : The filename_infere it is not same as the name found by the functions in P_codeState
#
#
# **Why we have the Bizzar indices? Shouldn't be corrected in phase1 or 2 of nettoyage?**
#
# It's because of the function's structure **correct_filename_infere_in_subset** in **data_cleaning**. I prioritize the matching of filename_infere with the pattern (which include all the names of files) , and if matches, so it returns the filename_infere and it skips the checking part of P_codeState which works for the majority but if there are traces where their name of filename_infere is correct but it is not same as the name found by looking at the P_codeState, the algorithm fails. Of course we can prioritize the checking P_codeState in the function, BUT it will take a lots of time, and it will check each P_codeState of traces which are already correct, so it won't be effective. However, now that the majority of data is cleaned, we can check again what are the filename_infere which doesn't correspond to name found in P_codeState and replace them. 
#
# **What we should to them?**
# The filename_infere which will be found in case1 or case2, can be replaced by the name is found by whether the name between traces or the functions name in P_codeState, (since we are more sure that the name found by P_codeState is more correct, we can replace them) but for those in case **filename_impossible_to_find_index** , which means we can't find the name neither by their functions or name beween traces, we can't do anything, so we remove them to have a correct analyze.
#
# | Phase | Total_trace |Filled_trace | Correct_trace | Incorrect_trace | EmptyTotal_trace | OtherVerbsEmpty_trace | FilledBySandwich | BizzarIndices |
# |----------|----------|----------|----------|----------|----------|----------|----------| ----------|
# | Phase1   | 306,946   | 213,995  | 158,437  | 55,558  | 92,919  | 53,239 | 0 | 0 |
# | Phase2   | 304198   |266,925  | 266,925  | 0       | 37,273  | 18,261 | 59,783 | 574 |
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

# %% [markdown]
# ### Extract these strange indices

# %%
# extract these strange indices
def find_strange_filename_infere(TP,verb):

    # create the lists
    filename_impossible_to_find_index, filename_case1_index, filename_case2_index = [], [] , []
    
    for index, row in df[(df['TP'] == TP) & (df['verb'] == verb)].iterrows():

        match_state = re.search(r"<trace>(.*?)</trace>", str(row['P_codeState']))
        
        if match_state:
            
            trace_line = match_state.group(1)
                
            # Case1 : if <trace></trace> exists and the name between is different from the name in filename_infere
            if row['filename_infere'] != trace_line:
                # Save the index
                filename_case1_index.append(index)
                
                # check the similarity, to find the correct name
                filename_infere_removed = row['filename_infere'].replace('.py', '')
                similarity = difflib.SequenceMatcher(None, trace_line[:-3], filename_infere_removed).ratio()

                if similarity > 0.8:
                        # if the similarity is more than 80%, then change it
                        df.loc[index,'filename_infere'] = trace_line
                    
        else:
            # Case2 : if <trace></trace> is removed, try to find the name by the functions 
            filename_infere_codestate = data_cleaning.find_filename_by_function_name(all_TP_functions_name,row['P_codeState'])

            if filename_infere_codestate == '': 
                # Can't find the filename by functions in P_codeState
                # Save the index
                filename_impossible_to_find_index.append(index)

            else: 
                # Can find the fielname by functions' name but it is not same as the name in filename_infere
                if row['filename_infere'] != filename_infere_codestate:
                    
                    # Save the index
                    filename_case2_index.append(index) 

                    # Change the name by the correct one
                    df.loc[index,'filename_infere'] = filename_infere_codestate


    return filename_impossible_to_find_index, filename_case1_index, filename_case2_index

# Create Dataframe
df_strange_filenames_Run_Test = pd.DataFrame(columns=['TP','filename_impossible_to_find_index', 'filename_case1','filename_case2']) 

# Fill dataframe only for Run.Test for each TP
for tp in TP_NAME:

    impossible_filename, filename_case1, filename_case2 = find_strange_filename_infere(tp,'Run.Test')
    
    # Append row to df
    df_strange_filenames_Run_Test = pd.concat([
        df_strange_filenames_Run_Test,
        pd.DataFrame({'TP': [tp], 'filename_impossible_to_find_index': [impossible_filename], 'filename_case1': [filename_case1], 'filename_case2': [filename_case2]})
    ], ignore_index=True)

df_strange_filenames_Run_Test

# %% [markdown]
# ### Save bizzar indices into CSV

# %%
# save the removed trace into a csv
io_utils.write_csv(df_strange_filenames_Run_Test,INTERIM_DATA_DIR,'bizzar_traces')

# %% [markdown]
# ### Calculate the percentage of removing bizzar indices

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
# ### Plot the percentage of removing bizzar indices

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
# **Interpretation** 
#
# The plot above illustrates the percentage of rows that it was impossible to find a filename_infere by their P_codeState so they need to be removed to ensure accurate analysis. As shown, the highest percentage is for TP1 at 1.1%, which is relatively minor and not a major concern. Notably, TP_GAME (the most critical case) requires only 0.3% of its rows to be removed. This suggests we can proceed with the removal without worrying about a significant impact on the results.

# %% [markdown]
# ### Remove bizzar indices from dataframe

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
# ## Save the final dataframe

# %%
io_utils.write_csv(df,INTERIM_DATA_DIR,'phase3_nettoyage_fichiere')
