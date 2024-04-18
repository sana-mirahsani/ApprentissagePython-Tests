# Visitor which compares 2 editor contents and indicates for each
# function if it it was added, deleted, modified for tests, modified
# for code, modified for signture,  both of them, not modified at all,
# or other.
# Ex of "other" : a comment appears near the signature
# If the docstring was modified : use informations sent by L1test to
# check if tests were modified.
# author : Mirabelle Nebut, avril 2024

import ast

# status of functions in the 2nd editor content
DELETED = 'deleted'
APPEARED = 'appeared'
MODIFIED_DOCSTRING = 'modified_docstring'
MODIFIED_BODY = 'modified_body'
MODIFIED_SIGNATURE = 'modified_signature'
NOT_MODIFIED = 'not_modified'
MODIFIED_OTHER = 'modified_other'


class DescrFunction(ast.NodeVisitor):
    '''
    Visitor for the first editor content : collects for each function its
    text (from def to end), its ast node and its docstring if ever.

    No recursive visit so does not work for functions defined into functions.
    '''
    
    def __init__(self, source:str):
        super().__init__()
        self.source = source
        # dict func_names -> (text, ast, docstring)
        self._func_descr = {}

    def visit_FunctionDef(self, node) -> None:
        '''
        Sets a dictionary that associates to each function name a
        description of the function.
        '''
        func_text = ast.get_source_segment(self.source, node) # text
        doc = ast.get_docstring(node) # docstring
        self._func_descr[node.name] = (func_text, node, ast.get_docstring(node))


class DiffOnFunctions(ast.NodeVisitor):
    '''
    Visitor for the second editor content : collects for each function its
    text (from def to end), its ast node and its docstring if ever.

    No recursive visit so does not work for functions defined into functions.
    '''
    
    def __init__(self, source:str, func_descr:dict):
        super().__init__()
        self.func_descr = func_descr
        self.source = source
        # dict func_names -> status to be built during visit
        self._func_status = {}
        
    def visit_FunctionDef(self, node2) -> None:
        '''
        Visits the node and sets the status of the function in the set
        {APPEARED, NOT_MODIFIED, MODIFIED_SIGNATURE, MODIFIED_DOCSTRING, MODIFIED_BODY, MODIFIED_OTHER}.

        The status DELETED is not computed here.
        '''
        if node2.name not in self.func_descr:
            self._func_status[node2.name] = {APPEARED}
        else:
            (func_text1, node1, doc1) = self.func_descr[node2.name]
            func_text2 = ast.get_source_segment(self.source, node2)
            if func_text1 == func_text2:
                self._func_status[node2.name] = {NOT_MODIFIED}
            else: # modif in doc, body or signature, or both ?
                modif_found = False
                if not are_signatures_equal(node1, node2):
                    _add_to_dict(self._func_status, node2.name, MODIFIED_SIGNATURE)
                    modif_found = True
                if ast.get_docstring(node2) != doc1:
                    _add_to_dict(self._func_status, node2.name, MODIFIED_DOCSTRING)
                    modif_found = True
                if not are_stmts_equal(node1, node2):
                    _add_to_dict(self._func_status, node2.name, MODIFIED_BODY)
                    modif_found = True
                if not modif_found:
                    self._func_status[node2.name] = {MODIFIED_OTHER}

def _add_to_dict(d:dict, k:str, v:any) -> None:
    '''
    Adds (k, v) to d. If the k key exists in d, adds v to values.
    precond : values in d are sets. 
    '''
    if k in d:
        values = d[k] | {v}
        d[k] = values
    else:
        d[k] = {v}

def are_signatures_equal(func1:ast.FunctionDef, func2:ast.FunctionDef) -> bool:
    '''
    Equality if same arguments name with same annotations types in the same order, including same return type annotation.

    Cf tests !
    '''
    # FunctionDef contains args, which themselves contain args (list)
    arguments1 = func1.args
    arguments2 = func2.args
    if len(arguments1.args) != len(arguments2.args): # number of parameters
        return False
    # returns.id contains the annotation type for the result
    if func1.returns != None and func2.returns != None and func1.returns.id != func2.returns.id:
        return False
    if func1.returns == None and func2.returns != None or func1.returns != None and func2.returns == None:
        return False
    # args contain arg : the name of the parameter
    # annotation.id contains the annotation type    
    args= zip(arguments1.args, arguments2.args)
    for arg1, arg2 in args:
        if arg1.arg != arg2.arg or arg1.annotation.id != arg2.annotation.id:
            return False
    return True

def are_stmts_equal(func1:ast.FunctionDef, func2:ast.FunctionDef) -> bool:
    '''
    Returns True if statements (body without docstring) of functions in
    func1 and func2 are equals.

    Uses ast.unparse to converse ast.Body into str. Ugly but not other idea. 
    Hence if the bodies are not strictly equals in the str sense 
    (eg different spaces) but the ast are similar, result is MODIFIED_OTHER. 
    '''
    body1 = func1.body
    body2 = func2.body
    docstring1 = ast.get_docstring(func1)
    # if a docstring is present, func.body is a list with
    # the dosctring at position 0 then other instructions at greater
    # positions
    if docstring1:
        without_doc1 = body1[1:]
        stmt_text1 = list(ast.unparse(stmt) for stmt in without_doc1)
    else:
        stmt_text1 = list(ast.unparse(stmt) for stmt in body1)
    docstring2 = ast.get_docstring(func2)
    if docstring2:
        without_doc2 = body2[1:]
        stmt_text2 = list(ast.unparse(stmt) for stmt in without_doc2)
    else:
        stmt_text2 = list(ast.unparse(stmt) for stmt in body2)
    return stmt_text1 == stmt_text2
    
                    
def compare_func(editor_content1:str, editor_content2:str) -> dict:
    '''
    Compares editor_content1 with editor_content2, returns  a
    dict which associates a set included in {APPEARED, NOT_MODIFIED, 
    MODIFIED_SIGNATURE, MODIFIED_DOCSTRING, MODIFIED_BODY, MODIFIED_OTHER,
    DELETED} to function names collected in editor_content1 U editor_content2.

    '''
    visitor1 = DescrFunction(editor_content1)
    module1:ast.Module = ast.parse(editor_content1, mode='exec')
    visitor1.visit(module1)
    func_descr1 = visitor1._func_descr

    visitor2 = DiffOnFunctions(editor_content2, func_descr1)
    module2:ast.Module = ast.parse(editor_content2, mode='exec')
    visitor2.visit(module2)
    func_descr2 = visitor2._func_status 
    
    # case of DELETED functions
    missing_func = func_descr1.keys() - func_descr2.keys()
    for name in missing_func:
        func_descr2[name] = {DELETED}
    return func_descr2
