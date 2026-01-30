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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Preparation Workflow Overview:
# 1. Import Libraries
# 2. Load File (JSON) : traces260105_brutes.json
# 3. Clean JSON 
# 4. Convert JSON to DF
# 5. Save cleaned DataFrame : traces260105_clean.csv
# ____________________________________________
# **Explanation** 
#
# The goal of this part is to get the raw data in JSON format, cleaned them and transform it to CSV file. This code is the copy of Thomas code.
#
# File date_labels.json contains calendar week numbers, it aims to compute column 'seance', eg week 36 yields "semaine_1". This file must be verified each year.
#

# ## 1.Import Libraries

# +
import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import numpy as np
import json
import csv

from src.features import io_utils, data_cleaning
from src.data.constants import *

# filename, input from user, change it for every year
filename = "traces260105"


# +
def _clean_data(logs):
    """
    Simplifie les noms de colonnes et les valeurs sous forme d'URI.
    Enlève les colonnes inutiles.
    Met le Timestamp au bon format

    Args:
        logs (pandas.DataFrame): les logs à nettoyer

    Returns:
        pandas.DataFrame: les logs propres
    """    
    logs['timestamp.$date'] = pd.to_datetime(logs['timestamp.$date'], format='ISO8601')
    #logs.drop(UNUSED_COLUMNS, inplace=True, axis=1)
    logs.rename(columns=COLUMNS_NAMES, inplace=True)
    logs.replace(to_replace=VERB_NAMES, inplace=True)
    logs.replace('https://www.cristal.univ-lille.fr/users/', '', regex=True, inplace=True)
    logs['session.id'] = logs['session.id'].apply(str)

    return logs

def _remove_old_plugin_data(logs) -> pd.DataFrame:
    '''
    Au cas où il traînerait des races émises par une vieille
    version de L1Log.
    '''
    good_logs = logs
    if 'context.extension.https://www.cristal.univ-lille.fr/objects/Plugin' in logs:
        print("Des données de l'ancien plugin sont présentes. Elles vont être supprimées")
        to_remove = logs[~logs['context.extension.https://www.cristal.univ-lille.fr/objects/Plugin'].isnull()]
        actors_to_remove = to_remove['actor'].unique()

        print(f"{len(to_remove)} lignes vont être supprimées pour les acteurs suivants : {actors_to_remove}")
        logs.drop(COLUMNS_FROM_OLD_PLUGIN, inplace=True, axis=1)
        good_logs = logs[logs['actor'].isin(actors_to_remove)== False]

    return good_logs

def _fillna(logs):
    """ Remplace les valeurs nulles des différentes colonnes par une valeur par défaut :
    - True pour result.success
    - "" pour les autres colonnes

    Args:
        logs (pandas.DataFrame): les logs à nettoyer

    Returns:
        pandas.DataFrame: les logs sans valeurs nulles
    """    
    # 'Session.Start', 'File.Save', 'Session.End', 'File.Open', 'Docstring.Generate' n'ont pas de valeur
    # pour result.success. on force a True pour garder une colonne de booléens.
    if 'result.success' in logs.columns:
        logs.fillna({'result.success': True}, inplace=True)
        logs['result.success'] = logs['result.success'].astype(bool)
    logs.fillna("", inplace=True)
    return logs

def _remove_automatic_file_save(logs):
    """ Supprime les événements File.Save qui précèdent un RUN.Program (sauvegarde automatique)

    Args:
        logs (pandas.DataFrame): les logs à nettoyer

    Returns:
        pandas.DataFrame: les logs sans les sauvegardes inutiles
    """    
    logs.sort_values(['actor', 'timestamp.$date'], inplace=True, ignore_index=True)
    logs['remove_save'] = (logs['verb'] == 'File.Save') & (logs['verb'].shift() == 'Run.Program')

    to_remove = logs.loc[(logs['verb'] == 'File.Save') & (logs['remove_save'] == True)]

    print(f"removing {len(to_remove)} automatic file saves")

    clean = logs.drop(to_remove.index).reset_index(drop=True)
    clean.drop(['remove_save'], axis=1, inplace=True)

    return clean

def _remove_empty_sessions(logs, min_events):
    """
    Supprime les sessions vides (un ou deux événements seulement)

    Args:
        logs (pandas.DataFrame): les logs à nettoyer

    Returns:
        pandas.DataFrame: les logs avec des sessions de plus de deux événements
    """    
    logs['session_size'] = logs.groupby(['actor', 'session.id'])['verb'].transform(len)
    to_remove = logs.loc[logs['session_size'] <= min_events]
    
    print(f"removing {len(to_remove)} short sessions (less than {min_events} events)")
    
    logs.drop(to_remove.index, inplace=True)
    logs.drop(['session_size'], axis=1, inplace=True)
    logs.reset_index(drop=True, inplace=True)

    return logs

