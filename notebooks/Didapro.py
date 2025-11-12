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


# quasiment pareil ajout_colonnes, sauf le codeState...
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
    df_copy['debutant'] = (df_copy.merge(df_admin_actor_debutants, on='actor', how='inner'))['debutant']
    return df_copy


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



# finalement ne sert pas
def est_debutant(actor:str, df_is_deb:pd.DataFrame) -> bool:
    """
    Renvoie True ssi actor est "debutant" dans df_is_deb
    """
    return (df_is_deb[df_is_deb['actor']==actor]['debutant']==True).values[0]


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
# Les activités de programmation consistent à écrire des fonctions dont le nom est fourni, et dont la signature est fortement suggérée dans le fichier fourni à compléter. Les tests sont fournis au début, puis ils sont fournis de manière moins claire. Par exemple soit un test est donné et il est précisé dans les consignes qu'il faut en ajouter, soit des données de tests sont données sans syntaxe, soit rien n'est fourni.
#
# Dans la mesure où nous savons exactement quelles fonctions chercher dans les traces d'activités des étudiant·es, nous pouvons analyser la pratique du test par fonction. Nous pouvons aussi exclure de l'analyse les fonctions dont nous savons qu'elles ne sont pas testables (fonction impliquant des entrées-sorties ou de l'aléatoire, fonctions principales). Nous n'avons pas cherché à analyser si les étudiant·es essaient d'écrire des tests pour ces fonctions non testables.
#
# ### TPs de programmation non guidés
#
# Durant les 3 dernières semaines, les étudiant·es réalisent un jeu en mode texte pour lequel aucune indication n'est donnée à part la règle du jeu et des indications sur le niveau de difficulté. Le découpage en fonctions n'est pas donné dans le sujet. Plusieurs sujets sont proposés, tous basés sur ue grille 2D (tic-tac-toe, puissance 4, 2048, binairo, etc). Les sujets sont disponibles dès le début du semestre pour les NSI. Il est attendu que chacun·e programme le jeu de tic-tac-toe, estimé le jeu le moins difficile. 
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
# Pour extraire les tests écrits du code nous utilisons une fonctionnalité interne à L1Test qui nécessite d'analyser syntaxiquement le code Python. Ce n'est pas possible si l'étudiant·e a fait une erreur de syntaxe. L'algorithme est donc le suivant : on examine le contenu de l'éditeur le plus récent. Si on peut en extraire des tests, on le fait. Si on ne peut pas en extraire des tests, alors on cherche le contenu d'éditeur qui a l'horodatage le plus récent à l'exclusion du précédent, et on répète tant qu'il y a des contenus d'éditeur à examiner. L'inconvénient de notre approche est que nous excluons de notre analyse le travail des étudiant·es qui ne parviennent pas à maîtriser les aspects syntaxiques, mais le nombre de travaux exclus reste faible en regard du nombre total. Sur les TPs 2 à 9 nous avons exclu en moyenne 2.6% des travaux, avec un maximum à 5.8% pour le TP8. Les travaux exclus sont en moyenne à 90% des travaux de débutants (écart-type : 17), avec une valeur de 100% pour 5 des TPs. C'est cohérent avec la non maîtrise syntaxique du langage.
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

df_tests_number_tp_prog_deb = merge_debutant(df_tests_number_tp_prog, df_is_deb)


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
    # J'ai bien relu ce code, il est long mais compréhensible, il pourrait être découpé en 6 petites fonctions
    df_tests_number_sans_nan = df_tests_number.copy() # au cas où
    # Rappel : NaN pour le nb de tests qd la fonction n'existe pas dans le code analysé 
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
    # autres var résultat
    actors_toutes_fonc_testees = list(df_tests_number_avec_tous_tests.index)
    actors_deb_toutes_fonc_testees = list(df_tests_number_avec_tous_tests_deb.index)
    actors_aucune_fonction_testee = list(df_tests_number_avec_0_test.index)
    actors_deb_aucune_fonction_testee = list(df_tests_number_avec_0_test_deb.index)
    # Tient lieu de test
    assert len(list(df_tests_number_avec_tous_tests.index)) + len(list(df_tests_number_avec_0_test.index)) + len(actors_qq_fonc_testees) == len(df_tests_number.actor.unique())
    assert set(actors_deb_toutes_fonc_testees) == set(select_debutants(actors_toutes_fonc_testees, df_is_deb))
    assert set(actors_deb_aucune_fonction_testee) == set(select_debutants(actors_aucune_fonction_testee, df_is_deb))
    assert set(actors_qq_fonc_testees_deb) == set(select_debutants(actors_qq_fonc_testees, df_is_deb))
    return actors_toutes_fonc_testees, actors_aucune_fonction_testee, actors_qq_fonc_testees, \
        actors_deb_toutes_fonc_testees, actors_deb_aucune_fonction_testee, actors_qq_fonc_testees_deb


actors_toutes_fonc_testees, actors_aucune_fonction_testee, actors_qq_fonc_testees,\
actors_deb_toutes_fonc_testees, actors_deb_aucune_fonction_testee, actors_deb_qq_fonc_testees \
= actors_par_pratique_ecriture_tests(df_tests_number_tp_prog_deb)

# +
LBL_NB_ETUD = 'Nb étud'
LBL_NB_DEB = 'Nb débutants'
LBL_NB_NON_DEB = 'Nb non débutants'
LBL_NB_ETUD_ANALYSABLE = 'Nb étud analyse possible'
LBL_NB_ETUD_NON_ANALYSABLE = 'Nb étud analyse impossible'
LBL_PCT_NON_ANALYSABLE = 'Pourcentage étud analyse impossible'
LBL_NB_DEB_ANALYSABLE = 'Nb déb analyse possible'
LBL_NB_DEB_NON_ANALYSABLE = 'Nb déb analyse impossible'
LBL_NB_NON_DEB_ANALYSABLE = 'Nb non déb analyse possible'
LBL_NB_NON_DEB_NON_ANALYSABLE = 'Nb non déb analyse impossible'
LBL_PCT_DEB_NON_ANALYSABLE = 'Pourcentage débutants analyse impossible (an impossible)'
LBL_NB_ETUD_TESTS_PRESENTS = 'Nb étud avec tests présents'
LBL_NB_DEB_TESTS_PRESENTS = 'Nb débutants avec tests présents'
LBL_NB_NON_DEB_TESTS_PRESENTS = 'Nb non débutants avec tests présents'
LBL_PCT_TESTS_PRESENTS = 'Pourcentage avec tests présents (analyse possible)'
LBL_PCT_DEB_TESTS_PRESENTS = 'Pourcentage débutants avec tests présents (débutants an possible)'
LBL_PCT_NON_DEB_TESTS_PRESENTS = 'Pourcentage non débutants avec tests présents (non débutants an possible)'
LBL_NB_ETUD_TESTS_PRESENTS_TTES_FCTS = 'Nb étud avec tests présents pour toute fonction écrite'
LBL_NB_DEB_TESTS_PRESENTS_TTES_FCTS = 'Nb débutants avec tests présents pour toute fonction écrite'
LBL_NB_NON_DEB_TESTS_PRESENTS_TTES_FCTS = 'Nb non débutants avec tests présents pour toute fonction écrite'
LBL_PCT_TTES_FCTS = 'Pourcentage pour toute fonction (travaux analysables)'
LBL_PCT_TTES_FCTS_DEB = 'Pourcentage débutants avec tests présents pour toute fonction (déb travaux analysables)'
LBL_PCT_TTES_FCTS_NON_DEB = 'Pourcentage non débutants avec tests présents pour toute fonction (non déb travaux analysables)'
LBL_NB_ETUD_NO_TEST = 'Nb étud sans test'
LBL_NB_DEB_NO_TEST = 'Nb débutants sans test'
LBL_NB_NON_DEB_NO_TEST = 'Nb non débutants sans test'
LBL_PCT_DEB_NO_TEST = 'Pourcentage débutants sans test (déb travaux analysables)'
LBL_PCT_NON_DEB_NO_TEST = 'Pourcentage non débutants sans test (non déb travaux analysables)'
NB_ETUD_TESTS_QQ_FONCTIONS = 'Nb étud avec tests présents pour qq fonctions écrites'

