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
columns = ['empty_filename', 'filename_case1', 'filename_case2']

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
# ### 4.12 Calculate how many students didn't do the run.test in each TP, TP_prog
#
# Questions: how can be understand they didn't do a Run.Test?

# %%
df_not_doing_run_test = pd.DataFrame(columns=['TP','total_number_students','total_number_students_not_run_test']) # create the df

for tp in TP_NAME:

    df_filtered = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')] # filter on TP & TP_prog

    # calculate the number total of students
    actor_column1  = df_filtered['actor']
    binome_column1 = df_filtered['binome']
    all_students1  = set(actor_column1).union(set(binome_column1))
    total_number1  = len(all_students1)
    print(total_number1)

    # filter on NOT doing Run.Test
    df_filtered_new = df_filtered[df_filtered['verb'] != 'Run.Test']
    actor_column  = df_filtered_new['actor']

    binome_column = df_filtered_new['binome']

    all_students  = set(actor_column).union(set(binome_column))
    print(len(all_students))

    # Append row to df
    df_not_doing_run_test = pd.concat([
        df_not_doing_run_test,
        pd.DataFrame({'TP': [tp], 'total_number_students' : [total_number1],'total_number_students_not_run_test' : [len(all_students)]})
    ], ignore_index=True)

df_not_doing_run_test

# %% [markdown]
# ### 4.13 Calculate the total number of session.Start and .End without including any Run.Test in TP_prog only (specially in Tp_game).

# %%
df.loc[1010:1020,'session.id']

# %%
df_indices_excluding_run_test = pd.DataFrame(columns=['TP', 'indices', 'total_num_No_Run_Test'])

 # Fill df_indices for each student in a week
for tp in TP_NAME: # it takes 4 mins maximum, it's normal because it checks for all TPs

    # extract the list of indices of each TP
    indices_to_check = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')].index.tolist()

    if indices_to_check:
        # if there is a TP_prog
        final_indices, total_num_No_Run_Test = data_testing.check_not_including_Run_Test_in_session(df,indices_to_check)

        # Fill the dataframe
        df_indices_excluding_run_test = pd.concat([
            df_indices_excluding_run_test,
            pd.DataFrame({'TP': [tp], 'indices': [final_indices], 'total_num_No_Run_Test': [len(final_indices)]})
        ], ignore_index=True)

df_indices_excluding_run_test


# %% [markdown]
# add the plotting
# add another filtrage by the name students (only actors not the binomes)

# %% [markdown]
# ### 4.14 Run.test rate per TP

# %%
# Function to calculate the percentage
def calculation(tp,df):
    
    actor1 = set(df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['actor']) # extract the actors
    binome1 = set(df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['binome']) # extract the binomes

    actor2 = set(df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['verb'] == 'Run.Test')]['actor']) # extract the actors of only Run.Test
    binome2 = set(df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['verb'] == 'Run.Test')]['binome']) # extract the binomes of only Run.Test

    all1 = actor1.union(binome1) # union on actors and binomes of TP_prog
    all2 = actor2.union(binome2) # union on actors and binomes of TP_prog and Run.Test

    print(tp)
    run_test_rate_per_tp = (len(all2) / len(all1)) * 100
    print(f"In {tp}: {run_test_rate_per_tp:.2f}% of students made the Run.Test.")

    return run_test_rate_per_tp


# %%
run_test_rate_per_tp_all = [] # list to save all percentage

for tp in TP_NAME:

    if tp != 'Tp10':
        percentage = calculation(tp,df) # calculate the percentage
        run_test_rate_per_tp_all.append(percentage) # store the result
    
    else: # it's TP10 and there is TP_prog!
        run_test_rate_per_tp_all.append(0)

# %%
# Plotting
plt.figure(figsize=(8, 5))
plt.plot(TP_NAME, run_test_rate_per_tp_all, marker='o', linestyle='-', color='skyblue')
plt.title('Percentage Values')
plt.ylabel('Percentage (%)')
plt.ylim(0, 100)  # Since you're dealing with percentages
plt.grid(True)
plt.show()

# %% [markdown]
# ### 4.15 In TP_GAME, look for each student, in the newest file of Run.Test, how many their column tests is empty and isn't

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
# ## Create a dataframe of column 'tests'

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
#
# - False : Red
# - True : Green
#
# check this function df_tests = tests_utils.construct_DataFrame_from_all_tests(run_test_copy) in script_initialisation.py in thomas version

# %%
df_of_column_test[df_of_column_test['status'] == False]

# %%
# add column color_test
df_of_column_test['color_test'] = np.where(df_of_column_test['status'] == True, 'Green', 'Red')

df_of_column_test[['color_test','status']] 

# %% [markdown]
# ### Keep research data only

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
# - semaine_5: there are two sessions, but only one sessions they were working, because the second session was controle TP and the internet was cut
# - Ignore the part of **utilisation print**
# - we want just Nom_TP_PPROGRAMMATION without the first week
# - Leave the part after the print on Etude_sur_les_testes.py
# - How write boolean for test green or red for Run.Test : DONE!
# - See cleaning.keep_research_data_only in notebooks/Init_data.py
# - try to find another way of coding of correct_filename_infere_in_subset, reduce the number of if
# - Fill the interpretations
#
# New :
# - correct the filename_inere in case 1 and two by the P_codeState, and calculate the percentage of emoing traces only for those with empty filename, which we can't find the filename by the P_codeState : Done!
#
# - add diagram to compare the number of students using each verb and the total number of present student in TP (TP_prog) : DONE!
#
# - Calculate the total number of Run.Test in the too_short_session : DONE!
#
# - Calculate how many students didn't do the run.test in each TP, TP_prog : DONE! but I'm not sure about the calculation
#
# - Calculate the total number of session.Start and .End without including any Run.Test in TP_prog only (specially in Tp_game) : DONE! but I'm not sure if the way I calculated is correct or not!
#
# - calculate the percentage of how many students in each TP, (only TP_prog) did the Run.Test from all present students : Done! 
#
# - In each TP_GAME, look for each student, in the newest file of Run.Test, how many their column tests is empty and isn't : DONE but need to check 
#
# - look Run.Test in each TP if the value in column tests is empty or not.
# if the Run.Test is clicked once and the tests is empty so there is no Run.Test
#
# - We must anonymized the too_short_sessions.csv, the column of actors
#
# - In 4.15 :add the plotting 
#
# - add in Readme how the dataframe form json is sorted by actor (alphabet) an then by session.id and then tempstamp.date, this is in cleaning.py of Thomas version
#
# - How many students stoped doing run.test in TP-GAME 
#
# - check this https://gitlab.univ-lille.fr/L1-programmation/analyse-des-traces/-/blob/amadou_analyse/notebooks/PJI_amadou_2024.py 
#
# - check the students who didn't do the test during the TP_GAME, wht is the reason, didn't they do any test during other TP or not, for these people check also if they 
#
# - add number of student who did each file.py in TP_GAME, extract the name of students
#
# - add in TP_GAME and for student who didn't do the run.test, in which of P_codestate (the last one) is not empty, and if there is any name in the previous step, then check eachf ile for them (if they had worked on all files)
#
# - add in 4.15, the student which were in 60% of doing the run.test, are they empty tests or not. you should extract their name.
