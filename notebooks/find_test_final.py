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
from src.data.constants import INTERIM_DATA_DIR, RAW_DATA_DIR
from src.data.variable_constant_2425 import SORTED_SEANCE, TP_NAME
import matplotlib.pyplot as plt
import numpy as np
import difflib

# just for test
from src.data.variable_constant_2425 import SORTED_SEANCE
import re
from src.data.variable_constant_2425 import FILES_BY_TP, TP_NAME
from src.features import data_cleaning

# -

# # import spécifiques à L1test

from thonnycontrib.backend.test_finder import L1TestFinder
from thonnycontrib.exceptions import SpaceMissingAfterPromptException

# # Dataframe

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase3_nettoyage_fichiere.csv')

len(df)

# Inutile mais j'en avais besoin avant...

df['codeState'] = df['P_codeState'] + df['F_codeState']

# nb étudiants

set_actor_df = set(df.actor)
set_binome_df = set(df.binome)
if '' in set_binome_df:
    set_binome_df.remove('')
nb_actor_df = len(set_actor_df.union(set_binome_df))

print(f'nb étudiants dans le df global : {nb_actor_df}')

# # Tableur étud

df_admin_etud = io_utils.reading_dataframe(dir= RAW_DATA_DIR, file_name='identifiants_2425.csv')

df_admin_etud.columns

df_admin_etud

# ## Nettoyage étudiants sans NIP

df_admin_etud[df_admin_etud['NIP']=='']

students = (set(df['actor'].values).union(df['binome'].values))
students.remove('')

'mamadou.barry8.etu' in students

len(df[df['actor']=='mamadou.barry8.etu'])

'mamadou-bachir.barry.etu' in students

len(df[df['actor']=='mamadou-bachir.barry.etu'])

# À voir comment on fait avec cet étudiant.

df_admin_etud[df_admin_etud['redoublant']=='']

len(df_admin_etud[(df_admin_etud['redoublant']=='oui')]) + len(df_admin_etud[df_admin_etud['redoublant']=='non'])

df_admin_etud['debutant'] = (df_admin_etud['NSI']!='NSI2') & (df_admin_etud['redoublant']=='non')

df_admin_etud

# ## Comment merger avec un autre df

df_admin_etud_debutants = df_admin_etud[['actor', 'debutant']].copy()

df_admin_etud_debutants

df_debutant = df.copy()

df_debutant['debutant'] = (df_debutant.merge(df_admin_etud_debutants, on='actor', how='inner'))['debutant']

len(df_debutant)

df_debutant.debutant.unique()

df_debutant[df_debutant['actor']=='nadjib.zoubir.etu'].debutant.unique()

df_debutant[df_debutant['actor']=='yanko.lemoine.etu'].debutant.unique()

df_debutant[df_debutant['actor']=='ibrahima.diop.etu'].debutant.unique()

df_debutant[df_debutant['actor']=='rosche-rostell.batchi-vouala.etu'].debutant.unique()

df_debutant[df_debutant['actor']=='ilyes.benferhat.etu'].debutant.unique()

# # Fonctions pour analyser les TPs Tp_Prog de 'Tp2' à 'Tp9'

# ## Ajouts à faire dans src.data.variable_constants_2425

# Normalement ce qui suit est déjà dans dans src.data.variable_constants_2425. Ce sont les noms des fonctions par TP, noms de fonctions uniquement. 

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
    #"miroir", à enlever car présent ds 2 TP
    "compte_car"
]



# TP7
FUNCTIONS_TP7_Prog = [
    "echantillonne",
    "elements_indices_impairs",
    #"miroir", à enlever car présent ds 2 TP
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
    #"saisie_pseudo_avec_verification" # non testable 
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


# Peut-être pas déjà dans src.data.variable_constants_2425. Il faudra peut-être renommer les valeurs de cette constante en fonction de ce qui existe déjà dans src.data.variable_constants_2425. Attention les clés sont les TP, pas les filename.

PROG_FUNCTIONS_NAME_BY_TP = {
    'Tp2' : FUNCTIONS_TP2_Prog,
    'Tp3' : FUNCTIONS_TP3_Prog,
    'Tp4' : FUNCTIONS_TP4_Prog,
    'Tp5' : FUNCTIONS_TP5_Prog,
    'Tp6' : FUNCTIONS_TP6_Prog,
    'Tp7' : FUNCTIONS_TP7_Prog,
    'Tp8' : FUNCTIONS_TP8_Prog,
    'Tp9' : FUNCTIONS_TP9_Prog,
}

# Je préfère utiliser les filename_infere plutôt que les Tps, ça m'évite les mésaventures pour le TP8 qui contenait 2 fichiers : jeu_nim.py ne m'intéresse pas pour les fonctions.

PROG_FILENAMES_BY_TP = {
    'Tp2' : 'fonctions.py',
    'Tp3' : 'booleens.py',
    'Tp4' : 'conditionnelles.py',
    'Tp6' : 'iterables_for.py',
    'Tp7' : 'iterable_indexation.py',
    'Tp8' : 'while.py',
    'Tp9' : 'parcours_interrompu.py',    
}


# ## Fonctions

# Mettre ces fonctions dans src. Elles comptent le nombre de tests écrits par fonction (les $$$) sans du tout analyser les Run.Test (qui eux exécutent les tests). On utilise une fonctionnalité interne de l1test (le L1TestFinder) pour analyser le contenu des codeState. Le L1TestFinder provoquera une erreur si le contenu du codeState n'est pas syntaxiquement correct (par ex parce qu'il y a une erreur de syntaxe Python ou une erreur de syntaxe dans les tests).
#
# Pour un TP donné et un actor donné il y a plein de codeState dans les traces, il faut en choisir un. Le principe adopté ici est de prendre le codeState qui a le timestamp le plus récent et qu'on peut imaginer être le travail le plus abouti. Si on peut en extraire des tests, on le fait. Si on ne peut pas en extraire des tests (erreur de syntaxe), alors on cherche le codeState qui a le timestamp le plus récent à l'exclusion du précédent, et on répète tant qu'il y a des codeState à examiner.
#
# Si tous les codeStates sont vides ou si on n'a pas pu les analyser, on renvoie None.

def find_tests_in_codestate(source:str) -> dict:
    '''
    Returns a dictionnary which associates to each function found in `source` its number of tests (using l1test), or None if `source` cannot be parsed either by Python or the l1test parser.
    
    Args:
        source is some codestate

    Returns:
        a dictionnary if the kind {<function_name> : <test_number>:int} or None if `source` couldn't be parsed.
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


def find_tests_in_codestate_for_functions(codeState:str, functions_tp:list[str]) -> dict:
    '''
    Returns a dictionnary which associates to each function of `functions_tp` found in `codeState` its number of tests, or None if the function could'nd be found in `codeState`.

    Args:
        codeState : some codeState
        functions_tp : a list of functions name to consider

    Returns:
        the dict has the shape {name_func : int (number of tests) or None (function not found)}, or None if codeState not parsable.

    Ex: 
    codeState1 is not parsable
    >>> find_tests_in_codestate_for_functions(codeState1, ['foo1', 'foo2', 'foo3'])
    None

    codeState2 is parsable, foo1 has 3 tests, foo2 is not defined in codeState2, foo3 has 0 test
    >>> find_tests_in_codestate_for_functions(codeState2, ['foo1', 'foo2', 'foo3'])
    {'foo1' : 3, 'foo2' : None, 'foo3' : 0}
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


#
#

def find_tests_for_tp_tpprog_name(name:str, df:pd.DataFrame, tp:str, functions_names:dict, filename:str=None) -> tuple[pd.DataFrame, bool, bool]:
    """
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for `name` and `tp`, then looks repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

    - a DataFrame with columns 'actor', 'tp', 'function_name', 'tests_number' (int or None if not present in codestates), 'index' (index in df of the analyzed codeState)
    - a first bool, True if for that student the codeStates cannot be analyzed (Python or l1test syntax error) or codestates contain no function of functions_names
    - a second bool, True if for that student and that tp no codeState was found, or only empty codeStates

    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        name: some actor (ex : 'truc.machin.etu')
        df: some DataFrame
        tp: some TP identifiers (ex : 'Tp2')
        functions_name: a dict which associates to each Tp identifier a list of functions name (ex : functions_names['Tp2] is ['foo1', 'foo2', 'foo3'])
        filename: the name of a particular filename_infere to analyze. Other filename_infere of the tp are not analyzed. Useful when a TP involves multiple files
        
    Returns:
        None, False, True: if no codeState was found, or only empty codeStates
        None, True, False: if no codeState could be parsed, or no codeState contains at least one function of functions_name
        df, False, False: if some codeState could be parsed and contains the number of tests
    
    """
    # Les timestamps ne sont pas triés par ordre croissant.
    # La fonction recherche les codeState comme suit : 
    # - elle cherche le codestate le plus récent,
    # - s'il est analysable, elle vérifie qu'il y a au moins une des fonctions cherchées dedans
    # - s'il n'est pas analysable ou si aucune fonction n'est trouvée, elle cherche à nouveau le codestate le plus récent, moins le précédent.
    # Et ce tant qu'il y a des codestate à traiter.
    if filename == None:
        df_name_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & ((df['actor'] == name) | (df['binome'] == name))]
    else:
        df_name_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') \
                        & ((df['actor'] == name) | (df['binome'] == name)) \
                        & (df['filename_infere'] == filename)]
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
            dict_tests = find_tests_in_codestate_for_functions(most_recent_codeState, functions_names[tp])
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