def _add_session_start_when_missing(logs, input_file, save_problems = True):
    """ Adds session start in case it would be missing from session

    Args:
        logs (pandas.DataFrame): les logs à nettoyer
        input_file (str): nom du fichier traité
        save_problems (bool, optional): sauvegarde des sessions modifiées pour analyse. Defaults to True.

    Returns:
        pandas.DataFrame: les logs avec des sessions complétées
    """
    no_start = logs.groupby('session.id').filter(lambda x: x['verb'].eq('Session.Start').sum() == 0)

    if len(no_start) > 0:
        if save_problems:
            no_start.to_csv(RAW_DATA_DIR + input_file + "_no_start.csv", index=False)

        no_start.sort_values(by=['actor', 'session.id', 'timestamp.$date'], inplace=True, ignore_index=True)
        first_verb = no_start.groupby('session.id').last().reset_index()
        first_verb['verb'] = 'Session.Start'
        first_verb['timestamp.$date'] = first_verb['timestamp.$date'] - pd.to_timedelta('1ms')

        print(f"completing {len(first_verb)} sessions with 'Session.Start'")

        with_start = pd.DataFrame(first_verb[['actor', 'session.id', 'verb', 'timestamp.$date']], columns=logs.columns)

        completed = pd.concat([logs, with_start], ignore_index=True)
        completed.sort_values(by=['actor', 'timestamp.$date'], inplace=True, ignore_index=True)
        
        return completed
    else:
        return logs

def _add_session_end_when_missing(logs, input_file, save_problems = True):
    """ Ajoute un événement 'Session.End' pour les sessions où il est absent.
    L'évenement 'Session.End' à le même 'timestamp.$date' que le dernier événement
    de la session + 1 milliseconde
    Args:
        logs (pandas.DataFrame): les logs à compléter
        input_file (str): nom du fichier traité
        save_problems (bool, optional): sauvegarde des sessions modifiées pour analyse. Defaults to True.

    Returns:
        pandas.DataFrame: les logs avec des sessions complétées
    """ 
    no_end = logs.groupby('session.id').filter(lambda x: x['verb'].eq('Session.End').sum() == 0)

    if save_problems:
        no_end.to_csv(RAW_DATA_DIR + input_file + "no_session_end.csv", index=False)

    no_end.sort_values(by=['actor', 'session.id', 'timestamp.$date'], inplace=True)

    last_verb = no_end.groupby('session.id').last().reset_index()
    last_verb['verb'] = 'Session.End'
    last_verb['timestamp.$date'] = last_verb['timestamp.$date'] + pd.to_timedelta('1ms')
    
    print(f"completing {len(last_verb)} sessions with 'Session.End'")

    with_end = pd.DataFrame(last_verb[['actor', 'session.id', 'verb', 'timestamp.$date']], columns=logs.columns)
    
    completed = pd.concat([logs, with_end], ignore_index=True)

    completed.sort_values(by=['actor', 'timestamp.$date'], inplace=True, ignore_index=True)
    
    return completed

def _remove_multiple_session_end(logs, input_file, save_problems = True):
    """
      Certaine sessions ont plusieurs 'Session.end'. Cette fonction supprime
      les fins de session en trop.

    Args:
        logs (pandas.DataFrame): les logs à nettoyer
        input_file (str): nom du fichier traité
        save_problems (bool, optional): sauvegarde des sessions modifiées pour analyse. Defaults to True.

    Returns:
        pandas.DataFrame: des logs pour lesquels il n'y a qu'un 'Session.end' par session
    """
    logs.sort_values(by=['actor', 'session.id', 'timestamp.$date'], inplace=True, ignore_index=True)

    more_ends = logs.groupby('session.id').filter(lambda x: x['verb'].eq('Session.End').sum() > 1)

    if save_problems:
        more_ends.to_csv(RAW_DATA_DIR + input_file + "multi_session_end.csv", index=False)

    one_end = more_ends[~(more_ends.duplicated(subset=['session.id', 'verb'], keep='last') & (more_ends['verb'] == 'Session.End'))]

    print (f"removing {len(more_ends) - len(one_end)} duplicated 'Session.End'")

    logs.drop(more_ends.index, inplace=True)
    cleaned = pd.concat([logs, one_end], ignore_index=True)

    cleaned.sort_values(by=['actor', 'timestamp.$date'], inplace=True, ignore_index=True)

    return cleaned

