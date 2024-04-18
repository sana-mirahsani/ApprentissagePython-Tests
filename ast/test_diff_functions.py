import unittest
import ast
from diff_functions import compare_func, are_signatures_equal, are_stmts_equal
from diff_functions import DELETED, APPEARED, MODIFIED_DOCSTRING, NOT_MODIFIED, MODIFIED_BODY, MODIFIED_OTHER

SOURCE1 = '''def disparaitra(x:int)->int:
   """
   Blablabla
   $$$ disparaitra(3)
   3
   """
   return x

def modif_code(x:int)->int:
   """
   Blablabla
   $$$ modif_code(4)
   5
   $$$ modif_code(5)
   0
   """
   return x+1

def disparaitra2(x:int)->int:
   """
   Blablabla
   $$$ disparaitra2(3)
   3
   """
   return x

def modif_signature(x:int)->int:
   """
   Blablabla
   $$$ modif_signature(4, 1)
   5
   $$$ modif_signature(5, -5)
   0
   """
   return x+y

def modif_doc(x:int)->int:
   """
   Blablabla
   $$$ modif_doc(4)
   5
   $$$ modif_doc(5)
   0   
   """
   return x+1

def sans_modif(x:int)->int:
   """
   Blablabla
   $$$ sans_modif(4)
   5
   $$$ sans_modif(5)
   0   
   """
   return x+1
'''

SOURCE2 = '''def apparue(x:int)->int:
   """
   Blablabla
   $$$ apparue(3)
   3
   """
   return x

def modif_code(x:int)->int:
   """
   Blablabla
   $$$ modif_code(4)
   5
   $$$ modif_code(5)
   0
   """
   return x+2

def modif_signature(x:int,y:int)->int:
   """
   Blablabla
   $$$ modif_signature(4, 1)
   5
   $$$ modif_signature(5, -5)
   0
   """
   return x+y

def modif_doc(x:int)->int:
   """
   Blablabla
   $$$ modif_doc(4)
   5
   $$$ modif_doc(5)
   6   
   """
   return x+1

def apparue2(x:int)->int:
   """
   Blablabla
   $$$ apparue(3)
   3
   """
   return x

def sans_modif(x:int)->int:
   """
   Blablabla
   $$$ sans_modif(4)
   5
   $$$ sans_modif(5)
   0   
   """
   return x+1
'''

class TestDiffOnFunctions(unittest.TestCase):

    def test_functions_names(self):
        diff_functions = compare_func(SOURCE1, SOURCE2)
        self.assertEqual(set(diff_functions.keys()), {'disparaitra', 'disparaitra2', 'modif_code', 'modif_signature', 'modif_doc', 'sans_modif', 'apparue', 'apparue2'} )

    def test_functions_deleted(self):
        diff_functions = compare_func(SOURCE1, SOURCE2)
        status1 = diff_functions['disparaitra']
        status2 = diff_functions['disparaitra2']
        self.assertEqual(status1, {DELETED})
        self.assertEqual(status2, {DELETED})

    def test_functions_appeared(self):
        diff_functions = compare_func(SOURCE1, SOURCE2)
        status1 = diff_functions['apparue']
        status2 = diff_functions['apparue2']
        self.assertEqual(status1, {APPEARED})
        self.assertEqual(status2, {APPEARED})

    def test_functions_modified_docstring(self):
        diff_functions = compare_func(SOURCE1, SOURCE2)
        status = diff_functions['modif_doc']
        self.assertEqual(status, {MODIFIED_DOCSTRING})

    def test_functions_not_modified(self):
        diff_functions = compare_func(SOURCE1, SOURCE2)
        status = diff_functions['sans_modif']
        self.assertEqual(status, {NOT_MODIFIED})

    def test_functions_modified_body(self):
        diff_functions = compare_func(SOURCE1, SOURCE2)
        status = diff_functions['modif_code']
        self.assertEqual(status, {MODIFIED_BODY})

    def test_function_modified_docstring_body(self):
        SOURCE1 = '''def foo(x:int)->int:
   """booh !"""
   y = 3
   z = 4
   return x + y + z
   '''
        SOURCE2 = '''def foo(x:int)-> int:
   """quoi encore ?"""
   return x + 7
   '''
        diff_functions = compare_func(SOURCE1, SOURCE2)
        self.assertEqual(diff_functions.keys(), {'foo'})
        status = diff_functions['foo']
        self.assertEqual(status, {MODIFIED_BODY, MODIFIED_DOCSTRING})

    def test_function_with_other_modification(self):
        SOURCE1 = '''def foo(x:int)->int:
   """booh !"""
   y = 3
   z = 4
   return x + y + z
   '''
        SOURCE2 = '''def foo(x:int)->int:
   # TODO
   """booh !"""
   y = 3
   z = 4
   return x + y + z
   '''
        diff_functions = compare_func(SOURCE1, SOURCE2)
        self.assertEqual(diff_functions.keys(), {'foo'})
        status = diff_functions['foo']
        self.assertEqual(status, {MODIFIED_OTHER})

    def test_function_with_different_spaces(self):
        SOURCE1 = '''def foo(x:int)->int:
   """booh !"""
   y =    3
   z =    4
   return x+y+z
   '''
        SOURCE2 = '''def foo(x:int)->int:
   """booh !"""
   y = 3
   z = 4
   return x + y + z
   '''
        diff_functions = compare_func(SOURCE1, SOURCE2)
        self.assertEqual(diff_functions.keys(), {'foo'})
        status = diff_functions['foo']
        self.assertEqual(status, {MODIFIED_OTHER})
        
