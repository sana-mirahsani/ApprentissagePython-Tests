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
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Preparation Workflow Overview:
# 1. Import Libraries
# 2. Load DataFrame
# 3. Clean DataFrame
#     <br>
#     3.1 Convert Time Format
#     <br>
#     3.2 Clean **Actor** Field
#     <br> 
#     3.3 Clean **Filename** Field 
# 4. Anonymize Data

# ## Import Libraries

import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import re
import io_utils, data_cleaning, data_anonymization
#from tests import test_preprocessing, test_anonymization
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant import SORTED_SEANCE, TP_NAME


# ## Load DataFrame
# - Use functions in file **io_utils.py.py**
# - The csv file is the output of process_raw_data

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='traces250102_clean.csv')

# ### Print 5 rows and columns of dataframe

df.head()

# ## Create a copy of dataframe to compare later

df_clean = df.copy()

# ## Clean DataFrame

# ### Convert Time Format

# Before
df_clean[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# Apply
df_clean = data_cleaning.clean_time(df_clean)

# After
df_clean[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# ### Clean **Actor** Field
# Process: 
# 1. Split actor and binome into 2 columns -> **df_clean = split_actor_binome()**
# 2. Delete emails at the end -> **df_clean = delete_end_email()**
# 3. Extract all the non matching name of actor with prenom.nom.etu -> **incorrect = not_a_correct_identifier()**
# 4. Delete all rows of nebut -> **df_clean = delete_actor_lines()** 
# 5. Remove actors or binomes name -> **df_clean = delete_name_actor_binome()**
# 6. Replace joker -> **df_clean = replace_jokers()**
# 7. Cleaning manually -> **df_clean = cleaning_manual_actors_2425()**

# #### 1. Split actor and binome into 2 columns (This part delete '/')

# +
# Before 
total_slash = df_clean['actor'].str.contains('/').sum()
total_nan   = df_clean['actor'].isna().sum()
total_empty = (df_clean['actor']=='').sum()

print(f"Total number of rows : {len(df_clean)}")
print(f"Total number of rows include / : {total_slash}")
print(f"Total number of Nan rows : {total_nan}")
print(f"Total number of empty strings : {total_empty}")
# -

# Apply
df_clean = data_cleaning.split_actor_binome(df_clean)

# +
# After
total_slash_actor  = df_clean['actor'].str.contains('/').sum()
total_slash_binome = df_clean['binome'].str.contains('/').sum() # double_check

print(f"Total number of rows include / in actor: {total_slash_actor}")
print(f"Total number of rows include / in binome: {total_slash_binome}")

print("Successful!") if total_slash_actor == 0 and total_slash_binome == 0 else print("Error!") 
# -

# #### 2. Delete the email at the end

# +
# Before (check actor and binom)
total_email_actor  = df_clean['actor'].str.contains('@').sum()
total_email_binome = df_clean['binome'].str.contains('@').sum()

print(f"Total number of rows include @ in actor:   {total_email_actor}")
print(f"Total number of rows include @ in binome : {total_email_binome}")
# -

# Apply 
df_clean = data_cleaning.delete_end_email(df_clean)

# +
# After
total_email_actor = df_clean['actor'].str.contains('@').sum()

print(f"Total number of rows include @ in actor: {total_email_actor}")

print("Successful!") if total_email_actor == 0 else print("Error!") 
# -

# #### 3. Extract all the non matching name of actor with prenom.nom.etu

# +
incorrect_actor  = data_cleaning.not_a_correct_identifier(df_clean,'actor')
incorrect_binome = data_cleaning.not_a_correct_identifier(df_clean,'binome')

incorrect_actor, incorrect_binome
# -

# #### 4. Delete all rows of nebut

# Before
total = (df_clean['actor'] == 'nebut').sum()
print(f"total occurance of nebut : {total}") 

# Apply
df_clean = data_cleaning.delete_actor_lines(df_clean, "nebut")

# After
total = (df_clean['actor'] == 'nebut').sum()
print(f"total occurance of nebut : {total}") 
print("Successful!") if total == 0 else print("Error!") 

# #### 5. Remove actors or binomes name ( just replace them by '' in binome column)

# Before in binome
total = (df_clean['binome'] == 'luc').sum()
print(f"total occurance : {total} ")

# Apply
df_clean = data_cleaning.delete_name_actor_binome(df_clean, 'binome', 'luc')

# After 
total = (df_clean['binome'] == 'luc').sum()
print(f"Total occurance of : {total}")
print("Successful!") if total == 0 else print("Error!") 

# #### 6. Replace joker

# +
# Before
total_joker1 = (df_clean['binome'] == 'MI1304').sum()
total_joker2 = (df_clean['binome'] == 'MI1301').sum()

print(f"Total occurance of joker 1 : {total_joker1}")
print(f"Total occurance of joker 2 : {total_joker2}")
# -

# Apply
jokers_real_name = {
    'MI1304': 'mariama-sere.sylla.etu',
    'MI1301': 'mariama-sere.sylla.etu'
}
df_clean = data_cleaning.replace_jokers(df_clean, ['actor','binome'],jokers_real_name)

# +
# After
total_joker1 = (df_clean['binome'] == 'MI1304').sum()
total_joker2 = (df_clean['binome'] == 'MI1301').sum()

print(f"Total occurance of joker 1 : {total_joker1}")
print(f"Total occurance of joker 2 : {total_joker2}")

print("Successful!") if total_joker1 == 0 and total_joker1 == 0 else print("Error!") 
# -


# #### 7. Cleaning manually

# +
# Before
total = (df_clean['actor'] == 'anis.younes.etu').sum()

print(f"Total occurance : {total}")
# -

# Apply
df_clean = data_cleaning.cleaning_manual_actors_2425(df_clean, 'anis.younes.etu')

# +
# After
total = (df_clean['actor'] == 'anis.younes.etu').sum()
print(f"Total occurance : {total}")

print("Successful!") if total == 0 else print("Error!") 
# -

# #### Retry Test for invalid actor or binome

# +
incorrect_actor  = data_cleaning.not_a_correct_identifier(df_clean,'actor')
incorrect_binome = data_cleaning.not_a_correct_identifier(df_clean,'binome')

print(len(incorrect_actor),len(incorrect_binome))

print("Cleaning actor successful!") if len(incorrect_actor) == 0 and len(incorrect_binome) == 0 else print("Error!") 
# -

# #### Save new dataframe

io_utils.write_csv(df_clean,INTERIM_DATA_DIR)

# ### Read clean dataframe

df_clean = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='acteur_nettoyage_2425.csv')

df_clean[['actor','binome']].head(10)

# ### Clean **Filename** Field
# Process:
#
# 1. Add Column 'TP'
#
# 2. Add Column 'filename_infere'
#
#     2.1 Fill filename_infere by filename values
#
#     2.2 Check empty filename_infere of **Run.Test**
#
#     2.3 Check empty filename_infere of **Run.Program**
#
#         2.3.1 Fill empty filename_infere of **Run.Program** by commandRan
#
#         2.3.2 Fill empty filename_infere of **Run.Program** by P_codestate
#
#     2.4 Check empty filename_infere of **Run.Debugger**
#
#         2.4.1 Fill empty filename_infere of **Run.Debugger** by commandRan
#
#     2.5 Check empty filename_infere of **Run.Command**
#
#     2.6 Check empty filename_infere of **File.Open**
#
#     2.7 Check empty filename_infere of **File.Save**
#
#     2.8 Check empty filename_infere of **Docstring.Generate** 
#
# 3. check all filename_infere and fill the rest
#
#     3.1 TP2 
#
# 4. Add Column 'Type_TP'
#

# #### 1. Add column TP

# +
# creat new list of TP with the same size as SORTED_SEANCE to use map
TP_NAME_change = ['Tp1','Tp2','Tp3','Tp4','Tp5','Tp6','Tp7','Tp8','DSI','Tp9','Tp10','Tp_game','Tp_game','Tp_game']

mapping_dict = dict(zip(SORTED_SEANCE, TP_NAME_change))

col_index = df_clean.columns.get_loc('seance')
df_clean.insert(col_index + 1, 'TP', df_clean['seance'].map(mapping_dict)) # use map to change all values

df_clean[['seance','TP']]

# +
# check Nan values in TP

print(f" Total number of nan in TP :{df_clean['TP'].isna().sum()}")
df_clean['TP'] = df_clean['TP'].fillna('')
print(f" Total number of nan in TP :{df_clean['TP'].isna().sum()}")
# -

# #### 2. Add Column 'filename_infere'

# create new column next to the filename
col_index = df_clean.columns.get_loc('filename')
df_clean.insert(col_index + 1, 'filename_infere', '') 
df_clean.columns

# #### 2.1 Fill filename_infere by filename values

# +
# Before
total_empty_filename_infere = (df_clean['filename_infere']=='').sum()
print(f"Total number of empty strings in filename_infere : {total_empty_filename_infere}")

# Apply
df_clean['filename_infere'] = data_cleaning.extract_short_filename(df_clean['filename'])

# After
total_empty_filename_infere = (df_clean['filename_infere']=='').sum()
print(f"Total number of empty strings in filename_infere : {total_empty_filename_infere}")
# -

df_clean[['filename','filename_infere']].head(10)

# Some filenames have already the name, we can fill filename_infere by them, which we filled some of them, reduced from 306914 to 151183

# #### 2.2 Check empty filename_infere of **Run.Test**

# +
total_Run_Test       = len(df_clean[df_clean['verb']  == 'Run.Test'])
total_Run_Test_empty = (df_clean[df_clean['verb'] =='Run.Test']['filename'] == '').sum()
total_Run_Test_nan   = df_clean[df_clean['verb'] =='Run.Test']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Test : {total_Run_Test}")
print(f"Total number of empty strings in filename_infere in Run.Test : {total_Run_Test_empty}")
print(f"Total number of None in filename_infere in Run.Test : {total_Run_Test_nan}")
# -

# **Interpretation** There is no empty or none values for Run.Test, but we need to check the correctness of their name which we do later.

# ####  2.3 Check empty filename_infere of **Run.Program**

# +
# Before
total_Run_Program       = len(df_clean[df_clean['verb']  == 'Run.Program'])
total_Run_Program_empty = (df_clean[df_clean['verb']=='Run.Program']['filename_infere'] == '').sum()
total_Run_Program_nan   = df_clean[df_clean['verb']=='Run.Program']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Program : {total_Run_Program}")
print(f"Total number of empty strings in filename_infere in Run.Program : {total_Run_Program_empty}")
print(f"Total number of None in filename_infere in Run.Program : {total_Run_Program_nan}")

# -

# **Interpretation** All rows of Run.Program is empty so we first look at column **commandRan** and then if there is still any empty string, we look at **P_codeState**

# ##### 2.3.1 Fill empty filename_infere of **Run.Program** by commandRan

# +
# check if all values in commandRan starts with %Run
total_non_empty_commandRan = len(df_clean[(df_clean['verb'] == 'Run.Program') & (df_clean['commandRan'] != '')])
total_commandRan_start_Run = len(df_clean[df_clean['verb'] == 'Run.Program']['commandRan'].str.startswith('%Run'))

print(f"Total rows of not empty strings in commandRan for Run.Program : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Run in Run.Program : {total_commandRan_start_Run}")
# -

# Apply
mask = df_clean['verb'] == 'Run.Program'
df_clean.loc[mask, 'filename_infere'] = data_cleaning.extract_short_filename_from_commandRan_Run_Program(df_clean.loc[mask, 'commandRan'])

# +
# After
total_Run_Program_empty = (df_clean[df_clean['verb']=='Run.Program']['filename_infere'] == '').sum()

print(f"Total rows of empty strings in Run.Program : {total_Run_Program_empty}")
# -

# **Interpretation** : we reduced empty filename_infere from 54352 to 5791, since they are still empty string, we need to look at **P_codeState** column.

# ##### 2.3.2 Fill empty filename_infere of **Run.Program** by P_codestate

# Apply
mask = (df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] == '')
df_clean.loc[mask, 'filename_infere'] = df_clean.loc[mask, 'P_codeState'].map(data_cleaning.extract_short_filename_from_P_codestate_Run_Program)

