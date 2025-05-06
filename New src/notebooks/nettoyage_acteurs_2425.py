# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: venv_jupyter
#     language: python
#     name: venv_jupyter
# ---

# # Regarder les identifiants avant anonymisation

# import à recopier sans comprendre
import sys
sys.path.append('../') # ces deux lignes permettent au notebook de trouver le chemin jusqu'au code source contenu dans 'src'
sys.path.append('../src/') # Yvan dit que c'est absurde, mais sans ça ne marche pas
from src import * # on importe ce qui se trouve dans 'src'
import pandas as pd
from src import script_initialisation, clean_corrupted_data
from src.data import cleaning
get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

df = load_clean_data('traces250102_clean.csv')

df

df.columns

# + jp-MarkdownHeadingCollapsed=true
actors = give_list_actors(df)
number_of_student = utils.give_number_of_actors(df)
print("-> Nombre total d'étudiants tous participants confondus en 2425: " + str(number_of_student))
# -

# ## Recherche des identifiants louches, pas de la forme prenom.nom.etu

import re
regexp_identifiant = r'[^.]+\.[^.]+.etu$'
pattern_identifiant = re.compile(regexp_identifiant)

identifiants_louches = [id for id in actors if not pattern_identifiant.match(id)]
print(f'{len(identifiants_louches)} identifiants louches')
identifiants_louches

# On trouve surtout des adresses mail en @univ-lille.fr, une adresse tronquée en .etu@, 'nebut' (!!!) 'luc' et 2 jokers MI1304 et MI1301.

# On regarde si les adresse mail correspondent à des identifiants classiques :

adresses_mail = [identifiant for identifiant in identifiants_louches if '@' in identifiant]
adresses_mail

print(f'-> {len(adresses_mail)} adresses mail ou assimilées')

# ## Recherche des adresses qui correspondent à un identifiant classique dans les traces

# Recherche des identifiants classique :

identifiants = [id for id in actors if pattern_identifiant.match(id)] 

# Recherche des adresses mail pour lesquelles on trouve dans les traces un identifiant classique :

adresses_mail_correspondant_identifiant = [adresse for adresse in adresses_mail if adresse.split('@')[0] in identifiants]
adresses_mail_correspondant_identifiant

print(f'-> {len(adresses_mail_correspondant_identifiant)} adresses mail avec un identifiant correspondant')

# Il y a une adresse louche qui ne colle pas et 19 qui collent -> faire le remplacement, cf fin de notebook

# ## Traitement de l'adresse louche et de 'nebut'

# ### Recherche de l'adresse louche

adresses_mail_louche = [adresse for adresse in adresses_mail if adresse.split('@')[0] not in identifiants]
adresses_mail_louche

# L'adresse est bien correcte (vérifié dans Mon Dossier Étudiant)

[actor for actor in actors if 'younes' in actor]

# On regarde combien de traces sont concernées :

df[df['actor'].str.contains('anis.younes.etu@univ-lille.fr')]

print(f'-> {len(df[df['actor'].str.contains('anis.younes.etu@univ-lille.fr')])} traces sont concernées')

df

# On peut virer ces 2 traces, juste une session vide.

index_a_virer = df[df['actor'].str.contains('anis.younes.etu@univ-lille.fr')].index

df_sans_adresse_louche = df.copy()
df_sans_adresse_louche = df_sans_adresse_louche.drop(index_a_virer)
df_sans_adresse_louche.reset_index(drop=True, inplace=True)

reste = len(df_sans_adresse_louche[df_sans_adresse_louche['actor'].str.contains('anis.younes.etu@univ-lille.fr')])
print(f'-> Il reste {reste} traces avec adresse louche.')

df

# ### Supprimer les traces de 'nebut'

# Je ne me rappelle plus avec voir ces tests, mais les traces utilisent bien des fichiers de mon compte, je les vire.

df_sans_nebut = df_sans_adresse_louche.copy()
len(df_sans_nebut[df_sans_nebut['actor'].str.contains('nebut')])

