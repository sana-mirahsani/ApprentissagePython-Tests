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
from src.data.variable_constant_2425 import SORTED_SEANCE
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

# # Dictionnaire fonctions

# À mettre dans src.data.variable_constants_2425

# +
# Added by Sana

# TP2
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

# TP3
FUNCTIONS_TP3_Prog = [
    "est_non_vide",
    "est_reponse",
    "est_beneficiaire",
    "est_reponse_correcte",
    "est_en_ete",
    "est_nombre_mystere",
    "ont_intersection_vide",
    "intervalle1_contient_intervalle2",
    "sont_intervalles_recouvrants",
    "est_gagnant",
    "est_strict_anterieure_a",
    "est_mineur_a_date",
    "est_senior_a_date",
    "a_tarif_reduit_a_date",
]


# TP4 
FUNCTIONS_TP4_Prog = [
    "numero_jour",
    "nom_jour",
    "est_date_valide",
    "est_jour_valide",
    "nombre_jours",
    "est_mois_valide",
    "calcul_gain",
    "montant_facture",
    "nombre_exemplaires",
    "conseil_voiture",
    "argminimum",
    "cout_location",
    "minimum3",
    "compare",
    "maximum", 
    "est_bissextile"
]



# TP5
FUNCTIONS_TP5_Prog = [
    #"<trace>imprimerie.py</trace>",
    #"<trace>jeu_421.py</trace>",
    "representation_lancer",
    "de",
    "est_42",
    "est_421",
]



# TP6
FUNCTIONS_TP6_Prog = [
    "carres",
    "nombre_occurrences",
    "nombre_occurrences2",
    "moyenne",
    "sans_elt",
    "positive",
    "chiffres",
    "miroir",
    "compte_car"
]



# TP7
FUNCTIONS_TP7_Prog = [
    "echantillonne",
    "elements_indices_impairs",
    "miroir",
    "minimum",
    "decoupage",
    "premieres_occurrences",
    "matchs",
    "nom_domaines",
    "max_identiques",
    "suffixes",
    "resume",
    "ajout_separateur",
    "construit_mots"
    
]


# TP8
FUNCTIONS_TP8_Prog = [
    #"# Jeu de Nim",
    "compte_motif",
    "indice_maximum",
    "moyenne_ponderee",
    "addition_digit",
    "addition",
    "determine",
    "supprime",
    "filtre",
    "nb_jours_avant_1m_blob",
    "somme_chiffres",
    "saisie_pseudo_avec_verification" 
]



# TP9
FUNCTIONS_TP9_Prog = [
    "toutes_longueurs_impaires_while",
    "toutes_longueurs_impaires_for",
    "contient_chiffre_ou_minuscule_while",
    "indice_positif_while",
    "indice_positif_for",
    "contient_nb_occurrences_ou_plus_while",
    "contient_nb_occurrences_ou_plus_for",
    "est_palindrome_while",
    "est_palindrome_for",
    "est_croissante_while",
    "est_croissante_for",
    "tous_differents_while",
    "tous_differents_for",
    "produit_vaut_n_while",
    "produit_vaut_n_for",
    "suffixe_somme_while",
    "suffixe_somme_for",
    "hexa_decimal",
    "decimal_hexa",
    "est_hexa",
    "hexa_binaire",
    "binaire_hexa",
    "genere_hexa",
    "genere_hexa_sans_begaiement",

]

# -

# TP prog only
prog_functions_name_by_tp = {
    'Tp2': FUNCTIONS_TP2_Prog,  # TP2
    'Tp3' : FUNCTIONS_TP3_Prog, # TP3
    'Tp4' : FUNCTIONS_TP4_Prog, # TP4
    'Tp5' : FUNCTIONS_TP5_Prog, # TP5
    "Tp6" : FUNCTIONS_TP6_Prog ,  # TP6
    "Tp7": FUNCTIONS_TP7_Prog, # TP7
    "Tp8" : FUNCTIONS_TP8_Prog,  # TP8
    "Tp9" : FUNCTIONS_TP9_Prog # TP9
    }

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase2_nettoyage_fichiere.csv')

