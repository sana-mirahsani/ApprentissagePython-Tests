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
# # Preparation Workflow Overview:
# 1. Import Libraries
# 2. Load DataFrame : phase1_nettoyage_fichiere.csv
# 3. Validate 'filename_infere' values for each week
#     <br>
#     3.0 Initialize pahse two 
#     <br>
#
#     3.1 DF[seance] == semaine_1 
#     <br>
#
#     3.2 DF[seance] == semaine_2
#     <br>
#
#     3.3 DF[seance] == semaine_3
#     <br>
#
#     3.4 DF[seance] == semaine_4
#     <br>
#
#     3.5 DF[seance] == semaine_5 
#     <br>
#
#     3.6 DF[seance] == semaine_6
#     <br>
#
#     3.7 DF[seance] == semaine_7
#     <br>
#
#     3.8 DF[seance] == semaine_8
#     <br>
#
#     3.9 DF[seance] == semaine_9
#     <br>
#
#     3.10 DF[seance] == semaine_10
#     <br>
#
#     3.11 DF[seance] == DSi
#     <br>
#
#     3.12 DF[seance] == semaine_11
#     <br>
#
#     3.13 DF[seance] == semaine_12
#     <br>
#
#     3.14 DF[seance] == CTP
#     <br>
#
# 4. Add column TP
# 5. 
# 6. Save new DataFrame : phase2_nettoyage_fichiere.csv
#
#
# _________________________________________________________
# **Explanation** 
#
# The goal is validate the filename_infere and find a correct name for those which were impossible to find in phase one. At the end, the columns : **TP** and **Type_TP** are added to the dataframe to shows the numbr of TP and the type : programmation or manipulation by looking at the name of the filename_infere. 

# %% [markdown]
# ## Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import re
import numpy as np
from src.features import io_utils, data_cleaning, data_testing
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant_2425 import FILES_BY_TP, TP_name, Type_TP

# Global variable pattern
pattern = ''
for tp_name in FILES_BY_TP:

    file_name = '|'.join(tp_name)
    pattern = pattern +  file_name + '|'

pattern = pattern  + 'Irrelevant'

# %% [markdown]
# ## Load DataFrame

# %%
df_clean = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase1_nettoyage_fichiere.csv')


# %% [markdown]
# ## 3. Validate 'filename_infere' values for each week

# %% [markdown]
# ### 3.0 Initialize pahse two

# %%
# Validate all filenames for each activiy
def validate_process_of_filename(df_index,df,pattern):

    for index, row in df_index.iterrows():

        for activity in row['indices']:
            start = activity[0]
            end   = activity[1]
            
            subset_df = df.loc[start:end]

            try:
                data_cleaning.correct_filename_infere_in_subset(subset_df,df,pattern)
            
            except Exception as errors:
                name = row['name_students']
                print(f'Student: {name}')
                print(f'Activity in {start} : {end}')
                print(errors)
                break

    print('successful!!')   

# Find filename_infere for traces which doesn't have any valid codestate
def find_filename_by_sandwich(df_index,df):

    for index, row in df_index.iterrows():

        for activity in row['indices']:
            start = activity[0]
            end   = activity[1]
            
            subset_df = df.loc[start:end]

            # check if all the values in filename_infere are empty
            if (subset_df['filename_infere'] == '').all():
                df.loc[subset_df.index, 'filename_infere'] = 'Irrelevant'
            
            else:
                try:
                    data_cleaning.sandwich(subset_df,df)
                
                except Exception as errors:
                    name = row['name_students']
                    print(f'Student: {name}')
                    print(f'Activity in {start} : {end}')
                    print(errors)
                    break

    print('successful!!')    


