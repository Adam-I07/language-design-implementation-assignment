from TokenType import TokenType

class Token:
    def __init__(self, type: TokenType, lexme: str, literal: object, line: int):
        # Initialize a new Token object with provided attributes.
        # type: Specifies the category of the token (e.g., NUMBER, STRING, IDENTIFIER).
        # lexeme: The raw string of characters that makes up the token in the source code.
        # literal: The actual value represented by the token, if applicable (e.g., the integer value for a NUMBER token).
        # line: The line number in the source code where the token was found.
        # This information is useful for error reporting and debugging.
        self.type = type
        self.lexme = lexme
        self.literal = literal
        self.line = line

    def __str__(self):
        # Returns a formatted string representation of the Token instance.
        return f"{self.type} {self.lexme} {self.literal}"