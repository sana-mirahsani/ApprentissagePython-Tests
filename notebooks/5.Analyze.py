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
# 2. Bizzar indices
# 3. Load DataFrame : Final_nettoyage_2425.csv
# 4. Analyze
#
#     4.1 Total number of students during semester
#
#     4.2 Total number of students during each week
#
#     4.3 Total number of students during each TP
#
#     4.4 Total number of students during TP_mani and TP_prog
#
#     4.5 Number of TP_mani and TP_prog in each TP 
#
#     4.6 Number of student using each verb in each TP
#
#     4.7 Number of student using each verb in only each TP_prog
#     
#     4.8 Comparing the total number of students with the number of students using each verb in TP_prog
#
#     4.9 Number of each TP in each seance
#
#     4.10 Number of empty filename_infere in each seance
#
#     4.11 Calculate the total number of Run.Test in the too_short_session.csv
#
#     4.12 
#

# %% [markdown]
# ## Import Libraries

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import ast
from src.features import io_utils, data_testing
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant_2425 import SORTED_SEANCE, TP_NAME
import matplotlib.pyplot as plt
import numpy as np
import difflib

# just for test
from src.data.variable_constant_2425 import SORTED_SEANCE, all_TP_functions_name 
import re
from src.data.variable_constant_2425 import FILES_BY_TP
from src.features import data_cleaning

# just for test
# Global variable pattern
pattern = ''
for tp_name in FILES_BY_TP:

    file_name = '|'.join(tp_name)
    pattern = pattern +  file_name + '|'

pattern = pattern  + 'Irrelevant' 


# %% [markdown]
# ## Load DataFrame

# %%
df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase2_nettoyage_fichiere.csv')


# %% [markdown]
# ## Bizzar indices

# %% [markdown]
# **What are these Bizzar indices?**
#
# There are filename_infere that are same as their filename but when I compare the content of their P_codeState, the name should be something else, it means that the student used a file which has already a name between traces or even with the function's name it should be another name, but she changed the name to another name which is correct also; and since in phase2 nettoyage, it checks first if the name is in the pattern, if so return the name without checking the P_codeState (it's more efficase than checking the content of P_codeState for each row), so it is obvious these names didn't change eventhough they should have. These traces are in three situations:
#
# **Note :These traces are only for Run.Test and these are the number of traces , NOT number of the students**
#
# - filename_impossible_to_find_index : It has a filename_infere but can't find the filename by P_codestate to check them 
# - filename_case1_index : The filename_infere it is not same as the name between <trace></trace> in P_codeState
# - filename_case2_index : The filename_infere it is not same as the name found by the functions in P_codeState
#
#
# **Why we have the Bizzar indices? Shouldn't be corrected in phase1 or 2 of nettoyage?**
#
# It's because of the function's structure **correct_filename_infere_in_subset** in **data_cleaning**. I prioritize the matching of filename_infere with the pattern (which include all the names of files) , and if matches, so it returns the filename_infere and it skips the checking part of P_codeState which works for the majority but if there are traces where their name of filename_infere is correct but it is not same as the name found by looking at the P_codeState, the algorithm fails. Of course we can prioritize the checking P_codeState in the function, BUT it will take a lots of time, and it will check each P_codeState of traces which are already correct, so it won't be effective. However, now that the majority of data is cleaned, we can check again what are the filename_infere which doesn't correspond to name found in P_codeState and replace them. 
#
# **What we should to them?**
# The filename_infere which will be found in case1 or case2, can be replaced by the name is found by whether the name between traces or the functions name in P_codeState, (since we are more sure that the name found by P_codeState is more correct, we can replace them) but for those in case **filename_impossible_to_find_index** , which means we can't find the name neither by their functions or name beween traces, we can't do anything, so we remove them to have a correct analyze.