def find_tests_for_tp_tpprog(df:pd.DataFrame, tp:str, functions_names:dict, filename:str=None) -> tuple[pd.DataFrame, list[str], list[str]]:
    """
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for all students of `tp`, then looks repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

    - a DataFrame with columns 'actor', 'tp', 'function_name', 'tests_number' (int or None if function not present in codestates), 'index' (index in df of the analyzed codeState)
    - a first list : actors for which the codeStates for `tp` cannot be analyzed (Python or l1test syntax error) or codestates contain no function of functions_names
    - a second list, actors for which no codeState was found for `tp`, or only empty codeStates

    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        df: some DataFrame
        tp: some TP identifiers (ex : 'Tp2')
        functions_name: a dict which associates to each Tp identifier a list of functions name (ex : functions_names['Tp2] is ['foo1', 'foo2', 'foo3'])
        filename: the name of a particular filename_infere to analyze. Other filename_infere of the tp are not analyzed. Useful when a TP involves multiple files

    Returns:
        a tuple of len 3 :
        >>> df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp  = find_tests_for_tp_tpprog(df, some_tp, PROG_FUNCTIONS_NAME_BY_TP)
        - df_tests_tp is a DataFrame of 'columns actor', 'tp', 'function_name', 'tests_number', 'index'
        - cannot_analyze_codestate_students_tp is the list of actors for which no codeState could be analysed (or no functions found)
        - empty_codestate_students_tp is the list of actors for which only empty codestate could be found
        
        in columns 'test_number': 0 means no tests, None means function not found
        """
    df_result = pd.DataFrame(columns=['actor', 	'tp', 	'function_name', 	'tests_number', 	'index'])
    empty_codestate_students = []
    cannot_analyze_codestate_students = []
    if filename == None:
        actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['actor']
        column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['binome']
    else:
        actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == filename)]['actor']
        column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == filename)]['binome']
    all_students_tp  = set(actor_column_tp).union(set(column_binome_tp))
    if '' in all_students_tp:
        all_students_tp.remove('')
    for name in all_students_tp:
        df_name, cannot_analyze_codestate, empty_codestates = find_tests_for_tp_tpprog_name(name, df, tp, functions_names, filename)
        if cannot_analyze_codestate:
            cannot_analyze_codestate_students.append(name)
        if empty_codestates:
            empty_codestate_students.append(name)
        if df_name is not None:
            df_result = pd.concat([df_result, df_name], ignore_index=True)
    return df_result, cannot_analyze_codestate_students, empty_codestate_students   


def find_tests_for_all_tp_tpprog(df:pd.DataFrame, functions_names:dict) -> tuple[pd.DataFrame, dict, dict]:
    """
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for all students of all tp, then looks repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

    - a DataFrame with columns 'actor', 'tp', 'function_name', 'tests_number' (int or None if function not present in codestates), 'index' (index in df of the analyzed codeState)
    - a first dict : keys are tp and values are the list of actors for which the codeStates for `tp` cannot be analyzed (Python or l1test syntax error) or codestates contain no function of functions_names
    - a second list: keys are tp and values are the list of actors for which no codeState was found for `tp`, or only empty codeStates

    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        df: some DataFrame
        functions_name: a dict which associates to each Tp identifier a list of functions name (ex : functions_names['Tp2] is ['foo1', 'foo2', 'foo3'])
        
    Returns:
        a tuple of len 3 :
        >>> df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp  = find_tests_for_tp_tpprog(df, PROG_FUNCTIONS_NAME_BY_TP)
        - df_tests is a DataFrame of 'columns actor', 'tp', 'function_name', 'tests_number', 'index'
        - cannot_analyze_codestate_students is the dict of {<tp>: <actors>}, actors for which no codeState could be analysed (or no functions found)
        - empty_codestate_students is the dict of {<tp>: <actors>}, actors for which only empty codestate could be found
        
        in columns 'test_number': 0 means no tests, None means function not found   
    """
    df_tests = pd.DataFrame(columns=['actor', 	'tp', 	'function_name', 	'tests_number', 	'index'])
    cannot_analyze_codestate_students = {}
    empty_codestate_students = {}
    for tp in functions_names:
        print(f'TP {tp}')
        df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp = find_tests_for_tp_tpprog(df, tp, functions_names)
        df_tests = pd.concat([df_tests, df_tests_tp], ignore_index=True)
        cannot_analyze_codestate_students[tp] = cannot_analyze_codestate_students_tp
        empty_codestate_students[tp] = empty_codestate_students_tp
    return df_tests, cannot_analyze_codestate_students, empty_codestate_students


# ## Exemple d'utilisation pour le Tp2.

df_tests_tp2, cannot_analyze_codestate_students_tp2, empty_codestate_students_tp2  = find_tests_for_tp_tpprog(df, 'Tp2', PROG_FUNCTIONS_NAME_BY_TP)

print(f'Cannot analyze codestate in Tp2 for : {cannot_analyze_codestate_students_tp2}')
print(f'only empty codestates in Tp2 for : {empty_codestate_students_tp2}')

# Explication des colonnes (voir les docstrings des fonctions aussi) :
#
# - l'index correspond à l'index du codeState qui a été analysé
# - test_number peut prendre 2 types de valeur
#   
#       - None : la fonction (fonction_name) n'est pas codée dans le codeState
#       - int : la fonction est codée avec test_number tests
#

df_tests_tp2[0:50]

df_tests_tp2[df_tests_tp2['tests_number']==0]

len(df_tests_tp2[df_tests_tp2['tests_number']==0]) 

# ## Exemple d'utilisation pour le TP5

# Not relevant for Tp5 ("print week") 
#
# - only 4 functions with tests (all others were not testable)
# -  2 provided files for TP_Prog: not easy to analyze.
#
# As we can see below : codeStates could not be analyzed for a lot of actors. Maybe because data was analyzed before executing Sana's changes in cleaning phase1 and 2 + modifications in variable_constants_2425.  I saved these actors in cannot_analyze_codestate_students_tp5_saved.

df_tests_tp5, cannot_analyze_codestate_students_tp5, empty_codestate_students_tp5  = find_tests_for_tp_tpprog(df, 'Tp5', PROG_FUNCTIONS_NAME_BY_TP)

df_tests_tp5

print(f'Cannot analyze codestate in Tp5 for : {cannot_analyze_codestate_students_tp5}')


cannot_analyze_codestate_students_tp5_saved = ['anaelle.case.etu', 'boubacar.barry.etu', 'komivi.akpata.etu', 'sami.boumiz.etu', 'valentin.faust.etu', 'pedro-luis.lock-benites.etu', 'david.kahak.etu', 'nhungocanh.nguyen.etu', 'jacques-lazare.diatta.etu', 'florian.heyte.etu', 'edohson-arnaud.guedou.etu', 'abdoulaye.nguere.etu', 'enzo.dewez.etu', 'nassim.abbad.etu', 'hugo.vandewalle2.etu', 'faustine.descatoire.etu', 'yanis.kharchi.etu', 'louis.warembourg.etu', 'elyas.rabhiu.etu', 'dania.baroud.etu', 'lea.claire.etu', 'walid.farrash.etu', 'alpha-mahmoudou.diallo.etu', 'ruben.cassin.etu', 'mamadou.manga.etu', 'marion.le-guen.etu', 'yanis.nabet.etu', 'aurelien.bithorel.etu', 'ben-magloire.hoessi.etu', 'luc.duriez.etu', 'rosche-rostell.batchi-vouala.etu', 'elyes.guedria.etu', 'noe.le-van-canh-dit-ban.etu', 'bilel.taieb.etu', 'assia.mousselmal.etu', 'igor.belyaev.etu', 'thomas.desbuissons.etu', 'fawaaz.oyedotun.etu', 'ayao-landry-jeremie.dzossou-afanlete.etu', 'romane.deleau.etu', 'nadjib.zoubir.etu', 'shema.mugambira.etu', 'chaima.chakroun.etu', 'safa-khawthar.draouche.etu', 'kotchi-ange-gedeon.kama.etu', 'elliot.launay.etu', 'yanis.gannar.etu', 'sadia.muhammad.etu', 'aymeric.amblanc.etu', 'maodo.niang.etu', 'serigne.cisse.etu', 'mugisha.nzakamwita.etu', 'antoine.hotin.etu', 'nayad.senaici.etu', 'kilian.graye.etu', 'amine.khadri.etu', 'guillaume.depelchin.etu', 'nolan.chevalier.etu', 'adame.chairi.etu', 'ibrahim.yahia.etu', 'koffi-john.evon.etu', 'dantoire-lalle.namoni.etu', 'ahmedzeidane.mohamedelmoctar.etu', 'momar.niang.etu', 'raphael.tafani.etu', 'kamal-deen-oloumide.savi.etu', 'alicia.zouadi.etu', 'nourou.diouf.etu', 'ivan.mbonjo.etu', 'samy.yahia-cherif.etu', 'jean-mayes.zitouni.etu', 'noa.gobaut.etu', 'mohamed-nazim.ait-kaci.etu', 'adam.oukzedou.etu', 'el-hadji-malick.gueye.etu', 'hadja-maimouna.balde.etu', 'abdelrahmane.bendjeladjel.etu', 'eya.yahyaoui.etu', 'imad.berhoum.etu']

print(f'only empty codestates in Tp5 for : {empty_codestate_students_tp5}')

# ## Ex d'utilisation pour l'ens des TPs

# Cette fonction prend du temps, j'ai mis des print pour suivre l'avancement.

# À noter :
#
# - un message bizarre dans le TP4 : ':235: SyntaxWarning: invalid decimal literal'
# - des messages indiquant qu'il doit y avoir un df vide dans pd.concat, mais je ne vois pas d'où ça viendrait.

df_tests, cannot_analyze_codestate_students, empty_codestate_students  = find_tests_for_all_tp_tpprog(df, PROG_FUNCTIONS_NAME_BY_TP)

# ## Sauvegarde des données

print(empty_codestate_students)

obtained_empty_codestate_students = {'Tp2': ['sami.boumiz.etu'], 'Tp3': ['hamza.chebbah.etu'], 'Tp4': ['ismail.nejjar.etu'], 'Tp5': ['ibrahima.sylla2.etu', 'julien.choquet.etu', 'imrane.mehenni.etu', 'mounir.achbad.etu', 'anaba.hilary-williams.etu'], 'Tp6': ['yasser.jad.etu', 'hugo.leleu.etu'], 'Tp7': ['louis.warembourg.etu', 'mohamed.trougouty.etu', 'thomas.desbuissons.etu'], 'Tp8': [], 'Tp9': ['mohamed.trougouty.etu']}

