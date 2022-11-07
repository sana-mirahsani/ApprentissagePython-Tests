# %%
import sys
sys.path.append('../') # ces deux lignes permettent au notebook de trouver le chemin jusqu'au code source contenu dans 'src'

from src import * # on importe ce qui se trouve dans 'src'
import pandas as pd # on importe 'pandas' qui sera a priori utilisé dans la majorité des notebooks

# ces deux lignes gèrent l'auto-import : à chaque fois qu'un fichier source est MODIFIÉ et ENREGISTRÉ, 
# il n'est pas utile de relancer le notebook pour prendre en compte les modifications apportées au code source

%load_ext autoreload 
%autoreload 2

# %% [markdown]
# # Nettoyage des traces

# %%
process_raw_data("traces.json")

# %%
logs = pd.read_csv(interim_data_dir + "traces_clean.csv", index_col=0, keep_default_na=False, parse_dates=['timestamp'])

# %% [markdown]
# # Calculs d'indicateurs généraux

# %%
print_sessions_count(logs)

# %%
print_users_count(logs)

# %%
print_sessions_counts(logs)

# %%
select_sessions_by_duration(logs, max_duration='00:10:00')