# +
# After
total_Run_Program_empty = (df_clean[df_clean['verb']=='Run.Program']['filename_infere'] == '').sum()

print(f"Total rows of empty strings in Run.Program : {total_Run_Program_empty}")
# -

df_clean[(df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] != '')][['filename_infere','commandRan','P_codeState']]

# #### 2.4 Check empty filename_infere of **Run.Debugger**

# +
# Before
total_Run_Debugger       = len(df_clean[df_clean['verb']  == 'Run.Debugger'])
total_Run_Debugger_empty = (df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'] == '').sum()
total_Run_Debugger_nan   = df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Debugger : {total_Run_Debugger}")
print(f"Total number of empty strings in filename_infere in Run.Debugger : {total_Run_Debugger_empty}")
print(f"Total number of None in filename_infere in Run.Debugger : {total_Run_Debugger_nan}")
# -

# Same as Run.Program we will do the same process

# ##### 2.4.1 Fill empty filename_infere of **Run.Debugger** by commandRan

# +
# check if all values in commandRan starts with %Debug
total_non_empty_commandRan       = len(df_clean[(df_clean['verb'] == 'Run.Debugger') & (df_clean['commandRan'] != '')])
total_commandRan_start_Debug     = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Debug').sum()
total_commandRan_start_NiceDebug = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Nice').sum()
total_commandRan_start_FastDebug = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Fast').sum()

print(f"Total rows of not empty strings in commandRan for Run.Debugger  : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Debug in Run.Debugger     : {total_commandRan_start_Debug}")
print(f"Total rows of commandRan starts with %NiceDebug in Run.Debugger : {total_commandRan_start_NiceDebug}")
print(f"Total rows of commandRan starts with %FastDebug in Run.Debugger : {total_commandRan_start_FastDebug}")
# -

# **Interpretation** All values in commandRan starts with %Debug, we can extract filename from commandRan.

# Apply
mask = df_clean['verb'] == 'Run.Debugger'
df_clean.loc[mask, 'filename_infere'] = data_cleaning.extract_short_filename_from_commandRan_Run_Debugger(df_clean.loc[mask, 'commandRan'])

# After
total_Run_Debugger_empty = (df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'] == '').sum()
print(f"Total number of empty strings in filename_infere in Run.Debugger : {total_Run_Debugger_empty}")

df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'].head(10)

# #### 2.5 Check empty filename_infere of **Run.Command**

# +
# Before
total_Run_command       = len(df_clean[df_clean['verb']  == 'Run.Command'])
total_Run_command_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_nan   = df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.command : {total_Run_command}")
print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of None in filename_infere in Run.command : {total_Run_command_nan}")

# +
# check if all values in commandRan starts with %NiceDebug or %FastDebug
total_non_empty_commandRan       = len(df_clean[(df_clean['verb'] == 'Run.Command') & (df_clean['commandRan'] != '')])
total_commandRan_start_Debug     = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%Debug').sum()
total_commandRan_start_NiceDebug = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%NiceDebug').sum()
total_commandRan_start_FastDebug = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%FastDebug').sum()

print(f"Total rows of not empty strings in commandRan for Run.Command  : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Debug in Run.Command     : {total_commandRan_start_Debug}")
print(f"Total rows of commandRan starts with %NiceDebug in Run.Command : {total_commandRan_start_NiceDebug}")
print(f"Total rows of commandRan starts with %FastDebug in Run.Command : {total_commandRan_start_FastDebug}")
# -

# **Interpretation** Only 70 values starts wtih %FastDebug, so we can fill only 70 values of filename_infere

# +
# Apply 
mask = df_clean['verb'] == 'Run.Command'

# Get only cleaned values for those starting with %FastDebug
cleaned_values = data_cleaning.extract_short_filename_from_commandRan_Run_Command(df_clean.loc[mask, 'commandRan'])

df_clean.loc[cleaned_values.index, 'filename_infere'] = cleaned_values

# +
# After
total_Run_command_empty     = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_not_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] != '').sum()

