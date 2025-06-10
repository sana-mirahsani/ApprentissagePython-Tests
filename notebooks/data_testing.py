# will be moved to test.py
def test_filename_infere_each_week(week,df,pattern):

    total_semaine               = (df['seance'] == week).sum()
    total_empty_string_semaine  = (df[df['seance'] == week]['filename_infere'] == '').sum()
    total_nan_semaine           = df[df['seance'] == week]['filename_infere'].isna().sum()

    subset = df[(df['seance'] == week) & (df['filename_infere'] != '')]

    total_correct_name_semaine     = subset['filename_infere'].str.contains(pattern, na = False).sum()
    total_NOT_correct_name_semaine = (~ subset['filename_infere'].str.contains(pattern, na = False)).sum()

    print(f"Total number of rows in {week} : {total_semaine}")
    print(f"Total number of empty string : {total_empty_string_semaine}")
    print(f"Total number of Nan : {total_nan_semaine}")
    print(f"Total number of correct name : {total_correct_name_semaine}")
    print(f"Total number of NOT correct name : {total_NOT_correct_name_semaine}")