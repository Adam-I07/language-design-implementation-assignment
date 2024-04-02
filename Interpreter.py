from time import time
from typing import List, Self
from types import MethodType
import Expr
import Stmt
from TokenType import TokenType
from Token import Token
from RuntimeError import RuntimeError
from ErrorReporter import error_reporter
from Environment import Environment
from LoxCallable import LoxCallable
from LoxFunction import LoxFunction
from LoxClass import LoxClass
from LoxInstance import LoxInstance
from Return import Return
from LoxInput import LoxInput


class Interpreter(Expr.Visitor[object], Stmt.Visitor[None]):
    # Initialises the interpreter with global variables and predefined functions.
    def __init__(self):
        # Establishes a global environment for variables and functions.
        self.globals = Environment()  
        # Sets the current environment scope to global by default.
        self.environment = self.globals  
        # Keeps track of local scopes for variables.
        self.locals = {} 
        # Defines a built-in "input" function within the global scope.
        self.globals.define("input", LoxInput())

        # Defines the arity method for the "clock" function, indicating it takes no arguments.
        def _arity(self):
            return 0

        # Defines the call method for the "clock" function, returning the current Unix timestamp.
        def _call(self, interpreter: Self, arguments: List[object]):
            return float(time())

        # Provides a string representation for the "clock" function.
        def _to_string(self):
            return "<native fn>"

        # Creates an instance of LoxCallable for the "clock" function and sets its methods.
        clock = LoxCallable()
        # Sets the function's arity.
        clock.arity = MethodType(_arity, clock)  
        # Defines how the function is called.
        clock.call = MethodType(_call, clock)  
        # Sets the function's string representation.
        clock.to_string = MethodType(_to_string, clock)  

        # Adds the "clock" function to the global scope, making it available in Lox programs.
        self.globals.define("clock", clock)

    # Executes a list of statements as part of the program's interpretation process.
    def interpret(self, statements: List[Stmt.Stmt]):
        try:
            # Iterates through each statement to be executed.
            for statement in statements: 
                # Executes the current statement. 
                self.execute(statement)  
        # Catches and handles any runtime errors that occur during execution.
        except RuntimeError as error: 
            # Reports the error using the global error reporter.
            error_reporter.runtime_error(error)  

    # Evaluates and returns the value of a literal expression.
    def visit_literal_expr(self, _expr: Expr.Literal):
        return _expr.value
    # Evaluates logical expressions and implements short-circuit evaluation.
    def visit_logical_expr(self, _expr: Expr.Logical):
        left = self.evaluate(_expr.left)
        # Implements OR logic with short-circuit evaluation.
        if _expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        # Implements AND logic with short-circuit evaluation.
        else:
            if not self.is_truthy(left):
                return left
        # Evaluates the right-hand expression if short-circuiting does not occur.
        return self.evaluate(_expr.right)

    # Sets a property on an object, ensuring the object is an instance of a class.
    def visit_set_expr(self, _expr: Expr.Set):
        _object = self.evaluate(_expr.object)
        if not isinstance(_object, LoxInstance):
            raise RuntimeError(_expr.name, "Only instances have fields.")
        value = self.evaluate(_expr.value)
        _object.set(_expr.name, value)
        return value

    # Handles the 'super' keyword, binding methods from a superclass.
    def visit_super_expr(self, _expr: Expr.Super):
        distance = self.locals.get(_expr)
        superclass = self.environment.get_at(distance, "super")
        _object = self.environment.get_at(distance - 1, "this")
        method = superclass.find_method(_expr.method.lexme)
        if method is None:
            raise RuntimeError(_expr.method, f"Undefined property '{_expr.method.lexme}'.")
        return method.bind(_object)

    # Evaluates and returns the current object instance for 'this'.
    def visit_this_expr(self, _expr: Expr.This):
        return self.look_up_variable(_expr.keyword, _expr)

    # Evaluates unary expressions, implementing negation and arithmetic negation.
    def visit_unary_expr(self, _expr: Expr.Unary):
        right = self.evaluate(_expr.right)
        if _expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        elif _expr.operator.type == TokenType.MINUS:
            self.check_number_operand(_expr.operator, right)
            return -float(right)
        # Placeholder for unreachable code.
        return None

    # Retrieves the value of a variable from the environment.
    def visit_variable_expr(self, _expr: Expr.Variable):
        return self.look_up_variable(_expr.name, _expr)


   # Looks up a variable's value, considering both local and global scopes.
    def look_up_variable(self, name: Token, _expr: Expr.Expr):
        if _expr in self.locals:
            distance = self.locals[_expr]
            return self.environment.get_at(distance, name.lexme)
        else:
            return self.globals.get(name)

    # Ensures an operand for a unary operation is a number.
    def check_number_operand(self, operator: Token, operand: object):
        if isinstance(operand, float):
            return
        raise RuntimeError(operand, "Operand must be a number.")

    # Ensures both operands for a binary operation are numbers.
    def check_number_operands(self, operator: Token, left: object, right: object):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RuntimeError(operator, "Operands must be numbers.")

    # Evaluates an expression within a grouping, effectively ignoring the parentheses.
    def visit_grouping_expr(self, _expr: Expr.Grouping):
        return self.evaluate(_expr.expression)

    # Determines the truthiness of an object in Lox's logic.
    def is_truthy(self, object: object):
        if object is None:
            return False
        if isinstance(object, bool):
            return bool(object)
        return True

    # Compares two objects for equality in Lox's logic.
    def is_equal(self, a: object, b: object):
        if a is None and b is None:
            return True
        if a is None:
            return False
        return type(a) == type(b) and a == b

    # Converts a Lox object to its string representation.
    def stringify(self, object: object):
        if object is None:
            return "nil"
        if isinstance(object, float):
            text = str(object)
            if text.endswith(".0"):
                text = text[: -2]
            return text
        return str(object)

    # Evaluates an expression by accepting its visitor method.
    def evaluate(self, _expr: Expr.Expr):
        return _expr.accept(self)

    # Executes a statement by accepting its visitor method.
    def execute(self, _stmt: Stmt.Stmt):
        _stmt.accept(self)

    # Records the depth at which a local variable is found for later retrieval.
    def resolve(self, _expr: Expr.Expr, depth: int):
        self.locals[_expr] = depth

    # Executes a block of statements in a new environment scope.
    def execute_block(self, statements: List[Stmt.Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    # Handles the execution of a block statement by creating a new scope.
    def visit_block_stmt(self, _stmt: Stmt.Block):
        self.execute_block(_stmt.statements, Environment(self.environment))
        return None

    # Defines a new class, handling inheritance if a superclass is specified.
    def visit_class_stmt(self, _stmt: Stmt.Class):
        superclass = None
        if _stmt.superclass is not None:
            superclass = self.evaluate(_stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(_stmt.superclass.name, "Superclass must be a class.")
        self.environment.define(_stmt.name.lexme, None)
        if _stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        methods = {}
        for method in _stmt.methods:
            function = LoxFunction(method, self.environment, method.name.lexme == "init")
            methods[method.name.lexme] = function
        klass = LoxClass(_stmt.name.lexme, superclass, methods)
        if superclass is not None:
            self.environment = self.environment.enclosing
        self.environment.assign(_stmt.name, klass)
        return None

    # Evaluates and executes an expression statement.
    def visit_expression_stmt(self, _stmt: Stmt.Stmt):
        self.evaluate(_stmt.expression)
        return None

    # Defines a new function, adding it to the current environment.
    def visit_function_stmt(self, _stmt: Stmt.Function):
        function = LoxFunction(_stmt, self.environment, False)
        self.environment.define(_stmt.name.lexme, function)
        return None

    # Executes the branches of an if statement based on the condition's truthiness.
    def visit_if_stmt(self, _stmt: Stmt.If):
        if self.is_truthy(self.evaluate(_stmt.condition)):
            self.execute(_stmt.then_branch)
        elif _stmt.else_branch is not None:
            self.execute(_stmt.else_branch)
        return None

    # Prints the string representation of an expression's value.
    def visit_print_stmt(self, _stmt: Stmt.Stmt):
        value = self.evaluate(_stmt.expression)
        print(self.stringify(value))
        return None

    # Handles the return statement in a function, throwing a special exception.
    def visit_return_stmt(self, _stmt: Stmt.Return):
        value = None
        if _stmt.value is not None:
            value = self.evaluate(_stmt.value)
        raise Return(value)

    # Defines a variable in the current environment, optionally initialising it.
    def visit_var_stmt(self, _stmt: Stmt.Var):
        value = None
        if _stmt.initializer is not None:
            value = self.evaluate(_stmt.initializer)
        self.environment.define(_stmt.name.lexme, value)
        return None

    # Repeatedly executes a statement while the condition is truthy.
    def visit_while_stmt(self, _stmt: Stmt.While):
        while self.is_truthy(self.evaluate(_stmt.condition)):
            self.execute(_stmt.body)
        return None

    # Assigns a new value to a variable, handling both local and global scopes.
    def visit_assign_expr(self, _expr: Expr.Assign):
        value = self.evaluate(_expr.value)
        if _expr in self.locals:
            distance = self.locals[_expr]
            self.environment.assign_at(distance, _expr.name, value)
        else:
            self.globals.assign(_expr.name, value)
        return value

    # Evaluates a binary expression, performing the specified arithmetic or logical operation.
    def visit_binary_expr(self, _expr: Expr.Binary):
        left = self.evaluate(_expr.left)
        right = self.evaluate(_expr.right)
        # Handles each binary operator by performing the appropriate operation.
        if _expr.operator.type == TokenType.GREATER:
            self.check_number_operands(_expr.operator, left, right)
            return float(left) > float(right)
        elif _expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_number_operands(_expr.operator, left, right)
            return float(left) >= float(right)
        elif _expr.operator.type == TokenType.LESS:
            self.check_number_operands(_expr.operator, left, right)
            return float(left) < float(right)
        elif _expr.operator.type == TokenType.LESS_EQUAL:
            self.check_number_operands(_expr.operator, left, right)
            return float(left) <= float(right)
        elif _expr.operator.type == TokenType.MINUS:
            self.check_number_operands(_expr.operator, left, right)
            return float(left) - float(right)
        elif _expr.operator.type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            if isinstance(left, float) and isinstance(right, str):
                return str(left) + right
            if isinstance(left, str) and isinstance(right, float):
                return left + str(right)
            raise RuntimeError(_expr.operator, "Operands must be two numbers or two strings.")
        elif _expr.operator.type == TokenType.SLASH:
            return float(left) / float(right)
        elif _expr.operator.type == TokenType.STAR:
            self.check_number_operands(_expr.operator, left, right)
            return float(left) * float(right)
        elif _expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif _expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        # Unreachable, but included for completeness.
        return None

    # Calls a function or class constructor, evaluating its arguments and executing it.
    def visit_call_expr(self, _expr: Expr.Call):
        callee = self.evaluate(_expr.callee)
        arguments = []
        for argument in _expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee, LoxCallable):
            raise RuntimeError(_expr.paren, "Can only call functions and classes.")
        function = callee
        if len(arguments) != function.arity():
            raise RuntimeError(_expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")
        return function.call(self, arguments)

    # Retrieves a property from an object instance, throwing an error if the object is not an instance.
    def visit_get_expr(self, _expr: Expr.Get):
        _object = self.evaluate(_expr.object)
        if isinstance(_object, LoxInstance):
            return _object.get(_expr.name)
        raise RuntimeError(_expr.name, "Only instances have properties.")
