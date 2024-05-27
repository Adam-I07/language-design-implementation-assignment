"""
Represents an instance of a LoxClass in the interpreter. Stores instance fields and provides methods to get and set 
them. It manages method lookups, enabling dynamic method binding for class instances. The class ensures encapsulation 
and access control for instance variables and methods. 
"""

from Token import Token
from RuntimeError import RuntimeError


class LoxInstance:
    # Initialise a new instance of a Lox class with a reference to its class and an empty fields dictionary.
    def __init__(self, klass: "LoxClass"):
        self.klass = klass  # Store the class definition.
        self.fields = {}  # Initialise an empty dictionary for instance fields.

    # Return a string representation of this instance, typically for debugging purposes.
    def __str__(self):
        # Format the class name followed by the word 'instance'.
        return f"{self.klass._name} instance"

    # Retrieve a field or method from this instance based on a given name.
    def get(self, name: Token):
        # If the field exists in this instance's fields, return its value.
        if name.lexme in self.fields:
            return self.fields[name.lexme]
        # If the field is not found, attempt to find a method of the same name in the class.
        method = self.klass.find_method(name.lexme)
        # If a method is found, return it bound to this instance.
        if method is not None:
            return method.bind(self)
        # If neither field nor method is found, raise a runtime error indicating an undefined property.
        raise RuntimeError(name, f"Undefined property '{name.lexme}'.")

    # Assign a value to a field of this instance.
    def set(self, name: Token, value: object):
        # Store the value in this instance's fields dictionary under the given name.
        self.fields[name.lexme] = value
