## 📁 Project Structure

```
project-root/
├── data/ 
│   ├── interim/ 
│      ├── traces250102_clean.csv       
│      ├── acteurs_corriges_2425.csv    # cleaned column 'actor' and 'binome' of traces250102_clean.csv
│      ├── phase1_nettoyage_fichiere.csv # cleaned column 'filename_infere' phase 1
│      ├── phase2_nettoyage_fichiere.csv # cleaned column 'filename_infere' phase 2
│
├── notebooks/             # Jupyter notebooks
│   ├── 1.Preparation.py   # Cleaning data
│   ├── 2.Analyze.ipynb    # Analyzing data          
│   
├── src/                     # Thomas's code (they can get removed, except constants.py and variable_constant.py)
│   ├── data/                # Data loading/cleaning functions
│   │    ├── anonymizing.py
│   │    ├── cleaning.py
│   │    ├── constants.py
│   │    ├── variable_constant.py
│   │    
│   ├── features/            # Feature engineering
│       ├── utils.py   
│      
│
├── utils_module/              # Python modules
│   ├── data_anonymization.py  # Functions to anonymize
│   ├── data_cleaning.py       # Functions to cleaning actors or filename_infere
│   ├── data_testing.py        # Functions to test the result
│   ├── io_utils.py            # Functions to read and write csv files 
│
│        
└── README.md                # Project documentation
```

## The command for syncronation
jupytext --sync *.ipynb
jupytext --to notebook 1.Preparation.py


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

​
 



