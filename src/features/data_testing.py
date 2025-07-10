# All function for testing data 

#------------------------------------------------
#                  Library
#------------------------------------------------
import pandas as pd 
from typing import Tuple
import sys
sys.path.append('../')
#------------------------------------------------
#                  Functions
#------------------------------------------------

# Get all total values for the dataframe
def test_filename_infere_total(df:pd.DataFrame,pattern: str) -> None:

    """
    It test the totals of filename_infere of the entire dataframe.

    Args:
        df : The original dataframe.
        pattern : A string of filenames.

    Returns:
        None 
    """

    excluded_verbs = ['Session.Start', 'Session.End', 'Docstring.Generate']

    total_trace          = len(df)
    total_empty_string   = (df['filename_infere'] == '').sum()
    total_empty_string_2 = ((df['filename_infere'] == '') & (df['seance'] != 'semaine_1') & (~df['verb'].isin(excluded_verbs))).sum()
    total_nan            = df['filename_infere'].isna().sum()

    subset = df[df['filename_infere'] != '']

    total_correct_name     = subset['filename_infere'].str.contains(pattern, na = False).sum()
    total_NOT_correct_name = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()

    if total_trace == total_correct_name:
        print("All filenames are cleaned!")
    
    else:
        print("There are still traces to be cleaned")

    print(f"Total number of rows : {total_trace}")
    print(f"Total number of empty string : {total_empty_string}")
    print(f"Total empty strings excluding semaine_1 and verbs : Sessions.Start/End/Docstring.Generate: {total_empty_string_2}")
    print(f"Total number of Nan : {total_nan}")
    print(f"Total number of correct name : {total_correct_name}")
    print(f"Total number of NOT correct name : {total_NOT_correct_name}")

# Get all total values for a week
def test_filename_infere_each_week(week: str,df: pd.DataFrame,pattern: str) -> None:

    """
    It test the totals of filename_infere of a specific week.

    Args:
        week : A value of the seance column.
        df : The original dataframe.
        pattern : A string of filenames.

    Returns:
        None 
    """

    total_semaine               = (df['seance'] == week).sum()
    total_empty_string_semaine  = (df[df['seance'] == week]['filename_infere'] == '').sum()
    total_nan_semaine           = df[df['seance'] == week]['filename_infere'].isna().sum()

    subset = df[(df['seance'] == week) & (df['filename_infere'] != '')]

    total_correct_name_semaine     = subset['filename_infere'].str.contains(pattern, na = False).sum()
    total_NOT_correct_name_semaine = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()

    if total_semaine == total_correct_name_semaine:
        print("Cleaning successful!")
    
    else:
        print("There are still traces to be cleaned")
    print(f"Total number of rows in {week} : {total_semaine}")
    print(f"Total number of empty string : {total_empty_string_semaine}")
    print(f"Total number of Nan : {total_nan_semaine}")
    print(f"Total number of correct name : {total_correct_name_semaine}")
    print(f"Total number of NOT correct name : {total_NOT_correct_name_semaine}")

# Get total empty strings for each verb
def get_number_of_empty_filename_for_week(week: str,df : pd.DataFrame) -> None:
    
    """
    Calculates the number of empty strings in filename_infere in a week.

    Args:
        week : A value of the seance column.
        df : The original dataframe.

    Returns:
        None 
    """
     
    verbs = ['File.Open', 'File.Save', 'Run.Test', 'Run.Debugger', 'Run.Program','Run.Command']

    for verb in verbs:
        total = ((df['verb'] == verb) & (df['filename_infere'] == '')  & (df['seance'] == week)).sum()
        print(f"Total number of emptystring for {verb} : {total}")

# Test if there are still incorrect filename_infere after removing the too short traces
def test_incorrect_names(df : pd.DataFrame, week: str, pattern: str) -> None:

    """
    Test if there is any incorrect filename_infere or not after removing the too_short_session.

    Args:
        week : A value of the seance column.
        df : The original dataframe.
        pattern : A string of filenames.

    Returns:
        None 
    """

    # check if there is still any invalid names 
    subset = df[(df['seance'] == week) & (df['filename_infere'] != '')]
    total_invalid_names = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()
    
    if total_invalid_names == 0:
        print('There is no more invalid names, YAY!')
        return df

    else:
        print("There are still invalid names, something is wrong...")
    
# Check after the cleanign part, is there any sessions that doesn't include Run.Test at all in each TP_prog
def check_not_including_Run_Test_fast(df: pd.DataFrame, tp_prog_indices: list) -> Tuple[list, int]:
    result = []

    session_starts = df[df['verb'] == 'Session.Start'].index.tolist()
    session_ends = df[df['verb'] == 'Session.End'].index.tolist()

    sessions = list(zip(session_starts, session_ends))
    tp_prog_set = set(tp_prog_indices)  # for faster lookup

    for start_idx, end_idx in sessions:
        # Check if any TP_prog falls within this session
        if any(i in tp_prog_set for i in range(start_idx, end_idx + 1)):
            session_slice = df.loc[start_idx:end_idx]
            if not (session_slice['verb'] == 'Run.Test').any():
                result.append((start_idx, end_idx))

    return result, len(result)