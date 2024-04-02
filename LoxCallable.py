from typing import List

class LoxCallable:
    # Initialise the class with no specific actions.
    def __init__(self):
        # No initialisation actions are defined here. This method is a placeholder.
        pass

    # Return the number of arguments that the callable expects.
    def arity(self):
        # This method should be overridden in subclasses to return the actual number of arguments.
        pass

    # Call or execute the callable with a given set of arguments.
    def call(self, interpreter: "Interpreter", arguments: List[object]):
        # This method should be overridden in subclasses to define how the callable is executed.
        pass

    # Return a string representation of the callable.
    def to_string(self):
        # This method should be overridden in subclasses to return a meaningful string representation.
        pass