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

# # Contexte de l'expérimentation

# ## Contexte de collecte des traces

# Les traces d'activité des étudiant·es ne sont collectées que sur les ordinateurs des salles de l'université, pendant les TPs. On ne collecte donc pas les traces laissées par les étudiant·es quand ils travaillent chez eux ou en dehors de ces salles. On ne collecte pas non plus les traces des étudiant·es qui travaillent sur leur ordinateur personnel durant les TPs car le nombre d'ordinateurs est insuffisant.
#
# Problème des étudiant·es travaillant en binôme quand le nombre d'ordinateur dans la salle est insuffisant. Dans ce cas une trace compte pour 2 étudiant·es, comme si on avait dupliqué la trace.
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

TPs_sans_sem5 = ['Tp2', 'Tp3', 'Tp4', 'Tp6', 'Tp7', 'Tp8', 'Tp9']


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
    df_param = df_TP_guides_prog(df, TPs_sans_sem5)
    df_res = pd.DataFrame(columns=['TP', 'nb_etud', 'nb_debutants', 'pourcentage_debutants'])
    for tp in TPs_sans_sem5:
        df_tp = df_param[df_param['TP'] == tp]
        df_tp_deb = df_tp[df_tp['debutant']==True]
        actors_set = actors(df_tp)
        actors_deb_set = actors(df_tp_deb)
        dict_tp = {'TP': [tp], 'nb_etud' : len(actors_set), 'nb_debutants' : len(actors_deb_set), 'pourcentage_debutants' : round(len(actors_deb_set)/len(actors_set)*100)}
        df_res = pd.concat([df_res, pd.DataFrame.from_dict(data=dict_tp)], ignore_index=True)
    return df_res


df_donnees_TP_guides = genere_donnees_presentation_TP_guides(df)

df_donnees_TP_guides

# Le nombre d'étudiant·es ayant réalisé en présentiel les TPs guidés oscille entre 152 et 173. Parmi ces étudiant·es, le pourcentage d'étudiant·es débutant·es ayant réalisé en présentiel les TPs guidés oscille entre 53 et 58%.

# ## Analyse de la pratique du test pour les TPs guidés

# La pratique du test implique principalement 3 activités :
#
# - écrire des tests
# - exécuter ces tests une fois le code à tester écrit
# - interpréter le verdict des tests et agir en conséquence
#
# Dans ce travail nous n'analysons pas l'action qui suit l'exécution des tests. Dans le cadre de TPs guidés puis des TPs non guidés, nous regardons si les étudiant·es ont écrit au moins un test. Puis, nous regardons si nous trouvons dans les traces une exécution de ce test ou ces tests. 
#
# Dans le cadre des TPs guidés, pour lesquels les fonctions à écrire sont connues, nous regardons de plus si les étudiant·es ont écrit un ou des tests pour chaque fonction, ou s'ils n'écrivent des tests pour aucune fonction.
#
# /!\ on ne sait pas si, qd un étudiant n'a pas exécuté tous les tests écrits sur toutes les fonctions, ce qu'il se passe. Il a peut-être exécuté les tests d'une fonction seulement en utilisant le menu de L1Test.



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
#
# Analyse qualitative :
#
# - quelle perception les étudiant·es ont de l'outil L1Test ?
# - quelle perception les étudiant·es ont du test : aide ou boulet consommeur de temps ? pensent-ils que si leurs tests passent alors leur code est correct ?
#
# Intégration du test dans les référentiels de programmation.


