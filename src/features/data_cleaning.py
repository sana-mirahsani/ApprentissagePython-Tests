# All function for cleaning data 


#------------------------------------------------
#                  Library
#------------------------------------------------
import pandas as pd 
import sys
sys.path.append('../')
from pandas import to_datetime, to_timedelta
import re
import numpy 
import difflib
from src.data.variable_constant_2425 import SORTED_SEANCE
from src.data.variable_constant_2425 import SORTED_SEANCE, all_TP_functions_name 
#------------------------------------------------
#                  Functions
#------------------------------------------------


# ---------------- Time cleaning --------------
# Change time format
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

# ---------------- Actor cleaning -------------
# Find not matching values
def not_a_correct_identifier(df: pd.DataFrame, column : str) -> list:

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

# Remove @ from the end
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

# Remove all lines of an actor
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

# Split actor and binome
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

# Delete specific name of actor or binome
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

# Replace jokers by real names
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

# Manually cleaning
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

#------------------------------------------------
#                  filename cleaning
#------------------------------------------------
# Cut datafram into small parts
def cut_df(df: pd.DataFrame, week: str, student_name: str) -> list:
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
    try:
        df_filtered = df[(df['seance'] == week) & (df['actor'] == student_name)]

        if len(df_filtered) == 0 :
            df_filtered = df[(df['seance'] == week) & (df['binome'] == student_name)]
            if len(df_filtered) == 0 :
                print(f"No trace with this name in semaine : {student_name}")
                

    except Exception as error:
        print('here1')
        print(error)

    indices = df_filtered.index[df_filtered['verb'].isin(['Session.Start', 'Session.End'])].tolist()
    values  = df_filtered.loc[indices, 'verb'].tolist()

    i = 0
    while i < len(values) - 1:
        
        try:
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

        except Exception as error:
            
            print(error)

    # return all indices
    return pairs, empty_trace_pairs

# Extract filename for not None value
def extract_short_filename(series: pd.Series) -> pd.Series:
    '''
    Extract filename by split / and get the last value for row which has a filename.

    Args:
        series : A column of dataframe.

    Returns:
        series : The same column but clean.
    '''
    return series.str.split('/').str[-1]

# Fill empty values of filename with clean commandRan column
def extract_short_filename_from_commandRan_Run_Program(commandRan_Run_Program: pd.Series) -> pd.Series:
    '''
    Get a Dataframe and fill filename column of Run.Program by
    cleaned commandRan column.

    Args:
        commandRan_Run_Program : A column of dataframe.

    Returns:
        clean: The same column but clean.
    '''

    # Replace $EDITOR_CONTENT by ''
    cleaned = commandRan_Run_Program.str.replace('%Run -c $EDITOR_CONTENT\n', '', regex=False)
    
    # Remove %Run from the beginning
    cleaned = cleaned.str.replace('^%Run ', '', regex=True).str.rstrip()
    
    # Remove \n from the end
    cleaned = cleaned.str.replace('\n', '', regex=False)

    return cleaned

# Fill empty values by P_codeState
def extract_short_filename_from_P_codestate_Run_Program(codestate_Run_Program: str) -> str:
    '''
    Get a Dataframe and fill filename column of Run.Program by
    cleaned commandRan column.

    Args:
        codestate_Run_Program : The value of codestate for Runprogram.

    Returns:
        codestate_Run_Program: Clean codestate_Run_Program just with the name of function.
    '''
    
    match = re.search(r"<trace>(.*?)</trace>", str(codestate_Run_Program))
    return match.group(1) if match else ''
    
# Fill empty values of filename with clean commandRan column
def extract_short_filename_from_commandRan_Run_Debugger(commandRan_Run_Debugger: pd.Series) -> pd.Series:
    '''
    Get a Dataframe and fill filename column of Run.Debugger by
    cleaned commandRan column.

    Args:
        commandRan_Run_Debugger : A column of dataframe.

    Returns:
        clean: The same column but clean.
    '''

    # Remove %Debug from the beginning
    try:
        cleaned = commandRan_Run_Debugger.str.replace('^%Debug ', '', regex=True).str.rstrip()
    
    except Exception as error:
        print(error)
        
    # Remove \n from the end
    cleaned = cleaned.str.replace('\n', '', regex=False)

    return cleaned

# Fill empty values of filename with clean commandRan column
def extract_short_filename_from_commandRan_Run_Command(commandRan_Run_Command: pd.Series) -> pd.Series:

    """
    Get a Dataframe and fill filename column of Run.Command by
    cleaned commandRan column.

    Args:
        commandRan_Run_Command : A column of dataframe.

    Returns:
        clean: The same column but clean.
    """
    # Create a mask
    mask = commandRan_Run_Command.str.startswith('%FastDebug ', na=False)
    
    # Apply cleaning only to matching rows
    cleaned = commandRan_Run_Command[mask] \
        .str.replace('^%FastDebug ', '', regex=True) \
        .str.rstrip() \
        .str.replace('\n', '', regex=False)
    
    # Return a Series with only the cleaned values, aligned with original index
    return cleaned

