from typing import Generic, TypeVar, List
from Token import Token

# Define a type variable 'R' to be used for generic return types in the Visitor pattern
R = TypeVar("R")

class Expr:
    def __init__(self):
        pass

# Define a generic Visitor base class using 'R' as its generic type.
# This class will be extended by specific visitor implementations to operate on expression instances.
class Visitor(Generic[R]):
    def __init__(self):
        pass

# A dictionary defining the structure of various expression subclasses.
# Each entry specifies the class name and its attributes with their types.
subclasses = {
    "Assign": {"name": "Token", "value": "Expr"},
    "Binary": {"left": "Expr", "operator": "int", "right": "Expr"},
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

# Dynamically create subclasses of Expr based on the definitions in the subclasses dictionary.
for name, attributes in subclasses.items():
    args = ""
    # Construct the argument list for the __init__ method
    for arg, arg_type in attributes.items():
        args += f", {arg}: {arg_type}"

    subclass_str = ""
    # Start defining the subclass, inheriting from Expr
    subclass_str += f"class {name}(Expr):\n"
    # Add the __init__ method with dynamically created parameters
    subclass_str += f"    def __init__(self{args}):\n"

    # Assign each passed argument to an instance attribute
    for arg in attributes:
        subclass_str += f"        self.{arg} = {arg}\n"

    # Define the accept method for the Visitor pattern
    subclass_str += "\n"
    subclass_str += "    def accept(self, visitor: Visitor[R]) -> R:\n"
    subclass_str += f"        return visitor.visit_{name.lower()}_expr(self)\n"
    
    # Execute the constructed class definition string, creating the class
    exec(subclass_str, globals())