# %%
# extract these strange indices
def find_strange_filename_infere(TP,verb):

    # create the lists
    filename_impossible_to_find_index, filename_case1_index, filename_case2_index = [], [] , []
    
    for index, row in df[(df['TP'] == TP) & (df['verb'] == verb)].iterrows():

        match_state = re.search(r"<trace>(.*?)</trace>", str(row['P_codeState']))
        
        if match_state:
            
            trace_line = match_state.group(1)
                
            # Case1 : if <trace></trace> exists and the name between is different from the name in filename_infere
            if row['filename_infere'] != trace_line:
                # Save the index
                filename_case1_index.append(index)
                
                # check the similarity, to find the correct name
                filename_infere_removed = row['filename_infere'].replace('.py', '')
                similarity = difflib.SequenceMatcher(None, trace_line[:-3], filename_infere_removed).ratio()

                if similarity > 0.8:
                        # if the similarity is more than 80%, then change it
                        df.loc[index,'filename_infere'] = trace_line
                    
        else:
            # Case2 : if <trace></trace> is removed, try to find the name by the functions 
            filename_infere_codestate = data_cleaning.find_filename_by_function_name(all_TP_functions_name,row['P_codeState'])

            if filename_infere_codestate == '': 
                # Can't find the filename by functions in P_codeState
                # Save the index
                filename_impossible_to_find_index.append(index)

            else: 
                # Can find the fielname by functions' name but it is not same as the name in filename_infere
                if row['filename_infere'] != filename_infere_codestate:
                    
                    # Save the index
                    filename_case2_index.append(index) 

                    # Change the name by the correct one
                    df.loc[index,'filename_infere'] = filename_infere_codestate


    return filename_impossible_to_find_index, filename_case1_index, filename_case2_index

# Create Dataframe
df_strange_filenames_Run_Test = pd.DataFrame(columns=['TP','filename_impossible_to_find_index', 'filename_case1','filename_case2']) 

# Fill dataframe only for Run.Test for each TP
for tp in TP_NAME:

    impossible_filename, filename_case1, filename_case2 = find_strange_filename_infere(tp,'Run.Test')
    
    # Append row to df
    df_strange_filenames_Run_Test = pd.concat([
        df_strange_filenames_Run_Test,
        pd.DataFrame({'TP': [tp], 'filename_impossible_to_find_index': [impossible_filename], 'filename_case1': [filename_case1], 'filename_case2': [filename_case2]})
    ], ignore_index=True)

df_strange_filenames_Run_Test

# %%
df.loc[261557,'P_codeState']

# %%
df.loc[261557,'filename_infere']

# %%
for index, row in df_strange_filenames_Run_Test.iterrows():
    print(row['TP'])
    print(len(row['filename_case1']))


# %%
for index, row in df_strange_filenames_Run_Test.iterrows():
    print(len(row['filename_case1']))

# %%
list_indices = df_strange_filenames_Run_Test[df_strange_filenames_Run_Test['TP'] == 'Tp6']['filename_case2'].tolist()

# %%
for i in list_indices[0]:
    
    print('-----------------------')
    print(i)
    print(df.loc[i,'verb'])
    print(df.loc[i,'filename'])
    print(df.loc[i,'filename_infere'])
    print(df.loc[i,'P_codeState'])
    

# %%
# save the removed trace into a csv
io_utils.write_csv(df_strange_filenames_Run_Test,INTERIM_DATA_DIR,'bizzar_traces')

# %%
all_percentage_removed = [] # save later for the plot

for tp in TP_NAME:

    total_traces_of_tp = (df['TP'] == tp).sum()
    total_traces_of_empty_filename = len(df_strange_filenames_Run_Test[df_strange_filenames_Run_Test['TP'] == tp]['filename_impossible_to_find_index'].iloc[0])
    total_traces_of_filename_case1 = len(df_strange_filenames_Run_Test[df_strange_filenames_Run_Test['TP'] == tp]['filename_case1'].iloc[0])
    total_traces_of_filename_case2 = len(df_strange_filenames_Run_Test[df_strange_filenames_Run_Test['TP'] == tp]['filename_case2'].iloc[0])

    total_traces_to_remove = total_traces_of_empty_filename 

    percentage_removed = (total_traces_to_remove / total_traces_of_tp) * 100
    all_percentage_removed.append(percentage_removed)

    print("---------------------------")
    print(tp)
    print(f"Total traces of empty_filename : {total_traces_of_empty_filename}")
    print(f"Total traces of filename_case1 : {total_traces_of_filename_case1}")
    print(f"Total traces of filename_case2 : {total_traces_of_filename_case2}")
    print(f"Total traces to remove : {total_traces_to_remove}")
    print(f"Total traces of TP : {total_traces_of_tp}")
    print(f"{percentage_removed:.2f}% of the rows will be removed.")

# %% [markdown]
# ### Plot the percentage of removing bizzar indices

# %%
indices = TP_NAME

plt.figure(figsize=(10, 6))
plt.bar(indices, all_percentage_removed, color='coral')
plt.title('Percentage of Rows Removed')
plt.xlabel('Index')
plt.ylabel('Percentage Removed (%)')

