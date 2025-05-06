# Folder 
This folder is about changing the old folder to the new version.

## Changes
- src\data\anonymizing.py
    - optimized_anonymize_dataframe -> use **min** to ensure we cover all the indices.
    - anonymize_dataframe -> Remove the nested loop and use the vectorized operations. 

- src\features\utils.py
    - give_list_actors -> for loop and "+=" is replaced by **itertools.chain**

- notebooks\nettoyage_actuer_2425.ipynb
    - Problems with importing **from src.data import cleaning**, **from src.features import utils**, that is why it didn't work.
    - **cleaning_identifiants()**, **test_on_dataframe()** : it is better to have two functions, one for cleaning the data and one to test the cleaning; instead of having the code without a function.
