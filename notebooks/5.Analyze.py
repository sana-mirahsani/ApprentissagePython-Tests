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
import ast
from src.features import io_utils
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant_2425 import SORTED_SEANCE, TP_NAME
import matplotlib.pyplot as plt


# %% [markdown]
# ## Load DataFrame

# %%
df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase2_nettoyage_fichiere.csv')

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

plt.title("Number of trace per TP and Type_TP")
plt.ylabel("Number of trace")
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

# %%
from src.data.variable_constant_2425 import SORTED_SEANCE, all_TP_functions_name 
import re
from src.data.variable_constant_2425 import FILES_BY_TP
from src.features import data_cleaning

# Global variable pattern
pattern = ''
for tp_name in FILES_BY_TP:

    file_name = '|'.join(tp_name)
    pattern = pattern +  file_name + '|'

pattern = pattern  + 'Irrelevant'


# %%
def find_strange_filename_infere(pattern,TP,verb):

    # create the lists
    filename_empty_index, filename_case1_index, filename_case2_index = [], [] , []

    for index, row in df[(df['TP'] == TP) & (df['verb'] == verb)].iterrows():

        match_state = re.search(pattern, row['P_codeState']) # search if the name of file is in the codeState

        if match_state:
            
            # if the name between <trace></trace> is different from the name in filename_infere
            if row['filename_infere'] != match_state.group():
                filename_case1_index.append(index)
                
        else:
            # if there is no name between <trace></trace> 
            filename_infere = data_cleaning.find_filename_by_function_name(all_TP_functions_name,row['P_codeState'])
            if filename_infere == '': # if there is no good function's name in P_codeState
                filename_empty_index.append(index)

            else: # if the filename found by function's name is not same as the name in filename_infere
                if row['filename_infere'] != filename_infere:
                    filename_case2_index.append(index) 

    return filename_empty_index, filename_case1_index, filename_case2_index


# %%
df_strange_filenames_Run_Test = pd.DataFrame(columns=['TP','empty_filename', 'filename_case1','filename_case2']) # create the df

for tp in TP_NAME:

    empty_filename, filename_case1, filename_case2 = find_strange_filename_infere(pattern,tp,'Run.Test')
    
    # Append row to df
    df_strange_filenames_Run_Test = pd.concat([
        df_strange_filenames_Run_Test,
        pd.DataFrame({'TP': [tp], 'empty_filename': [empty_filename], 'filename_case1': [filename_case1], 'filename_case2': [filename_case2]})
    ], ignore_index=True)

df_strange_filenames_Run_Test

# %%
for i in filename_case2:
    print('----------------')
    print(df.loc[i,'filename_infere'])
    print(df.loc[i,'filename'])
    print(df.loc[i,'P_codeState'])

# %%
for i in case2_index:
    print('----------------')
    print(df.loc[i,'P_codeState'])

# %%
df.loc[44754,'P_codeState']

# %%
pattern

# %%
df.loc[301556,'P_codeState']

# %%
df[(df['TP'] == 'Tp1') & (df['verb'] == 'Run.Test')& (df['tests'] != '[]')][['filename_infere','filename','P_codeState','tests']]

# %%
df.loc[179842,'tests']

# %%
df.loc[44754,'P_codeState']

# %%
df.loc[44754]

# %%
df[(df['TP'] == 'Tp1') & (df['verb'] == 'Run.Test')]['filename_infere'].unique()

# %%
df[(df['TP'] == 'Tp1') & (df['verb'] == 'Run.Test')]['tests'].unique()

# %%
import re
from src.data.variable_constant_2425 import FILES_BY_TP, TP_name, Type_TP

# Global variable pattern
pattern = ''
for tp_name in FILES_BY_TP:

    file_name = '|'.join(tp_name)
    pattern = pattern +  file_name + '|'

pattern = pattern  + 'Irrelevant'

match = re.search(pattern, df.loc[44754,'filename_infere']) 
match

# %%
df.loc[44754,'filename']

# %%
from src.features import io_utils, data_cleaning
pattern_list = pattern.split('|')

# %%
pattern_list

# %%
df.loc[126963,'filename']
import difflib

