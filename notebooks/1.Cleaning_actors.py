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
# 2. Load DataFrame : filename_clean.csv
# 3. Clean DataFrame
#     <br>
#     3.1 Convert Time Format
#     <br>
#     3.2 Clean **Actor** Field
# 4. Filter on research_usage
# 5. Save new DataFrame : filename_actor_clean.csv
# ____________________________________________
# **Explanation** 
#
# The goal is cleaning name of students, divide the actors and binomes, put them in 2 different columns actor and binome. Fortunately, all actors are cleaned as the result of test at the end shows.

# %% [markdown]
# ## 1.Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import importlib

from src.features import io_utils, data_cleaning, pipeline_utils

#from src.data.constants import INTERIM_DATA_DIR
path_valid_students = "../data/logins_L1_2526.txt"

# reload the modules to make sure we have the latest version of the code
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
    filename = "traces260105" # change this to the name of the file you want to process (without the .json extension)
    out_dir_interim = f"../data/interim/{filename}_20260205_093949"
    out_dir_raw = f"../data/raw/{filename}_20260205_093949"
    filename, out_dir_interim, _ = pipeline_utils.execute_manually(filename, out_dir_interim, out_dir_raw)


# %% [markdown]
# Fin des modifs à faire liées à l'exécution autonome / pipeline.

# %%
input_file = filename + "_clean" + ".csv"
output_file = filename + "_actor_clean" + ".csv"

# %% [markdown]
# ## 2.Load DataFrame
# - Use functions in file **io_utils.py.py**
# - The csv file is the output of process_raw_data

# %%
df = io_utils.reading_dataframe(dir= out_dir_interim, file_name= input_file)

# %% [markdown]
# ### 1.Print 5 rows and columns of dataframe

# %%
df.head()

# %% [markdown]
# ### 2.Create a copy of dataframe to compare later

# %%
df['actor']

# %%
df_clean = df.copy()
df_clean.columns

# %% [markdown]
# ## 3.Clean DataFrame

# %% [markdown]
# ### 1.Convert Time Format