# Add percentage labels above bars
for i, v in enumerate(all_percentage_removed):
    plt.text(i, v + 1, f"{v:.1f}%", ha='center')

plt.ylim(0, 10)
plt.show()

# %% [markdown]
# **Interpretation** 
#
# The plot above illustrates the percentage of rows that it was impossible to find a filename_infere by their P_codeState so they need to be removed to ensure accurate analysis. As shown, the highest percentage is for TP1 at 1.1%, which is relatively minor and not a major concern. Notably, TP_GAME (the most critical case) requires only 0.3% of its rows to be removed. This suggests we can proceed with the removal without worrying about a significant impact on the results.

# %%
old_df_before_removing = df.copy() # save the original one just in case

# Before removing
len(df)

# %%
columns = ['filename_impossible_to_find_index', 'filename_case1', 'filename_case2']

for tp in TP_NAME:

    for column in columns:
        index_to_removed = df_strange_filenames_Run_Test[df_strange_filenames_Run_Test['TP'] == tp][column].iloc[0]

        if index_to_removed != []:
            df = df.drop(index=index_to_removed)

# %%
# After removing traces
len(df)

# %% [markdown]
# From now, the analyze will be on the df but without those bizzar traces!

# %% [markdown]
# ## Analyze

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
# **Interpretation**

# %% [markdown]
# ### 4.3 Total number of students during each TP

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
# ### 4.4 Total number of students during TP_mani and TP_prog

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
df_students_per_Type_Tp[:11].set_index('TP')[['TP_mani', 'TP_prog']].plot(kind='bar', figsize=(12, 6))

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
df_students_per_verb[:11].set_index('TP')[['Run.Command', 'Run.Program','Run.Test','Run.Debugger']].plot(kind='bar', figsize=(12, 6))

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
# ### 4.8 Comparing the total number of students with the number of students using each verb in TP_prog

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
df_too_short = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='too_short_sessions.csv')
df_too_short 

# %%
df_inlcuding_too_short_sessions = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase1_nettoyage_fichiere.csv')

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
# can eb in data_testing
def calculate_verb_in_TP(df,verb,tp): 

    df_filtered = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')] 
    actor_column  = df_filtered['actor']
    binome_column = df_filtered['binome']
    all_students  = set(actor_column).union(set(binome_column))
    all_students.remove('')

    students_excluding_verb = []
    students_including_verb = []

    for name in all_students:    

        verbs_of_student = df_filtered[(df_filtered['actor'] == name) | (df_filtered['binome'] == name)]['verb'].unique()
        
        if not verb in verbs_of_student: # not doing Run.Test
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
    if tp != 'Tp10':
        df_empty_test = pd.concat([
            df_empty_test,
            pd.DataFrame({'TP': [tp], 'total_student': [len(all_students)],'num_doing_run_test' : [len(total_students_doing_test)], 'num_doing_empty_run_test' : [len(total_students_with_empty_test)], 'name_doing_run_test' : [total_students_doing_test], 'name_doing_empty_run_test' : [total_students_with_empty_test]})
        ], ignore_index=True)

    else:
        df_empty_test = pd.concat([
            df_empty_test,
            pd.DataFrame({'TP': [tp], 'total_student': [0], 'num_doing_run_test' : [0],'num_doing_empty_run_test' : [0], 'name_doing_run_test' : [''], 'name_doing_empty_run_test' : ['']})
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

num_students_with_empty_tests, num_students_with_a_tests


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
# ### 4.19 Extract the consecutive Run.Test of students who is doing a real test

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


# %%
def extract_consecutive_run_test(df,tp):
    """
    Extract the consecutive indices of Run.Test
    In all_students_doing_real_test, we have the name of all students for each TP, who did a real test (Did Run.Test and tests is not empty),
    I extract the students which have more than 2 Run.Test in a TP.
    Then extract these indices, and check if there are consecutive indices or not, if so it will print the name and the number of total Run.Test appearence. 
    """
    
    for name in all_students_doing_real_test[tp]:
        df_filtered = df[(df['TP'] == tp) & ((df['actor'] == name) | (df['binome'] == name))]
        if 'Run.Test' in df_filtered['verb'].unique():
            num = df_filtered['verb'].value_counts()['Run.Test']

            if num > 2:
                
                lst = df[(df['TP'] == tp) & ((df['actor'] == name) | (df['binome'] == name)) & (df['verb'] == 'Run.Test')].index.tolist()

                is_consecutive = all(b - a == 1 for a, b in zip(lst, lst[1:]))
                if is_consecutive:
                    print(name,num)

for tp in TP_NAME:
    print(tp)
    extract_consecutive_run_test(df,tp)

# %% [markdown]
# ### 4.20 Get_mad_actors

# %% [markdown]
# Now we are facing with two different type of students during on TP_GAME, the one who did a Run.Test but their tests column is not empty, and the one with the empty tests. Alos now we want to know what is the reason that they are students with empty tests, and find another type of students in doing Run.Test but not empty. This type consider the students who pushed the Test button without changing any thing (mad students). Since we already have the list of students with Run.Test (not empty) in 4.19, we can use this list to find them easier.

# %%
std_list = all_students_doing_real_test['Tp_GAME']
std_list[1]

# %%
df[(df['TP'] == 'Tp_GAME') & (df['binome'] == 'kade-bhoye.wann.etu')][['verb','P_codeState','filename_infere','tests','timestamp.$date']]

# %%
df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'kade-bhoye.wann.etu')][['verb','P_codeState','filename_infere','tests','timestamp.$date']]

