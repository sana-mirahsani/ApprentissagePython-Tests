# Les constantes de l'analyse qui varient suivant les collectes
# 02/25 PFE Thomas Briche

# Les intitulés de semaine ds leur ordre temporel
# OK pour 2425
SORTED_SEANCE =  [
    'semaine_1',
    'semaine_2',
    'semaine_3',
    'semaine_4',
    'semaine_5',
    'semaine_6',
    'semaine_7',
    'semaine_8',
    'DSi',
    'semaine_9',
    'semaine_10',
    'semaine_11',
    'semaine_12',
    'CTP'
]

# Les intitulés de TP
TP_NAME = ['Tp1', 'Tp2', 'Tp3', 'Tp4', 'Tp5','Tp6', 'Tp7', 'Tp8', 'Tp9', 'Tp10', 'Tp_game']

# les fichiers manipulés par TP, y compris ceux de manips
FILES_TP1 = ["note_UE.py", "pour_debogueur.py", "calcul_interets.py"]
FILES_TP2 = ["mesure_global.py", "mesure.py", "polynomes.py", "fonctions.py"]
FILES_TP3 = ["manipulations.py", "erreurs_multiples.py", "booleens.py"]
FILES_TP4 = ["erreurs_cond.py", "categories.py", "conditionnelles.py"]
FILES_TP5 = [
    "affichage.py",
    "echappement.py",
    "interactions_mystere.py",
    "saisies_diverses.py",
    "saison.py",
    "saison_main.py",
    "imprimerie.py",
    "jeu_421.py"
]
FILES_TP6 = ["debogueur-for.py", "iterables_for.py", "activite_range.py"]
FILES_TP7 = ["elements_consecutifs.py", "iterable_indexation.py", "configurations_init_jeu_vie.py"]
FILES_TP8 = ["erreurs_boucles_while.py", "devinette.py","while.py", "jeu_nim.py"]
FILES_TP9 = ["erreurs_boucles_while_suite.py", "parcours_interrompu.py"]
FILES_TP10 = ["erreurs_aliasing.py"]
FILES_GAME = ["tictactoe.py", "puissance4.py", "jeu_2048.py", "binairo.py", "tectonic.py", "galaxies.py"]

FILES_BY_TP = [
    FILES_TP1,
    FILES_TP2,
    FILES_TP3,
    FILES_TP4,
    FILES_TP5,
    FILES_TP6,
    FILES_TP7,
    FILES_TP8,
    FILES_TP9,
    FILES_TP10,
    FILES_GAME
]

