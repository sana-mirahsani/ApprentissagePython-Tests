# Folder 
This folder is about changing the old folder to the new version.

## Changes
- src\data\anonymizing.py
    - optimized_anonymize_dataframe -> use **min** to ensure we cover all the indices.
    - anonymize_dataframe -> Remove the nested loop and use the vectorized operations. 

- src\features\utils.py
    - give_list_actors -> for loop and "+=" is replaced by **itertools.chain**