# %%
print(df.loc[143788,'P_codeState']) # Run.program

# %%
print(df.loc[143789,'P_codeState']) # Run.Test

# %% [markdown]
#  File.Save

# %%
print(df.loc[143791,'P_codeState']) # Run.Test with an error

# %%
print(df.loc[143791,'tests'])

# %% [markdown]
# File.Save

# %%
print(df.loc[143793,'P_codeState']) # Run.Test with fixed bug

# %%
print(df.loc[143794,['commandRan','P_codeState']]) # Run.Command

# %%
print(df.loc[143795,['commandRan','P_codeState','verb']]) # Docstring.Generate

# %%
print(df.loc[143796,['commandRan','P_codeState','verb']]) # filen.Save

# %%
print(df.loc[143797,'P_codeState']) # Run.Test

# %%
print(df.loc[143797,'tests'])

# %%
print(df.loc[143798,'P_codeState']) # Run.program

# %%
print(df.loc[143798,'stderr'])

# %%
print(df.loc[143799,'commandRan']) # Run.command

# %%
print(df.loc[143800,'commandRan']) # Run.command

# %%
print(df.loc[143801,'verb']) # File.Save

# %%
print(df.loc[143802,'P_codeState']) # Run.Program

# %%
print(df.loc[143803,'P_codeState']) # Run.Program

# %%
print(df.loc[143804,'P_codeState']) # Run.Test

# %%
print(df.loc[143804,'tests'])

# %%
print(df.loc[143805,'P_codeState']) # Run.Program

# %%
print(df.loc[143806,'P_codeState']) # Run.Program

# %%
print(df.loc[143807:143814,['verb','commandRan','actor','filename_infere']]) # Run.Command

# %%
df.loc[143814,'filename_infere'] # 'File.Open'

# %%
print(df.loc[143815,'filename_infere']) # File.Save

# %%
print(df.loc[143816,'P_codeState']) # Run.Program

# %%
print(df.loc[143816,'P_codeState']) # Run.Program

# %%
print(df.loc[143817,'P_codeState']) # Run.Program

# %%
print(df.loc[143818,'P_codeState']) # Run.Program

# %%
print(df.loc[143819,'commandRan']) # Docstring.Generate

# %%
print(df.loc[143820,'filename_infere']) # File.Save

# %%
print(df.loc[143821,'P_codeState']) # Run.Program

# %%
print(df.loc[143822,'P_codeState']) # Run.Program

# %%
print(df.loc[143823,'filename_infere']) # File.Save

# %%
print(df.loc[143824,'P_codeState']) # Run.Program

# %%
print(df.loc[143825,'P_codeState']) # Run.Program

# %%
print(df.loc[143826,'P_codeState']) # Run.Program

# %%
print(df.loc[143827,'P_codeState']) # Run.Test

# %%
print(df.loc[143827,'tests']) # tests

# %%
print(df.loc[143828,'filename_infere']) # File.Save

# %%
print(df.loc[143829,'P_codeState']) # Run.Program

# %%
print(df.loc[143830,'P_codeState']) # Run.Program

# %%
print(df.loc[143831,'filename_infere']) # File.Save