for correct_name in pattern_list:
    
    similarity = difflib.SequenceMatcher(None, correct_name[:-3], 'chaine_rep').ratio()
    
    if similarity > 0.7: print(True)

#data_cleaning.find_similarity(pattern_list,'chaine_rep.py')

# %%
df.loc[126963,'filename']

# %%
df.loc[126963,'P_codeState']

# %%
df.loc[44754]

# %%
df[(df['TP'] == 'Tp1') & (df['verb'] == 'Run.Test') & (df['tests'] != '[]')][['filename_infere','filename','tests']]

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
# ### Number of each TP in each seance

# %%
# create a crossttable of two columns of df
count_table_seance_TP = pd.crosstab(df['seance'],df['TP'])
count_table_seance_TP = count_table_seance_TP.reindex(index = SORTED_SEANCE, columns = TP_ORDER, fill_value=0)
count_table_seance_TP

# %%
count_table_seance_TP.plot(kind='bar', figsize=(14, 6))

plt.title("Number of TP in each semaine")
plt.ylabel("Number of TPs")
plt.xlabel("Seance")
plt.xticks(rotation=45)
plt.legend(title="TP")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### Number of empty filename_infere in each seance

# %%
df_empty_filename_in_each_seance = pd.DataFrame(columns=['seance','num_empty_filename']) # create the df

for seance in SORTED_SEANCE:

    num_total = ((df['seance'] == seance) & (df['filename_infere'] == '')).sum() # filter on seance and TP_prog

    # Append row to df
    df_empty_filename_in_each_seance = pd.concat([
        df_empty_filename_in_each_seance,
        pd.DataFrame({'seance': [seance], 'num_empty_filename': [num_total]})
    ], ignore_index=True)

df_empty_filename_in_each_seance

# %%
labels = SORTED_SEANCE
values = df_empty_filename_in_each_seance['num_empty_filename']

plt.subplots(figsize=(17, 6))
plt.bar(labels, values)
plt.title("Number of empty filename_infere in each seance")
plt.xlabel("Seance")
plt.ylabel("Number of empty filename_infere")
plt.show()


# %% [markdown]
# ### Create a dataframe of column 'tests'

# %%
def convert_column_tests_to_df(df):
    
    df_test_not_empty = df[df['tests'] != '']['tests']

    df_all_tests = None
    frames = []

    for test_value in df_test_not_empty:
        
        lst = ast.literal_eval(test_value) # extract the list inside the string
        df_one_test = pd.DataFrame(lst)
        frames.append(df_one_test)

    df_all_tests = pd.concat(frames, ignore_index=True)
    return df_all_tests
    
df_of_column_test = convert_column_tests_to_df(df)  
df_of_column_test 

# %% [markdown]
# ### Add Red or Green column for Run.Test

# %% [markdown]
# How write boolean for test green or red for Run.Test : This column should be added by the values in 'status' column?

# %%
df_of_column_test[df_of_column_test['status'] == False]

# %% [markdown]
# ### Keep research data only

# %%
df['research_usage'].unique()

# %% [markdown]
# ### Example of an student who worked alone and then en binome during one seance

# %%
# Example of the error above
df[(df['seance'] == 'semaine_1') & ( (df['actor'] == 'hichame.haddou.etu'))][['actor','binome']].head(10)

# %%
df[(df['seance'] == 'semaine_1') & ( (df['binome'] == 'hichame.haddou.etu'))][['actor','binome']].head(10)

# %% [markdown]
# # ToDo
#
# - semaine_5: there are two sessions, but only one sessions they were working, because the second session was controle TP and the internet was cut
# - add the part to see how many filename_infere are empty in each semaine : DONE!
# - Ignore the part of **utilisation print**
#
# - filename_infere of students who save their files in the correct name but not the correct name of the semaine
#
# - add dataframe for the cases one, two, for each TP (create a function) : DONE!
# - add matrix with columns seance and TP : DONE!
#
# - see how created df of column 'test' (in Amadouho version) : Done!
# - How write boolean for test green or red for Run.Test
# - we want just Nom_TP_PPROGRAMMATION without the first week
# - Leave the part after the print on Etude_sur_les_testes.py
# - See cleaning.keep_research_data_only in notebooks/Init_data.py
