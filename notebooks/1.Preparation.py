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

# # Preparation Workflow Overview:
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
import difflib
from collections import Counter
import numpy as np
import io_utils, data_cleaning, data_anonymization
#from tests import test_preprocessing, test_anonymization
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant import SORTED_SEANCE, TP_NAME, FILES_BY_TP, FUNCTIONS_TP2 , TP2_Files


# ## Load DataFrame
# - Use functions in file **io_utils.py.py**
# - The csv file is the output of process_raw_data

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='traces250102_clean.csv')

# ### Print 5 rows and columns of dataframe

df.head()

# ## Create a copy of dataframe to compare later

df_clean = df.copy()

# ## Clean DataFrame

# ### Convert Time Format

# Before
df_clean[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# Apply
df_clean = data_cleaning.clean_time(df_clean)

# After
df_clean[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# ### Clean **Actor** Field
# Process: 
# 1. Split actor and binome into 2 columns -> **df_clean = split_actor_binome()**
# 2. Delete emails at the end -> **df_clean = delete_end_email()**
# 3. Extract all the non matching name of actor with prenom.nom.etu -> **incorrect = not_a_correct_identifier()**
# 4. Delete all rows of nebut -> **df_clean = delete_actor_lines()** 
# 5. Remove actors or binomes name -> **df_clean = delete_name_actor_binome()**
# 6. Replace joker -> **df_clean = replace_jokers()**
# 7. Cleaning manually -> **df_clean = cleaning_manual_actors_2425()**

# #### 1. Split actor and binome into 2 columns (This part delete '/')

# +
# Before 
total_slash = df_clean['actor'].str.contains('/').sum()
total_nan   = df_clean['actor'].isna().sum()
total_empty = (df_clean['actor']=='').sum()

print(f"Total number of rows : {len(df_clean)}")
print(f"Total number of rows include / : {total_slash}")
print(f"Total number of Nan rows : {total_nan}")
print(f"Total number of empty strings : {total_empty}")
# -

# Apply
df_clean = data_cleaning.split_actor_binome(df_clean)

# +
# After
total_slash_actor  = df_clean['actor'].str.contains('/').sum()
total_slash_binome = df_clean['binome'].str.contains('/').sum() # double_check

print(f"Total number of rows include / in actor: {total_slash_actor}")
print(f"Total number of rows include / in binome: {total_slash_binome}")

print("Successful!") if total_slash_actor == 0 and total_slash_binome == 0 else print("Error!") 
# -

# #### 2. Delete the email at the end

# +
# Before (check actor and binom)
total_email_actor  = df_clean['actor'].str.contains('@').sum()
total_email_binome = df_clean['binome'].str.contains('@').sum()

print(f"Total number of rows include @ in actor:   {total_email_actor}")
print(f"Total number of rows include @ in binome : {total_email_binome}")
# -

# Apply 
df_clean = data_cleaning.delete_end_email(df_clean)

# +
# After
total_email_actor = df_clean['actor'].str.contains('@').sum()

print(f"Total number of rows include @ in actor: {total_email_actor}")

print("Successful!") if total_email_actor == 0 else print("Error!") 
# -

# #### 3. Extract all the non matching name of actor with prenom.nom.etu

# +
incorrect_actor  = data_cleaning.not_a_correct_identifier(df_clean,'actor')
incorrect_binome = data_cleaning.not_a_correct_identifier(df_clean,'binome')

incorrect_actor, incorrect_binome
# -

# #### 4. Delete all rows of nebut

# Before
total = (df_clean['actor'] == 'nebut').sum()
print(f"total occurance of nebut : {total}") 

# Apply
df_clean = data_cleaning.delete_actor_lines(df_clean, "nebut")

# After
total = (df_clean['actor'] == 'nebut').sum()
print(f"total occurance of nebut : {total}") 
print("Successful!") if total == 0 else print("Error!") 

# #### 5. Remove actors or binomes name ( just replace them by '' in binome column)

# Before in binome
total = (df_clean['binome'] == 'luc').sum()
print(f"total occurance : {total} ")

# Apply
df_clean = data_cleaning.delete_name_actor_binome(df_clean, 'binome', 'luc')

# After 
total = (df_clean['binome'] == 'luc').sum()
print(f"Total occurance of : {total}")
print("Successful!") if total == 0 else print("Error!") 

# #### 6. Replace joker

# Add the number total of matching marie is equal to the total occurance of two jokers

# +
# Before
total_joker1 = (df_clean['binome'] == 'MI1304').sum()
total_joker2 = (df_clean['binome'] == 'MI1301').sum()

total = total_joker1 + total_joker2

print(f"Total occurance of joker 1 : {total_joker1}")
print(f"Total occurance of joker 2 : {total_joker2}")
# -

# Apply
jokers_real_name = {
    'MI1304': 'mariama-sere.sylla.etu',
    'MI1301': 'mariama-sere.sylla.etu'
}
df_clean = data_cleaning.replace_jokers(df_clean, ['actor','binome'],jokers_real_name)

# +
# After
total_joker1 = (df_clean['binome'] == 'MI1304').sum()
total_joker2 = (df_clean['binome'] == 'MI1301').sum()
total_new_name = (df_clean['binome'] == 'mariama-sere.sylla.etu').sum()

print(f"Total occurance of joker 1 : {total_joker1}")
print(f"Total occurance of joker 2 : {total_joker2}")

print("Successful!") if total_joker1 == 0 and total_joker1 == 0 and total_new_name == total else print("Error!") 
# -


# #### 7. Cleaning manually

# +
# Before
total = (df_clean['actor'] == 'anis.younes.etu').sum()

print(f"Total occurance : {total}")
# -

# Apply
df_clean = data_cleaning.cleaning_manual_actors_2425(df_clean, 'anis.younes.etu')

# +
# After
total = (df_clean['actor'] == 'anis.younes.etu').sum()
print(f"Total occurance : {total}")

print("Successful!") if total == 0 else print("Error!") 
# -

# #### Retry Test for invalid actor or binome

# +
incorrect_actor  = data_cleaning.not_a_correct_identifier(df_clean,'actor')
incorrect_binome = data_cleaning.not_a_correct_identifier(df_clean,'binome')

print(len(incorrect_actor),len(incorrect_binome))

print("Cleaning actor successful!") if len(incorrect_actor) == 0 and len(incorrect_binome) == 0 else print("Error!") 
# -

# #### Save new dataframe

io_utils.write_csv(df_clean,INTERIM_DATA_DIR)

# ### Read clean dataframe

df_clean = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='acteur_nettoyage_2425.csv')

df_clean[['actor','binome']].head(10)

# ### Clean **Filename** Field
# Process:
#
# 1. First part : Fill 'filename_infere'
#
#     1.1 Fill filename_infere using filename values
#
#     1.2 Check empty filename_infere of **Run.Test**
#
#     1.3 Check empty filename_infere of **Run.Program**
#
#         1.3.1 Fill empty filename_infere of **Run.Program** by **commandRan**
#
#         1.3.2 Fill empty filename_infere of **Run.Program** by **P_codestate**
#
#     1.4 Check empty filename_infere of **Run.Debugger**
#
#         1.4.1 Fill empty filename_infere of **Run.Debugger** by commandRan
#
#     1.5 Check empty filename_infere of **Run.Command**
#
#     1.6 Check empty filename_infere of **File.Open**
#
#     1.7 Check empty filename_infere of **File.Save**
#
#     1.8 Check empty filename_infere of **Docstring.Generate** 
#
# 2. Second part : Validate 'filename_infere' values for each week
#
#     2.1 DF[seance] == semaine_2
#
#     2.2 DF[seance] == semaine_3
#
#     2.3 DF[seance] == semaine_4
#
#     2.4 DF[seance] == semaine_5
#
#     2.5 DF[seance] == semaine_6
#
#     2.6 DF[seance] == semaine_7
#
#     2.7 DF[seance] == semaine_8
#
#     2.8 DF[seance] == semaine_9
#
#     2.9 DF[seance] == semaine_10
#
#     2.10 DF[seance] == semaine_GAME
#
# 4. Add Column 'TP'
# 5. Add Column 'Type_TP'
#

# #### 1. First part : Fill 'filename_infere'

# create new column next to the filename
col_index = df_clean.columns.get_loc('filename')
df_clean.insert(col_index + 1, 'filename_infere', '') 
df_clean.columns

# #### 1.1 Fill filename_infere by filename values

# +
# Before
total_empty_filename_infere = (df_clean['filename_infere']=='').sum()
print(f"Total number of empty strings in filename_infere : {total_empty_filename_infere}")

# Apply
df_clean['filename_infere'] = data_cleaning.extract_short_filename(df_clean['filename'])

# After
total_empty_filename_infere = (df_clean['filename_infere']=='').sum()
print(f"Total number of empty strings in filename_infere : {total_empty_filename_infere}")
# -

df_clean[['filename','filename_infere']].head(10)

# Some filenames have already the name, we can fill filename_infere by them, which we filled some of them, reduced from 306914 to 151183

# #### 1.2 Check empty filename_infere of **Run.Test**

# +
# Before
total_Run_Test       = len(df_clean[df_clean['verb']  == 'Run.Test'])
total_Run_Test_empty = (df_clean[df_clean['verb'] =='Run.Test']['filename'] == '').sum()
total_Run_Test_nan   = df_clean[df_clean['verb'] =='Run.Test']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Test : {total_Run_Test}")
print(f"Total number of empty strings in filename_infere in Run.Test : {total_Run_Test_empty}")
print(f"Total number of None in filename_infere in Run.Test : {total_Run_Test_nan}")
# -

# **Interpretation** There is no empty or none values for Run.Test, but we need to check the correctness of their name which we do later.

# ####  1.3 Check empty filename_infere of **Run.Program**

# +
# Before
total_Run_Program       = len(df_clean[df_clean['verb']  == 'Run.Program'])
total_Run_Program_empty = (df_clean[df_clean['verb'] =='Run.Program']['filename_infere'] == '').sum()
total_Run_Program_nan   = df_clean[df_clean['verb'] =='Run.Program']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Program : {total_Run_Program}")
print(f"Total number of empty strings in filename_infere in Run.Program : {total_Run_Program_empty}")
print(f"Total number of None in filename_infere in Run.Program : {total_Run_Program_nan}")
# -

# **Interpretation** All rows of Run.Program is empty so we first look at column **P_codeState** since the filename between trace is correct and then if there is still any empty string, we look at **commandRan** which might not be a correct name but we don't care in this part.

# ##### 1.3.1 Fill empty filename_infere of **Run.Program** by P_codestate

# +
# check if all values in P_codeState have <trace></trace>
total_non_empty_codestate     = (df_clean[df_clean['verb']  == 'Run.Program']['P_codeState'] != '').sum()
total_codestate_contain_trace = df_clean[df_clean['verb']  == 'Run.Program']['P_codeState'].str.contains(r'<trace>.*\.py</trace>', regex=True, na=False).sum()

print(f"Total rows of not empty strings in P_codeState for Run.Program : {total_non_empty_codestate}")
print(f"Total rows of P_codeState contian <trace> : {total_codestate_contain_trace}")
# -

# Apply
mask = (df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] == '')
df_clean.loc[mask, 'filename_infere'] = df_clean.loc[mask, 'P_codeState'].map(data_cleaning.extract_short_filename_from_P_codestate_Run_Program)

