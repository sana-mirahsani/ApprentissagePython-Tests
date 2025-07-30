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
# 2. Load DataFrame : acteur_nettoyage_2425.csv
# 3. Clean DataFrame
#     <br>
#     3.1 Add column **filename_infere**
#     <br>
#
#     3.2 Extract short filename
#     <br>
#
#     3.3 Check empty filename_infere of **Run.Test**
#     <br>
#
#     3.4 Check empty filename_infere of **Run.Program**
#
#         3.4.1 Fill empty filename_infere of Run.Program by P_codestate 
#         
#         3.4.2 Fill empty filename_infere of Run.Program by commandRan
#
#     3.5 Check empty filename_infere of **Run.Command** 
#     <br>
#
#     3.6 Check empty filename_infere of **File.Open** 
#     <br>
#
#     3.7 Check empty filename_infere of **File.Save**
#     <br>
#
#     3.8 Check empty filename_infere of **Docstring.Generate**
#
# 4. Save new DataFrame : phase1_nettoyage_fichiere.csv
#
#
# _________________________________________________________
# **Explanation** 
#
# The goal is creating a new column filename_infere, and finding the correct name of files and put them into this column. Since the process is complecated, I divided this part into two phases, phase one filling column filename_infere by columns : filename, commandRan and codestate; phase two validate them and use mecanism like similarity and sandwich to find filenames which were impossible to find them during the phase one. This notebook includs only phase one, it saves the result into a csv file and shoudl read this csv file as the input in the phase two notebook which is the next step.

# %% [markdown]
# ## 1.Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
from src.features import io_utils, data_cleaning
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant_2425 import pattern_files_name, all_TP_functions_name_except_TP1_and_TPGAME

# %% [markdown]
# ## 2.Load DataFrame

# %%
df_clean = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='acteur_nettoyage_2425.csv')

# %%
len(df_clean)

# %%
len(df_clean[df_clean['seance'] == ''].index.to_list())

# %% [markdown]
# ## 3.Clean DataFrame

# %% [markdown]
# ### Add column **filename_infere**

# %%
col_index = df_clean.columns.get_loc('filename')
df_clean.insert(col_index + 1, 'filename_infere', '') 
df_clean.columns

# %% [markdown]
# ### Extract short filename

# %%
# Before
total_empty_filename_infere = (df_clean['filename_infere']=='').sum()
print(f"Total number of empty strings in filename_infere : {total_empty_filename_infere}")

# Apply
df_clean['filename_infere'] = data_cleaning.extract_short_filename(df_clean['filename'])

# After
total_empty_filename_infere = (df_clean['filename_infere']=='').sum()
print(f"Total number of empty strings in filename_infere : {total_empty_filename_infere}")

# %%
df_clean[['filename','filename_infere']].head(10)

# %% [markdown]
# There are already some names in column filename, I extract them and put them in column filename_infere, total empty filename reduced from 306,914 to 151,183.