# %%
print(df.loc[143832,'P_codeState']) # Run.Program

# %% [markdown]
# Conclusion
#
# At first student, started with a code which had a bug and then he fixed the bug (he found it and fixed it) but after a while in the same day, he got stuck on a part of code, that it wasn't not correct but he couldn't find it! even when he tried with Run.Test find he couldn't because every time he ran the run.Test on the part which was correct and he forgot to change the part to test, so every time the Run.Test was PASSED but when he tried to execute the code, it raised an error! At the end he tried several ways to find the bug but he couldn't so it gave up even though the result of test is successful.
#
# This means that they are students with not empty test and a progress but at the end they gave up, so checking only the content of P_codeState and tests is not enough, we need a value that says when the Run.programm is there, is the result successful or it raised an error? because as we saw sometimes the reuslt of tests is True but there is a bug in the code. Also if student do the run.test and the result is not successful it is easy to find it, because in this case, we only need to check the result of test, and if in this case the content of P_codeState is still the same in each run.test and run.test is not successful, so it means the students tried just pushing the button!
# So we can conclude there are 3 types of students from the students with a real test (not students with the empty tests)
#
# different types of students :
# <br>
#     - strong students : They started strongly and they solved all the bugs without any giving up.
#     <br>
#     - tried failed students : they tried and they changed but at the end they gave up because they couldn't find the bug (Whether the result of test is successful or not)
#     <br>
#     - tried successful students : They tried and they have a progress and at the end they understood the TP.
#     <br>
#     - lazy students : They don't have lot's of traces for a TP and during the TP they didn't change a specific thing. (wether the test result is passed or not)
#     <br>
#     - mad students : They tried lot's of Run.Test with the same code or a tiny difference during a day

# %% [markdown]
# ### analyze function

# %%
strong_student = []
tried_failed_students = []
tried_successful_students = []
lazy_students = []
mad_students = []

# %%
std_list = all_students_doing_real_test['Tp_GAME']
std_list

# %%
# add the correct format of time 
df['correct_time'] = pd.to_datetime(df['timestamp.$date'], format='mixed')
df['correct_time'] = df['correct_time'].dt.date

# %%
std_list[0]

# %%
# extract the different days in one TP for one student
unique_days = df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'avsin.ata.etu')]['correct_time'].unique()
unique_days

# %%
# day one
analyze_the_process_of_each_day(unique_days[0],'avsin.ata.etu') # lazy_student just for this day

# %%
df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'avsin.ata.etu')]['binome']

# %%
# day two
analyze_the_process_of_each_day(unique_days[1],'avsin.ata.etu') # tried_successful_students just for this day

# %%
std_list[1]

# %%
unique_days = df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'hugo.vandewalle2.etu')]['correct_time'].unique()
unique_days

# %%
# day one
analyze_the_process_of_each_day(unique_days[0],'hugo.vandewalle2.etu') # strong_student ( because it starts strongly and most of his test.results are )

# %%
# day one
analyze_the_process_of_each_day(unique_days[1],'hugo.vandewalle2.etu') # strong_students

# %%
# another example
df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'ibrahima-al-amine.diaw.etu')][['verb','P_codeState','filename_infere','tests','timestamp.$date','correct_time']] 

# %%
# extract the different days in one TP for one student
unique_days = df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'ibrahima-al-amine.diaw.etu')]['correct_time'].unique()
unique_days

# %%
# day one
analyze_the_process_of_each_day(unique_days[0],'ibrahima-al-amine.diaw.etu')

# %%
# day two
analyze_the_process_of_each_day(unique_days[1],'ibrahima-al-amine.diaw.etu')

# %%
# day 3
analyze_the_process_of_each_day(unique_days[2],'ibrahima-al-amine.diaw.etu')

# %%
# day 4
analyze_the_process_of_each_day(unique_days[3],'ibrahima-al-amine.diaw.etu')

# %%
# day 5
analyze_the_process_of_each_day(unique_days[4],'ibrahima-al-amine.diaw.etu')

# %%
# another students 
std_list[2]

# %%
# extract the different days in one TP for one student
unique_days = df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'richard.kpande-adzare.etu')]['correct_time'].unique()
unique_days

# %%
# day 1
analyze_the_process_of_each_day(unique_days[0],'richard.kpande-adzare.etu')

# %%
# day 1
analyze_the_process_of_each_day(unique_days[1],'richard.kpande-adzare.etu')

