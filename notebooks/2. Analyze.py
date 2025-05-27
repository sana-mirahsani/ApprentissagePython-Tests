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
# # Check code of Etude_sur_les_testes.py in Thomas version

# %% [markdown]
# # Analyze Workflow Overview:
# 1. Import Libraries
# 2. Load DataFrame
# 3. Analyze
#     3.1 Total number of students

# %% [markdown]
# ## Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import io_utils
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant import SORTED_SEANCE
import matplotlib.pyplot as plt

{
  "jupytext": {
    "formats": "ipynb,py:percent"
  }
}


# %% [markdown]
# ## Load DataFrame
# - Use functions in file **io_utils.py.py**
# - The csv file is the output of Preparation.ipynb

# %%
df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='acteur_nettoyage_2425.csv')

# %% [markdown]
# ## Analyze

# %% [markdown]
# ### Total number of students during semester

# %%
# Analyze
number_actor  = set(df['actor'])
number_binome = set(df['binome'])

total_students = number_actor.union(number_binome)

common_values = set(df['actor']).intersection(set(df['binome']))

print(f"Total number of students during the semester : {len(total_students)}")
print(f"Total number of students in common : {len(common_values)}")


# %%
# Test
Total_number_with_duplicates = len(number_actor) + len(number_binome)

print("Analyze Correct!") if Total_number_with_duplicates -  len(common_values) == len(total_students) else print("Error!") 

# %% [markdown]
# ### Total number of students during each week

# %%
df_common_name = pd.DataFrame(columns=['week', 'num_common_names', 'common_names'])

for seance in SORTED_SEANCE:
    actor_column = df[df['seance'] == seance]['actor']
    actor_binome = df[df['seance'] == seance]['binome']
    common_values = set(actor_column).intersection(set(actor_binome))

    # Append row
    df_common_name = pd.concat([
        df_common_name,
        pd.DataFrame({'week': [seance], 'num_common_names': [len(common_values)], 'common_names': [common_values]})
    ], ignore_index=True)


df_common_name

# %% [markdown]
# Normally there should NOT be any common name for each week between actor and binome column. It means there are students during the same TP, they were working alone and also as a groupe.
# So to calculate the total number of students for each TP, we should consider this problem to prevent counting a student twice.
# <br>
#
# Example below shows a student work alone at first and then conitues with another student but the binome changes again all in the same TP.

# %%
# Example of the error above
df[(df['seance'] == 'semaine_1') & ( (df['actor'] == 'hichame.haddou.etu'))][['actor','binome']].head(10)

# %%
df[(df['seance'] == 'semaine_1') & ( (df['binome'] == 'hichame.haddou.etu'))][['actor','binome']].head(10)

# %%
presence_actor  = df.groupby('seance')['actor'].unique() 
presence_actor  = presence_actor.loc[SORTED_SEANCE] # Sort in the order of semester

presence_binome  = df.groupby('seance')['binome'].unique() 
presence_binome  = presence_binome.loc[SORTED_SEANCE] # Sort in the order of semester

df_all_students = pd.DataFrame(columns=['week', 'num_students', 'name_students'])

for seance in SORTED_SEANCE:

    # Append row
    all_students = set(presence_actor[seance]).union(set(presence_binome[seance]))

    df_all_students = pd.concat([
        df_all_students,
        pd.DataFrame({'week': [seance], 'num_students': [len(all_students)], 'name_students': [all_students]})
    ], ignore_index=True)


df_all_students

# %%
# Test
for seance in SORTED_SEANCE:
    x = df_common_name[df_common_name['week']== seance]['num_common_names']
    real_number = len(presence_actor[seance]) + len(presence_binome[seance]) - int(x.iloc[0])

    if real_number != df_all_students[df_all_students['week']== seance]['num_students'].iloc[0]:
        print(f'Error in week : {seance}')
        break

print("Analyze Correct!")

# %%
df_all_students.plot(kind='bar', figsize=(10, 5), color='skyblue')
plt.title('Unique Actors per Seance')
plt.xlabel('Seance')
plt.ylabel('Number of Unique Actors')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %% [markdown]
# # ToDo
#
# - change seance by TP
