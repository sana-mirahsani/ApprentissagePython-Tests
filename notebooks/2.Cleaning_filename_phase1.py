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

# %% [markdown] jupyter={"source_hidden": true}
# ## 1.Import Libraries

# %%
import sys
import importlib

sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
from src.features import io_utils, data_cleaning
#from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant_2425 import pattern_files_name, all_TP_functions_name_except_TP1_and_TPGAME

# reload the modules to make sure we have the latest version of the code
importlib.reload(io_utils)
importlib.reload(data_cleaning)


# %%
def execute_by_pipeline(filename, out_dir_interim, out_dir_raw):
    # check if the parameters are passed correctly
    assert filename is not None, "filename was not passed!"
    assert out_dir_interim is not None, "out_dir_interim missing"
    assert out_dir_raw is not None, "out_dir_raw missing"

    return filename, out_dir_interim, out_dir_raw


# %%
def execute_manually():
    # Define the path to the raw data file and the output directories (you can change them whatever you want)
    filename = "traces260105" # change this to the name of the file you want to process (without the .json extension)
    out_dir_interim = f"../data/interim/{filename}_20260205_093949"
    
    return filename, out_dir_interim


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
    filename, out_dir_interim, _ = execute_by_pipeline(filename, out_dir_interim, out_dir_raw)
else:
    print("Running directly in Jupyter")
    filename, out_dir_interim = execute_manually()

# %% [markdown]
# Fin des modifs à faire liées à l'exécution autonome / pipeline.

# %%
# input and output data for this notebook
input_file = filename + "_actor_clean" + ".csv"
output_file = filename + "_filename_phase1_clean" + ".csv"

# %% [markdown]
# ## 2.Load DataFrame

# %%
df_clean = io_utils.reading_dataframe(dir= out_dir_interim, file_name=input_file)

# %%
df_clean.head()

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
# move to test_function.py
def check_empty_values_in_column(df, column_name,time_happened):
    empty_values = (df[column_name] == '').sum()
    print(f"{time_happened} applying : Total number of empty strings in {column_name} = {empty_values}")

    null_values = df[column_name].isna().sum()
    print(f"{time_happened} applying : Total number of null values in {column_name} = {null_values}")

    return empty_values, null_values

def check_to_pass_or_not(old_value, new_value, name_value):
    if old_value < new_value:
        raise ValueError(f"New value {new_value} of {name_value} is smaller than its old value {old_value}. This should not happen.")
    elif old_value > new_value:
        print(f"Process is successfully completed for {name_value}.")
    else:
        print(f"Nothing has changed in {name_value}.")

def Check_empty_filename_infere_in_verb(df, verb_name):
    total_verb       = len(df[df['verb']  == verb_name])
    total_verb_empty = (df[df['verb'] == verb_name]['filename_infere'] == '').sum()
    total_verb_nan   = df[df['verb'] == verb_name]['filename_infere'].isna().sum()

    if total_verb > 0 and total_verb_empty == 0 and total_verb_nan == 0:
        print(f"All rows with verb '{verb_name}' have non-empty 'filename_infere'.") 
        return 0
    
    elif total_verb > 0 and (total_verb_empty > 0 or total_verb_nan > 0):
        print(f"Some rows with verb '{verb_name}' have {total_verb_empty} empty 'filename_infere' and {total_verb_nan} NaN 'filename_infere'.")
        return 1
    
    elif total_verb == 0:
        print(f"No rows with verb '{verb_name}' found in the DataFrame.")
        return 2


# %%
old_num_empty, old_num_null = check_empty_values_in_column(df_clean, 'filename_infere', "before")

# Fill the values
df_clean['filename_infere'] = data_cleaning.extract_short_filename(df_clean['filename'])

new_num_empty, new_num_null = check_empty_values_in_column(df_clean, 'filename_infere', "after")

check_to_pass_or_not(old_num_empty, new_num_empty, "empty values")
check_to_pass_or_not(old_num_null, new_num_null, "null values")

# %%
df_clean[['filename','filename_infere']].head(10)

# %%
all_verbs = df_clean['verb'].unique()
print(all_verbs)

# %%
# check for each verb if the filename_infere is empty or not
all_verbs_with_their_states = {}

for verb in all_verbs:
    result = Check_empty_filename_infere_in_verb(df_clean, verb)
    all_verbs_with_their_states[verb] = result

# %%
all_verbs_with_their_states