print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of NOT empty strings in filename_infere in Run.command : {total_Run_command_not_empty}")
# -

len(df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].unique())

# +
total_PcodeState_empty = (df_clean[df_clean['verb'] == 'Run.Command']['P_codeState'] == "").sum()
total_FcodeState_empty = (df_clean[df_clean['verb'] == 'Run.Command']['F_codeState'] == "").sum()

print(f"Total number of empty strings in P_codeState in Run.command : {total_PcodeState_empty}")
print(f"Total number of empty strings in F_codeState in Run.command : {total_FcodeState_empty}")
# -

# **Interpretation**
#
# There are 22461 different values in commandRan for Run.command, we can't use or analyze each single value, and since all values for Run.Command in P_codeState or F_codeState are empty we analyze them in the part of analyze each TP alone.

# #### 2.6 Check empty filename_infere of **File.Open**

# +
# Before
total_File_Open       = len(df_clean[df_clean['verb']  == 'File.Open'])
total_File_Open_empty = (df_clean[df_clean['verb'] == 'File.Open']['filename_infere'] == '').sum()
total_File_Open_nan   = df_clean[df_clean['verb'] == 'File.Open']['filename_infere'].isna().sum()

print(f"Total number of traces in File.Open : {total_File_Open}")
print(f"Total number of empty strings in filename_infere in File.Open : {total_File_Open_empty}")
print(f"Total number of None in filename_infere in File.Open : {total_File_Open_nan}")
# -