# After
total_Run_Program_empty = (df_clean[df_clean['verb'] =='Run.Program']['filename_infere'] == '').sum()
print(f"Total rows of empty strings in Run.Program : {total_Run_Program_empty}")

# ##### 1.3.2 Fill empty filename_infere of **Run.Program** by commandRan

# +
# check if all values in commandRan starts with %Run
total_non_empty_commandRan = len(df_clean[(df_clean['verb'] == 'Run.Program') & (df_clean['commandRan'] != '')])
total_commandRan_start_Run = len(df_clean[df_clean['verb'] == 'Run.Program']['commandRan'].str.startswith('%Run'))

print(f"Total rows of not empty strings in commandRan for Run.Program : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Run in Run.Program : {total_commandRan_start_Run}")
# -

# **Interpretation** : Even though all values start wtih %Run, there are values contain %Run Editor which means there is not value for filename. 

# Apply
mask = (df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] == '')
df_clean.loc[mask, 'filename_infere'] = data_cleaning.extract_short_filename_from_commandRan_Run_Program(df_clean.loc[mask, 'commandRan'])

# +
# After
total_Run_Program_empty = (df_clean[df_clean['verb']=='Run.Program']['filename_infere'] == '').sum()

print(f"Total rows of empty strings in Run.Program : {total_Run_Program_empty}")
# -