COLUMNS_STAT_ECR_TESTS = ['Tps',
                          LBL_NB_ETUD,
                          LBL_NB_DEB,
                          LBL_NB_NON_DEB,
                          LBL_NB_ETUD_ANALYSABLE,
                          LBL_NB_ETUD_NON_ANALYSABLE,
                          LBL_NB_DEB_ANALYSABLE,
                          LBL_NB_DEB_NON_ANALYSABLE,
                          LBL_NB_NON_DEB_ANALYSABLE,
                          LBL_NB_NON_DEB_NON_ANALYSABLE,
                          LBL_PCT_NON_ANALYSABLE,
                          LBL_PCT_DEB_NON_ANALYSABLE,
                          LBL_NB_ETUD_TESTS_PRESENTS,
                          LBL_NB_DEB_TESTS_PRESENTS,
                          LBL_NB_NON_DEB_TESTS_PRESENTS,
                          LBL_PCT_TESTS_PRESENTS,
                          LBL_PCT_DEB_TESTS_PRESENTS,
                          LBL_PCT_NON_DEB_TESTS_PRESENTS,
                          LBL_NB_ETUD_TESTS_PRESENTS_TTES_FCTS,
                          LBL_NB_DEB_TESTS_PRESENTS_TTES_FCTS,
                          LBL_NB_NON_DEB_TESTS_PRESENTS_TTES_FCTS,
                          LBL_PCT_TTES_FCTS,
                          LBL_PCT_TTES_FCTS_DEB,
                          LBL_PCT_TTES_FCTS_NON_DEB,
                          LBL_NB_ETUD_NO_TEST,
                          LBL_NB_DEB_NO_TEST,
                          LBL_NB_NON_DEB_NO_TEST,
                          LBL_PCT_DEB_NO_TEST,
                          LBL_PCT_NON_DEB_NO_TEST,
                          NB_ETUD_TESTS_QQ_FONCTIONS
    ]


# -

