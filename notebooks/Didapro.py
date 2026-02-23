# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.19.1
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

# Ici c'est faux, j'ajoute la colonne 'debutant' uniquement en me basant sur l'acteur. Il ne faut pas utiliser ce champ 'debutant' du df.

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
    union(actors + binomes - '')
    """
    set_actor_df = set(df.actor)
    assert '' not in set_actor_df
    set_binome_df = set(df.binome)
    if '' in set_binome_df:
        set_binome_df.remove('')
    return set_actor_df.union(set_binome_df)


print(f"Le df après nettoyage contient {len(actors(df_raw))} acteurs et {len(df_raw)} lignes")

# Ici on ajoute la colonne 'debutants' ET on propage, pourquoi j'ai fait ça en une seule ligne ???

df_propag = propage_chgt_avis_research_OK(df_deb)

# Attention dans la ligne ci-dessous il ne faut pas écrire != '0.0' à la place de == "1.0". En effet les Session.End n'ont pas de valeur pour research_usage. donc si on regarde les != 0.0 on les garde ds le df à analyser, ce qui donne des étudiant·es qui n'ont que des Session.End ! 

# df contient l'info 'debutant', et slt les RGPD compatibles.

df = df_propag[df_propag['research_usage']== '1.0']

print(f"Le df après RGPD contient {len(actors(df))} acteurs et binômes et {len(df)} lignes")


def is_deb_def(df_admin:pd.DataFrame) -> pd.DataFrame:
    """
    Construit un DataFrame de colonne 'actor' et 'debutant'
    """
    df_admin_copy = df_admin.copy()
    df_admin_copy['debutant'] = (df_admin_copy['NSI']!='NSI2') & (df_admin_copy['redoublant']=='non')
    df_admin_actor_debutants = df_admin_copy[['actor', 'debutant']]
    return df_admin_actor_debutants


# TODO ici ajouter des tests pour qques étudiant·es

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
    assert len(set(res)) == len(res)
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


df_tp2_guide_prog = df_TP_guides_prog(df, ['Tp2'])

len(actors(df_tp2_guide_prog))


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
        df_tp_deb = df_tp[df_tp['debutant']==True] # ici il ne faut pas faire ça
        actors_set = actors(df_tp)
        actors_deb_set = actors(df_tp_deb)
        dict_tp = {'TP': [tp], 'nb_etud' : len(actors_set), 'nb_debutants' : len(actors_deb_set), 'pourcentage_debutants' : round(len(actors_deb_set)/len(actors_set)*100)}
        df_res = pd.concat([df_res, pd.DataFrame.from_dict(data=dict_tp)], ignore_index=True)
    return df_res


def genere_donnees_presentation_TP_guides_corrige(df:pd.DataFrame, df_is_deb_param:pd.DataFrame) -> pd.DataFrame:
    """
    Produit un df avec les colonnes suivantes :
        - TP : le numéro du TP
        - nb_etud : le nombre d'étudiants ayant réalisé ce TP
        - nb_debutants : le nombre de débutants ayant réalisé ce TP
        - pourcentage_debutants : le pourcentage de débutants ayant réalisé ce TP

    Args:
        df : le df initial avec l'indication de cursus, colonnes 'TP', 'Type_TP', 'actor', 'binome', 'filename_infere', 'debutant'
        df_is_deb_param : le df de colonnes 'actor' 'debutant'
        
    """
    df_param = df_TP_guides_prog(df, TPS_SANS_SEM_5)
    df_res = pd.DataFrame(columns=['TP', 'nb_etud', 'nb_debutants', 'pourcentage_debutants'])
    for tp in TPS_SANS_SEM_5:
        df_tp = df_param[df_param['TP'] == tp]
        #df_tp_deb = df_tp[df_tp['debutant']==True] # ici il ne faut pas faire ça
        actors_set = actors(df_tp)
        actors_deb_set = select_debutants(actors_set, df_is_deb_param.copy())
        dict_tp = {'TP': [tp], 'nb_etud' : len(actors_set), 'nb_debutants' : len(actors_deb_set), 'pourcentage_debutants' : round(len(actors_deb_set)/len(actors_set)*100)}
        df_res = pd.concat([df_res, pd.DataFrame.from_dict(data=dict_tp)], ignore_index=True)
    return df_res


df_param_local = df_TP_guides_prog(df, TPS_SANS_SEM_5)
df_tp_tp2_local = df_param_local[df_param_local['TP'] == 'Tp2']
df_tp_deb_tp2_local = df_tp_tp2_local[df_tp_tp2_local['debutant']==True]
actors_set_tp2_local = actors(df_tp_tp2_local)
actors_deb_set_tp2_local = actors(df_tp_deb_tp2_local) 
# ici on récupère 3 non débutants 'luc.duriez.etu', 'mohamed-el-amine.samahri.etu', 'samuel.huret.etu'
# et a priori on rate 4 débutants {'hajar.amnay.etu', 'henry.hebelamou.etu', 'qassim.kahoul.etu', 'yanis.brahimi.etu'}

len(actors_deb_set_tp2_local)

df_donnees_TP_guides = genere_donnees_presentation_TP_guides(df)

df_donnees_TP_guides

df_donnees_TP_guides_corrige = genere_donnees_presentation_TP_guides_corrige(df, df_is_deb)

# Là je retombe bien sur les données de la section ecriture de tests

df_donnees_TP_guides_corrige

print(f"Nombre de traces pour les TPs guidés : {len(df_TP_guides_prog(df, TPS_SANS_SEM_5))}")

print(f"Nombre d'acteurs pour les TPs guidés : {len(actors(df_TP_guides_prog(df, TPS_SANS_SEM_5)))}")


def affiche_acteurs(df) -> None:
    actors_df_total = actors(df)
    df_prog = df_TP_guides_prog(df, TPS_SANS_SEM_5)
    actors_df_prog = actors(df_prog)
    actors_sans_prog = set(actors_df_total) - set(actors_df_prog)
    print(f"acteurs sans activité prog : {actors_sans_prog}")


affiche_acteurs(df)

df_donnees_TP_guides['nb_etud'].astype(int).describe()

df_donnees_TP_guides_corrige['nb_etud'].astype(int).describe()

df_donnees_TP_guides['pourcentage_debutants'].astype(float).describe()

df_donnees_TP_guides_corrige['pourcentage_debutants'].astype(float).describe()


# **TODO revoir ce texte** Le nombre d'étudiant·es ayant réalisé en présentiel les TPs guidés oscille entre 152 (semaine 9) et 181 (semaine 4) selon la semaine, avec une moyenne de 168 étudiant·es par semaine. Les chiffres reflètent l'évolution de la promotion au fil du semestre, avec une décroissance des effectifs à partir du milieu du semestre dûe aux abandons.  Parmi ces étudiant·es, le pourcentage d'étudiant·es débutant·es ayant réalisé en présentiel les TPs guidés oscille entre 53 (semaine 6) et et 58% (semaine 7) selon la semaine, avec une moyenne de 56% d'étudiant·es débutant·es (écart-type : 1.68).

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

# prendre cette figure pour l'article

plot_TPs_guides_general(df_donnees_TP_guides_corrige)

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

# Les tests sont cherchés dans les fichiers récupérés dans les contenus d'éditeur. Pour un·e étudiant·e donné·e les traces contiennent de nombreux contenus d'éditeurs relatifs à un TP donné, qui représentent la chronologie du travail de l'étudiant·e. Il faut en choisir un. Le principe adopté ici est de prendre le contenu de l'éditeur qui a l'horodatage le plus récent et qu'on peut imaginer être le travail le plus abouti. Cette heuristique ne marche pas toujours : nous avons trouvé l'activité de débutant·es pour lesquelles on trouve le début d'un TP réalisé, puis la fin sans le début. Dans ce cas seule la fin du TP sera prise en compte dans l'analyse.
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

# Cette variable est très mal nommée : il ne s'agit pas des débutant·es mais du df "nb de tests par fonction" qui contient l'info "débutant ou pas". Et cette info est correcte, car pas de pb de binôme ici.

df_tests_number_tp_prog_deb = merge_debutant(df_tests_number_tp_prog, df_is_deb)

df_is_deb[df_is_deb['actor']=='ibn-farrid.sama.etu']

df_is_deb[df_is_deb['actor']=='aurelien.dez.etu']

df_tests_number_tp_prog_deb


def nb_tests_par_etud_par_fonction_tp(tp:str, df_tests_number:pd.DataFrame) -> float:
    """
    Renvoie la moyenne du nb moyen de tests que chaque étudiant a écrit par fonction pour le tp `tp`.
    """
    df_tests_number_tp = df_tests_number[df_tests_number['tp']==tp].copy()
    # 1er mean : nb de test moyen des tests écrits par fonctio, par étudiant
    # 2ème mean : la moyenne de ce nombre
    return df_tests_number_tp.groupby('actor').tests_number.mean().mean()


def nb_tests_par_etud_par_fonction(df_tests_number:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un df de colonnes 'tp' et 'nb tests par fonction moyen', 'nb tests par fonction moyen débutants', 'nb tests par fonction moyen non débutants'
    """
    df_res = pd.DataFrame()
    moyennes = []
    moyennes_deb = []
    moyennes_non_deb = []
    for tp in TPS_SANS_SEM_5:
        moyennes.append(nb_tests_par_etud_par_fonction_tp(tp, df_tests_number))
        moyennes_deb.append(nb_tests_par_etud_par_fonction_tp(tp, df_tests_number[df_tests_number['debutant']==True]))
        moyennes_non_deb.append(nb_tests_par_etud_par_fonction_tp(tp, df_tests_number[df_tests_number['debutant']==False]))
    return pd.DataFrame({'tp' : TPS_SANS_SEM_5, 'nb tests par fonction moyen' : moyennes,\
                         'nb tests par fonction moyen débutants' : moyennes_deb,
                        'nb tests par fonction moyen non débutants' : moyennes_non_deb}
                       )