# %%
# main process
def main_process(week: str,df: pd.DataFrame,pattern: str) -> pd.DataFrame:

    print(f"------------------ Start process in : {week} ------------------")

    # Test total for the current semaine
    data_testing.test_filename_infere_each_week(week,df,pattern)
    print('----------------------------------------')

    # create the list of students of the current week
    try:
        print('creating list of students...')
        list_students_semaine = df[df['seance'] == week]['actor'].unique().tolist()
        print('process ok!')
    except Exception as error:
        print(f"Error!! {error}")

    # create the dataframe of all sessions for each students in the current week
    try:
        print('creating df_indices...')
        df_indices = data_cleaning.create_df_indices(list_students_semaine,df,week)
        print('process ok!')
    except Exception as error:
        print(f"Error!! {error}")

    # save too_short_sessions in another dataframe before removing them
    try:
        print('saving too_short_sessions...')
        io_utils.write_too_short_indices_to_csv(df_indices,INTERIM_DATA_DIR, week, filename='too_short_sessions')
    except Exception as error:
        print(f"Error!! {error}")

    # test the total empty strings in the current week for each verb
    try:
        print('Get total number of empty strings...')
        data_testing.get_number_of_empty_filename_for_week(week,df)
    except Exception as error:
        print(f"Error!! {error}")

    # phase 1 :process of checking or filling the correct name in filename_infere
    try:
        print('Start validate process of filename...')
        validate_process_of_filename(df_indices,df,pattern)
    except Exception as error:
        print(f"Error!! {error}")

    # Test total for the current semaine
    data_testing.test_filename_infere_each_week(week,df,pattern)
    print('----------------------------------------')

    # check if there too_short_indices, then remove them
    try:
        print('Start removing too_short_indices (if they exist!)...')
        df = data_cleaning.check_invalid_names(df,df_indices)
    except Exception as error:
        print(f"Error!! {error}")

    # test if there is any incorrect name even after removing too_short_indices
    try:
        print('Test incorrect names again:')
        data_testing.test_incorrect_names(df, week, pattern)
    except Exception as error:
        print(f"Error!! {error}")

    # Test total for the current semaine
    data_testing.test_filename_infere_each_week(week,df,pattern)
    print('----------------------------------------')

    # creating new dataframe of only traces with filename_infere = ''
    try:
        print('creating new dataframe of empty filename_infere...')
        subset_empty_strings = df[(df['seance'] == week) & (df['filename_infere'] == '') & (df['verb'] != 'Docstring.Generate')] 
        print('process ok!')
    except Exception as error:
        print(f"Error!! {error}")

    # create the dataframe of all sessions for each students in the current week
    try:
        print('creating df_indices_new...')
        df_indices_new = data_cleaning.create_df_indices(list_students_semaine,subset_empty_strings,week)
        print('process ok!')
    except Exception as error:
        print(f"Error!! {error}")
    
    # phase 2: filling empty filename_infere by sandwich method
    try:
        print('start sandwich method...')
        find_filename_by_sandwich(df_indices_new,df)
    except Exception as error:
        print(f"Error!! {error}")

    # Test total for the current semaine
    data_testing.test_filename_infere_each_week(week,df,pattern)
    print('---------------Finish!------------------')

    # Find the empty string that have no solution 
    print('Excluding : Sessions.Start, Sessions.End , Docstring.Generate ...')
    
    excluded_verbs = ['Session.Start', 'Session.End', 'Docstring.Generate']

    # Filter conditions
    mask = (
        (df['seance'] == week) &
        (df['filename_infere'] == '') &
        (~df['verb'].isin(excluded_verbs))
    )
    
    # Apply filter and select columns
    df_empty_string = df[mask] 
    
    print(f'The total number of empty string with no solution : {len(df_empty_string)}')

    return df, df_empty_string


# %%
data_testing.test_filename_infere_total(df_clean,pattern) 

# %% [markdown]
# ### 3.1 **DF[seance] == semaine_1**

# %%
df_clean, df_empty_string_semaine_1 = main_process('semaine_1',df_clean,pattern)

# %% [markdown]
# ### 3.2 **DF[seance] == semaine_2**

# %%
df_clean, df_empty_string_semaine_2 = main_process('semaine_2',df_clean,pattern)

# %% [markdown]
# ### 3.3 **DF[seance] == semaine_3**

# %%
df_clean, df_empty_string_semaine_3 = main_process('semaine_3',df_clean,pattern)

# %% [markdown]
# ### 3.4 **DF[seance] == semaine_4**

# %%
df_clean, df_empty_string_semaine_4 = main_process('semaine_4',df_clean,pattern)

# %% [markdown]
# ### 3.5 **DF[seance] == semaine_5**

# %%
df_clean, df_empty_string_semaine_5 = main_process('semaine_5',df_clean,pattern)

# %% [markdown]
# ### 3.6 **DF[seance] == semaine_6**

# %%
df_clean, df_empty_string_semaine_6 = main_process('semaine_6',df_clean,pattern)

