import sys
from functools import singledispatchmethod
from Token import Token
from TokenType import TokenType
from RuntimeError import RuntimeError


class ErrorReporter:
    # Initialise the error reporter with flags for tracking errors.
    def __init__(self):
        # Tracks whether a syntax error has occurred.
        self.had_error = False  
        # Tracks whether a runtime error has occurred.
        self.had_runtime_error = False  

    # Define a generic error method that can be specialized based on argument type.
    @singledispatchmethod
    def error(self, arg, msg: str):
        # Placeholder method, specialized versions will be used.
        pass  

    # Specialised error method for reporting errors with a line number.
    @error.register
    def _(self, line: int, msg: str):
        # Utilise the report method to print the error message.
        self.report(line, "", msg)  

    # Reports the error to stderr with line number, location, and message.
    def report(self, line: int, where: str, msg: str):
        # Print the formatted error message.
        print(f"[line {line}] Error{where}: {msg}", file=sys.stderr)  
        # Set the error flag to True indicating an error has occurred.
        self.had_error = True  

    # Specialised error method for reporting errors with a token.
    @error.register
    def _(self, token: Token, msg: str):
        # Check if the error is at the end of the file.
        if token.type == TokenType.EOF:  
            # Report error at EOF.
            self.report(token.line, " at end", msg)  
        # For errors at specific tokens other than EOF.
        else:  
            # Report error at the specific token location.
            self.report(token.line, f" at '{token.lexme}'", msg)  

    # Handles runtime errors and prints them to stderr.
    def runtime_error(self, error: RuntimeError):
        # Print the runtime error message.
        print(f"{repr(error)}\n[line {error.token.line}]", file=sys.stderr)  
         # Set the runtime error flag to True indicating a runtime error has occurred.
        self.had_runtime_error = True 

# Instantiate the error reporter.
error_reporter = ErrorReporter()
