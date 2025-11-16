LBL_NB_ETUD = 'Nb étud'
LBL_NB_DEB = 'Nb débutants'
LBL_NB_NON_DEB = 'Nb non débutants'
LBL_NB_ETUD_ANALYSABLE = 'Nb étud analyse possible'
LBL_NB_ETUD_NON_ANALYSABLE = 'Nb étud analyse impossible'
LBL_NB_DEB_ANALYSABLE = 'Nb déb analyse possible'
LBL_NB_DEB_NON_ANALYSABLE = 'Nb déb analyse impossible'
LBL_NB_NON_DEB_ANALYSABLE = 'Nb non déb analyse possible'
LBL_NB_NON_DEB_NON_ANALYSABLE = 'Nb non déb analyse impossible'
LBL_PCT_DEB_NON_ANALYSABLE = 'Pourcentage débutants analyse impossible (an impossible)'
LBL_NB_ETUD_TESTS_PRESENTS = 'Nb étud avec tests présents'
LBL_NB_DEB_TESTS_PRESENTS = 'Nb débutants avec tests présents'
LBL_NB_NON_DEB_TESTS_PRESENTS = 'Nb non débutants avec tests présents'
LBL_PCT_TESTS_PRESENTS = 'Pourcentage avec tests présents (analyse possible)'
LBL_PCT_DEB_TESTS_PRESENTS = 'Pourcentage débutants avec tests présents (débutants an possible)'
LBL_PCT_NON_DEB_TESTS_PRESENTS = 'Pourcentage non débutants avec tests présents (non débutants an possible)'
LBL_NB_ETUD_TESTS_PRESENTS_TTES_FCTS = 'Nb étud avec tests présents pour toute fonction écrite'
LBL_NB_DEB_TESTS_PRESENTS_TTES_FCTS = 'Nb débutants avec tests présents pour toute fonction écrite'
LBL_NB_NON_DEB_TESTS_PRESENTS_TTES_FCTS = 'Nb non débutants avec tests présents pour toute fonction écrite'
LBL_PCT_TTES_FCTS = 'Pourcentage pour toute fonction (travaux analysables)'
LBL_PCT_TTES_FCTS_DEB = 'Pourcentage débutants avec tests présents pour toute fonction (déb travaux analysables)'
LBL_PCT_TTES_FCTS_NON_DEB = 'Pourcentage non débutants avec tests présents pour toute fonction (non déb travaux analysables)'
LBL_NB_ETUD_NO_TEST = 'Nb étud sans test'
LBL_NB_DEB_NO_TEST = 'Nb débutants sans test'
LBL_NB_NON_DEB_NO_TEST = 'Nb non débutants sans test'
LBL_PCT_DEB_NO_TEST = 'Pourcentage débutants sans test (déb travaux analysables)'
LBL_PCT_NON_DEB_NO_TEST = 'Pourcentage non débutants sans test (non déb travaux analysables)'
NB_ETUD_TESTS_QQ_FONCTIONS = 'Nb étud avec tests présents pour qq fonctions écrites'

COLUMNS_STAT_ECR_TESTS = ['Tps',
                          LBL_NB_ETUD,
                          LBL_NB_DEB,
                          LBL_NB_NON_DEB,
                          LBL_NB_ETUD_ANALYSABLE,
                          LBL_NB_ETUD_NON_ANALYSABLE,
                          LBL_NB_DEB_ANALYSABLE,
                          LBL_NB_DEB_NON_ANALYSABLE,
                          LBL_NB_NON_DEB_ANALYSABLE,
                          LBL_NB_NON_DEB_NON_ANALYSABLE,
                          LBL_PCT_DEB_NON_ANALYSABLE,
                          LBL_NB_ETUD_TESTS_PRESENTS,
                          LBL_NB_DEB_TESTS_PRESENTS,
                          LBL_NB_NON_DEB_TESTS_PRESENTS,
                          LBL_PCT_TESTS_PRESENTS,
                          LBL_PCT_DEB_TESTS_PRESENT,
                          LBL_PCT_NON_DEB_TESTS_PRESENTS,
                          LBL_NB_ETUD_TESTS_PRESENTS_TTES_FCTS,
                          LBL_NB_DEB_TESTS_PRESENTS_TTES_FCTS,
                          LBL_NB_NON_DEB_TESTS_PRESENTS_TTES_FCTS,
                          LBL_PCT_TTES_FCTS,
                          LBL_PCT_TTES_FCTS_DEB,
                          LBL_PCT_TTES_FCTS_NON_DEB,
                          LBL_NB_ETUD_NO_TEST,
                          LBL_NB_DEB_NO_TEST,
                          LBL_NB_NON_DEB_NO_TEST,
                          LBL_PCT_DEB_NO_TEST,
                          LBL_PCT_NON_DEB_NO_TEST,
                          NB_ETUD_TESTS_QQ_FONCTIONS
    ]