# %% [markdown]
# ### 3.7 **DF[seance] == semaine_7**

# %%
df_clean, df_empty_string_semaine_7 = main_process('semaine_7',df_clean,pattern)

# %% [markdown]
# ### 3.8 **DF[seance] == semaine_8**

# %%
df_clean, df_empty_string_semaine_8 = main_process('semaine_8',df_clean,pattern)

# %% [markdown]
# ### 3.9 **DF[seance] == semaine_9**

# %%
df_clean, df_empty_string_semaine_9 = main_process('semaine_9',df_clean,pattern)

# %% [markdown]
# ### 3.10 **DF[seance] == semaine_10**

# %%
df_clean, df_empty_string_semaine_10 = main_process('semaine_10',df_clean,pattern)

# %% [markdown]
# ### **3.11 DF[seance] == DSi**

# %%
df_clean, df_empty_string_semaine_DSi = main_process('DSi',df_clean,pattern)

# %% [markdown]
# ### **3.12 DF[seance] == semaine_11**

# %%
df_clean, df_empty_string_semaine_11 = main_process('semaine_11',df_clean,pattern)

# %% [markdown]
# ### **3.13 DF[seance] == semaine_12**

# %%
df_clean, df_empty_string_semaine_12 = main_process('semaine_12',df_clean,pattern)

# %% [markdown]
# ### **3.14 DF[seance] == CTP**

# %%
df_clean, df_empty_string_CTP= main_process('CTP',df_clean,pattern)

# %% [markdown]
# ### **3.15 DF[seance] == ''**

# %%
# save the traces of seance = ''
io_utils.write_csv(df_clean[df_clean['seance'] == ''],INTERIM_DATA_DIR,None)

# extract the indices of seance == ''
index_seance_empty = df_clean[df_clean['seance'] == ''].index.to_list()

# drop these indices
df_clean.drop(index_seance_empty, inplace=True)  

# test
df_clean[df_clean['seance'] == '']

# %% [markdown]
# ## Final test

# %%
data_testing.test_filename_infere_total(df_clean,pattern)

# %%
subset = df_clean[df_clean['filename_infere'] != '']

subset[~ subset['filename_infere'].str.contains(pattern, na = False)]['seance'].unique()

# %% [markdown]
# **Interpretation**
#
# Before starting Phase 1, I added a column called 'filename_infere', which was initially completely empty. In Phase 1, using the values from the 'filename', 'commandRan', and 'P_codeState' columns, I was able to fill in 213,995 entries in 'filename_infere'. Out of these, 158,437 were correct names and 55,558 were incorrect.
# After this phase, 92,919 entries in 'filename_infere' remained empty. Among these, 53,239 were neither from semaine_1 nor contained the verbs Sessions.Start, Sessions.End, or Docstring.Generate—and we are not concerned with semaine_1 or these verbs.
# <br>
#
# In Phase 2, I performed checks and filled 'filename_infere' values for each semaine. As a result, a total of 266,925 entries were filled, which all of them are correct ! The function validate_process replaces incorrect names with empty strings. 
# <br>
#
# After both phases, 37,273 'filename_infere' entries are still empty. Among these, 18,261 correspond to traces that either do not include the specified verbs (Sessions.Start, Sessions.End, Docstring.Generate) .
# <br>
#
# Overall, having only 18,261 unresolved entries out of 304,851 total, and successfully inferring 266,887 correct filenames, is a strong result.