# Find filename_infere by checking the name of functions in codestate
def find_filename_by_function_name(TP_files:dict,codestate:str) -> str:

    """
    Get the codestate of a row, and see if it can find any name of functions of all TPs
    in it, if it finds, it extracts the corresponding filename of the function, and return it.

    Args:
        TP_files : A Dict of all files with their functions.
        codestate : P_codestate or F_codestate of a row.

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """

    for item in TP_files.items():
    
        if len(item[1]) > 1:
            pattern = '|'.join(item[1])

        else: 
            pattern = item[1][0]

        match = re.search(pattern, codestate)

        if match: 
            
            filename_infere = item[0]
            return filename_infere
            
    return '' # no match found!

# Find the correct filename by checking the similarity
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

        similarity = difflib.SequenceMatcher(None, correct_name, filename_infere).ratio()

        if similarity > 0.6:
            return correct_name
        
    return '' # Wasn't similar!

# find filename by checking the name of the file in codestate
def find_filename_by_codestate(pattern: str, codestate: str) -> str:

    """
    It gets a pattern : all filenames, and the codestate, it checks if it can find
    the name of the file in the codestate like the name between <trace></trace>
    if not if check the name of the function in codestate by calling find_filename_by_function_name.

    Args:
        pattern : All filesname.
        codestate : P_codeState or F_codeState of a row.

    Returns:
        filename_infere: The correct name of the file or an empty string.
    """

    match_state = re.search(pattern, codestate)

    if match_state: # if the name is in the P_codeState
        matched_filename = match_state.group()  # Extract the name
        return matched_filename

    else: # if the exact name is not in P_codeState and student might removed the name part, we check the match with the content
        filename_infere = find_filename_by_function_name(all_TP_functions_name,codestate)
        
        # Remove to test
        #if filename_infere == '':
            #print("Filename not found!")
        return filename_infere
    
# check and correct the filename_infere between each session.Start and session.End
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
    # Remove to test:
    #not_found_filename_index = []

    for index in subset.index:
        row = df.loc[index]
            
        filename_infere = row['filename_infere']
        
        # check the emptyness (only for Run.Command and Run.Program, Ignore Docstring,session.start,session.end)
        if filename_infere == '':
            
            if row['verb'] in ['Run.Command', 'Run.Program']:

                if row['P_codeState'] != '': # P_codeState has a content
                    filename_infere = find_filename_by_codestate(pattern,row['P_codeState'])
                    
                    if filename_infere == '':
                        pass
                        # Remove to test:
                        #not_found_filename_index.append(index)

                else:
                    pass
                    #print('here3')
                    #not_found_filename_index.append(index)
            else:
                pass
                # Remove to test:
                #not_found_filename_index.append(index)   
                #print(row['verb'])
                #print(not_found_filename_index)

        # filename_infere non vide
        else:
            match = re.search(pattern, filename_infere) 
            
            if match: # if it's match, extract the correct name
                filename_infere = match.group()

            else: # filename is not correct
                #print('here2')
                # Try to find the similar correct name
                filename_infere = find_similarity(pattern_list,filename_infere)
                #print(filename_infere)
                if filename_infere == '': # If the name is not similar
                    #print('here3')
                    if row['verb'] in ['File.Open', 'File.Save']:
                        #print('here4')
                        if row['F_codeState'] != '': # F_codeState has a content
                            filename_infere = find_filename_by_codestate(pattern,row['F_codeState'])
                            #print('here5')
                            if filename_infere == '':
                                pass
                                # Remove to test:
                                #not_found_filename_index.append(index)
                            
                        else:
                            pass
                            # Remove to test:
                            #print('here2')
                            #not_found_filename_index.append(index)

                    elif row['verb'] in ['Run.Test', 'Run.Command', 'Run.Program', 'Run.Debugger']:

                        if row['P_codeState'] != '': # P_codeState has a content
                            filename_infere = find_filename_by_codestate(pattern,row['P_codeState'])
                            
                            if filename_infere == '':
                                pass
                                # Remove to test:
                                #not_found_filename_index.append(index)

                        else:
                            pass
                            # Remove to test:
                            #print('here1')
                            #not_found_filename_index.append(index)

        # change filename_infere of df with the correct name
        df.at[index, 'filename_infere'] = filename_infere 

    # Remove to test:
    #if filename_infere == '':
    #    print("Can't find filename for these indices:")
    #    print(not_found_filename_index)

# Fill empty string by using sandwich method
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

# Creat indices of each Session.Start and Session.End
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
        indices, too_short_indices = cut_df(df,week,student)

        df_indices = pd.concat([
            df_indices,
            pd.DataFrame({'name_students': [student], 'indices': [indices], 'too_short_indices': [too_short_indices]})
        ], ignore_index=True)

    return df_indices

# Remove indices which has only one or two traces
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

                try:
                    df = df.drop(index=range(start , end + 1)) # remove useless indices
                except Exception as error:
                    print(f"Error in removing useless traces : {error}")
                    return None
                
            try:
                row['too_short_indices'].clear()
            except:
                print("Removing failed!")
                
    return df

# Clean traces with one or two verbs
def check_invalid_names(df:pd.DataFrame,df_indices:pd.DataFrame): 

    """
    It checks if there is any too short session, if so it removes them by calling function remove_too_short_traces.

    Args:
        df : The original dataframe.
        df_indices : A dataframe of all activities for each student.

    Returns:
        df : The same dataframe but without any short session.
    """

    # if in the test there are still incorrect filename_infere and there not deleted
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