df['codeState'] = df['P_codeState'] + df['F_codeState']

df.columns

# # Fonction pour récupérer le nombre de tests par fonction d'un source, via l1test 

# +
from thonnycontrib.backend.test_finder import L1TestFinder
from thonnycontrib.exceptions import SpaceMissingAfterPromptException

def find_tests_in_codestate(source:str) -> dict:
    '''
    Renvoie un dictionnaire qui associe à chaque fonction trouvée dans source son nombre de tests.
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
    except (ValueError, SyntaxError, SpaceMissingAfterPromptException, AttributeError) as e: 
        # AttributeError levé par thonnycontrib/utils.py
        # AttributeError: 'Attribute' object has no attribute 'id'
        dico = None
    return dico


# -

# # Brouillonnage 1ère version : on cherche le codestate qui a le timestamp le plus récent

df_yanko = df[(df['TP'] == 'Tp2') & (df['actor'] == 'yanko.lemoine.etu')] 



FUNCTIONS_TP2_Prog



df_yanko.columns

df_yanko[df_yanko['codeState'] != '']['timestamp.$date']

df_yanko[df_yanko['codeState'] != '']['timestamp.$date'].idxmax()

most_recent_codeState_yanko = df_yanko.loc[298676]['codeState']

find_tests_in_codestate(most_recent_codeState_yanko)


# # Fonctions 1ère version  et 2ème version : on regarde tous les 

def find_test_in_codestate_for_functions(codeState:str, functions_tp:list[str]) -> dict:
    '''
    Returns the number of tests found in codeState, only for functions in functions_tp

    dict has the shape name_func : int (number of tests) or None (function not found)
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

# les timestamps ne sont pas triés par ordre croissant

timestamps_rostell.is_monotonic_increasing

timestamps_rostell = df_rostell[df_rostell['codeState'] != '']['timestamp.$date'].tolist()
for i in range(len(timestamps_rostell)-1):
    if timestamps_rostell[i] > timestamps_rostell[i+1]:
        print(i, i+1, timestamps_rostell[i], timestamps_rostell[i+1]) 

df_rostell[df_rostell['timestamp.$date'] == '2024-10-11 08:36:30.899000+00:00']['session.id']

df_rostell[df_rostell['timestamp.$date'] == '2024-09-12 13:22:20.311000+00:00']['session.id']

df_rostell.columns

list_index_timestamps_rostell = df_rostell[df_rostell['codeState'] != '']['timestamp.$date'].index.tolist()
df_rostell[df_rostell['codeState'] != '']['timestamp.$date'].idxmax()

list_index_timestamps_rostell.index(257660)

index_a_parcourir = list_index_timestamps_rostell[:72+1]
for i in range(72, -1, -1):
    index = index_a_parcourir[i]
    if df.loc[index]['verb'] == 'Session.Start':
        print(None)
        break # oui je sais, je sais...
    most_recent_codeState = df_rostell.loc[index]['codeState']
    dict_tests = find_test_in_codestate_for_functions(most_recent_codeState, prog_functions_name_by_tp['Tp2'])
    if dict_tests != None:
        print(dict_tests)
        break
print(None)

most_recent_codeState_rostell = df_rostell.loc[df_rostell[df_rostell['codeState'] != '']['timestamp.$date'].idxmax()]['codeState']

find_test_in_codestate_for_functions(most_recent_codeState_rostell, FUNCTIONS_TP2_Prog)

df_magatte = df[(df['TP'] == 'Tp2') & (df['binome'] == 'magatte.mbathie.etu')]

len(df_magatte)

actor_column_tp2  = df[(df['TP'] == 'Tp2') & (df['Type_TP'] == 'TP_prog')]['actor']
column_binome_tp2 = df[(df['TP'] == 'Tp2') & (df['Type_TP'] == 'TP_prog')]['binome']
all_students_tp2  = set(actor_column_tp2).union(set(column_binome_tp2))

df.loc[81051]



# Je ne sais plus où on a fait l'hypothèse que les timestamps étaient croissants, mais ce n'est pas vrai
# car on ajoute des traces "binome" à des traces "actor".