def _add_session_timings(logs):
    """
    Ajoute la colonne 'time_delta' qui indique le temps entre deux actions par utilisateur session ainsi
    que la colonne 'session.duration' qui indique la durée totale de la session.

    Args:
        logs (pandas.DataFrame): les logs à enrichir

    Returns:
        pandas.DataFrame: les logs enrichi
    """
    timed = logs.sort_values(by=['actor', 'timestamp.$date'], ignore_index=True)
    timed['time_delta'] = timed.groupby(['actor'])['timestamp.$date'].diff()
    timed.fillna({'time_delta':pd.Timedelta(seconds=0)}, inplace=True)
    session_items = timed.loc[timed['verb'].isin(SESSION_MARKERS)].groupby(['actor', 'session.id'])
    timed['session.duration'] = session_items['timestamp.$date'].diff()

    timed.sort_values(by=['actor', 'timestamp.$date'], inplace=True, ignore_index=True)
    return timed

def _attribute_week_label(timestamp):
    """
    Computes eg "semaine_1" from week "36" (36 being the calendar week number)
    """
    date = str(timestamp.week)

    if date in date_labels:
        return date_labels[date]

def _add_week_label(logs):
    global date_labels

    with open(EXTERNAL_DATA_DIR + "date_labels.json", encoding='utf-8') as labels:
        date_labels = json.load(labels)
    
    logs['seance'] = logs['timestamp.$date'].apply(_attribute_week_label)
    
    return logs


def keep_research_data_only(input_file:str, output_file:str) -> None :
    """
    Filters and keeps only the data available for research from the <input_file>.CSV file and writes the filtered data to the <output_file>.CSV file. All that in
    INTERIM_DATA_DIR.
    
    Args:
        input_file (str): The name of the input CSV file located in the INTERIM_DATA_DIR.
        output_file (str): The name of the output CSV file to be saved in the INTERIM_DATA_DIR.
    """

    logs : pd.DataFrame = pd.read_csv(
        INTERIM_DATA_DIR + input_file + ".csv",
        keep_default_na=False,
        dtype={'session.id': str}
    )
    print("all logs : " + str(len(logs)))

    # filter the list of user who authorize to keep their data to research
    filtred_logs : pd.DataFrame = logs[logs['research_usage'] == '1.0']
    users : [] = []
    users.extend(filtred_logs['actor'].unique())
    filtred_users : [] = []
    for user in users :
        filtred_users += user.split('/')
    filtred_users = list(set(filtred_users))
    filtred_users.remove('')

    # Filter log to keep those of user who authorise to keep their data to research at least one time
    regex : str = ""
    for filtred_user in filtred_users :
        regex += filtred_user + '|'
    research_logs : pd.DataFrame = logs[logs['actor'].str.contains(regex[:-1], case=False, regex=True)]
    print("research logs : " + str(len(research_logs)))

    research_logs.to_csv(INTERIM_DATA_DIR + output_file + ".csv", na_rep="", index=False)


# -

def process_raw_data(input_file, output_file):
    """
    Nettoie et enrichit les données brutes. Celles-ci sont ensuite sauvegardées dans data/interim/traces_clean.csv

    Args:
        input_file (String): nom du fichier de traces brutes
        output_file (String): nom du fichier de sortie
    """
    with open(RAW_DATA_DIR + input_file, encoding='utf-8') as f:
        d = json.load(f)
    logs = pd.json_normalize(d)
    del d # free memory ?
    print("Columns in the logs DataFrame:", logs.columns)
    
    logs = _clean_data(logs)

    filename = input_file.strip().split('.')[0]
    
    logs = _remove_old_plugin_data(logs)
    print(type(logs))
    logs = _remove_automatic_file_save(logs)
    print("error1")
    logs = _add_session_start_when_missing(logs, filename)
    print("error2")
    logs = _add_session_end_when_missing(logs, filename)
    print("error3")
    logs = _remove_multiple_session_end(logs, filename)
    print("error4")
    logs = _remove_empty_sessions(logs, min_events=2)
    print("error5")
    logs = _add_session_timings(logs)
    print("error6")
    logs = _add_week_label(logs)
    print("error7")
    logs = _fillna(logs)
    print("error8")
    logs.sort_values(by=['actor', 'session.id', 'timestamp.$date'], inplace=True, ignore_index=True)
    print("error9")
    logs.to_csv(INTERIM_DATA_DIR + output_file, na_rep="", index=False, escapechar="\\")
    print("error10")
    # in an older version : compute parallel sessions, see Thomas' branch


def process_data_clean(input_file:str, output_file:str) -> None :
    '''Nettoie les traces trouvées dans <input_file>.json et les enregistre sous <output_file>.csv dans INTERIM_DATA_DIR.
        
    Args:
        input_file : préfixe du fichier json contenant les traces brutes
        output_file : préfixe du fichier csv contenant les traces nettoyées
    
    Returns: None
    '''
    process_raw_data(input_file + ".json", output_file + ".csv")


process_data_clean(filename, filename + "_clean") 
