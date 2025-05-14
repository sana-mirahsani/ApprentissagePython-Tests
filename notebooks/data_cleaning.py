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

# Find not matching values
def not_a_correct_identifier(df: pd.DataFrame) -> list:

    """
    Find the names of actor that doesn't match the pattern.
    Returns a list of these unique names.

    Args:
        df : The dataframe.

    Returns:
        list: A list of not matching names.
    """

    pattern = r'^[a-zA-Z\-]+\.[a-zA-Z0-9\-]+\.etu$'

    invalid_actors = df['actor'].dropna().unique()
    invalid_actors = pd.Series(invalid_actors)
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
    Find the name in actor or in binome and replace it by None.

    Args:
        df : A dataframe.
        column : The name of the column.
        name : The name to remove.

    Returns:
        df: The same dataframe but with removed name in the column.
    """

    df.loc[df[column] == name, column] = None

    return df


# Replace None value by ""
def replace_None_by_str(df: pd.DataFrame, column : str) -> pd.DataFrame:

    """
    Fill all the None values with the an empty string (une chaine vide).

    Args:
        df : A dataframe.
        column : The name of the column.

    Returns:
        df: The same dataframe but with one name in actor and second name in binome.
    """
     
    df[column] = df[column].fillna("")

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

def clean_actor(names: str) -> Optional[str]:
    """ Not USED!!!
    clean actors with this pattern 'prenom.nom.etu'.
    This function doesn't get a dataframe, instead it is applied on a dataframe and 
    it gets the row one by one of the dataframe as the input, 
    it changes them in-place without returning anything.

    Args:
        name : Row by row with the str type of dataframe.

    Returns:
        None or a cleaned name of actor as string.
    """
     
    #print(name) this is for test
    if isinstance(names, str):
        pattern = r'^[a-zA-Z\-]+\.[a-zA-Z0-9\-]+\.etu$'

        # 1. Remove '/'
        names = names.split('/')

        # 2. Remove ' '
        if '' in names : names.remove('')

        #print(names) #this is for test
        
        # 3. Check pattern prenom.nom.etu for both students
        cleaned = [] # it only takes one or two values (prenom.nom.etu)
        for name in names:
            if re.match(pattern, name):
                cleaned.append(name)  # valid, keep as is
            
            elif '@' in name:  # maybe correctable
                match = re.match(r'^([a-zA-Z\-]+\.[a-zA-Z0-9\-]+\.etu)@', name)

                if match:
                    cleaned.append(match.group(1)) # extract clean part

            else: # Jokers, must change
                # Remove nebut and luc
                if name == 'nebut' or name == 'luc':
                    cleaned.append(None)
                    print(name)

                elif name == 'MI1301' or name == 'MI1304':
                    cleaned.append('mariama-sere.sylla.etu')

        # Return first name as 'actor', second as 'binom' (if exists)
        if cleaned:
            return pd.Series([cleaned[0], cleaned[1] if len(cleaned) > 1 else None])
        
    # if the name is not str type
    return pd.Series([None, None])