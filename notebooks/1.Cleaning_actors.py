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
# 2. Load DataFrame : traces250102_clean.csv
# 3. Clean DataFrame
#     <br>
#     3.1 Convert Time Format
#     <br>
#     3.2 Clean **Actor** Field
# 4. Save new DataFrame : acteur_nettoyage_2425.csv
#
#
# ____________________________________________
# **Explanation** 
#
# The goal is cleaning name of students, divide the actors and binomes, put them in 2 different columns actor and binome. Fortunately, all actors are cleaned as the result of test at the end shows.

# %% [markdown]
# ## Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import re
import numpy as np
from src.features import io_utils, data_cleaning

from src.data.constants import INTERIM_DATA_DIR

# %% [markdown]
# ## Load DataFrame
# - Use functions in file **io_utils.py.py**
# - The csv file is the output of process_raw_data

# %%
df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='traces250102_clean.csv')

# %% [markdown]
# ### Print 5 rows and columns of dataframe

# %%
df.head()

# %% [markdown]
# ### Create a copy of dataframe to compare later

# %%
df['actor']

# %%
df_clean = df.copy()
df_clean.columns

# %% [markdown]
# ## Clean DataFrame

# %% [markdown]
# ### Convert Time Format

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
# ### Clean **Actor** Field
# Process: 
# 1. Split actor and binome into 2 columns -> **df_clean = split_actor_binome()**
# 2. Delete emails at the end -> **df_clean = delete_end_email()**
# 3. Extract all the non matching name of actor with prenom.nom.etu -> **incorrect = not_a_correct_identifier()**
# 4. Delete all rows of nebut -> **df_clean = delete_actor_lines()** 
# 5. Remove actors or binomes name -> **df_clean = delete_name_actor_binome()**
# 6. Replace joker -> **df_clean = replace_jokers()**
# 7. Cleaning manually -> **df_clean = cleaning_manual_actors_2425()**

# %% [markdown]
# #### 1. Split actor and binome into 2 columns (This part delete '/')

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
# #### 2. Delete the email at the end

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
# #### 3. Extract all the non matching name of actor with prenom.nom.etu

# %%
incorrect_actor  = data_cleaning.not_a_correct_identifier(df_clean,'actor')
incorrect_binome = data_cleaning.not_a_correct_identifier(df_clean,'binome')

incorrect_actor, incorrect_binome

# %% [markdown]
# #### 4. Delete all rows of nebut

# %%
# Before
total = (df_clean['actor'] == 'nebut').sum()
print(f"total occurance of nebut : {total}") 

# %%
# Apply
df_clean = data_cleaning.delete_actor_lines(df_clean, "nebut")

# %%
# After
total = (df_clean['actor'] == 'nebut').sum()
print(f"total occurance of nebut : {total}") 
print("Successful!") if total == 0 else print("Error!") 

# %% [markdown]
# #### 5. Remove actors or binomes name ( just replace them by '' in binome column)

# %%
# Before in binome
total = (df_clean['binome'] == 'luc').sum()
print(f"total occurance : {total} ")

# %%
# Apply
df_clean = data_cleaning.delete_name_actor_binome(df_clean, 'binome', 'luc')

# %%
# After 
total = (df_clean['binome'] == 'luc').sum()
print(f"Total occurance of : {total}")
print("Successful!") if total == 0 else print("Error!") 

# %% [markdown]
# #### 6. Replace joker

# %% [markdown]
# Add the number total of matching marie is equal to the total occurance of two jokers

# %%
# Before
total_joker1 = (df_clean['binome'] == 'MI1304').sum()
total_joker2 = (df_clean['binome'] == 'MI1301').sum()

total = total_joker1 + total_joker2

print(f"Total occurance of joker 1 : {total_joker1}")
print(f"Total occurance of joker 2 : {total_joker2}")

# %%
# Apply
jokers_real_name = {
    'MI1304': 'mariama-sere.sylla.etu',
    'MI1301': 'mariama-sere.sylla.etu'
}
df_clean = data_cleaning.replace_jokers(df_clean, ['actor','binome'],jokers_real_name)

# %%
# After
total_joker1 = (df_clean['binome'] == 'MI1304').sum()
total_joker2 = (df_clean['binome'] == 'MI1301').sum()
total_new_name = (df_clean['binome'] == 'mariama-sere.sylla.etu').sum()

print(f"Total occurance of joker 1 : {total_joker1}")
print(f"Total occurance of joker 2 : {total_joker2}")

print("Successful!") if total_joker1 == 0 and total_joker1 == 0 and total_new_name == total else print("Error!") 

# %% [markdown]
# #### 7. Cleaning manually

# %%
# Before
total = (df_clean['actor'] == 'anis.younes.etu').sum()

print(f"Total occurance : {total}")

# %%
# Apply
df_clean = data_cleaning.cleaning_manual_actors_2425(df_clean, 'anis.younes.etu')

# %%
# After
total = (df_clean['actor'] == 'anis.younes.etu').sum()
print(f"Total occurance : {total}")

print("Successful!") if total == 0 else print("Error!") 

# %% [markdown]
# #### Retry Test for invalid actor or binome

# %%
incorrect_actor  = data_cleaning.not_a_correct_identifier(df_clean,'actor')
incorrect_binome = data_cleaning.not_a_correct_identifier(df_clean,'binome')

print(len(incorrect_actor),len(incorrect_binome))

print("Cleaning actor successful!") if len(incorrect_actor) == 0 and len(incorrect_binome) == 0 else print("Error!") 

# %% [markdown]
# #### Save new dataframe

# %%
io_utils.write_csv(df_clean,INTERIM_DATA_DIR,None) 
