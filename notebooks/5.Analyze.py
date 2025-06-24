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
# 2. Load DataFrame : Final_nettoyage_2425.csv
# 3. Analyze
#     3.1 Total number of students
#

# %% [markdown]
# ## Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
from src.features import io_utils
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant_2425 import SORTED_SEANCE, TP_NAME
import matplotlib.pyplot as plt


# %% [markdown]
# ## Load DataFrame

# %%
df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='Final_nettoyage_2425.csv')

# %% [markdown]
# ## Analyze

# %% [markdown]
# ### Total number of students during semester

# %%
number_actor  = set(df['actor'])
number_binome = set(df['binome'])

total_students = number_actor.union(number_binome)

print(f"Total number of students during the semester : {len(total_students)}")


# %% [markdown]
# ### Total number of students during each week

# %%
df_students_per_week = pd.DataFrame(columns=['week', 'number of students'])

for seance in SORTED_SEANCE:
    actor_column = df[df['seance'] == seance]['actor']
    column_binome = df[df['seance'] == seance]['binome']
    all_students = set(actor_column).union(set(column_binome))

    # Append row
    df_students_per_week = pd.concat([
        df_students_per_week,
        pd.DataFrame({'week': [seance], 'number of students': len(all_students)})
    ], ignore_index=True)


df_students_per_week

# %%
labels = SORTED_SEANCE
values = df_students_per_week['number of students']

plt.subplots(figsize=(17, 6))
plt.bar(labels, values)
plt.title("Nombre d'eleves present par seance")
plt.xlabel("Seance")
plt.ylabel("Nombre d'eleves")
plt.show()

# %% [markdown]
# **Interpretation**

# %% [markdown]
# ### Total number of students during each TP

# %%
# replace the empty strings in TP and Type_TP columns by not_found
df['TP'] = df['TP'].replace('','not_found')
df['Type_TP'] = df['Type_TP'].replace('','not_found')

# create a list of order of TP
TP_ORDER = TP_NAME
TP_ORDER.append('not_found')

# %%
df_students_per_TP = pd.DataFrame(columns=['TP', 'number of students'])

for tp in TP_ORDER:
    actor_column  = df[df['TP'] == tp]['actor']
    column_binome = df[df['TP'] == tp]['binome']
    all_students  = set(actor_column).union(set(column_binome))

    # Append row
    df_students_per_TP = pd.concat([
        df_students_per_TP,
        pd.DataFrame({'TP': [tp], 'number of students': len(all_students)})
    ], ignore_index=True)


df_students_per_TP

# %%
# remove the last value : filename_not_found
df_students_per_TP_filtered = df_students_per_TP.iloc[:11]

labels = df_students_per_TP_filtered['TP']
values = df_students_per_TP_filtered['number of students']

plt.subplots(figsize=(17, 6))
plt.bar(labels, values)
plt.title("Nombre d'eleves par TP")
plt.xlabel("TP")
plt.ylabel("Nombre d'eleves")
plt.show()

# %% [markdown]
# **Interpretation**

# %% [markdown]
# ### Type of TP

# %%
df_students_per_Type_Tp = pd.DataFrame(columns=['TP','TP_mani', 'TP_prog']) # create the df
Type_TPs = ['TP_mani', 'TP_prog'] # create a list of different types of tp

for tp in TP_NAME:

    all_types_tp = []   # saving all numbers of types of TP

    for type_tp in Type_TPs:

        actor_column  = df[(df['TP'] == tp) & (df['Type_TP'] == type_tp)]['actor']
        column_binome = df[(df['TP'] == tp) & (df['Type_TP'] == type_tp)]['binome']

        all_students  = set(actor_column).union(set(column_binome))
        all_types_tp.append(len(all_students))

    # Append row to df
    df_students_per_Type_Tp = pd.concat([
        df_students_per_Type_Tp,
        pd.DataFrame({'TP': [tp], 'TP_mani': all_types_tp[0], 'TP_prog': all_types_tp[1]})
    ], ignore_index=True)


df_students_per_Type_Tp

# %%
df_students_per_Type_Tp.set_index('TP')[['TP_mani', 'TP_prog']].plot(kind='bar', figsize=(12, 6))

