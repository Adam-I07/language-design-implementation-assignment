from TokenType import TokenType
from Token import Token
from ErrorReporter import error_reporter
from typing import List, Optional


class Scanner:
    def __init__(self, src: str):
        self.src = src     # Source code to scan.
        self.tokens: List[Token] = []  # List to hold generated tokens.
        self.start = 0     # Start index of the current token being scanned.
        self.current = 0   # Current index in the source code.
        self.line = 1      # Current line number in the source code.
        self.keywords = { 
            # Map of keyword strings to their corresponding token types.
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }

    # Scans the source code to extract tokens, adds an EOF token at the end, and returns the list of tokens.
    def scan_tokens(self):
        while not self.is_at_end():  # Continue until end of source code is reached.
            self.start = self.current  # Mark the start of a new token.
            self.scan_token()  # Scan and add a token starting from the current position.
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))  # Append an End of File token at the end.
        return self.tokens  # Return the list of scanned tokens.
    
    # Checks if the current position is at the end of the source code.
    def is_at_end(self):
        return self.current >= len(self.src)

    # Advances the current position in the source code and returns the character that was just passed.
    def advance(self):
        self.current += 1
        return self.src[self.current - 1]

    # Adds a new token of the specified type and literal value to the list of tokens.
    def add_token(self, type: TokenType, literal: Optional[object] = None):
        text = self.src[self.start : self.current]  # Extract the text of the token.
        self.tokens.append(Token(type, text, literal, self.line))  # Create and append the new token.

    # Scans the current character to determine and add the appropriate token to the tokens list.
    def scan_token(self):
        c = self.advance()  # Advances and gets the current character from the source.
        # Checks the current character against known symbols and adds the corresponding token.
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "*":
            self.add_token(TokenType.STAR)
        elif c == "!":  # Checks for != or ! and adds the corresponding token.
            self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
        elif c == "=":  # Checks for == or = and adds the corresponding token.
            self.add_token(TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL)
        elif c == "<":  # Checks for <= or < and adds the corresponding token.
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
        elif c == ">":  # Checks for >= or > and adds the corresponding token.
            self.add_token(TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER)
        elif c == "/":  # Handles comments or adds a slash token.
            if self.match("/"):  # If a comment, skips to the end of the line.
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:  # Not a comment, adds a slash token.
                self.add_token(TokenType.SLASH)
        elif c in [" ", "\r", "\t"]:  # Ignores whitespace characters.
            pass
        elif c == "\n":  # Increments line count on newline character.
            self.line += 1
        elif c == '"':  # Handles string literals.
            self.string()
        else:  # Handles numbers, identifiers, or reports an error for unexpected character.
            if self.is_digit(c):
                self.number()
            elif self.is_alpha(c):
                self.identifier()
            else:
                error_reporter.error(self.line, "Unexpected character.")

    # Scans for and adds an identifier token, distinguishing between user-defined identifiers and reserved keywords.
    def identifier(self):
        # Continue scanning as long as the next character is alphanumeric.
        while self.is_alpha_numeric(self.peek()):
            self.advance()  # Move forward in the source code.
        text = self.src[self.start : self.current]  # Extract the identifier text.
        # Check if the identifier is a reserved keyword or a user-defined identifier.
        if text not in self.keywords:
            self.add_token(TokenType.IDENTIFIER)  # Add as an identifier if not a keyword.
        else:
            self.add_token(self.keywords[text])  # Add the specific token type for the keyword.

    # Scans and constructs a numerical token from the source, handling both integer and decimal numbers.
    def number(self):
        # Scan through consecutive digits to form the integer part of a number.
        while self.is_digit(self.peek()):
            self.advance()  # Move forward for each digit found.
        # Check for a decimal point followed by at least one digit (the fractional part).
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()  # Consume the decimal point.
            while self.is_digit(self.peek()):
                self.advance()  # Continue through the digits after the decimal point.
        # Once the number is fully scanned, add it as a NUMBER token, converting the string to a float.
        self.add_token(TokenType.NUMBER, float(self.src[self.start : self.current]))

    # Scans for and constructs a string token, handling multiline strings and unterminated string errors.
    def string(self):
        while self.peek() != '"' and not self.is_at_end():  # Continue until closing quote or end of source.
            if self.peek() == "\n":  # Increment line count for multiline strings.
                self.line += 1
            self.advance()  # Move forward through the string.
        if self.is_at_end():  # If end of source without closing quote, report error.
            error_reporter.error(self.line, "Unterminated string.")
            return
        self.advance()  # Consume the closing quote.
        value = self.src[self.start + 1 : self.current - 1]  # Extract the string's value without quotes.
        self.add_token(TokenType.STRING, value)  # Add the string token with its value.

    # Checks and consumes the current character if it matches the expected one, advancing the scan position.
    def match(self, expected: str):
        # Check if at the end of the source to prevent overreach.
        if self.is_at_end():
            return False  # Cannot match if at the end of the source.
        # Check if the current character matches the expected character.
        if self.src[self.current] != expected:
            return False  # If it does not match, return False.
        self.current += 1  # Move to the next character after a successful match.
        return True  # Return True if the current character matches the expected one.

    # Returns the current character without advancing the scanner.
    def peek(self):
        if self.is_at_end():  # If at the end of the source, return a null character.
            return "\0"
        return self.src[self.current]  # Return the current character.

    # Returns the next character without advancing the scanner or consuming the character.
    def peek_next(self):
        if self.current + 1 >= len(self.src):  # Check if next position is beyond source length.
            return "\0"  # Return null character if beyond the end of the source.
        return self.src[self.current + 1]  # Return the character after the current one.

    # Determines if a character is an alphabetical letter or an underscore.
    def is_alpha(self, c: str):
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"  # Check if c is in the alphabet or is an underscore.

    # Determines if a character is either an alphabetical letter, an underscore, or a digit.
    def is_alpha_numeric(self, c: str):
        return self.is_alpha(c) or self.is_digit(c)  # True if c is alphanumeric.

    # Determines if a character is a digit.
    def is_digit(self, c: str):
        return c >= "0" and c <= "9"  # Check if c is between '0' and '9'.
