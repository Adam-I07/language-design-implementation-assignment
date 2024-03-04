class Token:
    def __init__(self, type, lexeme, literal, line):
        # Initialize a new Token object with provided attributes.
        # type: Specifies the category of the token (e.g., NUMBER, STRING, IDENTIFIER).
        self.type = type
        # lexeme: The raw string of characters that makes up the token in the source code.
        self.lexeme = lexeme
        # literal: The actual value represented by the token, if applicable (e.g., the integer value for a NUMBER token).
        self.literal = literal
        # line: The line number in the source code where the token was found.
        self.line = line
        # This information is useful for error reporting and debugging.

    def __str__(self):
        # Define a string representation of the Token object.
        # This method is called when a Token instance is passed to the print() function or when str() is used.
        # It returns a formatted string that includes the token's type, lexeme, and literal value,
        # making it easier to understand the token's role and value in the source code at a glance.
        return f"{self.type} {self.lexeme} {self.literal}"
