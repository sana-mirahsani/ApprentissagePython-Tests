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
# # Analyze Workflow Overview:
# 1. Import Libraries
#
# 2. Load DataFrame : phase2_nettoyage_fichiere.csv 
# <br>
# (It should be Final_nettoyage_2425.csv but for now we don't work with anonymized data because it is hard)
#
# 3. All analyzes
#
# 4. ToDo (will be deleted later)

# %% [markdown]
# ## 1.Import Libraries

# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast

import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'

from src.features import io_utils, data_testing, pipeline_utils

import importlib
importlib.reload(io_utils)
importlib.reload(data_testing)
importlib.reload(pipeline_utils)

# add for Mirabelle's code 
from thonnycontrib.backend.test_finder import L1TestFinder
from thonnycontrib.exceptions import SpaceMissingAfterPromptException


# %%
filename = "traces260105"
out_dir_interim = f"../data/interim/{filename}_20260205_093949"
out_dir_raw = f"../data/raw/{filename}_20260205_093949"

filename, out_dir_interim, _ = pipeline_utils.execute_manually(filename, out_dir_interim, out_dir_raw)

match filename:
    case "traces250102":
        from src.data.variable_constant_2425 import TP_NAME, SORTED_SEANCE, all_TP_prog_functions_name_by_tp
        
    case "traces260105":
        from src.data.variable_constant_2526 import TP_NAME, SORTED_SEANCE, all_TP_prog_functions_name_by_tp

input_file = filename + "_filename_phase3_clean" + ".csv"

# %% [markdown]
# ## 2.Load DataFrame

# %%
df = io_utils.reading_dataframe(dir= out_dir_interim, file_name= input_file)

# %% [markdown]
# ### Add column codeState, combined by P_codeState and F_codeState

# %%
df['codeState'] = df['P_codeState'] + df['F_codeState']

# %% [markdown]
# ## 3.Analyze

# %% [markdown]
# ### 4.1 Total number of students during semester

# %%
number_actor  = set(df['actor'])
number_binome = set(df['binome'])

total_students = number_actor.union(number_binome)

print(f"Total number of students during the semester : {len(total_students)}")

# %% [markdown]
# ### 4.2 Total number of students during each seance

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
# ### 4.3 Total number of students during each TP

# %%
df_students_per_TP = pd.DataFrame(columns=['TP', 'number of students'])

for tp in TP_NAME:
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
df_students_per_TP

labels = df_students_per_TP['TP']
values = df_students_per_TP['number of students']

plt.subplots(figsize=(17, 6))
plt.bar(labels, values)
plt.title("Nombre d'eleves par TP")
plt.xlabel("TP")
plt.ylabel("Nombre d'eleves")
plt.show()

# %% [markdown]
# ### 4.4 Total number of students during TP_mani and TP_prog

# %%
df_students_per_Type_Tp = pd.DataFrame(columns=['TP','TP_mani', 'TP_prog']) # create the df
Type_TPs = ['TP_mani', 'TP_prog'] # create a list of different types of tp

for tp in TP_NAME:

    all_types_tp = []  # saving all numbers of types of TP

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
df[(df['TP'] == 'Tp_GAME') & (df['Type_TP'] == 'TP_mani')]['filename_infere'].unique()

# %% [markdown]
# **It is change :** The reason why in Tp_GAME, 60 files exist of maniplulation but in the previous method it didn't showed, is because I put wrongly 'experimentations_fichiers.py' in TP_prog. Now we can see how correcting methods is working.

# %%
df_students_per_Type_Tp.set_index('TP')[['TP_mani', 'TP_prog']].plot(kind='bar', figsize=(12, 6))

plt.title("Number of Students in Each Type of TP")
plt.ylabel("Number of Students")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Type")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 4.5 Number of TP_mani and TP_prog in each TP 

# %%
# First filter Type_TP only on TP_mani and TP_prog
filtered_df = df[df['Type_TP'].isin(['TP_mani', 'TP_prog'])] 

# Calculate crosstable
count_table = pd.crosstab(df['TP'], filtered_df['Type_TP'])

# Get the index to change the order, TP10 move to TP9
current_order = list(count_table.index)

# Remove TP10
row_to_move = current_order.pop(1)

# Add TP10 after TP9
current_order.insert(9, row_to_move)

# Reindex crosstable
count_table = count_table.reindex(current_order)
count_table

# %% [markdown]
# **It is change :** same reason of part 4.4

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
# ### 4.6 Number of student using each verb in each TP

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
df_students_per_verb.set_index('TP')[['Run.Command', 'Run.Program','Run.Test','Run.Debugger']].plot(kind='bar', figsize=(12, 6))

plt.title("Number of students per verb in each TP")
plt.ylabel("Number of students")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Verbs")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 4.7 Number of student using each verb only in each TP_prog

# %%
verbs = ['Run.Command','Run.Program','Run.Test','Run.Debugger']

df_students_per_verb_TP_prog = pd.DataFrame(columns=['TP','Run.Command', 'Run.Program','Run.Test','Run.Debugger']) # create the df

for tp in TP_NAME:

    df_filtered = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')] # filter on TP & TP_prog
    number_of_students = []

    for verb in verbs:

        actor_column  = df_filtered[df_filtered['verb'] == verb]['actor']

        binome_column = df_filtered[df_filtered['verb'] == verb]['binome']

        all_students  = set(actor_column).union(set(binome_column))
        # ici il faudrait virer ''
        number_of_students.append(len(all_students))

    # Append row to df
    df_students_per_verb_TP_prog = pd.concat([
        df_students_per_verb_TP_prog,
        pd.DataFrame({'TP': [tp], 'Run.Command': number_of_students[0], 'Run.Program': number_of_students[1], 'Run.Test': number_of_students[2], 'Run.Debugger': number_of_students[3]})
    ], ignore_index=True)

