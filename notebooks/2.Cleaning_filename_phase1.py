# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
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

# %% [markdown]
# # Preparation Workflow Overview:
# 1. Import Libraries
# 2. Load DataFrame : acteur_nettoyage_2425.csv
# 3. Clean DataFrame
#     <br>
#     3.1 Add column **filename_infere**
#     <br>
#
#     3.2 Extract short filename
#     <br>
#
#     3.3 Check empty filename_infere of **Run.Test**
#     <br>
#
#     3.4 Check empty filename_infere of **Run.Program**
#
#         3.4.1 Fill empty filename_infere of Run.Program by P_codestate 
#         
#         3.4.2 Fill empty filename_infere of Run.Program by commandRan
#
#     3.5 Check empty filename_infere of **Run.Command** 
#     <br>
#
#     3.6 Check empty filename_infere of **File.Open** 
#     <br>
#
#     3.7 Check empty filename_infere of **File.Save**
#     <br>
#
#     3.8 Check empty filename_infere of **Docstring.Generate**
#
# 4. Save new DataFrame : phase1_nettoyage_fichiere.csv
#
#
# _________________________________________________________
# **Explanation** 
#
# The goal is creating a new column filename_infere, and finding the correct name of files and put them into this column. Since the process is complecated, I divided this part into two phases, phase one filling column filename_infere by columns : filename, commandRan and codestate; phase two validate them and use mecanism like similarity and sandwich to find filenames which were impossible to find them during the phase one. This notebook includs only phase one, it saves the result into a csv file and shoudl read this csv file as the input in the phase two notebook which is the next step.

# %% [markdown]
# ## Import Libraries

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
pattern

# %% [markdown]
# ## Load DataFrame

# %%
df_clean = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='acteur_nettoyage_2425.csv')

# %%
df_clean[df_clean['_id.$oid'] == '66ed37fabd5a98b8f9da4354'][['filename','P_codeState','verb','commandRan']]

# %%
df_clean[df_clean['_id.$oid'] == '66ed3929bd5a98b8f9da4482'][['filename','P_codeState','verb','commandRan']]

# %% [markdown]
# ## Clean DataFrame

# %% [markdown]
# ### Add column **filename_infere**

# %%
col_index = df_clean.columns.get_loc('filename')
df_clean.insert(col_index + 1, 'filename_infere', '') 
df_clean.columns

# %% [markdown]
# ### Extract short filename

# %%
# Before
total_empty_filename_infere = (df_clean['filename_infere']=='').sum()
print(f"Total number of empty strings in filename_infere : {total_empty_filename_infere}")

# Apply
df_clean['filename_infere'] = data_cleaning.extract_short_filename(df_clean['filename'])

# After
total_empty_filename_infere = (df_clean['filename_infere']=='').sum()
print(f"Total number of empty strings in filename_infere : {total_empty_filename_infere}")

# %%
df_clean[['filename','filename_infere']].head(10)

# %% [markdown]
# There are already some names in column filename, I extract them and put them in column filename_infere, total empty filename reduced from 306,914 to 151,183.

