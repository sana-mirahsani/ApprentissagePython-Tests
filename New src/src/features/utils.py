# 02/25 PFE Thomas Briche
# ajouts Mirabelle

# ajout Mirabelle
# peut-être mieux ailleurs

from itertools import chain

def extract_filename_from_commandRan_Run_Program(command: str) -> str:
    '''
    precond : command doit commencer par %Run
    '''
    if command == '%Run -c $EDITOR_CONTENT\n':
        return ''
    filename = command[len('%Run '):].rstrip()
    return filename
    
import pandas as pd
from ..data.variable_constant import FUNCTIONS_BY_TP, FILES_BY_TP

def give_actors(actor : str) -> list[str] :
    """Returns the list composed of the 2 identifiants or the only
    identifiant contained in actor.

    Args:
        actor (str): text in the 'actor' column, either '<ident>/<ident>' or '<ident>/'

    Returns:
        The list containing the 1 or 2 identifiers.
    """
    actors = actor.split('/')
    if '' in actors :
        actors.remove('')
    return actors

def give_list_actors(df : pd.DataFrame) -> list[str] :
    """
    CHANGED
    Extracts a list of actors that appear in the dataframe `df` by spliting the binome.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
    
    Returns:
        list[str]: A list of unique users extracted the dataframe.
    """
    unique_actors = df['actor'].unique()
    split_actors = chain.from_iterable(give_actors(actor) for actor in unique_actors)
    return list(set(split_actors))

def give_number_of_actors(df : pd.DataFrame) -> list[str] :
    """
    Returns the number of unique actors in the given DataFrame.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing actor data.

    Returns:
        int: The number of unique actors in the DataFrame.
    """
    return len(give_list_actors(df))

def give_regex(values : list[str]) -> str :
    """
    Generates a regex pattern that matches any of the given values.
    
    Args:
        values (list[str]): A list of strings to be included in the regex pattern.
    
    Returns:
        str: A regex pattern string that matches any of the input values, separated by the '|' character.
    """

    regex = ""
    for value in values :
        regex += value + "|"
    return regex[:-1]

def _give_regex_def(values : list[str]) -> str :
    """
    Generates a regex pattern string based on the provided list of values for function.
    
    Args:
        values (list[str]): A list of strings to be included in the regex pattern.
    
    Returns:
        str: A regex pattern string where each value is separated by a pipe ('|').
            If a value does not start with '#' or '<', 'def ' is prefixed to the value.
    """

    regex = ""
    for value in values :
        if (value[0] != "#") and (value[0] != "<") :
            regex += "def "
        regex += value + "|"
    return regex[:-1]

def give_regex_wanted_values_and_unwanted_values(values_in : list[str], values_out : list[str]) -> str :
    """
    Generates a regular expression that matches strings containing all the desired values and none of the undesired values.
    
    Args:
        values_in (list[str]): A list of strings that must be present in the matched string.
        values_out (list[str]): A list of strings that must not be present in the matched string.
    
    Returns:
        str: A regular expression string that matches the criteria.
    """

    regex = "^(?=.*" + give_regex(values_in) + ")"
    for value in values_out :
        regex += "(?!.*" + value + ")"
    regex += ".*"
    return regex[:-1]

def give_list_df_by_col_value(df : pd.DataFrame, col : str, values : list[str]) -> list[pd.DataFrame] :
    """
    Splits a DataFrame into a list of DataFrames based on unique values in a specified column.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame.
        col (str): The column name to filter by.
        values (list[str]): A list of values to filter the DataFrame by.
    
    Returns:
        list[pd.DataFrame]: A list of DataFrames, each containing rows where the specified column matches one of the given values.
    """


    list = []
    for value in values :
        list.append(df[df[col].isin([value])])
    return list

def compare_dataframes(df1 : pd.DataFrame, df2 : pd.DataFrame) -> list[pd.DataFrame] :
    """
    Compare two pandas DataFrames and return a list of DataFrames containing the common rows and the remaining rows in each DataFrame.
    
    Parameters:
        df1 (pd.DataFrame): The first DataFrame to compare.
        df2 (pd.DataFrame): The second DataFrame to compare.
    
    Returns:
        list[pd.DataFrame]: A list containing three DataFrames:
            - The second DataFrame contains the remaining rows in df1 that are not in the common DataFrame.
            - The third DataFrame contains the remaining rows in df2 that are not in the common DataFrame.
            - The first DataFrame contains the common rows between df1 and df2.
    """

    common = pd.merge(df1, df2, how='inner')
    remains_df1 = df1[df1.index.isin(common.index)]
    remains_df2 = df2[df2.index.isin(common.index)]

    return [remains_df1, remains_df2, common]