def nb_tests_par_TP(tp:str, df_tests_number:pd.DataFrame) -> pd.DataFrame:
    """

    """
    df_res = pd.DataFrame(columns=['tp', 'func_name', 'nb tests moyen'])
    df_tests_number_tp = df_tests_number[df_tests_number['tp']==tp].copy()
    for func_name in PROG_FUNCTIONS_NAME_BY_TP[tp]:
        df_tests_number_tp_name = df_tests_number_tp[df_tests_number_tp['function_name']==func_name]
        nb_tests_moyen = df_tests_number_tp_name['tests_number'].mean()
        petit_df = pd.DataFrame({'tp' : [tp], 'func_name': func_name, 'nb tests moyen': nb_tests_moyen})
        df_res = pd.concat([df_res, petit_df], ignore_index=True)
    return df_res


nb_tests_par_TP('Tp9', df_tests_number_tp_prog_deb)

nb_tests_par_TP('Tp6', df_tests_number_tp_prog_deb)

nb_tests_par_TP('Tp4', df_tests_number_tp_prog_deb)

nb_tests_par_TP('Tp2', df_tests_number_tp_prog_deb)

df_nb_test_par_fonctions = nb_tests_par_etud_par_fonction(df_tests_number_tp_prog_deb)

df_nb_test_par_fonctions

df_nb_test_par_fonctions['nb tests par fonction moyen'].describe()


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
LBL_PCT_TESTS_ABSENTS = 'Pourcentage avec tests absents (analyse possible)'
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
                          LBL_PCT_TESTS_ABSENTS,
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
        if '' in all_students_tp:
            all_students_tp.remove('')
        deb_students_tp = select_debutants(all_students_tp, df_is_deb)
        non_deb_students_tp = list(all_students_tp - set(deb_students_tp))
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
            LBL_NB_DEB_NON_ANALYSABLE: len(deb_students_tp)-len(etud_deb_analyse_possible),\
            LBL_NB_NON_DEB_NON_ANALYSABLE: len(non_deb_students_tp)-len(etud_non_deb_analyse_possible),\
            LBL_PCT_NON_ANALYSABLE: len(etud_analyse_impossible)/len(all_students_tp)*100,\
            LBL_PCT_DEB_NON_ANALYSABLE: len(etud_deb_analyse_impossible)/len(etud_analyse_impossible)*100,\
            LBL_NB_ETUD_TESTS_PRESENTS: len(etud_avec_tests),\
            LBL_NB_DEB_TESTS_PRESENTS: len(etud_deb_avec_tests), \
            LBL_NB_NON_DEB_TESTS_PRESENTS: len(etud_avec_tests) - len(etud_deb_avec_tests),\
            LBL_PCT_TESTS_PRESENTS: len(etud_avec_tests)/len(etud_analyse_possible)*100,\
            LBL_PCT_TESTS_ABSENTS: len(etud_testant_aucune_fonction_ecrite_tp)/len(etud_analyse_possible)*100,\
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


# Nous excluons donc de notre analyse le travail des étudiant·es qui ne
# maîtrisent pas les aspects syntaxiques de Python.  Le nombre de
# travaux exclus reste toutefois faible en regard du nombre total.  Sur
# les TPs 2 à 9 nous avons exclu en moyenne 2,67\% des travaux, qui sont en moyenne à 90\% des travaux de débutant·es
# (écart-type : 17,85). %, avec une valeur de 100\% pour 5 des TPs.
# Cette sur-représentation des débutant·es est cohérente avec la non maîtrise
# syntaxique du langage.

def calcule_infos_tests_ecrits_sans_deb(df_nb_tests_ecrits_tp_guides:pd.DataFrame) -> pd.DataFrame:
    """
    Args :
        df_plot_nombre_tests_ecrits_tp_guides : colonnes définies en global
    """

    df_nb_tests_ecrits_tp_guides_sans_deb = df_nb_tests_ecrits_tp_guides.copy()
    return df_nb_tests_ecrits_tp_guides_sans_deb[['Tps', LBL_NB_ETUD, LBL_NB_ETUD_ANALYSABLE, LBL_NB_ETUD_TESTS_PRESENTS,\
                                                      LBL_PCT_TESTS_PRESENTS, \
                                                      LBL_NB_ETUD_TESTS_PRESENTS_TTES_FCTS, LBL_PCT_TTES_FCTS,\
                                                      LBL_NB_ETUD_NO_TEST,LBL_PCT_TESTS_ABSENTS, NB_ETUD_TESTS_QQ_FONCTIONS]]


df_infos_tests_ecrits_sans_deb =  calcule_infos_tests_ecrits_sans_deb(df_plot_nombre_tests_ecrits_tp_guides)
df_infos_tests_ecrits_sans_deb

df_infos_tests_ecrits_sans_deb[LBL_PCT_TESTS_PRESENTS].describe()

df_infos_tests_ecrits_sans_deb[LBL_PCT_TESTS_ABSENTS].describe()

df_infos_tests_ecrits_sans_deb[LBL_NB_ETUD_NO_TEST].astype(float).describe()

df_infos_tests_ecrits_sans_deb[LBL_PCT_TTES_FCTS].describe()


# La figure~\ref{fig:tests-dans-code-analysable} indique que les travaux syntaxiquement  analysables 
# ne contenant aucun test syntaxiquement correct sont en très petit nombre. 
# En moyenne sur l'ensemble des TPs 2,7\% des étudiant·es
# dont le travail est analysable n'ont écrit aucun test, avec un
# écart-type de 0,49.
#
# Les résultats montrent que la plupart des étudiant·es écrivent des tests pour toutes les fonctions testables réalisées. La moyenne sur les TPs indique que 86,7\% des étudiant·es dont le code est analysable écrivent des tests pour toutes les fonctions testables, avec un écart-type à 6,5, un maximum à 96,3\% pour le TP2, et un tassement pour le TP9 (pour ce TP environ 77\% des étudiant·es ayant écrit des tests l'ont fait pour toutes les fonctions testables).

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


#
# La brique de base pour le test unitaire étant la fonction, l'écriture d'au moins un test par fonction testable peut représenter un comportement nominal pour des débutant·es (le comportement nominal réel consistant à écrire un jeu de tests pertinents). Nous avons regardé quelle proportion des fonctions écrites et testables contiennent des tests (figure...). Les résultats montrent que la plupart des étudiant·es écrivent des tests pour toutes les fonctions testables qu'ils ou elles ont programmé. La moyenne sur les TPs indique que 86.7% des étudiant·es dont le code est analysable écrivent des tests pour toutes les fonctions, avec un écart-type à 6.5, un maximum à 96.3% pour le TP2, et un tassement pour le TP9 (pour ce TP environ 77% des étudiant·es ayant écrit des tests l'ont fait pour toutes les fonctions). On note que ce TP est l'un des plus difficiles du semestre, avec des boucles difficiles à écrire. 
#
# Nous n'avons pas regardé combien de fonctions ont été écrites par les étudiant·es : du point de vue de l'écriture des tests une étudiante qui n'aura écrit que 4 fonctions avec tests durant les séances est considérée de la même manière qu'une étudiante ayant écrit 10 fonctions avec tests, mais de manière différente d'une étudiante ayant écrit 12 fonctions sans aucun test. Dans le cas où toutes les fonctions ne possèdent pas de tests dans le code, nous n'avons pas regardé si c'est la dernière fonction écrite qui n'a pas de tests (ce qui peut correspondre au comportement "écrire le code, faire un test manuel puis ajouter des tests", avec fin du TP avant l'ajout des tests).
#
# Le nombre de tests par fonction moyen varie en fonction des TPs, mais reste homogène quant au cursus antérieur des étudiant·es (peu de différence constatée entre débutant·es et non débutant·es). Le nombre de tests par fonction moyen est de 2.36 (écart-type : 0.7). Le minimum moyen est constaté pour les TP2, TP6 et TP7 (autour de 1.7) et le nombre de tests par fonction moyen maximum est constaté pour le TP9 (3.4). Ces variations s'expliquent par les différences entre les feuilles d'exercices proposés et la précision des indications données concernant les tests à écrire. Par exemple, pour la fonction `repetition` du TP2 les 2 données de test pertinentes étaient données, et la nombre de test moyen pour cette fonction est très légèrement supérieur à 2. Pour la fonction `carres` de la semaine 6, le test nominal était donné, et une mise en garde globale à la feuille d'exercices rappelait que tous les tests n'étaient pas donnés. Les étudiant·es étaient censés penser à tester `carres` sur la liste vide. Le nombre moyen de tests pour cette fonction est 1.88, ce qui indique qu'un certain nombre d'étudiant·es s'est contenté du test nominal fourni. 
#
# Ces données tendent à montrer que les étudiant·es n'ont pas de problème avec la syntaxe des tests. Par contre, et même si une étude plus approfondie reste à mener, le nombre de test moyen laisse penser que les étudiant·es ont tendance à limiter les tests qu'ils écrivent à ceux qui sont indiqués dans le sujet. 

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


