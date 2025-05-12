#------------------------------------------------
#                  Library
#------------------------------------------------
import pandas as pd 
import os


#------------------------------------------------
#                  Functions
#------------------------------------------------

def reading_dataframe(dir : str, file_name : str) -> pd.DataFrame:
    """
    Read data from the CSV file in a directory and convert them into a dataframe.
    
    Args:
        dir: can be any directory like INTERIM_DATA_DIR
        file_name: the name of the file to read the data (like CSV or JSON)
    
    Returns:
        A dataframe.
    """
    # Check if the file exists in the directory
    file_path = os.path.join(dir, file_name)

    if os.path.isfile(file_path):
        print(f"The file {file_name} exists in the directory.")

        # convert to dataframe
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as error:
            print(f"There is an error is reading the dataframe, error : {error}")

    else:
        print(f"The file {file_name} does not exist in the directory.")

    return None

def column_and_head(df : pd.DataFrame) -> None:
    """
    Print the column and head of a dataframe as input.
    
    Args:
        df: Any dataframe.
    
    Returns:
        Print column and head of the dataframe.
    """
    print("5 rows of the dataframe: \n")
    print(df.head())
    print("\n")
    print("Columns of the dataframe: \n")
    print(df.columns)

    return None
    