# %%
df_clean[df_clean['_id.$oid'] == '66ed37fabd5a98b8f9da4354'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %%
df_clean[df_clean['_id.$oid'] == '66ed3929bd5a98b8f9da4482'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %%
df_clean[['filename','filename_infere']].head(10)

# %% [markdown]
# ### Check empty filename_infere of **Run.Test**

# %%
# Before
total_Run_Test       = len(df_clean[df_clean['verb']  == 'Run.Test'])
total_Run_Test_empty = (df_clean[df_clean['verb'] =='Run.Test']['filename'] == '').sum()
total_Run_Test_nan   = df_clean[df_clean['verb'] =='Run.Test']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Test : {total_Run_Test}")
print(f"Total number of empty strings in filename_infere in Run.Test : {total_Run_Test_empty}")
print(f"Total number of None in filename_infere in Run.Test : {total_Run_Test_nan}")

# %% [markdown]
# **Interpretation** There is no empty or none values for Run.Test, but I need to check the correctness of their name which I do in phase two.

# %% [markdown]
# ###  Check empty filename_infere of **Run.Program**

# %%
# Before
total_Run_Program       = len(df_clean[df_clean['verb']  == 'Run.Program'])
total_Run_Program_empty = (df_clean[df_clean['verb'] =='Run.Program']['filename_infere'] == '').sum()
total_Run_Program_nan   = df_clean[df_clean['verb'] =='Run.Program']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Program : {total_Run_Program}")
print(f"Total number of empty strings in filename_infere in Run.Program : {total_Run_Program_empty}")
print(f"Total number of None in filename_infere in Run.Program : {total_Run_Program_nan}")

# %% [markdown]
# **Interpretation** All rows of Run.Program is empty; first I look at the column **P_codeState**, if there is any file's name between <trace></trace>, I extract it. Then if there is any empty string still, I look at the **commandRan** column, since all values start with %Run, I can use an unique pattern to extract the filename for the empty filename_infere. Normally the filename_infere I found from P_codestate are correct, but since at the beginning I filled filename_infere by filename without checking them are correct or not, or extracting a name after %Run in commandRan, there might be incorrect names, which I will check them in phase two.  

# %% [markdown]
# #### Fill empty filename_infere of **Run.Program** by P_codestate

# %%
# check if all values in P_codeState have <trace></trace>
total_non_empty_codestate     = (df_clean[df_clean['verb']  == 'Run.Program']['P_codeState'] != '').sum()
total_codestate_contain_trace = df_clean[df_clean['verb']  == 'Run.Program']['P_codeState'].str.contains(r'<trace>.*\.py</trace>', regex=True, na=False).sum()

print(f"Total rows of not empty strings in P_codeState for Run.Program : {total_non_empty_codestate}")
print(f"Total rows of P_codeState contian <trace> : {total_codestate_contain_trace}")

# %%
# Apply
mask = (df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] == '')
df_clean.loc[mask, 'filename_infere'] = df_clean.loc[mask, 'P_codeState'].map(data_cleaning.extract_short_filename_from_P_codestate_Run_Program)

# %%
# After
total_Run_Program_empty = (df_clean[df_clean['verb'] =='Run.Program']['filename_infere'] == '').sum()
print(f"Total rows of empty strings in Run.Program : {total_Run_Program_empty}")

# %% [markdown]
# #### Fill empty filename_infere of **Run.Program** by commandRan

# %%
# check if all values in commandRan starts with %Run
total_non_empty_commandRan = len(df_clean[(df_clean['verb'] == 'Run.Program') & (df_clean['commandRan'] != '')])
total_commandRan_start_Run = len(df_clean[df_clean['verb'] == 'Run.Program']['commandRan'].str.startswith('%Run'))

print(f"Total rows of not empty strings in commandRan for Run.Program : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Run in Run.Program : {total_commandRan_start_Run}")

# %% [markdown]
# There are values in commandRan which they include %Run Editor content.

# %%
# Apply
mask = (df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] == '') # use commandRan ONLY for empty filename_infere
df_clean.loc[mask, 'filename_infere'] = data_cleaning.extract_short_filename_from_commandRan_Run_Program(df_clean.loc[mask, 'commandRan'])

# %%
# After
total_Run_Program_empty = (df_clean[df_clean['verb']=='Run.Program']['filename_infere'] == '').sum()

print(f"Total rows of empty strings in Run.Program : {total_Run_Program_empty}")

# %% [markdown]
# **Interpretation** : we reduced empty filename_infere from 54,352 to 5,658 by **P_codeState** and **commandRan**.

# %%
df_clean[(df_clean['verb'] == 'Run.Program') & (df_clean['filename_infere'] != '')][['filename_infere','commandRan','P_codeState']]

# %% [markdown]
# #### Check empty filename_infere of **Run.Debugger**

