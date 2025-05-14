#------------------------------------------------
# All functions for anonymization
#------------------------------------------------

#------------------------------------------------
#                  Library
#------------------------------------------------
import pandas as pd 
import hashlib
from typing import Optional
from src.data.constants import INTERIM_DATA_DIR, PROCESSED_DATA_DIR, COLUMNS_WITH_PATH
#------------------------------------------------
#                  Functions
#------------------------------------------------

# Hash function
def _hash_224(s : str) -> str:
    """
    Generates a SHA-224 hash for the given string.

    Args:
        s (str): The input string to be hashed.

    Returns:
        str: The resulting SHA-224 hash in hexadecimal format.
    """
    return hashlib.sha224(bytes(s,"utf-8")).hexdigest()

# Anonymize actor and binom 
def anonymize_actor(row : str) -> Optional[str]:
    """
    Anonymize the actor and binom column, 
    This function takes a row of the dataframe and anonymized the 'actor' and 'binom' column.

    Args:
        row : the value of row of dataframe.

    Returns:
        str or None: Hashed value.
    """
    # if there is actor and binom
    if pd.notna(row['actor']) and pd.notna(row['binom']):
        return [_hash_224(row['actor']), _hash_224(row['binom'])]
    
    # if there is only actor
    elif pd.notna(row['actor']) and pd.isna(row['binom']):
        return _hash_224(row['actor'])
    
# Replace actor with hashed version in specified columns 
def replace_columns(row : str) -> Optional[str]:
    """
    After hashing actor and binom, it should replace the actor and binom 
    in COLUMNS_WITH_PATH by their hash value.

    Args:
    
    Returns:
    
    """
    # ToDo
    # Create a mapping dictionary (original -> hashed)
    hash_map = dict(zip(actors_df[0], hashed_0[0]))

    # Replace all columns in one step (no loop needed)
    df[COLUMNS_WITH_PATH] = df[COLUMNS_WITH_PATH].replace(hash_map)

# Anonymize P_codeState, F_codeState
def replace_codeState(row : str) -> Optional[str]:
    """
    

    Args:
    
    Returns:
    
    """
    # ToDo
    pass