# **Interpretation** : we reduced empty filename_infere from 54352 to 5658 by **P_codeState** and **commandRan**. For the correctness and the other empty values we look in the second part.

df_clean[(df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] != '')][['filename_infere','commandRan','P_codeState']]

# #### 1.4 Check empty filename_infere of **Run.Debugger**

# +
# Before
total_Run_Debugger       = len(df_clean[df_clean['verb']  == 'Run.Debugger'])
total_Run_Debugger_empty = (df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'] == '').sum()
total_Run_Debugger_nan   = df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Debugger : {total_Run_Debugger}")
print(f"Total number of empty strings in filename_infere in Run.Debugger : {total_Run_Debugger_empty}")
print(f"Total number of None in filename_infere in Run.Debugger : {total_Run_Debugger_nan}")
# -

# Same as Run.Program we will do the same process

# ##### 1.4.1 Fill empty filename_infere of **Run.Debugger** by commandRan

# +
# check if all values in commandRan starts with %Debug
total_non_empty_commandRan       = len(df_clean[(df_clean['verb'] == 'Run.Debugger') & (df_clean['commandRan'] != '')])
total_commandRan_start_Debug     = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Debug').sum()
total_commandRan_start_NiceDebug = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Nice').sum()
total_commandRan_start_FastDebug = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Fast').sum()

print(f"Total rows of not empty strings in commandRan for Run.Debugger  : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Debug in Run.Debugger     : {total_commandRan_start_Debug}")
print(f"Total rows of commandRan starts with %NiceDebug in Run.Debugger : {total_commandRan_start_NiceDebug}")
print(f"Total rows of commandRan starts with %FastDebug in Run.Debugger : {total_commandRan_start_FastDebug}")
# -

# **Interpretation** All values in commandRan starts with %Debug, we can extract filename from commandRan.

# Apply
mask = df_clean['verb'] == 'Run.Debugger'
df_clean.loc[mask, 'filename_infere'] = data_cleaning.extract_short_filename_from_commandRan_Run_Debugger(df_clean.loc[mask, 'commandRan'])

# After
total_Run_Debugger_empty = (df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'] == '').sum()
print(f"Total number of empty strings in filename_infere in Run.Debugger : {total_Run_Debugger_empty}")

df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'].head(10)

# #### 1.5 Check empty filename_infere of **Run.Command**

# +
# Before
total_Run_command       = len(df_clean[df_clean['verb']  == 'Run.Command'])
total_Run_command_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_nan   = df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.command : {total_Run_command}")
print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of None in filename_infere in Run.command : {total_Run_command_nan}")

# +
# check if all values in commandRan starts with %NiceDebug or %FastDebug
total_non_empty_commandRan       = len(df_clean[(df_clean['verb'] == 'Run.Command') & (df_clean['commandRan'] != '')])
total_commandRan_start_Debug     = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%Debug').sum()
total_commandRan_start_NiceDebug = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%NiceDebug').sum()
total_commandRan_start_FastDebug = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%FastDebug').sum()

print(f"Total rows of not empty strings in commandRan for Run.Command  : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Debug in Run.Command     : {total_commandRan_start_Debug}")
print(f"Total rows of commandRan starts with %NiceDebug in Run.Command : {total_commandRan_start_NiceDebug}")
print(f"Total rows of commandRan starts with %FastDebug in Run.Command : {total_commandRan_start_FastDebug}")
# -

# **Interpretation** Only 70 values starts wtih %FastDebug, so we can fill only 70 values of filename_infere

# +
# Apply 
mask = df_clean['verb'] == 'Run.Command'

# Get only cleaned values for those starting with %FastDebug
cleaned_values = data_cleaning.extract_short_filename_from_commandRan_Run_Command(df_clean.loc[mask, 'commandRan'])

df_clean.loc[cleaned_values.index, 'filename_infere'] = cleaned_values

# +
# After
total_Run_command_empty     = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_not_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] != '').sum()

print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of NOT empty strings in filename_infere in Run.command : {total_Run_command_not_empty}")
# -

