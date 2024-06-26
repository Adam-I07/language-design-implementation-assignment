"""
Represents runtime errors encountered during interpretation. Extends Python's Exception class to provide custom error 
handling for Lox runtime errors. It stores error messages and relevant token information to facilitate debugging and 
error reporting during program execution. 
"""

from Token import Token

# Class for runtime errors in the program.
class RuntimeError(Exception): 
    def __init__(self, token: Token, msg: str):  # Constructor takes a token (where the error occurred) and an error message.
        super().__init__(msg)  # Calls the base class constructor with the error message.
        self.token = token  # Stores the token associated with the error for later reference.
