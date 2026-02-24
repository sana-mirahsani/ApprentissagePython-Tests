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
# ## Preparation Workflow Overview:
# 1. Import Libraries
# 2. Load DataFrame : acteur_nettoyage_2425.csv
# 3. Clean DataFrame:
#     
#     3.1 Add column **filename_infere**
#     <br>
#
#     3.2 Step1 : fill filename_infer by **filename** column
#     <br>
#
#     3.3 Step2 : fill filename_infere by **P_codestate** and **commandRan**
#     <br>
#
# 4. Save new DataFrame : phase1_nettoyage_fichiere.csv
#
# _________________________________________________________
# **Explanation** 
#
# In phase 1, the goal is only to find the filename but checking its correctness is considered in the next phase.
#
# Steps:
#  
#     1. Fill filename_infere column by values in filename column
#
#     2. Fill filename_infere for each verb, by their P_codestate or commandRan column.
#
# If there is a verb with zero empty filenam_infere, we skip it in this phase.

# %% [markdown] jupyter={"source_hidden": true}
# ## 1.Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'

import importlib

from src.features import io_utils, data_cleaning, data_testing, pipeline_utils

# reload the modules to make sure we have the latest version of the code
importlib.reload(io_utils)
importlib.reload(data_cleaning)
importlib.reload(data_testing)
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
    filename, out_dir_interim, _ = pipeline_utils.execute_by_pipeline(filename, out_dir_interim, out_dir_raw)
else:
    print("Running directly in Jupyter")
    filename = "traces260105"
    out_dir_interim = f"../data/interim/{filename}_20260205_093949"
    out_dir_raw = f"../data/raw/{filename}_20260205_093949"

    filename, out_dir_interim = pipeline_utils.execute_manually(filename, out_dir_interim, out_dir_raw)

match filename:
    case "traces250102":
        from src.data.variable_constant_2425 import TP_name, Type_TP, pattern_files_name, all_TP_functions_name_except_TP1_and_TPGAME
        
    case "traces260105":
        from src.data.variable_constant_2526 import TP_name, Type_TP, pattern_files_name, all_TP_functions_name_except_TP1_and_TPGAME


# %% [markdown]
# Fin des modifs à faire liées à l'exécution autonome / pipeline.

# %%
# input and output data for this notebook
input_file = filename + "_actor_clean" + ".csv"
output_file = filename + "_filename_phase1_clean" + ".csv"

# %% [markdown]
# ## 2.Load DataFrame

# %%
df = io_utils.reading_dataframe(dir= out_dir_interim, file_name=input_file)

# %%
# make a copy of the original dataframe
df_clean = df.copy()

# %%
df_clean.head()

# %% [markdown]
# ## 3.Clean DataFrame

# %% [markdown]
# ### 3.1 Add column **filename_infere**

# %%
col_index = df_clean.columns.get_loc('filename')
df_clean.insert(col_index + 1, 'filename_infere', '') 
df_clean.columns

# %% [markdown]
# ### 3.2 Step1 : fill filename_infer by filename column

# %%
old_num_empty, old_num_null = data_testing.check_empty_values_in_column(df_clean, 'filename_infere', "before")

# Fill the values
df_clean['filename_infere'] = data_cleaning.extract_short_filename(df_clean['filename'])

new_num_empty, new_num_null = data_testing.check_empty_values_in_column(df_clean, 'filename_infere', "after")

data_testing.check_to_pass_or_not(old_num_empty, new_num_empty, "empty values")
data_testing.check_to_pass_or_not(old_num_null, new_num_null, "null values")

# %% [markdown]
# ### 3.3 Step2 : fill filename_infere by P_codestate and commandRan

# %%
all_verbs = df_clean['verb'].unique()
print(all_verbs)

# %%
# check for each verb if the filename_infere is empty or not
all_verbs_with_their_states = {}

for verb in all_verbs:
    result = data_testing.Check_empty_filename_infere_in_verb(df_clean, verb)
    all_verbs_with_their_states[verb] = result

# %%
# Verbs with 0 mean all the filename_infere are filled, BUT we don't know if they are correctly filled or not, 
# we will check that later in phase 2
# Verbs with 1 mean, their filename_infere are not filled, so we try to fill them 
# by P_codestate and commandRan, if they have non-empty codestate or non-empty commandRan respectively, 
# and if they start with %Debug or %NiceDebug or %FastDebug or %Run
all_verbs_with_their_states

# %%
for i, (verb, states) in enumerate(all_verbs_with_their_states.items()):
    print(f"Processing verb {i+1}/{len(all_verbs_with_their_states)}: {verb}")

    # check before applying
    if states == 1:
        df_clean_masked = df_clean[df_clean['verb'] == verb]
        old_num_empty, old_num_null = data_testing.check_empty_values_in_column(df_clean_masked, column_name='filename_infere', time_happened="before")
    
    # apply the desicion function to fill filename_infere for the current verb
    df_clean = data_cleaning.desicion_function_to_fill_filename_infere(df_clean, verb, states, all_TP_functions_name_except_TP1_and_TPGAME, pattern_files_name)
    
    # check after applying
    if states == 1:
        df_clean_masked = df_clean[df_clean['verb'] == verb]
        new_num_empty, new_num_null = data_testing.check_empty_values_in_column(df_clean_masked, 'filename_infere', "after")

        data_testing.check_to_pass_or_not(old_num_empty, new_num_empty, "empty values")
        data_testing.check_to_pass_or_not(old_num_null, new_num_null, "null values")

    print("==================================================================")

# %%
df_clean['filename_infere'].head(50)

# %% [markdown]
# ## 4.Save new clean dataframe

# %%
io_utils.write_csv(df_clean,out_dir_interim,output_file)