len(df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].unique())

# +
total_PcodeState_empty = (df_clean[df_clean['verb'] == 'Run.Command']['P_codeState'] == "").sum()
total_FcodeState_empty = (df_clean[df_clean['verb'] == 'Run.Command']['F_codeState'] == "").sum()

print(f"Total number of empty strings in P_codeState in Run.command : {total_PcodeState_empty}")
print(f"Total number of empty strings in F_codeState in Run.command : {total_FcodeState_empty}")
# -

# **Interpretation**
#
# There are 22461 different values in commandRan for Run.command, we can't use or analyze each single value, and since all values for Run.Command in P_codeState or F_codeState are empty we analyze them in the part of analyze each TP alone.

# #### 1.6 Check empty filename_infere of **File.Open**

# +
# Before
total_File_Open       = len(df_clean[df_clean['verb']  == 'File.Open'])
total_File_Open_empty = (df_clean[df_clean['verb'] == 'File.Open']['filename_infere'] == '').sum()
total_File_Open_nan   = df_clean[df_clean['verb'] == 'File.Open']['filename_infere'].isna().sum()

print(f"Total number of traces in File.Open : {total_File_Open}")
print(f"Total number of empty strings in filename_infere in File.Open : {total_File_Open_empty}")
print(f"Total number of None in filename_infere in File.Open : {total_File_Open_nan}")
# -

# #### 1.7 Check empty filename_infere of **File.Save**

# +
total_File_Save       = len(df_clean[df_clean['verb']  == 'File.Save'])
total_File_Save_empty = (df_clean[df_clean['verb'] == 'File.Save']['filename_infere'] == '').sum()
total_File_Save_nan   = df_clean[df_clean['verb'] == 'File.Save']['filename_infere'].isna().sum()

print(f"Total number of traces in File.Save : {total_File_Save}")
print(f"Total number of empty strings in filename_infere in File.Save : {total_File_Save_empty}")
print(f"Total number of None in filename_infere in File.Save : {total_File_Save_nan}")
# -

# #### 1.8 Check empty filename_infere of **Docstring.Generate**

# +
total_Docstring       = len(df_clean[df_clean['verb']  == 'Docstring.Generate'])
total_Docstring_empty = (df_clean[df_clean['verb'] == 'Docstring.Generate']['filename_infere'] == '').sum()
total_Docstring_nan   = df_clean[df_clean['verb'] == 'Docstring.Generate']['filename_infere'].isna().sum()

print(f"Total number of traces in Docstring.Generate : {total_Docstring}")
print(f"Total number of empty strings in filename_infere in Docstring.Generate : {total_Docstring_empty}")
print(f"Total number of None in filename_infere in Docstring.Generate : {total_Docstring_nan}")
# -

df_clean[df_clean['verb'] == 'Docstring.Generate']['function']

# Question: don't know how should I fill it.

# ### Save new clean dataframe

io_utils.write_csv(df_clean,INTERIM_DATA_DIR)

# ### Read clean dataframe

df_clean = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase1_nettoyage_fichiere.csv')

# #### 2. Second part : Validate 'filename_infere' values for each week

# #### 2.1 **DF[seance] == semaine_2**

df_clean

# +

FUNCTIONS_TP2_Prog = [
    "repetition",
    "moyenne_entiere",
    "moyenne_entiere_ponderee",
    "heure2minute",
    "jour2heure",
    "en_minutes",
    "message",
    "bonbons_par_enfant"
]

FUNCTIONS_TP2_Manip = [
    "imperial2metrique",
    "poly1",
    "poly2"
]

# TP3
FUNCTIONS_TP3_Prog = [
    "est_non_vide\(",
    "est_reponse\(",
    "est_beneficiaire\(",
    "est_reponse_correcte\(",
    "est_en_ete\(",
    "est_nombre_mystere\(",
    "ont_intersection_vide\(",
    "intervalle1_contient_intervalle2\(",
    "sont_intervalles_recouvrants\(",
    "est_gagnant\(",
    "est_strict_anterieure_a\(",
    "est_mineur_a_date\(",
    "est_senior_a_date\(",
    "a_tarif_reduit_a_date\(",
]

FUNCTIONS_TP3_Manip = [
    "fonction2\(",
    "fonction3\(",
    "fonction4\(",
    "fonction5\(",
    "fonction1\(",
    "pred1\(",
    "pred2\(",
    "pred3\(",
    "pred4\(",
    "pred5\(",
    "pred9\("
]

# TP4 
FUNCTIONS_TP4_Prog = [
    "numero_jour\(",
    "nom_jour\(",
    "est_date_valide\(",
    "est_jour_valide\(",
    "nombre_jours\(",
    "est_mois_valide\(",
    "calcul_gain\(",
    "montant_facture\(",
    "nombre_exemplaires\(",
    "conseil_voiture\(",
    "argminimum\(",
    "cout_location\(",
    "minimum3\(",
    "compare\(",
    "maximum\(", 
    "est_bissextile\("
]

FUNCTIONS_TP4_Manip = [
    "categorie_tir_arc_v1\(",
    "categorie_tir_arc_v2\(",
    "categorie_tir_arc_v3\(",
    "categorie_tir_arc_v4\(",
    "mon_abs\(",
    "signe1\(",
    "signe2\(",
    "en_tete1\(",
    "int2str\(",
    "pile_ou_face1\(",
    "pile_ou_face2\("
    
]