df_students_per_verb_TP_prog

# %%
df_students_per_verb_TP_prog.set_index('TP')[['Run.Command', 'Run.Program','Run.Test','Run.Debugger']].plot(kind='bar', figsize=(12, 6))

plt.title("Number of students per verb in only TP_prog")
plt.ylabel("Number of students")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Verbs")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 4.8 Compare the total number of students with the number of students using each verb only in TP_prog

# %%
verbs = ['Run.Command','Run.Program','Run.Test','Run.Debugger']

df_comparing = pd.DataFrame(columns=['TP','total_number','Run.Command', 'Run.Program','Run.Test','Run.Debugger']) # create the df

for tp in TP_NAME:

    df_filtered = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')] # filter on TP & TP_prog
    number_of_students = []

    # calculate the number total of students
    actor_column  = df_filtered['actor']
    binome_column = df_filtered['binome']
    all_students  = set(actor_column).union(set(binome_column))
    total_number  = len(all_students)

    for verb in verbs:

        actor_column  = df_filtered[df_filtered['verb'] == verb]['actor']

        binome_column = df_filtered[df_filtered['verb'] == verb]['binome']

        all_students  = set(actor_column).union(set(binome_column))
        number_of_students.append(len(all_students))

    # Append row to df
    df_comparing = pd.concat([
        df_comparing,
        pd.DataFrame({'TP': [tp], 'total_number' : [total_number],'Run.Command': number_of_students[0], 'Run.Program': number_of_students[1], 'Run.Test': number_of_students[2], 'Run.Debugger': number_of_students[3]})
    ], ignore_index=True)

df_comparing

# %%
df_comparing.set_index('TP')[['total_number','Run.Command', 'Run.Program','Run.Test','Run.Debugger']].plot(kind='bar', figsize=(12, 6))

plt.title("Comparing the total number of students with the number of students using each verb in TP_prog")
plt.ylabel("Number of students")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Verbs")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 4.9 Number of each TP in each seance

# %%
# create a crossttable of two columns of df
count_table_seance_TP = pd.crosstab(df['seance'],df['TP'])
count_table_seance_TP = count_table_seance_TP.reindex(index = SORTED_SEANCE, columns = TP_NAME, fill_value=0)
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
# ### 4.10 Number of empty filename_infere in each seance

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
# ### 4.11 Calculate the total number of Run.Test in the too_short_session.csv

# %%
df_too_short = io_utils.reading_dataframe(dir= out_dir_interim, file_name='too_short_sessions.csv')
df_too_short 

# %%
df_inlcuding_too_short_sessions = io_utils.reading_dataframe(dir= out_dir_interim, file_name= filename + '_filename_phase1_clean.csv')

# Since the too_short_sessions are removed in the data of phase2, we need to read the data from phase1, before removing the too_short_sessions to check the verbs == Run.Test or not

# %%
for index, row in df_too_short.iterrows():

    activity = ast.literal_eval(row['too_short_indices'])

    for indices in activity:
        
        start_idx = indices[0]
        end_idx = indices[1]
        
        if abs(start_idx - end_idx) > 1:
            
            #print(df_inlcuding_too_short_sessions.loc[start_idx+1, 'verb']) #to see the verb
            if df_inlcuding_too_short_sessions.loc[start_idx+1, 'verb'] == 'Run.Test':
                
                print(indices)


# %% [markdown]
# There is no Run.Test in too_short_sessions

# %% [markdown]
# ### 4.12 Calculate how many students doing or not doing the run.test in each TP (TP_prog)

# %%
# can be in data_testing
def calculate_verb_in_TP(df,verb,tp): 

    df_filtered = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')] 
    actor_column  = df_filtered['actor']
    binome_column = df_filtered['binome']
    all_students  = set(actor_column).union(set(binome_column))

    if '' in all_students:
        all_students.remove('')

    students_excluding_verb = []
    students_including_verb = []

    for name in all_students:    

        verbs_of_student = df_filtered[(df_filtered['actor'] == name) | (df_filtered['binome'] == name)]['verb'].unique()
        
        if not (verb in verbs_of_student): # not doing Run.Test
            students_excluding_verb.append(name)
        
        else: # doing Run.Test
            students_including_verb.append(name)
    
    total_num_of_students = len(all_students)
    
    total_num_of_students_excluding_verb = len(students_excluding_verb)
    total_num_of_students_including_verb = len(students_including_verb)
    
    return total_num_of_students, total_num_of_students_including_verb, total_num_of_students_excluding_verb



# %%
df_run_test = pd.DataFrame(columns=['TP','total_number_students','doing_run_test','not_doing_run_test']) # create the df

for tp in TP_NAME:
    
    if tp != 'Tp10':
        total_students , total_students_including_run_test, total_students_excluding_run_test = calculate_verb_in_TP(df,'Run.Test',tp)
    
    else: 
        total_students , total_students_including_run_test, total_students_excluding_run_test = 0, 0 , 0
        
    # Append row to df
    df_run_test = pd.concat([
        df_run_test,
        pd.DataFrame({'TP': [tp], 'total_number_students' : [total_students], 'doing_run_test' : [total_students_including_run_test], 'not_doing_run_test' : [total_students_excluding_run_test]})
    ], ignore_index=True)