# %%
# this is for test you can remove it
df_clean[df_clean['_id.$oid'] == '66ed37fabd5a98b8f9da4354'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %%
# this is for test you can remove it
df_clean[df_clean['_id.$oid'] == '66ed3929bd5a98b8f9da4482'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %%
df_clean[['filename','filename_infere']].head(10)

# %% [markdown]
# ### Check empty filename_infere of **Run.Test**

# %%
# Before
total_Run_Test       = len(df_clean[df_clean['verb']  == 'Run.Test'])
total_Run_Test_empty = (df_clean[df_clean['verb'] =='Run.Test']['filename'] == '').sum()
total_Run_Test_nan   = df_clean[df_clean['verb'] =='Run.Test']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Test : {total_Run_Test}")
print(f"Total number of empty strings in filename_infere in Run.Test : {total_Run_Test_empty}")
print(f"Total number of None in filename_infere in Run.Test : {total_Run_Test_nan}")

# %% [markdown]
# **Interpretation** There is no empty or none values for Run.Test, but I need to check the correctness of their name which I do in phase two.

# %% [markdown]
# ###  Check empty filename_infere of **Run.Program**

# %%
# Before
total_Run_Program       = len(df_clean[df_clean['verb']  == 'Run.Program'])
total_Run_Program_empty = (df_clean[df_clean['verb'] =='Run.Program']['filename_infere'] == '').sum()
total_Run_Program_nan   = df_clean[df_clean['verb'] =='Run.Program']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Program : {total_Run_Program}")
print(f"Total number of empty strings in filename_infere in Run.Program : {total_Run_Program_empty}")
print(f"Total number of None in filename_infere in Run.Program : {total_Run_Program_nan}")

# %% [markdown]
# **Interpretation** All rows of Run.Program is empty; first I look at the column **P_codeState**, if there is any file's name between <trace></trace>, I extract it. Then if there is any empty string still, I look at the **commandRan** column, since all values start with %Run, I can use an unique pattern to extract the filename for the empty filename_infere. Normally the filename_infere I found from P_codestate are correct, but since at the beginning I filled filename_infere by filename without checking them are correct or not, or extracting a name after %Run in commandRan, there might be incorrect names, which I will check them in phase two.  

# %% [markdown]
# #### Fill empty filename_infere of **Run.Program** by P_codestate

# %%
# check if all values in P_codeState have <trace></trace>
total_non_empty_codestate     = (df_clean[df_clean['verb']  == 'Run.Program']['P_codeState'] != '').sum()
total_codestate_contain_trace = df_clean[df_clean['verb']  == 'Run.Program']['P_codeState'].str.contains(r'<trace>.*\.py</trace>', regex=True, na=False).sum()

print(f"Total rows of not empty strings in P_codeState for Run.Program : {total_non_empty_codestate}")
print(f"Total rows of P_codeState contian <trace> : {total_codestate_contain_trace}")

# %%
# Apply : Extract the name between <traces> without looking the dictionary
mask = (df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] == '')
df_clean.loc[mask, 'filename_infere'] = df_clean.loc[mask, 'P_codeState'].map(data_cleaning.extract_short_filename_from_P_codestate_Run_Program)

# %%
# After
total_Run_Program_empty = (df_clean[df_clean['verb'] =='Run.Program']['filename_infere'] == '').sum()
print(f"Total rows of empty strings in Run.Program : {total_Run_Program_empty}")

# %% [markdown]
# #### Fill empty filename_infere of **Run.Program** by commandRan

# %%
# check if all values in commandRan starts with %Run
total_non_empty_commandRan = len(df_clean[(df_clean['verb'] == 'Run.Program') & (df_clean['commandRan'] != '')])
total_commandRan_start_Run = len(df_clean[df_clean['verb'] == 'Run.Program']['commandRan'].str.startswith('%Run'))

print(f"Total rows of not empty strings in commandRan for Run.Program : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Run in Run.Program : {total_commandRan_start_Run}")

# %% [markdown]
# There are values in commandRan which they include %Run Editor content.

# %%
# Apply
mask = (df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] == '') # use commandRan for ONLY empty filename_infere
df_clean.loc[mask, 'filename_infere'] = data_cleaning.extract_short_filename_from_commandRan_Run_Program(df_clean.loc[mask, 'commandRan'])

# %%
# After
total_Run_Program_empty = (df_clean[df_clean['verb']=='Run.Program']['filename_infere'] == '').sum()

print(f"Total rows of empty strings in Run.Program : {total_Run_Program_empty}")

# %% [markdown]
# **Interpretation** : we reduced empty filename_infere from 54,352 to 5,658 by **P_codeState** and **commandRan**.

# %%
df_clean[(df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] != '')][['filename_infere','commandRan','P_codeState']]

# %% [markdown]
# #### Check empty filename_infere of **Run.Debugger**

