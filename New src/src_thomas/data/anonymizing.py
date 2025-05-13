import hashlib
import pandas as pd
from .constants import INTERIM_DATA_DIR, PROCESSED_DATA_DIR, COLUMNS_WITH_PATH
from .cleaning import load_clean_data
from src.features.utils import give_list_actors

def anonymize_data(input_file:str, data_output_file:str, actors_output_file:str) -> None:
    """
    Anonymizes data from the input file and saves the results to specified output files.
    
    Parameters:
        input_file (str): The prefix of the name of the input CSV file.
        data_output_file (str): The prefix of the name of CSV file where the anonymized data will be saved.
        actors_output_file (str): The prefix of the name of CSV file where the anonymized actors will be saved.

    Prend du temps car utilise une boucle dans pandas, Thomas a coupé l'écriture
    en petits bouts pour que ça prenne qq minutes et non qq heures.
  
    """
    df = load_clean_data(input_file + ".csv")

    print("Saving anonymized actors")
    create_anonymized_actor_csv(df, actors_output_file)

    print("Anonymizing data")
    create_anonymized_dataframe_csv(df, data_output_file)

def create_anonymized_dataframe_csv(df: pd.DataFrame, filename: str):
    """
    Anonymizes specific columns in a DataFrame and saves the result to a CSV file.

    This function processes row of the given DataFrame where actor name can be find. Anonymizing the 'actor' column
    by hashing its components, and replaces occurrences of the original actor names in 
    specified columns. It also cleans up comments in 'P_codeState' and 'F_codeState' columns.
    The anonymized DataFrame is then saved as a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to be anonymized.
        filename (str): The name of the output CSV file.
    """
    anonymized_df = optimized_anonymize_dataframe(df)
    anonymized_df.to_csv(INTERIM_DATA_DIR + filename + ".csv")

def optimized_anonymize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    CHANGED!
    Anonymizes a DataFrame in chunks to optimize performance.

    This function processes the input DataFrame in chunks of 1000 rows at a time,
    anonymizing each chunk and then concatenating the results into a single DataFrame.

    Parameters:
        df (pd.DataFrame): The input DataFrame to be anonymized.

    Returns:
        pd.DataFrame: The anonymized DataFrame.

    Notes:
        - This function is optimized for performance, as it processes the DataFrame in chunks
        to avoid memory issues when anonymizing large datasets.
        - chunk size is set to 1000 rows, but can be adjusted as needed. By exemple, chunk size 
        of 500 rows is the best one but chuck of 1000 rows are chosen because the change is sly 
        (take 0.16 second more for 1000 rows) and better lisibility in the logs.
    """
    chunk_size = 1000
    chunks = []
    total_rows = len(df)
    
    for start in range(0, total_rows, chunk_size):
        end = min(start + chunk_size, total_rows)
        print(f"Anonymizing rows {start}-{end-1}/{total_rows}")
        chunks.append(_slice_anonymize_dataframe(df, start, end))
    
    return pd.concat(chunks, ignore_index=True)

def _slice_anonymize_dataframe(df: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    """
    Slices the given DataFrame from the specified start index to the end index,
    and then anonymizes the sliced DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to be sliced and anonymized.
        start (int): The starting index for slicing.
        end (int): The ending index for slicing.

    Returns:
        pd.DataFrame: The anonymized DataFrame after slicing.
    """
    sliced_df = df.iloc[start:end]
    return anonymize_dataframe(sliced_df)
    
def anonymize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    CHANGED!
    Anonymizes the given DataFrame by hashing actors name and cleaning up comment in code state columns.

    Args:
        df (pd.DataFrame): The input DataFrame to be anonymized.

    Returns:
        pd.DataFrame: The anonymized DataFrame.
    """
    # Split 'actor' column into two parts
    actors_df = df['actor'].str.split('/', expand=True)
    
    # Hash both parts
    hashed_0 = actors_df[0].apply(_hash_224)
    hashed_1 = actors_df[1].apply(lambda x: '' if x == '' else _hash_224(x))
    
    # Reconstruct the 'actor' column
    df['actor'] = hashed_0 + '/' + hashed_1

    # Replace actor[0] with hashed version in specified columns
    for column in COLUMNS_WITH_PATH:
        df[column] = df[column].replace(actors_df[0].tolist(), hashed_0.tolist(), regex=False)

    # Apply comment cleaning functions
    df['P_codeState'] = df['P_codeState'].apply(_clean_unused_comments)
    df['F_codeState'] = df['F_codeState'].apply(_clean_unused_comments)
    
    return df


def _hash_224(s : str) -> str:
    """
    Generates a SHA-224 hash for the given string.

    Args:
        s (str): The input string to be hashed.

    Returns:
        str: The resulting SHA-224 hash in hexadecimal format.
    """
    return hashlib.sha224(bytes(s,"utf-8")).hexdigest()

def _clean_unused_comments(codestate : str) -> str:
    """
    Removes comments from the given code string, except for lines containing "\<trace\>".

    Args:
        codestate (str): The input code as a single string.

    Returns:
        str: The code with comments removed, except for lines containing "\<trace\>".
    """
    codestates = codestate.split('\n')
    cleanned_codestate = ""
    for ligne in codestates:
        idx = ligne.find("#")
        if (idx == -1) or ("<trace>" in ligne):
            cleanned_codestate += ligne + '\n'
        elif idx != 0:
            cleanned_codestate += ligne[:idx] + '\n'
    return cleanned_codestate[:-1]

def create_anonymized_actor_csv(df: pd.DataFrame, filename: str):
    """
    Creates a CSV file where actor are paired with there anonymized actor name.

    This function takes a DataFrame containing actor data, anonymizes the actor names
    using a hashing function, and saves the result to a CSV file.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing actor data.
        filename (str): The name of the output CSV file.
    """
    all_actors = give_list_actors(df)
    all_anonymized_actors = [_hash_224(actor) for actor in all_actors]
    df_all_actors = pd.DataFrame({
        'actor': all_actors,
        'anonymized_actor': all_anonymized_actors
    })
    df_all_actors.to_csv(PROCESSED_DATA_DIR + filename + ".csv")
