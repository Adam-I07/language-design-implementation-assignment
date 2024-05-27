"""
Represents a function in Lox. Implements LoxCallable. Manages function parameters, closure (the environment where 
it was declared), and execution. Supports method binding and initialisers for classes.
"""

from typing import List, Self
from Return import Return
from Environment import Environment
from LoxCallable import LoxCallable
from LoxInstance import LoxInstance
from Stmt import Function


class LoxFunction(LoxCallable):
    # Initialise a Lox function with its declaration, closure environment, and initializer status.
    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool):
        self.is_initializer = is_initializer  # Indicates if this function is a class initialiser.
        self.closure = closure  # The environment capturing the surrounding scope at the time of function definition.
        self.declaration = declaration  # The function declaration.

    # Create a new function bound to a given instance, for handling 'this' keyword.
    def bind(self, instance: LoxInstance):
        # Create a new environment enclosing the function's closure for the bound instance.
        environment = Environment(self.closure)
        # Define 'this' in the new environment to refer to the instance.
        environment.define("this", instance)
        # Return a new LoxFunction that is identical to this one but with 'this' bound to the instance.
        return LoxFunction(self.declaration, environment, self.is_initializer)

    # Return a string representation of the function, primarily for debugging purposes.
    def to_string(self):
        # Format the function's name for display.
        return f"fn {self.declaration.name.lexme}>"

    # Return the number of parameters that the function expects.
    def arity(self):
        # The arity is the length of the function's parameters list.
        return len(self.declaration.params)

    # Call this LoxFunction with a given list of arguments.
    def call(self, interpreter: "Interpreter", arguments: List[object]):
        # Create a new environment for the function's execution, enclosing its closure.
        environment = Environment(self.closure)
        # Define the function's parameters in the new environment with the provided arguments.
        for idx, param in enumerate(self.declaration.params):
            environment.define(param.lexme, arguments[idx])
        try:
            # Execute the function's body within the new environment.
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            # If a return statement is hit, return its value.
            if self.is_initializer:
                # If this function is an initializer, always return the instance.
                return self.closure.get_at(0, "this")
            return return_value.value
        # If the function completes without hitting a return statement, return None unless it's an initializer.
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None