plt.title("Number of Students in Each Type of TP")
plt.ylabel("Number of Students")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Type")
plt.tight_layout()
plt.show()

# %%
# create a crossttable of two columns of df
count_table = pd.crosstab(df['TP'], df['Type_TP'])
count_table = count_table.reindex(TP_ORDER)
count_table

# %%
count_table.plot(kind='bar', figsize=(14, 6))

plt.title("Number of Files per TP and Type_TP")
plt.ylabel("Number of Files")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Type_TP")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### Number of student using each verb in each TP

# %%
verbs = ['Run.Command','Run.Program','Run.Test','Run.Debugger']

df_students_per_verb = pd.DataFrame(columns=['TP','Run.Command', 'Run.Program','Run.Test','Run.Debugger']) # create the df

for tp in TP_NAME:

    df_filtered = df[df['TP'] == tp] # filter on TP
    number_of_students = []

    for verb in verbs:

        actor_column  = df_filtered[df_filtered['verb'] == verb]['actor']

        binome_column = df_filtered[df_filtered['verb'] == verb]['binome']

        all_students  = set(actor_column).union(set(binome_column))
        number_of_students.append(len(all_students))

    # Append row to df
    df_students_per_verb = pd.concat([
        df_students_per_verb,
        pd.DataFrame({'TP': [tp], 'Run.Command': number_of_students[0], 'Run.Program': number_of_students[1], 'Run.Test': number_of_students[2], 'Run.Debugger': number_of_students[3]})
    ], ignore_index=True)

df_students_per_verb

# %%
df_students_per_verb[:11].set_index('TP')[['Run.Command', 'Run.Program','Run.Test','Run.Debugger']].plot(kind='bar', figsize=(12, 6))

plt.title("Number of students per verb in each TP")
plt.ylabel("Number of students")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Verbs")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### Number of using of each verb in each TP

# %%
df_usage_per_verb = pd.DataFrame(columns=['TP','Run.Command', 'Run.Program','Run.Test','Run.Debugger']) # create the df

for tp in TP_NAME:

    df_filtered = df[df['TP'] == tp] # filter on TP
    number_of_usage = []

    for verb in verbs:

        total_number = (df_filtered['verb'] == verb).sum()

        number_of_usage.append(total_number)

    # Append row to df
    df_usage_per_verb = pd.concat([
        df_usage_per_verb,
        pd.DataFrame({'TP': [tp], 'Run.Command': number_of_usage[0], 'Run.Program': number_of_usage[1], 'Run.Test': number_of_usage[2], 'Run.Debugger': number_of_usage[3]})
    ], ignore_index=True)

df_usage_per_verb

# %%
df_usage_per_verb[:11].set_index('TP')[['Run.Command', 'Run.Program','Run.Test','Run.Debugger']].plot(kind='bar', figsize=(12, 6))

plt.title("Number of usage per verb in each TP")
plt.ylabel("Number of usage")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Verbs")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### Number of using of each verb in each TP_prog

# %%
df_usage_per_verb_TP_prog = pd.DataFrame(columns=['TP','Run.Command', 'Run.Program','Run.Test','Run.Debugger']) # create the df

for tp in TP_NAME:

    df_filtered = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')] # filter on TP
    number_of_usage = []

    for verb in verbs:

        total_number  = (df_filtered['verb'] == verb).sum()

        number_of_usage.append(total_number)

    # Append row to df
    df_usage_per_verb_TP_prog = pd.concat([
        df_usage_per_verb_TP_prog,
        pd.DataFrame({'TP': [tp], 'Run.Command': number_of_usage[0], 'Run.Program': number_of_usage[1], 'Run.Test': number_of_usage[2], 'Run.Debugger': number_of_usage[3]})
    ], ignore_index=True)

df_usage_per_verb_TP_prog

# %%
df_usage_per_verb_TP_prog[:11].set_index('TP')[['Run.Command', 'Run.Program','Run.Test','Run.Debugger']].plot(kind='bar', figsize=(12, 6))

plt.title("Number of usage per verb in each TP_prog")
plt.ylabel("Number of usage")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Verbs")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### Number of using of each verb in each seance only for TP_prog

# %%
df_usage_per_verb_TP_prog_semaine = pd.DataFrame(columns=['seance','Run.Command', 'Run.Program','Run.Test','Run.Debugger']) # create the df