# remove the last row which the empty filenameinfere (we don't need them)
df_run_test 

# %%
df_run_test.set_index('TP')[['total_number_students','doing_run_test','not_doing_run_test']].plot(kind='bar', figsize=(12, 6))

plt.title("Comparing the total number of students with the number of students Not doing Run.Test in TP_prog")
plt.ylabel("Number of students")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Verbs")
plt.tight_layout()
plt.show()


# %% [markdown]
# ### 4.13 Calculate how many students are doing the empty tests

# %%
def calculation_empty_test(df,tp):

    df_filtered   = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')] 
    actor_column  = df_filtered['actor']
    binome_column = df_filtered['binome']
    all_students  = set(actor_column).union(set(binome_column))
    
    if '' in all_students:
        all_students.remove('')

    students_doing_test = []
    students_with_empty_test = []
    verb = 'Run.Test'
    
    for name in all_students:
        verbs_of_student = df_filtered[(df_filtered['actor'] == name) | (df_filtered['binome'] == name)]['verb'].unique()
        
        if verb in verbs_of_student: # doing Run.Test
            
            array_tests_unique = df_filtered[(df_filtered['verb'] == verb) & ((df_filtered['actor'] == name) | (df_filtered['binome'] == name))]['tests'].unique()
            
            students_doing_test.append(name) # add to a list
           
            if (array_tests_unique.size == 1) & (array_tests_unique[0] == '[]'): # means the test is empty
                
                    students_with_empty_test.append(name) # student did the run.test but it is empty
    
    return all_students, students_doing_test, students_with_empty_test


# %%
df_empty_test = pd.DataFrame(columns=['TP','total_student','num_doing_run_test','num_doing_empty_run_test','name_doing_run_test','name_doing_empty_run_test']) # create the df
students_doing_test_all_tp = []
students_with_empty_test_all_tp = []

for tp in TP_NAME:
    
    # start the calculation
    all_students, total_students_doing_test , total_students_with_empty_test = calculation_empty_test(df,tp)

    # Append row to df
    if tp != 'Tp10' and tp != 'Tp1':
        df_empty_test = pd.concat([
            df_empty_test,
            pd.DataFrame({'TP': [tp], 'total_student': [len(all_students)],'num_doing_run_test' : [len(total_students_doing_test)], 'num_doing_empty_run_test' : [len(total_students_with_empty_test)], 'name_doing_run_test' : [total_students_doing_test], 'name_doing_empty_run_test' : [total_students_with_empty_test]})
        ], ignore_index=True)

    else:
        df_empty_test = pd.concat([
            df_empty_test,
            pd.DataFrame({'TP': [tp], 'total_student': [len(all_students)], 'num_doing_run_test' : [0],'num_doing_empty_run_test' : [0], 'name_doing_run_test' : [''], 'name_doing_empty_run_test' : ['']})
        ], ignore_index=True)

df_empty_test 

# %%
df_empty_test.set_index('TP')[['total_student','num_doing_run_test','num_doing_empty_run_test']].plot(kind='bar', figsize=(12, 6))

plt.title("Number of students doing the empty tests in each TP_prog")
plt.ylabel("Number of students")
plt.xlabel("TP")
plt.xticks(rotation=45)
plt.legend(title="Verbs")
plt.tight_layout()
plt.show()


# %% [markdown]
# ### 4.14 Run Test Participation Rate per TP (TP_prog)

# %%
# Function to calculate the percentage (can be in data_testing)
def run_test_rate_by_tp(tp,df):

    # This function calculates the result by the calculation of calculation_empty_test()
    total_num_of_students = df[df_empty_test['TP'] == tp]['total_student'].iloc[0]
    total_num_of_students_doing_test = df[df['TP'] == tp]['num_doing_run_test'].iloc[0]
    total_num_of_students_doing_empty_test = df[df['TP'] == tp]['num_doing_empty_run_test'].iloc[0]

    total_num_of_students_doing_real_test = total_num_of_students_doing_test - total_num_of_students_doing_empty_test

    test_rate_per_tp = (total_num_of_students_doing_test / total_num_of_students) * 100
    real_test_rate_per_tp = (total_num_of_students_doing_real_test / total_num_of_students) * 100

    print(f"------------------{tp}-----------------------")
    print(f"{test_rate_per_tp:.2f}% of students made the Run.Test and {real_test_rate_per_tp:.2f}% of them are the real test.")
    
    return test_rate_per_tp, real_test_rate_per_tp


# %%
run_test_rate_per_tp_all  = [] # list to save all percentage
real_test_rate_per_tp_all = [] # list to save all percentage real test

for tp in TP_NAME:

    if tp != 'Tp10':
        percentage_test, percentage_real_test = run_test_rate_by_tp(tp,df_empty_test) # calculate the percentage
        run_test_rate_per_tp_all.append(percentage_test) # store the result

        real_test_rate_per_tp_all.append(percentage_real_test) # store the result of real test
    
    else: # it's TP10 and there is TP_prog!
        run_test_rate_per_tp_all.append(0)
        real_test_rate_per_tp_all.append(0)

# %%
# Plotting
plt.figure(figsize=(8, 5))
plt.plot(TP_NAME, run_test_rate_per_tp_all, marker='o', linestyle='-', color='skyblue', label = 'Doing Run Test')
plt.plot(TP_NAME, real_test_rate_per_tp_all, marker='o', linestyle='-', color='orange', label = 'Doing Real Test')
plt.title('Rate of students doing Run.Test and real test per each TP')
plt.ylabel('Percentage (%)')
plt.ylim(0, 100) 
plt.grid(True)
plt.legend()
plt.show()

