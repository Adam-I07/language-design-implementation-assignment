from TokenType import TokenType
from Token import Token

class Scanner:
    # A dictionary mapping string representations of keywords to their corresponding TokenType.
    # This allows the scanner to easily identify and classify keywords in the source code
    # by their TokenType, facilitating syntax analysis and parsing.
    keywords = {
        "and": TokenType.AND,       # Maps the string "and" to the TokenType representing the logical AND operator.
        "class": TokenType.CLASS,   # Maps "class" to the TokenType for class definitions.
        "else": TokenType.ELSE,     # Maps "else" to the TokenType for else statements in conditional logic.
        "false": TokenType.FALSE,   # Maps "false" to the TokenType representing the boolean value FALSE.
        "for": TokenType.FOR,       # Maps "for" to the TokenType for for-loop constructs.
        "fun": TokenType.FUN,       # Maps "fun" to the TokenType for function definitions.
        "if": TokenType.IF,         # Maps "if" to the TokenType for if statements.
        "nil": TokenType.NIL,       # Maps "nil" to the TokenType representing a null value.
        "or": TokenType.OR,         # Maps "or" to the TokenType representing the logical OR operator.
        "print": TokenType.PRINT,   # Maps "print" to the TokenType for the print statement or function.
        "return": TokenType.RETURN, # Maps "return" to the TokenType for return statements in functions.
        "super": TokenType.SUPER,   # Maps "super" to the TokenType for accessing methods of a parent class.
        "this": TokenType.THIS,     # Maps "this" to the TokenType for referring to the current class instance.
        "true": TokenType.TRUE,     # Maps "true" to the TokenType representing the boolean value TRUE.
        "var": TokenType.VAR,       # Maps "var" to the TokenType for variable declarations.
        "while": TokenType.WHILE,   # Maps "while" to the TokenType for while-loop constructs.
    }

    def __init__(self, source):
        self.source = source  # The source code string to be scanned for tokens.
        self.tokens = []      # Initializes an empty list to store tokens found in the source code.
        self.start = 0        # The index in the source string where the current token begins.
        self.current = 0      # The current character position in the source string being scanned.
        self.line = 1         # Tracks the current line number in the source code for error reporting and token location.
        self.had_error = False  # Flag indicating whether a scanning error has occurred.
  
    def scan_tokens(self):
        # Continuously scan the source code until the end is reached.
        while not self.is_at_end():
            # Set 'start' to the current position. This marks the beginning of the next token to be scanned.
            self.start = self.current
            # Scan for a single token from the current position.
            self.scan_token()
        # Once all tokens have been scanned and the end of the source is reached, append an EOF (End Of File) token.
        # This EOF token is used to signify the end of the token list to the parser.
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        # Return the list of scanned tokens to the caller.
        return self.tokens

    def scan_token(self):
        # Advance one character in the source code and assign it to 'c'.
        c = self.advance()
        # Check if 'c' is one of the single-character tokens.
        if c in '(){}.,-+;*':
            # If 'c' is a single-character token, add it to the tokens list.
            # The TokenType is determined dynamically using the character as a key.
            self.add_token(TokenType[c])
        elif c == '!':
            # For '!', check if the next character is '=', forming '!='.
            # If it is, add BANG_EQUAL; otherwise, add BANG.
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            # Similar to '!', but for '=' and '=='.
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            # For '<', check if the next character is '=', forming '<='.
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            # For '>', check if the next character is '=', forming '>='.
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        elif c in ' \r\t':
            # Ignore whitespace characters.
            pass
        elif c == '\n':
            # Increment the line counter for newlines to track the token's location accurately.
            self.line += 1
        elif c == '"':
            # If 'c' is a double quote, initiate string tokenization.
            self.string()
        elif c == '/':
            # Special case for '/', could be a comment or a division operator.
            if self.match('/'):
                # If the next character is also '/', it's a comment. Skip the rest of the line.
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                # If not a comment, it's a division operator token.
                self.add_token(TokenType.SLASH)
        else:
            # For characters not matched above, check if they start a number or identifier,
            # or report them as unexpected characters.
            if self.is_digit(c):
                # If 'c' is a digit, tokenize a number.
                self.number()
            elif self.is_alpha(c):
                # If 'c' is an alphabetic character, tokenize an identifier.
                self.identifier()
            else:
                # If 'c' does not match any known token patterns, report an error.
                self.error(self.line, "Unexpected character.")

    def number(self):
        # Continue scanning as long as the next character is a digit.
        while self.is_digit(self.peek()):
            self.advance()  # Move forward in the source code, effectively 'consuming' a digit.
        # Look for a fractional part after a decimal point.
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # If there's a '.' followed by a digit, consume the '.' and proceed to scan the fractional part.
            self.advance()
            # Continue scanning as long as the next character is a digit.
            while self.is_digit(self.peek()):
                self.advance()  # Consume the fractional part of the number.
        # Once the whole number (integer or float) has been scanned, add it to the tokens list.
        # Convert the scanned string representing the number to a float and pass it as the literal value for the token.
        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def identifier(self):
        # Continue scanning as long as the next character is alphanumeric.
        # This loop will consume all parts of the identifier (letters, digits, underscores).
        while self.is_alpha_numeric(self.peek()):
            self.advance()  # Move forward in the source code to include the character in the current identifier.
        # Once the loop ends, the full identifier has been scanned. Extract the identifier's text from the source.
        text = self.source[self.start:self.current]
        # Attempt to find the extracted text in the predefined list of keywords.
        # If the text is a known keyword, its corresponding TokenType will be used.
        # Otherwise, it's classified as a generic IDENTIFIER.
        type = self.keywords.get(text, TokenType.IDENTIFIER)
        # Add the token with the determined type to the list of tokens.
        # For keywords, this adds a specific keyword token; for non-keywords, an IDENTIFIER token is added.
        self.add_token(type)


    def string(self):
        # Continue scanning the string until a closing quote is found or the end of the source is reached.
        while self.peek() != '"' and not self.is_at_end():
            # If a newline character is encountered within the string, increment the line counter.
            # This supports multi-line strings.
            if self.peek() == '\n':
                self.line += 1
            # Advance to the next character in the string.
            self.advance()
        # If the end of the source code is reached before finding a closing quote, report an error.
        if self.is_at_end():
            self.error(self.line, "Unterminated string.")
            return  # Exit the method early since the string is not properly terminated.
        self.advance()  # Consume the closing quote of the string.
        # Extract the string value from the source code.
        # This excludes the surrounding quotes by using the start and current indices.
        value = self.source[self.start + 1:self.current - 1]
        # Add the string token, with its value, to the list of tokens.
        self.add_token(TokenType.STRING, value)
    
    def match(self, expected):
        # Check if the current position is at the end of the source or if the current character does not match the expected character.
        if self.is_at_end() or self.source[self.current] != expected:
            return False  # If either condition is true, return False without advancing the current position.
        self.current += 1  # Move to the next character in the source since the current character matches the expected one.
        return True  # Return True to indicate a successful match.

    def peek(self):
        # Check if the scanner has reached the end of the source code.
        if self.is_at_end():
            return '\0'  # Return a null character if at the end, indicating no more characters to read.
        return self.source[self.current]  # Return the current character without advancing the scanner's position.

    def peek_next(self):
        # Check if advancing one character would go past the end of the source code.
        if self.current + 1 >= len(self.source):
            return '\0'  # Return a null character if there's no character after the current one.
        return self.source[self.current + 1]  # Return the character immediately after the current one, without advancing.

    def is_alpha(self, c):
        # Check if a character is an alphabetic letter or an underscore.
        # This is used to determine if a character can be part of an identifier in the language.
        return c.isalpha() or c == '_'

    def is_alpha_numeric(self, c):
        # Check if a character is either alphabetic (including underscore) or numeric.
        # This method combines `is_alpha` and `is_digit` to check if a character can be part of identifiers that may include numbers.
        return self.is_alpha(c) or self.is_digit(c)

    def is_digit(self, c):
        # Check if a character is a digit.
        # This is used to determine if a character can be part of a numeric literal.
        return c.isdigit()

    def is_at_end(self):
        # Determine if the current position is at or beyond the end of the source code.
        # This method helps prevent out-of-bounds errors when accessing the source string.
        return self.current >= len(self.source)

    def advance(self):
        # Move the current position forward by one character and return the character that was just passed.
        # This method is used to consume characters in the source code as they are scanned and classified into tokens.
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, type, literal=None):
        # Create a new token based on the current lexeme and add it to the list of tokens.
        # 'type' is the TokenType of the token being added.
        # 'literal' is an optional argument that carries the actual value of the token (e.g., the numerical value for NUMBER tokens).
        text = self.source[self.start:self.current]  # Extract the lexeme from the source code.
        self.tokens.append(Token(type, text, literal, self.line))  # Append the new token to the tokens list.

    def error(self, line, message):
        # Report an error that occurred at a specific line in the source code.
        # This method is a wrapper that specifies "Error" as the type of report.
        self.report(line, "Error", message)

    def report(self, line, where, message):
        # Print an error or report message to the console.
        # 'line' specifies the line number where the report originates.
        # 'where' provides context within the line (e.g., "Error" or a more specific location).
        # 'message' is the content of the report or error message.
        print(f"[line {line}] {where}: {message}")