index_a_virer = df_sans_nebut[df_sans_nebut['actor'].str.contains('nebut')].index
index_a_virer
print(f'{len(index_a_virer)} index à virer')

df_sans_nebut = df_sans_nebut.drop(index_a_virer)
df_sans_nebut.reset_index(drop=True, inplace=True)
reste = len(df_sans_nebut[df_sans_nebut['actor'].str.contains('nebut')])
print(f'-> Il reste {reste} traces avec nebut.')

df

# ## Traitement identifiant 'luc'

df_sans_luc = df_sans_nebut.copy()
regexp_luc = r'^luc/.*|.*/luc$'
df_sans_luc[df_sans_luc['actor'].str.match(regexp_luc)]

df_sans_luc.iloc[151849]['P_codeState']

# Un tic-tac-toe en septembre -> virer luc

df_sans_luc['actor'] = df_sans_luc['actor'].replace('kilian.graye.etu/luc', 'kilian.graye.etu/')

reste = len(df_sans_luc[df_sans_luc['actor'].str.match(regexp_luc)])
print(f'-> Il reste {reste} traces avec luc.')

# ## Traitement jokers  'MI1301' et 'MI1304'

# ### MI1301

# MI1301 est mariama-sere.sylla.etu d'après le Moodle PROG. 

df_sans_joker = df_sans_luc.copy()
df_MI1301 = df[df['actor'].str.contains('MI1301')]
df_MI1301

print(f'{len(df_MI1301)} traces concernées')

# Ça fait trop pour les virer, regarder des dates :

df['timestamp.$date'].iloc[145134]

df

array_date = df[df['actor'].str.contains('MI1301')]['timestamp.$date'].map(lambda date: str(date.year) + str(date.month) + str(date.day)).unique().copy()
liste_date = list(array_date)
sorted(liste_date)

# Dates en septembre et novembre, bizarre.

df

print(f'{len(df[df['actor'].str.contains('mariama-sere.sylla.etu')])} traces avec le login correct')

# 445 traces en binome en septembre puis novembre mais, bizarre, aucune autre trace à son login, ds Mon Dossier Etudiant a tout de même 
# des notes de TP et DS de PROG, mais inscrite en MIASHS aussi ? Je remplace par son login.

df_sans_joker['actor'] = df_sans_joker['actor'].replace('kade-bhoye.wann.etu/MI1301', 'kade-bhoye.wann.etu/mariama-sere.sylla.etu')
print(f'-> il reste {len(df_sans_joker[df_sans_joker['actor'].str.contains('MI1301')])} traces avec MI1301')

# Regarder avec qui a bossé la binôme :

df[df['actor'].str.contains('kade-bhoye.wann.etu')]['actor'].unique()

# On retrouve les 2 jokers. Si ça se trouve les 2 jokers sont la même personne.

# Dates auxquelles la binôme a bossé seule :

array_date = df[df['actor'] == 'kade-bhoye.wann.etu/']['timestamp.$date'].map(lambda date: str(date.year) + str(date.month) + str(date.day)).unique()
liste_date = list(array_date)
sorted(liste_date)

# Seulement 2 dates, dates qui sont aussi ds les dates avec le joker : elles devaient probablement bosser ensemble.

# ### MI1304

df[df['actor'].str.contains('MI1304')]

len(df[df['actor'].str.contains('MI1304')])

df['P_codeState'].iloc[145185]

# Pour MI1304 : 52 traces le 5 décembre sur un jeu de puissance4, avec la même binôme. On va supposer que
# c'est la même que MI1301.

df_sans_joker['actor'] = df_sans_joker['actor'].replace('kade-bhoye.wann.etu/MI1304', 'kade-bhoye.wann.etu/mariama-sere.sylla.etu')

reste = len(df_sans_joker[df_sans_joker['actor'].str.contains('MI1304')])
print(f'-> Il reste {reste} traces avec MI1304.')