# %% [markdown]
# ### 4.15 Find the session.Start and session.End without including any Run.Test in each TP (TP_prog)

# %%
# A list to store all the indices
records = []

for tp in TP_NAME:
    tp_df = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')] # filter on TP and TP_prog
    indices_to_check = tp_df.index.tolist() # extract the indices of files of TP_prog

    if indices_to_check:
        final_indices, total_num_No_Run_Test = data_testing.check_not_including_Run_Test_fast(df, indices_to_check) # check each indices if they include any Run.Test or not

        records.append({
            'TP': tp,
            'indices': final_indices,
            'total_num_No_Run_Test': total_num_No_Run_Test
        }) 

    else:
        records.append({
            'TP': tp,
            'indices': [],
            'total_num_No_Run_Test': 0
        }) 

df_indices_excluding_run_test = pd.DataFrame(records) # convert the dictionary into a dataframe

df_indices_excluding_run_test

# %%
labels = TP_NAME
values = df_indices_excluding_run_test['total_num_No_Run_Test']

plt.subplots(figsize=(17, 6))
plt.bar(labels, values)
plt.title("Number of sessions with NO Run.Test in TP_prog")
plt.xlabel("TP")
plt.ylabel("Number of sessions")
plt.show()

# %% [markdown]
# ### 4.16 Calculate how many students didn't do any Run.Test in their session.Start and session.End during each TP (TP_prog)

# %%
records_student = [] 

for idx, row in df_indices_excluding_run_test.iterrows():
    tp_name = row['TP']
    index_ranges = row['indices']  # list of tuples like (start, end)

    actors_in_ranges = set()
    
    for start_idx, end_idx in index_ranges:
        # Select the slice from original DataFrame
        actor_slice = df.loc[start_idx:end_idx, 'actor']
        actors_in_ranges.update(actor_slice.unique())

    records_student.append({
            'TP': tp_name,
            'students_name': actors_in_ranges,
            'total_num': len(actors_in_ranges)
        }) 

# %%
df_students_excluding_run_test = pd.DataFrame(records_student)
df_students_excluding_run_test 

# %%
labels = TP_NAME
values = df_students_excluding_run_test['total_num']

plt.subplots(figsize=(17, 6))
plt.bar(labels, values)
plt.title("Number of students with NO Run.Test in their sessions")
plt.xlabel("TP")
plt.ylabel("Number of studnets")
plt.show()

# %% [markdown]
# ### 4.17 In TP_GAME, look for each student, in the newest file of Run.Test, how many their column tests is empty and isn't

# %%
actors  = set(df[(df['TP'] == 'Tp_GAME') & (df['verb'] == 'Run.Test')]['actor'])
binomes = set(df[(df['TP'] == 'Tp_GAME') & (df['verb'] == 'Run.Test')]['binome'])
all_students = actors.union(binomes)

num_students_with_empty_tests = 0
num_students_with_a_tests = 0

for student in all_students:
    filtered_df = df[
        ((df['actor'] == student) | (df['binome'] == student)) &
        (df['TP'] == 'Tp_GAME') &
        (df['verb'] == 'Run.Test')
    ]

    timestap_column = filtered_df['timestamp.$date']
    newest_index = timestap_column.idxmax()

    if df.loc[newest_index,'tests'] == '[]':
        num_students_with_empty_tests += 1
    
    else: num_students_with_a_tests += 1

print(f'In TP_GAME, number of students with empty tests : {num_students_with_empty_tests}')
print(f'In TP_GAME, number of students with tests : {num_students_with_a_tests}')


# %% [markdown]
# ### 4.18 Number of students who did each file.py in TP_GAME, extract the name of students

# %%
def calculation_files_of_tp_game(df,filename):

    df_TP_game = df[df['TP'] == 'Tp_GAME'] 
    actor_column  = df_TP_game['actor']
    binome_column = df_TP_game['binome']
    all_students  = set(actor_column).union(set(binome_column))
    all_students.remove('')

    actor_column_filename  = df_TP_game[df_TP_game['filename_infere'] == filename]['actor']
    binome_column_filename = df_TP_game[df_TP_game['filename_infere'] == filename]['binome']
    all_students_filename  = set(actor_column_filename).union(set(binome_column_filename))
    all_students_filename.remove('')

    return len(all_students), len(all_students_filename)


# %%
files_tp_game = (df[df['TP'] == 'Tp_GAME']['filename_infere'].unique()).tolist()
files_tp_game.remove('experimentations_fichiers.py')
files_tp_game

# %%
df_files_tp_game = pd.DataFrame(columns=['filename','total_number_students']) # create the df

for filename in files_tp_game:
    
    total_students , total_students_in_filename = calculation_files_of_tp_game(df,filename)
     
    # Append row to df
    df_files_tp_game = pd.concat([
        df_files_tp_game,
        pd.DataFrame({'filename': [filename], 'total_number_students' : [total_students_in_filename]})
    ], ignore_index=True)

df_files_tp_game

# %%
labels = files_tp_game
values = df_files_tp_game['total_number_students']

plt.subplots(figsize=(17, 6))
plt.bar(labels, values)
plt.title("Number of students doing in each file of TP_GAME")
plt.xlabel("file")
plt.ylabel("Number of studnets")
plt.show()


# %% [markdown]
# ### 4.19 Create a dataframe of column 'tests'

