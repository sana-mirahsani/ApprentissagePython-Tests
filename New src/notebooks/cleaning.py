#------------------------------------------------
# All function for cleaning data 
#------------------------------------------------

#------------------------------------------------
#                  Library
#------------------------------------------------
import pandas as pd 
import os
from pandas import to_datetime, to_timedelta
import re

#------------------------------------------------
#                  Functions
#------------------------------------------------

# Change time format
def clean_time(df: pd.DataFrame) -> pd.DataFrame:

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

# Clean actor column
def clean_actor(names) -> None:
    """
    clean actors with this pattern 'prenom.nom.etu'.
    This function doesn't get a dataframe, instead it is applied on a dataframe and 
    it gets the row one by one of the dataframe as the input, 
    it changes them in-place without returning anything.

    Args:
        name : A row of DataFrame.

    Returns:
        the cleaned name of actor
    """
     
    #print(name) this is for test
    if isinstance(names, str):
        pattern = r'^[a-zA-Z\-]+\.[a-zA-Z0-9\-]+\.etu$'

        # 1. Remove '/'
        names = names.split('/')

        # 2. Remove ' '
        if '' in names : names.remove('')

        #print(name) this is for test
        
        # 3. Check pattern prenom.nom.etu for both students
        for name in names:
            if re.match(pattern, name):
                return name  # valid, keep as is
            
            elif '@' in name:  # maybe correctable
                match = re.match(r'^([a-zA-Z\-]+\.[a-zA-Z0-9\-]+\.etu)@', name)

                if match:
                    return match.group(1)  # extract clean part
            else:
                #ToDO
                pass
     # discard bad names

# Seperate actor column
def split_actor_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Seperate actors name and put the binom's name into the binom column.

    Args:
        name : DataFrame.

    Returns:
        Same dataframe with the column binom.
    """

    df = df.copy()
    df['binom'] = df['actor'].apply(lambda x: x[1] if len(x) > 1 else None) # Add column binom
    df['actor'] = df['actor'].apply(lambda x: x[0])

    return df