print(cannot_analyze_codestate_students)

obtained_cannot_analyze_codestate_students = {'Tp2': ['wail.ghouila.etu', 'kotchi-ange-gedeon.kama.etu', 'said.dahmani.etu', 'malick-ndiaye.kone.etu', 'clara.kombe.etu', 'oyawa.liza.etu'], 'Tp3': ['komi.dogbe.etu', 'wail.ghouila.etu', 'yves.djegnon.etu', 'abaly.oura.etu', 'massama.keita.etu', 'oyawa.liza.etu', 'eya.yahyaoui.etu'], 'Tp4': ['bilel.taieb.etu'], 'Tp5': ['anaelle.case.etu', 'boubacar.barry.etu', 'komivi.akpata.etu', 'sami.boumiz.etu', 'valentin.faust.etu', 'pedro-luis.lock-benites.etu', 'david.kahak.etu', 'nhungocanh.nguyen.etu', 'jacques-lazare.diatta.etu', 'florian.heyte.etu', 'edohson-arnaud.guedou.etu', 'abdoulaye.nguere.etu', 'enzo.dewez.etu', 'nassim.abbad.etu', 'hugo.vandewalle2.etu', 'faustine.descatoire.etu', 'yanis.kharchi.etu', 'louis.warembourg.etu', 'elyas.rabhiu.etu', 'dania.baroud.etu', 'lea.claire.etu', 'walid.farrash.etu', 'alpha-mahmoudou.diallo.etu', 'ruben.cassin.etu', 'mamadou.manga.etu', 'marion.le-guen.etu', 'yanis.nabet.etu', 'aurelien.bithorel.etu', 'ben-magloire.hoessi.etu', 'luc.duriez.etu', 'rosche-rostell.batchi-vouala.etu', 'elyes.guedria.etu', 'noe.le-van-canh-dit-ban.etu', 'bilel.taieb.etu', 'assia.mousselmal.etu', 'igor.belyaev.etu', 'thomas.desbuissons.etu', 'fawaaz.oyedotun.etu', 'ayao-landry-jeremie.dzossou-afanlete.etu', 'romane.deleau.etu', 'nadjib.zoubir.etu', 'shema.mugambira.etu', 'chaima.chakroun.etu', 'safa-khawthar.draouche.etu', 'kotchi-ange-gedeon.kama.etu', 'elliot.launay.etu', 'yanis.gannar.etu', 'sadia.muhammad.etu', 'aymeric.amblanc.etu', 'maodo.niang.etu', 'serigne.cisse.etu', 'mugisha.nzakamwita.etu', 'antoine.hotin.etu', 'nayad.senaici.etu', 'kilian.graye.etu', 'amine.khadri.etu', 'guillaume.depelchin.etu', 'nolan.chevalier.etu', 'adame.chairi.etu', 'ibrahim.yahia.etu', 'koffi-john.evon.etu', 'dantoire-lalle.namoni.etu', 'ahmedzeidane.mohamedelmoctar.etu', 'momar.niang.etu', 'raphael.tafani.etu', 'kamal-deen-oloumide.savi.etu', 'alicia.zouadi.etu', 'nourou.diouf.etu', 'ivan.mbonjo.etu', 'samy.yahia-cherif.etu', 'jean-mayes.zitouni.etu', 'noa.gobaut.etu', 'mohamed-nazim.ait-kaci.etu', 'adam.oukzedou.etu', 'el-hadji-malick.gueye.etu', 'hadja-maimouna.balde.etu', 'abdelrahmane.bendjeladjel.etu', 'eya.yahyaoui.etu', 'imad.berhoum.etu'], 'Tp6': ['serigne.cisse.etu'], 'Tp7': ['michael.tankeu-bigna.etu', 'mamadou-bachir.barry.etu', 'maodo.niang.etu', 'massama.keita.etu'], 'Tp8': ['naim.abdellaoui.etu', 'amadou.balde.etu', 'fadil.sani-labo.etu', 'ibrahima.sylla2.etu', 'grace-rochelde.louhanana.etu', 'igor.belyaev.etu', 'abaly.oura.etu', 'nadjib.zoubir.etu', 'matthieu.misiak.etu', 'sadia.muhammad.etu', 'tarik.amirat.etu', 'amine.khadri.etu', 'bilel.doggui.etu', 'lino.mallevaey.etu', 'adam.oukzedou.etu'], 'Tp9': ['abaly.oura.etu', 'amine.khadri.etu', 'ahmedzeidane.mohamedelmoctar.etu', 'hajar.zeaiter.etu']}

print(df_tests)

io_utils.write_csv(df_tests,INTERIM_DATA_DIR, 'test_number_old_phase2')


# # Fonctions pour chercher si les tests trouvés apparaissent dans un Run.Test

# Repiqué du notebook 6.Analyze de Sana

# +
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
# -

# Ce dataframe est construit à partir des "tests" de Run.Test non vides slt.

df_of_column_test

df_of_column_test.columns


def nom_fonction(name:str) -> str:
    '''
    Renvoie le nom de la fonction sans les arguments
    '''
    return name.split('(')[0]


nom_fonction('compare(nb1, nb2)')

df_of_column_test['name'] =  df_of_column_test['name'].apply(nom_fonction)

df_of_column_test[df_of_column_test['status']==False]


# À tester avec 'willy.nguyen.etu' et les données plus bas

def index_last_RunTest(actor:str, df:pd.DataFrame, filename_infere:str, df_of_column_test:pd.DataFrame) -> int:
    '''
    Returns the index of the most recent Run.Test of actor, limited to df and filename_infere.
    '''
    df_RunTest = df[(df['verb']=='Run.Test') & ((df['actor']==actor) | (df['binome']==actor)) & (df['filename_infere']==filename_infere)]
    timestamps = df_RunTest['timestamp.$date'].copy() # pour être sûre de ne pas modifier le df initial
    found = False # found Run.Test which can be exploited
    while not timestamps.empty and not found: 
        index_of_timestamp_max_RunTest = timestamps.idxmax()
        #print('index_of_timestamp_max_RunTest', index_of_timestamp_max_RunTest)
        #input('avancer')
        if index_of_timestamp_max_RunTest in df_of_column_test['original_index']:
            found = True # timestamp_max_RunTest
        else:
            # passer à un timestamp antérieur
            timestamps = timestamps.drop(index=[index_of_timestamp_max_RunTest])
    if found:
        return index_of_timestamp_max_RunTest
    else:
        return None


indexes_codestates_df_tests_tp2 = df_tests_tp2['index'].unique()

df_action_df_tests_tp2 = df.loc[indexes_codestates_df_tests_tp2]

df_action_df_tests_tp2.verb.unique()

len(df_action_df_tests_tp2[df_action_df_tests_tp2['verb'] == 'File.Open']) # risque d'être problématique ?

len(df_action_df_tests_tp2[df_action_df_tests_tp2['verb'] == 'Run.Test'])

len(df_action_df_tests_tp2[df_action_df_tests_tp2['verb'] == 'File.Save'])

len(df_action_df_tests_tp2[df_action_df_tests_tp2['verb'] == 'Run.Program'])

len(df_action_df_tests_tp2[df_action_df_tests_tp2['verb']=='File.Save'])

# Essai avec un étudiant dont le codestate qui contient les tests correspond à un Run.TEst, mais File.save

df_tp2_y, cannot_analyze_codestate_y_tp2, empty_codestate_y_tp2 = find_tests_for_tp_tpprog_name('yanko.lemoine.etu', df, 'Tp2', PROG_FUNCTIONS_NAME_BY_TP)

df_tp2_y # son index correspond à un Run.Test

cannot_analyze_codestate_y_tp2

empty_codestate_y_tp2

index_yanko = index_last_RunTest('yanko.lemoine.etu', df, 'fonctions.py', df_of_column_test)
index_yanko

# Essai avec un étudiant dont le codestate qui contient les tests ne correspond pas à un Run.TEst, mais un File.Save

df[(df['actor']=='willy.nguyen.etu') & (df['filename_infere'] == 'fonctions.py')][0:20]

# Pour cet étudiant le codeState qui a permis de trouver les tests écrits est un File.Save d'index 284498. Le Run.Test le plus proche en remontant le temps est à l'index 284495.

df_tests_tp2[df_tests_tp2['actor']=='willy.nguyen.etu']

index_wng = index_last_RunTest('willy.nguyen.etu', df, 'fonctions.py', df_of_column_test)
index_wng # ça marche ! C'est celui que je trouve à la main

# Essai avec un étudiant dont le codeState est un File.Open d'index 142828 et à la main son dernier Run.Test est d'index 142585

df_action_df_tests_tp2[df_action_df_tests_tp2['verb']=='File.Open']

df_tests_tp2[df_tests_tp2['actor']=='keba.thiam.etu']

df.loc[142828]

df[(df['actor']=='keba.thiam.etu') & (df['filename_infere'] == 'fonctions.py')][-20:]

df.loc[142585]

index_kt = index_last_RunTest('keba.thiam.etu', df, 'fonctions.py', df_of_column_test)
index_kt # C'est le bon !

df_of_column_test[df_of_column_test['original_index']==142585]

df_of_column_test_kt = df_of_column_test[df_of_column_test['original_index']==142585]

df_runTest_kt_tests_number= pd.DataFrame(columns=['function_name', 'tests_number'])
for name in df_of_column_test_kt['name'].unique():
    function_df = pd.DataFrame({'function_name' : [name], 'tests_number' : df_of_column_test_kt.groupby(['name'])['name'].count()[name]})
    df_runTest_kt_tests_number = pd.concat([df_runTest_kt_tests_number, function_df], ignore_index=True)
df_runTest_kt_tests_number

df_of_column_test_wng = df_of_column_test[df_of_column_test['original_index']==284495]

df_of_column_test_wng_tests= pd.DataFrame(columns=['function_name', 'tests_number'])
for name in df_of_column_test_wng['name'].unique():
    function_df = pd.DataFrame({'function_name' : [name], 'tests_number' : df_of_column_test_wng.groupby(['name'])['name'].count()[name]})
    df_of_column_test_wng_tests = pd.concat([df_of_column_test_wng_tests, function_df], ignore_index=True)