# %%
# Before
total_Run_Debugger       = len(df_clean[df_clean['verb']  == 'Run.Debugger'])
total_Run_Debugger_empty = (df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'] == '').sum()
total_Run_Debugger_nan   = df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.Debugger : {total_Run_Debugger}")
print(f"Total number of empty strings in filename_infere in Run.Debugger : {total_Run_Debugger_empty}")
print(f"Total number of None in filename_infere in Run.Debugger : {total_Run_Debugger_nan}")

# %% [markdown]
# The process is same as Run.Program.

# %% [markdown]
# #### Fill empty filename_infere of **Run.Debugger** by commandRan

# %%
# check if all values in commandRan starts with %Debug
total_non_empty_commandRan       = len(df_clean[(df_clean['verb'] == 'Run.Debugger') & (df_clean['commandRan'] != '')])
total_commandRan_start_Debug     = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Debug').sum()
total_commandRan_start_NiceDebug = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Nice').sum()
total_commandRan_start_FastDebug = df_clean[df_clean['verb'] == 'Run.Debugger']['commandRan'].str.startswith('%Fast').sum()

print(f"Total rows of not empty strings in commandRan for Run.Debugger  : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Debug in Run.Debugger     : {total_commandRan_start_Debug}")
print(f"Total rows of commandRan starts with %NiceDebug in Run.Debugger : {total_commandRan_start_NiceDebug}")
print(f"Total rows of commandRan starts with %FastDebug in Run.Debugger : {total_commandRan_start_FastDebug}")

# %% [markdown]
# **Interpretation** All values in commandRan starts with %Debug, so I extract them but checking them if they are correct or not, is going to be in phase two.

# %%
# Apply
mask = df_clean['verb'] == 'Run.Debugger'
df_clean.loc[mask, 'filename_infere'] = data_cleaning.extract_short_filename_from_commandRan_Run_Debugger(df_clean.loc[mask, 'commandRan'])

# %%
# After
total_Run_Debugger_empty = (df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'] == '').sum()
print(f"Total number of empty strings in filename_infere in Run.Debugger : {total_Run_Debugger_empty}")

# %%
df_clean[df_clean['verb'] == 'Run.Debugger']['filename_infere'].head(10)

# %%
df_clean[df_clean['_id.$oid'] == '66ed37fabd5a98b8f9da4354'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %%
df_clean[df_clean['_id.$oid'] == '66ed3929bd5a98b8f9da4482'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %% [markdown]
# ### Check empty filename_infere of **Run.Command**

# %%
# Before
total_Run_command       = len(df_clean[df_clean['verb']  == 'Run.Command'])
total_Run_command_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_nan   = df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'].isna().sum()

print(f"Total number of traces in Run.command : {total_Run_command}")
print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of None in filename_infere in Run.command : {total_Run_command_nan}")

# %%
# check if all values in commandRan starts with %NiceDebug or %FastDebug
total_non_empty_commandRan       = len(df_clean[(df_clean['verb'] == 'Run.Command') & (df_clean['commandRan'] != '')])
total_commandRan_start_Debug     = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%Debug').sum()
total_commandRan_start_NiceDebug = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%NiceDebug').sum()
total_commandRan_start_FastDebug = df_clean[df_clean['verb'] == 'Run.Command']['commandRan'].str.startswith('%FastDebug').sum()

print(f"Total rows of not empty strings in commandRan for Run.Command  : {total_non_empty_commandRan}")
print(f"Total rows of commandRan starts with %Debug in Run.Command     : {total_commandRan_start_Debug}")
print(f"Total rows of commandRan starts with %NiceDebug in Run.Command : {total_commandRan_start_NiceDebug}")
print(f"Total rows of commandRan starts with %FastDebug in Run.Command : {total_commandRan_start_FastDebug}")

# %% [markdown]
# **Interpretation** 
#
# Only 70 values starts wtih %FastDebug, which I can use them to fill filename_infere, also there are names' of function in this column, that I can find the corresponding filename of the function in the commandRan by function find_filename_by_codestate() , I used the same function which is in phase two, that's why the name is by codestate, because I'm lazy and I didn't want to write another function with another name which does the same thing :)

# %%
# Apply 
mask = df_clean['verb'] == 'Run.Command'

# Get only cleaned values for those starting with %FastDebug
cleaned_values = data_cleaning.extract_short_filename_from_commandRan_Run_Command(df_clean.loc[mask, 'commandRan'])

df_clean.loc[cleaned_values.index, 'filename_infere'] = cleaned_values

# %%
# After
total_Run_command_empty     = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_not_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] != '').sum()

print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of NOT empty strings in filename_infere in Run.command : {total_Run_command_not_empty}")

# %%
# Apply : find_filename_by_codestate for Run.command by looking commandRan
df_clean.loc[mask, 'filename_infere'] = df_clean.loc[mask, 'commandRan'].apply(
    lambda command: data_cleaning.find_filename_by_codestate(pattern, command)
)

# %%
# After
total_Run_command_empty     = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] == '').sum()
total_Run_command_not_empty = (df_clean[df_clean['verb'] == 'Run.Command']['filename_infere'] != '').sum()

