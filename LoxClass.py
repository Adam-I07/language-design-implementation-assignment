"""
Represents a class in Lox. Implements LoxCallable, allowing instances of LoxClass to be created. Manages class methods, 
inheritance (via superclass), and provides the mechanism for calling class constructors and methods. 
"""

from LoxCallable import LoxCallable
from LoxInstance import LoxInstance
from LoxFunction import LoxFunction
from typing import List, Dict, Self


class LoxClass(LoxCallable):
    # Initialise a new Lox class with its name, optional superclass, and methods.
    def __init__(self, name: str, superclass: "LoxClass", methods: Dict[str, LoxFunction]):
        self._superclass = superclass  # Store the superclass, if any, for inheritance.
        self._name = name  # The name of the class.
        self._methods = methods  # A dictionary of method names to their corresponding LoxFunction instances.

    # Find a method in the class or its superclass by name.
    def find_method(self, name: str):
        # Check if the method exists in the current class.
        if name in self._methods:
            return self._methods[name]
        # If the method isn't found and there is a superclass, try to find the method in the superclass.
        if self._superclass is not None:
            return self._superclass.find_method(name)
        # Return None if the method is not found in the class hierarchy.
        return None

    # Return the class name as its string representation.
    def __str__(self):
        # The string representation is simply the class's name.
        return self._name

    # Create a new instance of the class and call its initialiser, if any, with provided arguments.
    def call(self, interpreter: "Interpreter", arguments: List[object]):
        # Create a new instance of this class.
        instance = LoxInstance(self)
        # Look for an 'init' method which acts as the class constructor.
        initializer = self.find_method("init")
        # If an initializer is found, bind it to the new instance and call it with the provided arguments.
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        # Return the new instance.
        return instance

    # Get the number of parameters expected by the class's initialiser, if any.
    def arity(self):
        # Find the 'init' method.
        initializer = self.find_method("init")
        # If there is no initialiser, the arity is zero since the class can be instantiated without arguments.
        if initializer is None:
            return 0
        # If an initialiser exists, return its arity (number of parameters it expects).
        return initializer.arity()