# Traces dans lesquelles la binôme était seule :

df[df['actor'].str.match(r'kade-bhoye.wann.etu/$')]

# TODO je ne suis plus trop d'accord pour rajouter la binôme.
# On rajoute l'ancienne joker :

df_sans_joker['actor'] = df_sans_joker['actor'].str.replace(r'kade-bhoye.wann.etu/$','kade-bhoye.wann.etu/mariama-sere.sylla.etu', regex=True)

reste = len(df_sans_joker[df_sans_joker['actor'].str.match(r'kade-bhoye.wann.etu/$')])
print(f'-> Il reste {reste} traces avec binome seule.')

# Vérification

ancien = len(df[df['actor'].str.contains('kade-bhoye.wann.etu')])
print(f"-> {ancien} traces binome dans l'ancien df")

nouveau = len(df_sans_joker[df_sans_joker['actor'].str.contains('kade-bhoye.wann.etu')])
print(f"-> {ancien} traces binome dans le nouveau df")

# ## Remplacement des adresses mail par l'identifiant associé

# Pour les actors de adresses_mail_correspondant_identifiant, remplacer par l'identifiant qui précède le @.
# Utilisation du DataFrame.str.replace de pandas, qui appelle re.sub (écrit en pas très gros ds la doc).

df_sans_mail = df_sans_joker.copy()


def repl_adresse(matchobj:re.Match) -> str:
    '''Renvoie la chaîne qui doit remplacer la partie matchée par le paramètre, ici l'identifiant
    qui précède le caractère '@'
    '''
    return matchobj[0].split('@')[0]


# Attention DataFrame.replace ne fait pas ce qu'on veut : remplace le champ masqué par une chaîne fixe.
# DataFrame.str.replace fait ce qu'on veut si on passe une fonction de remplacement (peut-être que regex passe à True par défaut dans
# ce cas, en tout cas la doc dit que regexp ne peut pas être à False si on utilise une telle fonction). Cette fonction de remplacement
# calcule la chaîne qui vient remplacer la zone matchée en fonction de cette zone.

df_sans_mail['actor'] = df_sans_mail['actor'].str.replace(r'.*@.*$', repl_adresse, regex=True)

len(df[df['actor'].str.contains('abaly.oura.etu@univ-lille.fr')])

len(df_sans_mail[df_sans_mail['actor'].str.contains('abaly.oura.etu@univ-lille.fr')])

len(df[df['actor'].str.contains('abaly.oura.etu')])

len(df_sans_mail[df_sans_mail['actor'].str.contains('abaly.oura.etu')])

# On n'a plus d'adresse mail pour cet identifiant, et le nb de traces reste le même. Deuxième test :

len(df[df['actor'].str.contains('mohamed-el-amine.samahri.etu@univ-lille.fr')])

len(df_sans_mail[df_sans_mail['actor'].str.contains('mohamed-el-amine.samahri.etu@univ-lille.fr')])

len(df[df['actor'].str.contains('mohamed-el-amine.samahri.etu')])

len(df_sans_mail[df_sans_mail['actor'].str.contains('mohamed-el-amine.samahri.etu')])

# Comme dirait tout étudiant de ML, ça a l'air bon !

# ## Vérification

actors = give_list_actors(df_sans_mail)

identifiants_louches = [id for id in actors if not pattern_identifiant.match(id)]
identifiants_louches

print(f'-> {len(actors)} étudiants tous participants confondus en 2425')

utils.give_number_of_actors(df_sans_mail)

# On avait 24 identifiants louches, on a viré 'nebut', 'luc', 19 adresses mail, et on a fusionné 2 jokers en un nouvel identifiant.
# On a dc supprimé 23 identifiants, 305 + 23 = 328. Ce qui est bien le nombre d'identifiants initial.

from src.data.constants import INTERIM_DATA_DIR

df_sans_mail.to_csv(INTERIM_DATA_DIR + "acteurs_corriges.csv")

#

df_sans_mail