# %%
def convert_column_tests_to_df(df):
    
    df_test_not_empty = df['tests']

    df_all_tests = None
    frames = []
    
    for index, test_value in df_test_not_empty.items():
        
        if (test_value != '') and (test_value != '[]'):
            lst = ast.literal_eval(test_value) # extract the list inside the string
            df_one_test = pd.DataFrame(lst)
            # add the column of actor and filename_infere and verb and P_codeState
            df_one_test.insert(0, 'original_index', index)
            frames.append(df_one_test)        

    df_all_tests = pd.concat(frames, ignore_index=True)
    return df_all_tests

# creating a dataframe from tests column in the original dataframe
df_of_column_test = convert_column_tests_to_df(df)  
df_of_column_test 

# %%
df_of_column_test['verdict'].unique()

# %% [markdown]
# Different values in verdict columns : 
#
# - **PassedVerdict** : The code is passed with the correct output (as excepted)
# - **ExceptionVerdict** : It didn’t reach the end of the test due to an error.
# - **FailedVerdict** : The code ran successfully, but the output was incorrect.
# - **PassedSetupVerdict** : The code passed a setup check, not the actual test.

# %% [markdown]
# ### 4.20 Add Red or Green column for Run.Test

# %% [markdown]
# How write boolean for test green or red for Run.Test : This column should be added by the values in 'status' column?
#
# - False : Red
# - True : Green
#
# check this function df_tests = tests_utils.construct_DataFrame_from_all_tests(run_test_copy) in script_initialisation.py in thomas version

# %%
# add column color_test
df_of_column_test['color_test'] = np.where(df_of_column_test['status'] == True, 'Green', 'Red')

df_of_column_test[['color_test','status']] 

# %% [markdown]
# ### 4.21 Extract the consecutive Run.Test (Unfinished and abundant)

# %%
df_empty_test # this dataframe is created in 4.13 part

# %%
all_students_doing_real_test = {} # a dictionary of students doing the real test in each TP by looking df_empty_test

for tp in TP_NAME:
    df_filtered_tp = df_empty_test[df_empty_test['TP'] == tp]
    
    students_doing_run_test   = set(df_filtered_tp['name_doing_run_test'].iloc[0])
    students_doing_empty_test = set(df_filtered_tp['name_doing_empty_run_test'].iloc[0])

    students_doing_real_test = list(students_doing_run_test - students_doing_empty_test)  
    all_students_doing_real_test.update({tp :students_doing_real_test})

all_students_doing_real_test 

# %% [markdown]
# ### 4.22 Red_test (Unfinished and abundant)

# %% [markdown]
# **Idea :** Find students who had atleast one red test during a session, and analyze what did they do after having this red test. 
#
# Different type of students after having a Red test: 
#
# - passed_after_failing_test : Students solved the problem after having a Red Test
#
# - abandoned_file_started_new : Students couldn't solve the bug and restart a another test
#
# - red_test_no_recovery : Students couldn't solve the bug and there is no more Run.Test (the left completely!) after a red test
#
# Red test: At least one of the colors in tests is red
#
# **Note :** This part is unfinished and abundant due to the lack of time of sana's internship.

# %%
all_students_doing_real_test['Tp1'] # This is created in 4.19 (before that you should run 4.13 also)

# %% [markdown]
# - Before checking each test, I should check if there is any Run.Test in a TP or not, if there is, check if there is any red test or not,if all of them are green no need to check.
#
# - Remember, in each TP_prog, for each students, there might be multipie tests for a Run.Test (if there are any Run.Test)
#
# - normal behavior , expected behavoir 
#
# Things to check :
# filename_infere, codestate, function's name, 
#
# - first : check if filename is same 
# - second : check if codestate is same
# - third : check if function's name are same of tests
#
#     if filename is same : 
#
#         consider like same run.test
#
#         if codestate is same:
#             consider like same run.test
#
#             if functions name are same in tests:
#                 consider like same test
#             
#             else:
#                 different run.test
#         else:
#             different run.test
#     else:
#         different run.test
#
#
#

# %%
import difflib
def check_difference_between_two_code(code1,code2):

    diff = list(difflib.ndiff(code1.splitlines(), code2.splitlines()))
    has_changes = any(line.startswith('- ') or line.startswith('+ ') for line in diff)

    if has_changes:
        print("Differences found:")
        for line in diff:
            if line.startswith('- ') or line.startswith('+ '):
                print(line)
    else:
        print("No differences.")



# %%
def find_red_test(name,df,tp): 
    
    tests_index_red = []
    tests_index_green = []

    df_just_run_test = df[(df['TP'] == tp)  & (df['Type_TP'] == 'TP_prog') & ((df['actor'] == name) | (df['binome'] == name)) & (df['verb'] == 'Run.Test')] # filter on Red_Test
    
    for index, row in df_just_run_test.iterrows(): # iterate on all Run.Test
        
        test_color = df_of_column_test[df_of_column_test['original_index'] == index]['color_test'] # extract all colors for this (one) Run.Test from df_of_column_test (4.21 & 4.22)

        if (test_color == 'Green').all():
            # There was no red test for the current Run.Test
            tests_index_green.append(index)
        else:
            # There is at least one red test in the current Run.Test
            #print(f"The real index of the df : {index}")
            tests_index_red.append(index) # Index of the Run.Test
            
    return tests_index_red, tests_index_green


# %% [markdown]
# #### Analyze TP1 for testing

# %%
all_test_result_TP1 = []