def find_tests_for_tp_tpprog_name_bis(name:str, df:pd.DataFrame, tp:str, functions_names:dict) -> tuple[pd.DataFrame, bool, bool]:
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
        timestamps = df_codestate_nonempty['timestamp.$date'].copy() # pour être sûre de ne pas modifier le df initial
        found = False # found codeState with functions not all unfoundable
        while not timestamps.empty and not found: 
            index_of_timestamp_max = timestamps.idxmax()
            most_recent_codeState = df_name_tp.loc[index_of_timestamp_max]['codeState']
            dict_tests = find_test_in_codestate_for_functions(most_recent_codeState, functions_names[tp])
            if dict_tests != None: # parseable
                col_functions = []
                col_tests_number = []
                for key, value in dict_tests.items():
                    col_functions.append(key)
                    col_tests_number.append(value)
                nb_rows = len(dict_tests)
                if col_tests_number != [None]*nb_rows: # convenient codestate found
                    found = True
                    col_actors = [name] * nb_rows
                    col_tp = [tp] * nb_rows
                    col_index = [index_of_timestamp_max] * nb_rows
                    df_result = pd.DataFrame({'actor' : col_actors, 'tp' : col_tp, 'function_name' : col_functions, \
                                          'tests_number' : col_tests_number, 'index' : col_index })
                else: # codestate no convenient : drop this index and continue
                    timestamps = timestamps.drop(index=[index_of_timestamp_max])
            else: # codestate not parsable : drop this index and continue
                timestamps = timestamps.drop(index=[index_of_timestamp_max])
        if found:
            return df_result, False, False
        else:
            #print(f"no functions found for {name} and index {index_of_timestamp_max}")
            return None, True, False


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
        timestamps = df_codestate_nonempty['timestamp.$date'].copy() # pour être sûre de ne pas modifier le df initial
        list_index_timestamps = timestamps.index.tolist()
        index_of_timestamp_max = timestamps.idxmax()
        ind_of_timestamp_max_in_list = list_index_timestamps.index(index_of_timestamp_max)
        index_to_examine = list_index_timestamps[:ind_of_timestamp_max_in_list+1]
        for i in range(ind_of_timestamp_max_in_list, -1, -1):
            index = index_to_examine[i]
            #if df.loc[index]['verb'] == 'Session.Start': # parseable codestate not found
            #    return None, True, False
            most_recent_codeState = df_name_tp.loc[index]['codeState']
            dict_tests = find_test_in_codestate_for_functions(most_recent_codeState, prog_functions_name_by_tp[tp])
            if dict_tests != None: # parseable
                col_functions = []
                col_tests_number = []
                for key, value in dict_tests.items():
                    col_functions.append(key)
                    col_tests_number.append(value)
                nb_rows = len(dict_tests)
                col_actors = [name] * nb_rows
                col_tp = [tp] * nb_rows
                col_index = [index] * nb_rows
                df_result = pd.DataFrame({'actor' : col_actors, 'tp' : col_tp, 'function_name' : col_functions, \
                                          'tests_number' : col_tests_number, 'index' : col_index })
                return df_result, False, False                                                      
        # not parsable
        return None, True, False


df_tests_yanko = find_tests_for_tp_tpprog_name('yanko.lemoine.etu', df, 'Tp2')
df_tests_yanko 

df_tests_yanko_bis = find_tests_for_tp_tpprog_name_bis('yanko.lemoine.etu', df, 'Tp2', prog_functions_name_by_tp)
df_tests_yanko_bis

df_tests_rostell = find_tests_for_tp_tpprog_name('rosche-rostell.batchi-vouala.etu', df, 'Tp2')
df_tests_rostell 

df_tests_rostell_bis = find_tests_for_tp_tpprog_name_bis('rosche-rostell.batchi-vouala.etu', df, 'Tp2', prog_functions_name_by_tp)
df_tests_rostell_bis 

df_tests_ange_bis = find_tests_for_tp_tpprog_name_bis('m-bah-ange-pascal.tanoh.etu', df, 'Tp2', prog_functions_name_by_tp)
df_tests_ange_bis

