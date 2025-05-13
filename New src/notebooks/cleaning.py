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

# Clean actor column
def clean_actor(names: str) -> Optional[str]:
    """
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