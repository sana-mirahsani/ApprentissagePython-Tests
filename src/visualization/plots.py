import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from ..data.constants import *

def plot_session(ax, logs):
    actor = logs['actor'].unique()[0]
    session = logs['session.id'].unique()[0]
    
    # recherche de la fin de session. Pour l'instant il semble que l'événement peut ne pas être présent
    # dans ce cas, on ne fait pas le graphe
    time_data = logs.loc[logs['verb'] == 'Session.end']
    if len(time_data) == 0:
        return ax

    session_duration = time_data['session.duration'].iloc[0].to_pytimedelta().total_seconds()
    session_duration_hours = int(session_duration / 3600)
    session_duration_minutes = int((session_duration - session_duration_hours * 3600) / 60)
    session_date = time_data['timestamp'].iloc[0].date()

    # Insertion de labels et de couleurs en double pour gérer les événements avec et sans erreur
    colors = list(verb_colors.values())
    colors.insert(4, verb_colors['Run.Program'])
    colors.insert(6, verb_colors['Run.Command'])
    colors.insert(8, verb_colors['Run.Test'])

    labels = list(verb_colors.keys())
    labels.insert(4,'_hidden')
    labels.insert(6,'_hidden')
    labels.insert(8,'_hidden')

    # Génération d'une liste par événement pour matplotlib.eventplot
    positions = []
    positions.append(logs.loc[logs['verb'] == 'Session.start']['timestamp'])
    positions.append(logs.loc[logs['verb'] == 'Session.end']['timestamp'])
    positions.append(logs.loc[logs['verb'] == 'File.Save']['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Program') & (logs['result.success'] == 'True')]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Program') & (logs['result.success'] == 'False')]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Command') & (logs['result.success'] == 'True')]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Command') & (logs['result.success'] == 'False')]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Test') & (logs['result.success'] == 'True')]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Test') & (logs['result.success'] == 'False')]['timestamp'])
    positions.append(logs.loc[logs['verb'] == 'Docstring.Generate']['timestamp'])
    
    ax.set_xlabel('event timestamp')
    ax.set_title(f"Session {session} de l'étudiant {actor}\nle {session_date} - durée : {session_duration_hours}h{session_duration_minutes}")

    ax.eventplot(positions=positions, lineoffsets=[.25, .25, .25, .25, -.25, .25, -.25, .25, -.25, .25], linelength=.5, colors=colors)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')

    ax.legend(labels, loc='lower left', ncol=4)
    ax.axhline(0, ls='-', color='k')
    ax.text(0.9, .85, 'Success', transform=ax.transAxes, fontsize=12)
    ax.text(0.9, 0.1, 'Failure', transform=ax.transAxes, fontsize=12)
    
    return ax

def plot_actor_sessions(logs, actor):
    actor_session_logs = logs.loc[logs['actor'] == actor].groupby('session.id')
    nb_sessions = actor_session_logs.ngroups

    fig, axs = plt.subplots(nb_sessions,1, squeeze = True, figsize=(14, 3*nb_sessions))
    plot = 0
    for session, session_logs in actor_session_logs:
        print(session)
        plot_session(axs[plot], session_logs)
        plot += 1

    fig.tight_layout()
    return fig