class TestSignatureEquality(unittest.TestCase):

    def test_distinct_arg_number(self):
        DEF1 = '''def foo(x:int)->int:
   """booh !"""
   return x
   '''
        DEF2 = '''def foo(x:int, y:int)-> int:
   return x + Y
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertFalse(are_signatures_equal(func1, func2))
        
    def test_distinct_arg_name(self):
        DEF1 = '''def foo(x:int,y:int)->int:
   return x + y
   '''
        DEF2 = '''def foo(x:int, z:int)-> int:
   return x + z
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertFalse(are_signatures_equal(func1, func2))

    def test_distinct_annotation_type_for_parameter(self):
        DEF1 = '''def foo(x:int,y:float)->int:
   return x + y
   '''
        DEF2 = '''def foo(x:int, z:int)-> int:
   return x + z
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertFalse(are_signatures_equal(func1, func2))

    def test_distinct_annotation_type_for_return(self):
        DEF1 = '''def foo(x:int,y:int)->bool:
   return x + y != 4
   '''
        DEF2 = '''def foo(x:int, y:int)-> int:
   return x + y
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertFalse(are_signatures_equal(func1, func2))

    def test_distinct_order_for_parameters(self):
        DEF1 = '''def foo(x:int,y:int)->int:
   return x + y 
   '''
        DEF2 = '''def foo(y:int, x:int)-> int:
   return x + y
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertFalse(are_signatures_equal(func1, func2))
        
        
    def test_same_signature(self):
        DEF1 = '''def foo(x:int,     z:int)->int:
   return x + z
   '''
        DEF2 = '''def foo(x:int, z:int)-> int:
   return x + z
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertTrue(are_signatures_equal(func1, func2))

    def test_same_signature_but_comments(self):
        DEF1 = '''def foo(x:int,     z:int)->int: # haha!
   return x + z
   '''
        DEF2 = '''def foo(x:int, z:int)-> int:
   return x + z
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertTrue(are_signatures_equal(func1, func2))

        
    def test_no_return_type(self):
        DEF1 = '''def foo(x:int,     z:int):
   return x + z
   '''
        DEF2 = '''def foo(x:int, z:int)-> int:
   return x + z
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertFalse(are_signatures_equal(func1, func2))

class TestBodyEquality(unittest.TestCase):

    def test_no_docstring(self):
        DEF1 = '''def foo(x:int,     z:int):
   return x + z
   '''
        DEF2 = '''def foo(x:int, z:int)-> int:
   return x + z
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertTrue(are_stmts_equal(func1, func2))
        

    def test_two_docstrings(self):
        DEF1 = '''def foo(x:int,     z:int):
   """a\nb
   c  
        z
   """
   4 == 3
   return x + z
   '''
        DEF2 = '''def foo(x:int, z:int)-> int:
   """jfhdg
   zqesrdgtfhj
   """
   4 == 3
   return x + z
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertTrue(are_stmts_equal(func1, func2))


    def test_one_docstring(self):
        DEF1 = '''def foo(x:int,     z:int):
   """a\nb
   c     
   """
   4 == 3
   return x + z
   '''
        DEF2 = '''def foo(x:int, z:int)-> int:
   4 == 3
   return x + z
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertTrue(are_stmts_equal(func1, func2))

    def test_marchait_pas(self):
        DEF1 = '''def modif_code(x:int)->int:
   """
   Blablabla
   $$$ modif_code(4)
   5
   $$$ modif_code(5)
   0
   """
   return x+1

   '''
        DEF2 = '''def modif_code(x:int)->int:
   """
   Blablabla
   $$$ modif_code(4)
   5
   $$$ modif_code(5)
   0
   """
   return x+2
   '''
        module1 = ast.parse(DEF1, mode='exec')
        module2 = ast.parse(DEF2, mode='exec')
        func1 = module1.body[0]
        func2 = module2.body[0]
        self.assertFalse(are_stmts_equal(func1, func2))