df_of_column_test_wng_tests

# Il reste à extraire les name qui apparaissent dans le df_tests de l'étudiant et de faire un equls sur les DataFrame ?

df_tests_tp2_kt_nb_strict_pos = df_tests_tp2[(df_tests_tp2['actor']=='keba.thiam.etu') & (df_tests_tp2['tests_number']>0)][['function_name', 'tests_number']]
df_tests_tp2_kt_nb_strict_pos

df_tests_tp2_strict_pos = df_tests_tp2_kt_nb_strict_pos
df_tests_tp2_strict_pos

df_run_tests_tp2 = df_of_column_test_kt_tests
df_run_tests_tp2

for ind, val in df_run_tests_tp2.iterrows():
    print(val['function_name'], '/', val['tests_number'])

type(df_run_tests_tp2.loc[df_run_tests_tp2['function_name']=='repetition']['tests_number'].values[0])

'repetition' in df_run_tests_tp2.function_name.values

df_run_tests_tp2['function_name']

# À vérifier : df_tests_tp2_strict_pos est "inclus" dans  df_run_tests_tp2

ok = True
for ind, val in df_tests_tp2_strict_pos.iterrows():
    func_name = val['function_name']
    if func_name not in df_run_tests_tp2.function_name.values:
        ok = False
    else:
        tests_number_ecrits = val['tests_number']
        tests_number_runTest = df_run_tests_tp2.loc[df_run_tests_tp2['function_name']==func_name]['tests_number'].values[0]
        if tests_number_ecrits < tests_number_runTest:
            ok = False
ok


# à revoir pour garder trace en plus du booléen du contenu du Run.Test et des tests écrits nettoyés.

def tests_executes_pour_tests_ecrits(actor:str, df: pd.DataFrame, df_tests_ecrits_filename:pd.DataFrame, df_of_column_test:pd.DataFrame, filename:str) -> bool:
    '''
    Cherche le Run.Test le plus récent dans df pour actor.
    Renvoie True ssi les fonctions qui ont n tests écrits ont au moins n tests exécutés dans le Run.Test.
    Args:
        df_tests_ecrits_tp : les tests écrits pour le codeState le plus récent dans df pour le même filename.

    '''
    index_runTest_in_df = index_last_RunTest(actor, df, filename, df_of_column_test)
    if index_runTest_in_df == None:
        return (False, None, None, None)
    # count test numbers in runTest : df_runTest_tests_number
    df_of_column_test_actor = df_of_column_test[df_of_column_test['original_index']==index_runTest_in_df]
    df_runTest_tests_number= pd.DataFrame(columns=['function_name', 'tests_number'])
    for name in df_of_column_test_actor['name'].unique():
        # on peut sûrement faire plus élégant
        function_df = pd.DataFrame({'function_name' : [name], 'tests_number' : df_of_column_test_actor.groupby(['name'])['name'].count()[name]})
        df_runTest_tests_number = pd.concat([df_runTest_tests_number, function_df], ignore_index=True)
    # keep only > 0 number of tests in df_tests_ecrits_tp : df_tests_ecrits_tp_strict_pos
    df_tests_ecrits_filename_strict_pos = df_tests_ecrits_filename[(df_tests_ecrits_filename['actor']==actor) & (df_tests_ecrits_filename['tests_number']>0)][['function_name', 'tests_number']]
    # on vérifie que, pour chaque fonction de df_tests_ecrits_tp_strict_pos
    # - la fonction apparaît dans df_runTest_tests_number
    # - le nb de tests y est égal ou supérieur
    for ind, val in df_tests_ecrits_filename_strict_pos.iterrows():
        func_name = val['function_name']
        if func_name not in df_runTest_tests_number.function_name.values:
            return (False, index_runTest_in_df, df_runTest_tests_number, df_tests_ecrits_filename_strict_pos)
        else:
            tests_number_ecrits = val['tests_number']
            # on peut sûrement faire plus élégant
            tests_number_runTest = df_runTest_tests_number.loc[df_runTest_tests_number['function_name']==func_name]['tests_number'].values[0]
            if tests_number_ecrits < tests_number_runTest:
                return (False, index_runTest_in_df, df_runTest_tests_number, df_tests_ecrits_filename_strict_pos)
    return (True, index_runTest_in_df,  df_runTest_tests_number, df_tests_ecrits_filename_strict_pos)


df_tp2_try, cannot_analyze_codestate_y_try, empty_codestate_y_try = find_tests_for_tp_tpprog(df, 'Tp2', PROG_FUNCTIONS_NAME_BY_TP, filename=PROG_FILENAMES_BY_TP['Tp2'])

tests_executes_pour_tests_ecrits('yanko.lemoine.etu', df, df_tp2_try, df_of_column_test,filename=PROG_FILENAMES_BY_TP['Tp2'] )[0]

tests_executes_pour_tests_ecrits('willy.nguyen.etu',  df, df_tp2_try, df_of_column_test,filename=PROG_FILENAMES_BY_TP['Tp2'] )[0]


tests_executes_pour_tests_ecrits('keba.thiam.etu',   df, df_tp2_try, df_of_column_test,filename=PROG_FILENAMES_BY_TP['Tp2'] )[0]

actor_column_tp2_tests_ecrits  = df_tp2_try['actor'].unique()
df_tests_ecrits_executes_tp2 = pd.DataFrame(columns=['actor', 'tests_ecrits_executes'])
for student in actor_column_tp2_tests_ecrits:
    res_bool, index_runTest_in_df,  df_runTest_tests_number, df_tests_ecrits_filename_strict_pos = tests_executes_pour_tests_ecrits(student, df, df_tp2_try, df_of_column_test, filename=PROG_FILENAMES_BY_TP['Tp2'] )
    petit_df = pd.DataFrame({'actor':[student], 'tests_ecrits_executes':res_bool})
    df_tests_ecrits_executes_tp2 = pd.concat([df_tests_ecrits_executes_tp2, petit_df], ignore_index=True )


df_tests_ecrits_executes_tp2

len(df_tests_ecrits_executes_tp2)

len(df_tests_ecrits_executes_tp2[df_tests_ecrits_executes_tp2['tests_ecrits_executes']==False])

31/210*100



# ## Analyses intéressantes à faire

# Faire les plus facile en premier, je ne me rends pas compte de la difficulté. Tout est bon à prendre. Je ne sais pas s'il faut faire les analyses par TP ou sur tout le semestre.

# Possible regarder 
#
# - l'ens des actors qui n'ont écrit aucun test (sur un TP / sur tous les TPs) :  pour eux la somme des tests_number vaut 0
# - l'ens actors qui ont des tests pour chaque fonction (sur un TP / sur tous les TPs) : pour eux il n'y a aucun tests_number à 0
# - en théorie ceux qui restent écrivent parfois des tests, parfois non.

# Pour ceux qui écrivent parfois des tests, intéressant de voir si chronologiquement :
#
# - ils écrivaient des tests dans les premiers TP et ils ont arrêté
# - ou au contraire ils n'en écrivaient pas et ils s'y sont mis
#
# Mais ça doit être compliqué à calculer, dc laisser tomber au début.

# La corrélation avec le fait d'exécuter ou non des Run.Test est intéressante aussi.
#
# - si un actor écrit des tests, le comportement attendu est qu'il les exécute : pour chaque fonction avec des tests il devrait y avoir au moins un Run.Test avec la valeur `tests` contenant cette fonction. Si tu peux calculer ça, ça a de la valeur. Ça montre que les étudiants ont compris qu'un test, ça s'exécute.
# -  si un actor n'écrit aucun test, il ne devrait pas faire de Run.Test non plus. La présence de Run.Test avec la valeur `tests` vide indique un comportemet bizarre (ou que le nettoyage a encore des lacunes...). 

# # Fonctions pour analyser les TP_Game

# Cette fois on compte les tests dans l'ensemble du module/codeState, on ne compte pas les tests par fonction (mélange de fonctions testables et non testables).
#

# Pour chaque étudiant on regarde les différents jeux sur lesquels il a travaillé, au travers des différents filename_infere. 
#

# Pour trouver le codeState on procède comme pour les TP2 à 9 en cherchant le codeState qui a le timestamp le plus récent, et on continue tant qu'on n'a pas trouvé un codeState analysable et contenant des tests. Si aucun codeState n'est analysable, on renvoie None. Par contre : si aucune codeState ne contient de tests, on indique bien qu'il y a 0 tests. 

# En cours de route je n'ai eu ni le temps ni l'envie de gérer les cannot_analyze_codestate et empty_codestate. 

# Cette constante est dans variable_constantes_2425 mais je n'ai aps redémarré le serveur...

FILENAME_TP_GAME = ["tictactoe.py", "puissance4.py", "jeu_2048.py", "binairo.py", "tectonic.py"]#, "galaxies.py"]


def count_tests_in_codestate(source:str) -> int:
    '''
    Returns the number of tests found in `source`, or None. 

    Args:
        source is some codestate

    Returns:
        the number of tests in source or None if `source` couldn't be parsed.
    '''
    counter = 0
    finder = L1TestFinder(source=source)
    try:
        res = finder.find_l1doctests()
        for ex_func in res:
            counter = counter + len(ex_func.get_examples())
    except (ValueError, SyntaxError, SpaceMissingAfterPromptException, AttributeError) as e: 
        # AttributeError levé par thonnycontrib/utils.py
        # AttributeError: 'Attribute' object has no attribute 'id'
        counter = None
    return counter


