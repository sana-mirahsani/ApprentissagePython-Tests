#------------------------------------------------
#Added by SANA : This is Thomas's code, I didn't change it, and niether used it in of my notebooks
#------------------------------------------------
from data import cleaning
from data.constants import MANIPULATION_FILES, INTERIM_DATA_DIR, PROCESSED_DATA_DIR
#from features import tests_utils
import pandas as pd
import numpy as np
import warnings
import sys

def process_data_clean(input_file:str, output_file:str) -> None :
    '''Nettoie les traces trouvées dans <input_file>.json et les enregistre sous <output_file>.csv dans INTERIM_DATA_DIR.
        
    Args:
        input_file : préfixe du fichier json contenant les traces brutes
        output_file : préfixe du fichier csv contenant les traces nettoyées
    
    Returns: None
    '''
    cleaning.process_raw_data(input_file + ".json", output_file + ".csv")

def process_tests_dataframe(input_file, output_file) :
    '''
    Attention ici Thomas vire les Run.Test dont le filename
    indique qu'ils relève d'un exo de manipulation.
    '''
    # Charge les données
    logs = cleaning.load_clean_data(input_file + ".csv")

    # Filtrage des Run.Test
    filtre_tests = logs[logs['verb'] == 'Run.Test']

    # Récupération des index à drop
    index_to_drop = cleaning.get_indexes_of_matching_filenames(filtre_tests, MANIPULATION_FILES)
    logs_to_keep = logs.drop(index_to_drop, axis = 0)

    # Copy des Run.Test et enrichissement
    filtre_tests = logs_to_keep[logs_to_keep['verb'] == 'Run.Test']
    run_test_copy = filtre_tests.copy()

    # Catch des warnings sur la sortie standard
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', SyntaxWarning)
        # récupération des fonctions testables dans le codestate
        run_test_copy = run_test_copy.join(run_test_copy['object.extension.https://www.cristal.univ-lille.fr/objects/Program/CodeState'].apply(tests_utils.count_testables_functions))

    # Construit le DataFrame des tests
    df_tests = tests_utils.construct_DataFrame_from_all_tests(run_test_copy)

    # Ne prend que le nom de la fonction et pas la signature pour la colonne 'name'
    df_tests = tests_utils.get_fonction_name_from_signature(df_tests)

    # L'enregistre
    df_tests.to_csv("../data/interim/" + output_file + ".csv", index=False)

def generate_authorizations_csv(input_file:str, output_file:str) -> None:
    """Écrit dans PROCESSED_DATA_DIR un fichier <output_file>.csv qui contient 3 colonnes :
    - 'authorized' = les identifiants des étudiants qui sont OK pour qu'on exploite leurs données,
    - 'authorized_by_proxy' = les identifiants des étudiants dont le binôme a été OK pour qu'on exploite leurs données,
    - 'unauthorized' = les identifiants des étudiants qui ne veulent pas.

    Args:
        input_file (str): préfixe du nom du fichier csv de traces brutes
        output_file (str) : préfixe du nom du fichier csv de sortie
    """
    df : pd.DataFrame = pd.read_csv(
        INTERIM_DATA_DIR + input_file + ".csv",
        keep_default_na=False,
        dtype={'session.id': str}
    )
    all_users : [] = []
    for user in df['actor'].unique() :
        all_users += user.split('/')
    all_users = list(set(all_users))
    if '' in all_users :
        all_users.remove('')

    filtred_logs : pd.DataFrame = df[df['research_usage'] == '1.0']
    users : [] = filtred_logs['actor'].unique()
    authorized_users : [] = []
    authorized_by_proxy_users : [] = []
    for user in users :
        tmp = user.split('/')
        authorized_users.append(tmp[0])
        authorized_by_proxy_users.append(tmp[1])
    authorized_users = list(set(authorized_users))
    authorized_by_proxy_users = list(set(authorized_by_proxy_users) - set(authorized_users))
    unauthorized = list(set(all_users) - set(authorized_by_proxy_users) - set(authorized_users))
    if '' in authorized_users :
        authorized_users.remove('')
    if '' in authorized_by_proxy_users :
        authorized_by_proxy_users.remove('')
    if '' in unauthorized :
        unauthorized.remove('')

    print("nombre total d'utilisateurs : " + str(len(all_users)))
    print("nombre d'utilisateurs qui autorisent la collecte de donnees : " + str(len(authorized_users)))
    print("nombre d'utilisateurs dont l'autorisation de la collecte de donnees a ete obtenue par le binome : " + str(len(authorized_by_proxy_users)))
    print("nombre d'utilisateurs qui refusent la collecte de donnees : " + str(len(unauthorized)))

    # Fill the shorter columns with NaN values
    length = max(len(authorized_users), len(authorized_by_proxy_users), len(unauthorized))
    authorized_users += [np.nan] * (length - len(authorized_users))
    authorized_by_proxy_users += [np.nan] * (length - len(authorized_by_proxy_users))
    unauthorized += [np.nan] * (length - len(unauthorized))

    data = {'authorized': authorized_users,
            'authorized_by_proxy': authorized_by_proxy_users,
            'unauthorized': unauthorized
    }
    df_final = pd.DataFrame(data)
    df_final.to_csv(PROCESSED_DATA_DIR + output_file + ".csv", na_rep="", index=False)

def main(args) :
    nb_arg = len(args)
    if nb_arg > 2:
        init_file = args[1]
        clean_file = args[1] +  "_clean"
        research_file = args[1] + "_research"
        test_file = args[1] + "_tests_dataframe"
    elif nb_arg > 3 :
        if nb_arg != 5 :
            print("too many arguments")
            return None

        init_file = args[1]
        clean_file = args[2]
        research_file = args[3]
        test_file = args[4]

    else :
        print("no argument")
        return None

    print("Etape 1 : nettoyage")
    process_data_clean(init_file, clean_file)

    print("Etape 2 : Exclusion des données impropre à la recherche")
    cleaning.keep_research_data_only(clean_file, research_file)

    print("Etape 3 : Préparation du dataframe contenant les informations des tests unitaires")
    process_tests_dataframe(research_file, test_file)

if __name__ == '__main__':
    main(sys.argv)
