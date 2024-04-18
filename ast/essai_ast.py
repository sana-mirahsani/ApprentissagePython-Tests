# Visitor which extracts from editor content "non testable" functions, and
# functions with no docstring, generated but not modified docstring, other
# docstring
# creation : 06/02/2024
# author : Mirabelle Nebut 

import ast

# copié de utils.py ds L1Test
# attention il faut appeler cette fonction sur les nodes de l'AST pour obtenir les noms
# de fonctions utilisés ds L1Log et exportés par L1Test
# je ne l'ai pas fait ds le visiteur d'ast ci-dessous

def create_node_representation(node:ast.AST):
    """
    Returns the node representation. Especially, returns the prototype or the signature of the node.
    This function can only construct a string representation of the supported nodes. 
    The supported nodes are reported in ASTParser.py in the global variable SUPPORTED_TYPES.
    
    Even if unsupported node is given so just it's name is returned.
    
    Args: 
        node (ast.AST): The supported node 

    Returns:
        str: Return the string represantation of a node
    """
    arg_to_exclude = lambda arg: arg in ("self", "cls")
    if isinstance(node, ast.ClassDef):
        return "%s(%s)" % (node.name, ", ".join([base.id for base in node.bases]))
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return "%s(%s)" % (node.name, ", ".join([a.arg for a in node.args.args if not arg_to_exclude(a.arg)]))
    else:
        return node.name

NAMES_TO_CHECK = ['print', 'input', 'open', 'close', 'readlines', 'readline', \
                      'write', 'read', 'randint', 'choice', 'random', 'randrange']
IMPORT_TO_CHECK = {'random' : ['randint', 'choice', 'random', 'randrange']}
NO_DOCSTRING = 'no_docstring'
GENERATED_DOCSTRING = 'generated_docstring'
STUDENT_DOCSTRING = 'student_docstring'
# WARNING : fragile. Can change with L1Test versions
# I don't know why, but the 2 \n after '$$$ ' are not returned by ast.get_dostring
DOCSTRING_PATTERN = 'à_remplacer_par_ce_que_fait_la_fonction\n\nPrécondition : \nExemple(s) :\n$$$ ' 

class NonTestableFunctions(ast.NodeVisitor):
    '''
    Non testable functions are assumed to be those that call side effects functions or
    random ones.

    The names of functions whose call made a caller function non testable are indicated in NAMES_TO_CHECK.

    Some of them belong to a module that can be named, the relation module_name-function_name is
    indicated in IMPORT_TO_CHECK.

    Without any module name, the ast node Call is as follows :
    Call(func=Name(id='print', ctx=Load()), args=[Constant(value='zert')], keywords=[])
    and the code must check the name of the function in the Name node (contained in node.id)

    With a module name, the ast node Call is as follows:
    Call(func=Attribute(value=Name(id='random', ctx=Load()), attr='choice', ctx=Load()), args=[Constant(value='abc')], keywords=[])
    and the code must check the id of the Name node (module name) and the attr of the Attribute node (function name).
    '''
    
    def __init__(self):
        super().__init__()
        # set to be built during visit
        self._non_testable_func_names = set()
        # name of function currently visited (current node or parent node)
        self._current_func_name = None
        # True if and only if the node currently visited is a Call or has a Call parent
        self._call = True
        # Contains the attr value of an Attribute, ie the name of a function call prefixed by a module name
        # ex : random.choice, attr='choice'
        self._function_name_in_attribute = None
        self._function_names = [] # all function names

    def visit_FunctionDef(self, node:ast.AST) -> None:
        docstring = ast.get_docstring(node)
        if not docstring:
            self._function_names.append((node.name, NO_DOCSTRING))
        elif docstring == DOCSTRING_PATTERN:
            self._function_names.append((node.name, GENERATED_DOCSTRING))
        else:
            self._function_names.append((node.name, STUDENT_DOCSTRING))
        self._current_func_name = node.name
        self.generic_visit(node)
        self._current_func_name = None


    def visit_Call(self, node:ast.AST) -> None:
        self._call = True
        self.generic_visit(node)
        self._call = False

    def visit_Name(self, node:ast.AST) -> None:
        if self._call and self._current_func_name and \
           (node.id in NAMES_TO_CHECK or \
            node.id in IMPORT_TO_CHECK and self._function_name_in_attribute in IMPORT_TO_CHECK[node.id]): 
            self._non_testable_func_names.add(self._current_func_name)
        self.generic_visit(node)


    def visit_Attribute(self, node:ast.AST) -> None:
        if self._call and self._current_func_name:
            self._function_name_in_attribute = node.attr
        self.generic_visit(node)
        self._function_name_in_attribute = None
        
def visit(editor_content:str) -> tuple[list,set]:
    '''Returns a tuple of the names of all functions then the set of names of
    non testable functions contained in editor_content.

    Names of tested functions can be retrieved from L1test export to
    L1log. Hence the name of untested functions (_function_names -
    _tested_functions_names).
    '''
    visitor = NonTestableFunctions()
    module = ast.parse(editor_content, mode='exec') # ast.Module
    visitor.visit(module)
    return (visitor._function_names, visitor._non_testable_func_names)