all_TP_functions_name = {
    'note_UE.py' : '# TP PROG semaine 1' , 'pour_debogueur.py' : '# TP PROG semaine 1' , 'calcul_interets.py' : '# TP PROG semaine 1' , # TP1
    'fonctions.py': FUNCTIONS_TP2_Prog, 'mesure.py': FUNCTIONS_TP2_Manip[0], 'polynomes.py': [FUNCTIONS_TP2_Manip[1],FUNCTIONS_TP2_Manip[2]], # TP2
    'booleens.py' : FUNCTIONS_TP3_Prog, 'erreurs_multiples.py': FUNCTIONS_TP3_Manip[:4], 'manipulations.py' : FUNCTIONS_TP3_Manip[4:], # TP3
    'conditionnelles.py' : FUNCTIONS_TP4_Prog, 'categories.py' : FUNCTIONS_TP4_Manip[:4] , 'erreurs_cond.py' : FUNCTIONS_TP4_Manip[4:] # TP4
    
    }

# +
# Before
pattern_TP1 = '|'.join(FILES_BY_TP[0])
pattern_TP2 = '|'.join(FILES_BY_TP[1])
pattern_TP3 = '|'.join(FILES_BY_TP[2])
pattern_TP4 = '|'.join(FILES_BY_TP[3])
pattern_TP5 = '|'.join(FILES_BY_TP[4])
pattern_TP6 = '|'.join(FILES_BY_TP[5])
pattern_TP7 = '|'.join(FILES_BY_TP[6])
pattern_TP8 = '|'.join(FILES_BY_TP[7])
pattern_TP9 = '|'.join(FILES_BY_TP[8])
pattern_TP10 = '|'.join(FILES_BY_TP[9])
pattern_TPGAME = '|'.join(FILES_BY_TP[10])

pattern     = pattern_TP1 + '|' + pattern_TP2 + '|' + pattern_TP3 + '|' + pattern_TP4 + '|' + pattern_TP5 + '|' + pattern_TP6 + '|' + pattern_TP7 + '|' + pattern_TP8 + '|' + pattern_TP9 + '|' + pattern_TPGAME

total_semaine_2                  = (df_clean['seance'] == 'semaine_2').sum()
total_empty_string_semaine_2     = (df_clean[df_clean['seance'] == 'semaine_2']['filename_infere'] == '').sum()
total_nan_semaine_2              = df_clean[df_clean['seance'] == 'semaine_2']['filename_infere'].isna().sum()

subset = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] != '')]

total_correct_name_semaine_2     = subset['filename_infere'].str.contains(pattern, na = False).sum()
total_NOT_correct_name_semaine_2 = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()

print(f"Total number of rows in semaine_2 : {total_semaine_2}")
print(f"Total number of empty string : {total_empty_string_semaine_2}")
print(f"Total number of Nan : {total_nan_semaine_2}")
print(f"Total number of correct name : {total_correct_name_semaine_2}")
print(f"Total number of NOT correct name : {total_NOT_correct_name_semaine_2}")
# -

# ##### 2.1.1 Find index of session.Start and session.End

# +
# Find actors of semaine_2
list_students_semaine_2 = df_clean[df_clean['seance'] == 'semaine_2']['actor'].unique().tolist()
list_students_semaine_2

# Extract indices for each student (actor)
df_indices = pd.DataFrame(columns=['name_students', 'indices'])

for student in list_students_semaine_2: # it takes 12 second maximum, it's normal
    indices = data_cleaning.cut_df(df_clean,'semaine_2',student)

    df_indices = pd.concat([
        df_indices,
        pd.DataFrame({'name_students': [student], 'indices': [indices]})
    ], ignore_index=True)
# -

# ##### 2.1.2 Remove indices with length less than two

# +
# Before
df_indices['num_2_traces'] = df_indices['indices'].apply(lambda lst: len([pair for pair in lst if abs(pair[1] - pair[0]) <= 2]))
total = (df_indices['num_2_traces'] != 0).sum()

print(f"total_number_of_students_with_small_activity : {total}")
# -

# Apply : remove any paire that there is only 1 or 2 verb
df_indices['indices'] = df_indices['indices'].apply(lambda lst: [pair for pair in lst if abs(pair[1] - pair[0]) > 2])

# +
# After
df_indices['num_2_traces'] = df_indices['indices'].apply(lambda lst: len([pair for pair in lst if abs(pair[1] - pair[0]) <= 2]))
total = (df_indices['num_2_traces'] != 0).sum()

print(f"total_number_of_students_with_small_activity : {total}")

# +
# check
total_number_emptystring_FO = ((df_clean['verb'] == 'File.Open') & (df_clean['filename_infere'] == '')).sum()
total_number_emptystring_FS = ((df_clean['verb'] == 'File.Save') & (df_clean['filename_infere'] == '')).sum()
total_number_emptystring_RT = ((df_clean['verb'] == 'Run.Test') & (df_clean['filename_infere'] == '')).sum()
total_number_emptystring_RD = ((df_clean['verb'] == 'Run.Debugger') & (df_clean['filename_infere'] == '')).sum()
total_number_emptystring_RP = ((df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] == '')).sum()
total_number_emptystring_RC = ((df_clean['verb'] == 'Run.Command') & (df_clean['filename_infere'] == '')).sum()

print(f"Total number of emptystring for File.Open : {total_number_emptystring_FO}")
print(f"Total number of emptystring for File.Save : {total_number_emptystring_FS}")
print(f"Total number of emptystring for Run.Test : {total_number_emptystring_RT}")
print(f"Total number of emptystring for Run.Debugger : {total_number_emptystring_RD}")
print(f"Total number of emptystring for Run.Program : {total_number_emptystring_RP}")
print(f"Total number of emptystring for Run.Command : {total_number_emptystring_RC}")


