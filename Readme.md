## What is this project about?
We want to clean the data of student of the first year in informatique using Thonny IDE, Simply, to see how many of them learn the subjects by analyzing their data.


## What is the project Structure?

```
project-root/
├── data/ 
│   ├── interim/ 
│   │  ├── traces250102_clean.csv        # Uncleaned data
│   │  ├── acteur_nettoyage_2425.csv     # Cleaned column 'actor' and 'binome' of traces250102_clean
│   │  ├── phase1_nettoyage_fichiere.csv # Cleaned column 'filename_infere' phase 1
│   │  ├── phase2_nettoyage_fichiere.csv # Cleaned column 'filename_infere' phase 2
│   │  ├── phase3_nettoyage_fichiere.csv # Cleaned column 'filename_infere' phase 3
│   │  ├── anonymized_data.csv           # Anonymized data
│   │  ├── bizzar_traces.csv           # Impossible traces to clean,removed in phase3_nettoyage_fichiere
│   │  ├── error_df.csv                  # Incorrect traces
│   │  ├── identifiants_2425.csv         # Data of different type of students
│   │  ├── seance_vide.csv               # Traces of the seance = '' (Removed from original df)
│   │  ├── traces_empty_seance.csv       # Traces of seance = ' ' (Removed from original df)
│   │  ├── too_short_sessions.csv        # Traces with too short lengths (Removed from original df)
│   │
│   ├── processed/
│      ├── anonymized_actor.csv          # Name of actors with their hash id
│
├── notebooks/             
│   ├── 1.Cleaning_actors.py           # Cleaning actor column
│   ├── 2.Cleaning_filename_phase1.py  # Cleaning filename_infere column by verb
│   ├── 3.Cleaning_filename_phase2.py  # Cleaning filename_infere column by sessions 
│   ├── 4.Cleaning_filename_phase3.py  # Finding and removing bizzar indices 
│   ├── 5.Anonymizing.py               # Anonymizing data   
│   ├── 6.Analyze.py                   # Analyzing data  
│   ├── find_filename_by_commandRan.py # Mirabelle's code, it is integrated in Sana's code             
│   ├── find_test_final.py             # Mirabelle's code, it is integrate in Sana's code
│   ├── find_tests.py                  # Mirabelle's code, I didn't use it
│ 
│
├── src/                     
│   ├── data/                # constants
│   │    ├── cleaning.py     # This is Thomas code , can be deleted, I don't use it in my code
│   │    ├── constants.py    # constants values that are used in different files of project
│   │    ├── variable_constant.py # constants values that change in each year
│   │    
│   ├── features/            # Feature engineering
│       ├── utils.py               # Thomas code , can be deleted later, I don't use it in my code
│       ├── data_anonymization.py  # Functions to anonymize (I used Thomas's code, it takes 37 mins!)
│       ├── data_cleaning.py       # Functions to cleaning actors or filename_infere
│       ├── data_testing.py        # Functions to test the results after cleaning each time
│       ├── io_utils.py            # Functions to read and write csv files 
│
│        
└── README.md                # Project documentation
```

## How to run the project?

- Go to folder : **notebooks**

- Run **1.Cleaning_actors.ipynb** with data : **traces250102_clean.csv** ----> result data : **acteur_nettoyage_2425.csv**
<br>
(remember to use the notebooks not the .py)

- Run **2.Cleaning_filename_phase1.ipynb** with data : **acteur_nettoyage_2425.csv** ----> result data : **phase1_nettoyage_fichiere.csv**
<br>

- Run **3.Cleaning_filename_phase2.ipynb** with data : **phase1_nettoyage_fichiere.csv** ----> result data : **phase2_nettoyage_fichiere.csv**
<br> 

- Run **4.Cleaning_filename_phase3.ipynb** with data : **phase2_nettoyage_fichiere.csv** ----> result data : **phase3_nettoyage_fichiere.csv**
<br> 

- Run **5.Anonymizing.ipynb** with data : **phase3_nettoyage_fichiere.csv** ----> result data : **anonymizing.csv** This data is not used for the next process because it was hard to analyze with anonymizing data, so I used **phase3_nettoyage_fichiere.csv** directly but it's better to use anonymized data for ananlyze in future.
<br> 

- Run **6.Ananlyze.ipynb** with data : **phase3_nettoyage_fichiere.csv** ----> result data : No data as result just plots
<br> 

## How does cleaning work?
Cleaning is in two main parts : 1- Cleaning actors 2- Cleaning filenames

- Cleaning actors:
    The goal is to make all values in **actor** column of dataframe, look like this structure : **prenom.nom.etu**.
    <br>
    Therefore, I add another column **binome** to seperate students who were in group; I also removed those who entered their name with @, and I removed others or correct them manually with Mirabelle, who were impossible to write a code for them.

- Cleaning filename:
    The goal is to find the correct filename for all rows (the correct filename of student were working with).
    <br>
    Therefore, I added another column **filename_infere** and I tried in two phase : phase 1 and phase 2 fill this column.

    - phase 1 : it tries to just fill the new column filename_infere for each different verb (it doesn't check if the name which is found is correct or not, it just fill them).

    - phase 2 : it checks the found filename_infere and correct them or delete them if needed (it is done by validate_process function), and then it tries to fill the empty filename_infere by sandwich function.

## The command for syncronation
jupytext --sync *.ipynb
jupytext --to notebook 1.Preparation.py

jupytext --to py my_notebook.ipynb (first time)
jupytext --set-formats ipynb,py:percent 2.Cleaning_filename_phase1.ipynb

## Three main thing for stage
- How to check if the student did the Test and continue the Test
- When the Test is red what did they do, did they continue or they did nothing
- Seperate the student that are very debutan and the student that already did some courses in programmation

## Some Explainations:

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


## An idea about different type of students, it's not implemented:

- By the size of difference found, you can check if the part was added or was deleted or it was completely change or it was just a tiny differences

- Students can't be grouped by the day because it's various but we can calculate the averag of work for each student or the average of progress for each student during each TP

- In TP_GAME, because there are 4 different files, we should analyze it seperatly and do the average method for each file and for each student.

- different types of students :
    - **strong students** : They started strongly and they solved all the bugs without any giving up.
    
    - **tried failed students** : they tried and they changed but at the end they gave up because they couldn't find the bug (Whether the result of test is successful or not)
    
    - **tried successful students** : They tried and they have a progress and at the end they understood the TP.
    
    - **lazy students** : They don't have lot's of traces for a TP and during the TP they didn't change a specific thing. (wether the test result is passed or not)
    
    - **mad students** : They tried lot's of Run.Test with the same code or a tiny difference during a day