# #### 2.7 Check empty filename_infere of **File.Save**

# +
total_File_Save       = len(df_clean[df_clean['verb']  == 'File.Save'])
total_File_Save_empty = (df_clean[df_clean['verb'] == 'File.Save']['filename_infere'] == '').sum()
total_File_Save_nan   = df_clean[df_clean['verb'] == 'File.Save']['filename_infere'].isna().sum()

print(f"Total number of traces in File.Save : {total_File_Save}")
print(f"Total number of empty strings in filename_infere in File.Save : {total_File_Save_empty}")
print(f"Total number of None in filename_infere in File.Save : {total_File_Save_nan}")
# -

# #### 2.8 Check empty filename_infere of **Docstring.Generate**

# +
total_Docstring       = len(df_clean[df_clean['verb']  == 'Docstring.Generate'])
total_Docstring_empty = (df_clean[df_clean['verb'] == 'Docstring.Generate']['filename_infere'] == '').sum()
total_Docstring_nan   = df_clean[df_clean['verb'] == 'Docstring.Generate']['filename_infere'].isna().sum()

print(f"Total number of traces in Docstring.Generate : {total_Docstring}")
print(f"Total number of empty strings in filename_infere in Docstring.Generate : {total_Docstring_empty}")
print(f"Total number of None in filename_infere in Docstring.Generate : {total_Docstring_nan}")
# -