FUNCTIONS_TP1 = [
    "# TP PROG semaine 1"
]
FUNCTIONS_TP2 = [
    "imperial2metrique\(",
    "poly1\(",
    "poly2\(",
    "repetition\(",
    "moyenne_entiere\(",
    "moyenne_entiere_ponderee\(",
    "heure2minute\(",
    "jour2heure\(",
    "en_minutes\(",
    "message\(",
    "bonbons_par_enfant\("
]
FUNCTIONS_TP3 = [
    "est_non_vide\(",
    "est_reponse\(",
    "est_beneficiaire\(",
    "est_reponse_correcte\(",
    "est_en_ete\(",
    "est_nombre_mystere\(",
    "ont_intersection_vide\(",
    "intervalle1_contient_intervalle2\(",
    "sont_intervalles_recouvrants\(",
    "est_gagnant\(",
    "est_strict_anterieure_a\(",
    "est_mineur_a_date\(",
    "est_senior_a_date\(",
    "a_tarif_reduit_a_date\(",
    "fonction1\(",
    "fonction2\(",
    "fonction3\(",
    "fonction4\(",
    "fonction5\(",
    "pred1\(",
    "pred2\(",
    "pred3\(",
    "pred4\(",
    "pred5\(",
    "pred9\("
]
# il faut trouver un autre nom pour maximum et compare
FUNCTIONS_TP4 = [
    #"maximum\(", #
    #"compare\(",
    "minimum3\(",
    "cout_location\(",
    "argminimum\(",
    "conseil_voiture\(",
    "nombre_exemplaires\(",
    "montant_facture\(",
    "calcul_gain\(",
    "est_bissextile\(",
    "est_mois_valide\(",
    "nombre_jours\(",
    "est_jour_valide\(",
    "est_date_valide\(",
    "nom_jour\(",
    "numero_jour\(",
    "categorie_tir_arc_v1\(",
    "categorie_tir_arc_v2\(",
    "categorie_tir_arc_v3\(",
    "categorie_tir_arc_v4\(",
    "mon_abs\(",
    "signe1\(",
    "signe2\(",
    "en_tete1\(",
    "int2str\(",
    "pile_ou_face1\(",
    "pile_ou_face2\("
]
FUNCTIONS_TP5 = [
    "de\(",
    "est_42\(",
    "est_421\(",
    "representation_lancer\(",
    "<trace>imprimerie.py</trace>",
    "saison\(",
    "affiche_saison\(",
    #"mystere\(",
    #"chaine\(", #
]
FUNCTIONS_TP6 = [
    "affiche_range\(",
    "compte_iterations\(",
    "saisie_caracteres\(",
    #"mystere\(",
    "mystere2\(",
    "carres\(",
    "nombre_occurrences\(",
    "nombre_occurrences2\(",
    "moyenne\(",
    "sans_elt\(",
    "positive\(",
    "chiffres\(",
    #"miroir\(",
    "compte_car\("
]
FUNCTIONS_TP7 = [
    "echantillonne\(",
    "elements_indices_impairs\(",
    #"miroir\(",
    #"minimum\(",
    "decoupage\(",
    "premieres_occurrences\(",
    "matchs\(",
    "nom_domaines\(",
    "max_identiques\(",
    "suffixes\(",
    "resume\(",
    "ajout_separateur\(",
    "construit_mots\(",
    "se_suivent\(",
    "calcule_produit_cartesien1\(",
    "calcule_produit_cartesien2\("
]
FUNCTIONS_TP8 = [
    "# Jeu de Nim",
    "compte_motif\(",
    "indice_maximum\(",
    "addition_digit\(",
    "addition\(",
    "determine\(",
    "supprime\(",
    "filtre\(",
    "nb_jours_avant_1m_blob\(",
    "somme_chiffres\(",
    "saisie_pseudo_avec_verification\(",
    "saisie_entier_intervalle\(",
    #"compare\(",
    "deviner_un_nombre\(",
    "multiplication\(",
    "saisie_reponse\(",
    "duree_atteinte_seuil\(",
    "compte_elements_identiques\(",
    "racine_entiere\("
]
FUNCTIONS_TP9 = [
    "toutes_longueurs_impaires_while\(",
    "toutes_longueurs_impaires_for\(",
    "contient_chiffre_ou_minuscule_while\(",
    "indice_positif_while\(",
    "indice_positif_for\(",
    "contient_nb_occurrences_ou_plus_while\(",
    "contient_nb_occurrences_ou_plus_for\(",
    "est_palindrome_while\(",
    "est_palindrome_for\(",
    "est_croissante_while\(",
    "est_croissante_for\(",
    "tous_differents_while\(",
    "tous_differents_for\(",
    "produit_vaut_n_while\(",
    "produit_vaut_n_for\(",
    "suffixe_somme_while\(",
    "suffixe_somme_for\(",
    "hexa_decimal",
    "decimal_hexa\(",
    "est_hexa\(",
    "hexa_binaire\(",
    "binaire_hexa\(",
    "genere_hexa\(",
    "genere_hexa_sans_begaiement\(",
    "contient_longue_chaine\(",
    "tous_entier_intervalle\(",
    "au_moins_2_oui\(",
    "contiennent_car\("
]
FUNCTIONS_TP10 = [
    "carre_1_au_centre\(",
    "affecte\("
]
FUNCTIONS_GAME = [
    "<trace>tictactoe.py</trace>",
    "<trace>puissance4.py</trace>",
    "<trace>jeu_2048.py</trace>",
    "<trace>binairo.py</trace>",
    "<trace>tectonic.py</trace>",
    "<trace>galaxies.py</trace>",
]

FUNCTIONS_BY_TP = [
    FUNCTIONS_TP1,
    FUNCTIONS_TP2,
    FUNCTIONS_TP3,
    FUNCTIONS_TP4,
    FUNCTIONS_TP5,
    FUNCTIONS_TP6,
    FUNCTIONS_TP7,
    FUNCTIONS_TP8,
    FUNCTIONS_TP9,
    FUNCTIONS_TP10,
    FUNCTIONS_GAME
]

NOMS_TP_PROGRAMMATION=[
    "fonctions.py",
    "booleens.py",
    "conditionnelles.py",
    "imprimerie.py",
    "jeu_421.py",
    "iterables_for.py",
    "iterable_indexation.py",
    "while.py",
    "jeu_nim.py",
    "parcours_interrompu.py",
] + FILES_GAME
