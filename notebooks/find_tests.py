# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: venv_jupyter_l1test
#     language: python
#     name: venv_jupyter_l1test
# ---

# +
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
from src.data.variable_constant_2425 import FILES_BY_TP, TP_NAME
from src.features import data_cleaning

# just for test
# Global variable pattern
pattern = ''
for tp_name in FILES_BY_TP:

    file_name = '|'.join(tp_name)
    pattern = pattern +  file_name + '|'

pattern = pattern  + 'Irrelevant' 
# -

from src.data.variable_constant_2425 import FUNCTIONS_TP2_Prog, FUNCTIONS_TP3_Prog, FUNCTIONS_TP4_Prog, FUNCTIONS_TP5_Prog, FUNCTIONS_TP6_Prog, FUNCTIONS_TP7_Prog, FUNCTIONS_TP8_Prog, FUNCTIONS_TP9_Prog

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase2_nettoyage_fichiere.csv')

# +
from thonnycontrib.backend.test_finder import L1TestFinder
from thonnycontrib.exceptions import SpaceMissingAfterPromptException

def find_tests_in_codestate(source:str) -> dict:
    '''
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


# -

df['codeState'] = df['P_codeState'] + df['F_codeState']

df_yanko = df[(df['TP'] == 'Tp2') & (df['actor'] == 'yanko.lemoine.etu')] 



FUNCTIONS_TP2_Prog



df_yanko.columns

df_yanko[df_yanko['codeState'] != '']['timestamp.$date']

df_yanko[df_yanko['codeState'] != '']['timestamp.$date'].idxmax()

most_recent_codeState_yanko = df_yanko.loc[298676]['codeState']

find_tests_in_codestate(most_recent_codeState_yanko)


def find_test_in_codestate_for_functions(codeState:str, functions_tp:list[str]) -> dict:
    '''
    Returns the number of tests found in codeState, only for functions in functions_tp
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


find_test_in_codestate_for_functions(most_recent_codeState_yanko, FUNCTIONS_TP2_Prog)

df_rostell = df[(df['TP'] == 'Tp2') & (df['actor'] == 'rosche-rostell.batchi-vouala.etu')] 

len(df_rostell)

df_rostell[df_rostell['codeState'] != '']['timestamp.$date'].idxmax()

most_recent_codeState_rostell = df_rostell.loc[257660]['codeState']

find_test_in_codestate_for_functions(most_recent_codeState_rostell, FUNCTIONS_TP2_Prog)

df_magatte = df[(df['TP'] == 'Tp2') & (df['binome'] == 'magatte.mbathie.etu')]

len(df_magatte)

actor_column_tp2  = df[(df['TP'] == 'Tp2') & (df['Type_TP'] == 'TP_prog')]['actor']
column_binome_tp2 = df[(df['TP'] == 'Tp2') & (df['Type_TP'] == 'TP_prog')]['binome']
all_students_tp2  = set(actor_column_tp2).union(set(column_binome_tp2))

df.loc[81051]

for name in all_students_tp2:
    df_name_tp2 = df[(df['TP'] == 'Tp2') & (df['Type_TP'] == 'TP_prog') & ((df['actor'] == name) | (df['binome'] == name))]
    df_codestate_nonempty = df_name_tp2[df_name_tp2['codeState'] != '']
    if len(df_codestate_nonempty) == 0:
        print('codestateempty', name)
        print(df_codestate_nonempty)
    else:
        most_recent_index_codestate = df_codestate_nonempty['timestamp.$date'].idxmax()
        most_recent_codeState = df_name_tp2.loc[most_recent_index_codestate]['codeState']
        res = find_test_in_codestate_for_functions(most_recent_codeState, FUNCTIONS_TP2_Prog)
#    if res is None:
#        print(name)

df.loc[266891][['actor','verb', 'filename_infere', 'codeState', 'commandRan']]

df.loc[266853][['TP', 'timestamp.$date','actor','verb', 'filename_infere', 'codeState', 'commandRan']]

df.loc[266889:266892][['TP', 'timestamp.$date','actor','verb', 'filename_infere', 'codeState', 'commandRan', 'stderr']]

df.loc[266854:266900][['TP', 'timestamp.$date','actor','verb', 'filename_infere', 'codeState', 'commandRan']]

