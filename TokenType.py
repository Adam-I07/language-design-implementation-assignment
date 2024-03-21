from enum import Enum

class TokenType(Enum):
    # Enum for token types: punctuation, operators, delimiters, with auto-assigned unique numeric values.
    # Single-character tokens
    LEFT_PAREN = 1    # Represents the '(' character.
    RIGHT_PAREN = 2   # Represents the ')' character.
    LEFT_BRACE = 3    # Represents the '{' character.
    RIGHT_BRACE = 4   # Represents the '}' character.
    COMMA = 5         # Represents the ',' character.
    DOT = 6           # Represents the '.' character.
    MINUS = 7         # Represents the '-' character.
    PLUS = 8          # Represents the '+' character.
    SEMICOLON = 9     # Represents the ';' character.
    SLASH = 10        # Represents the '/' character.
    STAR = 11         # Represents the '*' character.

    # One or two character tokens
    BANG = 12              # Represents the '!' character
    BANG_EQUAL = 13        # Represents the '!=' operator
    EQUAL = 14             # Represents the '=' character
    EQUAL_EQUAL = 15       # Represents the '==' operator
    GREATER = 16           # Represents the '>' character
    GREATER_EQUAL = 17     # Represents the '>=' operator
    LESS = 18              # Represents the '<' character
    LESS_EQUAL = 19        # Represents the '<=' operator

    # Literals
    IDENTIFIER = 20 # Represents identifiers, such as variable names, function names, or any user-defined names.
    STRING = 21     # Represents string literals, sequences of characters enclosed in quotes.
    NUMBER = 22     # Represents numeric literals, including integers and floating-point numbers.

    # Keywords
    AND = 23        # Logical AND operator keyword.
    CLASS = 24      # Keyword for defining classes.
    ELSE = 25       # Keyword for defining an alternative branch in conditional statements.
    FALSE = 26      # Boolean value FALSE.
    FUN = 27        # Keyword for defining functions.
    FOR = 28        # Keyword for defining for loops.
    IF = 29         # Keyword for defining conditional statements.
    NIL = 30        # Represents the null value in some languages (similar to None in Python).
    OR = 31         # Logical OR operator keyword.
    PRINT = 32      # Keyword or function for outputting text to the console.
    RETURN = 33     # Keyword for returning values from functions.
    SUPER = 34      # Keyword used to access methods of a parent class.
    THIS = 35       # Keyword referring to the current instance of a class.
    TRUE = 36       # Boolean value TRUE.
    VAR = 37        # Keyword for declaring variables.
    WHILE = 38      # Keyword for defining while loops.
    EOF = 39        # Represents the end-of-file marker, indicating no more tokens are available for parsing.

