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