for name in all_students_doing_real_test['Tp1']:
   
    all_indices_red, all_indices_green = find_red_test(name,df,'Tp1')

    test_result = {}
    test_result['name'] = name
    test_result['indices_red_test'] = all_indices_red
    test_result['indices_green_test'] = all_indices_green
   
    all_test_result_TP1.append(test_result)

all_test_result_TP1

# %% [markdown]
# #### Analyze TP2 for testing

# %% [markdown]
# - First check different filename, classify by each filename_infere
# - Each Run.Test 2 by 2 are compared
#     - Do they have overlap?
#     - Is it added test?
#     - Is it deleted test?
#     - Is same exact test (name and tested line is checked) with same Verdict?
#     - Is same exact test (name and tested line is checked) BUT different Verdict? (meaning student understood the problem)

# %%
all_test_result_TP2 = [] 

for name in all_students_doing_real_test['Tp2']:
   
    all_indices_red, all_indices_green  = find_red_test(name,df,'Tp2')

    test_result = {}
    test_result['name'] = name
    test_result['indices_red_test'] = all_indices_red
    test_result['indices_green_test'] = all_indices_green
   
    all_test_result_TP2.append(test_result)

# convert dict to df
df_test_TP2 = pd.DataFrame(all_test_result_TP2)
df_test_TP2


# %%
# step 0 : merge all indices of Run.Test
def merge_red_and_green_test(name):

    list_red_test   = df_test_TP2[df_test_TP2['name'] == name]['indices_red_test'].iloc[0]
    list_green_test = df_test_TP2[df_test_TP2['name'] == name]['indices_green_test'].iloc[0]

    # merge and sort in ascending order
    merged_sorted = sorted(list_red_test + list_green_test)
    return merged_sorted


# %%
# step1 : classify Run.Test by different filename_infere
def classify_by_filename(all_list_indices):
    
    # Select only the rows at the given indices
    selected_rows = df.loc[all_list_indices]

    # Group them by the 'filename_infere' column
    run_test_classification = selected_rows.groupby('filename_infere')

    all_classification_tests = []

    for filename, group in run_test_classification:
            classification_test = {}
            classification_test['filename'] = filename
            classification_test['indices'] = group.index.tolist()

            all_classification_tests.append(classification_test)
        
    return all_classification_tests


# %%
# step2 : check the overlab
def find_overlab_tests(test1_index,test2_index):

    # extract the two tests
    test1_df = df_of_column_test[df_of_column_test['original_index'] == test1_index]
    test2_df = df_of_column_test[df_of_column_test['original_index'] == test2_index]
    
    columns_to_check = ['filename', 'lineno', 'tested_line', 'expected_result', 'details', 'verdict', 'name', 'status', 'color_test']

    # check if they have overlab by merging them
    overlap = test1_df[columns_to_check].merge(test2_df[columns_to_check], how='inner')

    if not overlap.empty: # they have overlab
        print("There is overlap!")

        # check their lengths
        if len(test1_df) == len(test2_df):
            
            print("same length")
            
            if (test1_df[columns_to_check].reset_index(drop=True) == test2_df[columns_to_check].reset_index(drop=True)).all().all():
                print("They are exactly same test!")
            
            else:
                print("same test but modified")

        elif len(test1_df) < len(test2_df):
            print("test added")

        elif len(test1_df) > len(test2_df):
            print("test deleted")
    else:
        print("No overlap.")


# %%
# main
all_indices = merge_red_and_green_test('massil.kichi.etu') # step 0
all_classification_tests = classify_by_filename(all_indices) # step 1

if len(all_classification_tests) == 1:
    print("There is only one classification because there was only one filename")

else:
    print("There are different filenames")

for classifcation in all_classification_tests:
    for index in classifcation['indices']:
        print(index)
        find_overlab_tests(index,index+1)

# %%
test1 = df_of_column_test[df_of_column_test['original_index'] == 180778]
test1

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1659]


# %%
def check_difference_between_two_code(code1,code2):

    diff = list(difflib.ndiff(code1.splitlines(), code2.splitlines()))
    has_changes = any(line.startswith('- ') or line.startswith('+ ') for line in diff)

    if has_changes:
        print("Differences found:")
        for line in diff:
            if line.startswith('- ') or line.startswith('+ '):
                print(line)
    else:
        print("No differences.")


# %%
#code1 = df.loc[174404,'codestate']
#code2 = df.loc[174409,'codestate']

#check_difference_between_two_code(code1,code2) # P_codestate are different


# %% [markdown]
# Extract all unique tests and count the number of try for each unique test, then find :
# - if there is any failed and given up try
# - if there is any failed and solved try
#
# Before starts, check if there is any duplicated tests in all Run.Test (exactly the same)

# %% [markdown]
# ### 4.23 Keep research data only

# %%
df['research_usage'].unique()

# %%
set(df[df['research_usage'] == '1.0']['actor']).intersection(set(df[df['research_usage'] == '0.0']['actor']))


# %% [markdown]
# ### 4.24 Find_test_final

# %%
def find_tests_in_codestate(source:str) -> dict:
    '''
    Renvoie un dictionnaire qui associe à chaque fonction trouvée dans `source` son nombre de tests.
    Renvoie None si le source n'est pas analysable car SyntaxError ou erreur de syntaxe dans les tests
    
    source is some codestate
    '''
    dico = {}
    finder = L1TestFinder(source=source)
    try:
        res = finder.find_l1doctests()
        for ex_func in res:
            name = ex_func.get_name().split('(')[0]
            dico[name] = len(ex_func.get_examples())
    except (ValueError, SyntaxError, SpaceMissingAfterPromptException) as e:
        dico = None
    return dico


