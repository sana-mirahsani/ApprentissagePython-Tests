import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import *
from ..data.constants import *

def plot_session(ax, logs):

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
    positions.append(logs.loc[logs['verb'] == 'Session.Start']['timestamp'])
    positions.append(logs.loc[logs['verb'] == 'Session.End']['timestamp'])
    positions.append(logs.loc[logs['verb'] == 'File.Save']['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Program') & (logs['result.success'] == True)]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Program') & (logs['result.success'] == False)]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Command') & (logs['result.success'] == True)]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Command') & (logs['result.success'] == False)]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Test') & (logs['result.success'] == True)]['timestamp'])
    positions.append(logs.loc[(logs['verb'] == 'Run.Test') & (logs['result.success'] == False)]['timestamp'])
    positions.append(logs.loc[logs['verb'] == 'Docstring.Generate']['timestamp'])
    
    linelength = [1,1] + [.5] * 8

    ax.set_xlabel('event timestamp')
    ax.set_yticks([])
    #ax.set_ylabels(['failure', 'success']) 

    ax.set(ylim=(-1.5, 1.5))#, yticks=np.arange(1, 8))
    ax.eventplot(positions=positions, lineoffsets=[.5, .5, .25, .25, -.25, .25, -.25, .25, -.25, .25],\
        linelengths=linelength, colors=colors)

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
    #fig.subplots_adjust(hspace=.5, bottom=.5)
    plot = 0
    for session, session_logs in actor_session_logs:
        plot_session(axs[plot], session_logs)
    
        time_data = session_logs.loc[logs['verb'] == 'Session.End']

        session_duration = time_data['session.duration'].iloc[0].to_pytimedelta().total_seconds()
        session_duration_hours = int(session_duration / 3600)
        session_duration_minutes = int((session_duration - session_duration_hours * 3600) / 60)
        session_date = time_data['timestamp'].iloc[0].date()

        axs[plot].set_title(f"Session {session} de l'étudiant {actor}\nle {session_date} - durée : {session_duration_hours}h{session_duration_minutes:02}")
        plot += 1

    fig.tight_layout()
    return fig

def plot_tp_sessions(logs, date, start, end, scaled=False):
    tp_logs = logs.loc[(logs['timestamp'].dt.strftime('%Y-%m-%d') == date)
            & (logs['timestamp'].dt.strftime('%H:%M') > start)
            & (logs['timestamp'].dt.strftime('%H:%M') < end)]

    tp_actor_logs = tp_logs.groupby('actor')
    nb_actors = tp_actor_logs.ngroups
    if scaled == True:
        start_dt = datetime.combine(datetime.fromisoformat(date), time.fromisoformat(start))
        end_dt = datetime.combine(datetime.fromisoformat(date), time.fromisoformat(end))

    fig, axs = plt.subplots(nb_actors,1, squeeze = True, figsize=(14, 3*nb_actors))
    plot = 0
    for actor, actor_logs in tp_actor_logs:
        plot_session(axs[plot], actor_logs)
        if scaled == True:
            axs[plot].set_xlim(start_dt, end_dt)
        axs[plot].set_title(f"acteur {actor} - {date}")
        plot += 1

    fig.tight_layout()
    return fig

    def plot_session_scaled(ax, logs, xmin, xmax):
        pass

def plot_actions_and_test_per_week(logs):
    timed = logs.set_index('timestamp')
    sampled_timed = timed.resample('W')
    sampled_tests = timed.loc[timed['verb'] == 'Run.Test'].resample('W')

    df = pd.DataFrame(sampled_timed.size(), columns=['all'])
    
    df['test'] = sampled_tests.size()
    ax = df.plot(kind='bar', figsize=(10,4))
    
    ax.legend(['toutes actions', 'Run.Test'])
    plt.xticks(rotation = 45)
    ticklabels = [item.strftime('%W') for item in sampled_timed.groups]
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    ax.set_xlabel("semaines de TP")
    ax.set_ylabel("Nombre total d'actions par TP")
    ax.set_title("Visualisation du nombre d'actions et de tests par TP")
    
    plt.savefig('nb_actions_et_tests.png')