# %%
# Before
total_Run_Debugger       = len(df_clean[df_clean['verb']  == 'Run.Debugger'])
total_Run_Debugger_empty = (df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'] == '').sum()
total_Run_Debugger_nan   = df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Debugger : {total_Run_Debugger}")
print(f"Total number of empty strings in filename_infere in Run.Debugger : {total_Run_Debugger_empty}")
print(f"Total number of None in filename_infere in Run.Debugger : {total_Run_Debugger_nan}")

# %% [markdown]
# The process is same as Run.Program.

# %% [markdown]
# #### Fill empty filename_infere of **Run.Debugger** by commandRan

# %%
# check if all values in commandRan starts with %Debug
total_non_empty_commandRan       = len(df_clean[(df_clean['verb'] == 'Run.Debugger') & (df_clean['commandRan'] != '')])
total_commandRan_start_Debug     = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Debug').sum()
total_commandRan_start_NiceDebug = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Nice').sum()
total_commandRan_start_FastDebug = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Fast').sum()

print(f"Total rows of not empty strings in commandRan for Run.Debugger  : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Debug in Run.Debugger     : {total_commandRan_start_Debug}")
print(f"Total rows of commandRan starts with %NiceDebug in Run.Debugger : {total_commandRan_start_NiceDebug}")
print(f"Total rows of commandRan starts with %FastDebug in Run.Debugger : {total_commandRan_start_FastDebug}")

# %% [markdown]
# **Interpretation** All values in commandRan starts with %Debug, so I extract them but checking them if they are correct or not, is going to be in phase two.

# %%
# Apply
mask = df_clean['verb'] == 'Run.Debugger'
df_clean.loc[mask, 'filename_infere'] = data_cleaning.extract_short_filename_from_commandRan_Run_Debugger(df_clean.loc[mask, 'commandRan'])

# %%
# After
total_Run_Debugger_empty = (df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'] == '').sum()
print(f"Total number of empty strings in filename_infere in Run.Debugger : {total_Run_Debugger_empty}")

# %% [markdown]
# ### Check empty filename_infere of **Run.Command**

# %%
# Before
total_Run_command       = len(df_clean[df_clean['verb']  == 'Run.Command'])
total_Run_command_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_nan   = df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.command : {total_Run_command}")
print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of None in filename_infere in Run.command : {total_Run_command_nan}")

# %%
# check if all values in commandRan starts with %NiceDebug or %FastDebug
total_non_empty_commandRan       = len(df_clean[(df_clean['verb'] == 'Run.Command') & (df_clean['commandRan'] != '')])
total_commandRan_start_Debug     = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%Debug').sum()
total_commandRan_start_NiceDebug = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%NiceDebug').sum()
total_commandRan_start_FastDebug = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%FastDebug').sum()
total_commandRan_start_Run       = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%Run').sum()

print(f"Total rows of not empty strings in commandRan for Run.Command  : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Debug in Run.Command     : {total_commandRan_start_Debug}")
print(f"Total rows of commandRan starts with %NiceDebug in Run.Command : {total_commandRan_start_NiceDebug}")
print(f"Total rows of commandRan starts with %FastDebug in Run.Command : {total_commandRan_start_FastDebug}")
print(f"Total rows of commandRan starts with %Run in Run.Command       : {total_commandRan_start_Run}")

# %% [markdown]
# **Interpretation** 
#
# Only 70 values starts wtih %FastDebug, which I can use them to fill filename_infere, also there are names' of function in this column, that I can find the corresponding filename of the function in the commandRan by function find_filename_by_codestate() , I used the same function which is in phase two, that's why the name is by codestate, because I'm lazy and I didn't want to write another function with another name which does the same thing :)

# %%
# Apply 
mask = df_clean['verb'] == 'Run.Command'

# Get only cleaned values for those starting with %FastDebug
cleaned_values = data_cleaning.extract_short_filename_from_commandRan_Run_Command(df_clean.loc[mask, 'commandRan'])

df_clean.loc[cleaned_values.index, 'filename_infere'] = cleaned_values

# %%
# After
total_Run_command_empty     = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_not_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] != '').sum()