# %% [markdown]
# **Explanation**
#
# - **Why do I see 'No trace with this name in semaine: anaba.hilary-williams.etu'?**
#
#     It depends on where you're seeing this message. This line is printed by the function cut_df, which is defined in data_cleaning.py and is called within the function create_df_indices. The create_df_indices function itself is called twice in the main_process() function.
#     This message indicates that, in the current week’s dataframe, there is no trace for the student with the given name. The first time create_df_indices is called, it searches in the original dataframe. The second time, it searches in a filtered subset of the original dataframe that only contains rows with empty filename_infere.
#     <br>
#
#     So, if you see this message during the first call, it's unusual — it means there is no trace at all for the student in the original dataframe, which might be a problem. But if you see it during the second call, it’s expected. It means that the student either:
#
#         1. Didn’t work at all that week,
#         2. Used the correct filename (so their traces were already matched),
#         3. Or didn’t use the Run.Command at all.
#
# - **How we can be wrong in sandwich function?**
#
#     This function fills empty filename_infere values in two cases:
#
#         1. When there is no filename_infere at all in a session, it labels all traces in that session as "Irrelevant".
#         2. When some filename_infere values exist, it applies a "sandwich mechanism" — meaning that any empty values found between two identical filename_infere entries are filled with that same value.
#     
#     Of course, this method isn’t perfect. Some traces may be filled inaccurately. For example, even if two identical filename_infere values surround a set of empty entries, the student might have worked on something else during that time. But since we can't detect that with certainty, we assume they were working on the same file.
#
# - **How we can be wrong in FUNCTIONS_TP6 and FUNCTIONS_TP7?**
#
#     The function **miroir()** is in both TP prog semaine_6 and semaine_7, so in the validating process, if this function is written in codestate , we can't know is it for semaine_6 or semaine_7; therefore we might be wrong in naming this function.
#
# - **Why there are less traces after check_invalid function?**
#
#     This function checks if there is any too_short_traces or not, if so it removes them. too_short_traces means the traces that has zero or one verb between a Session.Start and Session.End, like 
#     ```
#     Session.Start 
#     Run.Test
#     Session.End
#     ```
#     
#     These traces provide no useful information and can be safely removed from the dataframe. However, before removing them, I saved them into a CSV file named **too_short_sessions.csv** for reference. Once removed, it's expected that the total number of traces in the dataframe will decrease.
#
#     It's also important to note that even after running the validate_process function, some incorrect filename_infere values may still appear. This seems problematic at first because validate_process is supposed to remove all invalid names. However, if you check manually, you'll see that these invalid names belong to the too-short traces. Since validate_process doesn't handle or check those, it doesn’t correct them.
#
#     Therefore, once we remove the too_short_traces, the remaining dataset contains no invalid names — because all the incorrect ones were part of the traces that were excluded.
#
# - **Remove seance == ''**
#
#     There is an empty seance in df, including only 13 traces of one student on 16/12/2024, it was useless, so I removed them BUT I saved them before removing in a csv file.

# %% [markdown]
# ## 4. Add column TP

# %%
# Add column TP
# create new column next to the filename
col_index = df_clean.columns.get_loc('seance')

try:
    df_clean.insert(col_index + 1, 'TP', '') 
except Exception as error:
    print(error)

# create dictionary with keys of filenames and values of TP name
file_to_tp = {}
for tp, files in TP_name.items():
    for f in files:
        file_to_tp[f] = tp

# Apply : fill all values of TP
df_clean["TP"] = df_clean["filename_infere"].map(file_to_tp)

# replace all Nan by empty string
df_clean['TP'] = df_clean['TP'].fillna('') 

# Test
tota_empty = (df_clean['TP'] == '').sum()
totan_empty_filename =  (df_clean['filename_infere'] == '').sum()
totan_Irr_filename   =  (df_clean['filename_infere'] == 'Irrelevant').sum()

print("Normally, The empty values in column TP are for rows where filename_infere is empty or Irrelevant")
print("Testing...")
if tota_empty == totan_empty_filename + totan_Irr_filename :
    print("Yes, all Nan values in TP are wether empty or Irrelevant filename_infere")
    print(df_clean[['filename_infere', 'TP']].head(10))


# %% [markdown]
# ## 5. Add column TP_Type

# %%
# Add column TP
# create new column next to the filename
col_index = df_clean.columns.get_loc('TP')

try:
    df_clean.insert(col_index + 1, 'Type_TP', '') 
except Exception as error:
    print(error)
    
# create dictionary with keys of filenames and values of TP name
file_to_type_tp = {}
for tp, files in Type_TP.items():
    for f in files:
        file_to_type_tp[f] = tp

# Apply : fill all values of Type_TP
df_clean["Type_TP"] = df_clean["filename_infere"].map(file_to_type_tp)

# replace all Nan by empty string
df_clean['Type_TP'] = df_clean['Type_TP'].fillna('') 

tota_empty = (df_clean['Type_TP'] == '').sum()
print(f"Total empty : {tota_empty}")
df_clean['Type_TP']

# %% [markdown]
# ## Save the final dataframe

# %%
io_utils.write_csv(df_clean,INTERIM_DATA_DIR,'phase2_nettoyage_fichiere.csv')
