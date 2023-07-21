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
process_raw_data("20230322.json")

# %%
logs = load_clean_data("traces_clean.csv")

# %%
select_sessions_by_duration(logs, min_duration='00:60:00', max_duration='01:30:00')

# %%
plot_actor_sessions(logs, '032a0e61f26bba1')

# %%
fig = plot_actor_sessions(logs,'5e4e413bfce200d')
plt.savefig('sessions.png')

# %%
traces = logs.loc[logs['actor'] == '5e4e413bfce200d'].groupby(['session.id'], sort=False)
for session, session_logs in traces:
    print(f"------------- {session} ---------------")
    print(session_logs.iloc[0][['timestamp', 'verb', 'session.duration']])
    print(session_logs.iloc[-1][['timestamp', 'verb', 'session.duration']])


# %%
fig = plot_tp_sessions(logs, '2023-01-31', '10:10', '11:50', scaled=True)
plt.savefig('tp_mardi_13092022_matin_scaled.png')

# %%
actor_session_logs = logs.loc[logs['actor'] == '5e4e413bfce200d'].groupby('session.id')
nb_sessions = actor_session_logs.ngroups
print(nb_sessions)
plot = 0
for session, session_logs in actor_session_logs:
    time_data = session_logs.loc[logs['verb'] == 'Session.End']
    #session_duration = time_data['session.duration'].to_pytimedelta().total_seconds()
    print(time_data['session.duration'].iloc[0].to_pytimedelta().total_seconds())