# %%
def find_tests_in_codestate_for_functions(codeState:str, functions_tp:list[str]) -> dict:
    '''
    Returns the number of tests found in codeState, only for functions in functions_tp

    dict has the shape {name_func : int (number of tests) or None (function not found)}
    '''
    res = {}
    test_number =  find_tests_in_codestate(codeState)
    if test_number is None:
        return None
    for func_name in  functions_tp:
        if func_name in test_number:
            res[func_name] = test_number[func_name]
        else:
            res[func_name] = None
    return res


# %% [markdown]
# Cette fonction est partie du principe que les timestamps étaient triés en ordre croissant, ce qui est faux.
#
# Elle cherche le codestate le plus récent, et s'il n'est pas analysable, en cherche un analysable dans les précédents. Ce faisant on risque de rater un autre codestate qui aurait pu être analysable, mais tant pis.

# %%
def find_tests_for_tp_tpprog_name(name:str, df:pd.DataFrame, tp:str) -> tuple[pd.DataFrame, bool, bool]:
    """
    Selects in df rows of tp and Type_TP is TP_Prog, selects for name the most recent parsable codeState and returns :
    - a DataFrame with columns actor, tp, Tp_Prog, function_name, tests_number (int or None if not present in codestates), index in df of codestate analyzed
    - a first bool, True if for that student the codeState cannot be analyzed (Python or l1test syntax error)
    - a second bool, True if for that student no codeState was found
    """
    
    df_name_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & ((df['actor'] == name) | (df['binome'] == name))]
    df_codestate_nonempty = df_name_tp[df_name_tp['codeState'] != '']
    if len(df_codestate_nonempty) == 0:
            return None, False, True
    else:
        # look for most recent parsable codeState
        list_index_timestamps = df_codestate_nonempty['timestamp.$date'].index.tolist()
        index_of_timestamp_max = df_codestate_nonempty['timestamp.$date'].idxmax()
        ind_of_timestamp_max_in_list = list_index_timestamps.index(index_of_timestamp_max)
        index_to_examine = list_index_timestamps[:ind_of_timestamp_max_in_list+1]
        for i in range(ind_of_timestamp_max_in_list, -1, -1):
            index = index_to_examine[i]
            #if df.loc[index]['verb'] == 'Session.Start': # parseable codestate not found
            #    return None, True, False
            most_recent_codeState = df_name_tp.loc[index]['codeState']
            dict_tests = find_tests_in_codestate_for_functions(most_recent_codeState, all_TP_prog_functions_name_by_tp[tp])
            if dict_tests != None: # parseable
                col_functions = []
                col_tests_number = []
                for key, value in dict_tests.items():
                    col_functions.append(key)
                    col_tests_number.append(value)
                
                nb_rows = len(dict_tests)
                if col_tests_number == [None]*nb_rows:
                     print(f'aucune fonction réalisée par {name}, indice {index}')
                col_actors = [name] * nb_rows
                col_tp = [tp] * nb_rows
                col_index = [index] * nb_rows
                df_result = pd.DataFrame({'actor' : col_actors, 'tp' : col_tp, 'function_name' : col_functions, \
                                          'tests_number' : col_tests_number, 'index' : col_index })
                return df_result, False, False                                                      
        # not parsable
        return None, True, False


# %%
def find_tests_for_tp_tpprog(df:pd.DataFrame, tp:str) -> tuple[pd.DataFrame, list[str], list[str]]:
    """
    Selects in df rows of tp and Type_TP is TP_Prog, selects for each student the most recent parsable codeState and returns :
    - a DataFrame with columns actor, tp, Tp_Prog, function_name, test_number (int or None if not present in codestates)
    - a first list of students for which the codeState cannot be analyzed (Python or l1test syntax error)
    - a second list of students for which no codeState was found
    """
    df_result = pd.DataFrame(columns=['actor', 	'tp', 	'function_name', 	'tests_number', 	'index'])
    empty_codestate_students = []
    cannot_analyze_codestate_students = []
    actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['actor']
    column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['binome']
    all_students_tp  = set(actor_column_tp).union(set(column_binome_tp))
    if '' in all_students_tp:
        all_students_tp.remove('')
    for name in all_students_tp:
        df_name, cannot_analyze_codestate, empty_codestates = find_tests_for_tp_tpprog_name(name, df, tp)
        if cannot_analyze_codestate:
            cannot_analyze_codestate_students.append(name)
        if empty_codestates:
            empty_codestate_students.append(name)
        if df_name is not None:
            df_result = pd.concat([df_result, df_name], ignore_index=True)
    return df_result, cannot_analyze_codestate_students, empty_codestate_students      


# %%
# TP2
df_tests_tp2, cannot_analyze_codestate_students_tp2, empty_codestate_students_tp2  = find_tests_for_tp_tpprog(df, 'Tp2')

# %%
df_tests_tp2

# %%
# TP3
df_tests_tp3, cannot_analyze_codestate_students_tp3, empty_codestate_students_tp3  = find_tests_for_tp_tpprog(df, 'Tp3')

# %%
df_tests_tp3

# %%
# TP4
df_tests_tp4, cannot_analyze_codestate_students_tp4, empty_codestate_students_tp4  = find_tests_for_tp_tpprog(df, 'Tp4')

# %%
df_tests_tp4

# %%
# TP5
df_tests_tp5, cannot_analyze_codestate_students_tp5, empty_codestate_students_tp5  = find_tests_for_tp_tpprog(df, 'Tp5')