print(f"Total number of empty strings in filename_infere in Run.command : {total_Run_command_empty}")
print(f"Total number of NOT empty strings in filename_infere in Run.command : {total_Run_command_not_empty}")

# %%
total_PcodeState_empty = (df_clean[df_clean['verb'] == 'Run.Command']['P_codeState'] == "").sum()
total_FcodeState_empty = (df_clean[df_clean['verb'] == 'Run.Command']['F_codeState'] == "").sum()

print(f"Total number of empty strings in P_codeState in Run.command : {total_PcodeState_empty}")
print(f"Total number of empty strings in F_codeState in Run.command : {total_FcodeState_empty}")

# %% [markdown]
# # Code with bug

# %% [markdown]
# Pour l'ajout d'espaces avant la parenthèse ouvrante dans les valeurs de all_TP_functions_name :
#
# - c'est l'antislash devant la parenthèse ouvrante dans all_TP_functions_name qui pose problème
# - mais je ne comprends pas où find_filename_by_function_name est appelée, donc je n'ai pas modifié. Comme on a 0 tests, j'ai peur de tout casser.
#
# Ci-dessous des exemples.

# %% [markdown]
# Le code de cette fonction est inutilement compliqué pour le join, mais on peut laisser comme ça.

# %%
'|'.join(['q'])

# %%
'|'.join(['a', 'q'])

# %%
'|'.join([])


# %%
def find_filename_by_function_name(TP_files:dict,commandRan:str) -> str:

    """
    Get the codestate of a row, and see if it can find any name of functions of all TPs
    in it, if it finds, it extracts the corresponding filename of the function, and return it.

    Args:
        TP_files : A Dict of all files with their functions.
        codestate : P_codestate or F_codestate of a row.

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """

    for item in TP_files.items():
    
        if len(item[1]) > 1:
            pattern = '|'.join(item[1])

        else: 
            pattern = item[1][0]

        match = re.search(pattern, commandRan)
        
        if match: 
            #print(match)
            filename_infere = item[0]
            return filename_infere
            
    return '' # no match found!


# %%
from src.data.variable_constant_2425 import SORTED_SEANCE, all_TP_functions_name 

# %%
all_TP_functions_name

# %% [markdown]
# Je redéfinis les listes de noms  de fonctions par TP en virant le '\'

# %%
# Added by Sana

# TP2
FUNCTIONS_TP2_Prog = [
    "repetition(",
    "moyenne_entiere(",
    "moyenne_entiere_ponderee(",
    "heure2minute(",
    "jour2heure(",
    "en_minutes(",
    "message(",
    "bonbons_par_enfant("
]

FUNCTIONS_TP2_Manip = [
    "imperial2metrique(",
    "poly1(",
    "poly2(",
    "perimetre_triangle(",
    "concatenation(",
    "nieme_chiffre(",
    "nb_secondes_par_jour(",
    "nb_secondes_moyen_par_an(",
    "nb_secondes_moyen_par_mois(",
    "date2secondes(",
    "secondes_depuis_date_reference(",
    "age_a_date(", 
]

