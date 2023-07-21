# Documentation Technique

## Description générale :

Le plugin collecte les évènements générés par Thonny lors des diverses intéractions de l'utilisateur avec l'éditeur, puis n'en séléctionne que les données intéréssantes et les reformates de manière à leur donner du sens, puis les envois à un serveur pour les stocker.


### Architecture
Il y a 5 composants principaux pour ce plugin.

* La classe principale, <code>mainApp.py</code> qui va récupérer les données que l'on souhaite, les nettoyer et effectuer des traitements préalables nécessaire.  
* La classe <code>formatData</code> (dans le package <code>processing</code>), qui va donner du sens aux données en rassemblant différentes intéractions en un même évènement et renommer les informations dans le dictionnaire. Ceci va aboutir à un formatage général et neutre, d'ou les données pourront être converties dans de nouveaux formats selon les besoins.  
* Le package <code>formats</code>, qui va contenir les différents traitements de formatage pour les formats voulus, actuellement il ne contient que le format xAPI.  
* Le package <code>communication</code>, qui contient les fonctions pour envoyer les données au serveur.  
* Le package <code>configuration</code>, qui contient les fonctions permettant d'obtenir et de changer les configurations du plugin, ainsi que la classe permettant d'ajouter une page de configuration dans la fenêtre d'options de Thonny.  

### Fichier de configuration

Le fichier de configuration contenant les valeurs des options (cf le panneau dédié dans le menu Tools>Options) n'est pas propre au plugin, c'est celui de Thonny. Il s'appelle <code>configuration.ini</code> et est dans le répertoire <code>.thonny</code> à la racine de l'environnement virtuel.

Extrait de ce fichier avec des valeurs d'options: 
```
[loggingPlugin]
send_logs = True
first_run = True
log_in_console = True
store_logs = True
server_address = http://127.0.0.1:8000
local_path = /tmp/plugin-log/venv_log/.thonny/LoggingPlugin/
```

## Collecte actuelle 

### Évènements et informations captées par le plugin :

Évènements de Thonny : 


| Nom 'sequence'     | Nom des informations récupérées                                  |
|--------------------|------------------------------------------------------------------|
|Save ; SaveAs ; Open|sequence ; editor ; text_widget ; filename                        |
|ShellInput         |sequence ; input_text ; tags                                      |
|TextInsert          |sequence ; index ; text ; text_widget ; text_widget_context ; tags|
|shellCommand        | sequence ; command_text ; tags                                   |


Évènements ne provenant pas de Thonny :


| Nom 'sequence'        | Description               | Nom des informations récupérées    |
|-----------------------|---------------------------|------------------------------------|
| l1Tests               | Plugin de Test            | sequence ; filename ; tested_line ; expected_result ; obtained_result ; exception ; name ; lineno ; selected |
| l1Tests.DocGenerator  | Générateur de docstring   | name |



### Premier formatage général 


Le but de ce formatage est d'avoir toutes les informations pour chaque évènement, avec un nommage adapté et facilement convertissable dans d'autre formats de données.


* Pour tout les événements on a :

    | Nom       | Type  | Description           |
    |-----------|-------|-----------------------|
    | eventID   | int   | l'id de l'événement
    | eventType | str   | le nom de l'événement
    | timestamp | datetime.datetime python | l'horodatage
    | sessionID | int   | l'id de la session
    | userID    | str   | hash du nom de session


* session 

    | Nom       | Type  | Description           |
    |-----------|-------|-----------------------|
    | status    | bool  | True si début, False sinon |



* open & save

    | Nom       | Type  | Description           |
    |-----------|-------|-----------------------|
    | filename  | str   | nom du fichier
    | codestate | str   | code du fichier


* run_command & run program

    | Nom       | Type  | Description           |
    |-----------|-------|-----------------------|
    | stdin     | str   | l'entrée standard     |
    | stdout    | str   | la sortie standard    |
    | stderr    | str   | la sortie erreur      |
    | status    | bool  | True si la commande / l'exécution s'est déroulée sans erreurs, false sinon    |
    | command   | str   | commande lancée       |


* run_program

    | Nom       | Type  | Description           |
    |-----------|-------|-----------------------|
    | codestate | str   | code du fichier       |



Pour tout les autres évènements dont on n'a pas défini de comportement spécifique dans cette classe, on garde toutes les informations capturées.


### Format xAPI


Pour chaque type d'évènement ci-dessus, un formatage xAPI a été réalisé.  

## Ajouter des événements / informations à la collecte


Le plugin ne capte que les évènements générés par Thonny. Pour ajouter à Thonny la génération d'évènement provenant d'un autre plugin, voir la partie ci-dessous   .

