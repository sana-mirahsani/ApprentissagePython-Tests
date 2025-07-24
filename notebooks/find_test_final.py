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
from src.data.variable_constant_2425 import SORTED_SEANCE
import re
from src.data.variable_constant_2425 import FILES_BY_TP, TP_NAME
from src.features import data_cleaning

# -

# # import spécifiques à L1test

from thonnycontrib.backend.test_finder import L1TestFinder
from thonnycontrib.exceptions import SpaceMissingAfterPromptException

# # Dataframe

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase2_nettoyage_fichiere.csv')

# Inutile mais j'en avais besoin avant...

df['codeState'] = df['P_codeState'] + df['F_codeState']

# # Analyse des TPs Tp_Prog de 'Tp2' à 'Tp9'

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

def find_tests_for_tp_tpprog_name(name:str, df:pd.DataFrame, tp:str, functions_names:dict) -> tuple[pd.DataFrame, bool, bool]:
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
        
    Returns:
        None, False, True: if no codeState was found, or only empty codeStates
        None, True, False: if no codeState could be parsed, or no codeState contains at least one function of functions_name
        df, False, False: if some codeState could be parsed and contains 
    
    """
    # Les timestamps ne sont pas triés par ordre croissant.
    # La fonction recherche les codeState comme suit : 
    # - elle cherche le codestate le plus récent,
    # - s'il est analysable, elle vérifie qu'il y a au moins une des fonctions cherchées dedans
    # - s'il n'est pas analysable ou si aucune fonction n'est trouvée, elle cherche à nouveau le codestate le plus récent, moins le précédent.
    # Et ce tant qu'il y a des codestate à traiter.
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


def find_tests_for_tp_tpprog(df:pd.DataFrame, tp:str, functions_names:dict) -> tuple[pd.DataFrame, list[str], list[str]]:
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
    actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['actor']
    column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['binome']
    all_students_tp  = set(actor_column_tp).union(set(column_binome_tp))
    if '' in all_students_tp:
        all_students_tp.remove('')
    for name in all_students_tp:
        df_name, cannot_analyze_codestate, empty_codestates = find_tests_for_tp_tpprog_name(name, df, tp, functions_names)
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

# # Analyse des TP_Game

# Cette fois on compte les tests dans l'ensemble du module/codeState, on ne compte pas les tests par fonction (mélange de fonctions testables et non testables).
#

# Pour chaque étudiant on regarde les différents jeux sur lesquels il a travaillé, au travers des différents filename_infere. 
#

# Pour trouver le codeState on procède comme pour les TP2 à 9 en cherchant le codeState qui a le timestamp le plus récent, et on continue tant qu'on n'a pas trouvé un codeState analysable et contenant des tests. Si aucun codeState n'est analysable, on renvoie None. Par contre : si aucune codeState ne contient de tests, on indique bien qu'il y a 0 tests. 

# En cours de route je n'ai eu ni le temps ni l'envie de gérer les cannot_analyze_codestate et empty_codestate. 

# Cette constante est dans variable_constantes_2425 mais je n'ai aps redémarré le serveur...

FILENAME_TP_GAME = ["tictactoe.py", "puissance4.py", "jeu_2048.py", "binairo.py", "tectonic.py", "galaxies.py"]


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
    df_name_tp = df[(df['TP'] == 'Tp_GAME') & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == filename_tpgame)& ((df['actor'] == name) | (df['binome'] == name))]
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
    df_name_tp = df[(df['TP'] == 'Tp_GAME') & (df['Type_TP'] == 'TP_prog') & ((df['actor'] == name) | (df['binome'] == name))]
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


# ## Ex d'utilisation

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


