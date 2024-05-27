"""
Implements an input function for the interpreter. Inherits from LoxCallable. Prompts the user for input, optionally 
using a provided string prompt. Defines arity to specify it expects one argument.
"""

from LoxCallable import LoxCallable 

class LoxInput(LoxCallable):
    def call(self, interpreter, arguments): 
        # Initialise prompt to an empty string
        prompt = "" 
        # If there's at least one argument, use it as the prompt
        if len(arguments) > 0:
            # Convert the first argument to a string and set as prompt
            prompt = str(arguments[0]) 
        # Return the input 
        return input(prompt) 

    # Defines the number of arguments the callable expects which is one
    def arity(self):  
        return 1  