for seance in SORTED_SEANCE:

    df_filtered = df[(df['seance'] == seance) & (df['Type_TP'] == 'TP_prog')] # filter on seance and TP_prog
    number_of_students = []

    for verb in verbs:

        actor_column  = df_filtered[df_filtered['verb'] == verb]['actor']

        binome_column = df_filtered[df_filtered['verb'] == verb]['binome']

        all_students  = set(actor_column).union(set(binome_column))
        number_of_students.append(len(all_students))

    # Append row to df
    df_usage_per_verb_TP_prog_semaine = pd.concat([
        df_usage_per_verb_TP_prog_semaine,
        pd.DataFrame({'seance': [seance], 'Run.Command': number_of_students[0], 'Run.Program': number_of_students[1], 'Run.Test': number_of_students[2], 'Run.Debugger': number_of_students[3]})
    ], ignore_index=True)

df_usage_per_verb_TP_prog_semaine

# %%
df_usage_per_verb_TP_prog_semaine.set_index('seance')[['Run.Command', 'Run.Program','Run.Test','Run.Debugger']].plot(kind='bar', figsize=(12, 6))

plt.title("Number of students per verb in each TP_prog of each seance")
plt.ylabel("Number of usage")
plt.xlabel("seance")
plt.xticks(rotation=45)
plt.legend(title="Verbs")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### Get number of students who used 'Print' statement

# %%
seance_before_print = ['semaine_1', 'semaine_2', 'semaine_3', 'semaine_4']
df_seance : pd.DataFrame = df[df['seance'].isin(seance_before_print)]

run_verb = ['Run.Command', 'Run.Program', 'Run.Test', 'Run.Debugger']
df_run : pd.DataFrame = df[df['verb'].isin(run_verb)]

df_run[(df_run['P_codeState'].str.contains('print', case=False, regex=True)) |
                  (df_run['F_codeState'].str.contains('print', case=False, regex=True)) |
                  (df_run['commandRan'].str.contains('print', case=False, regex=True))
                ]
df_run

# %% [markdown]
# # OLD

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

# %%
# check if you need them or not 
df_all_students = data_cleaning.extract_students_each_week(df_clean)

students_semaine_2 = list(df_all_students[df_all_students['week'] == 'semaine_2']['name_students'].iloc[0])
students_semaine_2 = [item for item in students_semaine_2 if isinstance(item, str) and item.strip() != "" and item.lower() != "nan"] # remove the empty strings or nan

df_analyze_students_semaine2 = data_cleaning.get_student_totals_each_week(df_clean, students_semaine_2, pattern) # takes maximum 1 min, it's normal

# %%
# Before
students_trace_zero = df_analyze_students_semaine2[df_analyze_students_semaine2['total_trace'] == 0]['name'].unique()
print(f" Number of students with zero trace in semaine_2 : {len(students_trace_zero)}")

# %% [markdown]
# Interpretation : they are students who were binome of an actor, that's why they don't have any trace, but it doesn't mean that they didn't work during this semaine, so we have to pick the values from their actors and put as their value in df_analyze_students_semaine2.

# %%
# Apply : Find actors 
df_of_students_zero_trace = data_cleaning.actors_of_student_with_zero_trace(df_clean, students_trace_zero)
df_of_students_zero_trace

# %%
# check if there is any binome with more than one actor
errors = df_of_students_zero_trace[df_of_students_zero_trace['its_actor'].apply(lambda x: not (isinstance(x, (list, np.ndarray)) and len(x) == 1))]
if errors.empty:
    print("No there is no binome with more than one actor")

# %%
# Apply : Fill values of binome by their atcor's values
df_analyze_students_semaine2 = data_cleaning.fill_values_of_binome_with_zero_trace(df_of_students_zero_trace,df_analyze_students_semaine2)

# %% [markdown]
# # ToDo
#
# - change seance by TP
# - change the nale x variable                                   
#
# - semaine_5: there are two sessions, but only one sessions they weere working, because the second session was contrl TP and the internet was cut
# - add the part to see how many filename_infere are empty in each semaine
# - Ignore the part of **utilisation print**

# %% [markdown]
# +