# %%
# Before
df_clean[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# %%
# Apply
df_clean = data_cleaning.clean_time(df_clean)

# %%
# After
df_clean[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# %% [markdown]
# **Interpretation** 
#
# I don't what exactly is cleaned or change in time.format but since Thomas did this part, I just copied, maybe there are some traces that are cleaned but since there are 300k traces is hard to find them. 

# %% [markdown]
# ### 2.Clean **Actor** Field
# Process: 
# 1. Split actor and binome into 2 columns -> **df_clean = split_actor_binome()**
# 2. Delete emails at the end -> **df_clean = delete_end_email()**
# 3. Find and correct invalid names

# %% [markdown]
# #### 1. Split actor and binome into 2 columns (remove '/' and same for each year)

# %%
# Before 
total_slash = df_clean['actor'].str.contains('/').sum()
total_nan   = df_clean['actor'].isna().sum()
total_empty = (df_clean['actor']=='').sum()

print(f"Total number of rows : {len(df_clean)}")
print(f"Total number of rows include / : {total_slash}")
print(f"Total number of Nan rows : {total_nan}")
print(f"Total number of empty strings : {total_empty}")

# %%
# Apply
df_clean = data_cleaning.split_actor_binome(df_clean)

# %%
# After
total_slash_actor  = df_clean['actor'].str.contains('/').sum()
total_slash_binome = df_clean['binome'].str.contains('/').sum() # double_check

print(f"Total number of rows include / in actor: {total_slash_actor}")
print(f"Total number of rows include / in binome: {total_slash_binome}")

print("Successful!") if total_slash_actor == 0 and total_slash_binome == 0 else print("Error!") 

# %%
df_clean['actor']

# %% [markdown]
# #### 2. Delete the email at the end (same for each year)

# %%
# Before (check actor and binom)
total_email_actor  = df_clean['actor'].str.contains('@').sum()
total_email_binome = df_clean['binome'].str.contains('@').sum()

print(f"Total number of rows include @ in actor:   {total_email_actor}")
print(f"Total number of rows include @ in binome : {total_email_binome}")

# %%
# Apply 
df_clean = data_cleaning.delete_end_email(df_clean)

# %%
# After
total_email_actor = df_clean['actor'].str.contains('@').sum()

print(f"Total number of rows include @ in actor: {total_email_actor}")

print("Successful!") if total_email_actor == 0 else print("Error!") 

# %% [markdown]
# #### 3. Find and correct invalid names (Depends on the year)

# %%
if filename == "traces260105":
    
    incorrect_actor  = data_cleaning.check_invalid_identifier_by_login_file(df_clean,'actor', path_valid_students)
    incorrect_binome = data_cleaning.check_invalid_identifier_by_login_file(df_clean,'binome', path_valid_students)
    print(f"Total number of incorrect actors 2526: {len(incorrect_actor)}")
    print(f"Total number of incorrect binomes 2526: {len(incorrect_binome)}")

    # remove mirabell.nebut
    df_clean = data_cleaning.delete_actor_lines(df_clean, incorrect_actor[0])
    
    # replace 'tele-djidjoe-flora.da-sylveira.etu' by 'flora.sylveira.etu'
    jokers_real_name = {
    'tele-djidjoe-flora.da-sylveira.etu': 'flora.sylveira.etu'
    }
    
    def_clean = data_cleaning.replace_jokers(df_clean, ['actor'], jokers_real_name)

    # check again
    incorrect_actor  = data_cleaning.check_invalid_identifier_by_login_file(df_clean,'actor', path_valid_students)
    incorrect_binome = data_cleaning.check_invalid_identifier_by_login_file(df_clean,'binome', path_valid_students)
    
    if len(incorrect_actor) == 0 and len(incorrect_binome) == 0:
        print("Removing invalid actors and binomes completed!")
    else:
        raise ValueError("There are still incorrect actors or binomes. Please check the lists of incorrect actors and binomes and clean them manually.")
    
elif filename == "traces250105":
    incorrect_actor  = data_cleaning.check_invalid_identifier_by_pattern(df_clean,'actor')
    incorrect_binome = data_cleaning.check_invalid_identifier_by_pattern(df_clean,'binome')
    print(incorrect_actor, incorrect_binome)
    print(f"Total number of incorrect actors 2425: {len(incorrect_actor)}")
    print(f"Total number of incorrect binomes 2425: {len(incorrect_binome)}")

    # remove mirabell.nebut
    df_clean = data_cleaning.delete_actor_lines(df_clean, "nebut")

    # replace binom=luc by empty string
    df_clean = data_cleaning.delete_name_actor_binome(df_clean, 'binome', 'luc')

    # replace jokers by real names
    jokers_real_name = {
    'MI1304': 'mariama-sere.sylla.etu',
    'MI1301': 'mariama-sere.sylla.etu'
    }
    df_clean = data_cleaning.replace_jokers(df_clean, ['actor','binome'],jokers_real_name)

    # cleaning manually, you can modify this function
    df_clean = data_cleaning.cleaning_manual_actors_2425(df_clean, 'anis.younes.etu')

    # check again
    incorrect_actor  = data_cleaning.check_invalid_identifier_by_pattern(df_clean,'actor')
    incorrect_binome = data_cleaning.check_invalid_identifier_by_pattern(df_clean,'binome')

    print(f"Total number of incorrect actors 2425: {len(incorrect_actor)}")
    print(f"Total number of incorrect binomes 2425: {len(incorrect_binome)}")

    if len(incorrect_actor) == 0 and len(incorrect_binome) == 0:
        print("Removing invalid actors and binomes completed!")
    else:
        raise ValueError("There are still incorrect actors or binomes. Please check the lists of incorrect actors and binomes and clean them manually.")

# %%
df_clean[df_clean['binome'] == '']

# %% [markdown]
# ## 4. Filter on research_usage

# %%
filtered_df_clean = data_cleaning.propage_chgt_avis_research_OK(df_clean)

# %% [markdown]
# ## 5.Save new dataframe

# %%
df_clean[df_clean['binome'] !=''][['binome', 'actor', 'research_usage']]

# %%
df_clean[df_clean['research_usage'] == ''][['actor','research_usage']]

# %%
actors = set(filtered_df_clean[(filtered_df_clean['research_usage'] == '0.0') & (filtered_df_clean['research_usage'] == '1.0')]['actor'])
binomes = set(filtered_df_clean['binome'])
binomes_and_actors = actors.intersection(binomes)

for name in binomes_and_actors:
    
    
    value = filtered_df_clean[(filtered_df_clean['actor'] == name) | (filtered_df_clean['binome'] == name)]['research_usage'].unique()
    
    if len(value) == 3:
        print(name)

# %%
actors = set(filtered_df_clean['actor'])
binomes = set(filtered_df_clean['binome'])
binomes_and_actors = actors.intersection(binomes)

for name in binomes_and_actors:
    
    
    value = filtered_df_clean[(filtered_df_clean['actor'] == name) | (filtered_df_clean['binome'] == name)]['research_usage'].unique()
    
    if len(value) == 3:
        print(name)

# %%
io_utils.write_csv(df_clean,out_dir_interim, output_file) 
