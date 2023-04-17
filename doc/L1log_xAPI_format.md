# Format xAPI :

Présentation du format adopté pour le stockage des données.

## Actions intéréssantes identifiées:

Voici les informations que l'on veut récupérer:  

* Executions du code réussi
	* Fichier et ses métadonnées relatives
	* inputs
	* Sorties programme
* Execution non aboutie
	* Fichier et ses métadonnées relatives
	* inputs
	* Messages d'erreurs
* Sauvegardes
	* Fichier et ses métadonnées relatives
* Ouvertures de fichier
	* Fichier et ses métadonnées relatives
* Commandes entrées
	* Entrées
	* Sorties
* Début de session
* Fin de session
	
## Traduction en actor-verb-object

Pour chaque objets json 'statement', le format xAPI autorise les extensions sous la forme d'un objet extension avec un couple clé/valeur dont la clé est une URI.  
Une URI n'est pas nécessairement resolvable 

```json
	extension{
		"http://URI_UNIQUE" : "Valeur",
		"http://URI_UNIQUE" : "Valeur 2"
	}
```

Pour chaque objet statement, en plus des attributs 'timestamp' et 'stored' pour les horodatage, et de l'uuid, nous aurons les objets json suivant :  
</br>

		
### Objet Actor
</br>
openid: ID, au format uuid 

objectType: str, "Agent" est le seul utilisé dans cet exemple  
</br> 

### Objet Verb	
</br>		

Verbes 			| Sens dans notre application			|Catégorie d'objet optionelle à ajouter
--------------	|------------------------------------	|------------
Session.Start	| A commencé une session				| Context	
Session.End		| A terminé une session					| Context
File.Open		| A ouvert un fichier existant/vide		| Context
File.Save		| A sauvegardé un fichier 				| Context
Submit			| A rentré une commande dans le shell	| Context, Result
Run.Program		| A lancé le programme					| Context, Result
Run.test		| A lancer un test avec le plugin de Test| Context, Result
Docstring.Generate| A générer un modèle de docstring via le plugin de Test | Context

</br>
Chaque verbe sera un objet avec les attributs suivant :

id : str , l'URI

</br>

### Object
</br>
objectType : str, "Activity" est un type défini par xAPI, le seul que l'on utilisera

id: str, un IRI  

Catégories d'objets et leur propriétés étendues :   
* File
	* Filename
	* Codestate
* Command
	* CommandRan
* Session
* Test
	* Filename
	* TestedExpression
	* TestedLine
	* TestedFunction
* Program
	* CommandRan
	* CodeState
* DoctestGenerate
</br>

### Objet Result
	
</br>
sucess : bool(true | false), si l'éxécution/la commande/le test a produit une erreur 

extension: {   
	"ProgramInput" : str, les inputs demandés par le programme (fonction input() de python)   
	"ProgramOutput" : str, la sortie standard du programme  
	"ProgramErrorOutput" : str, la sortie erreur complète  
}

</br>

### Objet Context

</br>
Pour lier l'événement à la session:
extension:{
	SessionID
}
Si l'évènement est un SessionStart et que le plugin L1Test est détecté :
extension:{
	Plugin : Plugin/L1Test
}


</br> 
	
	
## Exemples de statements :


L'utilisateur f5b815324ccaf24 a démarré une nouvelle session
```json
{
    "timestamp": "2022-07-21T11:08:56.879000",
    "stored": "2022-07-21T09:02:12.039000",
    "actor": {
      "openid": "https://www.cristal.univ-lille.fr/users/f5b815324ccaf24",
      "objectType": "Agent"
    },
    "verb": {
      "id": "https://www.cristal.univ-lille.fr/verbs/Session.Start"
    },
    "object": {
      "id": "https://www.cristal.univ-lille.fr/objects/Session",
      "objectType": "Activity",
      "extension": null
    },
    "result": null,
    "context": {
      "extension": {
        "https://www.cristal.univ-lille.fr/objects/Session/ID": "139938147466304"
      }
    }
  }
```

</br>

L'utilisateur f5b815324ccaf24 a éxecuté le program "helloworld.py"