def find_tests_for_tp_tpgame_name_filename(name:str, df:pd.DataFrame, filename_tpgame:str) -> tuple[pd.DataFrame, bool, bool]:
    """
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for `name` and `filename_tpgame`, then looks repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

    - a DataFrame with columns 'actor', 'tp', 'filename_infere', 'tests_number' (int or None if not present in codestates), 'index' (index in df of the analyzed codeState)
    - a first bool, True if for that student the codeStates cannot be analyzed (Python or l1test syntax error) 
    - a second bool, True if for that student and that filename no codeState was found, or only empty codeStates

    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        name: some actor (ex : 'truc.machin.etu')
        df: some DataFrame
        filename_tpgame: some filename (for a game ex : 'binairo.py')
        
    Returns:
        None, False, True: if no codeState was found, or only empty codeStates
        None, True, False: if no codeState could be parsed
        df, False, False: if some codeState could be parsed
    
    """
    # Les timestamps ne sont pas triés par ordre croissant.
    # La fonction recherche les codeState comme suit : 
    # - elle cherche le codestate le plus récent,
    # - s'il est analysable, on regarde s'il y a des tests, ou 0
    # - s'il n'est pas analysable ou si 0 test est trouvé, elle cherche à nouveau le codestate le plus récent, moins le précédent, mais
    # on garde en mémoire qu'on avait trouvé 0 test.
    # Et ce tant qu'il y a des codestate à traiter.
    df_name_tp = df[ (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == filename_tpgame)& ((df['actor'] == name) | (df['binome'] == name))]
    df_codestate_nonempty = df_name_tp[df_name_tp['codeState'] != '']
    if len(df_codestate_nonempty) == 0:
            return None, False, True
    else:
        # look for most recent parsable codeState
        timestamps = df_codestate_nonempty['timestamp.$date'].copy() # pour être sûre de ne pas modifier le df initial
        found = False # found codeState with functions not all unfoundable
        found_0_test = False
        while not timestamps.empty and not found: 
            index_of_timestamp_max = timestamps.idxmax()
            most_recent_codeState = df_name_tp.loc[index_of_timestamp_max]['codeState']
            nb_tests = count_tests_in_codestate(most_recent_codeState)
            if nb_tests != None: # parseable
                if nb_tests > 0: # tests in codeState
                    found = True
                    #print(f'actor {name} filename_infere {filename_tpgame} tests_number {nb_tests} index {index_of_timestamp_max}')
                    df_result = pd.DataFrame({'actor': [name], 'tp': ['Tp_GAME'], 'filename_infere': [filename_tpgame], \
                                          'tests_number': [nb_tests], 'index':  [index_of_timestamp_max]})
                else: # look for some tests in another codeState, but remember we found 0 test
                    found_0_test = True
                    df_result = pd.DataFrame({'actor': [name], 'tp': ['Tp_GAME'], 'filename_infere': [filename_tpgame], \
                                          'tests_number': [0], 'index':  [index_of_timestamp_max]})
                    timestamps = timestamps.drop(index=[index_of_timestamp_max])
            else: # codestate not parsable : drop this index and continue
                timestamps = timestamps.drop(index=[index_of_timestamp_max])
        if found or found_0_test:
            return df_result, False, False
        else:
            return None, True, False


# à finir pour trouver le df du nb tests d'un jeu
def find_tests_for_tp_tpgame_game(game:str, df:pd.DataFrame) -> pd.DataFrame:
    """
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for `game`, looking repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

    - a DataFrame with columns 'actor', 'tp', 'filename_infere', 'tests_number' (int or None if not present in codestates), 'index' (index in df of the analyzed codeState)
 
    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        game: some game (ex : 'puissance4.py')
        df: some DataFrame        
    Returns:
        None if no tp_game & tp_prog codestate could be found or analyzed.
    
    """
    df_game_tp = df[(df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == game)]
    actor_column_game  = df_game_tp['actor']
    column_binome_game = df_game_tp['binome']
    all_students_game  = set(actor_column_game).union(set(column_binome_game))
    if '' in all_students_game:
        all_students_game.remove('')

    df_result = pd.DataFrame(columns=['actor', 	'tp', 	'filename_infere', 	'tests_number', 	'index'])
    for name in all_students_game:
            df_filename, cannot_analyze_codestate, empty_codestate =  find_tests_for_tp_tpgame_name_filename(name, df, game)
            if df_filename is not None:
                df_result = pd.concat([df_result, df_filename], ignore_index=True)
    return df_result


def find_tests_for_tp_tpgame_name(name:str, df:pd.DataFrame) -> pd.DataFrame:
    """
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for `name` and all filename_infere we can find for `name`, then looks repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

    - a DataFrame with columns 'actor', 'tp', 'filename_infere', 'tests_number' (int or None if not present in codestates), 'index' (index in df of the analyzed codeState)
 
    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        name: some actor (ex : 'truc.machin.etu')
        df: some DataFrame        
    Returns:
        None if no tp_game & tp_prog codestate could be found or analyzed.
    
    """
    df_name_tp = df[(df['Type_TP'] == 'TP_prog') & ((df['actor'] == name) | (df['binome'] == name))]
    df_codestate_nonempty = df_name_tp[df_name_tp['codeState'] != '']
    if len(df_codestate_nonempty) == 0:
            return None
    else:
        df_result = pd.DataFrame(columns=['actor', 	'tp', 	'filename_infere', 	'tests_number', 	'index'])
        tpgame_filenames_infere_all = df_codestate_nonempty['filename_infere'].unique()
        tpgame_filenames = list(f for f in tpgame_filenames_infere_all if f in FILENAME_TP_GAME)
        if len(tpgame_filenames) == 0:
            return None
        for filename in tpgame_filenames:
            df_filename, cannot_analyze_codestate, empty_codestate =  find_tests_for_tp_tpgame_name_filename(name, df, filename)
            if df_filename is not None:
                df_result = pd.concat([df_result, df_filename], ignore_index=True)
        return df_result


