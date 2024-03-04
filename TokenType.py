from enum import Enum, auto

class TokenType(Enum):
    # Define an enumeration for different types of tokens that can be encountered in a language.
    # These tokens represent the smallest individual units of the language, such as punctuation,
    # operators, and delimiters. The `auto()` function automatically assigns an increasing numeric value
    # to each member, making each one unique. This is useful when the exact value of each enum member
    # is not important, but their distinctness and identity are.

    # Single-character tokens.
    LEFT_PAREN = auto()  # Represents the '(' character.
    RIGHT_PAREN = auto()  # Represents the ')' character.
    LEFT_BRACE = auto()  # Represents the '{' character.
    RIGHT_BRACE = auto()  # Represents the '}' character.
    COMMA = auto()  # Represents the ',' character.
    DOT = auto()  # Represents the '.' character.
    MINUS = auto()  # Represents the '-' character.
    PLUS = auto()  # Represents the '+' character.
    SEMICOLON = auto()  # Represents the ';' character.
    SLASH = auto()  # Represents the '/' character.
    STAR = auto()  # Represents the '*' character.
    
    # One or two character tokens.
    BANG = auto()          # Represents the '!' character, often used for logical negation.
    BANG_EQUAL = auto()    # Represents the '!=' operator, used for inequality comparison.
    EQUAL = auto()         # Represents the '=' character, typically used for assignment.
    EQUAL_EQUAL = auto()   # Represents the '==' operator, used for equality comparison.
    GREATER = auto()       # Represents the '>' character, used for greater than comparison.
    GREATER_EQUAL = auto() # Represents the '>=' operator, used for greater than or equal to comparison.
    LESS = auto()          # Represents the '<' character, used for less than comparison.
    LESS_EQUAL = auto()    # Represents the '<=' operator, used for less than or equal to comparison.

    # Literals.
    IDENTIFIER = auto()  # Represents identifiers, such as variable names, function names, or any user-defined names.
    STRING = auto()      # Represents string literals, sequences of characters enclosed in quotes.
    NUMBER = auto()      # Represents numeric literals, including integers and floating-point numbers.

    # Keywords.
    AND = auto()       # Logical AND operator keyword.
    CLASS = auto()     # Keyword for defining classes.
    ELSE = auto()      # Keyword for defining an alternative branch in conditional statements.
    FALSE = auto()     # Boolean value FALSE.
    FUN = auto()       # Keyword for defining functions.
    FOR = auto()       # Keyword for defining for loops.
    IF = auto()        # Keyword for defining conditional statements.
    NIL = auto()       # Represents the null value in some languages (similar to None in Python).
    OR = auto()        # Logical OR operator keyword.
    PRINT = auto()     # Keyword or function for outputting text to the console.
    RETURN = auto()    # Keyword for returning values from functions.
    SUPER = auto()     # Keyword used to access methods of a parent class.
    THIS = auto()      # Keyword referring to the current instance of a class.
    TRUE = auto()      # Boolean value TRUE.
    VAR = auto()       # Keyword for declaring variables.
    WHILE = auto()     # Keyword for defining while loops.
    EOF = auto()       # Represents the end-of-file marker, indicating no more tokens are available for parsing.