def genere_donnees_nombre_tests_ecrits_tp_guides(df:pd.DataFrame, functions_names:dict, df_is_deb:pd.DataFrame) -> pd.DataFrame:
    """
    Renvoie un DataFrame avec colonnes : 'Tps', 'Nb etud', 'Nb etud analyse impossible', 'Nb etud avec tests présents', 'Nb etud avec tests présents pour toute fonction écrite', \
                                    'Nb etud avec aucun test', 'Nb etud avec tests présents pour qq fonctions écrites'

    Args :
        - df : df initial
        - function_names : dico which associates to each Tp identifier a list of functions name (ex : functions_names['Tp2] is ['foo1', 'foo2', 'foo3'])
        - df_is_deb : columns 'actor' et 'debutant'
    """
    df_plot = pd.DataFrame(columns=COLUMNS_STAT_ECR_TESTS)            
                            
    for tp in TPS_SANS_SEM_5:
        if tp == 'Tp8':
            df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp  = find_tests_for_tp_tpprog(df, 'Tp8', functions_names, filename='while.py')
            actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == 'while.py')]['actor']
            column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog') & (df['filename_infere'] == 'while.py')]['binome'] 
        else:
            df_tests_tp, cannot_analyze_codestate_students_tp, empty_codestate_students_tp  = find_tests_for_tp_tpprog(df, tp, functions_names)
            actor_column_tp  = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['actor']
            column_binome_tp = df[(df['TP'] == tp) & (df['Type_TP'] == 'TP_prog')]['binome']
        all_students_tp  = set(actor_column_tp).union(set(column_binome_tp))
        deb_students_tp = select_debutants(all_students_tp, df_is_deb)
        non_deb_students_tp = list(all_students_tp - set(deb_students_tp))
        if '' in all_students_tp:
            all_students_tp.remove('')
        df_tests_tp_avec_deb = merge_debutant(df_tests_tp, df_is_deb)
        etud_testant_toute_fonction_ecrite_tp, etud_testant_aucune_fonction_ecrite_tp, etud_qq_tests_fonction_ecrite_tp, \
            etud_deb_testant_toute_fonction_ecrite_tp, etud_deb_testant_aucune_fonction_ecrite_tp, etud_deb_qq_tests_fonction_ecrite_tp \
                = actors_par_pratique_ecriture_tests(df_tests_tp_avec_deb)
        assert(set(etud_deb_testant_toute_fonction_ecrite_tp) == set(select_debutants(etud_testant_toute_fonction_ecrite_tp, df_is_deb)))
        etud_non_deb_testant_aucune_fonction_ecrite_tp = list(set(etud_testant_aucune_fonction_ecrite_tp) - set(etud_deb_testant_aucune_fonction_ecrite_tp))
        etud_non_deb_testant_toute_fonction_ecrite_tp = list(set(etud_testant_toute_fonction_ecrite_tp) - set(etud_deb_testant_toute_fonction_ecrite_tp))
        etud_analyse_impossible = cannot_analyze_codestate_students_tp + empty_codestate_students_tp
        etud_analyse_possible = list(set(all_students_tp) - set(etud_analyse_impossible))
        etud_deb_analyse_impossible:list = select_debutants(etud_analyse_impossible, df_is_deb)
        etud_non_deb_analyse_impossible:list = list(set(etud_analyse_impossible) - set(etud_deb_analyse_impossible))
        etud_deb_analyse_possible:list = list(set(deb_students_tp) - set(etud_deb_analyse_impossible))
        etud_non_deb_analyse_possible:list = list(set(non_deb_students_tp) - set(etud_non_deb_analyse_impossible))
        etud_avec_tests:list = etud_testant_toute_fonction_ecrite_tp + etud_qq_tests_fonction_ecrite_tp
        etud_deb_avec_tests:list = select_debutants(etud_avec_tests, df_is_deb)
        etud_non_deb_avec_tests:list = list(set(etud_avec_tests) - set(etud_deb_avec_tests))
        df_plot_tp = pd.DataFrame({
            'Tps': [tp],\
            LBL_NB_ETUD: len(all_students_tp),\
            LBL_NB_DEB: len(deb_students_tp),\
            LBL_NB_NON_DEB: len(non_deb_students_tp),\
            LBL_NB_ETUD_ANALYSABLE: len(etud_analyse_possible),\
            LBL_NB_DEB_ANALYSABLE: len(etud_deb_analyse_possible),\
            LBL_NB_NON_DEB_ANALYSABLE: len(etud_non_deb_analyse_possible),\
            LBL_NB_ETUD_NON_ANALYSABLE: len(etud_analyse_impossible),\
            LBL_PCT_DEB_NON_ANALYSABLE: len(etud_deb_analyse_impossible)/len(etud_analyse_impossible)*100,\
            LBL_NB_ETUD_TESTS_PRESENTS: len(etud_avec_tests),\
            LBL_NB_DEB_TESTS_PRESENTS: len(etud_deb_avec_tests), \
            LBL_NB_NON_DEB_TESTS_PRESENTS: len(etud_avec_tests) - len(etud_deb_avec_tests),\
            LBL_PCT_TESTS_PRESENTS: len(etud_avec_tests)/len(etud_analyse_possible)*100,\
            LBL_PCT_DEB_TESTS_PRESENTS: len(etud_deb_avec_tests)/len(etud_deb_analyse_possible)*100,\
            LBL_PCT_NON_DEB_TESTS_PRESENTS: len(etud_non_deb_avec_tests)/len(etud_non_deb_analyse_possible)*100,\
            LBL_NB_ETUD_TESTS_PRESENTS_TTES_FCTS: len(etud_testant_toute_fonction_ecrite_tp),\
            LBL_NB_DEB_TESTS_PRESENTS_TTES_FCTS: len(etud_deb_testant_toute_fonction_ecrite_tp),\
            LBL_NB_NON_DEB_TESTS_PRESENTS_TTES_FCTS: len(etud_non_deb_testant_toute_fonction_ecrite_tp),\
            LBL_PCT_TTES_FCTS: len(etud_testant_toute_fonction_ecrite_tp)/len(etud_analyse_possible)*100,\
            LBL_PCT_TTES_FCTS_DEB: len(etud_deb_testant_toute_fonction_ecrite_tp)/len(etud_deb_analyse_possible)*100,\
            LBL_PCT_TTES_FCTS_DEB: len(etud_non_deb_testant_toute_fonction_ecrite_tp)/len(etud_non_deb_analyse_possible)*100,\
            LBL_NB_ETUD_NO_TEST: len(etud_testant_aucune_fonction_ecrite_tp),\
            LBL_NB_DEB_NO_TEST: len(etud_deb_testant_aucune_fonction_ecrite_tp),\
            LBL_NB_NON_DEB_NO_TEST: len(etud_non_deb_testant_aucune_fonction_ecrite_tp),\
            LBL_PCT_DEB_NO_TEST: len(etud_deb_testant_aucune_fonction_ecrite_tp)/len(etud_deb_analyse_possible)*100,\
            LBL_PCT_NON_DEB_NO_TEST: len(etud_non_deb_testant_aucune_fonction_ecrite_tp)/len(etud_non_deb_analyse_possible)*100,\
            NB_ETUD_TESTS_QQ_FONCTIONS : len(etud_qq_tests_fonction_ecrite_tp)
                                  })
        df_plot = pd.concat([df_plot, df_plot_tp], ignore_index=True)
    return df_plot