print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of NOT empty strings in filename_infere in Run.command : {total_Run_command_not_empty}")

# %%
# Apply : find_filename_by_commandRan for Run.command by looking commandRan
df_clean.loc[mask, 'filename_infere'] = df_clean.loc[mask, 'commandRan'].apply(
    lambda command: data_cleaning.find_filename_by_commandRan(all_TP_functions_name_except_TP1_and_TPGAME, pattern_files_name, command)
)

# %%
# this is for test you can remove it
df_clean[df_clean['_id.$oid'] == '66ed37fabd5a98b8f9da4354'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %%
# this is for test you can remove it
df_clean[df_clean['_id.$oid'] == '66ed3929bd5a98b8f9da4482'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %%
# After
total_Run_command_empty     = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_not_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] != '').sum()

print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of NOT empty strings in filename_infere in Run.command : {total_Run_command_not_empty}")

# %%
total_PcodeState_empty = (df_clean[df_clean['verb'] == 'Run.Command']['P_codeState'] == "").sum()
total_FcodeState_empty = (df_clean[df_clean['verb'] == 'Run.Command']['F_codeState'] == "").sum()

print(f"Total number of empty strings in P_codeState in Run.command : {total_PcodeState_empty}")
print(f"Total number of empty strings in F_codeState in Run.command : {total_FcodeState_empty}")

# %% [markdown]
# **Interpretation**
#
# By find_filename_by_commandRan(Mirabelle version), I found filename for 9,185 files, which is not bad, but still there are 48,705 traces for Run.command, which neither I could find any name from their commandRan nor in their filename column, these values will be treated in phase two.

# %% [markdown]
# ### Check empty filename_infere of **File.Open**

# %%
# Before
total_File_Open       = len(df_clean[df_clean['verb']  == 'File.Open'])
total_File_Open_empty = (df_clean[df_clean['verb'] == 'File.Open']['filename_infere'] == '').sum()
total_File_Open_nan   = df_clean[df_clean['verb'] == 'File.Open']['filename_infere'].isna().sum()

print(f"Total number of traces in File.Open : {total_File_Open}")
print(f"Total number of empty strings in filename_infere in File.Open : {total_File_Open_empty}")
print(f"Total number of None in filename_infere in File.Open : {total_File_Open_nan}")

# %% [markdown]
# ### Check empty filename_infere of **File.Save**

# %%
total_File_Save       = len(df_clean[df_clean['verb']  == 'File.Save'])
total_File_Save_empty = (df_clean[df_clean['verb'] == 'File.Save']['filename_infere'] == '').sum()
total_File_Save_nan   = df_clean[df_clean['verb'] == 'File.Save']['filename_infere'].isna().sum()

print(f"Total number of traces in File.Save : {total_File_Save}")
print(f"Total number of empty strings in filename_infere in File.Save : {total_File_Save_empty}")
print(f"Total number of None in filename_infere in File.Save : {total_File_Save_nan}")

# %% [markdown]
# ### Check empty filename_infere of **Docstring.Generate**

# %%
total_Docstring       = len(df_clean[df_clean['verb']  == 'Docstring.Generate'])
total_Docstring_empty = (df_clean[df_clean['verb'] == 'Docstring.Generate']['filename_infere'] == '').sum()
total_Docstring_nan   = df_clean[df_clean['verb'] == 'Docstring.Generate']['filename_infere'].isna().sum()

print(f"Total number of traces in Docstring.Generate : {total_Docstring}")
print(f"Total number of empty strings in filename_infere in Docstring.Generate : {total_Docstring_empty}")
print(f"Total number of None in filename_infere in Docstring.Generate : {total_Docstring_nan}")

# %%
df_clean[df_clean['verb'] == 'Docstring.Generate']['function']

# %% [markdown]
# Question: don't know how should I fill it.

# %% [markdown]
# ## 4.Save new clean dataframe

# %%
io_utils.write_csv(df_clean,INTERIM_DATA_DIR,None)
