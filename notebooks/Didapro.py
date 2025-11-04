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

# Essai pour mettre au propre et filtrer sur research_usage

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

df_raw = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='phase3_nettoyage_fichiere.csv')

# ## Tableur avec NIP, identifiants et niveau de prog des étudiant·es

df_admin_etud = io_utils.reading_dataframe(dir= RAW_DATA_DIR, file_name='identifiants_2425.csv')


# ## Merge des données

def ajout_colonnes(df:pd.DataFrame, df_admin:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un nouveau df qui ajoute au paramètre `df` la colonne "débutant", de type booléen, définie par :
    dans df_admin, l'"actor" commun à `df` et `df_admin` :
                  - a une valeur "NSI" != "NSI2"
                  - a une valeur "redoublant" == 'non'
    Ajoute aussi la colonne 'codeState' qui réunit 'P_codeState' et 'F_codeState'

    Args:
        df : le df initial, avec colone "actor"
        df_admin : le df avec colonne "actor", "NSI", "redoublant"
    """
    df_admin_copy = df_admin.copy()
    df_admin_copy['debutant'] = (df_admin_copy['NSI']!='NSI2') & (df_admin_copy['redoublant']=='non')
    df_admin_actor_debutants = df_admin_copy[['actor', 'debutant']]
    df_copy = df.copy()
    df_copy['codeState'] = df_copy['P_codeState'] + df_copy['F_codeState']
    df_copy['debutant'] = (df_copy.merge(df_admin_actor_debutants, on='actor', how='inner'))['debutant']
    return df_copy


df_deb = ajout_colonnes(df_raw, df_admin_etud)


# ## Filtrage sur research_usage

def propage_chgt_avis_research_OK(df:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un nouveau df dont le research_OK est propagé en arrière et en avant.
    """
    df_copy = df.copy()
    actor_non_research_usage = set(df[df['research_usage'] == '0.0']['actor'].unique())
    actor_oui_research_usage = set(df[df['research_usage'] == '1.0']['actor'].unique())
    actors_chgt_avis = actor_non_research_usage.intersection(actor_oui_research_usage)
    for actor in actors_chgt_avis:
        indexes = df[df['actor'] == actor].index
        df_copy.loc[indexes, 'research_usage'] = "1.0"
    return df_copy


# ## utils : nombre d'acteurs (y compris binômes)

def actors(df:pd.DataFrame) -> set:
    """
    Renvoie l'ens des acteurs du df, y compris binômes.
    """
    set_actor_df = set(df.actor)
    set_binome_df = set(df.binome)
    if '' in set_binome_df:
        set_binome_df.remove('')
    return set_actor_df.union(set_binome_df)


print(f"Le df après nettoyage contient {len(actors(df_raw))} acteurs et {len(df_raw)} lignes")

df_propag = propage_chgt_avis_research_OK(df_deb)

df = df_propag[df_propag['research_usage']!= '0.0']

print(f"Le df après RGPD contient {len(actors(df))} acteurs et binômes et {len(df)} lignes")


# Je ne comprends pas comment je peux avoir des chiffres aussi hauts avec autant d'étudiants ayant refusé la collecte ?
# À voir pour l'an prochain, là pas le temps.

def is_deb_def(df_admin:pd.DataFrame) -> pd.DataFrame:
    """
    Construit un DataFrame de colonne 'actor' et 'debutant'
    """
    df_admin_copy = df_admin.copy()
    df_admin_copy['debutant'] = (df_admin_copy['NSI']!='NSI2') & (df_admin_copy['redoublant']=='non')
    df_admin_actor_debutants = df_admin_copy[['actor', 'debutant']]
    return df_admin_actor_debutants


df_is_deb = is_deb_def(df_admin_etud)


def est_debutant(actor:str, df_is_deb:pd.DataFrame) -> bool:
    """
    Renvoie True ssi actor est "debutant" dans df_is_deb
    """
    return (df_is_deb[df_is_deb['actor']==actor]['debutant']==True).values[0]


est_debutant('noam.taibi.etu', df_is_deb)

# # Contexte de l'expérimentation

# ## Contenu des traces collectées

# Les informations collectées sont : l'identifiant universitaire de l'étudiant·e connecté·e (et de l'éventuel·le binôme, cf ci-dessous), les actions de lancement et fermeture de Thonny, d'ouverture et de sauvegarde de fichier, d'exécution du fichier ouvert dans l'éditeur (par le bouton débogueur, le bouton exécution du script courant, le bouton exécution des tests), de commandes exécutées dans la console, l'horodatage de l'action. 

# ## Contexte de collecte des traces

# Les traces d'activité des étudiant·es ne sont collectées que sur les ordinateurs des salles de l'université, pendant les TPs. On ne collecte donc pas les traces laissées par les étudiant·es quand ils travaillent chez eux ou en dehors de ces salles. On ne collecte pas non plus les traces des étudiant·es qui travaillent sur leur ordinateur personnel durant les TPs quand le nombre d'ordinateurs est insuffisant. Par ailleurs en début d'année certain·es étudiant·es doivent travailler en binôme sur le même ordinateur, les effectifs étant trop importants pour le nombre de machines. L'identifiant de l'étudiant qui n'est pas connecté est demandé à l'ouverture de Thonny et vérifié dans le LDAP. Chaque trace collectée compte alors pour les 2 étudiant·es, comme si la trace était dupliquée. Enfin les traces ne sont collectées qu'une fois l'inscription administrative des étudiant·es terminée, car nous ne collectons les traces que lorsque l'identifiant de l'étudiant·e apparaît dans le groupe Unix du portail (nous ne pouvons donc pas tracer l'activité certain·es étudiant·es - surtout des débutant·es - en début de semestre).
#
#
# Une autre UE utilise un peu thonny.
#
# Grosse phase de nettoyage durant laquelle on cherche à rattacher chaque trace à une activité pratiquée pendant le semestre. On se base essentiellement (quand la trace permet d'identifier un nom ou un contenu de fichier) sur le noms des fichiers, la forme de l'en-tête du fichier (pour les activités de programmation guidée le fichier à compléter et rendre est fourni, ce qui permet d'indiquer dans l'en-tête quelle est l'ativité concernée), le nom des fonctions présentes dans le fichier. Quand la trace concerne une interaction dans la console de Thonny, il est difficile de rattacher cette commande à une activité. On suppose se base alors sur les traces qui encadrent temporellement cette commande. Quand il n'est pas possible d'associer une activité à la trace, celle-ci est ignorée.  
#
# RGPD. 

# ## Contexte des activités réalisées

# La première semaine du semestre n'est pas prise en compte, car l'outil de test n'était pas utilisé l'année de la collecte. Ensuite on distingue 2 phases : 
#
# - 8 semaines durant lesquelles les étudiant·es effectuent des activités fortement cadrées (programmation guidée)
# - 3 semaines durant lesquelles les étudiant·es réalisent librement un gros TP consistant à réaliser un jeu en mode texte (programmation non guidée)
#
# Pour toutes ces activités un fichier à compléter est fourni, ce qui nous permet de les repérer dans les traces en nous basant sur le nom du fichier et les informations figurant dans le commentaire d'entête.
#
# ### TPs de programmation guidés
#
# Durant les premières semaine, les étudiant·es peuvent réaliser des activités de manipulation (du type de données étudié pendant la semaine, de l'outil de débogage, de recherche d'erreurs dans les fonctions fournies dans un fichier...). Ce ne sont pas des activités de programmation à proprement parler et les analyses ne les prennent pas en compte. 
#
# Les activités de programmation consistent à écrire des fonctions dont le nom est fourni, et dont la signature est fortement suggérée dans le fichier fourni à compléter. Les tests sont fournis au début, puis ils sont fournis de manière moins claire. Par exemple un test est donné et il est précisé dans les consignes qu'il faut en ajouter, soit des données de tests sont données sans syntaxe, soit rien n'est fourni.
#
# Dans la mesure où nous savons exactement quelles fonctions chercher dans les traces d'activités des étudiant·es, nous pouvons analyser la pratique du test par fonction. Nous pouvons aussi exclure de l'analyse les fonctions dont nous savons qu'elles ne sont pas testables (fonction impliquant des entrées-sorties ou de l'aléatoire, fonctions principales). Nous n'avons pas cherché à analyser si les étudiant·es essaient d'écrire des tests pour ces fonctions non testables.
#
# ### TPs de programmation non guidés
#
# Durant les 3 dernières semaines, les étudiant·es réalisent un jeu en mode texte pour lequel aucune indication n'est donnée à part la règle du jeu et des indications sur le niveau de difficulté. Plusieurs sujets sont proposés, tous basés sur ue grille 2D (tic-tac-toe, puissance 4, 2048, binairo, etc). Les sujets sont disponibles dès le début du semestre pour les NSI. Il est attendu que chacun·e programme le jeu de tic-tac-toe, estimé le jeu le moins difficile. 
#
# Pour ces activités non guidées le fichier fourni à compléter ne contient aucune indication de fonction à programmer. Ce fichier est quasiment vide et les étudiant·es ne voient parfois pas l'utilité de l'utiliser, ce qui nous empèche sans doute d'identifier une partie des activités réalisées dans des fichiers aux noms autres que ceux attendus. Nous ne pouvons pas analyser la pratique du test par fonction sans savoir quelles fonctions seront écrites ni si elles sont testables (les jeux impliquent un grand nombre d'interactions avec l'utilisateur, non testables). 
#
# Pour ces activités non guidées nous pouvons donc juste analyser la pratique du test liée à la programmation d'un jeu identifié par son nom de fichier.
#
#

# ## Composition de la promotion

# Le portail MI accueille des étudiant·es de tous horizons. Pour les bac français, la spécialité math est demandée. Pour les bac étrangers, les résultats de maths sont regardés. Aucune sélection n'est effectuée sur les compétences en programmation ni sur la maîtrise des outils numériques. Le portail accueille donc des étudiant·es ayant fait la spécialité NSI et connaissant à l'avance tout le contenu de l'UE, comme des étudiant·es n'ayant jamais ou très peu touché un ordinateur auparavant.

# Pour analyser la pratique du test en fonction du cursus antérieur, nous avons séparé la promotion en 2 groupes : 
#
# - les non débutant·s : étudiant·es ayant fait au moins un an de spécialité NSI (première ou première et terminale), doublants
# - les débutant·s : le reste de la promotion. Les étudiant·es issues de réorientation sont classés en débutant·es.

# # QR1 : les étudiants peuvent-ils se servir d'un outil de test adapté à des débutants en apprenant à programmer

# On se base sur les semaines durant lequelles les activités de programmation ont été guidées.
#
# Deux semaines seront traitées comme des cas particuliers : 
#
# - semaine 5 : la notion abordée est les interactions avec l'utilisateur (print et input, notion de programme principal, utilisation du bouton "exécuter le script courant" de Thonny). Une des séances de TP de la semaine est consacrée à une évaluation. Très peu de fonctions étaient testables et elles apparaissaient en toute fin de feuille d'exercice. Cette semaine n'est pas pertinente pour analyser la pratique du test. Par contre il est intéressant de regarder la pratique du test en semaine 6, après une semaine passée à ne pas écrire ni exécuter de tests.
# - semaine 8 : en plus des fonctions classiques, un jeu simple (jeu de Nim) était à programmer de manière non cadrée. Nous n'avons pas analysé les traces liées à ce jeu.

# ## Données générales sur les TPs guidés

TPS_SANS_SEM_5 = ['Tp2', 'Tp3', 'Tp4', 'Tp6', 'Tp7', 'Tp8', 'Tp9']


def df_TP_guides_prog(df:pd.DataFrame, liste_tp:list[str]) -> pd.DataFrame:
    """
    Renvoie un df qui contient uniquement des traces de TP_prog du df passé en param pour les tp de liste_tp.

    Args : 
        - df : le df initial
        - liste_tp : une liste de tps, par ex ['Tp2', 'Tp3', 'Tp4', 'TP5', 'Tp6', 'Tp7', 'Tp8', 'Tp9']
    """
    df_param = df.copy()
    df_res = pd.DataFrame()
    for tp in liste_tp:
        if tp == 'Tp8':
            df_tp = df_param[(df_param['TP'] == tp) & (df_param['Type_TP'] == 'TP_prog') & (df_param['filename_infere'] == 'while.py')]
        else:
            df_tp = df_param[(df_param['TP'] == tp) & (df_param['Type_TP'] == 'TP_prog')]
        df_res = pd.concat([df_res, df_tp], ignore_index=True)
    return df_res


def genere_donnees_presentation_TP_guides(df:pd.DataFrame) -> pd.DataFrame:
    """
    Produit un df avec les colonnes suivantes :
        - TP : le numéro du TP
        - nb_etud : le nombre d'étudiants ayant réalisé ce TP
        - nb_debutants : le nombre de débutants ayant réalisé ce TP
        - pourcentage_debutants : le pourcentage de débutants ayant réalisé ce TP

    Args:
        df : le df initial avec l'indication de cursus, colonnes 'TP', 'Type_TP', 'actor', 'binome', 'filename_infere', 'debutant'
    """
    df_param = df_TP_guides_prog(df, TPS_SANS_SEM_5)
    df_res = pd.DataFrame(columns=['TP', 'nb_etud', 'nb_debutants', 'pourcentage_debutants'])
    for tp in TPS_SANS_SEM_5:
        df_tp = df_param[df_param['TP'] == tp]
        df_tp_deb = df_tp[df_tp['debutant']==True]
        actors_set = actors(df_tp)
        actors_deb_set = actors(df_tp_deb)
        dict_tp = {'TP': [tp], 'nb_etud' : len(actors_set), 'nb_debutants' : len(actors_deb_set), 'pourcentage_debutants' : round(len(actors_deb_set)/len(actors_set)*100)}
        df_res = pd.concat([df_res, pd.DataFrame.from_dict(data=dict_tp)], ignore_index=True)
    return df_res


df_donnees_TP_guides = genere_donnees_presentation_TP_guides(df)

df_donnees_TP_guides


# Le nombre d'étudiant·es ayant réalisé en présentiel les TPs guidés oscille entre 152 et 173 selon la semaine. Parmi ces étudiant·es, le pourcentage d'étudiant·es débutant·es ayant réalisé en présentiel les TPs guidés oscille entre 53 et 58% selon la semaine.

def plot_TPs_guides_general(df_donnees_TP_guides:pd.DataFrame) -> None:
    """
    Args :
        df avec colonnes TP, nb_etud , nb_debutants
    """
    fig, ax = plt.subplots()
    bottom = np.zeros(len(TPS_SANS_SEM_5))
    serie_nb_etud = df_donnees_TP_guides['nb_etud']
    serie_nb_deb = df_donnees_TP_guides['nb_debutants']
    serie_nb_non_deb = serie_nb_etud - serie_nb_deb
    dico = {'débutants' : serie_nb_deb, 'non débutants' : serie_nb_non_deb}
    
    for labels, values in dico.items():
        p = ax.bar(TPS_SANS_SEM_5, values, 0.5, label=labels, bottom=bottom)
        bottom += values

        ax.bar_label(p, label_type='center')

    ax.set_title('Données générales TPs guidés')
    ax.legend()

    plt.show()


plot_TPs_guides_general(df_donnees_TP_guides)

# ## Analyse de la pratique du test pour les TPs guidés

# La pratique du test implique principalement 3 activités :
#
# - écrire des tests
# - exécuter ces tests une fois le code à tester écrit
# - interpréter le verdict des tests et agir en conséquence
#
# Dans ce travail nous n'analysons pas l'action qui suit l'exécution des tests. Nous regardons juste si le travail contient un ou des tests et si nous trouvons une trace de l'exécution de ces tests.
#
#

# ### Écriture de tests

# Les tests sont cherchés dans les fichiers récupérés dans les contenus d'éditeur. Pour un·e étudiant·e donné·e les traces contiennent de nombreux contenus d'éditeurs relatifs à un TP donné, qui représentent la chronologie du travail de l'étudiant·e. Il faut en choisir un. Le principe adopté ici est de prendre le contenu de l'éditeur qui a l'horodatage le plus récent et qu'on peut imaginer être le travail le plus abouti. 
#
# Pour extraire les tests écrits du code nous utilisons une fonctionnalité interne à L1Test qui nécessite d'analyser syntaxiquement le code Python. Ce n'est pas possible si l'étudiant·e a fait une erreur de syntaxe. L'algorithme est donc le suivant : on examine le contenu de l'éditeur le plus récent. Si on peut en extraire des tests, on le fait. Si on ne peut pas en extraire des tests, alors on cherche le contenu d'éditeur qui a l'horodatage le plus récent à l'exclusion du précédent, et on répète tant qu'il y a des contenus d'éditeur à examiner. L'inconvénient de notre approche est que nous excluons de notre analyse le travail des étudiant·es qui ne parviennent pas à maîtriser les aspects syntaxiques, mais le nombre de travaux exclus reste faible en regard du nombre total. Sur les TPs 2 à 9 nous avons exclu au pire 9 étudiant·es (TP8 : 9 travaux non analysables sur 155). Pour 5 de ces TPs on trouve que 100% des travaux exclus sont ceux de débutant·es, ce qui est cohérent avec la non maîtrise syntaxique du langage.
#
#
#
# /!\ on ne sait pas si, qd un étudiant n'a pas exécuté tous les tests écrits sur toutes les fonctions, ce qu'il se passe. Il a peut-être exécuté les tests d'une fonction seulement en utilisant le menu de L1Test.

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
    #"<trace>jeu_421.py</traceDans le cadre des TPs guidés, pour lesquels les fonctions à écrire sont connues, nous estimons qu'au niveau débutant une fonction est testée si au moins un test a été écrit. Nous pouvons regarder si, au sein d'un TP, les étudiant·es ont écrit un ou des tests pour chaque fonction, ou s'ils n'écrivent des tests pour aucune fonction.>",
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

PROG_FILENAMES_BY_TP = {
    'Tp2' : 'fonctions.py',
    'Tp3' : 'booleens.py',
    'Tp4' : 'conditionnelles.py',
    'Tp6' : 'iterables_for.py',
    'Tp7' : 'iterable_indexation.py',
    'Tp8' : 'while.py',
    'Tp9' : 'parcours_interrompu.py',    
}


def find_tests_in_codestate(source:str) -> dict:
    '''
    Returns a dictionnary which associates to each function found in `source` its number of tests (using l1test), 
    or None if `source` cannot be parsed either by Python or the l1test parser.
    
    Args:
        source is some codestate

    Returns:
        a dictionary of the kind {<function_name> : <test_number>:int} or None if `source` couldn't be parsed.
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
    Returns a dictionnary which associates to each function of `functions_tp` found in `codeState` its number of tests, 
    or None if the function could'nd be found in `codeState`.

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
    for func_name in functions_tp:
        if func_name in test_number:
            res[func_name] = test_number[func_name]
        else:
            res[func_name] = None
    return res


def find_tests_for_tp_tpprog_actor(actor:str, df:pd.DataFrame, tp:str, functions_names:dict, filename:str=None) -> tuple[pd.DataFrame, bool, bool]:
    """
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for student `actor` and `tp`, then looks repeatedly 
    for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

    - a DataFrame with columns 'actor', 'tp', 'function_name', 'tests_number' (int or None if not present in codestates), 'index' (index in df of the analyzed codeState)
    - a first bool, True if for student 'actor' the codeStates cannot be analyzed (Python or l1test syntax error) or codestates contain no function of functions_names
    - a second bool, True if for student 'actor' and this tp no codeState was found, or only empty codeStates

    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        actor: some actor (ex : 'truc.machin.etu')
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
        df_name_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & ((df['actor'] == actor) | (df['binome'] == actor))]
    else:
        df_name_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') \
                        & ((df['actor'] == actor) | (df['binome'] == actor)) \
                        & (df['filename_infere'] == filename)]
    df_codestate_nonempty = df_name_tp[df_name_tp['codeState'] != '']
    if len(df_codestate_nonempty) == 0:
            return None, False, True
    else:
        # look for most recent parsable codeState
        timestamps = df_codestate_nonempty['timestamp.$date'].copy() # pour être sûre de ne pas modifier le df initial
        found = False # found codeState with functions not all unfoundable
        while not timestamps.empty and not found: 
            index_of_timestamp_max = timestamps.idxmax() # index of timestamp most recent
            most_recent_codeState = df_name_tp.loc[index_of_timestamp_max]['codeState']
            dict_tests = find_tests_in_codestate_for_functions(most_recent_codeState, functions_names[tp])
            if dict_tests != None: # parseable
                col_functions = []
                col_tests_number = []
                for key, value in dict_tests.items(): # key : function_name, value : tests_number
                    col_functions.append(key)
                    col_tests_number.append(value)
                nb_rows = len(dict_tests) # number of functions
                if col_tests_number != [None]*nb_rows: # convenient codestate found, with at least one function inside
                    found = True
                    col_actors = [actor] * nb_rows
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
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for all students of `tp`, then looks 
    repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

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
        - df_tests_tp is a DataFrame of columns 'actor', 'tp', 'function_name', 'tests_number', 'index'
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
        df_name, cannot_analyze_codestate, empty_codestates = find_tests_for_tp_tpprog_actor(name, df, tp, functions_names, filename)
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
        
        in columns 'test_number': 0 means no tests, None ou NaN ds pandas means function not found   
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


df_tests_number_tp_prog, _, _ =  find_tests_for_all_tp_tpprog(df, PROG_FUNCTIONS_NAME_BY_TP)


def ajout_debutant_admin(df:pd.DataFrame, df_admin:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un nouveau df qui ajoute au paramètre `df` la colonne "débutant", de type booléen, définie par :
    dans df_admin, l'"actor" commun à `df` et `df_admin` :
                  - a une valeur "NSI" != "NSI2"
                  - a une valeur "redoublant" == 'non'

    Args:
        df : le df initial, avec colone "actor"
        df_admin : le df avec colonne "actor", "NSI", "redoublant"
    """
    df_admin_copy = df_admin.copy()
    df_admin_copy['debutant'] = (df_admin_copy['NSI']!='NSI2') & (df_admin_copy['redoublant']=='non')
    df_admin_actor_debutants = df_admin_copy[['actor', 'debutant']]
    df_copy = df.copy()
    #df_copy['codeState'] = df_copy['P_codeState'] + df_copy['F_codeState']
    df_copy['debutant'] = (df_copy.merge(df_admin_actor_debutants, on='actor', how='inner'))['debutant']
    return df_copy


def merge_debutant(df:pd.DataFrame, df_is_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un nouveau df qui ajoute au paramètre `df` la colonne "débutant", de type booléen, définie dans df_is_deb.

    Args:
        df : initial ou autre, contient la colonne "actor"
        df_is_deb : colonnes 'actor' et 'debutant'
    """
    df_copy = df.copy()
    df_deb_copy = df_is_deb.copy()
    df_copy['debutant'] = (df_copy.merge(df_is_deb, on='actor', how='inner'))['debutant']
    return df_copy


df_tests_number_tp_prog_deb = merge_debutant(df_tests_number_tp_prog, df_is_deb)


def select_debutants(actors:list[str], df_is_deb:pd.DataFrame) -> list[str]:
    """
    Renvoie les débutants contenus dans `actors`, ssur la foi de `df_is_deb` 
    Args : 
        df_is_deb : df avec colonnes 'actor' et 'debutant' (bool)
    """
    df_param = df_is_deb.copy()
    df_select_deb = df_param[df_param['actor'].isin(actors)]
    res = list(df_select_deb[df_select_deb['debutant']==True]['actor'])
    for actor in res:
        assert df[df['actor']==actor]['debutant'].all()
    return res



def actors_par_pratique_ecriture_tests(df_tests_number:pd.DataFrame) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str]]:
    '''
    Renvoie 
        - la liste des étudiants ayant testé toutes les fonctions qu'ils ont écrites
        - la liste des étudiants n'ayant testé aucune fonction qu'ils ont écrite
        - la liste des étudiants qui ont testé au moins une fonction mais pas toutes les fonctions 
        - la liste des étudiants *débutants* ayant testé toutes les fonctions qu'ils ont écrites
        - la liste des étudiants *débutants* n'ayant testé aucune fonction qu'ils ont écrite
        - la liste des étudiants *débutants* qui ont testé au moins une fonction mais pas toutes les fonctions

    Args:
        df_tests_number : dataframe avec colonnes actor et tests_number issu d'un appel à find_tests_xxxx
    '''
    df_tests_number_sans_nan = df_tests_number.copy() # au cas où
    df_tests_number_sans_nan = df_tests_number_sans_nan[pd.notna(df_tests_number_sans_nan['tests_number'])]
    df_tests_number_sans_nan['tests_number_nul'] = df_tests_number_sans_nan['tests_number'].map(lambda x : x == 0)
    df_tests_number_sans_nan['tests_number_not_nul'] = df_tests_number_sans_nan['tests_number'].map(lambda x : x > 0)
    df_tests_number_sans_nan_deb = df_tests_number_sans_nan[df_tests_number_sans_nan['debutant']==True]
    # etud qui testent toutes les fonctions écrites
    df_tests_number_avec_tous_tests_interm = df_tests_number_sans_nan.groupby(['actor']).tests_number_not_nul.all()
    df_tests_number_avec_tous_tests = df_tests_number_avec_tous_tests_interm[df_tests_number_avec_tous_tests_interm==True]
    # etud debutants qui testent toutes les fonctions écrites
    df_tests_number_avec_tous_tests_interm_deb = df_tests_number_sans_nan_deb.groupby(['actor']).tests_number_not_nul.all()
    df_tests_number_avec_tous_tests_deb = df_tests_number_avec_tous_tests_interm_deb[df_tests_number_avec_tous_tests_interm_deb==True]
    # etud qui ne testent aucune fonction écrite
    df_tests_number_avec_0_test_interm = df_tests_number_sans_nan.groupby(['actor']).tests_number_nul.all()
    df_tests_number_avec_0_test = df_tests_number_avec_0_test_interm[df_tests_number_avec_0_test_interm==True]
    # etud debutants qui ne testent aucune fonction écrite
    df_tests_number_avec_0_test_interm_deb = df_tests_number_sans_nan_deb.groupby(['actor']).tests_number_nul.all()
    df_tests_number_avec_0_test_deb = df_tests_number_avec_0_test_interm_deb[df_tests_number_avec_0_test_interm_deb==True]
    # etud qui testent qq fonctions mais pas toutes
    df_tests_numbers_qq_tests_interm = df_tests_number_sans_nan.groupby(['actor']).tests_number_not_nul.any()
    df_tests_numbers_qq_tests = df_tests_numbers_qq_tests_interm[df_tests_numbers_qq_tests_interm==True]
    actors_qq_fonc_testees = list(set(df_tests_numbers_qq_tests.index).difference(set(df_tests_number_avec_tous_tests.index)))
    # etud debutants qui testent qq fonctions mais pas toutes
    df_tests_numbers_qq_tests_interm_deb = df_tests_number_sans_nan_deb.groupby(['actor']).tests_number_not_nul.any()
    df_tests_numbers_qq_tests_deb = df_tests_numbers_qq_tests_interm_deb[df_tests_numbers_qq_tests_interm_deb==True]
    actors_qq_fonc_testees_deb = list(set(df_tests_numbers_qq_tests_deb.index).difference(set(df_tests_number_avec_tous_tests_deb.index)))
    assert len(list(df_tests_number_avec_tous_tests.index)) + len(list(df_tests_number_avec_0_test.index)) + len(actors_qq_fonc_testees) == len(df_tests_number.actor.unique())
    actors_toutes_fonc_testees = list(df_tests_number_avec_tous_tests.index)
    actors_deb_toutes_fonc_testees = list(df_tests_number_avec_tous_tests_deb.index)
    assert set(actors_deb_toutes_fonc_testees) == set(select_debutants(actors_toutes_fonc_testees, df_is_deb))
    actors_aucune_fonction_testee = list(df_tests_number_avec_0_test.index)
    actors_deb_aucune_fonction_testee = list(df_tests_number_avec_0_test_deb.index)
    assert set(actors_deb_aucune_fonction_testee) == set(select_debutants(actors_aucune_fonction_testee, df_is_deb))
    assert set(actors_qq_fonc_testees_deb) == set(select_debutants(actors_qq_fonc_testees, df_is_deb))
    return actors_toutes_fonc_testees, actors_aucune_fonction_testee, actors_qq_fonc_testees, \
        actors_deb_toutes_fonc_testees, actors_deb_aucune_fonction_testee, actors_qq_fonc_testees_deb


actors_toutes_fonc_testees, actors_aucune_fonction_testee, actors_qq_fonc_testees,\
actors_deb_toutes_fonc_testees, actors_deb_aucune_fonction_testee, actors_deb_qq_fonc_testees \
= actors_par_pratique_ecriture_tests(df_tests_number_deb)


def genere_donnees_nombre_tests_ecrits_tp_guides(df:pd.DataFrame, functions_names:dict, df_is_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un DataFrame avec colonnes : 'Tps', 'Nb etud', 'Nb etud analyse impossible', 'Nb etud avec tests présents', 'Nb etud avec tests présents pour toute fonction écrite', \
                                    'Nb etud avec aucun test', 'Nb etud avec tests présents pour qq fonctions écrites'

    Args :
        - df : df initial
        - function_names : dico which associates to each Tp identifier a list of functions name (ex : functions_names['Tp2] is ['foo1', 'foo2', 'foo3'])
        - df_is_deb : columns 'actor' et 'debutant'
    """
    df_plot = pd.DataFrame(columns=['Tps', 'Nb etud', 'Nb debutants', 'Nb non debutants', 'Nb debutants analyse possible',\
                                    'Nb non debutants analyse possible',
            'Nb etud analyse impossible', 'Pourcentage debutants (analyse impossible)', 'Nb etud avec tests présents',\
            'Pourcentage debutants (avec tests présents)', 'Nb etud avec tests présents pour toute fonction écrite',   \
            'Nb debutants avec tests présents pour toute fonction écrite', 'Nb non debutants avec tests présents pour toute fonction écrite',\
            'Pourcentage debutants (avec tests présents pour toute fonction écrite)', \
            'Nb etud sans test', 'Nb debutants sans test', 'Nb non debutants sans test', 'Pourcentage debutants (sans test)', \
            'Nb etud avec tests présents pour qq fonctions écrites', \
            'Pourcentage debutants (avec tests présents pour qq fonctions écrites)'])            
                            
    for tp in TPS_SANS_SEM_5:
        if tp == 'Tp8':
            df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp  = find_tests_for_tp_tpprog(df, 'Tp8', functions_names, filename='while.py')
            actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == 'while.py')]['actor']
            column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == 'while.py')]['binome'] 
        else:
            df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp  = find_tests_for_tp_tpprog(df, tp, functions_names)
            actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['actor']
            column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['binome']
        all_students_tp  = set(actor_column_tp).union(set(column_binome_tp))
        deb_students_tp = select_debutants(all_students_tp, df_is_deb)
        non_deb_students_tp = list(all_students_tp - set(deb_students_tp))
        if '' in all_students_tp:
            all_students_tp.remove('')
        df_tests_tp_avec_deb = merge_debutant(df_tests_tp, df_is_deb)
        etud_testant_toute_fonction_ecrite_tp, etud_testant_aucune_fonction_ecrite_tp, etud_qq_tests_fonction_ecrite_tp, \
            etud_deb_testant_toute_fonction_ecrite_tp, etud_deb_testant_aucune_fonction_ecrite_tp, etud_deb_qq_tests_fonction_ecrite_tp \
                = actors_par_pratique_ecriture_tests(df_tests_tp_avec_deb)
        assert(set(etud_deb_testant_toute_fonction_ecrite_tp) == set(select_debutants(etud_testant_toute_fonction_ecrite_tp, df_is_deb)))
        etud_non_deb_testant_aucune_fonction_ecrite_tp = list(set(etud_testant_aucune_fonction_ecrite_tp) - set(etud_deb_testant_aucune_fonction_ecrite_tp))
        etud_non_deb_testant_toute_fonction_ecrite_tp = list(set(etud_testant_toute_fonction_ecrite_tp) - set(etud_deb_testant_toute_fonction_ecrite_tp))
        etud_analyse_impossible = cannot_analyze_codestate_students_tp + empty_codestate_students_tp
        etud_deb_analyse_impossible:list = select_debutants(etud_analyse_impossible, df_is_deb)
        etud_non_deb_analyse_impossible:list = list(set(etud_analyse_impossible) - set(etud_deb_analyse_impossible))
        etud_deb_analyse_possible:list = list(set(deb_students_tp) - set(etud_deb_analyse_impossible))
        etud_non_deb_analyse_possible:list = list(set(non_deb_students_tp) - set(etud_non_deb_analyse_impossible))
        etud_avec_tests:list = etud_testant_toute_fonction_ecrite_tp + etud_qq_tests_fonction_ecrite_tp
        etud_deb_avec_tests:list = select_debutants(etud_avec_tests, df_is_deb)
        df_plot_tp = pd.DataFrame({'Tps': [tp],\
                                    'Nb etud': len(all_students_tp),\
                                    'Nb debutants': len(deb_students_tp),\
                                    'Nb non debutants': len(non_deb_students_tp),\
                                    'Nb debutants analyse possible': len(etud_deb_analyse_possible), \
                                    'Nb non debutants analyse possible': len(etud_non_deb_analyse_possible), \
                                    'Nb etud analyse impossible': len(etud_analyse_impossible),\
                                    'Pourcentage debutants (analyse impossible)': round(len(etud_deb_analyse_impossible)/len(etud_analyse_impossible)*100),\
                                    'Nb etud avec tests présents': len(etud_avec_tests),\
                                    'Pourcentage debutants (avec tests présents)': round(len(etud_deb_avec_tests)/len(etud_avec_tests)*100),\
                                    'Nb etud avec tests présents pour toute fonction écrite' : len(etud_testant_toute_fonction_ecrite_tp),\
                                    'Nb debutants avec tests présents pour toute fonction écrite' : len(etud_deb_testant_toute_fonction_ecrite_tp),\
                                    'Nb non debutants avec tests présents pour toute fonction écrite' : len(etud_non_deb_testant_toute_fonction_ecrite_tp),\
                                     'Pourcentage debutants (avec tests présents pour toute fonction écrite)' : \
                                       round(len(etud_deb_testant_toute_fonction_ecrite_tp)/len(etud_testant_toute_fonction_ecrite_tp)*100),\
                                    'Nb etud sans test' : len(etud_testant_aucune_fonction_ecrite_tp),\
                                    'Nb debutants sans test' : len(etud_deb_testant_aucune_fonction_ecrite_tp),\
                                    'Nb non debutants sans test' : len(etud_non_deb_testant_aucune_fonction_ecrite_tp),\
                                    'Pourcentage debutants (sans test)' :\
                                       round(len(etud_deb_testant_aucune_fonction_ecrite_tp)/len(etud_testant_aucune_fonction_ecrite_tp)*100),\
                                    'Nb etud avec tests présents pour qq fonctions écrites' : len(etud_qq_tests_fonction_ecrite_tp),\
                                    'Pourcentage debutants (avec tests présents pour qq fonctions écrites)' :\
                                       round(len(etud_deb_qq_tests_fonction_ecrite_tp)/len(etud_qq_tests_fonction_ecrite_tp)*100)
                                  })
        df_plot = pd.concat([df_plot, df_plot_tp], ignore_index=True)
    return df_plot


df_plot_nombre_tests_ecrits_tp_guides = genere_donnees_nombre_tests_ecrits_tp_guides(df, PROG_FUNCTIONS_NAME_BY_TP, df_is_deb)
df_plot_nombre_tests_ecrits_tp_guides


def calcule_infos_tests_ecrits_sans_deb(df_plot_nombre_tests_ecrits_tp_guides:pd.DataFrame) -> pd.DataFrame:
    """
    Args :
        df_plot_nombre_tests_ecrits_tp_guides : colonnes 'Nb etud', 'Nb etud analyse impossible', 'Nb etud avec tests présents pour toute fonction écrite',
            'Nb etud avec tests présents', 'Nb etud sans test', 'Nb etud avec tests présents pour qq fonctions écrites'
    """

    df_plot_nombre_tests_ecrits_tp_guides_sans_deb = df_plot_nombre_tests_ecrits_tp_guides.copy()
    df_plot_nombre_tests_ecrits_tp_guides_sans_deb['Nb etud travaux analysables'] = df_plot_nombre_tests_ecrits_tp_guides_sans_deb['Nb etud'] - df_plot_nombre_tests_ecrits_tp_guides_sans_deb['Nb etud analyse impossible']
    df_plot_nombre_tests_ecrits_tp_guides_sans_deb['pourcentage pour toute fonction (travaux analysables)'] = df_plot_nombre_tests_ecrits_tp_guides_sans_deb['Nb etud avec tests présents pour toute fonction écrite']/df_plot_nombre_tests_ecrits_tp_guides_sans_deb['Nb etud travaux analysables']*100
    return df_plot_nombre_tests_ecrits_tp_guides_sans_deb[['Tps', 'Nb etud', 'Nb etud travaux analysables', 'Nb etud avec tests présents',\
                                           'Nb etud avec tests présents pour toute fonction écrite', 'pourcentage pour toute fonction (travaux analysables)',\
                                               'Nb etud sans test', 'Nb etud avec tests présents pour qq fonctions écrites']]


calcule_infos_tests_ecrits_sans_deb(df_plot_nombre_tests_ecrits_tp_guides)


def plot_tests_ecrits_TP_guides(df_tests_ecrits_tp_guides:pd.DataFrame) -> None:
    """
    Args :
        df avec colonnes 'Tps', 'Nb etud travaux analysables', 'Nb etud avec tests présents', 'Nb etud sans test' 
    """
    fig, ax = plt.subplots()
    bottom = np.zeros(len(TPS_SANS_SEM_5))
    serie_nb_avec_tests = df_tests_ecrits_tp_guides['Nb etud avec tests présents']
    serie_nb_sans_test = df_tests_ecrits_tp_guides['Nb etud sans test']
    dico = {'avec au moins un test' : serie_nb_avec_tests, 'sans test' : serie_nb_sans_test}
    
    for labels, values in dico.items():
        p = ax.bar(TPS_SANS_SEM_5, values, 0.5, label=labels, bottom=bottom)
        bottom += values

        ax.bar_label(p, label_type='center')

    ax.set_title('TPs guidés : étudiants dont le code est analysable')
    ax.legend()

    plt.show()


plot_tests_ecrits_TP_guides(calcule_infos_tests_ecrits_sans_deb(df_plot_nombre_tests_ecrits_tp_guides))


def plot_tests_ecrits_par_fonctions_TP_guides(df_tests_ecrits_tp_guides:pd.DataFrame) -> None:
    """
    Args :
        df avec colonnes 'Tps', Nb etud avec tests présents',  'Nb etud avec tests présents pour toute fonction écrite'
    """
    fig, ax = plt.subplots()
    bottom = np.zeros(len(TPS_SANS_SEM_5))
    serie_nb_avec_tests = df_tests_ecrits_tp_guides['Nb etud avec tests présents']
    serie_nb_avec_tests_pour_toute_fonction = df_tests_ecrits_tp_guides['Nb etud avec tests présents pour toute fonction écrite']
    serie_nb_avec_tests_pour_certaines_fonctions = df_tests_ecrits_tp_guides['Nb etud avec tests présents pour qq fonctions écrites']
    dico = {'Pour chaque fonction' : serie_nb_avec_tests_pour_toute_fonction, 'Pour certaines fonctions' : serie_nb_avec_tests_pour_certaines_fonctions}
    
    for labels, values in dico.items():
        p = ax.bar(TPS_SANS_SEM_5, values, 0.5, label=labels, bottom=bottom)
        bottom += values

        ax.bar_label(p, label_type='center')

    ax.set_title('TPs guidés : étudiants ayant écrit au moins un test')
    ax.legend()

    plt.show()


plot_tests_ecrits_par_fonctions_TP_guides(calcule_infos_tests_ecrits_sans_deb(df_plot_nombre_tests_ecrits_tp_guides))


# Le premier graphique montre que quasiment tous les travaux analysables (c'est à dire un fichier Python syntaxiquement correct contenant des fonctions) contiennent au moins un test. Comme pour les TPs guidés nous connaissons les fonctions à programmer, nous pouvons regarder quelle proportion des fonctions écrites et testables contiennent des tests. Le second graphique montre que la plupart des étudiant·es écrivent des tests pour toutes les fonctions testables qu'ils ou elles ont programmé. On note un tassement modéré pour le TP9 : environ 77% des étudiant·es ayant écrit des tests l'ont fait pour toutes les fonctions. À noter que nous n'avons pas regardé combien de fonctions ont été écrites par les étudiant·es : du point de vue de l'écriture des tests une étudiante qui n'aura écrit que 4 fonctions avec tests durant les séances est considérée de la même manière qu'une étudiante ayant écrit 10 fonctions avec tests, mais de manière différente d'une étudiante ayant écrit 12 fonctions sans aucun test. 

# ### Impact du cursus antérieur sur l'écriture des tests

# On regarde la proportion de débutant·es dans les cas extrèmes :
#
# - toute fonction testée
# - aucun test
#
# Mais cette proportion doit être rapportée à la proportion de débutant·es pour les travaux analysables
#
# Dc on fait pour chaque TP une barre:
#
# - nb debutants analysables
# - nb débutants toute fonction testée
# - nb débutants aucun test  

def calcule_infos_tests_ecrits_avec_deb(df_nb_tests_ecrits_tp_guides_avec_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Args :
        df_plot_nombre_tests_ecrits_tp_guides : colonnes Tps', 'Nb debutants analyse possible',
                                                    'Nb debutants avec tests présents pour toute fonction écrite',
                                                    'Nb debutants sans test'
    """
    df_local_select =  df_nb_tests_ecrits_tp_guides_avec_deb[['Tps', 'Nb debutants analyse possible',\
                                                    'Nb debutants avec tests présents pour toute fonction écrite',\
                                                    'Nb debutants sans test']].copy()
    df_local_select['Pourcentage deb avec tests présents pour toute fonction écrite'] = \
        df_local_select['Nb debutants avec tests présents pour toute fonction écrite']/df_local_select['Nb debutants analyse possible']*100
    df_local_select['Pourcentage deb sans test'] = \
        df_local_select['Nb debutants sans test']/df_local_select['Nb debutants analyse possible']*100
    return df_local_select


calcule_infos_tests_ecrits_avec_deb(df_plot_nombre_tests_ecrits_tp_guides)


def calcule_infos_tests_ecrits_avec_non_deb(df_nb_tests_ecrits_tp_guides_avec_non_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Args :
        df avec colonnes Tps', 'Nb non debutants analyse possible',
                                                    'Nb non debutants avec tests présents pour toute fonction écrite',
                                                    'Nb non debutants sans test'
    """
    df_local_select =  df_nb_tests_ecrits_tp_guides_avec_non_deb[['Tps', 'Nb non debutants analyse possible',\
                                                    'Nb non debutants avec tests présents pour toute fonction écrite',\
                                                    'Nb non debutants sans test']].copy()
    df_local_select['Pourcentage non deb avec tests présents pour toute fonction écrite'] = \
        df_local_select['Nb non debutants avec tests présents pour toute fonction écrite']/df_local_select['Nb non debutants analyse possible']*100
    df_local_select['Pourcentage non deb sans test'] = \
        df_local_select['Nb non debutants sans test']/df_local_select['Nb non debutants analyse possible']*100
    return df_local_select


calcule_infos_tests_ecrits_avec_non_deb(df_plot_nombre_tests_ecrits_tp_guides)


def plot_tests_ecrits_deb(df_tests_ecrits_deb:pd.DataFrame) -> None:
    """
    Args :
        df avec colonnes 'Tps', 'Nb debutants analyse possible',
                                                    'Nb debutants avec tests présents pour toute fonction écrite',
                                                    'Nb debutants sans test'
    """
    df_local = df_tests_ecrits_deb[['Tps', 'Nb debutants analyse possible', \
                                    'Nb debutants avec tests présents pour toute fonction écrite', 'Nb debutants sans test']].copy()
    df_local = df_local.rename(columns={'Nb debutants analyse possible':'dont les travaux sont analysables',\
                                       'Nb debutants avec tests présents pour toute fonction écrite': 'ayant écrit au moins un test\n pour toute fonction écrite',\
                                        'Nb debutants sans test': 'sans test'})
    df_local.set_index('Tps').plot(kind='bar', figsize=(12, 6))

    plt.title("Étudiant·es débutant·es : écriture de tests")
    plt.ylabel("Nombre d'étudiant·es débutant·es")
    plt.xlabel("TP")
    plt.xticks(rotation=45)
    plt.legend(title="Nombre de débutant·es")
    plt.tight_layout()
    plt.show()


def plot_tests_ecrits_non_deb(df_tests_ecrits_non_deb:pd.DataFrame) -> None:
    """
    Args :
        df avec colonnes 'Tps', 'Nb non debutants analyse possible',
                                                    'Nb nondebutants avec tests présents pour toute fonction écrite',
                                                    'Nb non debutants sans test'
    """
    df_local = df_tests_ecrits_non_deb[['Tps', 'Nb non debutants analyse possible', \
                                        'Nb non debutants avec tests présents pour toute fonction écrite', \
                                        'Nb non debutants sans test']].copy()
    df_local = df_local.rename(columns={'Nb non debutants analyse possible':'dont les travaux sont analysables',\
                                       'Nb non debutants avec tests présents pour toute fonction écrite': 'ayant écrit au moins un test\n pour toute fonction écrite',\
                                        'Nb nondebutants sans test': 'sans test'})
    df_local.set_index('Tps').plot(kind='bar', figsize=(12, 6))

    plt.title("Étudiant·es non débutant·es : écriture de tests")
    plt.ylabel("Nombre d'étudiant·es non débutant·es")
    plt.xlabel("TP")
    plt.xticks(rotation=45)
    plt.legend(title="Nombre de non débutant·es")
    plt.tight_layout()
    plt.show()


plot_tests_ecrits_deb(calcule_infos_tests_ecrits_avec_deb(df_plot_nombre_tests_ecrits_tp_guides))
plot_tests_ecrits_non_deb(calcule_infos_tests_ecrits_avec_non_deb(df_plot_nombre_tests_ecrits_tp_guides))


# En comparant le pourcentage d'étudiant·es débutant·es et non débutant·es qui écrivent au moins un test pour toutes les fonctions écrites, il ne ressort rien de particulier. Les pourcentages sont similaires à quelques unités. Pour les étudiant·es qui n'écrivent aucun test : les pourcentages sont plus élevés pour les débutant·es mais restent bas (autour de 4.4% pour le TP3 et 4.3% pour le TP6). On ne peut donc pas dire que le cursus des étudiant·es (vrais débutant·es ou étudiant·es ayant déjà pratiqué de la programmationPython  

# # QR2 : les étudiants prennent-ils l'habitude de tester leurs programmes ?

# # Pistes de recherche

# Analyse :
#
# - quelle action suite à un test en échec ou erreur ?
# - les tests écrits par les étudiant·es sont-ils pertinents ?
# - les étudiant·es se contentent-ils de recopier en les adaptant les données de test suggérées par l'énoncé, quand il y en a ?
# - Peut-on dégager des classes de comportements ? Par ex j'écris les tests puis le code puis je teste, ou j'écris tout le code de toutes les fonctions puis je teste sans procéder par approche itérative ?
# - quand un test est en échec, est-ce le plus souvent un test mal écrit ou un code faux ?
# - quelle proportion de code avec des tests qui passent est néanmoins faux (TPs guidés) ?
# - écriture des tests avant le code ou ajouts des tests une fois une tout est testé manuellement ?
#
# Analyse qualitative :
#
# - quelle perception les étudiant·es ont de l'outil L1Test ?
# - quelle perception les étudiant·es ont du test : aide ou boulet consommeur de temps ? pensent-ils que si leurs tests passent alors leur code est correct ?
#
# Intégration du test dans les référentiels de programmation.


