#------------------------------------------------
# All function for testing the result
#------------------------------------------------

#------------------------------------------------
#                  Library
#------------------------------------------------
import pandas as pd 
import re
from typing import Tuple, List

#------------------------------------------------
#                  Functions
#------------------------------------------------

# Test time format
def test_on_time() -> None:
    # ToDo
    # I didn't see any changes in using the format of time, what does it change?
    pass

# Test actor's name 
def test_on_actor(df: pd.DataFrame, column: str) -> Tuple[int, set[str]]:
    """
    Counts the number of values in 'actor' or 'binom' column 
    that do NOT match with the pattern 'prenom.nom.etu'.

    Args:
        df (pd.DataFrame): The input DataFrame.
        column (str): The name of the column to check.

    Returns:
        int: Total number of values not matching the expected pattern.
        set: Values not matching, remove the duplicates.
    """

    pattern = r'^[a-zA-Z\-]+\.[a-zA-Z0-9\-]+\.etu$'
    non_matching_values = df[~df[column].astype(str).str.strip().str.fullmatch(pattern)][column].tolist()

    if None in set(non_matching_values):
        print(f"There is no non_matching name in {column} column!")

    return df[column].apply(lambda x: not re.fullmatch(pattern, str(x).strip())).sum(), set(non_matching_values)