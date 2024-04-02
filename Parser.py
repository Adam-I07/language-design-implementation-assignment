from typing import List
from Token import Token
from TokenType import TokenType
from ErrorReporter import error_reporter
from Expr import (Expr, Assign, Binary, Unary, Literal, Grouping, Variable, Logical, Call, Get, Set, This, Super,)
from Stmt import Stmt, Print, Expression, Var, Block, If, While, Function, Return, Class


class ParseError(Exception):
    pass


class Parser:
    # Initialise the parser with tokens and set the starting point for parsing.
    def __init__(self, tokens: List[Token]):
        # Initialise parser with a list of tokens.
        self._tokens = tokens  
        # Set the current position in the token list to the beginning.
        self._current = 0  

    # Parse the tokens into a list of statements until the end of tokens is reached.
    def parse(self):
        # Initialise an empty list to hold parsed statements.
        statements = []  
        # Continue parsing until the end of tokens is reached.
        while not self.is_at_end():  
            # Parse a declaration and add it to the list of statements.
            statements.append(self.declaration())  
        # Return the list of parsed statements.
        return statements  
        
    # Parse and return an expression, starting with assignment expressions.
    def expression(self):
        # Delegate to the assignment method for parsing.
        return self.assignment()  

    # Attempt to parse a declaration, handling various declaration types or falling back to a statement.
    def declaration(self):
        try:
            # If current token is a class, parse a class declaration.
            if self.match(TokenType.CLASS):  
                return self.class_declaration()
            # If current token is a function, parse a function declaration.
            if self.match(TokenType.FUN):  
                return self.function("function")
            # If current token is a variable, parse a variable declaration.
            if self.match(TokenType.VAR):  
                return self.var_declaration()
            # If none of the above, parse a statement.
            return self.statement()  
        # Catch parsing errors to synchronize and recover.
        except ParseError:  
            # Attempt to recover from the error by synchronizing.
            self.synchronize()  
            # Return None to indicate the failure to parse a declaration.
            return None  

    def class_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        superclass = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable(self.previous())
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, superclass, methods)
    
    # Parse a class declaration, including its name, optional superclass, and methods.
    def class_declaration(self):
        # Consume the class name identifier.
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")  
        # Initialise superclass to None; it's optional.
        superclass = None  
        # If a '<' is found, a superclass is being defined.
        if self.match(TokenType.LESS):  
            # Consume the superclass name identifier.
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")  
            # Create a Variable instance for the superclass.
            superclass = Variable(self.previous())  
        # Ensure class body starts with '{'.
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")  
        # Initialise an empty list for class methods.
        methods = []  
        # Parse methods until '}' or end of tokens.
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end(): 
            # Parse a method and add it to the methods list.
            methods.append(self.function("method"))  
        # Ensure class body ends with '}'.
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")  
        # Return a Class instance with parsed name, superclass, and methods.
        return Class(name, superclass, methods)  
    
    # Parse a statement, handling different types based on the current token.
    def statement(self):
        # If current token is for, parse a for loop statement.
        if self.match(TokenType.FOR):  
            return self.for_statement()
        # If current token is if, parse an if statement.
        if self.match(TokenType.IF):  
            return self.if_statement()
        # If current token is print, parse a print statement.
        if self.match(TokenType.PRINT):  
            return self.print_statement()
        # If current token is return, parse a return statement.
        if self.match(TokenType.RETURN):  
            return self.return_statement()
        # If current token is while, parse a while loop statement.
        if self.match(TokenType.WHILE):  
            return self.while_statement()
        # If current token is a left brace, parse a block statement.
        if self.match(TokenType.LEFT_BRACE):  
            return Block(self.block())
        # If none of the above match, parse an expression statement.
        return self.expression_statement() 

    # Parse a for loop statement, including its initialiser, condition, increment, and body.
    def for_statement(self):
        # Consume the '(' after 'for'.
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")  
        # Initialise the loop initialiser to None.
        initializer = None  
        # Check if there's no initialiser.
        if self.match(TokenType.SEMICOLON):  
            initializer = None
        # If the initialiser is a variable declaration.
        elif self.match(TokenType.VAR):  
            initializer = self.var_declaration()
        # The initialiser is an expression statement.
        else: 
            initializer = self.expression_statement()
        # Initialise the loop condition to None.
        condition = None  
        # If there's a condition.
        if not self.check(TokenType.SEMICOLON):  
            condition = self.expression()
        # Consume the ';' after the condition.
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")  
        # Initialise the loop increment to None.
        increment = None   
        # If there's an increment.
        if not self.check(TokenType.RIGHT_PAREN): 
            increment = self.expression()
        # Consume the ')' after the for clauses.
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")  
        # Parse the body of the loop.
        body = self.statement()  
        # If there's an increment, wrap the body and increment in a Block.
        if increment is not None:  
            body = Block([body, Expression(increment)])
        # If there's no condition, make it a literal true.
        if condition is None:  
            condition = Literal(True)
        # Wrap the modified body in a While loop for the condition.
        body = While(condition, body)  
        # If there's an initialiser, wrap it and the modified body in a Block.
        if initializer is not None:  
            body = Block([initializer, body])
        # Return the constructed loop body.
        return body  

    # Parse an if statement, including its condition, then branch, and optional else branch.
    def if_statement(self):
        # Consume the '(' after 'if'.
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")  
        # Parse the condition expression.
        condition = self.expression()  
        # Consume the ')' after the condition.
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")  
        # Parse the statement to execute if the condition is true.
        then_branch = self.statement()  
        # Initialise the else branch to None.
        else_branch = None  
        # Check if there is an 'else' part.
        if self.match(TokenType.ELSE):  
            # Parse the statement to execute if the condition is false.
            else_branch = self.statement()  
        # Return an If statement with the parsed components.
        return If(condition, then_branch, else_branch)  

    # Parse a print statement for outputting values.
    def print_statement(self):
        # Parse the expression to be printed.
        value = self.expression()  
        # Ensure the statement ends with a ';'.
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")  
        # Return a Print statement with the parsed value.
        return Print(value)  

    # Parse a return statement, which may optionally include a value to return.
    def return_statement(self):
        # Get the 'return' keyword token.
        keyword = self.previous()  
        # Initialise the return value to None.
        value = None  
        # If there's an expression after 'return'.
        if not self.check(TokenType.SEMICOLON):  
            # Parse the return value expression.
            value = self.expression()  
        # Ensure the statement ends with a ';'.
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")  
        # Return a Return statement with the parsed components.
        return Return(keyword, value) 

    # Parse a variable declaration, including the variable name and optional initialiser.
    def var_declaration(self):
        # Consume the variable name identifier.
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")  
        # Initialise the variable initialiser to None.
        initializer = None  
        # If an '=' is found, there's an initialiser.
        if self.match(TokenType.EQUAL): 
            # Parse the initialiser expression.
            initializer = self.expression()  
        # Ensure declaration ends with a ';'.
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")  
        # Return a Var statement with the parsed name and initialiser.
        return Var(name, initializer)  
    
    # Parse a while loop statement, including its condition and body statement.
    def while_statement(self):
        # Consume the '(' after 'while'.
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")  
        # Parse the loop condition expression.
        condition = self.expression()  
        # Consume the ')' after the condition.
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")  
        # Parse the body of the loop.
        body = self.statement()  
        # Return a While statement with the parsed condition and body.
        return While(condition, body)  

    # Parse an expression statement, ending with a semicolon.
    def expression_statement(self):
        # Parse the expression.
        Expr = self.expression()  
        # Ensure the statement ends with a ';'.
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")  
        # Return an Expression statement with the parsed expression.
        return Expression(Expr)  
   
    # Parse a function declaration, including its name, parameters, and body.
    def function(self, kind: str):
        # Consume the function/method name.
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        # Consume the '(' after the function/method name.  
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")  
        # Initialise the list of parameters.
        parameters = []  
        # If there are parameters to consume.
        if not self.check(TokenType.RIGHT_PAREN):  
            while True:
                # Check parameter limit.
                if len(parameters) >= 255: error_reporter.error(self.peek(), "Can't have more than 255 parameters.") 
                # Consume a parameter name.
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))  
                # Break the loop if there's no comma, indicating the end of parameters.
                if not self.match(TokenType.COMMA):  
                    break
        # Consume the ')' after parameters.
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")  
        # Consume the '{' before the function/method body.
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.") 
        # Parse the function/method body as a block of statements.
        body = self.block()  
        # Return a Function object with the parsed components.
        return Function(name, parameters, body)  

    # Parse a block of statements, enclosed in curly braces.
    def block(self):
        # Initialise an empty list for statements within the block.
        statements = []  
        # Parse statements until a '}' or end of tokens.
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():  
            # Parse a declaration (or statement) and add it to the list.
            statements.append(self.declaration())  
        # Consume the '}' marking the end of the block.
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")  
        # Return the list of parsed statements.
        return statements  
    
    # Parse an assignment expression, supporting both simple and compound assignments.
    def assignment(self):
        # Start by parsing an 'or' expression to handle possible logical operations.
        Expr = self._or()  
        # Check for an '=' to indicate an assignment.
        if self.match(TokenType.EQUAL): 
            # Get the '=' token. 
            equals = self.previous()  
            # Recursively parse the right-hand side as an assignment to support chains.
            value = self.assignment()  
            # If the left-hand side is a variable, it's a valid assignment target.
            if isinstance(Expr, Variable):  
                # Extract the variable name.
                name = Expr.name  
                # Return an Assign expression.
                return Assign(name, value) 
            # If the left-hand side is a property access, it's a valid target for assignment.
            elif isinstance(Expr, Get):  
                # Get the property access expression.
                get = Expr  
                # Return a Set expression for property assignment.
                return Set(get.object, get.name, value)  
            # If neither, report an error.
            error_reporter.error(equals, "Invalid assignment target.")  
        # If no assignment, return the parsed expression as is.
        return Expr  

    # Parse a logical 'or' expression, potentially chaining with 'and' expressions.
    def _or(self):
        # Start with parsing an 'and' expression to handle logical ANDs at a lower level.
        Expr = self._and()  
        # While there are 'or' tokens, indicating logical OR operations.
        while self.match(TokenType.OR):  
            # Get the 'or' operator token.
            operator = self.previous()  
            # Parse the right-hand side as an 'and' expression for correct precedence.
            right = self._and()  
            # Combine into a Logical expression representing the OR operation.
            Expr = Logical(Expr, operator, right)  
        return Expr  # Return the combined expression.


    # Parse a logical 'and' expression, chaining together multiple equality expressions.
    def _and(self):
        # Start with an equality expression as the base for 'and' operations.
        Expr = self.equality()
        # Continue parsing 'and' operations as long as 'AND' tokens are encountered.
        while self.match(TokenType.AND):
            # Capture the 'AND' operator token for later use in the Logical expression.
            operator = self.previous()
            # Parse the right-hand side as another equality expression.
            right = self.equality()
            # Construct a new Logical expression that chains the current and new expressions with the 'AND' operator.
            Expr = Logical(Expr, operator, right)
        # Return the final chained Logical expression.
        return Expr

    # Parse an equality expression, dealing with '!=' and '==' operations.
    def equality(self):
        # Start with a comparison expression as the base for equality operations.
        Expr = self.comparison()
        # Continue parsing as long as inequality ('!=') or equality ('==') tokens are encountered.
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            # Capture the equality/inequality operator token for use in the Binary expression.
            operator = self.previous()
            # Parse the right-hand side as another comparison expression.
            right = self.comparison()
            # Construct a new Binary expression that represents the equality/inequality operation.
            Expr = Binary(Expr, operator, right)
        # Return the final Binary expression, which may represent a chain of equality/inequality comparisons.
        return Expr


    # Parse a comparison expression, handling '>', '>=', '<', and '<=' operators.
    def comparison(self):
        # Start with a term expression to handle addition and subtraction in comparisons.
        Expr = self.term()
        # Continue parsing while there are comparison operators.
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            # Capture the comparison operator token for later use in the Binary expression.
            operator = self.previous()
            # Parse the right-hand side as another term expression for correct precedence.
            right = self.term()
            # Construct a new Binary expression that represents the comparison.
            Expr = Binary(Expr, operator, right)
        # Return the final Binary expression, potentially representing a chain of comparisons.
        return Expr

    # Parse a term expression, dealing with '+' and '-' operators.
    def term(self):
        # Start with a factor expression as the base for addition and subtraction operations.
        Expr = self.factor()
        # Continue parsing as long as addition ('+') or subtraction ('-') tokens are encountered.
        while self.match(TokenType.MINUS, TokenType.PLUS):
            # Capture the addition/subtraction operator token for use in the Binary expression.
            operator = self.previous()
            # Parse the right-hand side as another factor expression to ensure correct operation precedence.
            right = self.factor()
            # Construct a new Binary expression that represents the addition or subtraction.
            Expr = Binary(Expr, operator, right)
        # Return the final Binary expression, which may represent a chain of additions and/or subtractions.
        return Expr

    # Parse a factor expression, handling '*' and '/' operators.
    def factor(self):
        # Start with a unary expression as the base for multiplication and division operations.
        Expr = self.unary()
        # Continue parsing as long as multiplication ('*') or division ('/') tokens are encountered.
        while self.match(TokenType.SLASH, TokenType.STAR):
            # Capture the multiplication/division operator token for use in the Binary expression.
            operator = self.previous()
            # Parse the right-hand side as another unary expression to ensure correct operation precedence.
            right = self.unary()
            # Construct a new Binary expression that represents the multiplication or division.
            Expr = Binary(Expr, operator, right)
        # Return the final Binary expression, which may represent a chain of multiplications and/or divisions.
        return Expr

    # Parse a unary expression, handling negation and logical complement.
    def unary(self):
        # Check for unary operators '!' (logical NOT) or '-' (negation).
        if self.match(TokenType.BANG, TokenType.MINUS):
            # Capture the unary operator token.
            operator = self.previous()
            # Recursively parse the right-hand side as a unary expression to support nested unary operations.
            right = self.unary()
            # Return a Unary expression representing the unary operation.
            return Unary(operator, right)
        # If no unary operator is found, proceed to parsing a call expression.
        return self.call()

    # Finalize parsing a call expression, including handling arguments.
    def finish_call(self, callee: Expr):
        arguments = []  # Initialize an empty list for function arguments.
        # Continue parsing arguments until a ')' is encountered or the argument limit is reached.
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                # Enforce a limit on the number of arguments to prevent excessive parameters.
                if len(arguments) >= 255: error_reporter.error(self.peek(), "Can't have more than 255 arguments.")
                # Parse an argument expression and add it to the list of arguments.
                arguments.append(self.expression())
                # If a ',' is not found, break the loop indicating the end of arguments.
                if not self.match(TokenType.COMMA):
                    break
        # Consume the ')' token indicating the end of the arguments list.
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        # Return a Call expression with the parsed callee and arguments.
        return Call(callee, paren, arguments)

    # Parse a call expression, potentially including function calls or property accesses.
    def call(self):
        # Start with a primary expression which can be a literal, variable, or a grouping.
        Expr = self.primary()
        # Continue parsing as long as there are function call '(' or property access '.' tokens.
        while True:
            if self.match(TokenType.LEFT_PAREN):
                # If a '(' is found, parse the function call including its arguments.
                Expr = self.finish_call(Expr)
            elif self.match(TokenType.DOT):
                # If a '.' is found, parse a property access by consuming the property name.
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                # Construct a Get expression representing the property access on the object.
                Expr = Get(Expr, name)
            else:
                break
        return Expr  # Return the parsed call expression.

    # Parse a primary expression, handling literals, super, and grouping.
    def primary(self):
        # Handle literal values: false, true, and nil.
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NIL): return Literal(None)
        # Handle numeric and string literals.
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        # Handle 'super' keyword for accessing methods from a superclass.
        if self.match(TokenType.SUPER):
            keyword = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self.consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return Super(keyword, method)
        # Handle the 'this' keyword for referencing the current instance.
        if self.match(TokenType.THIS):
            # Return a This expression with the 'this' keyword token.
            return This(self.previous())
        # Handle identifiers for variables.
        if self.match(TokenType.IDENTIFIER):
            # Return a Variable expression with the identifier token.
            return Variable(self.previous())
        # Handle grouped expressions.
        if self.match(TokenType.LEFT_PAREN):
            # Parse the expression within the parentheses.
            Expr = self.expression()
            # Consume the closing ')' token, ensuring the grouping is properly closed.
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            # Return a Grouping expression that represents the expression within parentheses.
            return Grouping(Expr)
        # If no valid primary expression is found, raise a syntax error.
        raise self.error(self.peek(), "Expect expression.")
    
    # Check if the current token matches any of the given types and advance if it does.
    def match(self, *types: TokenType):
        # Iterate through the given token types to see if any match the current token.
        for type in types:
            if self.check(type):
                # Advance to the next token if a match is found.
                self.advance()
                return True
        # Return False if no match is found.
        return False

    # Consume a token of a specific type, or raise an error if it's not the expected type.
    def consume(self, type: TokenType, msg: str):
        # If the current token is of the expected type, advance and return it.
        if self.check(type):
            return self.advance()
        # Raise a syntax error with a custom message if the token is not as expected.
        raise self.error(self.peek(), msg)

    # Check if the current token is of a specified type without advancing.
    def check(self, type: TokenType):
        # Return False if the end of the tokens list has been reached.
        if self.is_at_end():
            return False
        # Return True if the current token's type matches the specified type.
        return self.peek().type == type

    # Advance the current token pointer and return the previous token.
    def advance(self):
        # Advance the current position if not at the end of the tokens list.
        if not self.is_at_end():
            self._current += 1
        # Return the token just passed by advance.
        return self.previous()

    # Check if the current token pointer is at the end of the tokens list.
    def is_at_end(self):
        # Return True if the current token is the EOF (end of file) token.
        return self.peek().type == TokenType.EOF

    # Get the current token without advancing the pointer.
    def peek(self):
        # Return the current token based on the current pointer position.
        return self._tokens[self._current]

    # Get the token just before the current one.
    def previous(self):
        # Return the token before the current position.
        return self._tokens[self._current - 1]

    # Raise a parsing error and synchronise the parser.
    def error(self, token: Token, msg: str):
        # Report the error using the provided token and message.
        error_reporter.error(token, msg)
        # Return a new ParseError instance.
        return ParseError()

    # Synchronize the parser by advancing past problematic tokens until a statement boundary is found.
    def synchronize(self):
        # Advance to the next token to start error recovery.
        self.advance()
        # Continue advancing until a token that typically starts a statement is found, indicating a potential recovery point.
        while not self.is_at_end():
            # If a semicolon is found, it's considered a safe point to resume parsing.
            if self.previous().type == TokenType.SEMICOLON:
                return
            # Check for tokens that typically start a new statement, indicating a possible recovery point.
            if self.peek().type in [TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR, TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]:
                return
            # Advance to the next token if no recovery point is found yet.
            self.advance()
