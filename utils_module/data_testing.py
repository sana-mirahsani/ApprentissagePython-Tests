# Get all total values for the dataframe
def test_filename_infere_total(df,pattern):

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
def test_filename_infere_each_week(week,df,pattern):

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
def get_number_of_empty_filename_for_week(week,df):
    verbs = ['File.Open', 'File.Save', 'Run.Test', 'Run.Debugger', 'Run.Program','Run.Command']

    for verb in verbs:
        total = ((df['verb'] == verb) & (df['filename_infere'] == '')  & (df['seance'] == week)).sum()
        print(f"Total number of emptystring for {verb} : {total}")

# Test if there are still incorrect filename_infere after removing the too short traces
def test_incorrect_names(df, week, pattern):

    # check if there is still any invalid names 
    subset = df[(df['seance'] == week) & (df['filename_infere'] != '')]
    total_invalid_names = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()
    
    if total_invalid_names == 0:
        print('There is no more invalid names, YAY!')
        return df

    else:
        print("There are still invalid names, something is wrong...")
    
    