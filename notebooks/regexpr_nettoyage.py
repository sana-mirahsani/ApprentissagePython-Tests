# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: venv_jupyter_l1test
#     language: python
#     name: venv_jupyter_l1test
# ---

# %%
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import re
import numpy as np
from src.features import io_utils, data_cleaning
from src.data.constants import INTERIM_DATA_DIR
from src.data.variable_constant_2425 import FILES_BY_TP

# Global variable pattern
pattern = ''
for tp_name in FILES_BY_TP:

    file_name = '|'.join(tp_name)
    pattern = pattern +  file_name + '|'

pattern = pattern  + 'Irrelevant'

# %%
df_clean = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase1_nettoyage_fichiere.csv')

# %% [markdown]
# L'objectif est de refaire proprement les fonctions qui permettent de chercher soit un appel soit une définition 
# de function dans un commandRan (appel de fonction) ou un codestate (définition de fonction).
#
# Pour ça il faut une fonction qui cherche un appel de fonction dans une chaîne.
#
# Et une autre fonction qui cherche une définition de fonction dans une chaîne.
#
#

# %% [markdown]
# Il va falloir aussi se mettre d'accord sur la manière d'utiliser les noms de fonctions définis dans variable_constants_2425.
#
# En l'état on mélange des noms de fonctions, des expr reg (nom de fonction + \() et des chaînes diverses.
#
# Pour chercher les fonctions et compter leurs tests, j'ai besoin d'avoir des noms de fonctions et rien d'autres.
#
# Il faudra peut-être adapter le reste du code.

# %% [markdown]
# # le dictionnaire des fonctions de noms

# %%
from src.data.variable_constant_2425 import SORTED_SEANCE

# %% [markdown]
# Ça ne va encore pas pour la semaine 1 et d'autres: on ne devrait pas avoir par ex 'note_UE.py': ['# TP PROG semaine 1'].
#
# À la fin je veux uniquement des noms de fonctions.
#
# Si on veut garder des bouts de code, il faut les mettre dans un autre dictionnaire qu'on utilisera dans une autre fonction.

# %%
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

# %% [markdown]
# Il faut aussi revoir le dictionnaire all_TP_functions_name.

# %% [markdown]
# Dans un premier temps j'en fais un autre.

# %%
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

# %%
all_TP_functions_name_prog


# %% [markdown]
# # Les fonctions de recherche

# %% [markdown]
# Pour la fonction qui suit, anciennement find_filename_by_function_name
#
# - changement du nom pour bien faire apparaître l'appel de fonction dans une commande
# - simplification du code pour le join
# - simplification du code pour le items(), pour éviter les [0] et les [1]

# %%
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


# %%
'|'.join(['a'])

# %%
'|'.join(['a', 'b'])


# %% [markdown]
# Il faut une fonction qui génère à partir du nom d'une fonction une expr régulière qui représente un appel à cette fonction.

# %% [markdown]
# L'approche qu'on utilisait était FAUSSE. 
#
# On cherchait juste le nom de la fonction, suivi d'une parenthèse.
#
# Il manquait les espaces possibles avant la parenthèse.
#
# Surtout il manquait le fait qu'on a des fonctions qui sont préfixes ou suffixes d'autres noms ou contenu dans d'autres noms :
#
# - moyenne, préfixe de moyenne_ponderee et moyenne_entiere. Typiquement si on tombe d'abord sur la recherche de moyenne, c'est elle qui gagne alors qe le commandRan est "moyenne_p. 
# - maximum, indice_maximum
# - de et je ne sais plus quoi.

# %% [markdown]
# Donc, quand on cherche un appel de fonction, il faut vérifier qu'il n'y a pas avant un caractère autorisés dans un ident.
#
# Un appel de fonction est donc : 
#
# - le début de la chaîne ou un caractère qui n'est pas un caractère d'identificateur : \A|\W. On pour la fonction "f" on acceptera +f() mais pas autre_f()
# - suivi du nom de la fonction
# - suivi d'espaces éventuels puis (

# %%
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


# %%
re.search('(\\W|\\A)est_non_vide[ \\t]*\\(', "est_non_vide ('kl')\n")

# %%
re.search('(\\W|\\A)est_non_vide[ \\t]*\\(', "toto_est_non_vide ('kl')\n")

# %%
re.search('(\\W|\\A)est_non_vide[ \\t]*\\(', "est_non_vide('kl')\n")

# %%
re.search('(\\W|\\A)maximum[ \\t]*\\(', "indice_maximum ('kl')\n")

# %%
re.search('(\\W|\\A)indice_maximum[ \\t]*\\(', "maximum ('kl')\n")

# %%
re.search('(\\W|\\A)de[ \\t]*\\(', 'est_date_valide(')

# %%

# %%
all_TP_functions_name_prog_regexpr = get_regexp_for_function_call(all_TP_functions_name_prog)
all_TP_functions_name_prog_regexpr


# %%
def find_filename_by_commandRan(all_TP_functions : dict, pattern: str, commandRan: str) -> str:

    """
    Prend un paramètre

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """
    match_state = re.search(pattern, commandRan)

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


# %%
all_TP_functions_name_prog


# %%
def check_all_TP_functions_withfind_filename_by_etc(TP_files):
    for filename, function_names in TP_files.items():
        for func_name in function_names:
            filename_infered = find_filename_by_commandRan(TP_files, pattern, f'{func_name}   (')
            if filename_infered != filename:
                print(f'\"{func_name}\" infere {filename_infered} au lieu de {filename}')


# %%
check_all_TP_functions_withfind_filename_by_etc(all_TP_functions_name_prog)

# %% [markdown]
# miroir est dans les 2 TP iterables_for.py et iterable_indexation.py. On l'enlève.

# %%
find_filename_by_searching_function_call(all_TP_functions_name_prog_regexpr, 'repetition(')

# %%
find_filename_by_searching_function_call(all_TP_functions_name_prog_regexpr, 'indice_maximum(')

# %%
find_filename_by_searching_function_call(all_TP_functions_name_prog_regexpr, 'decoupage(')

# %%
find_filename_by_searching_function_call(all_TP_functions_name_prog_regexpr, 'est_date_valide(')

# %%
find_filename_by_commandRan(all_TP_functions_name_prog, pattern, 'est_date_valide(')

# %%
find_filename_by_commandRan(all_TP_functions_name_prog, pattern, 'decoupage(')

# %%
find_filename_by_commandRan(all_TP_functions_name_prog, pattern, 'indice_maximum(')

# %%
find_filename_by_commandRan(all_TP_functions_name_prog, pattern, 'maximum(')

# %%