# Cette partie-là n'est pas dans l'article. Chiffres OK.
#
# Pour comparer le comportement moyen des débutant·es et non débutant·es pour l'écriture des tests on se base sur le pourcentage d'étudiant·es de ces 2 catégories ayant écrit au moins un test pour chaque fonction et n'ayant écrit aucun test. 
#
# Les données indiquent que 87.8% des débutants en moyenne ont écrit au moins un test pour toutes les fonctions qu'ils ont écrites (écart-type : 7), avec un minimum à 77.9% pour le TP9. Par ailleurs 85.1% des non débutants en moyenne ont écrit au moins un test pour toutes les fonctions qu'ils ont écrites (écart-type : 7.7), avec un minimum à 76.5% aussi pour le TP9. Il ne ressort donc pas de différence marquante entre les débutants et les non débutants. De plus les 2 catégories ont plus de fonctions non testées pour le TP estimé le plus difficile.  
#
# Dans le cas des étudiant·es qui n'écrivent aucun test, 3% des débutants en moyenne n'écrivent pas de test (écart-type : 1) et 2.4% des non débutants en moyenne n'écrivent pas de tests (écart-type : 0.7). On ne peut donc pas dire que le cursus des étudiant·es - vrais débutant·es ou étudiant·es ayant déjà pratiqué de la programmation Python, que ce soit en NSI ou dans le portail - influence l'écriture de tests. 

# ### Exécution des tests

# Écrire des tests sans les exécuter montre une incompréhension du processus de test. Nous cherchons donc à vérifier que chaque étudiant·e a exécuté au moins les tests de chaque fonction qu'il ou elle a écrit. Nous regardons si, pour chaque étudiant·e et pour chaque fonction pour laquelle au moins un test a été écrit, on trouve une trace de l'exécution des tests de cette fonction. Nous reprenons les fonctions et les tests écrits dans les contenus de l'éditeur sélectionnés dans la section précédente. Nous procédons en cherchant dans les traces de l'étudiant·e les actions de clic sur le bouton dit `Run.Test` qui exécute tous les tests du fichier contenu dans l'éditeur, et les actions de clic dans le menu qui exécute les tests de la fonction sélectionnée. Nous analysons les verdicts de ces traces pour voir comment les tests exécutés sont reliés aux tests qui ont été écrits, en gardant une analyse par fonction. 
#
#

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

df_all_verdicts_interm_tpprog = convert_column_tests_to_df(df[df['Type_TP'] == 'TP_prog']) 
df_all_verdicts_interm_tpprog['name'] = df_all_verdicts_interm_tpprog['name'].apply(nom_fonction)
df_all_verdicts_tpprog = df_all_verdicts_interm_tpprog.copy()

# #### Étudiants qui n'exécutent pas du tout les tests qu'ils ont écrits

LBL_NB_ETUD_TOUS_TESTS_EXEC = "Nb étudiant·es avec tous tests exécutés"
LBL_NB_DEB_TOUS_TESTS_EXEC = "Nb débutant·es avec tous tests exécutés"
LBL_NB_NON_DEB_TOUS_TESTS_EXEC = "Nb non débutant·es avec tous tests exécutés"
LBL_PCT_ETUD_TESTS_EXEC = 'pourcentage étud avec tous tests exécutés'
LBL_PCT_DEB_TESTS_EXEC = 'pourcentage déb avec tous tests exécutés'
LBL_PCT_NON_DEB_TESTS_EXEC = 'pourcentage non déb avec tous tests exécutés'


def acteurs_au_moins_un_test_ecrit_tp(df_tests_number:pd.DataFrame, tp:str) -> list[str]:
    """
    Renvoie les étudiant·es qui ont écrit au moins un test pour le `tp`.
    """
    df_tests_number_sans_nan = df_tests_number[df_tests_number['tp']==tp].copy() # au cas où
    # Rappel : NaN pour le nb de tests qd la fonction n'existe pas dans le code analysé 
    df_tests_number_sans_nan = df_tests_number_sans_nan[pd.notna(df_tests_number_sans_nan['tests_number'])]
    df_tests_number_sans_nan['tests_number_not_nul'] = df_tests_number_sans_nan['tests_number'].map(lambda x : x > 0)
    df_tests_numbers_au_moins_un_test_interm = df_tests_number_sans_nan.groupby(['actor']).tests_number_not_nul.any()
    df_tests_numbers_au_moins_un_test = df_tests_numbers_au_moins_un_test_interm[df_tests_numbers_au_moins_un_test_interm==True]
    actors_au_moins_un_test =  df_tests_numbers_au_moins_un_test.index
    return actors_au_moins_un_test


def df_acteurs_au_moins_un_test_ecrit(df_tests_number:pd.DataFrame, df_is_deb:pd.DataFrame) -> list[str]:
    """
    Renvoie un df avec 'tp' et le nb d'étudiant·es qui ont écrit au moins un test
    """
    df_res = pd.DataFrame(columns=['tp', LBL_NB_ETUD_TESTS_PRESENTS, LBL_NB_DEB_TESTS_PRESENTS, LBL_NB_NON_DEB_TESTS_PRESENTS])
    for tp in TPS_SANS_SEM_5:
        actors_au_moins_un_test = acteurs_au_moins_un_test_ecrit_tp(df_tests_number, tp)
        actors_deb_au_moins_un_test = select_debutants(actors_au_moins_un_test, df_is_deb)
        actors_non_deb_au_moins_un_test = list(set(actors_au_moins_un_test) - set(actors_deb_au_moins_un_test))
        petit_df = pd.DataFrame({'tp':[tp], LBL_NB_ETUD_TESTS_PRESENTS:len(actors_au_moins_un_test),\
                                 LBL_NB_DEB_TESTS_PRESENTS:len(actors_deb_au_moins_un_test),\
                                LBL_NB_NON_DEB_TESTS_PRESENTS:len(actors_non_deb_au_moins_un_test)})
        df_res = pd.concat([df_res, petit_df], ignore_index=True)
    return df_res


df_acteurs_au_moins_un_test_ecrit(df_tests_number_tp_prog, df_is_deb)


def acteurs_0_RunTest_tpprog_tp(df:pd.DataFrame, tp:str) -> list[str]:
    """
    Renvoie les acteurs qui n'ont aucun Run.Test pour `tp` dans les tpprog.
    """
    etud_no_runTest = []
    if tp=='Tp8':
        df_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == 'while.py')]
    else:
        df_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]
    etuds_tp = actors(df_tp)
    for etud in etuds_tp:
            df_tp_etud = df_tp[(df_tp['actor'] == etud) | (df_tp['binome'] == etud)]
            verbs = df_tp_etud.verb.unique()
            if 'Run.Test' not in verbs:
                etud_no_runTest.append(etud)
    return etud_no_runTest


def acteurs_0_non_empty_RunTest_tpprog_tp(df:pd.DataFrame, tp:str) -> list[str]:
    """
    Renvoie les acteurs qui n'ont aucun Run.Test non vide pour `tp` dans les tpprog.
    """
    etud_no_runTest = []
    if tp=='Tp8':
        df_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == 'while.py')]
    else:
        df_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]
    etuds_tp = actors(df_tp)
    for etud in etuds_tp:
            df_tp_etud = df_tp[(df_tp['actor'] == etud) | (df_tp['binome'] == etud)]
            df_tp_etud_RT = df_tp_etud[(df_tp_etud['verb']=='Run.Test')]
            if len(df_tp_etud_RT)==0:
                etud_no_runTest.append(etud)
            else:
                tests_unique = df_tp_etud_RT.tests.unique()
                if len(tests_unique)==1 and tests_unique[0]=='[]': # test vide slt
                    etud_no_runTest.append(etud)
    return etud_no_runTest


acteurs_0_non_empty_RunTest_tpprog_tp(df, 'Tp3')