# %%
# day 2
analyze_the_process_of_each_day(unique_days[2],'richard.kpande-adzare.etu')

# %%
print(std_list[3])
# extract the different days in one TP for one student
unique_days = df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'alix.carton2.etu')]['correct_time'].unique()
unique_days

# %%
# day 1
analyze_the_process_of_each_day(unique_days[0],'alix.carton2.etu')

# %%
# check each different day for this student during the TP_GAME
df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'ibrahima-al-amine.diaw.etu') & (df['correct_time'] == unique_days[0])][['verb','filename_infere','P_codeState','commandRan']]

# %% [markdown]
# Conclusion for this day : Just open and save action on one file

# %%
df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'ibrahima-al-amine.diaw.etu') & (df['correct_time'] == unique_days[1])][['verb','filename_infere','P_codeState','commandRan','tests']]

# %%
print(df.loc[118421,'P_codeState']) # Run.Test

# %%
print(df.loc[118421,'tests']) # multipie test so it should check the size of the test and check the status and verdict and line tested of each dictionary

# %%
df_of_column_test[df_of_column_test['original_index'] == 118421] # successful test

# %% [markdown]
# What is a successful test?
#
# A successful test, is the test that includes atleast once all the function written in the code and its verdict is PassedVerdict and the status is True.

# %%
print(df.loc[118425,'P_codeState']) # Run.Test : add some parts , P_codeState is different

# %%
df_of_column_test[df_of_column_test['original_index'] == 118425] # incomplete test!

# %% [markdown]
# What is a incomplete test?
#
# An incomplete test is a test that all the verdict are Passedverdict and their status are True but it doesn't include all the function's name in the P_codeState

# %%
df.loc[118427,'commandRan'] # Run.Command

# %% [markdown]
# it just ran a function in a shell and entered (since there is \n at the end)

# %%
print(df.loc[118430,'P_codeState'] )# Run.Test

# %%
df_of_column_test[df_of_column_test['original_index'] == 118430] # incomplete test! with different P_codeState

# %%
print(df.loc[118433,'P_codeState'] )# Run.Test

# %%
df_of_column_test[df_of_column_test['original_index'] == 118433] # incomplete test! without any changes but with different P_codeState

# %%
print(df.loc[118435,'P_codeState'] )# Run.Test

# %%
df_of_column_test[df_of_column_test['original_index'] == 118435] # again with same test (incomplete) but with different P_codeState

# %% [markdown]
# **conclusion** for the second day for this person:
#
# He tried and wrote something but after a while he didn't change the test part at all but every time before every run.test he add or change the code in the P_codeState

# %%
df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'ibrahima-al-amine.diaw.etu') & (df['correct_time'] == unique_days[2])][['verb','filename_infere','P_codeState','commandRan','tests']]

# %%
print(df.loc[118671,'P_codeState']) # Run.test

# %%
df_of_column_test[df_of_column_test['original_index'] == 118671] # Run.Test incomplete test and same test but different P_codeState

# %%
print(df.loc[118672,'P_codeState']) # Run.Program no changes 

# %% [markdown]
# **conclusion**
#
# For the third day, he worked on another file which is not very important but he tried Run.Test and Run.program with the same code and with the same test result as the day before.

# %%
df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'ibrahima-al-amine.diaw.etu') & (df['correct_time'] == unique_days[3])][['verb','filename_infere','P_codeState','commandRan']]

# %% [markdown]
# This day just open the file

# %%
df[(df['TP'] == 'Tp_GAME') & (df['actor'] == 'ibrahima-al-amine.diaw.etu') & (df['correct_time'] == unique_days[4])][['verb','filename_infere','P_codeState','commandRan']]

# %%
print(df.loc[119224,'P_codeState']) # Run.test

# %%
df_of_column_test[df_of_column_test['original_index'] == 119224] # complete-error test!

# %% [markdown]
# what is a complete-error test?
#
# It means all the functions in the code are included in the tests but there is at least one test with FailedVerdict and False status.

# %%
print(df.loc[119226,'P_codeState']) # Run.test

# %%
df_of_column_test[df_of_column_test['original_index'] == 119226] # complete-error test! with a tiny difference in test part

# %%
check_difference_between_two_code(df.loc[119224,'P_codeState'],df.loc[119226,'P_codeState'])

# %%
print(df.loc[119228,'P_codeState']) # Run.test

# %%
df_of_column_test[df_of_column_test['original_index'] == 119228] # successful test! with a progress

