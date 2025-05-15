import json
import sys

# Vieux truc car l'année où Corentin a analysé les traces il y avait coexistence
# de 2  formats : le bon pour les étudiants et qques traces venant de Pierre
# Allegraud qui utilisait une vieille version de Thonny-l1test.
# Ce traitement ne devrait plus être utile. je l'ai réintégré dans cleaning

def main(input_file_name, output_file_name):
    with open('../data/raw/' + input_file_name + '.json', encoding='utf-8') as fd :
        d = json.load(fd)

    # récupère la liste des utilisateur qui possède l'attribut "Plugin" dans leur logs
    # Cet attribut sert à cerner les données issues de l'ancienne version du plugin l1test
    user_list = []
    for ind, doc in enumerate(d) :
        if 'https://www.cristal.univ-lille.fr/objects/Plugin' in doc['context']['extension'] :
            user_list += [doc['actor']['openid']]

    # On récupère ensuite les indices à supprimer
    inds_to_del = []
    for ind, doc in enumerate(d) :
        if doc['actor']['openid'] in user_list :
            inds_to_del += [ind]

    # On supprime les documents ciblés
    i = 0
    for ind in inds_to_del :
        del d[ind - i]
        i += 1

    # On re-enregistre les données
    with open('../data/raw/' + output_file_name + '.json','w') as fd :
        json.dump(d, fd)

if __name__ == "__main__" :
    match len(sys.argv):
        case 2 :
            main(sys.argv[1], sys.argv[1])

        case 3 :
            main(sys.argv[1], sys.argv[2])

        case _ :
            if len(sys.argv) > 3 :
                print("too many arguments")
            else :
                print("no argument")
