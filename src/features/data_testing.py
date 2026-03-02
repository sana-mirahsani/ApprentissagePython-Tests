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

def check_empty_values_in_column(df: pd.DataFrame, column_name: str, time_happened: str) -> tuple:
    """
    It checks the number of empty strings and null values 
    in a specific column of a DataFrame and prints the results.

    Args:
        df : A dataframe.
        column_name : The name of the column to check.
        time_happened : The time when the check is performed (before or after cleaning).

    Returns:
        A tuple containing the number of empty strings and null values in the column.
    """

    empty_values = (df[column_name] == '').sum()
    print(f"{time_happened} applying : Total number of empty strings in {column_name} = {empty_values}")

    null_values = df[column_name].isna().sum()
    print(f"{time_happened} applying : Total number of null values in {column_name} = {null_values}")

    return empty_values, null_values

def check_to_pass_or_not(old_value: int, new_value: int, name_value: str) -> None:
    """
    It comapres the old value and the new value of a specific metric (e.g., number of empty values)
    and prints whether the process is successful, nothing has changed, or if there is an issue.

    Args:
    old_value : The value before applying the cleaning process.
    new_value : The value after applying the cleaning process.
    name_value : The name of the metric being compared (e.g., "empty values").

    Returns:
        None
    """
    if old_value < new_value:
        raise ValueError(f"New value {new_value} of {name_value} is smaller than its old value {old_value}. This should not happen.")
    elif old_value > new_value:
        print(f"Process is successfully completed for {name_value}.")
    else:
        print(f"Nothing has changed in {name_value}.")

def Check_empty_filename_infere_in_verb(df: pd.DataFrame, verb_name: str) -> int:
    """
    It checks the number of empty strings and null values in the 'filename_infere' column 
    for a specific verb in the DataFrame.

    Args:
        df : A dataframe containing the data to check.
        verb_name : The name of the verb to check.

    Returns:
        An integer indicating the result of the check: 0 or 1 or 2.
    """
    total_verb       = len(df[df['verb']  == verb_name])
    total_verb_empty = (df[df['verb'] == verb_name]['filename_infere'] == '').sum()
    total_verb_nan   = df[df['verb'] == verb_name]['filename_infere'].isna().sum()

    if total_verb > 0 and total_verb_empty == 0 and total_verb_nan == 0:
        print(f"'{verb_name}' : {total_verb} rows and all have non-empty 'filename_infere'.") 
        return 0
    
    elif total_verb > 0 and (total_verb_empty > 0 or total_verb_nan > 0):
        print(f"'{verb_name}' : {total_verb} rows BUT {total_verb_empty} empty 'filename_infere' and {total_verb_nan} NaN 'filename_infere'.")
        return 1
    
    elif total_verb == 0:
        print(f"'{verb_name}' : No rows found in the DataFrame.")
        return 2
    
def check_P_codestate_and_commandRan(df: pd.DataFrame, verb_name: str) -> dict:
    """
    checks the content of 'P_codeState' and 'commandRan' columns for a specific verb in the DataFrame.

    Args:
        df : A dataframe containing the data to check.
        verb_name : The name of the verb to check (like Run.Test).

    Returns:
        A dictionary containing the results of the checks.
    """
    values = {}

    # check with P_codestate
    total_non_empty_codestate     = (df[df['verb']  == verb_name]['P_codeState'] != '').sum()
    total_codestate_contain_trace = df[df['verb']  == verb_name]['P_codeState'].str.contains(r'<trace>.*\.py</trace>', regex=True, na=False).sum()
    
    # check with commandRan
    total_non_empty_commandRan       = len(df[(df['verb'] == verb_name) & (df['commandRan'] != '')])
    total_commandRan_start_Debug     = df[df['verb'] == verb_name]['commandRan'].str.startswith('%Debug').sum()
    total_commandRan_start_NiceDebug = df[df['verb'] == verb_name]['commandRan'].str.startswith('%NiceDebug').sum()
    total_commandRan_start_FastDebug = df[df['verb'] == verb_name]['commandRan'].str.startswith('%FastDebug').sum()
    total_commandRan_start_Run       = df[df['verb'] == verb_name]['commandRan'].str.startswith('%Run').sum()

    # save all values in a dictionary
    values['total_non_empty_codestate'] = total_non_empty_codestate
    values['total_codestate_contain_trace'] = total_codestate_contain_trace
    values['total_non_empty_commandRan'] = total_non_empty_commandRan
    values['total_commandRan_start_Debug'] = total_commandRan_start_Debug   
    values['total_commandRan_start_NiceDebug'] = total_commandRan_start_NiceDebug
    values['total_commandRan_start_FastDebug'] = total_commandRan_start_FastDebug
    values['total_commandRan_start_Run'] = total_commandRan_start_Run

    # print values to simply check them
    print(f"Total rows of not empty strings in P_codeState for {verb_name} : {total_non_empty_codestate}")
    print(f"Total rows of P_codeState contian <trace> : {total_codestate_contain_trace}")

    print(f"Total rows of not empty strings in commandRan for {verb_name} : {total_non_empty_commandRan}")
    print(f"Total rows of commandRan starts with %Debug in {verb_name}     : {total_commandRan_start_Debug}")
    print(f"Total rows of commandRan starts with %NiceDebug in {verb_name} : {total_commandRan_start_NiceDebug}")
    print(f"Total rows of commandRan starts with %FastDebug in {verb_name} : {total_commandRan_start_FastDebug}")
    print(f"Total rows of commandRan starts with %Run in {verb_name}       : {total_commandRan_start_Run}")

    return values