df_tests_adama_bis = find_tests_for_tp_tpprog_name_bis('adama-eliya.avlah.etu', df, 'Tp2', prog_functions_name_by_tp)
df_tests_adama_bis

df_tout = pd.concat([df_tests_yanko[0], df_tests_rostell[0]], ignore_index=True)
df_tout


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


def find_tests_for_tp_tpprog_bis(df:pd.DataFrame, tp:str, functions_names:dict) -> tuple[pd.DataFrame, list[str], list[str]]:
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
        df_name, cannot_analyze_codestate, empty_codestates = find_tests_for_tp_tpprog_name_bis(name, df, tp, functions_names)
        if cannot_analyze_codestate:
            cannot_analyze_codestate_students.append(name)
        if empty_codestates:
            empty_codestate_students.append(name)
        if df_name is not None:
            df_result = pd.concat([df_result, df_name], ignore_index=True)
    return df_result, cannot_analyze_codestate_students, empty_codestate_students                    


df_tests_tp2_bis, cannot_analyze_codestate_students_tp2_bis, empty_codestate_students_tp2_bis  = find_tests_for_tp_tpprog_bis(df, 'Tp2', prog_functions_name_by_tp)

print(f'BIS Cannot analyze codestate in Tp2 for : {cannot_analyze_codestate_students_tp2_bis}')
print(f'BIS only empty codestates in Tp2 for : {empty_codestate_students_tp2_bis}')

df_tests_tp2, cannot_analyze_codestate_students_tp2, empty_codestate_students_tp2  = find_tests_for_tp_tpprog(df, 'Tp2')


print(f'Cannot analyze codestate in Tp2 for : {cannot_analyze_codestate_students_tp2}')
print(f'only empty codestates in Tp2 for : {empty_codestate_students_tp2}')

df_tests_tp2[0:50]

len(df_tests_tp2)

df_tests_tp5_bis, cannot_analyze_codestate_students_tp5bis, empty_codestate_students_tp5_bis  = find_tests_for_tp_tpprog_bis(df, 'Tp5', prog_functions_name_by_tp)

df_tests_tp5_bis

print(f'Cannot analyze codestate in Tp5 for : {cannot_analyze_codestate_students_tp5bis}')
print(f'only empty codestates in Tp5 for : {empty_codestate_students_tp5_bis}')


def find_tests_for_all_tp_tpprog_bis(df:pd.DataFrame, functions_names:dict) -> tuple[pd.DataFrame, dict, dict]:
    df_tests = pd.DataFrame(columns=['actor', 	'tp', 	'function_name', 	'tests_number', 	'index'])
    cannot_analyze_codestate_students = {}
    empty_codestate_students = {}
    for tp in functions_names:
        print(f'TP {tp}')
        df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp = find_tests_for_tp_tpprog_bis(df, tp, functions_names)
        df_tests = pd.concat([df_tests, df_tests_tp], ignore_index=True)
        cannot_analyze_codestate_students[tp] = cannot_analyze_codestate_students_tp
        empty_codestate_students[tp] = empty_codestate_students_tp
    return df_tests, cannot_analyze_codestate_students, empty_codestate_students


df_tests_bis, cannot_analyze_codestate_students_bis, empty_codestate_students_bis  = find_tests_for_all_tp_tpprog_bis(df, prog_functions_name_by_tp)



df_tests_bis

print(f'Cannot analyze codestate for : {cannot_analyze_codestate_students_bis}')

print(f'only empty codestates in for : {empty_codestate_students_bis}')

# # Recherche du nb de tests par tp_game

# Cette fois on compte les tests dans l'ensemble du module.
#
# Pour chaque étudiant on regarde quels tp game il a fait. 
#
# Pour chaque tp_game on regarde le nb de tests.

# # Exemples pour vieille version calcul nb tests TP2 à TP9 

df.loc[218732] # ne devrait pas y avoir de tests

print(df.loc[218732]['codeState']) # il y a des tests, ce n'est pas un fichier très cohérent...

df.loc[188941] # c'est un TicTacToe... pas du tout le TP2 !

print(df.loc[188941]['codeState'])

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


