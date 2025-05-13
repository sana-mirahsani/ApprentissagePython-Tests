from datetime import date

RAW_DATA_DIR = "../data/raw/"
EXTERNAL_DATA_DIR = "../data/external/"
INTERIM_DATA_DIR = "../data/interim/"
PROCESSED_DATA_DIR = "../data/processed/"

COLUMNS_NAMES = {
        'actor.openid': 'actor',
        'verb.id':      'verb',
        'object.id':    'object',
        'context.extension.https://www.cristal.univ-lille.fr/objects/Session/ID':               'session.id',
        'object.extension.https://www.cristal.univ-lille.fr/objects/Command/CommandRan':        'commandRan',
        'object.extension.https://www.cristal.univ-lille.fr/objects/Program/CodeState':         'P_codeState',
        'result.extension.https://www.cristal.univ-lille.fr/objects/Command/stdin':             'stdin',
        'result.extension.https://www.cristal.univ-lille.fr/objects/Command/stdout' :           'stdout',
        'result.extension.https://www.cristal.univ-lille.fr/objects/Command/stderr':            'stderr',
        'object.extension.https://www.cristal.univ-lille.fr/objects/File/Filename':             'filename',
        'object.extension.https://www.cristal.univ-lille.fr/objects/File/CodeState':            'F_codeState',
        'object.extension.https://www.cristal.univ-lille.fr/objects/DocString/Function':        'function',
        'object.extension.https://www.cristal.univ-lille.fr/objects/Tests/Tests' :              'tests',
        'object.extension.https://www.cristal.univ-lille.fr/objects/Debug/TimeStampEnd' :       'Debug_TimeStampEnd',
        'object.extension.https://www.cristal.univ-lille.fr/objects/Debug/TimeStampActions' :   'Debug_TimeStampActions'
        }

# unused
UNUSED_COLUMNS = [
    #'timestamp.$date',
    'stored.$date',
    '_id.$oid',
    'actor.objectType',
    'object.objectType',
    'object.extension',
    'result',
    'object.id'
    ]

COLUMNS_FROM_OLD_PLUGIN = [
    'context.extension.https://www.cristal.univ-lille.fr/objects/Plugin',
    'object.extension.https://www.cristal.univ-lille.fr/objects/Test/TestedExpression',
    'object.extension.https://www.cristal.univ-lille.fr/objects/Test/TestedLine',
    'object.extension.https://www.cristal.univ-lille.fr/objects/Test/TestedFunction',
    'result.extension.https://www.cristal.univ-lille.fr/objects/Test/expectedResult',
    'result.extension.https://www.cristal.univ-lille.fr/objects/Test/obtainedResult'
]

VERB_NAMES = {
    'https://www.cristal.univ-lille.fr/verbs/Session.Start':      'Session.Start',
    'https://www.cristal.univ-lille.fr/verbs/Session.End':        'Session.End',
    'https://www.cristal.univ-lille.fr/verbs/File.Open':          'File.Open',
    'https://www.cristal.univ-lille.fr/verbs/File.Save':          'File.Save',
    'https://www.cristal.univ-lille.fr/verbs/Run.Program':        'Run.Program',
    'https://www.cristal.univ-lille.fr/verbs/Run.Command':        'Run.Command',
    'https://www.cristal.univ-lille.fr/verbs/Run.test':           'Run.Test',
    'https://www.cristal.univ-lille.fr/verbs/Run.Debugger' :      'Run.Debugger',
    'https://www.cristal.univ-lille.fr/verbs/Docstring.Generate': 'Docstring.Generate'
}

VERB_COLORS = {
    'Session.Start' : 'k',
    'Session.End': 'k',
    'File.Save': 'm',
    'Run.Program': 'b',
    'Run.Command': 'g',
    'Run.Test': 'r',
    'Run.Debugger': 'v',
    'Docstring.Generate': 'c'
}

SESSION_MARKERS = ['Session.Start', 'Session.End']

MANIPULATION_FILES = [
    'calcul_UE','mesure','polynomes','manipulations','erreurs_multiples','aléatoire','erreurs_cond','categories',
    'affichage','echappement','interactions_mystere','saisies_diverses', 'saison', 'saison_main', 'bandit_manchot',
    'debogueur-for','imbriquees','erreurs_boucles_while','devinette','erreurs_boucles_while_suite','erreurs_aliasing','experimentations_fichiers',
    'manip','pol','alea','categ','debog','erreur'
    ]

FEATURES_TO_KEEP_RUN_TEST = ['session.id','seance','actor','tests','timestamp.$date','nb_testables', 'nb_non_testables','noms_testables','noms_non_testables']

COLUMNS_TO_ANON = ['commandRan', 'stdin', 'stdout', 'stderr', 'filename']

RUN_VERB = ['Run.Command', 'Run.Program', 'Run.Test', 'Run.Debugger']

COLUMNS_WITH_PATH = ['filename', 'commandRan', 'stdout', 'stdin', 'stderr', 'tests']

BADVERDICT = ['ExceptionVerdict', 'FailedVerdict', 'FailedWhenExceptionExpectedVerdict']

GOODVERDICT = ['PassedVerdict', 'PassedSetupVerdict']