Pour chacune des étapes ci-dessous, j'ai pris l'exemple de l'ajout de la captation des données issues d'un plugin de test tiers.


### Ajouter la captation de l'évenement généré par Thonny 


Dans <code>pluggin/thonnycontrib/thonny-LoggingPlugin/mainApp.py</code> :    

On ajoute au dictionnaire le nom de 'sequence' en clé ainsi les informations à capturer en valeur.    
```python
self._inDict = {
            "ShellCommand" : {'sequence','command_text','tags'},
            "ShellInput" : {'sequence','input_text','tags'},
            "TextInsert" : {'sequence','index','text','text_widget','text_widget_context','tags'},

            "Save" : {'sequence','editor','text_widget','filename'},
            "Open" : {'sequence','editor','text_widget','filename'},
            "SaveAs" : {'sequence','editor','text_widget','filename'},

            "l1Tests" : {'sequence','filename','tested_line','expected_result','obtained_result','exception','name','lineno','selected'}
        }
```


### [OPTIONNEL] Ajouter des traitements préalables :


Dans <code>plugin/thonnycontrib/thonny-LoggingPlugin/mainApp.py</code> :  

Ajouter les traitements dans la méthode '_input_processing'  

```python
def _input_processing(self, data : dict, event : object) -> dict :
        [...]
        if data['sequence'] == 'l1Tests':
            if  'exception' in data or 'obtained_result' in data :
                data['status'] = False
            else :
                data['status'] = True 

            if not 'obtained_result' in data :
                if not 'exception' in data :
                    data['obtained_result'] = data['expected_result']
                else :
                    data['obtained_result'] = data['exception']

        if 'filename' in data :
            data['filename'] = self.hash_filename(data['filename'])
            
        return data
```


### [OPTIONNEL] Sélectionner les informations à garder / renommer dans le formatage général


Dans <code>plugin/thonnycontrib/thonny_LoggingPlugin/processing/formatData.py</code>  

Pour cet exemple, il n'y a pas besoin d'établir un formatage sur les données reçues  

```python
def init_event(self, data, id):
        [...]
        else:
            #Informations générales
            self.current['timestamp'] = data['time']
            self.current['eventID'] = id
            self.current['userID'] = self.userID
            self.current['sessionID'] = self.sessionID

            # Cas des runs commandes ou programme
            if data['sequence'] == 'ShellCommand':
                self.format_ShellComand(data)

            # Cas des ouvertures / sauvegardes / nouveau fichiers
            elif data['sequence'] in {'Open', 'Save', 'SaveAS'}:
                self.format_open_save(data)
            

            #Cas non référencés
            
            else :
                self.current['eventType'] = data['sequence']
                for el in data :
                    if el not in self.current and el not in {'sequence','tags'}:
                        self.current[el] = data[el]
                self.end_event()
````


### Convertir les données au format xAPI


Dans <code>plugin/thonnycontrib/thonny_LoggingPlugin/formats/xAPI_creation.py  </code>

Ajouter pour chaque objet différent, la convertion au format xAPI.  

```python
def create_result(data):
    [...]
    elif data['eventType'] == 'l1Tests' :

        result['extension'] = {
            OBJECTS_URI['test'] +'/expectedResult' : data['expected_result'],
            OBJECTS_URI['test'] +'/obtainedResult' : data['obtained_result'],
        }

    return result
```


## Ajouter la génération d'évènements d'un nouveau plugin Thonny

```python
from thonny import get_workbench

NOM_EVENT = "..."

#Cette fonction sert à obtenir l'objet principal de Thonny.
wb = get_workbench()

#Bind sert à lier un évènement généré à une fonction, mais créer aussi l'évènement NOM_EVENT, c'est pour cela qu'elle est utilisée ici.
wb.bind(NOM_EVENT,lambda x : 0 ,True)

#Cette fonction génére des évènements thonny, contenant le dictionnaire des couples clé-valeurs à transmettre
wb.event_generate(NOM_EVENT,None,**DICT_VALEURS_EVENEMENT)

