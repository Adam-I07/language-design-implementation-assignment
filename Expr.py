"""
Abstract base class for all expression types. Defines the structure for expression evaluation.
Subclasses (Binary, Grouping, Literal, Unary, Variable, etc.) Description: Represent specific types of expressions.
Each subclass defines the structure and evaluation logic for its type of expression, such as binary
operations, literals, variable references, and more.
"""

from typing import Generic, TypeVar, List
from Token import Token

# Defines a generic type variable R for return types.
R = TypeVar("R")

# Base class for all expression types.
class Expr:
    def __init__(self):
        pass

# Generic visitor class for implementing visitor pattern for expressions.
class Visitor(Generic[R]):
    def __init__(self):
        pass

# Maps expression types to their attributes for dynamic class generation.
subclasses = {
    "Assign": {"name": "Token", "value": "Expr"},
    "Binary": {"left": "Expr", "operator": "Token", "right": "Expr"},
    "Call": {"callee": "Expr", "paren": "Token", "arguments": "List[Expr]"},
    "Get": {"object": "Expr", "name": "Token"},
    "Grouping": {"expression": "Expr"},
    "Literal": {"value": "object"},
    "Logical": {"left": "Expr", "operator": "Token", "right": "Expr"},
    "Set": {"object": "Expr", "name": "Token", "value": "Expr"},
    "Super": {"keyword": "Token", "method": "Token"},
    "This": {"keyword": "Token"},
    "Unary": {"operator": "Token", "right": "Expr"},
    "Variable": {"name": "Token"},
}

# Iterate through expression types and dynamically create classes.
for name, attributes in subclasses.items():
    args = ""  # Initialises argument string for constructor signature.
    for arg, arg_type in attributes.items():  # Builds constructor argument string.
        args += f", {arg}: {arg_type}"
    subclass_str = ""  # Initialises the string to hold the class definition code.
    subclass_str += f"class {name}(Expr):\n"  # Starts class definition.
    subclass_str += f"    def __init__(self{args}):\n"  # Adds constructor signature.
    for arg in attributes:  # Adds code to assign instance variables.
        subclass_str += f"        self.{arg} = {arg}\n"
    subclass_str += "\n"
    subclass_str += "    def accept(self, visitor: Visitor[R]):\n"  # Adds accept method for visitor pattern.
    subclass_str += f"        return visitor.visit_{name.lower()}_expr(self)\n"
    exec(subclass_str, globals())  # Dynamically executes the class definition code in the global namespace.