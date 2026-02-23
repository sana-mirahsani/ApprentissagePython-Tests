# All functions which are called directly or inside another function for cleaning data
"""
Explanation:
This file contains all functions for cleaning data.
Above of each function is mentioned wether the function 
is called directly in a notebook, or inside another function in this file.
Also all functions from each notebook are sorted next to each other and above them is written they belong to which notebook.
If there is a function which is used in different notebooks, I mentioned above it.
Hope it helps you :)
"""
#------------------------------------------------
#                  Library
#------------------------------------------------
import sys
sys.path.append('../')

import pandas as pd 
from pandas import to_datetime, to_timedelta
import re
import difflib
import ast
from src.features.data_testing import check_P_codestate_and_commandRan
from src.data.variable_constant_2425 import pattern_files_name , all_TP_functions_name_except_TP1_and_TPGAME

#------------------------------------------------
#      Functions of 1.Cleaning_actor.ipynb
#------------------------------------------------


# ---------------- part 1 : Time cleaning --------------
# Change time format : called directly
def clean_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consider type of 'session.id' as str.
    Change the format of 'timestamp.$date', 'time_delta', 'session.duration'.
    Reset the indices.

    Args:
        df : A dataframe.

    Returns:
        Same dataframe but cleaned.
    """

    # 1. Change the type of session.id to str
    if 'session.id' in df.columns: # check if the column exist
        df['session.id'] = df['session.id'].astype(str)

    # 2. change the format of timestamp.$date, time_delta, session.duration
    df.update({
    'timestamp.$date': to_datetime(df['timestamp.$date'], format='ISO8601'),
    'time_delta': to_timedelta(df['time_delta']),
    'session.duration': to_timedelta(df['session.duration']),
    })

    # 3. Reset the index
    df.reset_index(drop=True, inplace=True)
    return df

# ---------------- part 2: Actor cleaning -------------
def check_invalid_identifier_by_pattern(df: pd.DataFrame, column : str) -> list:

    """
    Find the names of actor that doesn't match the pattern prenom.nom.etu
    Returns a list of these unique names.

    Args:
        df : The dataframe.
        column : A column can be actor or binome (any column to check with format).

    Returns:
        list: A list of not matching names.
    """

    pattern = r'^[a-zA-Z\-]+\.[a-zA-Z0-9\-]+\.etu$'

    invalid_actors = df[column].dropna().unique()
    invalid_actors = pd.Series(invalid_actors)

    # Remove empty strings before applying regex
    invalid_actors = invalid_actors[invalid_actors != '']

    invalid_actors = invalid_actors[~invalid_actors.str.fullmatch(pattern)]

    return invalid_actors

def check_invalid_identifier_by_login_file(df: pd.DataFrame, column : str, path:str) -> list:
    """
    Find the names of actor that are not in the login.txt

    Args:
        df : The dataframe.
        column : A column can be actor or binome (any column to check with format).
        path : path of the login.txt

    Returns:
        diff: A list of invalid names for that year.
    """
    
    #extract unique actors as list
    unique_actors = df[column].dropna().unique().tolist()
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip() # read txt file in str
        names = ast.literal_eval(content) # extract names as list

        # find invalid students name, those not in the names
        diff = [x for x in unique_actors if x not in names]

        diff_wtihout_empty_strings = [x for x in diff if x != '']

    return diff_wtihout_empty_strings

# Remove @ from the end : called directly
def delete_end_email(df: pd.DataFrame) -> pd.DataFrame:

    """
    Check if there actors contians @, if so just pick the first part.

    Args:
        df : The dataframe.

    Returns:
        df: Same dataframe with the cleaned actor column.
    """

    pattern = r'^([a-zA-Z\-]+\.[a-zA-Z0-9\-]+\.etu)@'

    matches = df['actor'].str.extract(pattern)[0]

    # Replace values in 'actor' column **only where a match is found**
    df['actor'] = matches.combine_first(df['actor'])

    return df

# Remove all lines of an actor : called directly
def delete_actor_lines(df: pd.DataFrame,name: str) -> pd.DataFrame:
    """
    Remove all traces of the name of actor which we don't need to keep like nebut.

    Args:
        df : The dataframe.
        name : The given name to delete its traces
    Returns:
        df: Same dataframe with deleted traces.
    """

    df_cleaned = df[df['actor'] != name]
    return df_cleaned

# Split actor and binome : called directly
def split_actor_binome(df: pd.DataFrame) -> pd.DataFrame:

    """
    Split the actor and binome, keep the first name in actor but 
    put the second name in binome column (new column).

    Args:
        df : A dataframe.

    Returns:
        df: The same dataframe but with one name in actor and second name in binome.
    """
     
    split_df = df['actor'].str.split('/', n=1, expand=True)
    
    # Insert a new empty column next to 'actor'
    col_index = df.columns.get_loc('actor')
    df.insert(col_index + 1, 'binome', '')

    # Assign first part back to 'actor', second part to 'binome'
    df['actor'] = split_df[0]
    df['binome'] = split_df[1]

    return df    

# Delete specific name of actor or binome : called directly
def delete_name_actor_binome(df: pd.DataFrame, column : str, name : str) -> pd.DataFrame:
    
    """
    Find the name in actor or in binome and replace it by ''.

    Args:
        df : A dataframe.
        column : The name of the column.
        name : The name to remove.

    Returns:
        df: The same dataframe but with removed name in the column.
    """

    df.loc[df[column] == name, column] = ''

    return df

# Replace jokers by real names : called directly
def replace_jokers(df: pd.DataFrame, columns : list, jokers_real_name : dict) -> pd.DataFrame:

    """
    Find jokers and replace them with the real name.

    Args:
        df : A dataframe.
        column : The name of the column to search jokers.
        jokers_real_name : A dictionary of jokers and real names.

    Returns:
        df: The same dataframe but with cleaned values of jokers.
    """
    for column in columns:
        df[column] = df[column].replace(jokers_real_name)

    return df  

# Manually cleaning : called directly
def cleaning_manual_actors_2425(df: pd.DataFrame, name: str) -> pd.DataFrame:

    """
    It's a manual cleanign which can be change, depends on the data.
    For now deleting rows of anis.younes.etu@univ-lille.fr actor.

    Args:
        df : A dataframe.
        name : The name of actor to remove rows.

    Returns:
        df: The same dataframe but with deleted values of name.
    """

    df_cleaned = df[df['actor'] != name]
    
    return df_cleaned

#------------------------------------------------------------
#      Functions of 2.Cleaning_filename_phase1.ipynb
#-----------------------------------------------------------

# Extract filename for not None value : called directly
def extract_short_filename(series: pd.Series) -> pd.Series:
    '''
    Extract filename by split / and get the last value for row which has a filename.

    Args:
        series : A column of dataframe.

    Returns:
        series : The same column but clean.
    '''
    return series.str.split('/').str[-1]

# Fill empty values of filename with clean commandRan column : called directly
def extract_short_filename_from_commandRan_Run_Program(commandRan_Run_Program: str) -> str:
    '''
    Get a Dataframe and fill filename column of Run.Program by
    cleaned commandRan column.

    Args:
        commandRan_Run_Program : A column of dataframe.

    Returns:
        clean: The same column but clean.
    '''

    # Safety check (important in pipelines)
    if not isinstance(commandRan_Run_Program, str):
            raise TypeError("commandRan_Run_Program must be a string")
        
    # Replace $EDITOR_CONTENT by ''
    commandRan_Run_Program = commandRan_Run_Program.replace('%Run -c $EDITOR_CONTENT\n', '')

    # Remove %Run from the beginning
    if commandRan_Run_Program.startswith('%Run '):
            commandRan_Run_Program = re.sub(r'^%Run ', '', commandRan_Run_Program)

    # Remove trailing whitespace  
    commandRan_Run_Program = commandRan_Run_Program.rstrip()

    # Remove \n from the end
    commandRan_Run_Program = commandRan_Run_Program.replace('\n', '')

    return commandRan_Run_Program

# Fill empty values by P_codeState : called directly
def extract_short_filename_from_P_codestate(codestate: str) -> str:
    '''
    Get a Dataframe and fill filename column of a verb by
    cleaned commandRan column.

    Args:
        codestate : The value of codestate for Runprogram.

    Returns:
        codestate: Clean codestate just with the name of function.
    '''
    
    match = re.search(r"<trace>(.*?)</trace>", str(codestate))
    return match.group(1) if match else ''
    
# Fill empty values of filename with clean commandRan column : called directly
def extract_short_filename_from_commandRan_Run_Debugger(commandRan_Run_Debugger: str) -> str:
    '''
    Get a Dataframe and fill filename column of Run.Debugger by
    cleaned commandRan column.

    Args:
        commandRan_Run_Debugger : A column of dataframe.

    Returns:
        clean: The same column but clean.
    '''
    # Safety check (important in pipelines)
    if not isinstance(commandRan_Run_Debugger, str):
            raise TypeError("commandRan_Run_Debugger must be a string")
        
    # Remove %Debug from the beginning
    if commandRan_Run_Debugger.startswith('%Debug '):
            commandRan_Run_Debugger = re.sub(r'^%Debug ', '', commandRan_Run_Debugger)

    # Remove trailing whitespace
    commandRan_Run_Debugger = commandRan_Run_Debugger.rstrip()
        
    # Remove \n from the end
    commandRan_Run_Debugger = commandRan_Run_Debugger.replace('\n', '')

    return commandRan_Run_Debugger

# Fill empty values of filename with clean commandRan column : called directly
def extract_short_filename_from_commandRan_Run_Command(command: str) -> str:

    """
    Clean a single Run.Command command string.

    Args:
        command : A single string from commandRan column.

    Returns:
        Cleaned string.
    """

    # Safety check (important in pipelines)
    if not isinstance(command, str):
        raise TypeError("commandRan_Run_Command must be a string")

    # Remove prefix if present
    if command.startswith('%FastDebug '):
        command = re.sub(r'^%FastDebug ', '', command)

    # Remove trailing whitespace
    command = command.rstrip()

    # Remove newline characters
    command = command.replace('\n', '')

    return command

    """# Create a mask
    print(type(commandRan_Run_Command))
    mask = commandRan_Run_Command.str.startswith('%FastDebug ', na=False)
    
    # Apply cleaning only to matching rows
    cleaned = commandRan_Run_Command[mask] \
        .str.replace('^%FastDebug ', '', regex=True) \
        .str.rstrip() \
        .str.replace('\n', '', regex=False)
    
    # Return a Series with only the cleaned values, aligned with original index
    return cleaned"""

# Function to add space before parantes in dictionary : called inside find_filename_by_commandRan
def get_regexp_for_function_call(functions_name:dict) -> dict:
    '''
    functions_name is a dictionary whose keys are filenames and values are list of function names of the kind 'repetition'

    Adds a regexpr that allows spaces or tabs before the '('. 
    '''
    dico = {}
    for key in functions_name:
        function_list = functions_name[key]
        new_list = []
        for name in function_list:
            new_name = rf'(\W|\A){name}[ \t]*\('#r'(\W|\A)' + re.escape(name) + r'[ \t]*\('
            new_list.append(new_name)
        dico[key] = new_list
    return dico

# Function to find the corresponding filename: called inside find_filename_by_commandRan
def find_filename_by_searching_function_call(TP_files:dict, commandRan:str) -> str:

    """
    Searchs if the commandRan contains a call to a function in TP_files, and if any returns the associated filename.
    Else returns the empty string.

    Args:
        TP_files : A Dict of all files with their functions.
        commandRan : commandRan of a raw

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """

    for filename, function_names in TP_files.items():
        pattern = '|'.join(function_names)
        match = re.search(pattern, commandRan)
        
        if match: 
            return filename
            
    return '' # no match found!

# Find filename by looking the content of commandRan column : called directly
def find_filename_by_commandRan(all_TP_functions : dict, pattern_files_name: str, commandRan: str) -> str:

    """
    Prend en paramètre un dico qui associe à un nom de fichier une liste de nom de fonctions
    ex : 'fonctions.py' : ['repetition', ...]

    pattern_files_name : capture l'ens des noms de fichiers

    commandRan : une commandRan

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """
    match_state = re.search(pattern_files_name, commandRan)

    if match_state: # if the name is in the P_codeState
        matched_filename = match_state.group()  # Extract the name
        return matched_filename

    else: # if the exact name is not in P_codeState and student might removed the name part, we check the match with the content
        dico_regexpr = get_regexp_for_function_call(all_TP_functions)
        filename_infere = find_filename_by_searching_function_call(dico_regexpr, commandRan)
        
        # Remove to test
        #if filename_infere == '':
            #print("Filename not found!")
        return filename_infere

# Fill filename_infere for a verb
def fill_filename_infere_for_verb(df: pd.DataFrame, verb_name: str, values_for_verb: dict) -> pd.DataFrame:
    """
    It fills the empty values of filename_infere for a verb by P_codeState 
    if it contains <trace>.*\.py</trace>, and if not it fills them by commandRan 
    if it starts with %Debug or %NiceDebug or %FastDebug or %Run for ONLY empty filename_infere.

    Args:
    df : The dataframe.
    verb_name : The name of the verb to fill filename_infere for it.
    values_for_verb : A dictionary of values for the verb which we will use to check.

    Returns:
    df: The same dataframe but with filled filename_infere for the verb.
    """
    # first : fill by P_codeState if it contains <trace>.*\.py</trace>
    if values_for_verb['total_non_empty_codestate'] > 0 and values_for_verb['total_codestate_contain_trace'] > 0:
        mask = (df['verb'] == verb_name) & (df['filename_infere'] == '')
        df.loc[mask, 'filename_infere'] = df.loc[mask, 'P_codeState'].map(extract_short_filename_from_P_codestate)
        
    # second : fill by commandRan if it starts with %Debug or %NiceDebug or %FastDebug or %Run for ONLY empty filename_infere
    if values_for_verb['total_non_empty_commandRan'] > 0:
        if verb_name == 'Run.Program':
            mask = (df['verb'] == 'Run.Program') & (df['filename_infere'] == '') 
            df.loc[mask, 'filename_infere'] = df.loc[mask, 'commandRan'].map(extract_short_filename_from_commandRan_Run_Program)
        
        elif verb_name == 'Run.Command':
            mask = (df['verb'] == 'Run.Command') & (df['filename_infere'] == '')
            df.loc[mask, 'filename_infere'] = df.loc[mask, 'commandRan'].map(extract_short_filename_from_commandRan_Run_Command)

            df.loc[mask, 'filename_infere'] = df.loc[mask, 'commandRan'].apply(
            lambda command: find_filename_by_commandRan(all_TP_functions_name_except_TP1_and_TPGAME, pattern_files_name, command)
            )
            
        elif verb_name == 'Run.Debugger':
            mask = (df['verb'] == 'Run.Debugger') & (df['filename_infere'] == '')
            df.loc[mask, 'filename_infere'] = df.loc[mask, 'commandRan'].map(extract_short_filename_from_commandRan_Run_Debugger)
        else:
            raise ValueError(f"Unexpected verb name: {verb_name}. Expected 'Run.Program', 'Run.Command', or 'Run.Debugger'.")

    return df

# Make decision how to fill the filename_infere
def desicion_function_to_fill_filename_infere(df: pd.DataFrame, verb_name: str, verb_name_value: int) -> pd.DataFrame:
    """
    It decides how to fill filename_infere for a verb, it has 3 cases:
        1. If all filename_infere for the verb are filled, we will check their correctness later
        2. If some filename_infere for the verb are empty, we will try to fill them by P_codeState and commandRan if they have non-empty codestate or non-empty commandRan respectively, and if they start with %Debug or %NiceDebug or %FastDebug or %Run.
        3. The verb doesn't exist.

    Args:
        df : The dataframe.
        verb_name : The name of the verb to fill filename_infere for it.
        verb_name_value : The value of the verb's state in the dictionary passed by check_P_codestate_and_commandRan function.

    Returns:
        df: The same dataframe but with filled filename_infere for the verb if it is the case.

    """

    if verb_name_value == 0:
        print(f"All filename_infere for {verb_name} are filled, we will check their correctness later in phase 2.")
        return df
    
    elif verb_name_value == 1:
        if verb_name == 'Session.Start' or verb_name == 'Session.End':
            print('Verb is Session.Start or Session.End, we will not fill filename_infere for these verbs.')
            return df
        
        else:
            print(f"Some filename_infere for {verb_name} are empty, we will try to fill them by P_codeState and commandRan if they have non-empty codestate or non-empty commandRan respectively, and if they start with %Debug or %NiceDebug or %FastDebug or %Run.")
            values_for_verb = check_P_codestate_and_commandRan(df, verb_name)
            df = fill_filename_infere_for_verb(df, verb_name, values_for_verb)
            return df
    else:
        raise ValueError(f"Unexpected verb_name_value: {verb_name_value}. Expected 0 or 1.")

#------------------------------------------------------------
#      Functions of 3.Cleaning_filename_phase3.ipynb
#-----------------------------------------------------------
# Find the correct filename by checking the similarity : called inside correct_filename_infere_in_subset
def find_similarity(TP_Files_name: list,filename_infere:str) -> str: 

    """
    Get the filename_infere of a row, and checks if it is similar with
    any name of the files, if the similarity is more than 60%, then return
    the correct filename, if not checks for the other.

    Note :The explaination of how does SequenceMatcher work, 
    is in the Readme part '## Explainations'
    
    Args:
        TP_Files_name : A list of files' name of TPs.
        filename_infere : filename_infere of a row.

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """
     
    for correct_name in TP_Files_name:

        # remove the .py
        filename_infere_removed = filename_infere.replace('.py', '')
        similarity = difflib.SequenceMatcher(None, correct_name[:-3], filename_infere_removed).ratio()

        if similarity > 0.7:
            return correct_name
        
    return '' # Wasn't similar!

# Function to choose the most appeared corresponding filename: called inside find_filename_by_codestate
def desicion_for_filename(extracted_function_names_list : list ,all_TP_functions:dict):

    """
    This function choose the most corresponding filename between all the filename correspond, and return it as the correct filename.
    Attention : This function choose the most appeared filename, so it there are more than one filename which apeared most and their frequency is same,
    it chooses by alphabet.

    Args:
        extracted_function_names_list : all functions found after word 'def' by find_filename_by_codestate()
        
        all_TP_functions : all_TP_functions_name_except_TP1_and_TPGAME from variable_constant_2425.py

    Returns:
        filename_infere: The correct name of the row or an empty string.
    """

    all_extracted_filename = []

    # step1: find all corresponding filenames
    for extracted_function in extracted_function_names_list:
        
        for filename, function_names in all_TP_functions.items():
            set_function_names = set(function_names) # convert to set, to increase the speed : O(n)

            if extracted_function in set_function_names: # if function name is in the list
                all_extracted_filename.append(filename) # append the corrsponding filename
            
    # step2: find the most appeared filename
    if len(all_extracted_filename) != 0: # if it is not empty
        all_extracted_filename_series = pd.Series(all_extracted_filename) # convert to pandas to find faster

        # find the most appeared
        most_common_filename = all_extracted_filename_series.mode()[0] 
        return most_common_filename
    
    else:
        # return empty string as filename
        return ''

# find filename by checking the name of the file in codestate : called inside correct_filename_infere_in_subset
def find_filename_by_codestate(all_TP_functions : dict, pattern_files_name : str, codeState: str) -> str:

    """
    This function finds the corresponding filename by looking the codeState's content
    It has two steps:
    step 1 : It searches for <trace></trace> in the codestate and if there is, it extracts the name between <trace></trace>.
             Then it checks if the extracted name is correct, meaning if it is equal to one of the file's name in the pattern_files_name.

    step 2 : If step 1 didn't work, meaning neither there was any <trace></trace> nor the extracted name was correct, 
             It extracted all function's names that are defined (by searching 'def' in codeState) then it finds
             the most filename appeared by calling desicion_for_filename.
             If student has used different functions from different TP, it choose the most appeared TP.
             This is a basic idea and it is good for TP which have same functions. It can be better!

    Args:
        all_TP_functions : all_TP_functions_name_except_TP1_and_TPGAME from variable_constant_2425.py
        pattern_files_name : pattern_files_name from variable_constant_2425.py
        codeState : The codeState (P_codeState or F_codeState) of the current row.

    Returns:
        filename_infere: The correct name of the row or an empty string.
    """

    # initialize filename_infere
    filename_infere = ''

    # step 1 : search for <trace></trace> in string (instead of searching the name)
    match = re.search(r"<trace>(.*?)</trace>", codeState)

    if match: # extract the filename between <trace></trace>
        
        # check if the extracted name is correct:
        filename_infere = match.group(1)

        # convert files name to set, to check faster
        file_set = set(pattern_files_name.split('|'))

        if filename_infere in file_set: # extracted name is correct
            return filename_infere
        
        else : # extracted name is NOT correct
            filename_infere = '' # make empty filename again

    # step 2 : search for 'def' in codestate
    if (not match) or (filename_infere == ''):
        
        # extract all functions name after 'def' in codestate
        extracted_function_names = re.findall(r'\bdef\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*\(', codeState)
        
        # if there is atleast one defined function:
        if len(extracted_function_names) != 0 : 
            # find the most appeared filename
            
            filename_infere = desicion_for_filename(extracted_function_names,all_TP_functions)
        
    return filename_infere
    
# check and correct the filename_infere between each session.Start and session.End : called directly
def correct_filename_infere_in_subset(subset: pd.DataFrame,df: pd.DataFrame,pattern:str) -> None:

    """
    It checks the filename_infere of each row of a subset of the the original dataframe.
    If it is empty, it tries to fill it by looking the P_codestate, it there is already a name,
    it checks the name and if it is not correct it tries to find the correct name if it can't,
    puts an empty string (like removing the name).

    Note 1: There are some parts which is written Remove to test: ; these are the parts to test for 
    the case where function can't find any correct name for the filename_infere, this can help to see their indices
    of the original dataframe.

    Note 2: This function used a loop on a subset of the original dataframe, the subset which includes the session.start
    and session.end of each student in a specific semaine.

    Args:
        subset : A subset of an acitivity.
        df : The original dataframe.
        pattern : A string of files name.

    Returns:
        None : it changes the filename_infere inside the for loop.
    """

    pattern_list = pattern.split('|')

    for index in subset.index:
        row = df.loc[index]
            
        filename_infere = row['filename_infere']
        new_filename_infere = ''
        
        # check the emptyness (only for Run.Program)
        if filename_infere == '':

                if (row['verb'] ==  'Run.Program') and (row['P_codeState'] != ''): # P_codeState has a content
                    new_filename_infere = find_filename_by_codestate(all_TP_functions_name_except_TP1_and_TPGAME,pattern_files_name,row['P_codeState'])          

        # filename_infere non vide
        else:
            match = re.search(pattern, filename_infere) 
            
            if match: # if it's match, extract the correct name
                new_filename_infere = match.group()

            else: # filename is not correct
                    # lets have a look to the codestate when possible
                    if row['verb'] == 'File.Save':
                        
                        if row['F_codeState'] != '': # F_codeState has a content
                            new_filename_infere = find_filename_by_codestate(all_TP_functions_name_except_TP1_and_TPGAME,pattern_files_name,row['F_codeState'])
                            
                            # if  it can't find the name in codestate, it checks the old filename_infere with similarity
                            if new_filename_infere == '':
                                new_filename_infere = find_similarity(pattern_list,row['filename_infere'])

                    elif row['verb'] in ['Run.Test', 'Run.Command', 'Run.Program', 'Run.Debugger']:

                        if row['P_codeState'] != '': # P_codeState has a content
                            new_filename_infere = find_filename_by_codestate(all_TP_functions_name_except_TP1_and_TPGAME,pattern_files_name,row['P_codeState'])
                            
                            # if  it can't find the name in codestate, it checks the old filename_infere with similarity
                            if new_filename_infere == '':
                                new_filename_infere = find_similarity(pattern_list,row['filename_infere'])         

        # change filename_infere of df with the correct name
        df.at[index, 'filename_infere'] = new_filename_infere 

"""
I dont know where I used this function!!

