# %%
import sys
sys.path.append('../') # ces deux lignes permettent au notebook de trouver le chemin jusqu'au code source contenu dans 'src'

from src import * # on importe ce qui se trouve dans 'src'
import pandas as pd # on importe 'pandas' qui sera a priori utilisé dans la majorité des notebooks
import matplotlib.pyplot as plt

# ces deux lignes gèrent l'auto-import : à chaque fois qu'un fichier source est MODIFIÉ et ENREGISTRÉ, 
# il n'est pas utile de relancer le notebook pour prendre en compte les modifications apportées au code source

%load_ext autoreload 
%autoreload 2

# %%
#process_raw_data("traces_17_01_23.json")

# %%
logs = load_clean_data("traces_clean.csv")

# %% [markdown]
# # Calcul du nombre de sessions et de la durée moyenne des sessions

# %%
print_sessions_count(logs)
logs['session.duration'].describe()

# %%
print_users_count(logs)

# %% [markdown]
# # Nombre d'actions par session

# %%
actions = logs[['actor', 'session.id', 'verb']]
actions.groupby(['actor', 'session.id']).size().plot()




