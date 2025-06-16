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
def write_csv(df : pd.DataFrame, dir: str, file_name: None) -> None:
    """
    Write the dataframe into csv file.
    
    Args:
        df  : Any dataframe.
        dir : Directory to save the csv file
        file_name : if there is already a filename to save the file 
    Returns:
        CSV file.
    """
    # If I hadn't give any name 
    if file_name is None:
        file_name = str(input("Enter the name of csv (WITHOUT .csv) : \n"))

    # Check if the file exists in the directory
    if os.path.isdir(dir):
        print(f"Directory is ok.")

        # convert to csv
        try:
            df.to_csv(dir + file_name + ".csv", index=False)
            print("File saved.")
            
        except Exception as error:
            print(f"There is an error in saving the dataframe in csv, error : {error}")

    else:
        print(f"The directory: {dir} doesn't exist.")

    return None
    
def write_too_short_indices_to_csv(df : pd.DataFrame, dir: str, week : str, filename:str) -> None:
    """
    Write the dataframe into csv file.
    
    Args:
        df: Any dataframe BUT with specific columns.
        dir : Directory to save the csv file.
        columns_to_keep : List of columns to keep them.

    Returns:
        CSV file.
    """

    # add column semaine
    df['seance'] = week

    # remove the rows without any too_short_sessions
    filtered_df = df[df['too_short_indices'].apply(lambda x: x != [])]

    # save them into a csv file
    try:
        write_csv(filtered_df[['name_students','too_short_indices']],dir,filename)
    except:
        print('There is an error in saving too_short_sessions in csv!')