```json
{
    "timestamp": "2022-07-21T11:10:00.646000",
    "stored": "2022-07-21T09:02:12.039000",
    "actor": {
      "openid": "https://www.cristal.univ-lille.fr/users/f5b815324ccaf24",
      "objectType": "Agent"
    },
    "verb": {
      "id": "https://www.cristal.univ-lille.fr/verbs/Run.Program"
    },
    "object": {
      "id": "https://www.cristal.univ-lille.fr/objects/Program",
      "objectType": "Activity",
      "extension": {
        "https://www.cristal.univ-lille.fr/objects/Command/CommandRan": "%Run helloworld.py\n",
        "https://www.cristal.univ-lille.fr/objects/Program/CodeState": "def helloworld():\n    return \"HelloWorld\"\n\n"
      }
    },
    "result": {
      "success": true,
      "extension": {
        "https://www.cristal.univ-lille.fr/objects/Command/stdin": "",
        "https://www.cristal.univ-lille.fr/objects/Command/stdout": "",
        "https://www.cristal.univ-lille.fr/objects/Command/stderr": ""
      }
    },
    "context": {
      "extension": {
        "https://www.cristal.univ-lille.fr/objects/Session/ID": "139938147466304"
      }
    }
  }
  ```

</br>

L'utilisateur f5b815324ccaf24 a lancé la commande "helloworld()" dans le shell

  ```json
  {
    "timestamp": "2022-07-21T11:10:08.233000",
    "stored": "2022-07-21T09:02:12.039000",
    "actor": {
      "openid": "https://www.cristal.univ-lille.fr/users/f5b815324ccaf24",
      "objectType": "Agent"
    },
    "verb": {
      "id": "https://www.cristal.univ-lille.fr/verbs/Run.Command"
    },
    "object": {
      "id": "https://www.cristal.univ-lille.fr/objects/Command",
      "objectType": "Activity",
      "extension": {
        "https://www.cristal.univ-lille.fr/objects/Command/CommandRan": "helloworld()\n"
      }
    },
    "result": {
      "success": true,
      "extension": {
        "https://www.cristal.univ-lille.fr/objects/Command/stdin": "",
        "https://www.cristal.univ-lille.fr/objects/Command/stdout": "'HelloWorld'\n",
        "https://www.cristal.univ-lille.fr/objects/Command/stderr": ""
      }
    },
    "context": {
      "extension": {
        "https://www.cristal.univ-lille.fr/objects/Session/ID": "139938147466304"
      }
    }
  }
```
## Toutes les URI utilisées :

```python
VERBS = {
    'Run_program'   : 'https://www.cristal.univ-lille.fr/verbs/Run.Program',
    'Run_command'   : 'https://www.cristal.univ-lille.fr/verbs/Run.Command',
    'Open'          : 'https://www.cristal.univ-lille.fr/verbs/File.Open',
    'Save'          : 'https://www.cristal.univ-lille.fr/verbs/File.Save',
    'Session_start' : 'https://www.cristal.univ-lille.fr/verbs/Session.Start',
    'Session_end'   : 'https://www.cristal.univ-lille.fr/verbs/Session.End',
    'l1Tests'       : 'https://www.cristal.univ-lille.fr/verbs/Run.test'
}

OBJECTS = {
    'file'    : 'https://www.cristal.univ-lille.fr/objects/File',
    'command' : 'https://www.cristal.univ-lille.fr/objects/Command',
    'session' : 'https://www.cristal.univ-lille.fr/objects/Session',
    'test'    : 'https://www.cristal.univ-lille.fr/objects/Test',
    'program' : 'https://www.cristal.univ-lille.fr/objects/Program',
    'plugin'  : 'https://www.cristal.univ-lille.fr/objects/Plugin',
}
```

## Eléments du format progsnap2

</br>
Voilà les colonnes que l'on aurait utilisé avec le format progsnap2

```python
csvMainTable {
            'EventID',              #Mandatory
            'EventType',            #Mandatory
            'SubjectID',            #Mandatory
            'ToolInstance',         #Mandatory
            'CodeStateID',          #Mandatory
            'ClientTimeStamp',      #Very Recommanded
            'ServerTimeStamp',      #Very Recommanded
            'SessionID',            #Required by EventType 'Session.start' && 'Session.end      
            'CodeStateSection',     #Required by EventType 'File.*'   
            'EditType',             #Required by EventType 'File.Edit'
            'ExecutionID',          #Required by EventType 'Run.Program'
            'ExecutionResult',      #Required by EventType 'Run.Program'
            'ProgramInput',         #Required by EventType 'Run.Program'
            'ProgramOutput',        #Required by EventType 'Run.Program'
            'ProgramErrorOutput',   #Required by EventType 'Run.Program'
        }
```

J'ai essayé de garder un maximum les noms du format progsnap2 sans dupliquer les informations dans le format xAPI.