df.loc[266901:266950][['TP',  'timestamp.$date', 'actor','verb', 'filename_infere', 'codeState', 'commandRan']]

df.loc[266951:266980][['TP','timestamp.$date','actor','verb', 'filename_infere', 'codeState', 'commandRan']]

df.loc[266981:267000][['TP','timestamp.$date','actor','verb', 'filename_infere', 'codeState', 'commandRan']]

df.loc[267001:267030][['TP','timestamp.$date','actor','verb', 'filename_infere', 'codeState', 'commandRan', 'function']]

df.loc[267031:267050][['TP','timestamp.$date','actor','verb', 'filename_infere', 'codeState', 'commandRan', 'function']]

TP_NAME

FUNCTIONS_PROG_BY_TP = {
    'Tp2' : FUNCTIONS_TP2_Prog,
    'Tp3' : FUNCTIONS_TP3_Prog,
    'Tp4' : FUNCTIONS_TP4_Prog,
    'Tp5' : FUNCTIONS_TP5_Prog,
    'Tp6' : FUNCTIONS_TP2_Prog,
    'Tp7' : FUNCTIONS_TP3_Prog,
    'Tp8' : FUNCTIONS_TP4_Prog,
    'Tp9' : FUNCTIONS_TP5_Prog}

FUNCTIONS_PROG_BY_TP

for tp in ['Tp2', 'Tp3', 'Tp4', 'Tp5', 'Tp6', 'Tp7', 'Tp8', 'Tp9']:
    print('************TP***', tp)
    actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['actor']
    column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['binome']
    all_students_tp  = set(actor_column_tp).union(set(column_binome_tp))

    for name in all_students_tp:
        df_name_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & ((df['actor'] == name) | (df['binome'] == name))]
        df_codestate_nonempty = df_name_tp[df_name_tp['codeState'] != '']
        if len(df_codestate_nonempty) == 0:
            print('codestateempty', name)
            print(df_codestate_nonempty)
        else:
            most_recent_index_codestate = df_codestate_nonempty['timestamp.$date'].idxmax()
            most_recent_codeState = df_name_tp.loc[most_recent_index_codestate]['codeState']
            res = find_test_in_codestate_for_functions(most_recent_codeState, FUNCTIONS_PROG_BY_TP[tp])


df.loc[266891]

df_hamza = df[(df['TP'] == 'Tp3') & ((df['Type_TP'] == 'TP_prog') & (df['actor'] == 'hamza.chebbah.etu') | (df['binome'] == 'hamza.chebbah.etu'))]
df_hamza[['verb', 'filename_infere', 'commandRan']]

df.loc[105140:105156][['verb', 'filename_infere', 'commandRan', 'codeState']]

df.loc[105147]['codeState']

print(df.loc[105147]['codeState'])

df.loc[105156:105160][['verb', 'filename_infere', 'commandRan', 'codeState']]

df.loc[105159]['codeState']

df_hamza = df[(df['TP'] == 'Tp3') & ((df['Type_TP'] == 'TP_prog') & (df['actor'] == 'hamza.chebbah.etu') | (df['binome'] == 'hamza.chebbah.etu'))]
df_hamza[['verb', 'filename_infere', 'commandRan']]

df_ismail = df[(df['TP'] == 'Tp4') & ((df['Type_TP'] == 'TP_prog') & (df['actor'] == 'ismail.nejjar.etu') | (df['binome'] == 'ismail.nejjar.etu'))]
df_ismail[['verb', 'filename_infere', 'commandRan']]


df.loc[26410:26424][['verb', 'filename_infere', 'commandRan']]

df.loc[26424:26430][['verb', 'filename_infere', 'commandRan']]

print(df.loc[26426]['codeState'])

df.loc[26427]['filename']

df_mounir = df[(df['TP'] == 'Tp5') & ((df['Type_TP'] == 'TP_prog') & (df['actor'] == 'mounir.achbad.etu') | (df['binome'] == 'mounir.achbad.etu'))]
df_mounir[['verb', 'filename_infere', 'commandRan']]


df.loc[211660:211670][['verb', 'filename_infere', 'commandRan']]

df.loc[211663]['commandRan']

df.loc[211664]['codeState']

import re
match = re.search("est_non_vide\(", "est_non_vide('')")
print(match)

match = re.search("est_non_vide\(", "est_non_vide('ki')")
print(match)

match.group()