# -

# Since there is no empty string of filename_infere for File.Open, File.Save, Run.Test and Run.Debugger we don't need them to check in the condition where filename_infere is empty, we only need to just check them in the condtion where there is already a name of filenamei_infere and we need to juts check if it's correct or not. But for the ithers we should check in both condition where there is a filename_infere and where there is not.

# data_cleaning
def find_filename_by_function_name(TP_files,codestate):

    for item in TP_files.items():
    
        if len(item[1]) > 1:
            pattern = '|'.join(item[1])

        else: 
            pattern = item[1][0]

        match = re.search(pattern, codestate)

        if match: 
            filename_infere = item[0]
            return filename_infere
            
    return '' # no match found!


# data_cleaning
def find_similarity(TP_Files,filename_infere):

    for item in TP_Files.items():
        correct_name = item[0]
        similarity = difflib.SequenceMatcher(None, correct_name, filename_infere).ratio()

        if similarity > 0.6:
            return correct_name
        
    return '' # Wasn't similar!


# data_cleaning
def find_filename_by_codestate(pattern, codestate):

    match_state = re.search(pattern, codestate)

    if match_state: # if the name is in the P_codeState
        matched_filename = match_state.group()  # Extract the name
        return matched_filename

    else: # if the exact name is not in P_codeState and student might removed the name part, we check the match with the content
        filename_infere = find_filename_by_function_name(all_TP_functions_name,codestate)
        return filename_infere


# # change TP2_Files to all functions name and TP names

# data_cleaning
# check in each activity between session.Start and session.End
def correct_filename_infere_in_subset(subset,df):

    for index in subset.index:
        row = df.loc[index]

        filename_infere = row['filename_infere']
        x = False
        if filename_infere == 'DEVOIR PROGRAMMATION.py': 
            print(index)
            print(filename_infere)
            x = True
        
        # check the emptyness (only for Run.Command and Run.Program we ignore Docstring or session.start or session.end)
        if filename_infere == '':
            
            if row['verb'] in ['Run.Command', 'Run.Program']:

                if row['P_codeState'] != '': # P_codeState has a content
                    filename_infere = find_filename_by_codestate(pattern,row['P_codeState'])
            
        # filename_infere non vide
        else:
            match = re.search(pattern, filename_infere)
            
            if not match: # it is not correct
                if row['verb'] in ['File.Open', 'File.Save']:

                    if row['F_codeState'] != '': # F_codeState has a content
                        filename_infere = find_filename_by_codestate(pattern,row['F_codeState'])
                   
                    else: # F_codestate is empty
                        filename_infere = find_similarity(all_TP_functions_name,filename_infere)

                elif row['verb'] in ['Run.Test', 'Run.Command', 'Run.Program', 'Run.Debugger']:

                    if row['P_codeState'] != '': # P_codeState has a content
                        filename_infere = find_filename_by_codestate(pattern,row['P_codeState'])

                    else: # filename and P_codeState are empty
                        filename_infere = find_similarity(all_TP_functions_name,filename_infere)
                       
        # change filename_infere of df with the correct name
        if x == True:
            print(filename_infere)

       #if index == 280600:
        #    print('here')
        
        df.at[index, 'filename_infere'] = filename_infere 


# ##### 2.1.3 Checking the correctness in each session

# +
for index, row in df_indices.iterrows():

    for activity in row['indices']:
        start = activity[0]
        end   = activity[1]
        
        subset_df = df_clean.iloc[start:end]

        try:
            correct_filename_infere_in_subset(subset_df,df_clean)
        
        except Exception as errors:
            name = row['name_students']
            print(f'Student: {name}')
            print(f'Activity in {start} : {end}')
            print(errors)
            break

print('successful!!')     

# +
# After
total_semaine_2               = (df_clean['seance'] == 'semaine_2').sum()
total_empty_string_semaine_2  = (df_clean[df_clean['seance'] == 'semaine_2']['filename_infere'] == '').sum()
total_nan_semaine_2           = df_clean[df_clean['seance'] == 'semaine_2']['filename_infere'].isna().sum()

subset = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] != '')]

total_correct_name_semaine_2     = subset['filename_infere'].str.contains(pattern, na = False).sum()
total_NOT_correct_name_semaine_2 = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()

print(f"Total number of rows in semaine_2 : {total_semaine_2}")
print(f"Total number of empty string : {total_empty_string_semaine_2}")
print(f"Total number of Nan : {total_nan_semaine_2}")
print(f"Total number of correct name : {total_correct_name_semaine_2}")
print(f"Total number of NOT correct name : {total_NOT_correct_name_semaine_2}")
# -

# ##### 2.1.4 Exceptions : Not correct name

df_clean.loc[280628:280631, ['verb', 'filename_infere','actor','binome','seance']]


# The 39 values which aren't correct, are the rows with only 2 traces like example above, so we need to remove them, that's why they didn't change even though their name can get correct in function correct_filename_infere_in_subset.

# +
subset = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] != '')]
incorrect_names       = subset[~ subset['filename_infere'].str.contains(pattern, na = False)]
incorrect_names_index = incorrect_names.index

for i in incorrect_names_index:
    
    if len(df_clean.loc[i - 1 :i + 1]) == 3: # there is only one trace between session.start and session.end

        print(f"Delete index : {i}")
        df_clean.drop(i, inplace=True)

subset = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] != '')]
total_NOT_correct_name_semaine_2 = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()
print(f"Total number of NOT correct name : {total_NOT_correct_name_semaine_2}")

# -

# ##### 2.1.5 Check Session.Start and Session.End and Docstring as the empty string

