"""
Abstract base class for all statement types in Lox. Defines the structure for statement execution. Subclasses 
(Expression, Print, Var, Block, If, While, Function, Return, etc.) Represent specific types of statements. 
Each subclass defines the structure and execution logic for its type of statement, such as variable declarations, 
control flow constructs, and function definitions.
"""

from Expr import Expr, Variable
from Token import Token
from typing import Generic, TypeVar, List

# Defines a generic type variable R for return types.
R = TypeVar("R")  

# Base class for all statement types.
class Stmt:  
    def __init__(self):
        pass

# Generic visitor class for implementing visitor pattern.
class Visitor(Generic[R]):  
    def __init__(self):
        pass 

# Maps statement types to their attributes for dynamic class generation.
subclasses = {
    "Block": {"statements": "List[Stmt]"},
    "Expression": {"expression": "Expr"},
    "Function": {"name": "Token", "params": "List[Token]", "body": "List[Stmt]"},
    "Class": {"name": "Token", "superclass": "Variable", "methods": "List[Function]"},
    "If": {"condition": "Expr", "then_branch": "Stmt", "else_branch": "Stmt"},
    "Print": {"expression": "Expr"},
    "Return": {"keyword": "Token", "value": "Expr"},
    "Var": {"name": "Token", "initializer": "Expr"},
    "While": {"condition": "Expr", "body": "Stmt"},
}

# Iterate through statement types and dynamically create classes.
for name, attributes in subclasses.items():  
    args = ""  # Initialises argument string for constructor signature.
    instance_init = ""  # Initialises instance variable assignment code.
    for arg, arg_type in attributes.items():  # Builds constructor argument string.
        args += f", {arg}: {arg_type}"

    subclass_str = ""  # Initialises the string to hold the class definition code.
    subclass_str += f"class {name}(Stmt):\n"  # Starts class definition.
    subclass_str += f"    def __init__(self{args}):\n"  # Adds constructor signature.

    for arg in attributes:  # Adds code to assign instance variables.
        subclass_str += f"        self.{arg} = {arg}\n"

    subclass_str += "\n"
    subclass_str += "    def accept(self, visitor: Visitor[R]):\n"  # Adds accept method for visitor pattern.
    subclass_str += f"        return visitor.visit_{name.lower()}_stmt(self)\n"

    exec(subclass_str, globals())  # Dynamically executes the class definition code in the global namespace.
