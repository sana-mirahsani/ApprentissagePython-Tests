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

# # Project Workflow Overview:
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


# ## Load DataFrame
# - Use functions in file **io_utils.py.py**
# - The csv file is the output of process_raw_data

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='traces250102_clean.csv')

# ### Print 5 rows and columns of dataframe

df.head()

# ## Clean DataFrame

# ### Convert Time Format

# Before
df[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# Apply
df = data_cleaning.clean_time(df)

# After
df[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# ### Clean **Actor** Field
# Process: 
# 1. Extract all the non matching name of actor with prenom.nom.etu -> **incorrect = not_a_correct_identifier()**
# 2. Delete emails at the end -> **df = delete_end_email()**
# 3. Delete all rows of nebut -> **df = delete_actor_lines()**
# 4. Split actor and binome into 2 columns -> **df = split_actor_binome()**
# 5. Remove actors or binomes name -> **df = delete_name_actor_binome()**
# 6. Replace None value by " " -> **df = replace_None_by_str()**
# 7. Replace joker -> **df = replace_jokers()**
# 8. Cleaning manually -> **df = cleaning_manual_actors_2425()**

# #### 1. Extract all the non matching name of actor with prenom.nom.etu

incorrect = data_cleaning.not_a_correct_identifier(df)
incorrect

# #### 2. Delete the email at the end

## Before deleting
print(df['actor'].unique())

# Apply deleting
df = data_cleaning.delete_end_email(df)
df['actor'].unique() # After deleting

# #### 3. Delete all rows of nebut

# +
# # Before
print(len(df[df['actor'] == 'nebut/'])) 

# Apply
df = data_cleaning.delete_actor_lines(df, "nebut/")

# After
print(len(df[df['actor'] == 'nebut/'])) 
# -

# ####  4. Split actor and binome into 2 columns

# Before
df['actor'].head(50)

# +
# Apply
df = data_cleaning.split_actor_binome(df)

# After
df[['actor','binome']]
# -

df['binome'].unique()

# #### 5. Remove actors or binomes name

# +
# Before in actor
count = (df['actor'] == 'nebut').sum()
print(f"The value appears {count} times for nebut.")

# Before in binome
count = (df['binome'] == 'luc').sum()
print(f"The value appears {count} times for luc.")

df = data_cleaning.delete_name_actor_binome(df, 'actor', 'nebut')
df = data_cleaning.delete_name_actor_binome(df, 'binome', 'luc')
    
# After in actor
count = (df['actor'] == 'nebut').sum()
print(f"The value appears {count} times for nebut.")

# After in binome
count = (df['binome'] == 'luc').sum()
print(f"The value appears {count} times for luc.")
# -

# #### 6. Replace None value by empty string

# +
# Before
print(f"Total value of None in actor: {len(df[df['actor'].isna()])}")
print(f"Total value of None in binome: {len(df[df['binome'].isna()])}")

# Apply
df = data_cleaning.replace_None_by_str(df,'binome')

# After
print("After")
print(f"Total value of None in actor: {len(df[df['actor'].isna()])}")
print(f"Total value of None in binome: {len(df[df['binome'].isna()])}")
# -


# #### 7. Replace joker

# +
# Before
print(len(df[df['binome'] == 'MI1304']), len(df[df['binome'] == 'MI1301']))

jokers_real_name = {
    'MI1304': 'mariama-sere.sylla.etu',
    'MI1301': 'mariama-sere.sylla.etu'
}

# Apply
df = data_cleaning.replace_jokers(df, ['actor','binome'],jokers_real_name)

# After
print("After")
print(len(df[df['binome'] == 'MI1304']), len(df[df['binome'] == 'MI1301']))
# -


# #### 8. Cleaning manually

# +
# Before
print(len(df[df['actor'] == 'anis.younes.etu']))

# Apply
df = data_cleaning.cleaning_manual_actors_2425(df, 'anis.younes.etu')

# After
print("After")
print(len(df[df['actor'] == 'anis.younes.etu@univ-lille.fr']))

# -

# Retry the test to see the number of incorrects
incorrect = data_cleaning.not_a_correct_identifier(df)
incorrect

# Save new df
io_utils.write_csv(df,INTERIM_DATA_DIR)

# ### Read clean dataframe

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='actuer_nettoyage_2425.csv')

df['actor'].unique()

# ### Clean **Filename** Field 
# Process:
# 1. Replace None values in filename by ""
# 2. Split filename, extract the filename
# 3. Fill empty filename for each verbe (like Run.Program)

# #### 1. Replace None values in filename by ""

# +
#Before 
print(df['filename'].isnull().sum())

# Apply 
df = data_cleaning.replace_None_by_str(df,'filename')

#After
print(df['filename'].isnull().sum())
# -

# #### 2. Split filename, extract the filename

# Before
df['filename'].head(50)

# Apply
df['filename'] = data_cleaning.extract_filename(df['filename'])

# After
df['filename'].head(50)

# #### 3. Fill empty filename for Run.Test

df[df['verb']=='Run.Test']['filename'].unique()

print(df[df['verb']=='Run.Test']['filename'].isna().sum())
print((df[df['verb']=='Run.Test']['filename'] == '').sum())

# There is no Nan or empty strings, OK for filename of Run.Test

# #### 3. Fill empty filename for Run.Program

# +
# Before
total       = len(df[df['verb']=='Run.Program'])
total_nan   = df[df['verb']=='Run.Program']['filename'].isna().sum()
total_empty = (df[df['verb']=='Run.Program']['filename'] == '').sum()

print(f"Total rows of Run.Program                  : {total}")
print(f"Total rows of Nan in Run.Program           : {total_nan}")
print(f"Total rows of empty strings in Run.Program : {total_empty}")
# -

# All values of filename for the rows where verb == Run.Program are an empty string.

# Fill by commandRan
mask = df['verb'] == 'Run.Program'
df.loc[mask, 'filename'] = data_cleaning.extract_filename_from_commandRan_Run_Program(df.loc[mask, 'commandRan'])

# +
# After
total_empty = (df[df['verb']=='Run.Program']['filename'] == '').sum()

print(f"Total rows of empty strings in Run.Program : {total_empty}")
# -

# The number of empty strings reduced from 54352 to 5791 thanks to commandRan.

df[df['verb']=='Run.Program'][['filename','commandRan']].head(50)

# Fill with P_codeState for the rest.
mask = (df['verb'] == 'Run.Program') & (df['filename'] == '')
df.loc[mask, 'filename'] = df.loc[mask, 'P_codeState'].map(data_cleaning.extract_filename_from_P_codestate_Run_Program)

# +
# After
total_empty = (df[df['verb']=='Run.Program']['filename'] == '').sum()

print(f"Total rows of empty strings in Run.Program : {total_empty}")
# -

# Empty strings reduced from 5791 to 4623 thanks to P_codeState.

df[df['verb']=='Run.Program'][['filename','P_codeState']].head(50)

# +
# Test for values with different pattern or empty string in filename of Run.Program
pattern = re.compile(r'^[\w\-]+\.py$') # Pattern : name(any number or space).py

filenames       = df[df['verb']=='Run.Program']['filename']
invalid_indices = filenames[~filenames.apply(lambda val: isinstance(val, str)  and bool(pattern.fullmatch(val.strip())))].index # Extract invalid index

mask = (df['verb'] == 'Run.Program') & (df['filename'] == '')

invalid_indices = set(invalid_indices) - set(df.loc[mask,'filename'].index) # Remove empty strings

print(f"Total rows    : {len(df[df['verb']=='Run.Program']['filename'])}")
print(f"Invalid rows  : {len(invalid_indices)}")
print(f"Empty strings : {len(df.loc[mask,'filename'])}")
# -

# From 54352 rows of Run.program, there are 3643 rows which doesn't have the same pattern as name.py in filename; and 4623 rows are empty string in filename.

# Check what are these 3643, first use unique() on their filename to reduces the number of redundent values.
unique_invalid_value = df.loc[list(invalid_indices)]['filename'].unique()
len(unique_invalid_value), unique_invalid_value

# There are 236 values not in the exactly pattern (some of them are correct).

# Check empty strings
#pd.set_option('display.max_rows', None) # To show all rows remove the '#'
#pd.set_option('display.max_columns', None) # To show all rows remove the '#'
df.loc[mask,['filename','commandRan','P_codeState']]

# Empty strings without commandRan or P_codeState

# #### 3. Fill empty filename for Run.Debogger

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
# - Finish filename cleaning
# - Decide what to do with empty strings of Run.Program
# - Calculate the total name of student (after cleaning process)
# - init_data.py (look at it and the readme of Thomas)
# - Anonymization : actor, binom, P-code state, F-code state, columns_with_path
# - Process raw data
# - Add column that trace the output ?? I don't remember
# - Look at notebooknettoyage of Thomas to add a column
