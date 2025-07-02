## 📁 Project Structure

```
project-root/
├── data/ 
│   ├── interim/ 
│      ├── traces250102_clean.csv        # Uncleaned data
│      ├── acteur_nettoyage_2425.csv     # Cleaned column 'actor' and 'binome' of traces250102_clean
│      ├── phase1_nettoyage_fichiere.csv # Cleaned column 'filename_infere' phase 1
│      ├── phase2_nettoyage_fichiere.csv # Cleaned column 'filename_infere' phase 2
│      ├── Final_nettoyage_2425.csv      # Final cleaning, adding columns TP, Type_TP
│      ├── anonymized_data.csv           # Anonymized data
│      ├── seance_vide.csv               # Traces of the seance = '' (Removed from original df)
│      ├── too_short_sessions.csv        # Traces with too short lengths (Removed from original df)
│
│   ├── processed/
│      ├── anonymized_actor.csv          # Name of actors with their hash id
│
├── notebooks/             
│   ├── 1.Cleaning_actors.py           # Cleaning actor column
│   ├── 2.Cleaning_filename_phase1.py  # Cleaning filename_infere by verb
│   ├── 3.Cleaning_filename_phase2.py  # Cleaning filename_infere by sessions 
│   ├── 4.Anonymizing.py               # Anonymizing   
│   ├── 5.Analyze.py                   # Analyzing data             
│   
├── src/                     
│   ├── data/                # Gloabl data
│   │    ├── cleaning.py     # Thomas code , can be deleted later
│   │    ├── constants.py    
│   │    ├── variable_constant.py
│   │    
│   ├── features/            # Feature engineering
│       ├── utils.py               # Thomas code , can be deleted later
│       ├── data_anonymization.py  # Functions to anonymize
│       ├── data_cleaning.py       # Functions to cleaning actors or filename_infere
│       ├── data_testing.py        # Functions to test the result
│       ├── io_utils.py            # Functions to read and write csv files 
│
│        
└── README.md                # Project documentation
```

## The command for syncronation
jupytext --sync *.ipynb
jupytext --to notebook 1.Preparation.py

jupytext --to py my_notebook.ipynb (first time)
jupytext --set-formats ipynb,py:percent 2.Cleaning_filename_phase1.ipynb

## Three main thing for stage
- How to check if the student did the Test and continue the Test
- When the Test is red what did they do, did they continue or they did nothing
- Seperate the student that are very debutan and the student that already did some courses in programmation

## Explainations:

- How does the similarity work in utils_module/data_cleaning.py : find_similarity()
    
    1. Find Longest Match:

        Identify the longest contiguous matching subsequence between the two input strings.
        This match must be in the same order in both strings, but not necessarily at the same position.

    2. Split and Recurse:

        After finding a match, split both strings into three parts:The part before the match, The match itself, The part after the match
        Repeat the process recursively on the "before" and "after" parts to find more matching subsequences.

    3. Collect Matches:

        All matching blocks are collected in a list of Match(a, b, size) tuples, indicating matching substrings starting at index a in the first string and b in the second string, with a given length size. These blocks are non-overlapping and ordered.

    4. Compute Similarity Ratio:

        The final similarity score is calculated with the formula:
        similarity ratio = 2 * (total matching characters) / length of string A + length of string B

- How and where dataframe traces250102_clean is sorted ?
    Before the cleaning process, there is another process which is called **process_raw_data** and it gets the data from server in json format and transforms it into a dataframe and then it sorts them in this order : first in order of alphabet of the actor column, second in order of the session.id column in descending order, and third in order of the tempstamp.date column. This process produce the data **traces250102_clean** which is the input data of **1.Cleaning_actors.ipynb**. This **process_raw_data** is done by Thomas and it is in **cleaning.py** module.


​







