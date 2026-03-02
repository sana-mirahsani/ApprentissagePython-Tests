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
│   |  ├── anonymized_actor.csv          # Name of actors with their hash id
│   |
│   ├── raw/ # JSON data
│
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
│       ├── pipeline_utils         # Functions to verify the values
│ 
├── requirement.txt
|       
└── README.md                # Project documentation
```

## How to run the project?

- Go to folder : **notebooks**

- Run **7.run_all_cleaning.py** and give the name of the raw data.json which must be in data/raw directory.

- This file creates a pipeline to execute all notebooks (from number 0 to 4) for cleaning phase. This pipeline gets the raw data in json and gives 
a cleaned df for actors and filenames in CSV in data/interim/filename.

- In Every execution of a notebook the output is saved as csv file and it is passed to the next notebook as the input.

- Add meta data tag:parameters the second cell in notebook

## Where are these csv files saved?

At the beginning of the pipeline, a directory is created in data/raw and data/interim with the name of file_name + date (yy/mm/dd) + time (h:m:s). 
<br>

**EX : traces260105_20260203_221511**

## How do I know which csv is the output of which part?
The formula is like this : 

**If filename : traces260105**

- filename + _clean.csv -----> output of 0.Cleaning_JSON.ipynb
- filename + _actor_clean.csv -----> output of 1.Cleaning_actors.ipynb
- filename + _filename_phase1_clean.csv -----> output of 2.Cleaning_filename_phase1.ipynb
- filename + _filename_phase2_clean.csv -----> output of 3.Cleaning_filename_phase2.ipynb
- filename + _filename_phase3_clean.csv -----> output of 4.Cleaning_filename_phase3.ipynb

## What does each notebook of cleaning do?

- 0.Cleaning_JSON.ipynb : Gets data in JSON, do some basic cleaning gives a csv file (Thomas code)
- 1.Cleaning_actors.ipynb : Cleans the students name.
- 2.Cleaning_filename_phase1.ipynb : Cleans the filename by verbs.
- 3.Cleaning_filename_phase2.ipynb : Cleans the filename by seance.
- 4.Cleaning_filename_phase3.ipynb : Cleans filenames which are correct but they don't respond to their content of P_codestate.

## How does cleaning work (with more details)?
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

## What are the modes of executing?
For cleaning phase, there are two modes : 1. By Pipeline 2. Manaully

To run by pipeline, you should have parameters tag in the metadata but manually you can run the notebook independtly and directly without any meta data.

## How to add the metadata to run by pipeline?

You need to add the text below in the cell where the parameters are written like filename.

```
{
    "tags": [
        "parameters"
    ]
}
```


## What is the result folder? what does it include?
With pipeline in 7.run_all_cleaning.py, we can have several run for one data or even with different data, 
since we want to save the output of each cell of a notebook in cleaning part, after the execution all notebook with it's output is save in JSON format, 
in this directory.

## How does the similarity work in utils_module/data_cleaning.py : find_similarity():
    
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

## How and where dataframe traces250102_clean is sorted ?
Before the cleaning process, there is another process which is called **process_raw_data** and it gets the data from server in json format and transforms it into a dataframe and then it sorts them in this order : first in order of alphabet of the actor column, second in order of the session.id column in descending order, and third in order of the tempstamp.date column. This process produce the data **traces250102_clean** which is the input data of **1.Cleaning_actors.ipynb**. This **process_raw_data** is done by Thomas and it is in **cleaning.py** module.


## An idea about different type of students, it's not implemented (in Future):

- By the size of difference found, you can check if the part was added or was deleted or it was completely change or it was just a tiny differences

- Students can't be grouped by the day because it's various but we can calculate the averag of work for each student or the average of progress for each student during each TP

- In TP_GAME, because there are 4 different files, we should analyze it seperatly and do the average method for each file and for each student.

- different types of students :
    - **strong students** : They started strongly and they solved all the bugs without any giving up.
    
    - **tried failed students** : they tried and they changed but at the end they gave up because they couldn't find the bug (Whether the result of test is successful or not)
    
    - **tried successful students** : They tried and they have a progress and at the end they understood the TP.
    
    - **lazy students** : They don't have lot's of traces for a TP and during the TP they didn't change a specific thing. (wether the test result is passed or not)
    
    - **mad students** : They tried lot's of Run.Test with the same code or a tiny difference during a day

## The command for syncronation
jupytext --sync *.ipynb
jupytext --to notebook 1.Preparation.py

jupytext --to py my_notebook.ipynb (first time)
jupytext --set-formats ipynb,py:percent 2.Cleaning_filename_phase1.ipynb

## report of every appointment.
### Wendsday 28/01
- look at the debutan and non debutan in didapro.
- anonymisation is send by email , code of mirabelle
- clean and make cleaner the code of didabro
- add test in find test functions
- classify the student in debutan, doing test, doing functions

### Friday 30/01
- what did I do in the nettoyage. how all those numbers are deleted.
- trace_clean the first CSV from Thomas work: 
look at his work to what to do about and add the phase zero before cleaning the actor column. check how much time does it take? Done
- Fnish the part not finish in analyse : 

First look at the thomas code for the new data : Done!

### For next appoinment : Done
--------
- Use the part of Mirbelle of research_usage ( not for now) : Done
- In cleaning actor add a function to extract all the actors name that are same or included in the list of student which mirabel gave it in data : Done
- Add a folder for each data of each year : Done
- How can we save the result of each cell of each notebook for using different data of each year : yes and Done

### Thursday 05/02 : Done
- add mode of execution : 1. pipeline 2. maneulment : Done
- add special function for each filename , for the part of jokers and cleaning manual in notebook 1.cleaning_actors.ipynb : Done

- add special function for docstring generate in 2.cleaning_phase1, special function for each year because we already have filename for docstring generate for this year but not for the last year BUT they are not correct : Done

- add how to make metdata in notebook, in readme : Done

- add function for choosing the correct src/data/variable_constant for each year since it changes for each year : Done

- add how can we run a notebook alone in Readme : Done

- add semaine 1 for cleaning in phase2 becaus ein this year we had data and it is important, so another special function : Done

### Friday: Remain only 1
In 0.cleaning_Json , put the the two functions in a src/features and then pass the inputs and outputs to the main function : Done

Add Selected_lineno, Lineno in Thomas code to convert them as the column.

chnage the name of test_function.py to verification_functions.py : done

Check if phase3 works correctly or not : Done

#### Last week:
- Put function debutan in data_cleaning and add its usage in clean_actor : Done
- Add Selected_lineno, Lineno in Thomas code to convert them as the column.
- Use the part of Mirbelle of research_usage : Done