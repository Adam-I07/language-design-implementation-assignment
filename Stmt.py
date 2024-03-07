from Expr import Expr, Variable
from Token import Token
from typing import Generic, TypeVar, List

R = TypeVar("R")

class Stmt:
    def __init__(self):
        pass

class Visitor(Generic[R]):
    def __init__(self):
        pass

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

for name, attributes in subclasses.items():
    # Initialize the class
    args = ""
    instance_init = ""
    for arg, arg_type in attributes.items():
        args += f", {arg}: {arg_type}"

    subclass_str = ""
    subclass_str += f"class {name}(Stmt):\n"
    subclass_str += f"    def __init__(self{args}):\n"

    for arg in attributes:
        subclass_str += f"        self.{arg} = {arg}\n"

    subclass_str += "\n"
    subclass_str += "    def accept(self, visitor: Visitor[R]) -> R:\n"
    subclass_str += f"        return visitor.visit_{name.lower()}_stmt(self)\n"

    # Exposes the class when module is imported
    exec(subclass_str, globals())