# TP3
FUNCTIONS_TP3_Prog = [
    "est_non_vide(",
    "est_reponse(",
    "est_beneficiaire(",
    "est_reponse_correcte(",
    "est_en_ete(",
    "est_nombre_mystere(",
    "ont_intersection_vide(",
    "intervalle1_contient_intervalle2(",
    "sont_intervalles_recouvrants(",
    "est_gagnant(",
    "est_strict_anterieure_a(",
    "est_mineur_a_date(",
    "est_senior_a_date(",
    "a_tarif_reduit_a_date(",
]

FUNCTIONS_TP3_Manip = [
    "fonction2(",
    "fonction3(",
    "fonction4(",
    "fonction5(",
    "fonction1(",
    "pred1(",
    "pred2(",
    "pred3(",
    "pred4(",
    "pred5(",
    "pred9(",
    "est_special(",
    "sont_proches("
]

# TP4 
FUNCTIONS_TP4_Prog = [
    "numero_jour(",
    "nom_jour(",
    "est_date_valide(",
    "est_jour_valide(",
    "nombre_jours(",
    "est_mois_valide(",
    "calcul_gain(",
    "montant_facture(",
    "nombre_exemplaires(",
    "conseil_voiture(",
    "argminimum(",
    "cout_location(",
    "minimum3(",
    "compare(",
    "maximum(", 
    "est_bissextile("
]

FUNCTIONS_TP4_Manip = [
    "categorie_tir_arc_v1(",
    "categorie_tir_arc_v2(",
    "categorie_tir_arc_v3(",
    "categorie_tir_arc_v4(",
    "mon_abs(",
    "signe1(",
    "signe2(",
    "en_tete1(",
    "int2str(",
    "pile_ou_face1(",
    "pile_ou_face2(",
    "parite(",
    "mediane(",
    "grade(",
    "myown_not(",
    "myown_or(",
    "myown_and("
    
]

# TP5
FUNCTIONS_TP5_Prog = [
    "<trace>imprimerie.py</trace>",
    "<trace>jeu_421.py</trace>",
    "representation_lancer(",
    "de(",
    "est_42(",
    "est_421(",
]

FUNCTIONS_TP5_Manip = [
    'print("coucou")',
    'chaine',
    "mystere(",
    "exercices de manipulation : print", # It's not a function
    "saison(",
    "affiche_saison(",
    "rouleau",
    "representation_rouleaux",
    "representation_differentiel"
    
]

# TP6
FUNCTIONS_TP6_Prog = [
    "carres(",
    "nombre_occurrences(",
    "nombre_occurrences2(",
    "moyenne(",
    "sans_elt(",
    "positive(",
    "chiffres(",
    "miroir(",
    "compte_car("
]

FUNCTIONS_TP6_Manip = [
    "mystere(",
    "mystere2(",
    "affiche_range(",
    "compte_iterations(",
    "saisie_caracteres(",
    "compte_positifs(",
    "variance(",
    "incremente(",
    "nombre_ponctuation_dans_chaine(",
    "nombre_ponctuation_dans_liste(",
    "puissance(",
    "prefixes(",
    "generer_point(",
    "est_dans_cercle(",
    "generer_liste_points(",
    "calcul_pi(",

]

# TP7
FUNCTIONS_TP7_Prog = [
    "echantillonne(",
    "elements_indices_impairs(",
    "miroir(",
    "minimum(",
    "decoupage(",
    "premieres_occurrences(",
    "matchs(",
    "nom_domaines(",
    "max_identiques(",
    "suffixes(",
    "resume(",
    "ajout_separateur(",
    "construit_mots("
    
]

FUNCTIONS_TP7_Manip = [
    "calcule_produit_cartesien1(",
    "calcule_produit_cartesien2(",
    "se_suivent("
]

# TP8
FUNCTIONS_TP8_Prog = [
    "# Jeu de Nim",
    "compte_motif(",
    "indice_maximum(",
    "moyenne_ponderee(",
    "addition_digit(",
    "addition(",
    "determine(",
    "supprime(",
    "filtre(",
    "nb_jours_avant_1m_blob(",
    "somme_chiffres(",
    "saisie_pseudo_avec_verification(" 
]

