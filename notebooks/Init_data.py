#!/usr/bin/env python
# coding: utf-8
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
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

# +
## Travail de Thomas PFE 2425
# # Initialisation des donnees
# reprise pour 2526

# +


import sys
sys.path.append('../') # ces deux lignes permettent au notebook de trouver le chemin jusqu'au code source contenu dans 'src'
sys.path.append('../src/')
from src import * # on importe ce qui se trouve dans 'src'
import pandas as pd
from src import script_initialisation, clean_corrupted_data
from src.data import cleaning, anonymizing
# %load_ext autoreload 
# %autoreload 2


# +


filename = "traces_26_01_05"


# Corrige les différence de version de thonny dans les traces (Il n'est pas nécessaire actuellement mais gardé au cas où)

# +


#clean_corrupted_data.main(filename, filename + "_corrigee")


# Convertie le json en un csv utilisable pour les notebooks

# +


script_initialisation.process_data_clean(filename, filename + "_clean")


# Sépart les données exploitable pour la recherche du reste

# +


cleaning.keep_research_data_only(filename + "_clean", filename + "_research")


# Anonymiser les données

# +


anonymizing.anonymize_data(filename + "_research", filename + "_anonyme", filename + "_anonymized_actors")




# +

# Crée le dataframe de test (hs suite a des problèmes dans les tags)
#script_initialisation.process_tests_dataframe(filename + "_research", filename + "_tests_dataframe")


# On genere un csv divisant les adresses etudiantes selon leurs acceptations de l'utilisation de leurs données pour la recherche en trois colonnes (oui, oui par bynome, non)

# +


script_initialisation.generate_authorizations_csv(filename + "_clean", filename + "_authorize")

# -