# +
LBL_NB_ETUD_NO_RUN_TEST = 'nb etud sans Run.Test ou vide uniquement'
LBL_NB_DEB_NO_RUN_TEST = 'nb deb sans Run.Test ou vide uniquement'
LBL_NB_NON_DEB_NO_RUN_TEST = 'nb non deb sans Run.Test ou vide uniquement'
LBL_NB_ETUD_TESTS_ECRITS_NO_RUN_TEST = 'nb etud tests écrits sans Run.Test non vide'
LBL_NB_DEB_TESTS_ECRITS_NO_RUN_TEST = 'nb deb tests écrits sans Run.Test non vide'
LBL_NB_NON_DEB_TESTS_ECRITS_NO_RUN_TEST = 'nb non deb tests écrits sans Run.Test non vide'
LBL_PCT_NO_RUN_TEST_QD_TESTS_ECRITS = 'pourcentage etud sans Run.Test non vide (ayant écrit des tests)'
LBL_PCT_DEB_NO_RUN_TEST_QD_TESTS_ECRITS = 'pourcentage deb sans Run.Test non vide (deb ayant écrit des tests)'
LBL_PCT_NON_DEB_NO_RUN_TEST_QD_TESTS_ECRITS = 'pourcentage non deb sans Run.Test non vide (non deb ayant écrit des tests)'
LBL_NB_FCT_TESTS_NON_EXECUTES = 'nb fonctions avec tests non exécutés'
LBL_NB_FCT_TESTS_EXECUTES = 'nb fonctions avec tests exécutés'
LBL_NB_FCT_AVEC_TESTS = 'nb fonctions avec tests écrits'
LBL_NB_ETUD_TESTS_NON_EXEC = "nb etud n'ayant pas exécuté les tests de toutes leurs fonctions (avec tests écrits)"
LBL_NB_DEB_TESTS_NON_EXEC = "nb deb n'ayant pas exécuté les tests de toutes leurs fonctions (avec tests écrits)"
LBL_NB_NON_DEB_TESTS_NON_EXEC = "nb non deb n'ayant pas exécuté les tests de toutes leurs fonctions (avec tests écrits)"
LBL_NB_ETUD_TESTS_EXEC = "nb etub avec au moins une exécution d'au moins un test écrit"
LBL_NB_ETUD_1_FCT_TESTS_NON_EXEC = "nb etud n'ayant pas exécuté les tests d'exactement une fonction (avec tests écrits)"
LBL_NB_DEB_1_FCT_TESTS_NON_EXEC = "nb deb n'ayant pas exécuté les tests d'exactement une fonction (avec tests écrits)"

LBL_NB_ETUD_TOUTES_FCTS_TESTS_EXEC = "nb etud ayant exécuté les tests de toutes leurs fonctions (avec tests écrits)"
LBL_NB_DEB_TOUTES_FCTS_TESTS_EXEC = "nb deb ayant exécuté les tests de toutes leurs fonctions (avec tests écrits)"
LBL_NB_NON_DEB_TOUTES_FCTS_TESTS_EXEC = "nb non deb ayant exécuté les tests de toutes leurs fonctions (avec tests écrits)"
LBL_PCT_ETUD_TOUTES_FCTS_TESTS_EXEC = 'pourcentage etud avec exec des tests pour toute fonction (nb etud avec tests écrits)'
LBL_PCT_DEB_TOUTES_FCTS_TESTS_EXEC = 'pourcentage deb avec exec des tests pour toute fonction (nb deb avec tests écrits)'

LBL_PCT_ETUD_FCTS_TESTS_NON_EXEC = 'pourcentage etud avec non exec des tests pour certaines fonctions (nb etud avec tests écrits)'
LBL_PCT_DEB_FCTS_TESTS_NON_EXEC = 'pourcentage deb avec non exec des tests pour certaines fonctions (nb deb avec tests écrits)'

LBL_PCT_ETUD_TESTS_NON_EXEC = 'pourcentage etud avec certaines fonctions aux tests non exécutés (nb etud avec tests écrits)'
LBL_PCT_DEB_TESTS_NON_EXEC = 'pourcentage deb avec certaines fonctions aux tests non exécutés (nb deb avec tests écrits)'
LBL_PCT_ETUD_1_FCT_TESTS_NON_EXEC = 'pourcentage etud avec une seule fonction aux tests non exécutés (nb etud avec certains tests non exécutés)' 
LBL_PCT_DEB_1_FCT_TESTS_NON_EXEC = 'pourcentage deb avec une seule fonction aux tests non exécutés (nb etud avec certains tests non exécutés)' 
# -

LBL_NB_ETUD_TESTS_NON_EXEC