df_clean[df_clean['verb'] == 'Docstring.Generate']['function']

# Question: don't know how should I fill it.

# #### 3. check all filename_infere and fill the rest

# Extract real students from week = DSi
df_all_students = data_cleaning.extract_students_each_week(df_clean)
list_students = df_all_students[df_all_students['week'] == 'DSi']['name_students'].iloc[0]
list_students

# ##### 3.1 TP2

# +
# Remove absent students
present_students_semaine_2 = []

for student in list_students:
    if len(df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['actor'] == student)]) != 0:
        present_students_semaine_2.append(student)

print(f"Numbr of present students in semaine_2 : {len(present_students_semaine_2)}")

# Extract indices for each student
df_indices = pd.DataFrame(columns=['name_students', 'indices'])

for student in present_students_semaine_2:
    indices = data_cleaning.cut_df(df_clean,'semaine_2',student)

    df_indices = pd.concat([
        df_indices,
        pd.DataFrame({'name_students': [student], 'indices': [indices]})
    ], ignore_index=True)


df_indices

# +
x = []

for index, row in df_indices.iterrows():
    print(f"Student : {row['name_students']}")  # print specific column
    print(f"Number of activities : {len(row['indices'])}")
    
    for i in row['indices']:

        if abs(i[0] - i[1]) < 2:
            continue

        print(f"Activiy : {i}")

        total = ((df_clean.iloc[i[0]:i[1]]['filename_infere'] == "") & (df_clean.iloc[i[0]:i[1]]['verb'] != "Session.Start")).sum()
        print(f"Total empty strings : {total}")
        
        subset = df_clean.iloc[i[0]:i[1]]
        filtered = subset[(subset['filename_infere'] == '') & (subset['verb'] != "Session.Start")][['filename_infere','verb','commandRan','P_codeState','F_codeState']]
        x.append(filtered)
    break

