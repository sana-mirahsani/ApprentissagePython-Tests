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

# code final pour calculer le nb de tests par fonction.

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
from src.data.variable_constant_2425 import SORTED_SEANCE, all_TP_functions_name, all_TP_prog_functions_name_by_tp
import re
from src.data.variable_constant_2425 import FILES_BY_TP, TP_NAME
from src.features import data_cleaning

# -

# import spécifiques à L1test

from thonnycontrib.backend.test_finder import L1TestFinder
from thonnycontrib.exceptions import SpaceMissingAfterPromptException

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase2_nettoyage_fichiere.csv')

df['codeState'] = df['P_codeState'] + df['F_codeState']

# À mettre dans src.data.variable_constants_2425. Ce sont les noms des fonctions par TP, noms de fonctions uniquement.

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


# +
from thonnycontrib.backend.test_finder import L1TestFinder
from thonnycontrib.exceptions import SpaceMissingAfterPromptException

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


# -

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


# Cette fonction est partie du principe que les timestamps étaient triés en ordre croissant, ce qui est faux.
#
# Elle cherche le codestate le plus récent, et s'il n'est pas analysable, en cherche un analysable dans les précédents. Ce faisant on risque de rater un autre codestate qui aurait pu être analysable, mais tant pis.

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
                col_actors = [name] * nb_rows
                col_tp = [tp] * nb_rows
                col_index = [index] * nb_rows
                df_result = pd.DataFrame({'actor' : col_actors, 'tp' : col_tp, 'function_name' : col_functions, \
                                          'tests_number' : col_tests_number, 'index' : col_index })
                return df_result, False, False                                                      
        # not parsable
        return None, True, False


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


df_tests_tp2, cannot_analyze_codestate_students_tp2, empty_codestate_students_tp2  = find_tests_for_tp_tpprog(df, 'Tp2')

print(f'Cannot analyze codestate in Tp2 for : {cannot_analyze_codestate_students_tp2}')
print(f'only empty codestates in Tp2 for : {empty_codestate_students_tp2}')

df_tests_tp2[0:50]

len(df_tests_tp2)




