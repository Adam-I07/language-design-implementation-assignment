import Expr
import Stmt
from Token import Token
from Interpreter import Interpreter
from ErrorReporter import error_reporter
from enum import Enum
from typing import List, overload
from functools import singledispatchmethod


class FunctionType(Enum):
    NONE = 1
    FUNCTION = 2
    INTIALIZER = 3
    METHOD = 4


class ClassType(Enum):
    NONE = 1
    CLASS = 2
    SUBCLASS = 3


class Resolver(Expr.Visitor[None], Stmt.Visitor[None]):
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    @singledispatchmethod
    def overloaded_resolve(self, arg):
        return NotImplemented

    @overloaded_resolve.register
    def _(self, statements: list):
        for statement in statements:
            self.overloaded_resolve(statement)

    @overloaded_resolve.register
    def _(self, _stmt: Stmt.Stmt):
        _stmt.accept(self)

    @overloaded_resolve.register
    def _(self, _expr: Expr.Expr):
        _expr.accept(self)

    @overload
    def resolve(self, statements: List[Stmt.Stmt]):
        ...

    @overload
    def resolve(self, _stmt: Stmt.Stmt):
        ...

    @overload
    def resolve(self, _expr: Expr.Expr):
        ...

    def resolve(self, *args, **kwargs):
        return self.overloaded_resolve(*args, **kwargs)

    def resolve_function(self, function: Stmt.Function, type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return

        if name.lexme in self.scopes[-1]:
            error_reporter.error(
                name, "Already a variable with this name in this scope."
            )

        self.scopes[-1][name.lexme] = False

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name.lexme] = True

    def resolve_local(self, _expr: Expr.Expr, name: Token):
        for idx in range(len(self.scopes) - 1, -1, -1):
            if name.lexme in self.scopes[idx]:
                self.interpreter.resolve(_expr, len(self.scopes) - 1 - idx)
                return

    def visit_block_stmt(self, _stmt: Stmt.Block):
        self.begin_scope()
        self.resolve(_stmt.statements)
        self.end_scope()
        return None

    def visit_expression_stmt(self, _stmt: Stmt.Expression):
        self.resolve(_stmt.expression)
        return None

    def visit_class_stmt(self, _stmt: Stmt.Class):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(_stmt.name)
        self.define(_stmt.name)
        if (_stmt.superclass is not None and _stmt.name.lexme == _stmt.superclass.name.lexme):
            error_reporter.error(_stmt.superclass.name, "A class can't inherit from itself.")
        if _stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            self.resolve(_stmt.superclass)
        if _stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True
        self.begin_scope()
        self.scopes[-1]["this"] = True
        for method in _stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexme == "init":
                declaration = FunctionType.INTIALIZER
            self.resolve_function(method, declaration)
        self.end_scope()
        if _stmt.superclass is not None:
            self.end_scope()
        self.current_class = enclosing_class
        return None

    def visit_if_stmt(self, _stmt: Stmt.If):
        self.resolve(_stmt.condition)
        self.resolve(_stmt.then_branch)
        if _stmt.else_branch is not None:
            self.resolve(_stmt.else_branch)
        return None

    def visit_print_stmt(self, _stmt: Stmt.Print):
        self.resolve(_stmt.expression)
        return None

    def visit_return_stmt(self, _stmt: Stmt.Return):
        if self.current_function == FunctionType.NONE:
            error_reporter.error(_stmt.keyword, "Can't return from top-level code.")

        if _stmt.value is not None:
            if self.current_function == FunctionType.INTIALIZER:
                error_reporter.error(_stmt.keyword, "Can't return a value from an initializer.")
            self.resolve(_stmt.value)

        return None

    def visit_function_stmt(self, _stmt: Stmt.Function):
        self.declare(_stmt.name)
        self.define(_stmt.name)

        self.resolve_function(_stmt, FunctionType.FUNCTION)
        return None

    def visit_var_stmt(self, _stmt: Stmt.Var):
        self.declare(_stmt.name)
        if _stmt.initializer is not None:
            self.resolve(_stmt.initializer)
        self.define(_stmt.name)
        return None

    def visit_while_stmt(self, _stmt: Stmt.While):
        self.resolve(_stmt.condition)
        self.resolve(_stmt.body)
        return None

    def visit_assign_expr(self, _expr: Expr.Assign):
        self.resolve(_expr.value)
        self.resolve_local(_expr, _expr.name)
        return None

    def visit_binary_expr(self, _expr: Expr.Binary):
        self.resolve(_expr.left)
        self.resolve(_expr.right)
        return None

    def visit_call_expr(self, _expr: Expr.Call):
        self.resolve(_expr.callee)

        for argument in _expr.arguments:
            self.resolve(argument)

        return None

    def visit_get_expr(self, _expr: Expr.Get):
        self.resolve(_expr.object)
        return None

    def visit_grouping_expr(self, _expr: Expr.Grouping):
        self.resolve(_expr.expression)
        return None

    def visit_literal_expr(self, _expr: Expr.Literal):
        return None

    def visit_logical_expr(self, _expr: Expr.Logical):
        self.resolve(_expr.left)
        self.resolve(_expr.right)
        return None

    def visit_set_expr(self, _expr: Expr.Set):
        self.resolve(_expr.value)
        self.resolve(_expr.object)
        return None

    def visit_super_expr(self, _expr: Expr.Super):
        if self.current_class == ClassType.NONE:
            error_reporter.error(_expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            error_reporter.error(_expr.keyword, "Can't use 'super' in a class with no superclass.")

        self.resolve_local(_expr, _expr.keyword)
        return None

    def visit_this_expr(self, _expr: Expr.This):
        if self.current_class == ClassType.NONE:
            error_reporter.error(_expr.keyword, "Can't use 'this' outside of a class.")
            return None

        self.resolve_local(_expr, _expr.keyword)
        return None

    def visit_unary_expr(self, _expr: Expr.Unary):
        self.resolve(_expr.right)
        return None

    def visit_variable_expr(self, _expr: Expr.Variable):
        if (len(self.scopes) > 0 and _expr.name.lexme in self.scopes[-1] and not self.scopes[-1][_expr.name.lexme]):
            error_reporter.error(_expr.name, "Can't read local variable in its own initialiser.")
        self.resolve_local(_expr, _expr.name)
        return None