# +
subset_other_verb = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] == '')]

number_empty_string = ((subset_other_verb['verb'] == 'Session.Start' ) | (subset_other_verb['verb'] == 'Docstring.Generate' ) | (subset_other_verb['verb'] == 'Session.End')).sum()

print(f"Total number of empty strings in filename_infere : {number_empty_string}")
# -

# Interpretation : From 10726 empty string in semaine_2, there are 3133 trace with verbs : 'Session.Start', 'Session.End', 'Docstring.Generate' which we don't care! but for the rest we should find another way

# ##### 2.1.6 Exceptions : Empty strings

subset_empty_strings = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] == '') & (df_clean['verb'] != 'Docstring.Generate')]
subset_empty_strings[['verb','P_codeState', 'F_codeState', 'filename_infere']]


# function sandwich:
# - only for filename_infere that are empty (they didn't have any P_codeState or F_codeState)
# - take the first filename_infere appear in a session, (it is correct since we are already check there is no more incorrect name)
# - if the filename_infere is not empty keep it as the last_filename_infere
#     - then check the next filename_infere, if it is empty contiue until you get the filename_infere which in not empty
#         - you check the new filename_infere, Is it the same as last_filenanme_infere, if so for all the filename_infere empty between these tow name, you put the same name
#         - if the filename_infere is not same as the previous, and there are empty filename_infere between these two, you pick the last filename_infere for all the filename_infere empty which were before this one, and then you change the last_filename_infere with the new filename_infere which is not empty.
# - if new filename_infere is not empty, then change the value of last filename_infere by this name
#
# when function above is finished, check how many filename_infere you have still, which means these filename_infere all of them are empty in a session, check if they are like this, then put the name TP_manip for all of them
#
# by these two function I don't think so there will be any other empty filename_infere

# +
# data.cleaning

def sandwich(filename_infere_list):
    
    filtered_list = [value for value in filename_infere_list if value != '']

    # Count frequency of each string
    counter = Counter(filtered_list)

    # Get the most common string
    if len(counter) != 0: # if there is any name
    
        most_common_string, count = counter.most_common(1)[0]
        return most_common_string
    
    else:
        return ''


# +
# Extract indices for each student (actor)
df_indices = pd.DataFrame(columns=['name_students', 'indices'])

for student in list_students_semaine_2: # it takes 12 second maximum, it's normal
    indices = data_cleaning.cut_df(subset_empty_strings,'semaine_2',student)

    df_indices = pd.concat([
        df_indices,
        pd.DataFrame({'name_students': [student], 'indices': [indices]})
    ], ignore_index=True)

# -

df_indices['indices'] = df_indices['indices'].apply(lambda lst: [pair for pair in lst if abs(pair[1] - pair[0]) > 2])

for index, row in df_indices.iterrows():
    
    for i in row['indices']:
        start = i[0]
        end = i[1]
        
        subset_new = df_clean.iloc[start:end]
        
        if (subset_new['filename_infere'] == '').sum() != 0:
            
            most_common_filename_infere = sandwich
            
            (filename_infere_list)

            # Get the index positions for the range
            subset_indices = df_clean.iloc[start:end].index
            excluded_verbs = ['Docstring.Generate', 'session.Start', 'session.End']

            # Update only rows with empty string in 'filename_infere'
            mask = (df_clean.loc[subset_indices, 'filename_infere'] == '') & ~df_clean.loc[subset_indices, 'verb'].isin(excluded_verbs)

            df_clean.loc[subset_indices[mask], 'filename_infere'] = most_common_filename_infere


# +
# After
total_semaine_2               = (df_clean['seance'] == 'semaine_2').sum()
total_empty_string_semaine_2  = (df_clean[df_clean['seance'] == 'semaine_2']['filename_infere'] == '').sum()
total_nan_semaine_2           = df_clean[df_clean['seance'] == 'semaine_2']['filename_infere'].isna().sum()

subset = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] != '')]

total_correct_name_semaine_2     = subset['filename_infere'].str.contains(pattern, na = False).sum()
total_NOT_correct_name_semaine_2 = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()

print(f"Total number of rows in semaine_2 : {total_semaine_2}")
print(f"Total number of empty string : {total_empty_string_semaine_2}")
print(f"Total number of Nan : {total_nan_semaine_2}")
print(f"Total number of correct name : {total_correct_name_semaine_2}")
print(f"Total number of NOT correct name : {total_NOT_correct_name_semaine_2}")
# -

x = subset[~ subset['filename_infere'].str.contains(pattern, na = False)]
x

codestate = df_clean.iloc[280629]['F_codeState']
find_filename_by_codestate(pattern,codestate)


pattern

# +
x = subset[~ subset['filename_infere'].str.contains(pattern, na = False)]

correct_filename_infere_in_subset(x,df_clean)
# -


# ##### 2.1.6 Exceptions : Not correct name

# +
# Before
subset = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] != '')]
subset_df = subset[~ subset['filename_infere'].str.contains(pattern, na = False)]

total_not_correct = len(subset_df)
print(f"Total number of invalid names : {total_not_correct}")
# -

# Apply
try:
    correct_filename_infere_in_subset(subset_df,df_clean)
except Exception as errors:
    print(errors) 

# +
subset = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] != '')]
subset_df = subset[~ subset['filename_infere'].str.contains(pattern, na = False)]

print('successful!') if len(subset_df) == 0 else print('Error!')

