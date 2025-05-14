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

# ## Main function has the entire process of 
# - Reading
# - data_cleaning
# - Anonymazing

# ### Library

import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import io_utils, data_cleaning, data_anonymization
#from tests import test_preprocessing, test_anonymization
from src.data.constants import INTERIM_DATA_DIR

# ### Reading dataframe
# - Use functions in file **io_utils.py.py**
# - The csv file is the output of process_raw_data

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='traces250102_clean.csv')

# ### Print 5 rows and columns of dataframe

io_utils.column_and_head(df)

# ### Clean dataframe
# - Change time format
# - Clean actor column

# #### Change time format

# Before apply 'clean_time"
df[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

df = data_cleaning.clean_time(df)

# #### After cleaning time

df[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# #### Clean actor column 
# 1. Extract all the non matching name of actor with prenom.nom.etu -> **incorrect = not_a_correct_identifier()**
# 2. Delete the email at the end -> **df = delete_end_email()**
# 3. Delete all rows of nebut -> **df = delete_actor_lines()**
# 4. Split actor and binome into 2 columns -> **df = split_actor_binome()**
# 5. Remove actors or binomes name -> **df = delete_name_actor_binome()**
# 6. Replace None value by " " -> **df = replace_None_by_str()**
# 7. Replace joker -> **df = replace_jokers()**
# 8. Cleaning manually -> **df = cleaning_manual_actors_2425()**

# 1. Extract all the non matching name of actor with prenom.nom.etu
incorrect = data_cleaning.not_a_correct_identifier(df)
incorrect

# 2. Delete the email at the end
## Before deleting
print(df['actor'].unique())

# Apply deleting
df = data_cleaning.delete_end_email(df)
df['actor'].unique() # After deleting

# 3. Delete all rows of nebut
print(len(df[df['actor'] == 'nebut/'])) # Before
df = data_cleaning.delete_actor_lines(df, "nebut/")
print(len(df[df['actor'] == 'nebut/'])) # After

# 4. Split actor and binome into 2 columns
df = data_cleaning.split_actor_binome(df)
df[['actor','binome']]

df['binome'].unique()

# +
# 5. Remove actors or binomes name

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

# +
# 6. Replace None value by " "

# Before
print(f"Total value of None in actor: {len(df[df['actor'].isna()])}")
print(f"Total value of None in binome: {len(df[df['binome'].isna()])}")

df = data_cleaning.replace_None_by_str(df,'binome')

# After
print("After")
print(f"Total value of None in actor: {len(df[df['actor'].isna()])}")
print(f"Total value of None in binome: {len(df[df['binome'].isna()])}")


# +
#7. Replace joker

# Before
print(len(df[df['binome'] == 'MI1304']), len(df[df['binome'] == 'MI1301']))

jokers_real_name = {
    'MI1304': 'mariama-sere.sylla.etu',
    'MI1301': 'mariama-sere.sylla.etu'
}

df = data_cleaning.replace_jokers(df, ['actor','binome'],jokers_real_name)

# After
print("After")
print(len(df[df['binome'] == 'MI1304']), len(df[df['binome'] == 'MI1301']))


# +
# 8. Cleaning manually
# Before

print(len(df[df['actor'] == 'anis.younes.etu']))
df = data_cleaning.cleaning_manual_actors_2425(df, 'anis.younes.etu')

# After
print("After")
print(len(df[df['actor'] == 'anis.younes.etu@univ-lille.fr']))

# -

# Retry the test to see the number of incorrects
incorrect = data_cleaning.not_a_correct_identifier(df)
incorrect

# # TODO
# - Add test functions
# - Save csv file
# - Calculate the total name of student (after cleanign process)
# - init_data.py (look at it and the readme of Thomas)
# - Anonymization : actor, binom, P-code state, F-code state, columns_with_path
# - Process raw data
# - Add column that trace the output ?? I don't remember
# - Look at notebooknettoyage of Thomas to add a column

#

# +
### Save dataframe in csv file
#io_utils.write_csv(df = df, dir = INTERIM_DATA_DIR)
# -

#

# #### Anonymization
# Create a new dataframe with three columns : 'actor', 'binom' , 'anonymized_actor'

# +
#anonymized_df = df[['actor', 'binom']].copy() 
#anonymized_df['anonymized_actor'] = df.apply(data_anonymization.anonymize_actor, axis=1)
# -

# Replace column actor and binom by anonymized_actor

# +
#df[['actor', 'binom']] = df.apply(data_anonymization.anonymize_actor)
# -

#