FUNCTIONS_TP8_Manip = [
    "multiplication(",
    "saisie_reponse(",
    "duree_atteinte_seuil(",
    "compte_elements_identiques(",
    "racine_entiere(",
    "saisie_entier_intervalle(",
    "compare(",
    "deviner_un_nombre(",
]

# TP9
FUNCTIONS_TP9_Prog = [
    "toutes_longueurs_impaires_while(",
    "toutes_longueurs_impaires_for(",
    "contient_chiffre_ou_minuscule_while(",
    "indice_positif_while(",
    "indice_positif_for(",
    "contient_nb_occurrences_ou_plus_while(",
    "contient_nb_occurrences_ou_plus_for(",
    "est_palindrome_while(",
    "est_palindrome_for(",
    "est_croissante_while(",
    "est_croissante_for(",
    "tous_differents_while(",
    "tous_differents_for(",
    "produit_vaut_n_while(",
    "produit_vaut_n_for(",
    "suffixe_somme_while(",
    "suffixe_somme_for(",
    "hexa_decimal(",
    "decimal_hexa(",
    "est_hexa(",
    "hexa_binaire(",
    "binaire_hexa(",
    "genere_hexa(",
    "genere_hexa_sans_begaiement(",

]

FUNCTIONS_TP9_Manip = [
    "contient_longue_chaine(",
    "tous_entier_intervalle(",
    "au_moins_2_oui(",
    "contiennent_car("
]

# TP10
FUNCTIONS_TP10_Manip = [
    "carre_1_au_centre(",
    "affecte("  
]

# TP11
FUNCTIONS_TP11_Manip = [
    "open(",
    "f1.write(",
    "f1.close(",
    "f2.write(",  
    "f2.writelines(",
    "f3.write(",
    "f3.close(",
    "f1.readlines(",
    "lentier(",
    "help(str.rstrip)",
    "rstrip("
]


# %% [markdown]
# Je redéfinis all_TP_functions_name.

# %% [markdown]
# lui ne change pas

# %%
FUNCTIONS_GAME = [
    "<trace>tictactoe.py</trace>",
    "<trace>puissance4.py</trace>",
    "<trace>jeu_2048.py</trace>",
    "<trace>binairo.py</trace>",
    "<trace>tectonic.py</trace>",
    "<trace>galaxies.py</trace>",
]

# %%
# All TP
all_TP_functions_name = {
    'note_UE.py' : ['# TP PROG semaine 1'] , 'pour_debogueur.py' : ['# TP PROG semaine 1'] , 'calcul_interets.py' : ['# TP PROG semaine 1'] , # TP1
    'fonctions.py': FUNCTIONS_TP2_Prog, 'mesure.py': [FUNCTIONS_TP2_Manip[0]], 'polynomes.py': FUNCTIONS_TP2_Manip[1:], # TP2
    'booleens.py' : FUNCTIONS_TP3_Prog, 'erreurs_multiples.py': FUNCTIONS_TP3_Manip[:4], 'manipulations.py' : FUNCTIONS_TP3_Manip[4:], # TP3
    'conditionnelles.py' : FUNCTIONS_TP4_Prog, 'categories.py' : FUNCTIONS_TP4_Manip[:4] , 'erreurs_cond.py' : FUNCTIONS_TP4_Manip[4:], # TP4
    'imprimerie.py' : [FUNCTIONS_TP5_Prog[0]], 'jeu_421.py' : FUNCTIONS_TP5_Prog[1:], "affichage.py" : [FUNCTIONS_TP5_Manip[0]], "echappement.py" : [FUNCTIONS_TP5_Manip[1]], "interactions_mystere.py" : [FUNCTIONS_TP5_Manip[2]], "saisies_diverses.py" : [FUNCTIONS_TP5_Manip[3]], "saison.py" : FUNCTIONS_TP5_Manip[4:], "saison_main.py" : FUNCTIONS_TP5_Manip[4:], # TP5
    "iterables_for.py" : FUNCTIONS_TP6_Prog , "debogueur-for.py" : FUNCTIONS_TP6_Manip[0:2], "activite_range.py": FUNCTIONS_TP6_Manip[2:], # TP6
    "iterable_indexation.py": FUNCTIONS_TP7_Prog, 'imbriquees.py':FUNCTIONS_TP7_Manip[:2], "elements_consecutifs.py": [FUNCTIONS_TP7_Manip[2]], "configurations_init_jeu_vie.py": ['configurations initiales pour jeu de la vie'], # TP7
    "while.py" : FUNCTIONS_TP8_Prog[1:], "jeu_nim.py" : [FUNCTIONS_TP8_Prog[0]], "erreurs_boucles_while.py" : FUNCTIONS_TP8_Manip[:5], "devinette.py" : FUNCTIONS_TP8_Manip[5:], # TP8
    "parcours_interrompu.py" : FUNCTIONS_TP9_Prog, "erreurs_boucles_while_suite.py" : FUNCTIONS_TP9_Manip, # TP9
    "erreurs_aliasing.py" : FUNCTIONS_TP10_Manip, # TP10
    "tictactoe.py" : [FUNCTIONS_GAME[0]], "puissance4.py" : [FUNCTIONS_GAME[1]], "jeu_2048.py" : [FUNCTIONS_GAME[2]], "binairo.py" : [FUNCTIONS_GAME[3]], "tectonic.py" : [FUNCTIONS_GAME[4]], "galaxies.py" : [FUNCTIONS_GAME[5]], "experimentations_fichiers.py" : FUNCTIONS_TP11_Manip # TP_GAME
    }