def correct_filename_infere_in_subset2(subset: pd.DataFrame,df: pd.DataFrame,pattern:str) -> None:

    pattern_list = pattern.split('|')

    for index in subset.index:

        row = df.loc[index]
        filename_infere = row['filename_infere']
        new_filename_infere = filename_infere  # Default fallback
        
        # check the emptyness (only for Run.Program)
        if filename_infere == '' and row['verb'] == 'Run.Program' and row['P_codeState']:
            # Case 1: Empty filename, Run.Program with available P_codeState
            new_filename_infere = find_filename_by_codestate(pattern, row['P_codeState'])

        # filename_infere non vide
        elif filename_infere != '':
            match = re.search(pattern, filename_infere) 
            
            if match: 
                # Case 2: filename_infere already valid
                new_filename_infere = match.group()

            else:
                # Case 3: filename_infere not valid, try to fix based on verb and codestate
                    if row['verb'] == 'File.Save':
                        
                        if row['F_codeState'] != '': # F_codeState has a content
                            new_filename_infere = find_filename_by_codestate(pattern,row['F_codeState'])
                            
                            # if  it can't find the name in codestate, it checks the old filename_infere with similarity
                            if new_filename_infere == '':
                                new_filename_infere = find_similarity(pattern_list,row['filename_infere'])

                    elif row['verb'] in ['Run.Test', 'Run.Command', 'Run.Program', 'Run.Debugger']:

                        if row['P_codeState'] != '': # P_codeState has a content
                            new_filename_infere = find_filename_by_codestate(pattern,row['P_codeState'])
                            
                            # if  it can't find the name in codestate, it checks the old filename_infere with similarity
                            if new_filename_infere == '':
                                new_filename_infere = find_similarity(pattern_list,row['filename_infere'])      

        # change filename_infere of df with the correct name
        df.at[index, 'filename_infere'] = new_filename_infere 
        """

# Fill empty string by using sandwich method : : called directly
def sandwich(subset:pd.DataFrame,df: pd.DataFrame) -> None:

    """
    It is used for the activity which there are some empty filename_inferes between a session.start and session.end.
    It fills them by the sandwich mecanism.

    Args:
        subset : A subset of an acitivity.
        df : The original dataframe.

    Returns:
        None : it changes the filename_infere inside the for loop.
    """

    # check values before last_filename_infere
    last_filename_infere = subset.loc[subset['filename_infere'] != '', 'filename_infere'].iloc[0]
    last_filename_infere_index = subset.loc[subset['filename_infere'] != '', 'filename_infere'].index[0]
    
    empty_filename_indices = []

    """to_fill_indices = subset.loc[
            (subset.index < last_filename_infere_index) & 
            (subset['filename_infere'] == '')
        ].index

    df.loc[to_fill_indices, 'filename_infere'] = last_filename_infere # fill values before the first value
    """
    start_index = last_filename_infere_index # start from the first not empty value

    for index, row in subset.loc[start_index:].iterrows():

        if row['filename_infere'] == '':
            empty_filename_indices.append(index)

        elif row['filename_infere'] != '':
            
            if row['filename_infere'] == last_filename_infere:
                
                df.loc[empty_filename_indices, 'filename_infere'] = last_filename_infere # Fill all empty string
                empty_filename_indices = [] # Reset the empty indices

            else:
                last_filename_infere = row['filename_infere']
                empty_filename_indices = [] # Reset the empty indices

    # if the rest of the values are empty after the first filename_infere
    #if empty_filename_indices:
        #df.loc[empty_filename_indices, 'filename_infere'] = last_filename_infere

# Cut datafram into small parts : called inside create_df_indices
def cut_df_by_seance(df: pd.DataFrame, week: str, student_name: str) -> list:
    '''
    Extract indices of all session.start and session.end of a week for a specific student.

    Args:
        df : A clean_actor dataframe.
        week : The name of the week.
        student_name : The name fo the student.

    Returns:
        indices : All indices of the session.start and session.end from dataframe.
    '''

    pairs = []
    empty_trace_pairs = []

    # Filter dataframe for the week and student
    df_filtered = df[(df['seance'] == week) & (df['actor'] == student_name)]

    if len(df_filtered) == 0 :
        df_filtered = df[(df['seance'] == week) & (df['binome'] == student_name)]
        if len(df_filtered) == 0 :
            print(f"No trace with this name in semaine : {student_name}")
    
    indices = df_filtered.index[df_filtered['verb'].isin(['Session.Start', 'Session.End'])].tolist()
    values  = df_filtered.loc[indices, 'verb'].tolist()

    i = 0
    while i < len(values) - 1:
        
        if values[i] == 'Session.Start' and values[i+1] == 'Session.End':
        
            start_idx = indices[i]
            end_idx   = indices[i+1]

            if abs(start_idx - end_idx) > 2: # put useful indices in pairs
                
                pairs.append([start_idx,end_idx])
            
            else: # put useless indices in empty_trace_pairs to remove them later
                empty_trace_pairs.append([start_idx,end_idx])
            
            i += 2  # move past the 1 and 2
        else:
            print(f"invalid pair {indices[i]}")
            i += 1  # skip if it's not a valid pair

    # return all indices
    return pairs, empty_trace_pairs

# Creat indices of each Session.Start and Session.End : called directly
def create_df_indices(list_students: list, df: pd.DataFrame,week: str) -> pd.DataFrame:

    """
    It creates a dataframe of session.start and sessions.end of all students during 
    a specific semaine. It does not consider the traces with less than 2 length.

    Args:
        list_students : A list of students of the current semaine.
        df : The original dataframe.
        week : Any values of column : seance.

    Returns:
        df_indices : A dataframe of all activities for each student.
    """
     
    # creat df_indices 
    df_indices = pd.DataFrame(columns=['name_students', 'indices', 'too_short_indices'])

    # Fill df_indices for each student in a week
    for student in list_students: # it takes 15 second maximum, it's normal
        indices, too_short_indices = cut_df_by_seance(df,week,student)

        df_indices = pd.concat([
            df_indices,
            pd.DataFrame({'name_students': [student], 'indices': [indices], 'too_short_indices': [too_short_indices]})
        ], ignore_index=True)

    return df_indices

# Remove indices which has only one or two traces : called inside check_invalid_names
def remove_too_short_traces(df: pd.DataFrame,df_indices: pd.DataFrame) -> pd.DataFrame:
    
    """
    It removes all too short sessions for each student.

    Args:
        df : The original dataframe.
        df_indices : A dataframe of all activities for each student.

    Returns:
        df : The same dataframe but without any short session.
    """

    for index, row in df_indices.iterrows():

            for activity in row['too_short_indices']:

                start = activity[0]
                end   = activity[1]

                df = df.drop(index=range(start , end + 1)) # remove useless indices
            
            row['too_short_indices'].clear()
                
    return df

# Clean traces with one or two verbs : called directly
def check_invalid_names(df:pd.DataFrame,df_indices:pd.DataFrame): 

    """
    It checks if there is any too short session, if so 
    it removes them by calling function remove_too_short_traces.

    Args:
        df : The original dataframe.
        df_indices : A dataframe of all activities for each student.

    Returns:
        df : The same dataframe but without any short session.
    """

    # if in the test there are still incorrect filename_infere and they weren't deleted
    if (df_indices['too_short_indices'].apply(lambda x: len(x) == 0)).all():
        print("There is no too short trace, if there are still invalid names, check them one by one!")
        return df

    else:
        print('There are invalid traces, start to remove them...')

    df = remove_too_short_traces(df,df_indices)

    if df is not None:
        print('Too short indices are removed successfuly!')
        return df
    
    else:
        print("Dataframe is None!")