# %%
check_difference_between_two_code(df.loc[119226,'P_codeState'],df.loc[119228,'P_codeState'])

# %%
print(df.loc[119231,'P_codeState']) # Run.test

# %%
df_of_column_test[df_of_column_test['original_index'] == 119231] # successful test! with a progress

# %% [markdown]
# ### functions for checking different type of actors

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
def analyze_the_process_of_each_day(day,actor):

    df_one_day = df[(df['TP'] == 'Tp_GAME') & (df['actor'] == actor) & (df['correct_time'] == day)][['verb','filename_infere','P_codeState','commandRan']]
    print(f"Student : {actor}, Day : {day}")
    last_p_code_state = None

    if len(df_one_day) > 2:

        for index, row in df_one_day.iterrows():

            print(row['filename_infere'],row['verb'],index)

            if row['verb'] == 'Run.Command':
                print(row['commandRan'])

            elif row['verb'] == 'Run.Test':
                print("--------------------------------------------------------------------------------------------------------------")
                print(row['P_codeState'])

                if last_p_code_state:
                    check_difference_between_two_code(last_p_code_state,row['P_codeState'])

                last_p_code_state = row['P_codeState']

                print(df_of_column_test[df_of_column_test['original_index'] == index])

            elif row['verb'] == 'Run.Program':
                print(row['P_codeState'])

                if last_p_code_state:
                    check_difference_between_two_code(last_p_code_state,row['P_codeState'])

                last_p_code_state = row['P_codeState']
            
            elif row['verb'] == 'Run.Debugger':
                print(row['P_codeState'])

                if last_p_code_state:
                    check_difference_between_two_code(last_p_code_state,row['P_codeState'])

                last_p_code_state = row['P_codeState']


# %% [markdown]
# ### Red_test

# %% [markdown]
# Different type of students of Red test: This is not correct
#
# - passed_after_failing_test : Students solved the problem after having a Red Test
#
# - abandoned_file_started_new : Students couldn't solve the bug and restart a another test
#
# - red_test_no_recovery : Students couldn't solve the bug and there is no more Run.Test (the left completely!) after a red test
#
# Red test: At least one of the colors in tests is red
#
# New classification:
#
# - progressed students
# - blocked students

# %%
all_students_doing_real_test['Tp1'] # 4.19 


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
# #### Analyze TP1

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
# #### Analyze TP2

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
    
    unique_filename_infere = df.loc[all_list_indices,'filename_infere'].unique().tolist()
    
    # Select only the rows at the given indices
    selected_rows = df.loc[all_list_indices]

    # Group them by the 'filename_infere' column
    run_test_classification = selected_rows.groupby('filename_infere')

    # Example: print each group
    for filename, group in run_test_classification:
        print(f"\nGroup: {filename}")
        print(group)

    return run_test_classification


# %%
# step2 : check the overlab
def find_overlab_tests(test1_index,test2_index):

    # extract the two tests
    test1 = df_of_column_test[df_of_column_test['original_index'] == test1_index]
    test2 = df_of_column_test[df_of_column_test['original_index'] == test2_index]

    # check if they have overlab by merging them
    overlap = test1.merge(test2, how='inner')

    if not overlap.empty: # they have overlab
        print("There is overlap!")
        print(overlap)
    else:
        print("No overlap.")



# %%
different_filenames

# %%
for filename, group in different_filenames:
        print(f"\nGroup: {filename}")
        print(type(group))

# %%
# main
all_indices = merge_red_and_green_test('massil.kichi.etu') # step 0
different_filenames = classify_by_filename(all_indices) # step 1


# %%
list1 = df_test_TP2[df_test_TP2['name'] == 'massil.kichi.etu']['indices_red_test'].loc[0] 
list2 = df_test_TP2[df_test_TP2['name'] == 'massil.kichi.etu']['indices_green_test'].loc[0]

merged_sorted = sorted(list1 + list2)
merged_sorted

# %%
# find unique filenames
unique_filename_infere = df.loc[merged_sorted,'filename_infere'].unique()
unique_filename_infere

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1659]

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1661]

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1664]

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1666]

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1668]

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1670]

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1673]

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1675]

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1679]

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 1681]

# %%
df_test_TP2[df_test_TP2['name'] == 'manel.cherief.etu']['indices_red_test'].loc[0] ,df_test_TP2[df_test_TP2['name'] == 'manel.cherief.etu']['indices_green_test'].loc[0]