def compare_dataframes_user(df1 : pd.DataFrame, df2 : pd.DataFrame) -> list[pd.DataFrame] :
    """
    This function compares two dataframes by analyzing user information. It returns a list of three dataframes:
        1. The remaining dataframe containing rows present only in first dataframe.
        2. The remaining dataframe containing rows present only in second dataframe.
        3. The common dataframe containing rows present in both dataframes.
    
    Parameters:
        df1 (pd.DataFrame): The first dataframe to compare.
        df2 (pd.DataFrame): The second dataframe to compare.
    
    Returns:
        list[pd.DataFrame]: A list containing three dataframes:
            - A dataframe of elements unique to the first dataframe.
            - A dataframe of elements unique to the second dataframe.
            - A dataframe of common elements.

    Notes:
        - This function can lost somme rows because of the bynôme in the actor column.
    """

    users = compare_list(give_list_actors(df1), give_list_actors(df2))

    common = pd.merge(df1, df2, how='outer')
    remains_common = common[common.actor.str.contains(give_regex_wanted_values_and_unwanted_values(users[2], users[0]))]
    remains_df1 = df1[df1.actor.str.contains(give_regex_wanted_values_and_unwanted_values(users[0], users[2] + users[1]))]
    remains_df2 = df2[df2.actor.str.contains(give_regex_wanted_values_and_unwanted_values(users[1], users[0] + users[2]))]

    return [remains_df1, remains_df2, remains_common]

def compare_list(list1 : list[str], list2 : list[str]) -> list[list[str]] :
    """
    Compare two lists of strings and return a list containing three lists:
        1. A list of elements that are in the first list but not in the second list.
        2. A list of elements that are in the second list but not in the first list.
        3. A list of common elements between the two input lists.
    
    Args:
        list1 (list[str]): The first list of strings to compare.
        list2 (list[str]): The second list of strings to compare.
    
    Returns:
        list[list[str]]: A list containing three lists:
            - A list of elements unique to the first list.
            - A list of elements unique to the second list.
            - A list of common elements.
    """

    common = [element for element in list1 if element in list2]
    remains_df1 = [element for element in list1 if element not in common]
    remains_df2 = [element for element in list2 if element not in common]

    return [remains_df1, remains_df2, common]

def give_df_by_files_name(df : pd.DataFrame, files_name : list[str]) -> pd.DataFrame :
    """
    Filters the given DataFrame based on a list of file names.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to filter.
        files_name (list[str]): A list of file names to filter the DataFrame by.
    
    Returns:
        pd.DataFrame: A filtered DataFrame containing only the rows where match from the provided list of file names.
    """

    regex = give_regex(files_name)
    return df[(df['filename'].str.contains(regex)) | (df['commandRan'].str.contains(regex))]

def give_list_df_by_files_name(df : pd.DataFrame, files_name : list[list[str]]) -> list[pd.DataFrame] :
    """
    Splits a DataFrame into a list of DataFrames based on a list of file names.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame to be split.
        files_name (list[list[str]]): A list of lists, where each inner list contains file names to filter the DataFrame.
    
    Returns:
        list[pd.DataFrame]: A list of DataFrames, each corresponding to the filtered data based on the provided file names.
    """

    list = []
    for files_name in files_name :
        list.append(
            give_df_by_files_name(
                df,
                files_name
            )
        )
    return list

def give_df_by_function(df : pd.DataFrame, functions : list[str]) -> pd.DataFrame :
    """
    Filters the given DataFrame based on the presence of specified functions.
    
    Args:
        df (pd.DataFrame): The input DataFrame to be filtered.
        functions (list[str]): A list of function names to filter the DataFrame by.
    
    Returns:
        pd.DataFrame: A DataFrame containing rows where the specified functions are present.
    """

    regex = _give_regex_def(functions)
    regex_ran = give_regex(functions)
    return df[
        (df['P_codeState'].str.contains(regex))
        | (df['F_codeState'].str.contains(regex))
        | (df['commandRan'].str.contains(regex_ran))
    ]

def give_list_df_by_function(df : pd.DataFrame, functions : list[list[str]]) -> list[pd.DataFrame] :
    """
    Splits a DataFrame into multiple DataFrames based on a list of functions.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame to be split.
        functions (list[list[str]]): A list of lists, where each inner list contains strings representing functions.
    
    Returns:
        list[pd.DataFrame]: A list of DataFrames where each containing rows where the specified functions are present.
    """

    list = []
    for function in functions :
        print(function)
        list.append(
            give_df_by_function(
                df,
                function
            )
        )
    return list