# -

x[1]

df_clean.loc[103359][['verb','P_codeState']]

# ##### 3.2 TP3

# ##### 3.3 TP4

# ##### 3.4 TP5

# ## Anonymize Data

# +
#anonymized_df = df[['actor', 'binom']].copy() 
#anonymized_df['anonymized_actor'] = df.apply(data_anonymization.anonymize_actor, axis=1)
# -

# Replace column actor and binom by anonymized_actor

# +
#df[['actor', 'binom']] = df.apply(data_anonymization.anonymize_actor)
# -

#
# # TODO
# - Second add column TP next to the column semaine (TP1, TP2, TP3 ...) DONE!
# - Third add column next to TP column 'Type_TP' with two values : 1-TP_programmation 2-TP_manipulation (activite_range.py is manipulation)
# - Forth add column filename_infere next to the filename DONE!
# - change function names : extract_filename to extract_short_filename DONE!
# <br>
#
# - P_codeState for Run.Program : check the name of function in P_codeState with the name function in variab_constant.py if okay put the name as the filename
# - check utils.py in src/feature to see how thoma extract filename for P_codeState
# - Check the Etude_sur_les_testes.py in notebook / Thomas version to calculate the number of student present of each week and each TP DONE!
# - for File.txt or file.md look at the codestate and then remove it or not the name of the function and the content between <trace></tracte>
# - leave the semaine11
# - just keep the Prog because in the Run.Debugger there is TP that are manipulation which we don't need
# - we want just Nom_TP_PPROGRAMMATION without the first week
# - Leave the part after the print on Etude_sur_les_testes.py
# - See cleaning.keep_research_data_only in notebooks/Init_data.py
#
# - For Docstring.Generate what should I do? take values from function column?
# ## others:
# - Analyze.ipynb
# - add why there are empty filename after commandRan for Run.Program
# - Decide what to do with empty strings of Run.Program
# - Calculate the total name of student (after cleaning process)
# - init_data.py (look at it and the readme of Thomas)
# - Anonymization : actor, binom, P-code state, F-code state, columns_with_path
# - Process raw data
# - Add column that trace the output ?? I don't remember
# - Look at notebooknettoyage of Thomas to add a column
# - Correct Readme
#
# ## Analyze.ipynb
# - analyze by TP, and by students
#
# ## Three main thing for stage
# - How to check if the student did the Test and continue the Test
# - When the Test is red what did they do, did they continue or they did nothing
# - Seperate the student that are very debutan and the student that already did some courses in programmation

#