# %%
all_TP_functions_name

# %% [markdown]
# J'ai refait la fonction add_space.

# %%
all_TP_functions_name_sans_par = {'booleens.py': ['est_non_vide(',
  'est_reponse(',
  'est_beneficiaire(',
  'est_reponse_correcte(',
  'est_en_ete(',
  'est_nombre_mystere(',
  'ont_intersection_vide(',
  'intervalle1_contient_intervalle2(',
  'sont_intervalles_recouvrants']}


# %%

# %%
def add_possible_space_before_brace(functions_name:dict) -> dict:
    '''
    functions_name is a dictionary whose keys are filenames and values are list of function names of the kind 'repetition('

    Adds a regexpr that allows spaces or tabs before the '('. 
    '''
    dico = {}
    for key in functions_name:
        function_list = functions_name[key]
        new_list = []
        for name in function_list:
            res_split = name.split('(')
            name_without_brace = res_split[0]
            if len(res_split) == 1: # no (
                new_name = name_without_brace
            else:
                new_name = re.escape(name_without_brace) + r'[ \t]*\('
            new_list.append(new_name)
        dico[key] = new_list
    return dico


# %%
all_TP_functions_name_without_brace = add_possible_space_before_brace(all_TP_functions_name)
all_TP_functions_name_without_brace


# %% [markdown]
# J'ai ajouté un paramètre pour all_TP_functions_name_without_brace à la function. Attention la doc et les commentaires
# sont à revoir.

# %%
def find_filename_by_commandRan(all_TP_functions : dict, pattern: str, commandRan: str) -> str:

    """
    It gets a pattern : all filenames, and the codestate, it checks if it can find
    the name of the file in the codestate like the name between <trace></trace>
    if not if check the name of the function in codestate by calling find_filename_by_function_name.

    Args:
        pattern : All filesname.
        codestate : P_codeState or F_codeState of a row.

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """

    match_state = re.search(pattern, commandRan)

    if match_state: # if the name is in the P_codeState
        matched_filename = match_state.group()  # Extract the name
        return matched_filename

    else: # if the exact name is not in P_codeState and student might removed the name part, we check the match with the content
        filename_infere = find_filename_by_function_name(all_TP_functions,commandRan)
        
        # Remove to test
        #if filename_infere == '':
            #print("Filename not found!")
        return filename_infere


# %% [markdown]
# Je vérifie sur les appels qui nous embêtaient.