# %%
df_tests_tp5

# %%
# TP6
df_tests_tp6, cannot_analyze_codestate_students_tp6, empty_codestate_students_tp6  = find_tests_for_tp_tpprog(df, 'Tp6')

# %%
df_tests_tp6

# %%
# TP7
df_tests_tp7, cannot_analyze_codestate_students_tp7, empty_codestate_students_tp7  = find_tests_for_tp_tpprog(df, 'Tp7')

# %%
df_tests_tp7

# %%
# TP8
df_tests_tp8, cannot_analyze_codestate_students_tp8, empty_codestate_students_tp8  = find_tests_for_tp_tpprog(df, 'Tp8')

# %%
df_tests_tp8

# %%
# TP9
df_tests_tp9, cannot_analyze_codestate_students_tp9, empty_codestate_students_tp9  = find_tests_for_tp_tpprog(df, 'Tp9')

# %%
df_tests_tp9

# %% [markdown]
# # ToDo
#
# **DONE:**
# - We must anonymized the too_short_sessions.csv, the column of actors
# - semaine_5: there are two sessions, but only one sessions they were working, because the second session was controle TP and the internet was cut
# - Ignore the part of **utilisation print**
# - we want just Nom_TP_PPROGRAMMATION without the first week
# - Leave the part after the print on Etude_sur_les_testes.py
# - How write boolean for test green or red for Run.Test : DONE!
# - See cleaning.keep_research_data_only in notebooks/Init_data.py
# - try to find another way of coding of correct_filename_infere_in_subset, reduce the number of if
# - correct the filename_inere in case 1 and two by the P_codeState, and calculate the percentage of emoing traces only for those with empty filename, which we can't find the filename by the P_codeState : Done!
# - add diagram to compare the number of students using each verb and the total number of present student in TP (TP_prog) : DONE! 4.8
# - Calculate the total number of Run.Test in the too_short_session : DONE! 4.11
# - calculate the percentage of how many students in each TP, (only TP_prog) did the Run.Test from all present students : Done! 4.14
# - In 4.15 :add the plotting and change the code: DONE! the time of execution reduced from 4 mins to 3s !
# - add in Readme how the dataframe form json is sorted by actor (alphabet) an then by session.id and then tempstamp.date, this is in cleaning.py of Thomas version : DONE!
# - Calculate how many students didn't do the run.test in each TP, TP_prog : DONE!
# - add in 4.13, the student which were in 60% of doing the run.test, are they empty tests or not. you should extract their name: DONE!
# - add number of student who did each file.py in TP_GAME : DONE 4.18
# - look Run.Test in each TP if the value in column tests is empty or not. if the Run.Test is clicked once and the tests is empty so there is no Run.Test:  DONE 4.18
# - In each TP_GAME, look for each student, in the newest file of Run.Test, how many their column tests is empty and isn't : DONE but need to check 
# - check this https://gitlab.univ-lille.fr/L1-programmation/analyse-des-traces/-/blob/amadou_analyse/notebooks/PJI_amadou_2024.py 
# - add how many students in ech TP , TP_prog, did the run test and from doing this run.test, how many of them are doing only empty ones and the percentage of doing run.test - empty run.test = a value / total students who did the TP : DONE!
# - add table in phase2, to explain better in markdown : Done
# - error in analyze for id df[df['_id.$oid'] == '673db140bd5a98b8f9dd1f13'][['filename_infere','filename','P_codeState','verb','commandRan','TP','Type_TP']] : DONE
# - seperate part Bizzar indices in another notebook, phase 3 nettoyage and then give the output of this file to another notebook: DONE
# - add trace in variable_constant : DONE!
#
# **In process:**
#
#
# **New :**
#
# - How many students stoped doing run.test in TP-GAME 
# - check the students who didn't do the test during the TP_GAME, wht is the reason, didn't they do any test during other TP or not
#
# - add in TP_GAME and for student who didn't do the run.test, in which of P_codestate (the last one) is not empty, and if there is any name in the previous step, then check each file for them (if they had worked on all files)
#
# - look first which students has the red tests and what they did?
#     - test red and solved the bug
#     - test red and left and went to do something else
#     - test red and didn't do anything else
#
# - check the file duplicated_runTest.ipynb
#
# - add part to find all the run.Test red and see how many students did Run.Debogguer just after this test red
#
# - add def for the functions in variable_constant_2425 (by mirabelle)
#
# - seperate the name between traces in variable_constant_2425 and create in another function 
#
# - add find_test_final in analyze
#
# - add in comment in find_test_final that the values for students(test number is Nan and they have a name of TP, it is not bizzar because it means student did only Run.command 
# and since the codestate is empty, there is no calling function in codestate but there is in commandRan)
# - find_test_final : the number of test shows the number of test students did for each function that is written in the codestate, if it is zero, means there is the function in codestate but with zero test, if Nan means there is no fonction in codestate or it is empty, (this is done by finding the most recent file if it is analyzable)
# - check how in nettoyage decides for the situation when there are different names of functions of both tp_mani and tp_prog 
# - check how it decides for tp name when there are different names of functions of different tps
# - read assert and test automatisé
#
# - new:
# - add checking the name extracted of traces with pattern (all fileanem)
# - add third condition which is going to check the text in tp after not finding filename_infere by def
# - add another dictionar only include the text of tp not the functions
#
# ## To show : 
# - 4.14, add a diagram on Run_test rate
# - 4.19
#
