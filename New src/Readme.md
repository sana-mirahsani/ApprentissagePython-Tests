# Folder 
This folder is about changing the old folder to the new version. so the structure is the same but the content is clearer and faster

## 📁 Project Structure

```
project-root/
├── data/ 
│   ├── interim/ 
│      ├── traces250102_clean.csv       
│      ├── acteurs_corriges_2425.csv    # cleaned 'actor' column of traces250102_clean.csv
│ 
├── notebooks/                          # Jupyter notebooks
│   ├── nettoyage_acteurs_2425.py       # original code but with some errors
│   ├── nettoyage_acteurs_2425.ipynb    # my code            
│   
├── src/                     # Source code
│   ├── data/                # Data loading/cleaning functions
│   │    ├── anonymizing.py
│   │    ├── cleaning.py
│   │    ├── constants.py
│   │    ├── variable_constant.py
│   │    
│   ├── features/            # Feature engineering
│       ├── utils.py   
│      
└── README.md                # Project documentation
```


## Changes
- src\data\anonymizing.py
    - optimized_anonymize_dataframe -> use **min** to ensure we cover all the indices.
    - anonymize_dataframe -> Remove the nested loop and use the vectorized operations. 

- src\features\utils.py
    - give_list_actors -> for loop and "+=" is replaced by **itertools.chain**

- notebooks\nettoyage_actuer_2425.ipynb
    - Problems with importing **from src.data import cleaning**, **from src.features import utils**, that is why it didn't work.
    - **clean_actor()**, **test_on_dataframe ()** : it is better to have two functions, one for cleaning the data and one to test the cleaning; instead of having the code without a function.
     