# %%
find_filename_by_commandRan(all_TP_functions_name_without_brace, pattern,"est_non_vide ('kl')\n")

# %%
find_filename_by_commandRan(all_TP_functions_name_without_brace, pattern,"est_non_vide ('')\n")

# %% [markdown]
# Je vérifie sur un codeState.

# %%
codeState_est_vide = '#exos de programation\ndef est_non_vide ( a:str )-> bool:\n    """ à_remplacer_par_ce_que_fait_la_fonction\n\n    Précondition : \n    Exemple(s) :\n    $$$ \n    """\n    a==(\'\')\n       '


# %%
find_filename_by_commandRan(all_TP_functions_name_without_brace, pattern, codeState_est_vide)

# %% [markdown]
# Je suppose que ce sont les lignes qui posaient souci.

# %%
df_clean[df_clean['_id.$oid'] == '66ed37fabd5a98b8f9da4354'][['filename','P_codeState','verb','commandRan']]

# %%
find_filename_by_commandRan(all_TP_functions_name_without_brace, pattern,"est_non_vide ('kl')\n")

# %%
df_clean[df_clean['_id.$oid'] == '66ed3929bd5a98b8f9da4482'][['filename','P_codeState','verb','commandRan']]

# %% [markdown]
# **Interpretation**
#
# By find_filename_by_codestate, I found filename for 10,481 files, that's not bad, but still there are 47,409 traces for Run.command, which doesn't have any filename_infere or values in P_codestate, these values will be treated in phase two.

# %% [markdown]
# ### Check empty filename_infere of **File.Open**

# %%
# Before
total_File_Open       = len(df_clean[df_clean['verb']  == 'File.Open'])
total_File_Open_empty = (df_clean[df_clean['verb'] == 'File.Open']['filename_infere'] == '').sum()
total_File_Open_nan   = df_clean[df_clean['verb'] == 'File.Open']['filename_infere'].isna().sum()

print(f"Total number of traces in File.Open : {total_File_Open}")
print(f"Total number of empty strings in filename_infere in File.Open : {total_File_Open_empty}")
print(f"Total number of None in filename_infere in File.Open : {total_File_Open_nan}")

# %% [markdown]
# ### Check empty filename_infere of **File.Save**

# %%
total_File_Save       = len(df_clean[df_clean['verb']  == 'File.Save'])
total_File_Save_empty = (df_clean[df_clean['verb'] == 'File.Save']['filename_infere'] == '').sum()
total_File_Save_nan   = df_clean[df_clean['verb'] == 'File.Save']['filename_infere'].isna().sum()

print(f"Total number of traces in File.Save : {total_File_Save}")
print(f"Total number of empty strings in filename_infere in File.Save : {total_File_Save_empty}")
print(f"Total number of None in filename_infere in File.Save : {total_File_Save_nan}")

# %% [markdown]
# ### Check empty filename_infere of **Docstring.Generate**

# %%
total_Docstring       = len(df_clean[df_clean['verb']  == 'Docstring.Generate'])
total_Docstring_empty = (df_clean[df_clean['verb'] == 'Docstring.Generate']['filename_infere'] == '').sum()
total_Docstring_nan   = df_clean[df_clean['verb'] == 'Docstring.Generate']['filename_infere'].isna().sum()

print(f"Total number of traces in Docstring.Generate : {total_Docstring}")
print(f"Total number of empty strings in filename_infere in Docstring.Generate : {total_Docstring_empty}")
print(f"Total number of None in filename_infere in Docstring.Generate : {total_Docstring_nan}")

# %%
df_clean[df_clean['verb'] == 'Docstring.Generate']['function']

# %% [markdown]
# Question: don't know how should I fill it.

# %% [markdown]
# ## Save new clean dataframe

# %%
df_clean[df_clean['_id.$oid'] == '66ed37fabd5a98b8f9da4354'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %%
df_clean[df_clean['_id.$oid'] == '66ed3929bd5a98b8f9da4482'][['filename_infere','filename','P_codeState','verb','commandRan']]

# %%
io_utils.write_csv(df_clean,INTERIM_DATA_DIR,None)