# %%
list1 = df_test_TP2[df_test_TP2['name'] == 'manel.cherief.etu']['indices_red_test'].loc[0] 
list2 = df_test_TP2[df_test_TP2['name'] == 'manel.cherief.etu']['indices_green_test'].loc[0]

merged_sorted = sorted(list1 + list2)
merged_sorted

# %%
# find unique filenames
unique_filename_infere = df.loc[merged_sorted,'filename_infere'].unique()
unique_filename_infere

# %%
# find unique days
unique_correct_time = df.loc[merged_sorted,'correct_time'].unique()
unique_correct_time

# %%
run_test = df.loc[merged_sorted]
run_test[run_test['correct_time'] == unique_correct_time[0]]

# %%
df.loc[174404:174411]

# %%
if df.loc[174404,'codestate'] == df.loc[174409,'codestate']: print(True) # codestates are not equal

# %%
code1 = df.loc[174404,'codestate']
code2 = df.loc[174409,'codestate']

check_difference_between_two_code(code1,code2) # P_codestate are different


# %%
print(code1)

# %%
print(code2)

# %%
# check tests
df_of_column_test[df_of_column_test['original_index'] == 174404]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174409]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174411]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174413]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174416]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174419]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174421]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174424]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174427]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174430]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174433]

# %%
df_of_column_test[df_of_column_test['original_index'] == 174435]

# %%
df_run_test = df.loc[merged_sorted]
run_test_day1 = df_run_test[df_run_test['correct_time'] == unique_correct_time[0]]
#run_test_day1

# %%
df_1 = df.loc[41643:41653]
df_filtered = df_1[df_1['verb'] == 'Run_Test']
df_filtered.duplicated(['P_codeState'])

# %%
df.loc[41643:41653]

# %%
df_filtered = df_test_TP2[df_test_TP2['name'] == 'aurelien.bithorel.etu']

# %%
df_of_column_test.loc[100982,'name'], df_of_column_test.loc[100982,'tested_line']

# %%
df_of_column_test.loc[100999,'name'] , df_of_column_test.loc[100999,'tested_line']

# %%
df_of_column_test.loc[101016,'name'], df_of_column_test.loc[101016,'tested_line']

# %%
for index, row in df_filtered.iterrows():
    print('----------------------------------')
    print(row['name'])
    k = 0

    for i in row['indices_red_test']:
        print(f'--------{k+1} runtest------------------')
        print(df.loc[i,'filename_infere'])
        print(df_of_column_test[df_of_column_test['original_index'] == i])

# %%
print(df.loc[41643,'tests'])


# %% [markdown]
# Extract all unique tests and count the number of try for each unique test, then find :
# - if there is any failed and given up try
# - if there is any failed and solved try
#
# Before starts, check if there is any duplicated tests in all Run.Test (exactly the same)

# %% [markdown]
# ### 4.21 Create a dataframe of column 'tests'

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
# ### 4.22 Add Red or Green column for Run.Test

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
# ## Keep research data only

# %%
df['research_usage'].unique()

# %%
set(df[df['research_usage'] == '1.0']['actor']).intersection(set(df[df['research_usage'] == '0.0']['actor']))

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
# - add table in phase2, to explain better in markdown
#
# **In process:**
#
# - find the index for each run.test of students which has already a test but not empty, and find the indices which are continued (if it is hard leave it) : Done but should be analyze the correctness
#
#
# **New :**
#
# - How many students stoped doing run.test in TP-GAME 
# - check the students who didn't do the test during the TP_GAME, wht is the reason, didn't they do any test during other TP or not
#
# - add in TP_GAME and for student who didn't do the run.test, in which of P_codestate (the last one) is not empty, and if there is any name in the previous step, then check each file for them (if they had worked on all files)
#
# - check message de Mirabelle
#
# - check the get_mad_actors : these are the students who stopped the progress after not having a successful result of Run.Test
#
# - look first which students has the red tests and what they did?
#     - test red and solved the bug
#     - test red and left and went to do something else
#     - test red and didn't do anything else
#
# - check the bizzar indices ( maybe the analyze should be repeated)
#
# - remove all try and except
#
# - check the file duplicated_runTest.ipynb
#
# - add part to find all the run.Test red and see how many students did Run.Debogguer just after this test red
#
#
# ## To show : 
# - 4.14, add a diagram on Run_test rate
# - 4.19
#

# %% [markdown]
#
