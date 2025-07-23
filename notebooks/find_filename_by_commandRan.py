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

import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import re
import numpy as np
from src.features import io_utils, data_cleaning
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant_2425 import FILES_BY_TP


# +
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

FUNCTIONS_TP2_Manip = [
    "imperial2metrique",
    "poly1",
    "poly2",
    "perimetre_triangle",
    "concatenation",
    "nieme_chiffre",
    "nb_secondes_par_jour",
    "nb_secondes_moyen_par_an",
    "nb_secondes_moyen_par_mois",
    "date2secondes",
    "secondes_depuis_date_reference",
    "age_a_date", 
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

FUNCTIONS_TP3_Manip = [
    "fonction2",
    "fonction3",
    "fonction4",
    "fonction5",
    "fonction1",
    "pred1",
    "pred2",
    "pred3",
    "pred4",
    "pred5",
    "pred9",
    "est_special",
    "sont_proches"
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

FUNCTIONS_TP4_Manip = [
    "categorie_tir_arc_v1",
    "categorie_tir_arc_v2",
    "categorie_tir_arc_v3",
    "categorie_tir_arc_v4",
    "mon_abs",
    "signe1",
    "signe2",
    "en_tete1",
    "int2str",
    "pile_ou_face1",
    "pile_ou_face2",
    "parite",
    "mediane",
    "grade",
    "myown_not",
    "myown_or",
    "myown_and"
    
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

# Encore des pbs ici.
FUNCTIONS_TP5_Manip = [
#    'print("coucou")',
    'chaine',
    "mystere",
#    "exercices de manipulation : print", # It's not a function
    "saison",
    "affiche_saison",
    "rouleau",
    "representation_rouleaux",
    "representation_differentiel"
    
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

FUNCTIONS_TP6_Manip = [
    "mystere",
    "mystere2",
    "affiche_range",
    "compte_iterations",
    "saisie_caracteres",
    "compte_positifs",
    "variance",
    "incremente",
    "nombre_ponctuation_dans_chaine",
    "nombre_ponctuation_dans_liste",
    "puissance",
    "prefixes",
    "generer_point",
    "est_dans_cercle",
    "generer_liste_points",
    "calcul_pi",

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

FUNCTIONS_TP7_Manip = [
    "calcule_produit_cartesien1",
    "calcule_produit_cartesien2",
    "se_suivent"
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

FUNCTIONS_TP8_Manip = [
    "multiplication",
    "saisie_reponse",
    "duree_atteinte_seuil",
    "compte_elements_identiques",
    "racine_entiere",
    "saisie_entier_intervalle",
    "compare",
    "deviner_un_nombre",
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

FUNCTIONS_TP9_Manip = [
    "contient_longue_chaine",
    "tous_entier_intervalle",
    "au_moins_2_oui",
    "contiennent_car"
]

# TP10
FUNCTIONS_TP10_Manip = [
    "carre_1_au_centre",
    "affecte"  
]
# -



# +
# Global variable pattern
pattern = ''
for tp_name in FILES_BY_TP:

    file_name = '|'.join(tp_name)
    pattern = pattern +  file_name + '|'

pattern = pattern  + 'Irrelevant'
# -

# JE n'ai fait les tests que pour les TP de prog, d'où le dico ci-dessous.

# All TP
all_TP_functions_name_prog = {
    'fonctions.py': FUNCTIONS_TP2_Prog,  # TP2
    'booleens.py' : FUNCTIONS_TP3_Prog, # TP3
    'conditionnelles.py' : FUNCTIONS_TP4_Prog, # TP4
    'imprimerie.py' : FUNCTIONS_TP5_Prog, # TP5
    "iterables_for.py" : FUNCTIONS_TP6_Prog ,  # TP6
    "iterable_indexation.py": FUNCTIONS_TP7_Prog, # TP7
    "while.py" : FUNCTIONS_TP8_Prog,  # TP8
    "parcours_interrompu.py" : FUNCTIONS_TP9_Prog # TP9
    }


def find_filename_by_searching_function_call(TP_files:dict, commandRan:str) -> str:

    """
    Searchs if the commandRan contains a call to a function in TP_files, and if any returns the associated filename.
    Else returns the empty string.

    Args:
        TP_files : A Dict of all files with their functions.
        commandRan : commandRan of a raw

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """

    for filename, function_names in TP_files.items():
        pattern = '|'.join(function_names)
        match = re.search(pattern, commandRan)
        
        if match: 
            return filename
            
    return '' # no match found!


def get_regexp_for_function_call(functions_name:dict) -> dict:
    '''
    functions_name is a dictionary whose keys are filenames and values are list of function names of the kind 'repetition'

    Adds a regexpr that allows spaces or tabs before the '('. 
    '''
    dico = {}
    for key in functions_name:
        function_list = functions_name[key]
        new_list = []
        for name in function_list:
            new_name = rf'(\W|\A){name}[ \t]*\('#r'(\W|\A)' + re.escape(name) + r'[ \t]*\('
            new_list.append(new_name)
        dico[key] = new_list
    return dico


def find_filename_by_commandRan(all_TP_functions : dict, pattern_files_name: str, commandRan: str) -> str:

    """
    Prend en paramètre un dico qui associe à un nom de fichier une liste de nom de fonctions
    ex : 'fonctions.py' : ['repetition', ...]

    pattern_files_name : capture l'ens des noms de fichiers

    commandRan : une commandRan

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """
    match_state = re.search(pattern_files_name, commandRan)

    if match_state: # if the name is in the P_codeState
        matched_filename = match_state.group()  # Extract the name
        return matched_filename

    else: # if the exact name is not in P_codeState and student might removed the name part, we check the match with the content
        dico_regexpr = get_regexp_for_function_call(all_TP_functions)
        filename_infere = find_filename_by_searching_function_call(dico_regexpr, commandRan)
        
        # Remove to test
        #if filename_infere == '':
            #print("Filename not found!")
        return filename_infere
0676027678
Raphael

# Juste pour tester la fonciton ci-dessous.

def check_all_TP_functions_withfind_filename_by_etc(TP_files):
    for filename, function_names in TP_files.items():
        for func_name in function_names:
            filename_infered = find_filename_by_commandRan(TP_files, pattern, f'{func_name}   (')
            if filename_infered != filename:
                print(f'\"{func_name}\" infere {filename_infered} au lieu de {filename}')


check_all_TP_functions_withfind_filename_by_etc(all_TP_functions_name_prog)


# Il faut enlever "miroir" des 2 TPs ds lesquels cette fonction apparaît.

# ## Recherche d'une def de fonction dans un codeState

# Pour le moment j'ai laissé la recherche d'au moins une def de fonction de TP_files dans le codeState.
#
# Si on veut en chercher plus d'une il faut faire autrement.
#

def find_filename_by_searching_function_def(TP_files:dict, codeState:str) -> str:

    """
    Searchs if the codeState contains a def of a function of TP_files, and if any returns the associated filename.
    Else returns the empty string.

    Args:
        TP_files : A Dict of all files with their functions.
        codeState : codeState of a raw

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """
    for filename, function_names in TP_files.items():
        pattern = '|'.join(function_names)
        match = re.search(pattern, codeState)
        
        if match: 
            return filename
            
    return '' # no match found!


def get_regexp_for_function_def(functions_name:dict) -> dict:
    '''
    functions_name is a dictionary whose keys are filenames and values are list of function names of the kind 'repetition'

    Adds a regexpr that allows spaces or tabs before the '('. 
    '''
    dico = {}
    for key in functions_name:
        function_list = functions_name[key]
        new_list = []
        for name in function_list:
            new_name = rf'def[ \t]*{name}[ \t]*\('
            new_list.append(new_name)
        dico[key] = new_list
    return dico


def find_filename_by_codeState(all_TP_functions : dict, pattern_files_name: str, codeState: str) -> str:

    """
    Searchs if the codeState contains a def of a function in TP_files, and if any returns the associated filename.
    Else returns the empty string.

    Args:
        TP_files : A Dict of all files with their functions, ex {'fonctions.py' : ['repetition'] ...]
        codeState : codeState of a raw
        pattern_files_name : a regexpr that captures all file names

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """
    match_state = re.search(pattern, codeState)

    if match_state: # if the name is in the P_codeState
        matched_filename = match_state.group()  # Extract the name
        return matched_filename

    else: # if the exact name is not in P_codeState and student might removed the name part, we check the match with the content
        dico_regexpr = get_regexp_for_function_def(all_TP_functions)
        filename_infere = find_filename_by_searching_function_def(dico_regexpr, codeState)
        
        # Remove to test
        #if filename_infere == '':
            #print("Filename not found!")
        return filename_infere