```

## Conformité RGPD

Vu avec le DPO de CRIStAL, Olivier Auverlot.

### Acceptation de la collecte des données

Au démarrage de Thonny, ouverture d'une fenêtre modale popup:
- mention légale courte
- mention du fait de ne pas entrer de données perso
- mention du fait qu'on peut revenir sur son choix
- bouton 'oui', bouton 'non' actif par défaut (les touches espace et echap ont l'effet de déclencher le bouton actif)

Lien vers un fichier de présentation depuis Tools>LoggingPlugin.

### Hachage de l'identificateur de l'utilisateur

Corentin a utilisé hashlib.sha224. Cette fonction prend en paramètre
un byte et renvoie un objet qu'on peut convertir en hexa, sous la
forme d'une chaîne de caractères. Cette chaîne est de longueur 56
(systématiquement, pour tout byte en paramètre). Corentin ne garde que
les 15 premiers caractères. Dc les login prenom.nom.etu sont stockés
ds une chaîne de 15 caractères (qui représente un début d'entier
dc).

-> à passer sur 56 caractères ?

Dans <code>formatData.py</code>:
```python
    def __init__(self, logger) -> None:
        self.logger = logger
        self.on_progress = False
        self.current = dict()
        self.userID = logger_utils.hash_identifiant()
        self.sessionID = id(get_workbench())
```

### Identifiant de session

Il est crée à partir de l'adresse de l'objet représentant le workbench
(cf ci-dessus).

### Hachage du nom des fichiers, qui peuvent contenir le nom de l'étudiant

Dans <code>MainApp.py</code> :
```python
    def _input_processing(self, data : dict, event : object) -> dict :
    [...]
        if 'filename' in data :
            data['filename'] = utils.hash_filename(data['filename'])
            
        return data
```

Dans les commandes générées par Thonny:

Dans <code>formatData.py</code>:

Dans le cas d'un Run Program :

```python
    def format_ShellComand(self,data):
    [...]
            if data['command_text'][:4] == '%Run':
            self.current['eventType'] = 'Run_program'
            # anonymisation du contenu de l'éditeur
            self.current['codestate'] = logger_utils.appose_masque(data['editorContent'])
            # le nom du fichier apparaît ds la commande -> anonymisation
            self.current['command'] = logger_utils.remplace_nom_fichier_ds_commande_Run_program(data['command_text'])
```

Dans le cas d'un Run Command :

```python
    def format_ShellComand(self,data):
    [...]
	else:
            self.current['eventType'] = 'Run_command'
            # cas du %cd
            # sans doute evt généré si Thonny lancé depuis une icône
            # le nom du fichier apparaît dedans
            if data['command_text'].startswith("%cd"):
                self.current['command'] = logger_utils.remplace_nom_repertoire_ds_commande_cd(data['command_text'])
            elif data['command_text'].startswith("%Debug"):
                self.current['command'] = logger_utils.remplace_nom_fichier_ds_commande_Debug(data['command_text'])
```

### Dans le contenu de l'éditeur/commandes, masquage des données sensibles

Masquage des :
- commentaires
- suite de chiffre de longueur >= 8 (nip, numéro carte bancaire)
- numéro de téléphone
- identifiant type prenom.nom.etu
- emails

#### Dans le contenu de l'éditeur

Dans <code>formatData.py</code>:

Dans le cas d'un Run Program :

```python
    def format_ShellComand(self,data):
    [...]
            if data['command_text'][:4] == '%Run':
            self.current['eventType'] = 'Run_program'
            # anonymisation du contenu de l'éditeur
            self.current['codestate'] = logger_utils.appose_masque(data['editorContent'])
            # le nom du fichier apparaît ds la commande -> anonymisation
            self.current['command'] = logger_utils.remplace_nom_fichier_ds_commande_Run_program(data['command_text'])

```

Dans le cas d'un Open/Save:

```python
    def format_open_save(self,data):
    [...]
        # anonymisation du contenu de l'éditeur
        if data['editorContent'] != None:
            self.current['codestate'] = logger_utils.appose_masque(data['editorContent'])
```

#### Dans le contenu de stderr, stdin, stdout

Dans <code>processing/formatData.py</code>:

```python
    def end_event(self):
    [...]
        # masquage des éventuelles données sensibles
        if 'stdout' in self.current:
            self.current['stdout'] = logger_utils.appose_masque(self.current['stdout'])
        if 'stderr' in self.current:
            self.current['stderr'] = logger_utils.appose_masque(self.current['stderr'])
        if 'stdin' in self.current:
            self.current['stdin'] = logger_utils.appose_masque(self.current['stdin'])
  
        self.logger.receive_formatted_logs(self.current)
        self.current = dict()
```

#### Dans le contenu des commandes entrées par l'utilisateur dans l'interpréteur

```python
    def format_ShellComand(self,data):
    	[...]
     	  elif data['command_text'][0] != '%':
                # interaction avec l'interpréteur Python ds la console
                # on cache ce qui gène ds la commande
                self.current['command'] = logger_utils.appose_masque(data['command_text'])
```




