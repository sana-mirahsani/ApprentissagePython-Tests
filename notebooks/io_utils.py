#------------------------------------------------
#                  Library
#------------------------------------------------
import pandas as pd 
import os


#------------------------------------------------
#                  Functions
#------------------------------------------------

# Read dataframe
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
        print(f"Directory is ok.")

        # convert to dataframe
        try:
            df = pd.read_csv(file_path, keep_default_na=False)
            return df
        except Exception as error:
            print(f"There is an error is reading the dataframe, error : {error}")

    else:
        print(f"The filepath : {file_path} does not exist.")

    return None

    
# Write the new dataframe into CSV file
def write_csv(df : pd.DataFrame, dir: str) -> None:
    """
    Write the dataframe into csv file.
    
    Args:
        df: Any dataframe.
        dir : Directory to save the csv file
    
    Returns:
        CSV file.
    """
    file_name = str(input("Enter the name of csv : \n"))

    # Check if the file exists in the directory
    if os.path.isdir(dir):
        print(f"Directory is ok.")

        # convert to csv
        try:
            df.to_csv(dir+file_name+".csv")
            print("File saved.")
            
        except Exception as error:
            print(f"There is an error in saving the dataframe in csv, error : {error}")

    else:
        print(f"The directory: {dir} doesn't exist.")

    return None
    