def find_tests_for_tp_tpgame(df:pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for all students and all filename_infere we can find for `name`, then looks repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

     - a DataFrame with columns 'actor', 'tp', 'filename_infere', 'tests_number' (int or None if not present in codestates), 'index' (index in df of the analyzed codeState)
     - a list of actors for which no data could be collected - they do not appear in the returned dataframe
     
    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        df: some DataFrame
    """
    cannot_find_or_analyze_tpgame = []
    df_result = pd.DataFrame(columns=['actor', 	'tp', 	'filename_infere', 	'tests_number', 	'index'])
    actor_column_game  = df[(df['TP'] == 'Tp_GAME') & (df['Type_TP'] == 'TP_prog')]['actor']
    column_binome_game = df[(df['TP'] == 'Tp_GAME') & (df['Type_TP'] == 'TP_prog')]['binome']
    all_students_game  = set(actor_column_game).union(set(column_binome_game))
    if '' in all_students_game:
        all_students_game.remove('')
    for name in all_students_game:
        df_name = find_tests_for_tp_tpgame_name(name, df)
        if df_name is None:
            cannot_find_or_analyze_tpgame.append(name)
        else:
            df_result = pd.concat([df_result, df_name], ignore_index=True)
    return df_result, cannot_find_or_analyze_tpgame


# + [markdown] jp-MarkdownHeadingCollapsed=true
# ## Ex d'utilisation
# -

df_count_tests_yanko_tictactoe, cannot_analyze_codestate_yanko, empty_codestate_yanko =  find_tests_for_tp_tpgame_name_filename('yanko.lemoine.etu', df, 'tictactoe.py')

df_count_tests_yanko_tictactoe

df_count_tests_yanko_all_games = find_tests_for_tp_tpgame_name('yanko.lemoine.etu', df)

df_count_tests_yanko_all_games

# Long mais pas d'affichage.

df_tests_tpgame_all, cannot_find_or_analyze_tpgame = find_tests_for_tp_tpgame(df)

cannot_find_or_analyze_tpgame

df_tests_tpgame_all

# ## Analyses intéressantes à faire

# Possible regarder
#
#     l'ens des actors qui n'ont écrit aucun test (sur un jeu / sur tous les jeux) : pour eux la somme des tests_number vaut 0
#     l'ens actors qui ont des tests (sur un jeu / sur tous les jeux) : pour eux il n'y a aucun tests_number à 0
#     en théorie ceux qui restent écrivent parfois des tests, parfois non.
#
# Mais je me rappelle que yanko a juste ouvert le fichier pour les galaxies, et il n'a pas codé ce jeu car il commençait à en avoir marre. Quand je compte les tests d'un codeState je renvoie None si le codeState n'est pas analysable, j'aurais plutôt dû lever une exception, et lever une autre exception quand il n'y a pas de fonctions ds le codeState. Si cet étudiant est le seul à avoir avoir des traces sur "galaxies.py", peut-être enlever ce jeu de l'analyse ?

df_tests_tpgame_all[df_tests_tpgame_all['filename_infere'] == 'galaxies.py']

# -> enlever 'galaxies.py' de FILENAME_TP_GAME

# Ensuite : 
#
# - pour les étudiants qui ont fait 0 tests, regarder s'ils faisaient des tests sur les TP2 à TP9 ou s'ils n'en faisaient déjà pas.
# - pour les étudiants qui ont fait des tests sur les TP2 à TP9, regarder si on trouve au moins un jeu avec tests
# - (je viens de dire 2 fois la même chose, à faire ds le sens que tu préfères)
#
# Ça me permettra d'évaluer si les étudiants qui testent ont pris l'habitude de le faire (ils testent quand on leur demande de le faire pdt les TP2 à 9 mais ils oublient ou n'y arrivent pas ensuite, ds le jeu libre).

# De même corrélation possible avec les Run.Test, sauf si ça n'apporte rien par rapport aux TP2 à 9.
#
# Je me rappelle qu'il y avait un grand nombre (21) d'étudiants avec des `tests` de Run.Test vides pour les Tp_Game. Si c'est tjs le cas avec le nouveau nettoyage il faut essayer de comprendre pourquoi.

# # Essai analyse TP2 à TP9

# ## Brouillonnage

# Les étudiants qui n'ont écrit aucun test. 

df_tests_tp2[df_tests_tp2['tests_number']==0]

# Avec sum ça marche mais je ne suis jamais sûre du traitement des valeurs NaN.

# Je n'ai pas trop compris comment faire all(fonction). J'ai donc salement rajouté des colonnes. Le rajout de colonne déclenche un warning
# que je n'ai pas réussi à supprimer.

dict_essai = {'actor' : ['tous', 'tous', 'tous', 'aucun', 'aucun', 'aucun', 'mixte', 'mixte', 'mixte', 'tous1', 'tous1', 'tous1', 'mixte1', 'mixte1', 'mixte1', 'aucun1', 'aucun1', 'aucun1'], \
              'tests_number' : [2, 3, None, 0, None, 0, 1, None, 0, 5, 6, 2, 1, None, 0, 0, 0, 0]}
df_essai = pd.DataFrame(dict_essai)

df_essai

df_essai_copy = df_essai.copy()
df_essai_values = df_essai_copy[pd.notna(df_essai_copy['tests_number'])]
df_essai_values


df_essai_values['tests_number_nul'] = df_essai_values['tests_number'].map(lambda x : x == 0)
df_essai_values['tests_number_not_nul'] = df_essai_values['tests_number'].map(lambda x : x > 0)
df_essai_values


df_essai_avec_0_tests_interm = df_essai_values.groupby(['actor']).tests_number_nul.all()
df_essai_avec_0_tests = df_essai_avec_0_tests_interm[df_essai_avec_0_tests_interm==True]

df_essai_avec_0_tests_interm

list(df_essai_avec_0_tests.index)

df_essai_avec_tous_tests_interm = df_essai_values.groupby(['actor']).tests_number_not_nul.all()
df_essai_avec_tous_tests = df_essai_avec_tous_tests_interm[df_essai_avec_tous_tests_interm==True]

list(df_essai_avec_tous_tests.index)

df_essai_qq_tests_interm = df_essai_values.groupby(['actor']).tests_number_not_nul.any()

df_essai_qq_tests = df_essai_qq_tests_interm[df_essai_qq_tests_interm==True]

set(df_essai_qq_tests.index).difference(set(df_essai_avec_tous_tests.index))

df_tests_tp2_sans_nan = df_tests_tp2.copy()
df_tests_tp2_sans_nan = df_tests_tp2_sans_nan[pd.notna(df_tests_tp2_sans_nan['tests_number'])]
df_tests_tp2_sans_nan

df_tests_tp2_sans_nan['tests_number_nul'] = df_tests_tp2_sans_nan['tests_number'].map(lambda x : x == 0)
df_tests_tp2_sans_nan['tests_number_not_nul'] = df_tests_tp2_sans_nan['tests_number'].map(lambda x : x > 0)
df_tests_tp2_sans_nan

df_tp2_avec_0_tests_interm = df_tests_tp2_sans_nan.groupby(['actor']).tests_number_nul.all()
df_tp2_avec_0_tests = df_tp2_avec_0_tests_interm[df_tp2_avec_0_tests_interm==True]
list(df_tp2_avec_0_tests.index)

df_tp2_avec_tous_tests_interm = df_tests_tp2_sans_nan.groupby(['actor']).tests_number_not_nul.all()
df_tp2_avec_tous_tests = df_tp2_avec_tous_tests_interm[df_tp2_avec_tous_tests_interm==True]
list(df_tp2_avec_tous_tests.index)

df_tests_tp2[df_tests_tp2['actor'] == 'koffi.gantchou.etu']

df_tests_tp2[df_tests_tp2['actor'] == 'bilal.ouazize.etu']

df.loc[48079].codeState

df_tests_tp2[df_tests_tp2['actor'] == 'candice.billerait.etu']

df.loc[53966][['actor', 'verb', 'codeState']]

print(df.loc[53966]['codeState'])

# Cet étudiant a bcp de 0, il a une seule fonction testée

df.loc[79458]['codeState']


# ## Fonctions pour analyse des TPs - nombre de tests écrits

def actors_par_pratique_ecriture_tests(df_tests_number:pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    '''
    Renvoie 
        - la liste des étudiants ayant testé toutes les fonctions qu'ils ont écrites
        - la liste des étudiants n'ayant testé aucune fonction qu'ils ont écrite
        - la liste des étudiants qui ont testé au moins une fonction mais pas toutes les fonctions 

    Args:
        df_tests_number : dataframe avec colonnes actor et tests_number issu d'un appel à find_tests_xxxx
    '''
    df_tests_number_sans_nan = df_tests_number.copy() # au cas où
    df_tests_number_sans_nan = df_tests_number_sans_nan[pd.notna(df_tests_number_sans_nan['tests_number'])]
    df_tests_number_sans_nan['tests_number_nul'] = df_tests_number_sans_nan['tests_number'].map(lambda x : x == 0)
    df_tests_number_sans_nan['tests_number_not_nul'] = df_tests_number_sans_nan['tests_number'].map(lambda x : x > 0)
    # etud qui testent toutes les fonctions écrites
    df_tests_number_avec_tous_tests_interm = df_tests_number_sans_nan.groupby(['actor']).tests_number_not_nul.all()
    df_tests_number_avec_tous_tests = df_tests_number_avec_tous_tests_interm[df_tests_number_avec_tous_tests_interm==True]
    # etud qui ne testent aucune fonction écrite
    df_tests_number_avec_0_test_interm = df_tests_number_sans_nan.groupby(['actor']).tests_number_nul.all()
    df_tests_number_avec_0_test = df_tests_number_avec_0_test_interm[df_tests_number_avec_0_test_interm==True]
    # etud qui testent qq fonctions mais pas toutes
    df_tests_numbers_qq_tests_interm = df_tests_number_sans_nan.groupby(['actor']).tests_number_not_nul.any()
    df_tests_numbers_qq_tests = df_tests_numbers_qq_tests_interm[df_tests_numbers_qq_tests_interm==True]
    actors_qq_tests = set(df_tests_numbers_qq_tests.index).difference(set(df_tests_number_avec_tous_tests.index))
    assert len(list(df_tests_number_avec_tous_tests.index)) + len(list(df_tests_number_avec_0_test.index)) + len(actors_qq_tests) == len(df_tests_number.actor.unique())
    return list(df_tests_number_avec_tous_tests.index), list(df_tests_number_avec_0_test.index), actors_qq_tests


df_tests_tp2_bis, cannot_analyze_codestate_students_tp2_bis, empty_codestate_students_tp2_bis  = find_tests_for_tp_tpprog(df, 'Tp2', PROG_FUNCTIONS_NAME_BY_TP, filename=PROG_FILENAMES_BY_TP['Tp2'])

etud_testant_toute_fonction_ecrite_tp2_bis, etud_testant_aucune_fonction_ecrite_tp2_bis, etud_qq_tests_fonction_ecrite_tp2_bis = actors_par_pratique_ecriture_tests(df_tests_tp2_bis)

len(etud_testant_toute_fonction_ecrite_tp2_bis)

etud_testant_toute_fonction_ecrite_tp2, etud_testant_aucune_fonction_ecrite_tp2, etud_qq_tests_fonction_ecrite_tp2 = actors_par_pratique_ecriture_tests(df_tests_tp2)

len(etud_testant_toute_fonction_ecrite_tp2)

len(etud_testant_aucune_fonction_ecrite_tp2)

len(etud_qq_tests_fonction_ecrite_tp2)

df_tests_tp3_bis, cannot_analyze_codestate_students_tp3_bis, empty_codestate_students_tp3_bis  = find_tests_for_tp_tpprog(df, 'Tp3', PROG_FUNCTIONS_NAME_BY_TP,  filename=PROG_FILENAMES_BY_TP['Tp3'])

etud_testant_toute_fonction_ecrite_tp3_bis, etud_testant_aucune_fonction_ecrite_tp3_bis, etud_qq_tests_fonction_ecrite_tp3_bis = actors_par_pratique_ecriture_tests(df_tests_tp3_bis)

len(etud_testant_toute_fonction_ecrite_tp3_bis)

df_tests_tp3, cannot_analyze_codestate_students_tp3, empty_codestate_students_tp3  = find_tests_for_tp_tpprog(df, 'Tp3', PROG_FUNCTIONS_NAME_BY_TP)

print(f'Cannot analyze codestate in Tp3 for : {cannot_analyze_codestate_students_tp3}')
print(f'only empty codestates in Tp3 for : {empty_codestate_students_tp3}')

etud_testant_toute_fonction_ecrite_tp3, etud_testant_aucune_fonction_ecrite_tp3, etud_qq_tests_fonction_ecrite_tp3 = actors_par_pratique_ecriture_tests(df_tests_tp3)

len(etud_testant_toute_fonction_ecrite_tp3)

len(etud_testant_aucune_fonction_ecrite_tp3)

len(etud_qq_tests_fonction_ecrite_tp3)

178 + 11 + 31

df_tests_tp4_bis, cannot_analyze_codestate_students_tp4_bis, empty_codestate_students_tp4_bis  = find_tests_for_tp_tpprog(df, 'Tp4', PROG_FUNCTIONS_NAME_BY_TP,  filename=PROG_FILENAMES_BY_TP['Tp4'])

etud_testant_toute_fonction_ecrite_tp4_bis, etud_testant_aucune_fonction_ecrite_tp4_bis, etud_qq_tests_fonction_ecrite_tp4_bis = actors_par_pratique_ecriture_tests(df_tests_tp4_bis)

len(etud_testant_toute_fonction_ecrite_tp4_bis)

df_tests_tp4, cannot_analyze_codestate_students_tp4, empty_codestate_students_tp4  = find_tests_for_tp_tpprog(df, 'Tp4', PROG_FUNCTIONS_NAME_BY_TP)

print(f'Cannot analyze codestate in Tp4 for : {cannot_analyze_codestate_students_tp4}')
print(f'only empty codestates in Tp4 for : {empty_codestate_students_tp4}')

etud_testant_toute_fonction_ecrite_tp4, etud_testant_aucune_fonction_ecrite_tp4, etud_qq_tests_fonction_ecrite_tp4 = actors_par_pratique_ecriture_tests(df_tests_tp4)

len(etud_testant_toute_fonction_ecrite_tp4)

len(etud_testant_aucune_fonction_ecrite_tp4)

len(etud_qq_tests_fonction_ecrite_tp4)

len(etud_testant_toute_fonction_ecrite_tp4) + len(etud_testant_aucune_fonction_ecrite_tp4) + len(etud_qq_tests_fonction_ecrite_tp4)

df_tests_tp6_bis, cannot_analyze_codestate_students_tp6_bis, empty_codestate_students_tp6_bis  = find_tests_for_tp_tpprog(df, 'Tp6', PROG_FUNCTIONS_NAME_BY_TP,  filename=PROG_FILENAMES_BY_TP['Tp6'])

etud_testant_toute_fonction_ecrite_tp6_bis, etud_testant_aucune_fonction_ecrite_tp6_bis, etud_qq_tests_fonction_ecrite_tp6_bis = actors_par_pratique_ecriture_tests(df_tests_tp6_bis)

len(etud_testant_toute_fonction_ecrite_tp6_bis)

df_tests_tp6, cannot_analyze_codestate_students_tp6, empty_codestate_students_tp6  = find_tests_for_tp_tpprog(df, 'Tp6', PROG_FUNCTIONS_NAME_BY_TP)

print(f'Cannot analyze codestate in Tp6 for : {cannot_analyze_codestate_students_tp6}')
print(f'only empty codestates in Tp6 for : {empty_codestate_students_tp6}')

etud_testant_toute_fonction_ecrite_tp6, etud_testant_aucune_fonction_ecrite_tp6, etud_qq_tests_fonction_ecrite_tp6 = actors_par_pratique_ecriture_tests(df_tests_tp6)

len(etud_testant_toute_fonction_ecrite_tp6)

len(etud_testant_aucune_fonction_ecrite_tp6)

len(etud_qq_tests_fonction_ecrite_tp6)

len(etud_testant_toute_fonction_ecrite_tp6) + len(etud_testant_aucune_fonction_ecrite_tp6) + len(etud_qq_tests_fonction_ecrite_tp6)

df_tests_tp7, cannot_analyze_codestate_students_tp7, empty_codestate_students_tp7  = find_tests_for_tp_tpprog(df, 'Tp7', PROG_FUNCTIONS_NAME_BY_TP)

print(f'Cannot analyze codestate in Tp7 for : {cannot_analyze_codestate_students_tp7}')
print(f'only empty codestates in Tp7 for : {empty_codestate_students_tp7}')

etud_testant_toute_fonction_ecrite_tp7, etud_testant_aucune_fonction_ecrite_tp7, etud_qq_tests_fonction_ecrite_tp7 = actors_par_pratique_ecriture_tests(df_tests_tp7)

len(etud_testant_toute_fonction_ecrite_tp7)

len(etud_testant_aucune_fonction_ecrite_tp7)

len(etud_qq_tests_fonction_ecrite_tp7)

len(etud_testant_toute_fonction_ecrite_tp7) + len(etud_testant_aucune_fonction_ecrite_tp7) + len(etud_qq_tests_fonction_ecrite_tp7)

188/216*100

# Pour le TP8 on obtient des résultats très bas, mais c'est à cause de la non utilisation du filename_infere.

df_tests_tp8, cannot_analyze_codestate_students_tp8, empty_codestate_students_tp8  = find_tests_for_tp_tpprog(df, 'Tp8', PROG_FUNCTIONS_NAME_BY_TP)

print(f'Cannot analyze codestate in Tp8 for : {cannot_analyze_codestate_students_tp8}')
print(f'only empty codestates in Tp8 for : {empty_codestate_students_tp8}')

etud_testant_toute_fonction_ecrite_tp8, etud_testant_aucune_fonction_ecrite_tp8, etud_qq_tests_fonction_ecrite_tp8 = actors_par_pratique_ecriture_tests(df_tests_tp8)

len(etud_testant_toute_fonction_ecrite_tp8)

len(etud_testant_aucune_fonction_ecrite_tp8)

len(etud_qq_tests_fonction_ecrite_tp8)

len(etud_testant_toute_fonction_ecrite_tp8) + len(etud_testant_aucune_fonction_ecrite_tp8) + len(etud_qq_tests_fonction_ecrite_tp8)

97/194*100

df_tests_tp9_bis, cannot_analyze_codestate_students_tp9_bis, empty_codestate_students_tp9_bis  = find_tests_for_tp_tpprog(df, 'Tp9', PROG_FUNCTIONS_NAME_BY_TP, filename=PROG_FILENAMES_BY_TP['Tp9'] )

etud_testant_toute_fonction_ecrite_tp9_bis, etud_testant_aucune_fonction_ecrite_tp9_bis, etud_qq_tests_fonction_ecrite_tp9_bis = actors_par_pratique_ecriture_tests(df_tests_tp9_bis)

len(etud_testant_toute_fonction_ecrite_tp9_bis)

df_tests_tp9, cannot_analyze_codestate_students_tp9, empty_codestate_students_tp9  = find_tests_for_tp_tpprog(df, 'Tp9', PROG_FUNCTIONS_NAME_BY_TP)

print(f'Cannot analyze codestate in Tp9 for : {cannot_analyze_codestate_students_tp9}')
print(f'only empty codestates in Tp9 for : {empty_codestate_students_tp9}')

etud_testant_toute_fonction_ecrite_tp9, etud_testant_aucune_fonction_ecrite_tp9, etud_qq_tests_fonction_ecrite_tp9 = actors_par_pratique_ecriture_tests(df_tests_tp9)

len(etud_testant_toute_fonction_ecrite_tp9)

len(etud_testant_aucune_fonction_ecrite_tp9)

len(etud_qq_tests_fonction_ecrite_tp9)

len(etud_testant_toute_fonction_ecrite_tp9) + len(etud_testant_aucune_fonction_ecrite_tp9) + len(etud_qq_tests_fonction_ecrite_tp9)

151/197*100

# ### Analyse particulière du TP8 

# Pour le TP8 il y avait 2 fichiers à rendre : while.py et jeu_nim.py.

df[(df['TP'] == 'Tp8') & (df['Type_TP'] == 'TP_prog')].filename_infere.unique()

df_tests_tp8_bis, cannot_analyze_codestate_students_tp8_bis, empty_codestate_students_tp8_bis  = find_tests_for_tp_tpprog(df, 'Tp8', PROG_FUNCTIONS_NAME_BY_TP, filename='while.py')

etud_testant_toute_fonction_ecrite_tp8_bis, etud_testant_aucune_fonction_ecrite_tp8_bis, etud_qq_tests_fonction_ecrite_tp8_bis = actors_par_pratique_ecriture_tests(df_tests_tp8_bis)

len(etud_testant_toute_fonction_ecrite_tp8_bis)

len(etud_testant_aucune_fonction_ecrite_tp8_bis)

len(etud_qq_tests_fonction_ecrite_tp8_bis)

158/(158+7+28)

# ## Plot

TPs = ['Tp2', 'Tp3', 'Tp4', 'Tp6', 'Tp7', 'Tp8', 'Tp9']


def genere_donnees_nombre_tests_ecrits_tp_guides(df:pd.DataFrame, functions_names:dict):
    df_plot = pd.DataFrame(columns=['Tps', 'number_of_students', 'number_of_students_analysis_not_possible', 'etud_testant_toute_fonction_ecrite', 'etud_testant_aucune_fonction_ecrite', 'etud_qq_tests_fonction_ecrite'])
    for tp in TPs:
        if tp == 'Tp8':
            df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp  = find_tests_for_tp_tpprog(df, 'Tp8', functions_names, filename='while.py')
            actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == 'while.py')]['actor']
            column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == 'while.py')]['binome'] 
        else:
            df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp  = find_tests_for_tp_tpprog(df, tp, functions_names)
            actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['actor']
            column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['binome']
        all_students_tp  = set(actor_column_tp).union(set(column_binome_tp))
        if '' in all_students_tp:
            all_students_tp.remove('')
        etud_testant_toute_fonction_ecrite_tp, etud_testant_aucune_fonction_ecrite_tp, etud_qq_tests_fonction_ecrite_tp = actors_par_pratique_ecriture_tests(df_tests_tp)
        df_plot_tp = pd.DataFrame({'Tps' : [tp], \
                                'number_of_students' : len(all_students_tp),\
                                'number_of_students_analysis_not_possible' : len(cannot_analyze_codestate_students_tp) + len(empty_codestate_students_tp), \
                                'etud_testant_toute_fonction_ecrite' : len(etud_testant_toute_fonction_ecrite_tp), \
                                'etud_testant_aucune_fonction_ecrite' : len(etud_testant_aucune_fonction_ecrite_tp), \
                                'etud_qq_tests_fonction_ecrite' : len(etud_qq_tests_fonction_ecrite_tp)})
        df_plot = pd.concat([df_plot, df_plot_tp], ignore_index=True)
    return df_plot


df_plot = genere_donnees_nombre_tests_ecrits_tp_guides(df, PROG_FUNCTIONS_NAME_BY_TP)
df_plot

import matplotlib.pyplot as plt


def genere_donnees_plot_nombre_tests_ecrits_tp_guides(df_plot:pd.DataFrame) -> pd.DataFrame:
    df_plot_pratique_ecriture_tests_tp = pd.DataFrame(columns=['Tps', 'pour toutes fonctions écrites', 'pour aucune fonction écrite', 'pour certaines fonctions écrites'])
    df_plot_pratique_ecriture_tests_tp['Tps'] = df_plot['Tps']
    df_nb_total = df_plot['etud_testant_toute_fonction_ecrite'] + df_plot['etud_testant_aucune_fonction_ecrite'] + df_plot['etud_qq_tests_fonction_ecrite']
    df_plot_pratique_ecriture_tests_tp['pour toutes fonctions écrites'] = pd.to_numeric(df_plot['etud_testant_toute_fonction_ecrite']/df_nb_total*100)
    df_plot_pratique_ecriture_tests_tp['pour aucune fonction écrite'] = pd.to_numeric(df_plot['etud_testant_aucune_fonction_ecrite']/df_nb_total*100)
    df_plot_pratique_ecriture_tests_tp['pour certaines fonctions écrites'] = pd.to_numeric(df_plot['etud_qq_tests_fonction_ecrite']/df_nb_total*100)
    return df_plot_pratique_ecriture_tests_tp.round(1)


genere_donnees_plot_nombre_tests_ecrits_tp_guides(df_plot)


def plot_nombre_tests_ecrits_tp_guides(df_plot:pd.DataFrame) -> None:
    names = TPs

    df_plot_pratique_ecriture_tests_tp = genere_donnees_plot_nombre_tests_ecrits(df_plot)
    
    df_plot_pratique_ecriture_tests_tp.set_index('Tps')[['pour toutes fonctions écrites', 'pour aucune fonction écrite', 'pour certaines fonctions écrites']].plot(kind='bar', figsize=(12, 6))
    plt.title("Pratique d'écriture de tests durant les TPs guidés, étudiants pour lequels le code a pu être analysé syntaxiquement")
    plt.ylabel("Pourcentage du nombre d'étudiants")
    plt.xlabel("TP guidés")
    plt.xticks(rotation=45)
    plt.legend(title="Tests présents")
    plt.tight_layout()
    plt.show()


plot_nombre_tests_ecrits_tp_guides(df_plot)



# ## Fonctions pour analyse des TPs Game

df_tests_tpgame_all.filename_infere.unique()

df_tictactoe = df_tests_tpgame_all[df_tests_tpgame_all['filename_infere'] == 'tictactoe.py'].copy()

df_tictactoe.columns

tictactoe_actors = df_tictactoe.actor
df_admin_etud_debutants_tictactoe = df_admin_etud_debutants[df_admin_etud_debutants['actor'].isin(tictactoe_actors)]

df_admin_etud_debutants_tictactoe.debutant.unique()

df_tictactoe_debutants = df_tictactoe.merge(df_admin_etud_debutants_tictactoe, on='actor', how='inner')

df_tictactoe_debutants['debutant'].unique()

len(df_tictactoe)

df_tictactoe_debutants 

# C'est bien ce que dit le notebook 6.Analyze.

# ### Étudiants ayant testé leur jeu

# ### tictactoe

df_tictactoe = df_tests_tpgame_all[df_tests_tpgame_all['filename_infere'] == 'tictactoe.py'].copy()

tictactoe_actors = df_tictactoe.actor
df_admin_etud_debutants_tictactoe = df_admin_etud_debutants[df_admin_etud_debutants['actor'].isin(tictactoe_actors)]

df_tictactoe_debutants = df_tictactoe.merge(df_admin_etud_debutants_tictactoe, on='actor', how='inner')

nb_etud_tictactoe = len(df_tictactoe)

print(f'{nb_etud_tictactoe} etud ont réalisé le tictactoe')

nb_etud_tictactoe_debutant = len(df_tictactoe_debutants[df_tictactoe_debutants['debutant']==True])
print(f'{nb_etud_tictactoe_debutant} etud DEBUTANTS ont réalisé le tictactoe, soit {nb_etud_tictactoe_debutant/nb_etud_tictactoe*100}% de ceux qui ont réalisé le tictactoe')

nb_etud_tictactoe_test = len(df_tictactoe_debutants[df_tictactoe_debutants['tests_number']>0])
print(f'{nb_etud_tictactoe_test} etud ont réalisé ET TESTÉ le tictactoe, soit {nb_etud_tictactoe_test/nb_etud_tictactoe*100}% de ceux qui ont réalisé le tictactoe')

len(df_tictactoe_debutants[df_tictactoe_debutants['tests_number']==0])

len(df_tictactoe_debutants[df_tictactoe_debutants['tests_number']>0]) + len(df_tictactoe_debutants[df_tictactoe_debutants['tests_number']==0])

nb_etud_tictactoe_tests_debutant = len(df_tictactoe_debutants[(df_tictactoe_debutants['tests_number']>0) & (df_tictactoe_debutants['debutant']==True)])
print(f'{nb_etud_tictactoe_tests_debutant} etud DEBUTANTS ont testé le tictatoe, soit {nb_etud_tictactoe_tests_debutant/nb_etud_tictactoe_test*100}% de ceux qui ont testé le tictactoe') 

nb_etud_tictactoe_tests_non_debutant = len(df_tictactoe_debutants[(df_tictactoe_debutants['tests_number']>0) & (df_tictactoe_debutants['debutant']==False)])
print(f'{nb_etud_tictactoe_tests_non_debutant} etud NON DEBUTANTS ont testé le tictatoe, soit {nb_etud_tictactoe_tests_non_debutant/nb_etud_tictactoe_test*100}% de ceux qui ont testé le tictactoe') 

# ### Puissance4

df_puissance4 = df_tests_tpgame_all[df_tests_tpgame_all['filename_infere'] == 'puissance4.py']

puissance4_actors = df_puissance4.actor
df_admin_etud_debutants_puissance4 = df_admin_etud_debutants[df_admin_etud_debutants['actor'].isin(puissance4_actors)]

df_puissance4_debutants = df_puissance4.merge(df_admin_etud_debutants_puissance4, on='actor', how='inner')

df_admin_etud_debutants_puissance4.debutant.unique()

nb_etud_puissance4 = len(df_puissance4)

print(f'{nb_etud_puissance4} etud ont réalisé le puissance4')

nb_etud_puissance4_debutant = len(df_puissance4_debutants[df_puissance4_debutants['debutant']==True])
print(f'{nb_etud_puissance4_debutant} etud DEBUTANTS ont réalisé le puissance4, soit {nb_etud_puissance4_debutant/nb_etud_puissance4*100}% de ceux qui ont réalisé le puissance4')

len(df_puissance4[df_puissance4['tests_number']>0])

nb_etud_puissance4_test = len(df_puissance4_debutants[df_puissance4_debutants['tests_number']>0])
print(f'{nb_etud_puissance4_test} etud ont réalisé ET TESTÉ le puissance4, soit {nb_etud_puissance4_test/nb_etud_puissance4*100}% de ceux qui ont réalisé le puissance4')

57/103*100

len(df_puissance4_debutants[df_puissance4_debutants['tests_number']>0]) + len(df_puissance4_debutants[df_puissance4_debutants['tests_number']==0])

nb_etud_puissance4_tests_debutant = len(df_puissance4_debutants[(df_puissance4_debutants['tests_number']>0) & (df_puissance4_debutants['debutant']==True)])
print(f'{nb_etud_puissance4_tests_debutant} etud DEBUTANTS ont testé le puissance4, soit {nb_etud_puissance4_tests_debutant/nb_etud_puissance4_test*100}% de ceux qui ont testé le puissance4') 

# ### binairo

# Très peu réalisé

df_binairo = df_tests_tpgame_all[df_tests_tpgame_all['filename_infere'] == 'binairo.py']

len(df_binairo)

len(df_binairo[df_binairo['tests_number']>0])

# ### jeu Nim

df_jeu_nim = find_tests_for_tp_tpgame_game('jeu_nim.py', df)

df_jeu_nim

len(df_jeu_nim)

# Tellement peu que je ne sais pas si on peut en conclure quoi que ce soit.

len(df_jeu_nim[df_jeu_nim['tests_number']>0])

39/78*100

# ### Synthèse

GAMES_ANALYZED = ['tictactoe.py', 'puissance4.py', 'binairo.py']#, 'jeu_nim.py']


def genere_donnees_test_games(df:pd.DataFrame, df_tests_game:pd.DataFrame, df_admin_etud_debutants:pd.DataFrame, games_names:list[str]) ->  df:
    '''
    Args:
        df : df total
        df_test_games : columns actor, tp, filename_infere, tests_number, index
        df_admin_etud_debutants : columns actor, debutant
    '''
    df_plot = pd.DataFrame(columns=['jeu', '% étudiants ayant réalisé le jeu (total)', '% étudiants débutants (jeu)', '% étudiants avec tests (jeu)', '% étudiants débutants avec tests (avec tests)'])
    set_actor_df = set(df.actor)
    set_binome_df = set(df.binome)
    if '' in set_binome_df:
        set_binome_df.remove('')
    # nb actors - global df    
    nb_actor_df = len(set_actor_df.union(set_binome_df))
    for game in games_names:
        #print(game, '---------')
        # nb actors - game
        df_game = df_tests_game[df_tests_game['filename_infere'] == game]
        game_actors = df_game.actor.unique()
        nb_actor_df_game = len(game_actors)
        #print('nb_actor_df_game : ', nb_actor_df_game)
        pourcent_etud_game = round(nb_actor_df_game/nb_actor_df*100)
        # debutants / game
        df_admin_etud_debutants_game = df_admin_etud_debutants[df_admin_etud_debutants['actor'].isin(game_actors)]
        df_game_debutants = df_game.merge(df_admin_etud_debutants_game, on='actor', how='inner') 
        nb_etud_game_debutant = len(df_game_debutants[df_game_debutants['debutant']==True])
        pourcent_etud_game_debutant = round(nb_etud_game_debutant/nb_actor_df_game*100)
        #print(' : nb_etud_game_debutant', nb_etud_game_debutant)
        # tests / game
        nb_etud_game_test = len(df_game_debutants[df_game_debutants['tests_number']>0])
        pourcent_etud_game_avec_tests = round(nb_etud_game_test/nb_actor_df_game*100)
        # test & debutants / tests
        nb_etud_game_tests_debutant = len(df_game_debutants[(df_game_debutants['tests_number']>0) & (df_game_debutants['debutant']==True)])
        pourcent_etud_game_tests_debutants = round(nb_etud_game_tests_debutant/nb_etud_game_test*100)
        # local df
        df_plot_game = pd.DataFrame({'jeu' : [game],
                                    '% étudiants ayant réalisé le jeu (total)' : pourcent_etud_game,
                                    '% étudiants débutants (jeu)' : pourcent_etud_game_debutant,
                                    '% étudiants avec tests (jeu)' : pourcent_etud_game_avec_tests,
                                    '% étudiants débutants avec tests (avec tests)' : pourcent_etud_game_tests_debutants})
        df_plot = pd.concat([df_plot, df_plot_game], ignore_index=True)
    return df_plot
        


df_plot_games =  genere_donnees_test_games(df, df_tests_tpgame_all, df_admin_etud_debutants, GAMES_ANALYZED)

df_plot_games


