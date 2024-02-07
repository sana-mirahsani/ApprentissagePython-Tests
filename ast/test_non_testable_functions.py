# Tests for visitor which extracts from editor content "non testable"
# functions, and functions with no docstring, generated but not
# modified docstring, other docstring
# creation : 06/02/2024 
# author : Mirabelle Nebut

import unittest
from essai_ast import visit
from essai_ast import GENERATED_DOCSTRING, NO_DOCSTRING, STUDENT_DOCSTRING

SOURCE = '''import math
def incr(x : int) -> int:
    """x_résumé_x

    Paramètres :
    - x (int) : 
    Valeur de retour () :
    Contraintes d'utilisation : 
    Exemples :
    $$$ incr(3)
    4
    $$$ incr(5)
    7
    $$$ incr(8)/0
    9
    $$$ x = 12
    """
    res = math.sqrt(x + 1)
    return res

def sans_test_avec_docstring_generee():
    """à_remplacer_par_ce_que_fait_la_fonction

    Précondition : 
    Exemple(s) :
    $$$ 

    """
    pass

def sans_test_avec_docstring_modifiee(x:int)-> str:
    """Renvoie str(x).

    Précondition : 
    Exemple(s) :
    $$$ 

    """
    return str(x)

import random
def pas_testable1() -> str:
    x = random.choice('abc')
    return x + '!'

from random import randint
def pas_testable2() -> int:
    return randint(0,5) + 12

def pas_testable3() -> None:
    print("zert")

from random import choice
def pas_testable4() -> str:
    x = choice('zert')
    y = choice('rdtfgh')
    return x + y

# ast.get_docstring contient None
def doc_mal_placee():
    x = 3
    """
    blablabla
    """
    return x

print("lalalala !")

def foo(x : int) -> int:
    return x + 1

if __name__ == '__main__':
    """à_remplacer_par_ce_que_fait_la_fonction

    Précondition : 
    Exemple(s) :
    $$$ 

    """
    print('coucou')

def after_main(y : str) -> str:
    """à_remplacer_par_ce_que_fait_la_fonction

    Précondition : 
    Exemple(s) :
    $$$ 

    """
    return y + ' '

def pas_testable5(nom_fichier:str) -> str:
    with open(nom_fichier, 'r') as f:
        tout = f.read()
    return tout

def pas_testable6() -> str:
    return input('entrer n"importe quoi :')

def bar(x : int, y : int) -> int:
    """ affreux mais testable"""
    print = x + y
    return print
'''



class TestNonTestableFunctions(unittest.TestCase):

    def test_untestable_func_names(self):
        _, untestable_func_names  = visit(SOURCE)
        self.assertEqual(untestable_func_names, {'pas_testable1', 'pas_testable2', 'pas_testable3', 'pas_testable4', 'pas_testable5', 'pas_testable6'})


    def test_func_names(self):
        func_names, _   = visit(SOURCE)
        self.assertEqual(func_names, \
                         [('incr', STUDENT_DOCSTRING),\
                          ('sans_test_avec_docstring_generee', GENERATED_DOCSTRING), \
                          ('sans_test_avec_docstring_modifiee', STUDENT_DOCSTRING), \
                          ('pas_testable1', NO_DOCSTRING), \
                          ('pas_testable2', NO_DOCSTRING), \
                          ('pas_testable3', NO_DOCSTRING), \
                          ('pas_testable4', NO_DOCSTRING), \
                          ('doc_mal_placee', NO_DOCSTRING), \
                          ('foo', NO_DOCSTRING), \
                          ('after_main', GENERATED_DOCSTRING), \
                          ('pas_testable5', NO_DOCSTRING), \
                          ('pas_testable6', NO_DOCSTRING), \
                          ('bar', STUDENT_DOCSTRING)])