def genere_donnees_nombre_tests_ecrits_tp_guides(df:pd.DataFrame, functions_names:dict, df_is_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un DataFrame avec colonnes : 'Tps', 'Nb etud', 'Nb etud analyse impossible', 'Nb etud avec tests présents', 'Nb etud avec tests présents pour toute fonction écrite', \
                                    'Nb etud avec aucun test', 'Nb etud avec tests présents pour qq fonctions écrites'

    Args :
        - df : df initial
        - function_names : dico which associates to each Tp identifier a list of functions name (ex : functions_names['Tp2] is ['foo1', 'foo2', 'foo3'])
        - df_is_deb : columns 'actor' et 'debutant'
    """
    df_plot = pd.DataFrame(columns=COLUMNS_STAT_ECR_TESTS)            
                            
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
        etud_analyse_possible = list(set(all_students_tp) - set(etud_analyse_impossible))
        etud_deb_analyse_impossible:list = select_debutants(etud_analyse_impossible, df_is_deb)
        etud_non_deb_analyse_impossible:list = list(set(etud_analyse_impossible) - set(etud_deb_analyse_impossible))
        etud_deb_analyse_possible:list = list(set(deb_students_tp) - set(etud_deb_analyse_impossible))
        etud_non_deb_analyse_possible:list = list(set(non_deb_students_tp) - set(etud_non_deb_analyse_impossible))
        etud_avec_tests:list = etud_testant_toute_fonction_ecrite_tp + etud_qq_tests_fonction_ecrite_tp
        etud_deb_avec_tests:list = select_debutants(etud_avec_tests, df_is_deb)
        etud_non_deb_avec_tests:list = list(set(etud_avec_tests) - set(etud_deb_avec_tests))
        df_plot_tp = pd.DataFrame({
            'Tps': [tp],\
            LBL_NB_ETUD: len(all_students_tp),\
            LBL_NB_DEB: len(deb_students_tp),\
            LBL_NB_NON_DEB: len(non_deb_students_tp),\
            LBL_NB_ETUD_ANALYSABLE: len(etud_analyse_possible),\
            LBL_NB_DEB_ANALYSABLE: len(etud_deb_analyse_possible),\
            LBL_NB_NON_DEB_ANALYSABLE: len(etud_non_deb_analyse_possible),\
            LBL_NB_ETUD_NON_ANALYSABLE: len(etud_analyse_impossible),\
            LBL_PCT_NON_ANALYSABLE: len(etud_analyse_impossible)/len(all_students_tp)*100,\
            LBL_PCT_DEB_NON_ANALYSABLE: len(etud_deb_analyse_impossible)/len(etud_analyse_impossible)*100,\
            LBL_NB_ETUD_TESTS_PRESENTS: len(etud_avec_tests),\
            LBL_NB_DEB_TESTS_PRESENTS: len(etud_deb_avec_tests), \
            LBL_NB_NON_DEB_TESTS_PRESENTS: len(etud_avec_tests) - len(etud_deb_avec_tests),\
            LBL_PCT_TESTS_PRESENTS: len(etud_avec_tests)/len(etud_analyse_possible)*100,\
            LBL_PCT_DEB_TESTS_PRESENTS: len(etud_deb_avec_tests)/len(etud_deb_analyse_possible)*100,\
            LBL_PCT_NON_DEB_TESTS_PRESENTS: len(etud_non_deb_avec_tests)/len(etud_non_deb_analyse_possible)*100,\
            LBL_NB_ETUD_TESTS_PRESENTS_TTES_FCTS: len(etud_testant_toute_fonction_ecrite_tp),\
            LBL_NB_DEB_TESTS_PRESENTS_TTES_FCTS: len(etud_deb_testant_toute_fonction_ecrite_tp),\
            LBL_NB_NON_DEB_TESTS_PRESENTS_TTES_FCTS: len(etud_non_deb_testant_toute_fonction_ecrite_tp),\
            LBL_PCT_TTES_FCTS: len(etud_testant_toute_fonction_ecrite_tp)/len(etud_analyse_possible)*100,\
            LBL_PCT_TTES_FCTS_DEB: len(etud_deb_testant_toute_fonction_ecrite_tp)/len(etud_deb_analyse_possible)*100,\
            LBL_PCT_TTES_FCTS_NON_DEB: len(etud_non_deb_testant_toute_fonction_ecrite_tp)/len(etud_non_deb_analyse_possible)*100,\
            LBL_NB_ETUD_NO_TEST: len(etud_testant_aucune_fonction_ecrite_tp),\
            LBL_NB_DEB_NO_TEST: len(etud_deb_testant_aucune_fonction_ecrite_tp),\
            LBL_NB_NON_DEB_NO_TEST: len(etud_non_deb_testant_aucune_fonction_ecrite_tp),\
            LBL_PCT_DEB_NO_TEST: len(etud_deb_testant_aucune_fonction_ecrite_tp)/len(etud_deb_analyse_possible)*100,\
            LBL_PCT_NON_DEB_NO_TEST: len(etud_non_deb_testant_aucune_fonction_ecrite_tp)/len(etud_non_deb_analyse_possible)*100,\
            NB_ETUD_TESTS_QQ_FONCTIONS : len(etud_qq_tests_fonction_ecrite_tp)
                                  })
        df_plot = pd.concat([df_plot, df_plot_tp], ignore_index=True)
    return df_plot


df_plot_nombre_tests_ecrits_tp_guides = genere_donnees_nombre_tests_ecrits_tp_guides(df, PROG_FUNCTIONS_NAME_BY_TP, df_is_deb)
df_plot_nombre_tests_ecrits_tp_guides 


def calcule_infos_travaux_non_analysables(df_nb_tests_ecrits_tp_guides:pd.DataFrame) -> pd.DataFrame:
    """
    Args :
        df_plot_nombre_tests_ecrits_tp_guides : colonnes définies en global
    """
    df_local = df_nb_tests_ecrits_tp_guides.copy()
    return df_local[['Tps', LBL_PCT_NON_ANALYSABLE, LBL_PCT_DEB_NON_ANALYSABLE]]


df_infos_travaux_non_analysables = calcule_infos_travaux_non_analysables(df_plot_nombre_tests_ecrits_tp_guides)
df_infos_travaux_non_analysables

df_infos_travaux_non_analysables[LBL_PCT_NON_ANALYSABLE].describe()

df_infos_travaux_non_analysables[LBL_PCT_DEB_NON_ANALYSABLE].describe()


def calcule_infos_tests_ecrits_sans_deb(df_nb_tests_ecrits_tp_guides:pd.DataFrame) -> pd.DataFrame:
    """
    Args :
        df_plot_nombre_tests_ecrits_tp_guides : colonnes définies en global
    """

    df_nb_tests_ecrits_tp_guides_sans_deb = df_nb_tests_ecrits_tp_guides.copy()
    return df_nb_tests_ecrits_tp_guides_sans_deb[['Tps', LBL_NB_ETUD, LBL_NB_ETUD_ANALYSABLE, LBL_NB_ETUD_TESTS_PRESENTS,\
                                                      LBL_PCT_TESTS_PRESENTS, \
                                                      LBL_NB_ETUD_TESTS_PRESENTS_TTES_FCTS, LBL_PCT_TTES_FCTS,\
                                                      LBL_NB_ETUD_NO_TEST, NB_ETUD_TESTS_QQ_FONCTIONS]]


df_infos_tests_ecrits_sans_deb =  calcule_infos_tests_ecrits_sans_deb(df_plot_nombre_tests_ecrits_tp_guides)
df_infos_tests_ecrits_sans_deb

df_infos_tests_ecrits_sans_deb[LBL_PCT_TESTS_PRESENTS].describe()

df_infos_tests_ecrits_sans_deb[LBL_PCT_TTES_FCTS].describe()


def plot_tests_ecrits_TP_guides(df_tests_ecrits_tp_guides:pd.DataFrame) -> None:
    """
    Args :
        df avec colonnes 'Tps', 'Nb etud travaux analysables', 'Nb etud avec tests présents', 'Nb etud sans test' 
    """
    fig, ax = plt.subplots()
    bottom = np.zeros(len(TPS_SANS_SEM_5))
    serie_nb_avec_tests = df_tests_ecrits_tp_guides[LBL_NB_ETUD_TESTS_PRESENTS]
    serie_nb_sans_test = df_tests_ecrits_tp_guides[LBL_NB_ETUD_NO_TEST]
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
    serie_nb_avec_tests = df_tests_ecrits_tp_guides[LBL_NB_ETUD_TESTS_PRESENTS]
    serie_nb_avec_tests_pour_toute_fonction = df_tests_ecrits_tp_guides[LBL_NB_ETUD_TESTS_PRESENTS_TTES_FCTS]
    serie_nb_avec_tests_pour_certaines_fonctions = df_tests_ecrits_tp_guides[NB_ETUD_TESTS_QQ_FONCTIONS]
    dico = {'Pour chaque fonction' : serie_nb_avec_tests_pour_toute_fonction, 'Pour certaines fonctions' : serie_nb_avec_tests_pour_certaines_fonctions}
    
    for labels, values in dico.items():
        p = ax.bar(TPS_SANS_SEM_5, values, 0.5, label=labels, bottom=bottom)
        bottom += values

        ax.bar_label(p, label_type='center')

    ax.set_title('TPs guidés : étudiants ayant écrit au moins un test')
    ax.legend()

    plt.show()


plot_tests_ecrits_par_fonctions_TP_guides(calcule_infos_tests_ecrits_sans_deb(df_plot_nombre_tests_ecrits_tp_guides))


# Un très grand nombre des travaux analysables (c'est à dire un fichier Python syntaxiquement correct contenant des fonctions) contient au moins un test (cf premier graphique). La moyenne sur les TPs indique que 94.7% des étudiant•es dont le travail est analysable ont écrit au moins un test, avec un écart-type de 1.86, un minimum de 92.25% pour le TP8 et un maximum de 96.7% pour le TP2.  Nous ne savons pas expliquer pourquoi le minimum se produit au niveau du TP8.
#
#
# La brique de base pour le test unitaire étant la fonction, l'écriture d'au moins un test par fonction testable peut représenter un comportement nominal pour des débutant·es (le comportement nominal réel consistant à écrire un jeu de tests pertinents). Pour les TPs guidés nous connaissons les fonctions à programmer : nous pouvons donc regarder quelle proportion des fonctions écrites et testables contiennent des tests. Les résultats montrent que la plupart des étudiant·es écrivent des tests pour toutes les fonctions testables qu'ils ou elles ont programmé. La moyenne sur les TPs indique que 86.7% des étudiant·es dont le code est analysable écrivent des tests pour toutes les fonctions, avec un écart-type à 6.5, un maximum à 96.3% pour le TP2, et un tassement pour le TP9 (pour ce TP environ 77% des étudiant·es ayant écrit des tests l'ont fait pour toutes les fonctions). On note que ce TP est l'un des plus difficiles du semestre, avec des boucles difficiles à écrire. 
#
# Nous n'avons pas regardé combien de fonctions ont été écrites par les étudiant·es : du point de vue de l'écriture des tests une étudiante qui n'aura écrit que 4 fonctions avec tests durant les séances est considérée de la même manière qu'une étudiante ayant écrit 10 fonctions avec tests, mais de manière différente d'une étudiante ayant écrit 12 fonctions sans aucun test. Dans le cas où toutes les fonctions ne possèdent pas de tests dans le code, nous n'avons pas regardé si c'est la dernière fonction écrite qui n'a pas de tests (ce qui peut correspondre au comportement "écrire le code, faire un test manuel puis ajouter des tests", avec fin du TP avant l'ajout des tests).

# ### Impact du cursus antérieur sur l'écriture des tests

def calcule_infos_tests_ecrits_deb_non_deb(df_nb_tests_ecrits_tp_guides_avec_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Args :
        df_plot_nombre_tests_ecrits_tp_guides : colonnes Tps', 'Nb debutants analyse possible',
                                                    'Nb debutants avec tests présents pour toute fonction écrite',
                                                    'Nb debutants sans test'
    """
    df_local_select =  df_nb_tests_ecrits_tp_guides_avec_deb[['Tps', LBL_NB_DEB_ANALYSABLE, LBL_NB_NON_DEB_ANALYSABLE,\
                                                    LBL_NB_DEB_TESTS_PRESENTS_TTES_FCTS, LBL_NB_NON_DEB_TESTS_PRESENTS_TTES_FCTS,\
                                                    LBL_PCT_TTES_FCTS_DEB, LBL_PCT_TTES_FCTS_NON_DEB, \
                                                    LBL_NB_DEB_NO_TEST, LBL_NB_NON_DEB_NO_TEST, \
                                                    LBL_PCT_DEB_NO_TEST, LBL_PCT_NON_DEB_NO_TEST]].copy()
    return df_local_select


df_infos_tests_ecrits_deb_non_deb = calcule_infos_tests_ecrits_deb_non_deb(df_plot_nombre_tests_ecrits_tp_guides)
df_infos_tests_ecrits_deb_non_deb 

df_infos_tests_ecrits_deb_non_deb[LBL_PCT_TTES_FCTS_DEB].describe()

df_infos_tests_ecrits_deb_non_deb[LBL_PCT_TTES_FCTS_NON_DEB].describe()

df_infos_tests_ecrits_deb_non_deb[LBL_PCT_DEB_NO_TEST].describe()

df_infos_tests_ecrits_deb_non_deb[LBL_PCT_NON_DEB_NO_TEST].describe()


def plot_tests_ecrits_deb(df_tests_ecrits_deb:pd.DataFrame) -> None:
    """
    Args :
        df avec colonnes 'Tps', 'Nb debutants analyse possible',
                                                    'Nb debutants avec tests présents pour toute fonction écrite',
                                                    'Nb debutants sans test'
    """
    df_local = df_tests_ecrits_deb[['Tps', LBL_NB_DEB_ANALYSABLE, \
                                    LBL_NB_DEB_TESTS_PRESENTS_TTES_FCTS, LBL_NB_DEB_NO_TEST]].copy()
    df_local = df_local.rename(columns={LBL_NB_DEB_ANALYSABLE: 'dont les travaux sont analysables',\
                                        LBL_NB_DEB_TESTS_PRESENTS_TTES_FCTS: 'ayant écrit au moins un test\n pour toute fonction écrite',\
                                        LBL_NB_DEB_NO_TEST: 'sans test'})
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
    df_tests_ecrits_non_deb[LBL_NB_NON_DEB_ANALYSABLE]
    df_local = df_tests_ecrits_non_deb[['Tps', LBL_NB_NON_DEB_ANALYSABLE, \
                                        LBL_NB_NON_DEB_TESTS_PRESENTS_TTES_FCTS, LBL_NB_NON_DEB_NO_TEST]].copy()
    df_local = df_local.rename(columns={LBL_NB_NON_DEB_ANALYSABLE: 'dont les travaux sont analysables',\
                                        LBL_NB_NON_DEB_TESTS_PRESENTS_TTES_FCTS: 'ayant écrit au moins un test\n pour toute fonction écrite',\
                                        LBL_NB_NON_DEB_NO_TEST: 'sans test'})
    df_local.set_index('Tps').plot(kind='bar', figsize=(12, 6))

    plt.title("Étudiant·es non débutant·es : écriture de tests")
    plt.ylabel("Nombre d'étudiant·es non débutant·es")
    plt.xlabel("TP")
    plt.xticks(rotation=45)
    plt.legend(title="Nombre de non débutant·es")
    plt.tight_layout()
    plt.show()


df_infos_tests_ecrits_deb_non_deb = calcule_infos_tests_ecrits_deb_non_deb(df_plot_nombre_tests_ecrits_tp_guides)
plot_tests_ecrits_deb(df_infos_tests_ecrits_deb_non_deb)
plot_tests_ecrits_non_deb(df_infos_tests_ecrits_deb_non_deb)


# Pour comparer le comportement moyen des débutant·es et non débutant·es pour l'écriture des tests on se base sur le pourcentage d'étudiant·es de ces 2 catégories ayant écrit au moins un test pour chaque fonction et n'ayant écrit aucun test. 
#
# Les données indiquent que 87.8% des débutants en moyenne ont écrit au moins un test pour toutes les fonctions qu'ils ont écrites (écart-type : 7), avec un minimum à 77.9% pour le TP9. Par ailleurs 84% des non débutants en moyenne ont écrit au moins un test pour toutes les fonctions qu'ils ont écrites (écart-type : 7.7), avec un minimum à 75.38% aussi pour le TP9. Il ne ressort donc pas de différence marquante entre les débutants et les non débutants. De plus les 2 catégories ont plus de fonctions non testées pour le TP estimé le plus difficile.  
#
# Dans le cas des étudiant·es qui n'écrivent aucun test, 3% des débutants en moyenne n'écrivent pas de test (écart-type : 1) et 2.4% des non débutants en moyenne n'écrivent pas de tests (écart-type : 0.7). On ne peut donc pas dire que le cursus des étudiant·es - vrais débutant·es ou étudiant·es ayant déjà pratiqué de la programmation Python, que ce soit en NSI ou dans le portail - influence l'écriture de tests. 

# ### Exécution des tests

# **/!\ ce paragraphe est une horreur à écrire et ça doit être encore pire à lire** **Et en plus aucune idée de l'effet de l'heuristique, sinon que sur le coup ça me simplifiait les calculs.**

# Écrire des tests sans les exécuter montre une incompréhension du processus de test. Nous cherchons donc à vérifier que chaque étudiant·e a exécuté au moins une fois chaque test qu'il ou elle a écrit. Nous regardons si, pour chaque étudiant·e et pour chaque fonction pour laquelle au moins un test a été écrit, on trouve une trace de l'exécution des tests de cette fonction. Nous reprenons les fonctions et les tests écrits dans les contenus de l'éditeur sélectionnés dans la section précédente. Nous procédons en cherchant dans les traces de l'étudiant·e les actions de clic sur le bouton dit `Run.Test` qui exécute les tests du fichier contenu dans l'éditeur. Nous sélectionnons comme précédemment le clic le plus récent, et nous itérons en remontant le temps jusqu'à trouver un clic qui a réellement déclenché l'exécution de tests[^1]. Nous analysons les verdicts de cette trace pour voir comment les tests exécutés sont reliés aux tests écrits dans le contenu d'éditeur analysé. 
#
# Pour chaque étudiant·e nous analysons une seule trace liée à un clic sur le bouton `Run.Test`. Cette simplification peut nous conduire à ignorer des exécutions de tests quand les étudiant·es utilisent une fonctionnalité de L1Test qui permet d'exécuter les tests d'une seule fonction. Dans ce cas, si l'exécution des tests la plus récente n'a exécuté les tests que d'une fonction et pas de toutes les fonctions du fichier, on considérera que cet étudiant·es n'a pas exécuté tous les tests qu'il ou elle a écrit. 
#
# [¹]: Nous ne traitons pas les clics ayant abouti au constat que le fichier ne contient aucun test.
#
# Techniquement nous utilisons une autre heuristique. Nous vérifions seulement que, dans la trace sélectionnée liée au clic sur le bouton `Run.Test`,  on trouve une trace de l'exécution d'au moins $n$ tests pour pour toute fonction possédant $n$ tests dans le contenu d'éditeur analysé. Nous ne vérifions pas l'égalité des appels de fonction ou expressions exécutées dans les tests. 

def convert_column_tests_to_df(df):
    """
    Returns a df that contains a line for each verdict found in the columns 'tests' of df. Columns :
    ['original_index', 'filename', 'lineno', 'tested_line',
       'expected_result', 'details', 'verdict', 'name', 'status']

    Ce dataframe est construit à partir des contenus de colonne "tests" de Run.Test non vides slt.

    Args:
        df : le dataframe complet d'origine, ds lequel la colonne "tests" indique le résultat d'un Run.Test, c'est à dire une liste
            de dictionnaires
    """
    df_tests = df['tests']
    df_all_tests = None
    list_of_df_verdicts = []
    
    for index, test_value in df_tests.items():    
        if (test_value != '') and (test_value != '[]'):
            lst:list[dict] = ast.literal_eval(test_value) # extract the list inside the string
            df_one_verdict = pd.DataFrame(lst) # each dict in lst is represented by a line in df_one_verdict
            df_one_verdict.insert(0, 'original_index', index)
            list_of_df_verdicts.append(df_one_verdict)        

    df_all_verdicts = pd.concat(list_of_df_verdicts, ignore_index=True)
    return df_all_verdicts


# nécessaire car L1Test renvoie les noms de fonction agrémenté des noms de param qu'il faut enlever
def nom_fonction(name:str) -> str:
    '''
    Renvoie le nom de la fonction sans les arguments

    >>> nom_fonction('compare(nb1, nb2)')
    'compare'
    '''
    return name.split('(')[0]


df_all_verdicts_interm = convert_column_tests_to_df(df) 
df_all_verdicts_interm['name'] = df_all_verdicts_interm['name'].apply(nom_fonction)
df_all_verdicts = df_all_verdicts_interm.copy()


def index_last_RunTest(actor:str, df:pd.DataFrame, filename_infere:str, df_all_verdicts:pd.DataFrame) -> int:
    '''
    Returns the index of the most recent Run.Test of actor, limited to df and filename_infere, which appears
    through its index in df_all_verdicts. Implies that this Run.Test was run on not empty tests.

    Returns None if no such index is found.

    Args:
        - actor : some student
        - df: the original df
        - filename_infred : some particular file name to be analyzed
        - df_all_verdicts : was computed elsewhere, not computed from df 
    '''
    df_RunTest = df[(df['verb']=='Run.Test') & ((df['actor']==actor) | (df['binome']==actor)) & (df['filename_infere']==filename_infere)]
    timestamps = df_RunTest['timestamp.$date'].copy() # pour être sûre de ne pas modifier le df initial
    found = False # found Run.Test which can be exploited
    while not timestamps.empty and not found: 
        index_of_timestamp_max_RunTest = timestamps.idxmax()
        if index_of_timestamp_max_RunTest in df_all_verdicts['original_index']:
            found = True # timestamp_max_RunTest
        else:
            # passer à un timestamp antérieur
            timestamps = timestamps.drop(index=[index_of_timestamp_max_RunTest])
    if found:
        return index_of_timestamp_max_RunTest
    else:
        return None


def tests_executes_pour_tests_ecrits(actor:str, df: pd.DataFrame, df_tests_ecrits_filename:pd.DataFrame, df_all_verdicts:pd.DataFrame, filename:str) -> tuple[bool, int, pd.DataFrame, pd.DataFrame]:
    '''
    Cherche le Run.Test le plus récent dans df pour actor, apparaissant dans df_all_verdicts, et analyse les colonnes
    "function_name" et 'tests_number' par rapport
    au contenu de df_tests_ecrits_filename, qui contient les fonctions et leur nb de tests du codeState analysé.
        
    Renvoie : res_bool, index_runTest_in_df,  df_runTest_tests_number, df_tests_ecrits_filename_strict_pos
        - res_bool : True ssi les fonctions qui ont n tests écrits dans df_all_verdicts ont au moins n tests exécutés dans le Run.Test.
        - index_runTest_in_df : index of the mot recent Run.Test found and used inside the computation
        - df_runTest_tests_number : df avec colonnes "function_name" et 'tests_number', calculé en regardant les tests de df_all_verdicts à l'index du Run.Test
        - df_tests_ecrits_filename_strict_pos : df avec colonnes "function_name" et 'tests_number', calculé en regardant les tests de df_tests_ecrits_filename pour filename
        
    Args:
        actor : some actor
        df : original df
        df_tests_ecrits_filename : les tests écrits pour le codeState le plus récent dans df pour le même filename, déjà calculé ailleurs
        df_all_verdicts : df des verdicts de df, déjà calculé ailleurs
    '''
    # cherche le RunTest le plus récent dont l'index apparaît dans df_all_verdicts, ici recherche par filename_infere
    index_runTest_in_df = index_last_RunTest(actor, df, filename, df_all_verdicts)
    # si on ne trouve pas ce Run.Test, on renvoie False
    if index_runTest_in_df == None:
        return (False, None, None, None)
    # on calcule les verdicts de df_all_verdicts qui concernent ce Run.Test    
    df_all_verdicts_actor = df_all_verdicts[df_all_verdicts['original_index']==index_runTest_in_df]
    # calcul de df_runTest_tests_number : comptage du nb de tests par fonctions ds runTest 
    df_runTest_tests_number= pd.DataFrame(columns=['function_name', 'tests_number'])
    # la colonne 'name' contient le nom de la fonction testée
    for name in df_all_verdicts_actor['name'].unique():
        # on peut sûrement faire plus élégant niveau pandas, j'ai eu du mal à extraire la valeur du comptage
        # compte le nb d'apparition de chaque fonction ds le df des tests en ligne, à l'index du Run.Test
        # 1 apparition => 1 test exécuté pour cette fonction
        function_df = pd.DataFrame({'function_name' : [name], 'tests_number' : df_all_verdicts_actor.groupby(['name'])['name'].count()[name]})
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
            # on peut sûrement faire plus élégant niveau pandas, le values[0] vise à extraire la valeur de type int de la Serie qui la contient
            tests_number_runTest = df_runTest_tests_number.loc[df_runTest_tests_number['function_name']==func_name]['tests_number'].values[0]
            if tests_number_ecrits < tests_number_runTest:
                return (False, index_runTest_in_df, df_runTest_tests_number, df_tests_ecrits_filename_strict_pos)
    return (True, index_runTest_in_df,  df_runTest_tests_number, df_tests_ecrits_filename_strict_pos)


LBL_NB_ETUD_TOUS_TESTS_EXEC = "Nb étudiant·es avec tous tests exécutés"
LBL_NB_DEB_TOUS_TESTS_EXEC = "Nb débutant·es avec tous tests exécutés"
LBL_NB_NON_DEB_TOUS_TESTS_EXEC = "Nb non débutant·es avec tous tests exécutés"
LBL_PCT_ETUD_TESTS_EXEC = 'pourcentage étud avec tous tests exécutés'
LBL_PCT_DEB_TESTS_EXEC = 'pourcentage déb avec tous tests exécutés'
LBL_PCT_NON_DEB_TESTS_EXEC = 'pourcentage non déb avec tous tests exécutés'


def genere_donnees_tests_ecrits_executes_tp(df:pd.DataFrame, df_tests:pd.DataFrame, df_all_verdicts:pd.DataFrame, \
                                         df_nb_tests_ecrits_tp_guides:pd.DataFrame, tp_filenames:dict, \
                                         df_is_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Génère un df avec les données pour plot, colonnes 'Tps', number_of_students_with_tests', 
    'number_of_students_with_all_tests_executed', 'pourcentage'

    Args :
        df : le df total et global
        df_tests : df avec colonnes ['actor', 'tp', 'function_name', 'tests_number', 'index']
        df_all_verdicts : le df qui contient tous les tests ligne par ligne extraits de df
        df_nb_tests_ecrits_tp_guides : contient la colonne 'Tps' et 'Nb etud avec tests présents' et bien d'autres, c'est le gros df
                                       fourre-tout sur les tests écrits
        tp_filenames : le dict {nom_TP : filename}
        df_is_deb : columns 'actor' et 'debutant'
    """
    df_plot = pd.DataFrame(columns=['Tps', \
                                    LBL_NB_ETUD_TESTS_PRESENTS, LBL_NB_DEB_TESTS_PRESENTS, LBL_NB_NON_DEB_TESTS_PRESENTS,\
                                    LBL_NB_ETUD_TOUS_TESTS_EXEC, LBL_PCT_ETUD_TESTS_EXEC, 
                                    LBL_NB_DEB_TOUS_TESTS_EXEC, LBL_PCT_DEB_TESTS_EXEC,
                                    LBL_NB_NON_DEB_TOUS_TESTS_EXEC, LBL_PCT_NON_DEB_TESTS_EXEC])
    for tp in TPS_SANS_SEM_5:
        df_tp_tests = df_tests[df_tests['tp']==tp]
        actor_column_tp_tests_ecrits  = df_tp_tests['actor'].unique()
        # df intermédiaire qu'on calcule : 'actor' et 'tests_ecrits_executes' : bool qui contient le résultat
        df_tests_ecrits_executes_tp = pd.DataFrame(columns=['actor', 'tests_ecrits_executes'])
        for student in actor_column_tp_tests_ecrits:
            res_bool, index_runTest_in_df,  df_runTest_tests_number, df_tests_ecrits_filename_strict_pos = \
                tests_executes_pour_tests_ecrits(student, df, df_tp_tests, df_all_verdicts, filename=tp_filenames[tp] )
            petit_df = pd.DataFrame({'actor':[student], 'tests_ecrits_executes':res_bool})
            df_tests_ecrits_executes_tp = pd.concat([df_tests_ecrits_executes_tp, petit_df], ignore_index=True )
        df_tests_ecrits_executes_tp_is_deb = merge_debutant(df_tests_ecrits_executes_tp, df_is_deb)
        # résultats pour toute la promo
        # pas élégant : sert à récupérer un entier
        nb_etuds_avec_tests = df_nb_tests_ecrits_tp_guides[df_nb_tests_ecrits_tp_guides['Tps']==tp][LBL_NB_ETUD_TESTS_PRESENTS].iloc[0]
        nb_etuds_avec_tests_executes = len(df_tests_ecrits_executes_tp[df_tests_ecrits_executes_tp['tests_ecrits_executes']==True])
        pourcentage_exec_tests_ecrits_tp = nb_etuds_avec_tests_executes/nb_etuds_avec_tests*100
        # résultats pour les débutants
        df_tests_ecrits_executes_tp_deb = df_tests_ecrits_executes_tp_is_deb[df_tests_ecrits_executes_tp_is_deb['debutant']==True]
        nb_deb_avec_tests = df_nb_tests_ecrits_tp_guides[df_nb_tests_ecrits_tp_guides['Tps']==tp][LBL_NB_DEB_TESTS_PRESENTS].iloc[0]
        nb_deb_avec_tests_executes = len(df_tests_ecrits_executes_tp_deb[df_tests_ecrits_executes_tp_deb['tests_ecrits_executes']==True])
        pourcentage_deb_exec_tests_ecrits_tp = nb_deb_avec_tests_executes/nb_deb_avec_tests*100
        # résultats pour les non débutants
        df_tests_ecrits_executes_tp_non_deb = df_tests_ecrits_executes_tp_is_deb[df_tests_ecrits_executes_tp_is_deb['debutant']==False]
        nb_non_deb_avec_tests = df_nb_tests_ecrits_tp_guides[df_nb_tests_ecrits_tp_guides['Tps']==tp][LBL_NB_NON_DEB_TESTS_PRESENTS].iloc[0]
        nb_non_deb_avec_tests_executes = len(df_tests_ecrits_executes_tp_non_deb[df_tests_ecrits_executes_tp_non_deb['tests_ecrits_executes']==True])
        pourcentage_non_deb_exec_tests_ecrits_tp = nb_non_deb_avec_tests_executes/nb_non_deb_avec_tests*100        
        df_plot_tp = pd.DataFrame({'Tps' : [tp], \
                                       LBL_NB_ETUD_TESTS_PRESENTS: nb_etuds_avec_tests, \
                                       LBL_NB_DEB_TESTS_PRESENTS: nb_deb_avec_tests, \
                                       LBL_NB_NON_DEB_TESTS_PRESENTS: nb_non_deb_avec_tests,\
                                       LBL_NB_ETUD_TOUS_TESTS_EXEC: nb_etuds_avec_tests_executes, \
                                       LBL_NB_DEB_TOUS_TESTS_EXEC: nb_deb_avec_tests_executes, \
                                       LBL_NB_NON_DEB_TOUS_TESTS_EXEC: nb_non_deb_avec_tests_executes, \
                                       LBL_PCT_ETUD_TESTS_EXEC: pourcentage_exec_tests_ecrits_tp,\
                                       LBL_PCT_DEB_TESTS_EXEC: pourcentage_deb_exec_tests_ecrits_tp,\
                                       LBL_PCT_NON_DEB_TESTS_EXEC: pourcentage_non_deb_exec_tests_ecrits_tp})
        df_plot = pd.concat([df_plot, df_plot_tp], ignore_index=True)
    return df_plot


df_tests_ecrits_executes = genere_donnees_tests_ecrits_executes_tp(df, df_tests_number_tp_prog, df_all_verdicts, \
                                                                df_plot_nombre_tests_ecrits_tp_guides, PROG_FILENAMES_BY_TP, df_is_deb)

df_tests_ecrits_executes

LABEL_NB_ETUD_WITH_TESTS = "avec tests présents"
LABEL_TESTS_EXECUTES = "dont tous les tests ont été exécutés"


def plot_tests_ecrits_executes(df_tests_ecrits_executes:pd.DataFrame) -> None:
    """
    AFfiche le graphe avec le nb d'étudiants ayant exécuté tous les tests présents dans le code.

    Args :
        df : le df total et global
        df_tests : df avec colonnes ['actor', 'tp', 'function_name', 'tests_number', 'index']
        df_all_verdicts : le df qui contient tous les tests ligne par ligne extraits de df
        df_plot_nombre_tests_ecrits_tp_guides : contient la colonne 'Nb etud avec tests présents'
        tp_filenames : le dict {nom_TP : filename}
    """
    df_plot = df_tests_ecrits_executes.copy()
    df_plot = df_plot.rename(columns={LBL_NB_ETUD_TESTS_PRESENTS: LABEL_NB_ETUD_WITH_TESTS, \
                                        LBL_NB_ETUD_TOUS_TESTS_EXEC: LABEL_TESTS_EXECUTES})
    df_plot.set_index('Tps')[[LABEL_NB_ETUD_WITH_TESTS, LABEL_TESTS_EXECUTES]].plot(kind='bar', figsize=(12, 6))
    plt.title("Étudiant·es ayant travaillé sur les TPs guidés")
    plt.ylabel("Nombre d'étudiant·es")
    plt.xlabel("TPs guidés")
    plt.xticks(rotation=45)
    plt.legend(title="Nombre étudiant·es")
    plt.tight_layout()
    plt.show()


plot_tests_ecrits_executes(df_tests_ecrits_executes)

df_tests_ecrits_executes[LBL_PCT_ETUD_TESTS_EXEC].describe()

df_tests_ecrits_executes[LBL_PCT_DEB_TESTS_EXEC].describe()

df_tests_ecrits_executes[LBL_PCT_NON_DEB_TESTS_EXEC].describe()

# Les données montrent que 86% en moyenne des étudiant·es ayant écrit au moins un test dans leur travail ont exécuté tous les tests écrits (écart-type : 3.6), 85.4% en moyenne des débutants ayant écrit au moins un test (écart-type : 6) et 88.4% en moyenne des non débutants (écart-type : 3.6). 

# # QR2 : les étudiants prennent-ils l'habitude de tester leurs programmes ?

GAMES_ANALYZED = ['tictactoe.py', 'puissance4.py', 'binairo.py', 'jeu_2048.py']#, 'jeu_nim.py']

# Je traîne du code inutilement compliqué... pas besoin de filtrer sur Tp_GAME ni TP_prog si je filtre d'abord sur le filename_infere.

assert(df[(df['filename_infere'].isin(GAMES_ANALYZED)) & ~((df['TP'] == 'Tp_GAME') & (df['Type_TP'] == 'TP_prog'))].empty)


# ## Écriture de tests

def find_tests_by_function_for_game_actor(actor:str, df:pd.DataFrame, filename:str) -> tuple[pd.DataFrame, bool, bool]:
    """
    Looks for codeStates related  to 'filename' for student `actor`, then looks repeatedly 
    for the most recent codeState that can be parsed tne returns:

    - a DataFrame with columns 'actor', 'filename', 'function_name', 'tests_number' (int or None if not present in codestates), 'index' (index in df of the analyzed codeState)
    - a first bool, True if for student 'name' the codeStates cannot be analyzed (Python or l1test syntax error) or codestates contain no function of functions_names
    - a second bool, True if for student 'name' and this tp no codeState was found, or only empty codeStates

    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        actor: some actor (ex : 'truc.machin.etu')
        df: some DataFrame
        filename: the name of a particular filename_infere to analyze. 
        
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
    df_name_tp = df[((df['actor'] == actor) | (df['binome'] == actor)) \
                        & (df['filename_infere'] == filename)]
    df_codestate_nonempty = df_name_tp[df_name_tp['codeState'] != '']
    no_func = []
    if len(df_codestate_nonempty) == 0:
            return None, False, True, []
    else:
        # look for most recent parsable codeState
        timestamps = df_codestate_nonempty['timestamp.$date'].copy() # pour être sûre de ne pas modifier le df initial
        found = False # found codeState with functions not all unfoundable
        while not timestamps.empty and not found: 
            index_of_timestamp_max = timestamps.idxmax() # index of timestamp most recent
            most_recent_codeState = df_name_tp.loc[index_of_timestamp_max]['codeState']
            dict_tests = find_tests_in_codestate(most_recent_codeState)
            if dict_tests != None and dict_tests != {}: # parseable and contains at least 1 function
                col_functions = []
                col_tests_number = []
                for key, value in dict_tests.items(): # key : function_name, value : tests_number
                    col_functions.append(key)
                    col_tests_number.append(value)
                nb_rows = len(dict_tests) # number of functions
                if col_tests_number != [None]*nb_rows: # convenient codestate found, with at least one function inside 
                                                       # comment pourrait-on avoir None partout ? si aucune fonction
                    found = True
                    col_actors = [actor] * nb_rows
                    col_index = [index_of_timestamp_max] * nb_rows
                    df_result = pd.DataFrame({'actor' : col_actors, 'filename_infere' : filename,'function_name' : col_functions, \
                                          'tests_number' : col_tests_number, 'index' : col_index })
                else: # no tests, codestate not convenient : drop this index and continue
                    print(index_of_timestamp_max)
                    assert(False) # pour vérifier
                    timestamps = timestamps.drop(index=[index_of_timestamp_max])
            elif dict_tests == {}: # no function
                no_func.append(index_of_timestamp_max)
                timestamps = timestamps.drop(index=[index_of_timestamp_max])
            else:# codestate not parsable : drop this index and continue
                timestamps = timestamps.drop(index=[index_of_timestamp_max])
        if found:
            return df_result, False, False, no_func
        else:
            #print(f"no functions found for {name} and index {index_of_timestamp_max}")
            return None, True, False, no_func


def find_tests_for_tpgame_game(df:pd.DataFrame, filename:str) -> pd.DataFrame:
    """
    Looks for codeStates related  to 'TP_prog' (df['Type_TP'] == 'TP_prog') for `name` and all filename_infere we can find for `name`, then looks repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

    - a DataFrame with columns 'actor', 'tp', 'filename_infere', 'function_name', 'tests_number' (int or None if not present in codestates), 'index' (index in df of the analyzed codeState)
 
    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        name: some actor (ex : 'truc.machin.etu')
        df: some DataFrame   
        games : la liste des noms de fichiers de jeu à considérer dans l'analyse
    Returns:
        None if no tp_game & tp_prog codestate could be found or analyzed.
    
    """
    df_game = df[df['filename_infere'] == filename].copy()
    all_students_game = actors(df_game)
    df_result = pd.DataFrame(columns=['actor', 'filename_infere', 'function_name', 'tests_number', 	'index'])
    no_func = []
    cannot_analyze_codestate = []
    empty_codestate = []
    for name in all_students_game:
        #print(f'----{name}')
        df_name, cannot_analyze_codestate_name, empty_codestate_name, no_func_name =  find_tests_by_function_for_game_actor(name, df, filename)
        if df_name is not None:
                df_result = pd.concat([df_result, df_name], ignore_index=True)
        else :
            if cannot_analyze_codestate_name != []:
                cannot_analyze_codestate.append(name)
            if no_func_name != []:
                no_func.append(no_func_name)
            if empty_codestate_name:
                empty_codestate.append(name)
    return df_result, cannot_analyze_codestate, empty_codestate, no_func


def find_tests_for_tpgame2(df:pd.DataFrame, games:list[str]) -> tuple[pd.DataFrame, list[str]]:
    """
    Looks for codeStates related  to 'Tp_GAME' (df['Type_TP'] == 'TP_prog') for all students and all filename_infere we can find for `name`, then looks repeatedly for the most recent codeState that can be parsed and contains at least one function of functions_names, then returns:

     - a DataFrame with columns 'actor', 'tp', 'filename_infere', 'function_name', 'tests_number' (int or None if not present in codestates), 'index' (index in df of the analyzed codeState)
     - a list of actors for which no data could be collected - they do not appear in the returned dataframe
     
    codeStates are considered from the most recent to the least recent, so it does not matter if timestamps are not sorted in increaded order.
    
    Args:
        df: some DataFrame
        games : la liste des noms de fichiers de jeu à considérer dans l'analyse
    """
    cannot_find_or_analyze_tpgame = {}
    df_result = pd.DataFrame(columns=['actor',  'filename_infere', 	'tests_number', 	'index'])
    df_local = df[(df['TP'] == 'Tp_GAME') & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'].isin(games))].copy()
    empty_codestate = {} 
    no_func = {}
    for filename in games:
        print(f'---- {filename}')
        df_game, cannot_find_or_analyze_game, empty_codestate_game, no_func_game = find_tests_for_tpgame_game(df, filename)
        df_result = pd.concat([df_result, df_game], ignore_index=True)
        cannot_find_or_analyze_tpgame[filename] = cannot_find_or_analyze_game
        empty_codestate[filename] = empty_codestate_game
        no_func[filename] = no_func_game
    return df_result, cannot_find_or_analyze_tpgame, empty_codestate, no_func


df_tests_tpgame_all, cannot_find_or_analyze_tpgame, empty_codestate_games, no_func_games = find_tests_for_tpgame2(df, GAMES_ANALYZED)

cannot_find_or_analyze_tpgame

# En regardant à la main : ce sont des étudiant·es dont le code ne contient que l'entête en commentaire.

empty_codestate_games

no_func_games

# En regardant à la main : ce sont les mêmes étudiant·es avec les mêmes codeStates contenant uniquement un entête en commentaires.

LBL_NB_ETUD_GAME = 'nb étudiants ayant réalisé le jeu'
LBL_NB_DEB_GAME = 'nb débutants ayant réalisé le jeu'
LBL_NB_NON_DEB_GAME = 'nb non débutants ayant réalisé le jeu'
LBL_NB_ETUD_AVEC_TESTS_GAME = 'Nb étud avec tests présents'
LBL_NB_DEB_AVEC_TESTS_GAME = LBL_NB_DEB_TESTS_PRESENTS
LBL_NB_NON_DEB_AVEC_TESTS_GAME = LBL_NB_NON_DEB_TESTS_PRESENTS
LBL_PCT_ETUD_GAME = '% étudiants ayant réalisé le jeu (total)'
LBL_PCT_DEB_GAME = '% étudiants débutants (jeu)'
LBL_PCT_NON_DEB_GAME = '% étudiants non débutants (jeu)'
LBL_PCT_ETUD_TESTS_GAME = '% étudiants avec tests (jeu)'
LBL_PCT_DEB_TESTS_GAME = '% étudiants débutants avec tests (nb débutants game)'
LBL_PCT_NON_DEB_TESTS_GAME = '% étudiants non débutants avec tests (nb non débutants game)'


def genere_donnees_test_games(df:pd.DataFrame, df_tests_games:pd.DataFrame, df_is_deb:pd.DataFrame, games_names:list[str]) -> pd.DataFrame:
    '''
    Génére un dataframe avec comme colonnes :

    - jeu : nom du jeu
    - 'nb étudiants ayant réalisé le jeu' : le nb d'étudiants qui ont une trace avec ce nom
    - % étudiants ayant réalisé le jeu (total) : le % rapporté au nb d'étudiants total, pas très parlant
    - '% étudiants débutants (jeu)' : le % de débutants rapporté au nb d'étudiants ayant réalisé le jeu
    - '% étudiants avec tests (jeu)' : le % d'étudiants ayant écrit des tests, rapporté au nb d'étudiants ayant réalisé le jeu
    - '% étudiants débutants avec tests (avec tests)' : le % d'étudiants débutants avec tests rapporté au nb de débutants
    
    Args:
        df : df total
        df_test_games : columns actor, tp, filename_infere, function_name, tests_number, index
        df_admin_etud_debutants : columns actor, debutant
    '''
    df_plot = pd.DataFrame(columns=['filename', LBL_NB_ETUD_GAME, LBL_NB_DEB_GAME, LBL_NB_NON_DEB_GAME,\
                                    LBL_NB_ETUD_AVEC_TESTS_GAME, LBL_NB_DEB_AVEC_TESTS_GAME, LBL_NB_NON_DEB_AVEC_TESTS_GAME,\
                                    LBL_PCT_ETUD_GAME, LBL_PCT_DEB_GAME, LBL_PCT_NON_DEB_GAME,\
                                    LBL_PCT_ETUD_TESTS_GAME, LBL_PCT_DEB_TESTS_GAME, LBL_PCT_NON_DEB_TESTS_GAME])
    all_students_df = actors(df)
    # nb actors - global df    
    nb_actor_df = len(all_students_df)
    df_tests_games_avec_debutants = merge_debutant(df_tests_games, df_is_deb) 

    for game in games_names:
        #print(game, '---------')
        # nb actors - game
        df_tests_game = df_tests_games_avec_debutants[df_tests_games_avec_debutants['filename_infere'] == game]
        game_etuds = df_tests_game.actor.unique()
        nb_etud_df_game = len(game_etuds)
        #print('nb_actor_df_game : ', nb_actor_df_game)
        pourcent_etud_game = nb_etud_df_game/nb_actor_df*100
        # debutants / game
        debutants_game = select_debutants(game_etuds, df_is_deb)
        non_debutants_game = list(set(game_etuds) - set(debutants_game))
        nb_debutants_game = len(debutants_game)
        nb_non_debutants_game = len(non_debutants_game)
        pourcent_etud_game_debutant = nb_debutants_game/nb_etud_df_game*100
        pourcent_etud_game_non_debutant = nb_non_debutants_game/nb_etud_df_game*100
        # tests / game
        df_tests_presents = df_tests_game[df_tests_game['tests_number']>0]
        etud_tests_presents = df_tests_presents.actor.unique()
        nb_etud_game_test = len(etud_tests_presents)
        pourcent_etud_game_avec_tests = nb_etud_game_test/nb_etud_df_game*100
        # tests & debutants / tests
        debutants_tests_presents = select_debutants(etud_tests_presents, df_is_deb)
        nb_etud_game_tests_debutant = len(debutants_tests_presents)
        pourcent_etud_game_tests_debutants = nb_etud_game_tests_debutant/nb_debutants_game*100
        # tests & non debutants / tests
        non_debutants_tests_presents = list(set(etud_tests_presents) - set(debutants_tests_presents))
        nb_etud_game_tests_non_debutant = len(non_debutants_tests_presents)
        pourcent_etud_game_tests_non_debutants = nb_etud_game_tests_non_debutant/nb_non_debutants_game*100
        # local df
        df_plot_game = pd.DataFrame({'filename' : [game], 
                                     LBL_NB_ETUD_GAME : nb_etud_df_game,
                                     LBL_NB_DEB_GAME : nb_debutants_game,
                                     LBL_NB_NON_DEB_GAME : nb_non_debutants_game,
                                     LBL_NB_ETUD_AVEC_TESTS_GAME: nb_etud_game_test,
                                     LBL_NB_DEB_AVEC_TESTS_GAME: nb_etud_game_tests_debutant,
                                     LBL_NB_NON_DEB_AVEC_TESTS_GAME: nb_etud_game_tests_non_debutant,
                                     LBL_PCT_ETUD_GAME: pourcent_etud_game,
                                     LBL_PCT_DEB_GAME: pourcent_etud_game_debutant,
                                     LBL_PCT_NON_DEB_GAME: pourcent_etud_game_non_debutant,
                                     LBL_PCT_ETUD_TESTS_GAME: pourcent_etud_game_avec_tests,
                                     LBL_PCT_DEB_TESTS_GAME: pourcent_etud_game_tests_debutants,
                                     LBL_PCT_NON_DEB_TESTS_GAME: pourcent_etud_game_tests_non_debutants})
        df_plot = pd.concat([df_plot, df_plot_game], ignore_index=True)
    return df_plot


df_plot_nombre_tests_ecrits_games =  genere_donnees_test_games(df, df_tests_tpgame_all, df_is_deb, GAMES_ANALYZED)
df_plot_nombre_tests_ecrits_games

# Il faut peut-être virer le 2048 car 8% d'étudiant·es (soit 23 étudiant·es) l'ont fait, c'est très peu. Pour le binairo et le puissance 4, ce n'est pas tellement mieux :( Je pense que des NSI ont fait les projets chez eux, ce qui explique qu'on ait si peu de non débutants pour le tictactoe.

# describe : croit que c'est une chaîne ou timestamp. Je ne retrouve plus comment corriger, pourtant je l'ai fait plus haut
df_plot_nombre_tests_ecrits_games[LBL_PCT_ETUD_TESTS_GAME].astype(int).describe()

df_plot_nombre_tests_ecrits_games[LBL_PCT_DEB_TESTS_GAME].describe()

df_plot_nombre_tests_ecrits_games[LBL_PCT_NON_DEB_TESTS_GAME].describe()


# Le nombre d'étudiant·es ayant réalisé les TPs non guidés est significativement inférieur au nombre d'étudiant·es ayant réalisé les TPs guidés : le jeu du TicTacToe n'a été réalisé que par 129 étudiant·es avec un code analysable, alors que pour le TP9 ils étaient 150. Le jeu du Puissance4 n'a été réalisé que par 80 étudiant·es avec un code analysable, puis on trouve le jeu du Binairo avec 47 étudiant·es et le jeu du 2048 avec 23 étudiant·es. La fonte des effectifs en fin de semestre quand arrivent les résultats des DS de mi-semestre est classique. De plus le rythme d'une notion par semaine avec rendu d'un travail en fin de semaine se casse brutalement pour passer à un travail sur 3 semaines, ce qui peut désorienter les étudiant·es les plus fragiles. 
#
# Le jeu du TicTacToe, annoncé comme le moins difficile, a été réalisé à 61% par des débutant·es. Le jeu du Puissance4 a été réalisé à 57% par des débutants. Au contraire le jeu du Binairo a été réalisé à 64% par des non débutants. Le jeu du 2048 a été réalisé à part égales par les débutants et les non débutants. 
#
# En moyenne sur les 4 jeux, 62.7% des étudiant·es ont écrit des tests (écart-type : 10.1), avec un minimum de 53.8% pour Puissance4 et de 57.4% pour le TicTacToe. Parmi les débutant·es ayant réalisé les jeux, on trouve qu'en moyenne et de manière homogène sur les 4 jeux 56% ont écrit des tests (écart-type : 1). Parmi les non-débutants ayant réalisé les jeux, on trouve qu'en moyenne sur les 4 jeux 66.3% ont écrit des tests (écart-type : 16.6), avec un minimum à 50% pour le jeu du Puissance4 et un maximum à 86.7% pour le jeu du Binairo.
#
# Il ressort de ces données qu'une grosse moitié des étudiant·es ayant réalisé les TPs non cadrés à continué à écrire des tests malgré la difficulté de la tâche. On peut sans doute dire que ces étudiant·es ont pris l'habitude de tester leur code. Pour l'autre moitié n'ayant pas écrit de tests, on peut supposer que l'habitude d'écrire des tests n'était pas prise, ou l'intérêt d'en écrire pas intégré. 
#

# ### Exécution des tests

def genere_donnees_tests_ecrits_executes_games(df:pd.DataFrame, df_tests:pd.DataFrame, df_all_verdicts:pd.DataFrame, \
                                         df_nb_tests_ecrits_tp_games:pd.DataFrame, \
                                         df_is_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Génère un df avec les données pour plot, colonnes 'game', number_of_students_with_tests', 
    'number_of_students_with_all_tests_executed', 'pourcentage'

    Args :
        df : le df total et global
        df_tests : df avec colonnes ['actor', 'game', 'function_name', 'tests_number', 'index']
        df_all_verdicts : le df qui contient tous les tests ligne par ligne extraits de df
        df_nb_tests_ecrits_tp_games : contient la colonne 'Tps' et 'Nb etud avec tests présents' et bien d'autres, c'est le gros df
                                       fourre-tout sur les tests écrits
        df_is_deb : columns 'actor' et 'debutant'
    """
    df_plot = pd.DataFrame(columns=['filename', \
                                    LBL_NB_ETUD_TESTS_PRESENTS, LBL_NB_DEB_TESTS_PRESENTS, LBL_NB_NON_DEB_TESTS_PRESENTS,\
                                    LBL_NB_ETUD_TOUS_TESTS_EXEC, LBL_PCT_ETUD_TESTS_EXEC, 
                                    LBL_NB_DEB_TOUS_TESTS_EXEC, LBL_PCT_DEB_TESTS_EXEC,
                                    LBL_NB_NON_DEB_TOUS_TESTS_EXEC, LBL_PCT_NON_DEB_TESTS_EXEC])
    for filename in GAMES_ANALYZED:
        df_tp_tests = df_tests[df_tests['filename_infere']==filename]
        actor_column_tp_tests_ecrits  = df_tp_tests['actor'].unique()
        # df intermédiaire qu'on calcule : 'actor' et 'tests_ecrits_executes' : bool qui contient le résultat
        df_tests_ecrits_executes_tp = pd.DataFrame(columns=['actor', 'tests_ecrits_executes'])
        for student in actor_column_tp_tests_ecrits:
            res_bool, index_runTest_in_df,  df_runTest_tests_number, df_tests_ecrits_filename_strict_pos = \
                tests_executes_pour_tests_ecrits(student, df, df_tp_tests, df_all_verdicts, filename=filename )
            petit_df = pd.DataFrame({'actor':[student], 'tests_ecrits_executes':res_bool})
            df_tests_ecrits_executes_tp = pd.concat([df_tests_ecrits_executes_tp, petit_df], ignore_index=True )
        df_tests_ecrits_executes_tp_is_deb = merge_debutant(df_tests_ecrits_executes_tp, df_is_deb)
        # résultats pour toute la promo
        # pas élégant : sert à récupérer un entier
        nb_etuds_avec_tests = df_nb_tests_ecrits_tp_games[df_nb_tests_ecrits_tp_games['filename']==filename][LBL_NB_ETUD_TESTS_PRESENTS].iloc[0]
        nb_etuds_avec_tests_executes = len(df_tests_ecrits_executes_tp[df_tests_ecrits_executes_tp['tests_ecrits_executes']==True])
        pourcentage_exec_tests_ecrits_tp = nb_etuds_avec_tests_executes/nb_etuds_avec_tests*100
        # résultats pour les débutants
        df_tests_ecrits_executes_tp_deb = df_tests_ecrits_executes_tp_is_deb[df_tests_ecrits_executes_tp_is_deb['debutant']==True]
        nb_deb_avec_tests = df_nb_tests_ecrits_tp_games[df_nb_tests_ecrits_tp_games['filename']==filename][LBL_NB_DEB_TESTS_PRESENTS].iloc[0]
        nb_deb_avec_tests_executes = len(df_tests_ecrits_executes_tp_deb[df_tests_ecrits_executes_tp_deb['tests_ecrits_executes']==True])
        pourcentage_deb_exec_tests_ecrits_tp = nb_deb_avec_tests_executes/nb_deb_avec_tests*100
        # résultats pour les non débutants
        df_tests_ecrits_executes_tp_non_deb = df_tests_ecrits_executes_tp_is_deb[df_tests_ecrits_executes_tp_is_deb['debutant']==False]
        nb_non_deb_avec_tests = df_nb_tests_ecrits_tp_games[df_nb_tests_ecrits_tp_games['filename']==filename][LBL_NB_NON_DEB_TESTS_PRESENTS].iloc[0]
        nb_non_deb_avec_tests_executes = len(df_tests_ecrits_executes_tp_non_deb[df_tests_ecrits_executes_tp_non_deb['tests_ecrits_executes']==True])
        pourcentage_non_deb_exec_tests_ecrits_tp = nb_non_deb_avec_tests_executes/nb_non_deb_avec_tests*100        
        df_plot_tp = pd.DataFrame({'filename' : [filename], \
                                       LBL_NB_ETUD_TESTS_PRESENTS: nb_etuds_avec_tests, \
                                       LBL_NB_DEB_TESTS_PRESENTS: nb_deb_avec_tests, \
                                       LBL_NB_NON_DEB_TESTS_PRESENTS: nb_non_deb_avec_tests,\
                                       LBL_NB_ETUD_TOUS_TESTS_EXEC: nb_etuds_avec_tests_executes, \
                                       LBL_NB_DEB_TOUS_TESTS_EXEC: nb_deb_avec_tests_executes, \
                                       LBL_NB_NON_DEB_TOUS_TESTS_EXEC: nb_non_deb_avec_tests_executes, \
                                       LBL_PCT_ETUD_TESTS_EXEC: pourcentage_exec_tests_ecrits_tp,\
                                       LBL_PCT_DEB_TESTS_EXEC: pourcentage_deb_exec_tests_ecrits_tp,\
                                       LBL_PCT_NON_DEB_TESTS_EXEC: pourcentage_non_deb_exec_tests_ecrits_tp})
        df_plot = pd.concat([df_plot, df_plot_tp], ignore_index=True)
    return df_plot


df_plot_nombre_tests_ecrits_games.columns

df_tests_ecrits_executes_games = genere_donnees_tests_ecrits_executes_games(df, df_tests_tpgame_all, df_all_verdicts, \
                                                                df_plot_nombre_tests_ecrits_games, df_is_deb)

df_tests_ecrits_executes_games

# # TODO

# Écriture des tests : combien de tests par fonction ?
#
# Éxec des tests :
#
# - n'exécutent jamais
# - régularité des tests par calcul du delta de nb fonction ajoutées entre 2 Run.Test consecutifs

# # Pistes de recherche

# Analyse :
#
# - quelle action suite à un test en échec ou erreur ?
# - les tests écrits par les étudiant·es sont-ils pertinents ?
# - les étudiant·es se contentent-ils de recopier en les adaptant les données de test suggérées par l'énoncé, quand il y en a ?
# - Analyse des comportements individuels des étudiant·es au lieu de l'analyse moyenne de la promo ? Peut-on dégager des classes de comportements ?
# - analyse temporelle des travaux. Pour notre analyse on regarde le travail le plus récent, mais pas la succession des travaux qui y ont mené. On a donc le travail le plus fini, mais on a peu ou prou un rendu Moodle à une étape intermédiaire. Par ex j'écris les tests puis le code puis je teste, ou j'écris tout le code de toutes les fonctions puis je teste sans procéder par approche itérative ?
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

# # Ref biblio à chercher

# Indicateurs de test : voir ds les refs biblio de l'article atelier APIMU un article ds lequel la métrique classique est le nb de tests ou le nb de lignes de tests écrites, pas adapté à des débutants qui ont tendance à dupliquer le même test plusieurs fois en variant un peu les valeurs si on leur met la pression pour écrire des tests. 

# Voir l'article envoyé par Yvan "coer

# Lire "Evaluating the Effectiveness of a Testing Checklist Intervention in
# CS2: An Quasi-experimental Replication Study" envoyé par Yvan le 9/12/24

# Lire ""Examining the Trade-offs between Simplified
# and Realistic Coding Environments in an
# Introductory Python Programming Class" envoyé par Yvan le 23/4/24
#
# Lire "Software Testing in Introductory Programming Courses" 14/3/24


