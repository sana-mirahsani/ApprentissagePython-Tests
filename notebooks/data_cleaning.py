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
from src.data.variable_constant import SORTED_SEANCE
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

# Extract name of students
def extract_students_each_week(df: pd.DataFrame)-> pd.DataFrame:
    
    presence_actor  = df.groupby('seance')['actor'].unique() 
    presence_actor  = presence_actor.loc[SORTED_SEANCE] # Sort in the order of semester

    presence_binome  = df.groupby('seance')['binome'].unique() 
    presence_binome  = presence_binome.loc[SORTED_SEANCE] # Sort in the order of semester


    df_all_students = pd.DataFrame(columns=['week', 'num_students', 'name_students'])


    for seance in SORTED_SEANCE:

        # Append row
        all_students = set(presence_actor[seance]).union(set(presence_binome[seance]))

        df_all_students = pd.concat([
            df_all_students,
            pd.DataFrame({'week': [seance], 'num_students': [len(all_students)], 'name_students': [all_students]})
        ], ignore_index=True)

    return df_all_students

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

    # Filter dataframe for the week and student
    try:
        df_filtered = df[(df['seance'] == week) & (df['actor'] == student_name)]

        if len(df_filtered) == 0 :
            print("Error!.")
            return None

    except Exception as error:
        
        print(error)

    indices = df_filtered.index[df_filtered['verb'].isin(['Session.Start', 'Session.End'])].tolist()
    values  = df_filtered.loc[indices, 'verb'].tolist()

    i = 0
    while i < len(values) - 1:
        
        try:
            if values[i] == 'Session.Start' and values[i+1] == 'Session.End':
            
                start_idx = indices[i]
                end_idx   = indices[i+1]
            
                pairs.append([start_idx,end_idx])
                i += 2  # move past the 1 and 2
            else:
                i += 1  # skip if it's not a valid pair

        except Exception as error:
            print(error)

    # return all indices
    return pairs

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

    '''
    Get a Dataframe and fill filename column of Run.Command by
    cleaned commandRan column.

    Args:
        commandRan_Run_Command : A column of dataframe.

    Returns:
        clean: The same column but clean.
    '''
    # Create a mask
    mask = commandRan_Run_Command.str.startswith('%FastDebug ', na=False)
    
    # Apply cleaning only to matching rows
    cleaned = commandRan_Run_Command[mask] \
        .str.replace('^%FastDebug ', '', regex=True) \
        .str.rstrip() \
        .str.replace('\n', '', regex=False)
    
    # Return a Series with only the cleaned values, aligned with original index
    return cleaned


# Get student totals in a seance
def get_student_totals_each_week(df: pd.DataFrame, students_semaine : list, pattern : str)-> pd.DataFrame:
    '''
    Get a Dataframe and the list of students in a seance and calculate the totals for each students  
    and put them into a new dataframe.

    Args:
        df : The original dataframe.
        students_semaine : The list of students in a seance.

    Returns:
        df: A new dataframe with 6 columns for each students.
    '''

    df_analyze_students = pd.DataFrame(columns=['name', 'total_trace' ,'total_correct_filename_infere' , 'total_empty_string_filename_infere','total_NOT_correct_filename_infere', 'binome'])

    for student in students_semaine:

        # calculate
        total_trace        = ((df['seance'] == 'semaine_2') & (df['actor'] == student)).sum()
        total_correct      = df[(df['seance'] == 'semaine_2') & (df['actor'] == student)]['filename_infere'].str.contains(pattern, na = False).sum()
        total_empty_string = ((df['seance'] == 'semaine_2') & (df['actor'] == student) & (df['filename_infere'] == "")).sum()
        total_NOT_correct  = total_trace - total_empty_string - total_correct

        binome             = df[(df['seance'] == 'semaine_2') & (df['actor'] == student)]['binome'].unique()
        binome_clean       = binome[binome != ""] # remove the empty string because python counts them as an element
        
        df_analyze_students = pd.concat([
            df_analyze_students,
            pd.DataFrame({'name': [student], 'total_trace': [total_trace], 'total_correct_filename_infere': [total_correct], 'total_empty_string_filename_infere': [total_empty_string] , 'total_NOT_correct_filename_infere': [total_NOT_correct], 'binome': [binome_clean]})
        ], ignore_index=True)


    return df_analyze_students

# Get actors of student with zero trace
def actors_of_student_with_zero_trace(df: pd.DataFrame, students_with_trace_zero : numpy.ndarray)-> pd.DataFrame:
    '''
    Get a Dataframe and the list of students iwith zero trace in a specific seance and find thir actor,
    put the name of binome and its actor in a dataframe and return it.

    Args:
        df : The original dataframe.
        students_with_trace_zero : Array of students with zero trace .

    Returns:
        df: A new dataframe with 2 columns for each students and their actor in the same seance.
    '''

    df_of_students_zero_trace = pd.DataFrame(columns=['binome_with_zero_trace', 'its_actor'])

    for student in students_with_trace_zero:

        actor       = df[(df['seance'] == 'semaine_2') & (df['binome'] == student)]['actor'].unique()
        actor_clean = actor[actor != ""] # remove the empty string because python counts them as an element
            
        df_of_students_zero_trace = pd.concat([
                df_of_students_zero_trace,
                pd.DataFrame({'binome_with_zero_trace': [student], 'its_actor': [actor_clean] })
            ], ignore_index=True)
        

    return df_of_students_zero_trace

# Fill values of students with zero trace
def fill_values_of_binome_with_zero_trace(df_of_students_zero_trace: pd.DataFrame, df_analyze_students : pd.DataFrame)-> pd.DataFrame:
    '''
    Get a Dataframe and the list of students iwith zero trace in a specific seance and find thir actor,
    put the name of binome and its actor in a dataframe and return it.

    Args:
        df : The original dataframe.
        students_with_trace_zero : Array of students with zero trace .

    Returns:
        df: A new dataframe with 2 columns for each students and their actor in the same seance.
    '''

    index = 0

    for student in df_of_students_zero_trace['binome_with_zero_trace']:

        actor = (df_of_students_zero_trace[df_of_students_zero_trace['binome_with_zero_trace'] == student]['its_actor']).loc[index] # extract its actor's name
        actor = actor[0] # Just extract the string 
        
        mask_actor  = df_analyze_students['name'] == actor # filter on this actor
        mask_binome = df_analyze_students['name'] == student # filter on binome
        
        # Fill values empty in binom by its actor
        df_analyze_students.loc[mask_binome, 'total_trace']                        = df_analyze_students[mask_actor]['total_trace']   
        df_analyze_students.loc[mask_binome, 'total_correct_filename_infere']      = df_analyze_students[mask_actor]['total_correct_filename_infere'] 
        df_analyze_students.loc[mask_binome, 'total_empty_string_filename_infere'] = df_analyze_students[mask_actor]['total_empty_string_filename_infere'] 
        df_analyze_students.loc[mask_binome, 'total_NOT_correct_filename_infere']  = df_analyze_students[mask_actor]['total_NOT_correct_filename_infere'] 

        index += 1 # it's because of the problem in pandas, to have access the names as a string not array

    return df_analyze_students