# +
# After
total_semaine_2               = (df_clean['seance'] == 'semaine_2').sum()
total_empty_string_semaine_2  = (df_clean[df_clean['seance'] == 'semaine_2']['filename_infere'] == '').sum()
total_empty_string_semaine_2_valid_verb  = ((df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] == '') & (df_clean['verb'] != 'Session.Start') & (df_clean['verb'] != 'Session.End') & (df_clean['verb'] != 'Docstring.Generate')).sum()
total_nan_semaine_2           = df_clean[df_clean['seance'] == 'semaine_2']['filename_infere'].isna().sum()

subset = df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] != '')]

total_correct_name_semaine_2     = subset['filename_infere'].str.contains(pattern, na = False).sum()
total_NOT_correct_name_semaine_2 = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()

print(f"Total number of rows in semaine_2 : {total_semaine_2}")
print(f"Total number of empty string : {total_empty_string_semaine_2}")
print(f"Total number of empty string for valid verb : {total_empty_string_semaine_2_valid_verb}")
print(f"Total number of Nan : {total_nan_semaine_2}")
print(f"Total number of correct name : {total_correct_name_semaine_2}")
print(f"Total number of NOT correct name : {total_NOT_correct_name_semaine_2}")
# -

# Interpretation : 

# #### 2.2 **DF[seance] == semaine_3**

# #### 2.3 **DF[seance] == semaine_4**

# #### 2.4 **DF[seance] == semaine_5**

# #### 2.5 **DF[seance] == semaine_6**

# #### 2.6 **DF[seance] == semaine_7**

# #### 2.7 **DF[seance] == semaine_8**

# #### 2.8 **DF[seance] == semaine_9**

# #### 2.9 **DF[seance] == semaine_10**

# #### 2.10 **DF[seance] == semaine_GAME**

# #### 3. Add column TP

# Add column TP
# create new column next to the filename
col_index = df_clean.columns.get_loc('seance')
df_clean.insert(col_index + 1, 'TP', '') 
df_clean.columns

df_clean[df_clean['seance'] == 'semaine_2'][['filename_infere', 'TP']]

df_clean[(df_clean['seance'] == 'semaine_2') & (df_clean['filename_infere'] == 'pour_debogueur.py')][['filename_infere', 'TP']]

# +
# creat new list of TP with the same size as SORTED_SEANCE to use map
TP_name = {'TP1' : FILES_BY_TP[0], 'TP2' : FILES_BY_TP[1], 'TP3' : FILES_BY_TP[2], 'TP4' : FILES_BY_TP[3]}

file_to_tp = {}
for tp, files in TP_name.items():
    for f in files:
        file_to_tp[f] = tp

df_clean["TP"] = df_clean["filename_infere"].map(file_to_tp)
# -

# ##### 3.2 TP3

# ##### 3.3 TP4

# ##### 3.4 TP5

# #### 4. Add column TP_Type

# Add column TP
# create new column next to the filename
col_index = df_clean.columns.get_loc('TP')
df_clean.insert(col_index + 1, 'Type_TP', '') 
df_clean.columns

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
# - First look at the functions name from the variable_constatnt.py and check if they exist in the P_codeState or commandRan
#
# - Second add column TP next to the column semaine (TP1, TP2, TP3 ...) Change
# - Third add column next to TP column 'Type_TP' with two values : 1-TP_programmation 2-TP_manipulation (activite_range.py is manipulation)
# - Forth add column filename_infere next to the filename DONE!
# - change function names : extract_filename to extract_short_filename DONE!
# <br>
#
# - Add the number total of matching marie is equal to the total occurance of two jokers: Done!
# - add column TP after add column filename_infere, to find which student worked on what TP
# - add interepareation for Run.program that there are Editor content and add the test for P_codeState: Done!
# - change the name of TP to notion , there is possiblity that in the semaine_3 there student that worked on notion or TP 2 should check by the name of the filename_infere
# - correct function remove_emptysession in process raw data with =< parametre check the e-mail : 23/05 she will do it mirabelle
# - new dataframe for deleteing some rows
# - check the process raw data
# - look at the functions name from the variable_constatnt.py and check if they exist in the P_codeState or commandRan
# - delete the traces where there is "ODI" in the P_codeState even if there is a filename (waiting for mirabelle response)
# - P_codeState for Run.Program : check the name of function in P_codeState with the name function in variab_constant.py if okay put the name as the filename
# - check utils.py in src/feature to see how thoma extract filename for P_codeState
# - Check the Etude_sur_les_testes.py in notebook / Thomas version to calculate the number of student present of each week and each TP DONE!
# - for File.txt or file.md look at the codestate and then remove it or not the name of the function and the content between <trace></tracte>
# - leave the semaine11
# - just keep the Prog because in the Run.Debugger there is TP that are manipulation which we don't need
# - we want just Nom_TP_PPROGRAMMATION without the first week
# - Leave the part after the print on Etude_sur_les_testes.py
# - See cleaning.keep_research_data_only in notebooks/Init_data.py
#
# - For Docstring.Generate what should I do? take values from function column?
# ## others:
# - Analyze.ipynb
# - add why there are empty filename after commandRan for Run.Program
# - Decide what to do with empty strings of Run.Program
# - Calculate the total name of student (after cleaning process)
# - init_data.py (look at it and the readme of Thomas)
# - Anonymization : actor, binom, P-code state, F-code state, columns_with_path
# - Process raw data
# - Add column that trace the output ?? I don't remember
# - Look at notebooknettoyage of Thomas to add a column
# - Correct Readme
#
# ## Analyze.ipynb
# - analyze by TP, and by students
#
# ## Three main thing for stage
# - How to check if the student did the Test and continue the Test
# - When the Test is red what did they do, did they continue or they did nothing
# - Seperate the student that are very debutan and the student that already did some courses in programmation

#
