#------------------------------------------------
# All function for cleaning data 
#------------------------------------------------

#------------------------------------------------
#                  Library
#------------------------------------------------
import pandas as pd 
from pandas import to_datetime, to_timedelta
import re
from typing import Optional

#------------------------------------------------
#                  Functions
#------------------------------------------------

#------------------------------------------------
#                  Time cleaning
#------------------------------------------------
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

#------------------------------------------------
#                  Actor cleaning
#------------------------------------------------
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
# Extract filename for not None value
def extract_filename(series: pd.Series) -> pd.Series:
    '''
    Extract filename by split / and get the last value for row which has a filename.

    Args:
        series : A column of dataframe.

    Returns:
        series : The same column but clean.
    '''
    return series.str.split('/').str[-1]

# Fill empty values of filename with clean commandRan column
def extract_filename_from_commandRan_Run_Program(commandRan_Run_Program: pd.Series) -> pd.Series:
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
def extract_filename_from_P_codestate_Run_Program(codestate_Run_Program: str) -> str:
    '''
    Get a Dataframe and fill filename column of Run.Program by
    cleaned commandRan column.

    Args:
        codestate_Run_Program : The value of codestate for Runprogram.

    Returns:
        codestate_Run_Program: Clean codestate_Run_Program just with the name of function.
    '''
    
    if isinstance(codestate_Run_Program, str) and codestate_Run_Program.strip().startswith('def '):
        try:
            # Extract between 'def ' and first '('
            codestate_Run_Program = codestate_Run_Program.strip()
            func_name = codestate_Run_Program.split('def ', 1)[1].split('(', 1)[0].strip()
            return func_name + '.py'
        except IndexError:
            return ''  # fallback if split fails
    return ''  # leave unchanged if it doesn't start with 'def '
    
# Fill empty values of filename with clean commandRan column
def extract_filename_from_commandRan_Run_Debugger(commandRan_Run_Debugger: pd.Series) -> pd.Series:
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