def acteurs_0_RunTest_tpprog(df:pd.DataFrame, df_is_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un df avec colonnes 'tp' et 'nb etud sans Run.Test ou vides uniquement' 
    """
    etud_no_RT = []
    etud_deb_no_RT = []
    etud_non_deb_no_RT = []
    for tp in TPS_SANS_SEM_5:
        acteurs_0_RT = acteurs_0_non_empty_RunTest_tpprog_tp(df, tp)
        acteurs_0_RT_deb = select_debutants(acteurs_0_RT, df_is_deb)
        acteurs_0_RT_non_deb = list(set(acteurs_0_RT) - set(acteurs_0_RT_deb))
        nb_0_RT = len(acteurs_0_RT)
        nb_deb_0_RT = len(acteurs_0_RT_deb)
        nb_non_deb_0_RT = len(acteurs_0_RT_non_deb)
        etud_no_RT.append(nb_0_RT)
        etud_deb_no_RT.append(nb_deb_0_RT)
        etud_non_deb_no_RT.append(nb_non_deb_0_RT)
    return pd.DataFrame({'Tps' : TPS_SANS_SEM_5, LBL_NB_ETUD_NO_RUN_TEST : etud_no_RT,\
                         LBL_NB_DEB_NO_RUN_TEST: etud_deb_no_RT,\
                        LBL_NB_NON_DEB_NO_RUN_TEST: etud_non_deb_no_RT})


acteurs_0_RunTest_tpprog(df, df_is_deb)


def acteurs_tests_ecrits_0_RunTest(df_tests_number:pd.DataFrame, df:pd.DataFrame) -> dict:
    """
    Renvoie un dico de clé les tps et de valeurs la liste des étud qui ont écrit des tests ET n'ont aucun Run.Test non vide
    """
    dico = {}
    for tp in TPS_SANS_SEM_5:
        actors_au_moins_un_test = acteurs_au_moins_un_test_ecrit_tp(df_tests_number, tp)
        etud_no_RunTest = acteurs_0_non_empty_RunTest_tpprog_tp(df, tp)
        acteurs_tests_0_RunTest = set(actors_au_moins_un_test).intersection(set(etud_no_RunTest))
        dico[tp] = list(acteurs_tests_0_RunTest)
    return dico


def pourcentage_acteurs_tests_ecrits_0_RunTest(df_tests_number:pd.DataFrame, df:pd.DataFrame,\
                                               df_is_deb:pd.DataFrame, df_infos_tests_ecrits:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un dico de clé les tps et de valeurs la liste des étud qui ont écrit des tests ET n'ont aucun Run.Test
    """
    dico = acteurs_tests_ecrits_0_RunTest(df_tests_number, df)
    dico_deb = {}
    dico_non_deb = {}
    for tp in TPS_SANS_SEM_5:
        dico_deb[tp] = select_debutants(dico[tp], df_is_deb)
        dico_non_deb[tp] = list(set(dico[tp]) - set(dico_deb[tp]))
    liste = list(len(dico[tp]) for tp in TPS_SANS_SEM_5)
    liste_deb =  list(len(dico_deb[tp]) for tp in TPS_SANS_SEM_5)
    liste_non_deb =  list(len(dico_non_deb[tp]) for tp in TPS_SANS_SEM_5)
    df_tp_nbEtud_0_RT = pd.DataFrame({'Tps' : TPS_SANS_SEM_5,\
                                      LBL_NB_ETUD_TESTS_ECRITS_NO_RUN_TEST : liste,\
                                     LBL_NB_DEB_TESTS_ECRITS_NO_RUN_TEST: liste_deb,\
                                     LBL_NB_NON_DEB_TESTS_ECRITS_NO_RUN_TEST: liste_non_deb}) # TODO ici df_infos_tests_ecrits_deb_non_deb
    colonnes = ['Tps', LBL_NB_ETUD_TESTS_ECRITS_NO_RUN_TEST, LBL_NB_DEB_TESTS_ECRITS_NO_RUN_TEST, LBL_NB_NON_DEB_TESTS_ECRITS_NO_RUN_TEST,\
                LBL_NB_ETUD_TESTS_PRESENTS, LBL_NB_DEB_TESTS_PRESENTS, LBL_NB_NON_DEB_TESTS_PRESENTS]
    df_tp_nbEtud_0_RT = df_tp_nbEtud_0_RT.merge(df_infos_tests_ecrits, on='Tps', how='inner')[colonnes]
    df_tp_nbEtud_0_RT[LBL_PCT_NO_RUN_TEST_QD_TESTS_ECRITS] = df_tp_nbEtud_0_RT[LBL_NB_ETUD_TESTS_ECRITS_NO_RUN_TEST] / df_tp_nbEtud_0_RT[LBL_NB_ETUD_TESTS_PRESENTS]*100
    df_tp_nbEtud_0_RT[LBL_PCT_DEB_NO_RUN_TEST_QD_TESTS_ECRITS] = df_tp_nbEtud_0_RT[LBL_NB_DEB_TESTS_ECRITS_NO_RUN_TEST] / df_tp_nbEtud_0_RT[LBL_NB_DEB_TESTS_PRESENTS]*100
    df_tp_nbEtud_0_RT[LBL_PCT_NON_DEB_NO_RUN_TEST_QD_TESTS_ECRITS] = df_tp_nbEtud_0_RT[LBL_NB_NON_DEB_TESTS_ECRITS_NO_RUN_TEST] / df_tp_nbEtud_0_RT[LBL_NB_NON_DEB_TESTS_PRESENTS]*100
    return df_tp_nbEtud_0_RT


def nb_acteurs_tests_ecrits_0_RunTest(df_tests_number:pd.DataFrame, df:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un dico de clé les tps et de valeurs la liste des étud qui ont écrit des tests ET n'ont aucun Run.Test non vide
    """
    dico = acteurs_tests_ecrits_0_non_empty_RunTest(df_tests_number, df)
    liste = list(len(dico[tp]) for tp in TPS_SANS_SEM_5)
    return pd.DataFrame({'Tps' : TPS_SANS_SEM_5, LBL_TESTS_NB_ETUD_ECRITS_NO_RUN_TEST : liste})


pourcentage_acteurs_tests_ecrits_0_RunTest(df_tests_number_tp_prog, df, df_is_deb, df_plot_nombre_tests_ecrits_tp_guides)

acteurs_tests_ecrits_0_RunTest(df_tests_number_tp_prog, df)


# En regardant on trouve des répétitions : 4 acteur·ices apparaissent comme non testeurs pour 2 TPs. Pour le TP2 on trouve au moins un binôme. Dans le TP7 on trouve un travail avec juste une fonction commencée. Il faudrait tout éplucher... Ces chiffres sont bas, max 6.28% étudiant·e ayant écrit des tests et sans Run.Test nonvide pour le TP4.

# #### Nb de fonctions non exécutées

# On veut regarder les étudiant·es qui ont des tests, faire "la somme" de leurs Run.Test (ou prendre le dernier ?) et voir combien de fonctions qui ont été codées n'ont pas été exécutées. Plus précis qu'un résultat binaire.

def nb_fonctions_tests_non_executes_tp(df:pd.DataFrame, df_all_verdicts:pd.DataFrame,\
                                    df_tests_number_tp_prog:pd.DataFrame, tp:str,\
                                   function_names:dict) -> pd.DataFrame:
    """
    Cette fonction renvoie un df qui contient, pour les acteurs qui ont écrit au moins un test uniquement, et pour ce tp :
        - le nb de fonctions (cadrées) avec tests écrits : celles qu'on a vu passer dans un Run.Test
        - le nb de fonctions (cadrées) avec avec tests écrits mais non exécutés : celles qu'on n'a vu passer ds aucun Run.Test
        
    Renvoie un df avec colonnes 'Tps', 'actor', 'nb fonctions avec tests écrits', 'nb fonctions avec tests écrits mais non exécutés'
    
    Arg : 
        tp : un TP
        function_names : les noms de fonctions par TP
        df_tests_number_tp_prog : colonnes ['actor', 'tp', 'function_name', 'tests_number', 'index']
        df_all_verdicts : colonnes ['original_index', 'filename', 'lineno', 'tested_line','expected_result', 'details', 'verdict', 'name', 'status']        
    """
    df_res = pd.DataFrame(columns = ['tp', 'actor', LBL_NB_FCT_AVEC_TESTS , LBL_NB_FCT_TESTS_EXECUTES, LBL_NB_FCT_TESTS_NON_EXECUTES])
    # Dans df_all_verdicts il n'y a pas les acteurs, mais il y a l'index d'origine du Run.Test
    # je passe par un merge sur cet index pour récupérer l'acteur et le binôme dans df
    # ce serait peut-être plus simple de les mettre dans df_all_verdicts lors du calcul...
    df_reduit = df.copy()
    df_reduit = df_reduit[['TP', 'actor', 'binome']].rename(columns={'TP':'tp'}) 
    df_reduit['original_index'] = df_reduit.index
    df_verdicts_with_actor = df_all_verdicts.merge(df_reduit, on='original_index', how='inner')
    # on récupère au passage tous les Run.Tests fait en manip
    df_verdicts_with_actor_tp = df_verdicts_with_actor[df_verdicts_with_actor['tp']==tp]
    df_tests_number_tp_prog_tp = df_tests_number_tp_prog[df_tests_number_tp_prog['tp']==tp]
    # acteurs avec au moins un test écrit pour une fonction de tp (tp prog)
    actors_au_moins_1_test_ecrit_tp = acteurs_au_moins_un_test_ecrit_tp(df_tests_number_tp_prog_tp, tp)
    # acteurs avec 0 Run.Test non vide, pour faire une vérif plus bas, ne sert pas ds le code fonctionnel
    actors_0_RT = acteurs_0_non_empty_RunTest_tpprog_tp(df, tp)
    for actor in actors_au_moins_1_test_ecrit_tp:
        # pour ces acteurs qui ont écrit au moins un test, on va voir quelles fonctions ont des tests
        # on filtre le df des fonctions écrites sur cet acteur
        df_tests_number_tp_prog_tp_actor =  df_tests_number_tp_prog_tp[df_tests_number_tp_prog_tp['actor']==actor]
        # on garde les lignes avec des fonctions avec tests
        df_tests_number_tp_prog_tp_actor_tests_ecrits = df_tests_number_tp_prog_tp_actor[df_tests_number_tp_prog_tp_actor['tests_number']>0]
        # on récupère le nom des fonctions
        fonctions_tests_ecrits =  df_tests_number_tp_prog_tp_actor_tests_ecrits.function_name.unique()
        # on calcule les fonctions dont les tests sont passés dans les verdicts : dc les tests ont été exécutés
        # on filtre le df des tests sur l'acteur et on garde le nom de la fonction (name)
        fonctions_tests_executes_as_actor =  df_verdicts_with_actor_tp[df_verdicts_with_actor_tp['actor']==actor].name
        fonctions_tests_executes_as_binome =  df_verdicts_with_actor_tp[df_verdicts_with_actor_tp['binome']==actor].name
        fonctions_tests_executes = set(fonctions_tests_executes_as_actor).union(set(fonctions_tests_executes_as_binome))
        #if actor == 'keba.thiam.etu':
        #    print(f'fonctions_tests_executes:{fonctions_tests_executes}')
        ### dans df_all_verdicts on récupére les Run.Test de toutes les fonctions testées, y compris celles qui étaient non guidées
        # on garde uniquement les fonctions cadrées
        fonctions_tests_executes = fonctions_tests_executes.intersection(set(function_names[tp]))
        # fonctions_tests_executes contient les noms de fonctions cadrées du tp
        # dont on a vu passer l'exec des tests par l'acteur dans les verdicts
        # Et du coup, on regarde les fonctions qui ont des tests, qui n'ont pas été exécutés
        fonctions_tests_ecrits_non_executes = set(fonctions_tests_ecrits) -  set(fonctions_tests_executes)
        if actor in actors_0_RT:
            # je vérifie que si l'acteur n'avait aucun Run.Test non vide, on ne trouve aucune fonction avec tests exécutés
            assert(len(fonctions_tests_executes)==0)
        # pourquoi j'avais mis un else ?
        # MOUISE ICI, je n'avais pas ajouté les acteurs qui ont 0 RT et dc 0 fonctions avec tests exécutés
        #else:
        df_res = pd.concat([df_res, pd.DataFrame({'tp': [tp],\
                                                  'actor' : actor,\
                                                  LBL_NB_FCT_AVEC_TESTS: len(fonctions_tests_ecrits),\
                                                  LBL_NB_FCT_TESTS_EXECUTES: len(fonctions_tests_executes),\
                                                  LBL_NB_FCT_TESTS_NON_EXECUTES: len(fonctions_tests_ecrits_non_executes)})],  ignore_index=True)
    return df_res


def nb_fonctions_tests_non_executes(df:pd.DataFrame, df_all_verdicts:pd.DataFrame,\
                                    df_tests_number_tp_prog:pd.DataFrame,\
                                   function_names:dict) -> pd.DataFrame:
    """
    Cette fonction renvoie un df qui contient, pour les acteurs qui ont écrit au moins un test uniquement, et par tp :
        - le nb de fonctions (cadrées) avec tests écrits
        - le nb de fonctions (cadrées) avec avec tests écrits mais non exécutés  
        
    Renvoie un df avec colonnes 'Tps', 'actor', 'nb fonctions avec tests écrits', 'nb fonctions avec tests écrits mais non exécutés'

    Arg : 
        tp : un TP
        function_names : les noms de fonctions par TP
        autres df : voir les noms des df ds le notebook
        
    """
    df_res = pd.DataFrame(columns = ['tp', 'actor', LBL_NB_FCT_AVEC_TESTS , LBL_NB_FCT_TESTS_EXECUTES, LBL_NB_FCT_TESTS_NON_EXECUTES])
    for tp in TPS_SANS_SEM_5:
        petit_df = nb_fonctions_tests_non_executes_tp(df, df_all_verdicts, df_tests_number_tp_prog, tp, function_names)
        df_res = pd.concat([df_res, petit_df], ignore_index=True)
    # on a travaillé sur les acteurs qui ont écrit au moins un test
    assert df_res[df_res[LBL_NB_FCT_AVEC_TESTS]==0].empty
    return df_res


df_test_ecrit_executes = nb_fonctions_tests_non_executes(df, df_all_verdicts_tpprog, df_tests_number_tp_prog, PROG_FUNCTIONS_NAME_BY_TP)

df_test_ecrit_executes[df_test_ecrit_executes[LBL_NB_FCT_TESTS_EXECUTES]==0]

# #### Différence promo et deb pour le nb de fonctions avec tests ? Un peu.

df_test_ecrit_executes.groupby('tp')[LBL_NB_FCT_AVEC_TESTS].mean()

df_test_ecrit_executes[LBL_NB_FCT_AVEC_TESTS].astype(int).describe()

actors_df_test_ecrit_executes = df_test_ecrit_executes.actor.unique()
deb_df_test_ecrit_executes = select_debutants(actors_df_test_ecrit_executes, df_is_deb)
df_test_ecrit_executes_deb = df_test_ecrit_executes[df_test_ecrit_executes['actor'].isin(deb_df_test_ecrit_executes)]

df_test_ecrit_executes_deb.groupby('tp')[LBL_NB_FCT_AVEC_TESTS].mean()

df_test_ecrit_executes_deb[LBL_NB_FCT_AVEC_TESTS].astype(int).describe()

# #### Étudiants sans tests : jamais ou occasionel ? occasionel

actors_sans_exec = df_test_ecrit_executes[df_test_ecrit_executes[LBL_NB_FCT_TESTS_EXECUTES]==0].actor.unique()
actors_sans_exec

actors_avec_exec = df_test_ecrit_executes[df_test_ecrit_executes[LBL_NB_FCT_TESTS_EXECUTES]!=0].actor.unique()

set(actors_sans_exec) - set(actors_avec_exec)


# On trouve seulement 7 étudiant·es qui n'ont jamais testé du tout.

def analyse_fonctions_tests_non_exec(df_test_ecrit_executes:pd.DataFrame, df_is_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Traite les étudiant·es qui ont au moins un test écrit, données dans df_test_ecrit_executes.
    
    Renvoie un df avec : 'tp', 'nb etud avec tests écrits', 'nb etud avec tests non exécutés', 'nb etud avec 1 fonction aux tests non exécutés'  

    Arg:
        df : avec colonnes 'tp', 'actor', 'nb fonctions avec tests écrits', 'nb fonctions avec tests exécutés', 'nb fonctions avec tests non exécutés'
    """
    df_res = pd.DataFrame(columns=['tp', LBL_NB_ETUD_TESTS_PRESENTS, LBL_NB_ETUD_TOUTES_FCTS_TESTS_EXEC, LBL_NB_DEB_TOUTES_FCTS_TESTS_EXEC, LBL_NB_ETUD_TESTS_NON_EXEC,\
                                   LBL_NB_DEB_TESTS_NON_EXEC, LBL_PCT_ETUD_TESTS_NON_EXEC, LBL_PCT_DEB_TESTS_NON_EXEC, LBL_NB_ETUD_1_FCT_TESTS_NON_EXEC])
    for tp in TPS_SANS_SEM_5:
        # filtrage tp
        df_test_ecrit_executes_tp = df_test_ecrit_executes[df_test_ecrit_executes['tp']==tp].copy()
        # df filtré : avec des fonctions aux tests non exécutés
        df_tests_ecrits_non_exec = df_test_ecrit_executes_tp[df_test_ecrit_executes_tp[LBL_NB_FCT_TESTS_NON_EXECUTES]!=0]
        # df filtré : avec uniquement des fonctions aux tests exécutés
        df_tests_ecrits_exec = df_test_ecrit_executes_tp[df_test_ecrit_executes_tp[LBL_NB_FCT_TESTS_NON_EXECUTES]==0]
        # df filtré : avec exactement une fonction aux tests non exécutés
        df_tests_ecrits_1_fct_non_testee = df_test_ecrit_executes_tp[df_test_ecrit_executes_tp[LBL_NB_FCT_TESTS_NON_EXECUTES]==1]
        # nb etud ayant écrit au moins un test
        nb_etud_tests_ecrits = len(df_test_ecrit_executes_tp)
        # nb etud avec au moins une fonction dont les tests n'ont jamais été exécutés
        nb_etud_avec_tests_non_exec = len(df_tests_ecrits_non_exec)
        # nb etud avec exactement une fonction dont les tests n'ont jamais été exécutés
        nb_etud_avec_slt_1_fct_non_exec = len(df_tests_ecrits_1_fct_non_testee)
        # pareil pour les deb
        actors_deb = select_debutants(df_test_ecrit_executes_tp.actor.unique(), df_is_deb)
        df_test_ecrit_executes_tp_deb = df_test_ecrit_executes_tp[df_test_ecrit_executes_tp['actor'].isin(actors_deb)]
        df_tests_ecrits_non_exec_deb = df_test_ecrit_executes_tp_deb[df_test_ecrit_executes_tp_deb[LBL_NB_FCT_TESTS_NON_EXECUTES]!=0]
        df_tests_ecrits_exec_deb = df_test_ecrit_executes_tp_deb[df_test_ecrit_executes_tp_deb[LBL_NB_FCT_TESTS_NON_EXECUTES]==0]
        df_tests_ecrits_1_fct_non_testee_deb = df_test_ecrit_executes_tp_deb[df_test_ecrit_executes_tp_deb[LBL_NB_FCT_TESTS_NON_EXECUTES]==1]
        nb_deb_tests_ecrits = len(df_test_ecrit_executes_tp_deb)
        nb_deb_avec_tests_non_exec = len(df_tests_ecrits_non_exec_deb)
        nb_deb_avec_slt_1_fct_non_exec = len(df_tests_ecrits_1_fct_non_testee_deb)
        petit_df = pd.DataFrame({'tp':[tp],\
                                 # nb étud avec tests écrits
                                 LBL_NB_ETUD_TESTS_PRESENTS: nb_etud_tests_ecrits,\
                                 # nb etud ayant éxec les tests de toutes les fonctions avec tests
                                 LBL_NB_ETUD_TOUTES_FCTS_TESTS_EXEC: len(df_tests_ecrits_exec),\
                                 LBL_NB_DEB_TOUTES_FCTS_TESTS_EXEC: len(df_tests_ecrits_exec_deb),\
                                 LBL_NB_ETUD_TESTS_NON_EXEC: nb_etud_avec_tests_non_exec,\
                                 # nb deb ayant éxec les tests de toutes les fonctions avec tests
                                 LBL_NB_DEB_TESTS_NON_EXEC: nb_deb_avec_tests_non_exec,\
                                 # % etud n'ayant pas éxec les tests de toutes les fonctions avec tests
                                 LBL_PCT_ETUD_TESTS_NON_EXEC: len(df_tests_ecrits_non_exec)/nb_etud_tests_ecrits*100,\
                                 LBL_PCT_DEB_TESTS_NON_EXEC: len(df_tests_ecrits_non_exec_deb)/nb_deb_tests_ecrits*100,\

                                 # pourcentage etud avec certaines fonctions aux tests non exécutés (nb etud avec tests écrits)
                                 LBL_NB_ETUD_1_FCT_TESTS_NON_EXEC: nb_etud_avec_slt_1_fct_non_exec,\
                                 LBL_NB_DEB_1_FCT_TESTS_NON_EXEC: nb_deb_avec_slt_1_fct_non_exec,\
                                 LBL_PCT_ETUD_1_FCT_TESTS_NON_EXEC: nb_etud_avec_slt_1_fct_non_exec/nb_etud_avec_tests_non_exec*100,\
                                 LBL_PCT_DEB_1_FCT_TESTS_NON_EXEC: nb_deb_avec_slt_1_fct_non_exec/nb_deb_avec_tests_non_exec*100})
        df_res = pd.concat([df_res, petit_df], ignore_index=True)
    return df_res


df_analyse_fonctions_test_non_exec = analyse_fonctions_tests_non_exec(df_test_ecrit_executes, df_is_deb)

df_analyse_fonctions_test_non_exec.columns

df_analyse_fonctions_test_non_exec


def analyse_fonctions_tests_non_exec_bis(df_tests_ecrits_executes:pd.DataFrame, df_tests_number:pd.DataFrame, df:pd.DataFrame,\
                                 df_is_deb:pd.DataFrame, df_infos_tests_ecrits:pd.DataFrame) -> pd.DataFrame:
    """
    Traite les étudiant·es qui ont des tests écrits.
    """
    df_no_RT = pourcentage_acteurs_tests_ecrits_0_RunTest(df_tests_number, df, df_is_deb, df_infos_tests_ecrits)
    df_acteurs_tests_ecrits = df_acteurs_au_moins_un_test_ecrit(df_tests_number, df_is_deb).copy()
    df_acteurs_tests_ecrits = df_acteurs_tests_ecrits.drop(columns=[LBL_NB_ETUD_TESTS_PRESENTS])   
    df_analyse_tests_executes= analyse_fonctions_tests_non_exec(df_test_ecrit_executes, df_is_deb)
    print(df_analyse_tests_executes.columns)
    df_res = df_analyse_tests_executes.merge(df_acteurs_tests_ecrits, on='tp', how='inner')
    print (df_res.columns)
    df_res[LBL_PCT_ETUD_TOUTES_FCTS_TESTS_EXEC] = df_res[LBL_NB_ETUD_TOUTES_FCTS_TESTS_EXEC]/df_res[LBL_NB_ETUD_TESTS_PRESENTS]*100
    df_res[LBL_PCT_DEB_TOUTES_FCTS_TESTS_EXEC] = df_res[LBL_NB_DEB_TOUTES_FCTS_TESTS_EXEC]/df_res[LBL_NB_DEB_TESTS_PRESENTS]*100
    df_res[LBL_NB_ETUD_TESTS_ECRITS_NO_RUN_TEST] = df_no_RT[LBL_NB_ETUD_TESTS_ECRITS_NO_RUN_TEST]
    df_res[LBL_NB_DEB_TESTS_ECRITS_NO_RUN_TEST] = df_no_RT[LBL_NB_DEB_TESTS_ECRITS_NO_RUN_TEST]
    df_res[LBL_PCT_ETUD_FCTS_TESTS_NON_EXEC] = df_res[LBL_NB_ETUD_TESTS_NON_EXEC]/df_res[LBL_NB_ETUD_TESTS_PRESENTS]*100
    df_res[LBL_PCT_DEB_FCTS_TESTS_NON_EXEC] = df_res[LBL_NB_DEB_TESTS_NON_EXEC]/df_res[LBL_NB_DEB_TESTS_PRESENTS]*100
    return df_res


df_analyse_tests_ecrits_fonctions_non_exec = analyse_fonctions_tests_non_exec_bis(df_test_ecrit_executes, df_tests_number_tp_prog, df, df_is_deb, df_plot_nombre_tests_ecrits_tp_guides)

df_analyse_tests_ecrits_fonctions_non_exec

# #### Plot

LABEL_TESTS_DE_TOUTES_FONCTION_EXECUTES = "dont les tests de toutes fonctions\n ont été exécutés"
LABEL_AUCUN_RT_NON_VIDE = "pour lesquels aucun clic significatif pour\n déclencher l'exécution de tests n'a été trouvé"
LABEL_AVEC_TESTS_NON_EXEC = "dont les tests de certaines fonctions n'ont pas été exécutés"


def plot_tests_ecrits_executes_subplot(df_tests_ecrits_exec:pd.DataFrame) -> None:
    """
    AFfiche le graphe avec le nb d'étudiants ayant exécuté tous les tests présents dans le code, ceux n'ayant aucun Run.Test, 
    et ceux qui n'ont pas exécuté les tests de certaines fonctions.

    Avec subplot
    """
    fig, ax = plt.subplots()
    bottom = np.zeros(len(TPS_SANS_SEM_5))
    dico = {LABEL_TESTS_DE_TOUTES_FONCTION_EXECUTES: df_tests_ecrits_exec[LBL_NB_ETUD_TOUTES_FCTS_TESTS_EXEC],\
            LABEL_AVEC_TESTS_NON_EXEC: df_tests_ecrits_exec[LBL_NB_ETUD_TESTS_NON_EXEC],\
           LABEL_AUCUN_RT_NON_VIDE: df_tests_ecrits_exec[LBL_NB_ETUD_TESTS_ECRITS_NO_RUN_TEST]}
    bar_colors = ['tab:green', 'tab:olive', 'tab:orange']
    i = 0
    for labels, values in dico.items():
        p = ax.bar(TPS_SANS_SEM_5, values, 0.5, label=labels, bottom=bottom, color=bar_colors[i])
        bottom += values
        i = i + 1

        ax.bar_label(p, label_type='center')

    ax.set_title('TPs guidés : étudiants ayant écrit au moins un test')
    ax.legend()

    plt.show()


plot_tests_ecrits_executes_subplot(df_analyse_tests_ecrits_fonctions_non_exec)


def plot_tests_ecrits_executes_subplot_deb(df_tests_ecrits_exec:pd.DataFrame) -> None:
    """
    AFfiche le graphe avec le nb de débutants ayant exécuté tous les tests présents dans le code, ceux n'ayant aucun Run.Test, 
    et ceux qui n'ont pas exécuté les tests de certaines fonctions.

    Avec subplot
    """
    fig, ax = plt.subplots()
    bottom = np.zeros(len(TPS_SANS_SEM_5))
    dico = {LABEL_TESTS_DE_TOUTES_FONCTION_EXECUTES: df_tests_ecrits_exec[LBL_NB_DEB_TOUTES_FCTS_TESTS_EXEC],\
            LABEL_AVEC_TESTS_NON_EXEC: df_tests_ecrits_exec[LBL_NB_DEB_TESTS_NON_EXEC],\
           LABEL_AUCUN_RT_NON_VIDE: df_tests_ecrits_exec[LBL_NB_DEB_TESTS_ECRITS_NO_RUN_TEST]}
    for labels, values in dico.items():
        p = ax.bar(TPS_SANS_SEM_5, values, 0.5, label=labels, bottom=bottom)
        bottom += values

        ax.bar_label(p, label_type='center')

    ax.set_title('TPs guidés : étudiants débutants ayant écrit au moins un test')
    ax.legend()

    plt.show()


plot_tests_ecrits_executes_subplot_deb(df_analyse_tests_ecrits_fonctions_non_exec)


def plot_tests_ecrits_executes(df_tests_ecrits_exec:pd.DataFrame) -> None:
    """
    AFfiche le graphe avec le nb d'étudiants ayant exécuté tous les tests présents dans le code, ceux n'ayant aucun Run.Test, 
    et ceux qui n'ont pas exécuté les tests de certaines fonctions.

    """
    df_plot = df_tests_ecrits_exec.copy()
    LABEL_NB_ETUD_WITH_TESTS = LBL_NB_ETUD_TESTS_PRESENTS
    df_plot = df_plot.rename(columns={LBL_NB_ETUD_TESTS_PRESENTS: LABEL_NB_ETUD_WITH_TESTS, \
                                        LBL_NB_ETUD_TOUTES_FCTS_TESTS_EXEC: LABEL_TESTS_DE_TOUTES_FONCTION_EXECUTES,
                                         LBL_NB_ETUD_TESTS_ECRITS_NO_RUN_TEST:LABEL_AUCUN_RT_NON_VIDE,
                                     LBL_NB_ETUD_TESTS_NON_EXEC: LABEL_AVEC_TESTS_NON_EXEC})
    df_plot.set_index('tp')[[LABEL_NB_ETUD_WITH_TESTS, LABEL_TESTS_DE_TOUTES_FONCTION_EXECUTES, LABEL_AUCUN_RT_NON_VIDE, LABEL_AVEC_TESTS_NON_EXEC]].plot(kind='bar', figsize=(12, 6))
    plt.title("Étudiant·es ayant travaillé sur les TPs guidés")
    plt.ylabel("Nombre d'étudiant·es")
    plt.xlabel("TPs guidés")
    plt.xticks(rotation=45)
    plt.legend(title="Nombre étudiant·es")
    plt.tight_layout()
    plt.show()


plot_tests_ecrits_executes(df_analyse_tests_ecrits_fonctions_non_exec)

df_pourcentage_acteurs_tests_ecrits_0_RunTest = pourcentage_acteurs_tests_ecrits_0_RunTest(df_tests_number_tp_prog, df, df_is_deb, df_plot_nombre_tests_ecrits_tp_guides)

df_pourcentage_acteurs_tests_ecrits_0_RunTest

df_analyse_tests_ecrits_fonctions_non_exec

df_pourcentage_acteurs_tests_ecrits_0_RunTest[LBL_PCT_NO_RUN_TEST_QD_TESTS_ECRITS].astype(float).describe()

df_pourcentage_acteurs_tests_ecrits_0_RunTest[LBL_PCT_DEB_NO_RUN_TEST_QD_TESTS_ECRITS].astype(float).describe()

df_analyse_tests_ecrits_fonctions_non_exec[LBL_PCT_ETUD_TOUTES_FCTS_TESTS_EXEC].astype(float).describe()

df_analyse_tests_ecrits_fonctions_non_exec[LBL_PCT_DEB_TOUTES_FCTS_TESTS_EXEC].astype(float).describe()

df_analyse_tests_ecrits_fonctions_non_exec[LBL_PCT_ETUD_FCTS_TESTS_NON_EXEC].astype(float).describe()

df_analyse_tests_ecrits_fonctions_non_exec[LBL_PCT_DEB_FCTS_TESTS_NON_EXEC].astype(float).describe()

df_analyse_tests_ecrits_fonctions_non_exec[LBL_PCT_ETUD_1_FCT_TESTS_NON_EXEC].astype(float).describe()

df_analyse_tests_ecrits_fonctions_non_exec[LBL_PCT_DEB_1_FCT_TESTS_NON_EXEC].astype(float).describe()

# Le graphique montre les étudiant·es ayant écrit des tests lors des TPs guidés et deux comportements extrêmes. D'une part on montre les étudiant·es qui ont exécutés (via le bouton Run.Test ou le menu L1Test) les tests de toutes les fonctions (présentant des tests) qu'ils ont écrites. Ces étudiant·es représentent en moyenne 88.5% des étudiant·es ayant écrit des tests (écart-type : 3.88), avec un minimm de 84.6% pour le TP4 et un maximum de 94.5% pour le TP6. Ce chiffre montre que la grande majorité des étudiant·es ont a priori compris qu'un test s'exécute. 
#
#
# D'autre part on montre les étudiant·es pour lesquel·les nous n'avons trouvé dans les traces aucune exécution significative de tests durant un TP donné ("significatif" signifiant ici que nous avons exclu les clics sur le bouton Run.Test qui ont été faits quand le contenu de l'éditeur ne contenait aucun test ou dans le menu L1Test sur une fonction sans test). Ces étudiant·es pour qui nous avons trouvé la présence d'au moins un test, mais sans aucune exécution via L1Test représentent en moyenne 3.18% des étudiant·es ayant écrit des tests (écart-type : 1.69), sur l'ensemble des TP, avec un maximum de 6.3% pour le TP4 et un minimum de 1.39% pour le TP8. On constate que ces étudiant·es apparaissent comme "non testeur·euse" pour un ou 2 TP seulement. Sur l'ensemble de la promotion, seul·es 7 étudiant·es présente du code avec au moins un test écrit mais n'ont jamais exécuté un test de tout le semestre. 
#
#
# Le reste des étudiant·es n'a pas exécutés les tests de toutes les fonctions écrites (exécution partielle des tests). Ces étudiant·es représentent en moyenne 11.5% des  étudiant·es ayant écrit des tests (écart-type : 3.9). 
#
#
#
# Nous n'avons pas encore analysé le comportement des étudiant·es qui exécutent tout ou partie de leurs tests. D'une part il est possible que les étudiant·es qui ont exécuté les tests d'une fonction (avec test) qu'ils ont écrite ont commencé par exécuter des appels à la fonction dans la console de Thonny, dans une approche essai-erreur, avant de rédiger des tests à partir de ces appels et éventuellement de les exécuter. Ce fonctionnement qu'on peut observer sur les écrans en TP montrerait que les étudiant·es ont compris l'intérêt de conserver une trace des appels de fonctions qui ont le comportement attendu, mais que l'exécution des tests dans L1Test offre un confort inférieur à l'exécution d'un appel de fonction dans la console.  Pour analyser cela il faudrait analyser les commandes exécutées dans la console de Thonny (ce qui n'est pas simple car nous ne savons pas bien relier une commande à un TP donné, les commandes étant décorrélées du fichier ouvert dans l'éditeur).
#
# D'autre part, quand les tests d'une fonction ne sont pas exécutés, on ne sait pas si c'est l'activité de test qui n'est pas bien maîtrisée ou si la fin de la séance de TP a stoppé l'activité de programmation au milieu de la mise au point d'une fonction. Nous avons regardé la fréquence avec laquelle le nombre de fonctions dont les tests ne sont pas exécutés est 1. En moyenne sur l'ensemble des TPs, les étudiant·es tel·les que seule une fonction a des tests non exécutés représentent 56.9% des étudiant·es avec exécution partielle (écart-type : 15.2). On peut émettre l'hypothèse que, pour ces étudiant·es, la fonction non testée était en cours d'écriture et n'avait pas encore été testée. Nous n'avons pas vérifié que cette fonction isolée est la fonction la plus récente présente dans les traces de l'étudiant·e.
#
# Pour finir, nous  n'avons pas observé de différence entre les étudiant·es débutant·es et le reste de la promotion quant à l'exécution des tests. On trouve 87.3% de débutant·es ayant exécutés (via le bouton Run.Test ou le menu L1Test) les tests de toutes les fonctions (présentant des tests) qu'ils ont écrites. On trouve 3.8% de débutant·es lesquel·les nous n'avons trouvé dans les traces aucune exécution significative de tests durant un TP donné. 
#

df_test_ecrit_executes_tp2 = nb_fonctions_tests_non_executes_tp(df, df_all_verdicts_tpprog, df_tests_number_tp_prog, 'Tp2', PROG_FUNCTIONS_NAME_BY_TP)

df_test_ecrit_executes_tp2[df_test_ecrit_executes_tp2[LBL_NB_FCT_TESTS_NON_EXECUTES]!=0]

df_test_ecrit_executes_tp3 = nb_fonctions_tests_non_executes_tp(df, df_all_verdicts_tpprog, df_tests_number_tp_prog, 'Tp3', PROG_FUNCTIONS_NAME_BY_TP)

df_test_ecrit_executes_tp3[df_test_ecrit_executes_tp3[LBL_NB_FCT_TESTS_NON_EXECUTES]!=0]

df_test_ecrit_executes_tp4 = nb_fonctions_tests_non_executes_tp(df, df_all_verdicts, df_tests_number_tp_prog, 'Tp4', PROG_FUNCTIONS_NAME_BY_TP)

df_test_ecrit_executes_tp4[df_test_ecrit_executes_tp4[LBL_NB_FCT_TESTS_NON_EXECUTES]!=0]

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

# ### Exécution des tests (vieux)

# **/!\ ce paragraphe est une horreur à écrire et ça doit être encore pire à lire** **Et en plus aucune idée de l'effet de l'heuristique, sinon que sur le coup ça me simplifiait les calculs.**

# Écrire des tests sans les exécuter montre une incompréhension du processus de test. Nous cherchons donc à vérifier que chaque étudiant·e a exécuté au moins une fois chaque test qu'il ou elle a écrit. Nous regardons si, pour chaque étudiant·e et pour chaque fonction pour laquelle au moins un test a été écrit, on trouve une trace de l'exécution des tests de cette fonction. Nous reprenons les fonctions et les tests écrits dans les contenus de l'éditeur sélectionnés dans la section précédente. Nous procédons en cherchant dans les traces de l'étudiant·e les actions de clic sur le bouton dit `Run.Test` qui exécute les tests du fichier contenu dans l'éditeur. Nous sélectionnons comme précédemment le clic le plus récent, et nous itérons en remontant le temps jusqu'à trouver un clic qui a réellement déclenché l'exécution de tests[^1]. Nous analysons les verdicts de cette trace pour voir comment les tests exécutés sont reliés aux tests écrits dans le contenu d'éditeur analysé. 
#
# Pour chaque étudiant·e nous analysons une seule trace liée à un clic sur le bouton `Run.Test`. Cette simplification peut nous conduire à ignorer des exécutions de tests quand les étudiant·es utilisent une fonctionnalité de L1Test qui permet d'exécuter les tests d'une seule fonction. Dans ce cas, si l'exécution des tests la plus récente n'a exécuté les tests que d'une fonction et pas de toutes les fonctions du fichier, on considérera que cet étudiant·es n'a pas exécuté tous les tests qu'il ou elle a écrit. 
#
# [¹]: Nous ne traitons pas les clics ayant abouti au constat que le fichier ne contient aucun test.
#
# Techniquement nous utilisons une autre heuristique. Nous vérifions seulement que, dans la trace sélectionnée liée au clic sur le bouton `Run.Test`,  on trouve une trace de l'exécution d'au moins $n$ tests pour pour toute fonction possédant $n$ tests dans le contenu d'éditeur analysé. Nous ne vérifions pas l'égalité des appels de fonction ou expressions exécutées dans les tests. 

# #### Vieux, à bouger en fin de notebook

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


def plot_tests_ecrits_executes_vieux(df_tests_ecrits_executes:pd.DataFrame) -> None:
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


plot_tests_ecrits_executes_vieux(df_tests_ecrits_executes)

df_tests_ecrits_executes[LBL_PCT_ETUD_TESTS_EXEC].describe()

df_tests_ecrits_executes[LBL_PCT_DEB_TESTS_EXEC].describe()

df_tests_ecrits_executes[LBL_PCT_NON_DEB_TESTS_EXEC].describe()

# + [markdown] jp-MarkdownHeadingCollapsed=true
# Les données montrent que 86% en moyenne des étudiant·es ayant écrit au moins un test dans leur travail ont exécuté tous les tests écrits (écart-type : 3.6), 85.4% en moyenne des débutants ayant écrit au moins un test (écart-type : 6) et 88.4% en moyenne des non débutants (écart-type : 3.6). 
# -


