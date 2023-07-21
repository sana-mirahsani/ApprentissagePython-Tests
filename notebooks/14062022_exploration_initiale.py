# %%
import json
import pandas as pd
from pandas.io.json import json_normalize

# %%
raw_data_dir = "../data/raw/"
interim_data_dir = "../data/interim/"
processed_data_dir = "../data/processed/"

# %%
with open(raw_data_dir + "traces.json") as f:
    d = json.load(f)
raw_logs = pd.json_normalize(d)
raw_logs.axes

# %% [markdown]
# # Nettoyage des colonnes

# %%
raw_logs['timestamp'] = pd.to_datetime(raw_logs['timestamp.$date'])
raw_logs.drop(['timestamp.$date', 'stored.$date', '_id.$oid', 'actor.objectType', 'object.objectType', 'object.extension'], inplace=True, axis=1)

raw_logs.head()

# %% [markdown]
# # Simplification des verbes et noms de colonnes

# %%
raw_logs.replace('https://www.cristal.univ-lille.fr/verbs/Session.Start', 'Session.start', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/verbs/Session.End', 'Session.end', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/verbs/File.Open', 'File.Open', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/verbs/File.Save', 'File.Save', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/verbs/Run.Program', 'Run.Program', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/verbs/Run.Command', 'Run.Command', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/verbs/Run.test', 'Run.Test', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/verbs/Docstring.Generate', 'Docstring.Generate', inplace=True)

raw_logs.replace('https://www.cristal.univ-lille.fr/objects/Session', 'Session', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/objects/Plugin/L1Test', 'L1Test', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/objects/Program', 'Program', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/objects/Command', 'Command', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/objects/Test', 'Test', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/objects/File', 'File', inplace=True)
raw_logs.replace('https://www.cristal.univ-lille.fr/objects/DocString', 'DocString', inplace=True)

raw_logs.replace('https://www.cristal.univ-lille.fr/users/', '', regex=True, inplace=True)

raw_logs.rename(columns={'actor.openid': 'actor', 'verb.id': 'verb', 'object.id': 'object',
    'context.extension.https://www.cristal.univ-lille.fr/objects/Session/ID': 'session.id',
    'context.extension.https://www.cristal.univ-lille.fr/objects/Plugin': 'plugin',
    'object.extension.https://www.cristal.univ-lille.fr/objects/Command/CommandRan': 'commandRan',
    'object.extension.https://www.cristal.univ-lille.fr/objects/Program/CodeState': 'codeState',
    'result.extension.https://www.cristal.univ-lille.fr/objects/Command/stdin': 'stdin',
    'result.extension.https://www.cristal.univ-lille.fr/objects/Command/stdout' : 'stdout',
    'result.extension.https://www.cristal.univ-lille.fr/objects/Command/stderr': 'stderr',
    'object.extension.https://www.cristal.univ-lille.fr/objects/File/Filename': 'filename',
    'object.extension.https://www.cristal.univ-lille.fr/objects/File/CodeState': 'codestate',
    'object.extension.https://www.cristal.univ-lille.fr/objects/DocString/Function': 'function',
    'object.extension.https://www.cristal.univ-lille.fr/objects/Test/TestedExpression': 'testedExpression',
    'object.extension.https://www.cristal.univ-lille.fr/objects/Test/TestedLine': 'testedline',
    'object.extension.https://www.cristal.univ-lille.fr/objects/Test/TestedFunction': 'testedFunction',
    'result.extension.https://www.cristal.univ-lille.fr/objects/Test/expectedResult': 'expectedResult',
    'result.extension.https://www.cristal.univ-lille.fr/objects/Test/obtainedResult': 'obtainedResult'}, inplace=True)

raw_logs.head()

# %% [markdown]
# # Anonymisation

# %%
raw_logs['commandRan'].replace(r"^%cd ", "%cd anonymized", regex=True, inplace=True)

# %% [markdown]
# # Définition des valeurs par défaut

# %%
clean_logs = raw_logs.fillna("")
raw_logs.head()

# %% [markdown]
# # Sauvegarde du fichier nettoyé

# %%
clean_logs.to_csv(interim_data_dir + "traces_clean.csv")

# %% [markdown]
# # Identification des débuts et fin de sessions

# %%
print("Nombre d'ouvertures de session " + str(clean_logs.loc[clean_logs.loc[:, 'verb'] == 'Session.start']['verb'].size))
print("Nombre de fermetures de session " + str(clean_logs.loc[clean_logs.loc[:, 'verb'] == 'Session.end']['verb'].size))

# %% [markdown]
# # Nombre d'enregistrements par utilisateur

# %%
print("Nombre d'utilisateurs", clean_logs['actor'].nunique())

# %%
print("Nombre de sessions par utilisateur")
max_sessions = clean_logs.groupby('actor')['session.id'].nunique().max()
mean_sessions = clean_logs.groupby('actor')['session.id'].nunique().mean()
total_sessions = clean_logs.groupby('actor')['session.id'].nunique().sum()

print(f"Nombre de sessions {total_sessions}, nombre moyen {mean_sessions:.2f} et maximum {max_sessions}")

# %% [markdown]
# # Calcul de la durée des sessions

# %%
session_items = ['Session.start', 'Session.end']
session_markers = clean_logs.loc[clean_logs['verb'].isin(session_items)].groupby(['actor', 'session.id'])
clean_logs['session.duration'] = session_markers['timestamp'].diff()
clean_logs['session.duration'].describe()

# %% [markdown]
# # Sélection des identifiants de sessions courtes (<10 minutes)

# %%
short_sessions = clean_logs.loc[clean_logs['session.duration'] < '00:10:00']['session.id']
short_sessions

# %%
def session_information(id, logs):
    actions = logs.loc[logs['session.id'] == id]
    print(f"Nombre d'actions de la session : {actions.shape[0]}")
    verbs = ''
    for  r in actions.itertuples():
        verbs = verbs + r[3] + ","
    print(verbs)

session_information('139918830574976', clean_logs)


# %% [markdown]
# # Identification des verbes utilisés

# %%
clean_logs['verb'].unique()

# %%
clean_logs['verb'].value_counts()

# %% [markdown]
# # Calcul du temps entre les actions

# %%
sessions = clean_logs.groupby(['actor', 'session.id'])
clean_logs['duration'] = sessions['timestamp'].diff()
clean_logs

# %%
clean_logs['duration'].describe()

# %%
sessions['verb'].apply(list)

# %% [markdown]
# # Etude d'une session

# %%
study = clean_logs.loc[clean_logs['session.id'] == '139717750653760']

# %%
study[['verb', 'duration']].apply(list)

# %%