def give_df_by_tp(df : pd.DataFrame, index_tp : int)  -> pd.DataFrame :
    """
    Filters a DataFrame based on specific files and functions associated with a given index_tp.
    
    Args:
        df (pd.DataFrame): The input DataFrame to be filtered.
        index_tp (int): The index corresponding to the specific set of files and functions to filter by.
    
    Returns:
        pd.DataFrame: A DataFrame filtered by the specified files and functions, merged using an outer join.
    """

    functions = FUNCTIONS_BY_TP[index_tp]
    files = FILES_BY_TP[index_tp]
    df1 = give_df_by_files_name(df, files)
    df2 = give_df_by_function(df, functions)
    return pd.merge(df1, df2, how='outer')

def give_list_df_by_tp(df : pd.DataFrame, index_begin : int, index_end) -> list[pd.DataFrame] :
    """
    Generates a list of DataFrames based on specific files and functions associated with a given index functioning with a range of indices.
    
    Args:
        df (pd.DataFrame): The input DataFrame to be processed.
        index_begin (int): The starting index (inclusive) for the range.
        index_end (int): The ending index (exclusive) for the range.
    
    Returns:
        list[pd.DataFrame]: A list of DataFrames generated by applying `give_df_by_tp` to each index in the specified range.
    """
    
    list = []
    for idx in range(index_begin, index_end) :
        list.append(give_df_by_tp(df, idx))
    return list

def give_list_df_by_all_tp(df : pd.DataFrame) -> list[pd.DataFrame] :
    """
    Splits the given DataFrame into a list of DataFrames based on all tp.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame to be split.
    
    Returns:
        list[pd.DataFrame]: A list of DataFrames, each corresponding to a specific tp.
    """

    return give_list_df_by_tp(df, 0, len(FILES_BY_TP))

# Ajout fonctions avec plus de paramètres pour expérimenter de manière plus souple
# en fonction des nom de fichiers / fonctions qu'on souhaite utiliser dans l'analyse, et des expr
# régulières qu'on souhaite utiliser pour chercher les noms de fichiers / fonctions en question

# def dfs_by_all_tp(df : pd.DataFrame, filenames:list[str], fonctionnames:list[str], regex_filenames:str, regex_functionnames:str) -> list[pd.DataFrame] :
#     """
#     Splits the given DataFrame into a list of DataFrames based on all parameters.

#     Precond : filenames et fonctionnames ont la même longueur, qui est le nb
#     de TPs analysés
    
#     Parameters:
#         df (pd.DataFrame): The input DataFrame to be split.
#         filenames : liste de noms de fichiers à considérer
#         functionnames : liste de noms de fonctions à considérer
#         regex_filenames : expr régulière utilisée pour repérer les noms de fichiers
#         regex_trace_filenames : expr régulière utilisée pour repérer les <trace>...</traces> dans les codeState
#         regex_fonctionnames : expr régulière utilisée pour repérer les noms de fonctions

#     Returns:
#         list[pd.DataFrame]: A list of DataFrames, each corresponding to a specific tp.
#     """
#     return df_by_tp(df, 0, len(filenames))


# def df_by_functions(df : pd.DataFrame, functions : list[str], regexpr_codestater:str, regexpr_commandran) -> pd.DataFrame :
#     """
#     Filters the given DataFrame based on the presence of specified functions.
    
#     Args:
#         df (pd.DataFrame): The input DataFrame to be filtered.
#         functions (list[str]): A list of function names to filter the DataFrame by.
#         regexpr_codestate : expr régulière qui sert à repérer les fonctions dans les P_codeState et F_codeState
#         regexpr_commandran : expr régulière qui sert à repérer les fonctions dans les comandRan 
#     Returns:
#         pd.DataFrame: A DataFrame containing rows where the specified functions are present.
#     """
# #    regex = _give_regex_def(functions)
# #    regex_ran = give_regex(functions)
#     return df[
#         (df['P_codeState'].str.contains(regexpr_codestate))
#         | (df['F_codeState'].str.contains(regexpr_codestate))
#         | (df['commandRan'].str.contains(regexpr_commandran))
#     ]

# def df_by_filename(df : pd.DataFrame, files_name : list[str], regexpr_path:str, regexpr_codestate:str) -> pd.DataFrame :
#     """
#     Filters the given DataFrame based on a list of file names.
    
#     Parameters:
#         df (pd.DataFrame): The DataFrame to filter.
#         files_name (list[str]): A list of file names to filter the DataFrame by.
#         regexpr_path : expr reg utilisée pour repérer un nom de fichier dans un path
#         regexpr_codestate : expr reg utilisée pour repérer un <trace>... dans un codestate
    
#     Returns:
#         pd.DataFrame: A filtered DataFrame containing only the rows where match from the provided list of file names.
#     """

#     regex = give_regex(files_name)
#     # TODO ici non, on ne veut pas slt in contains, j'arrête
#     return df[(df['filename'].str.contains(regex)) | (df['commandRan'].str.contains(regex))]