# %%
def check_P_codestate_and_commandRan(df, verb_name):
    values = {}

    # check with P_codestate
    total_non_empty_codestate     = (df[df['verb']  == verb_name]['P_codeState'] != '').sum()
    total_codestate_contain_trace = df[df['verb']  == verb_name]['P_codeState'].str.contains(r'<trace>.*\.py</trace>', regex=True, na=False).sum()
    
    # check with commandRan
    total_non_empty_commandRan       = len(df[(df['verb'] == verb_name) & (df['commandRan'] != '')])
    total_commandRan_start_Debug     = df[df['verb'] == verb_name]['commandRan'].str.startswith('%Debug').sum()
    total_commandRan_start_NiceDebug = df[df['verb'] == verb_name]['commandRan'].str.startswith('%NiceDebug').sum()
    total_commandRan_start_FastDebug = df[df['verb'] == verb_name]['commandRan'].str.startswith('%FastDebug').sum()
    total_commandRan_start_Run       = df[df['verb'] == verb_name]['commandRan'].str.startswith('%Run').sum()

    # save all values in a dictionary
    values['total_non_empty_codestate'] = total_non_empty_codestate
    values['total_codestate_contain_trace'] = total_codestate_contain_trace
    values['total_non_empty_commandRan'] = total_non_empty_commandRan
    values['total_commandRan_start_Debug'] = total_commandRan_start_Debug   
    values['total_commandRan_start_NiceDebug'] = total_commandRan_start_NiceDebug
    values['total_commandRan_start_FastDebug'] = total_commandRan_start_FastDebug
    values['total_commandRan_start_Run'] = total_commandRan_start_Run

    # print values to simply check them
    print(f"Total rows of not empty strings in P_codeState for {verb_name} : {total_non_empty_codestate}")
    print(f"Total rows of P_codeState contian <trace> : {total_codestate_contain_trace}")

    print(f"Total rows of not empty strings in commandRan for {verb_name} : {total_non_empty_commandRan}")
    print(f"Total rows of not empty strings in commandRan for {verb_name}  : {total_non_empty_commandRan}")
    print(f"Total rows of commandRan starts with %Debug in {verb_name}     : {total_commandRan_start_Debug}")
    print(f"Total rows of commandRan starts with %NiceDebug in {verb_name} : {total_commandRan_start_NiceDebug}")
    print(f"Total rows of commandRan starts with %FastDebug in {verb_name} : {total_commandRan_start_FastDebug}")
    print(f"Total rows of commandRan starts with %Run in {verb_name}       : {total_commandRan_start_Run}")

    return values


# %%
values_for_run_program = check_P_codestate_and_commandRan(df_clean, 'Run.Program')

# %%
check_P_codestate_and_commandRan(df_clean, 'Run.Command')


# %%
def fill_filename_infere_for_verb(df, verb_name, values_for_verb):
    # first : fill by P_codeState if it contains <trace>.*\.py</trace>
    if values_for_verb['total_non_empty_codestate'] > 0 and values_for_verb['total_codestate_contain_trace'] > 0:
        mask = (df['verb'] == verb_name) & (df['filename_infere'] == '')
        df.loc[mask, 'filename_infere'] = df.loc[mask, 'P_codeState'].map(data_cleaning.extract_short_filename_from_P_codestate)
    
    else:
        print(f"Cannot fill filename_infere for {verb_name} using P_codeState because there are no non-empty codestate or no codestate contain <trace>.*\.py</trace>.")
        
    # second : fill by commandRan if it starts with %Debug or %NiceDebug or %FastDebug or %Run
    if values_for_verb['total_non_empty_commandRan'] > 0:
        if verb_name == 'Run.Program':
            mask = (df['verb'] == 'Run.Program') & (df['filename_infere'] == '') # use commandRan for ONLY empty filename_infere
            df.loc[mask, 'filename_infere'] = df.loc[mask, 'commandRan'].map(data_cleaning.extract_short_filename_from_commandRan_Run_Program)
        
        elif verb_name == 'Run.Command':
            mask = df['verb'] == 'Run.Command'
            # Get only cleaned values for those starting with %FastDebug
            cleaned_values = data_cleaning.extract_short_filename_from_commandRan_Run_Command(df.loc[mask, 'commandRan'])
            df.loc[cleaned_values.index, 'filename_infere'] = cleaned_values

        elif verb_name == 'Run.Debugger':
            mask = df['verb'] == 'Run.Debugger'
            df.loc[mask, 'filename_infere'] = df.loc[mask, 'commandRan'].map(data_cleaning.extract_short_filename_from_commandRan_Run_Debugger)
        


    check_empty_values_in_column(df[df['verb'] == verb_name], 'filename_infere', f"after filling {verb_name} with P_codeState")

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

# %%
df_clean['verb'].unique()

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
io_utils.write_csv(df_clean,out_dir_interim,output_file)
