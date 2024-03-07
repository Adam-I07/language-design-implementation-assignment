import Expr
import Stmt
from Token import Token
from Interpreter import Interpreter
from Error_reporter import error_reporter
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
        self._interpreter = interpreter
        self._scopes = []
        self._current_function = FunctionType.NONE
        self._current_class = ClassType.NONE

    @singledispatchmethod
    def _overloaded_resolve(self, arg) -> None:
        return NotImplemented

    @_overloaded_resolve.register
    def _(self, statements: list) -> None:
        for statement in statements:
            self._overloaded_resolve(statement)

    @_overloaded_resolve.register
    def _(self, _stmt: Stmt.Stmt) -> None:
        _stmt.accept(self)

    @_overloaded_resolve.register
    def _(self, _expr: Expr.Expr) -> None:
        _expr.accept(self)

    @overload
    def _resolve(self, statements: List[Stmt.Stmt]) -> None:
        ...

    @overload
    def _resolve(self, _stmt: Stmt.Stmt) -> None:
        ...

    @overload
    def _resolve(self, _expr: Expr.Expr) -> None:
        ...

    def _resolve(self, *args, **kwargs) -> None:
        return self._overloaded_resolve(*args, **kwargs)

    def _resolve_function(self, function: Stmt.Function, type: FunctionType) -> None:
        enclosing_function = self._current_function
        self._current_function = type

        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)
        self._resolve(function.body)
        self._end_scope()
        self._current_function = enclosing_function

    def _begin_scope(self) -> None:
        self._scopes.append({})

    def _end_scope(self) -> None:
        self._scopes.pop()

    def _declare(self, name: Token) -> None:
        if len(self._scopes) == 0:
            return

        if name.lexme in self._scopes[-1]:
            error_reporter.error(
                name, "Already a variable with this name in this scope."
            )

        self._scopes[-1][name.lexme] = False

    def _define(self, name: Token) -> None:
        if len(self._scopes) == 0:
            return
        self._scopes[-1][name.lexme] = True

    def _resolve_local(self, _expr: Expr.Expr, name: Token) -> None:
        for idx in range(len(self._scopes) - 1, -1, -1):
            if name.lexme in self._scopes[idx]:
                self._interpreter.resolve(_expr, len(self._scopes) - 1 - idx)
                return

    def visit_block_stmt(self, _stmt: Stmt.Block) -> None:
        self._begin_scope()
        self._resolve(_stmt.statements)
        self._end_scope()
        return None

    def visit_expression_stmt(self, _stmt: Stmt.Expression) -> None:
        self._resolve(_stmt.expression)
        return None

    def visit_class_stmt(self, _stmt: Stmt.Class) -> None:
        enclosing_class = self._current_class
        self._current_class = ClassType.CLASS

        self._declare(_stmt.name)
        self._define(_stmt.name)

        if (
            _stmt.superclass is not None
            and _stmt.name.lexme == _stmt.superclass.name.lexme
        ):
            error_reporter.error(
                _stmt.superclass.name, "A class can't inherit from itself."
            )

        if _stmt.superclass is not None:
            self._current_class = ClassType.SUBCLASS
            self._resolve(_stmt.superclass)

        if _stmt.superclass is not None:
            self._begin_scope()
            self._scopes[-1]["super"] = True

        self._begin_scope()
        self._scopes[-1]["this"] = True

        for method in _stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexme == "init":
                declaration = FunctionType.INTIALIZER

            self._resolve_function(method, declaration)

        self._end_scope()

        if _stmt.superclass is not None:
            self._end_scope()

        self._current_class = enclosing_class
        return None

    def visit_if_stmt(self, _stmt: Stmt.If) -> None:
        self._resolve(_stmt.condition)
        self._resolve(_stmt.then_branch)
        if _stmt.else_branch is not None:
            self._resolve(_stmt.else_branch)
        return None

    def visit_print_stmt(self, _stmt: Stmt.Print) -> None:
        self._resolve(_stmt.expression)
        return None

    def visit_return_stmt(self, _stmt: Stmt.Return) -> None:
        if self._current_function == FunctionType.NONE:
            error_reporter.error(_stmt.keyword, "Can't return from top-level code.")

        if _stmt.value is not None:
            if self._current_function == FunctionType.INTIALIZER:
                error_reporter.error(
                    _stmt.keyword, "Can't return a value from an initializer."
                )

            self._resolve(_stmt.value)

        return None

    def visit_function_stmt(self, _stmt: Stmt.Function) -> None:
        self._declare(_stmt.name)
        self._define(_stmt.name)

        self._resolve_function(_stmt, FunctionType.FUNCTION)
        return None

    def visit_var_stmt(self, _stmt: Stmt.Var) -> None:
        self._declare(_stmt.name)
        if _stmt.initializer is not None:
            self._resolve(_stmt.initializer)
        self._define(_stmt.name)
        return None

    def visit_while_stmt(self, _stmt: Stmt.While) -> None:
        self._resolve(_stmt.condition)
        self._resolve(_stmt.body)
        return None

    def visit_assign_expr(self, _expr: Expr.Assign) -> None:
        self._resolve(_expr.value)
        self._resolve_local(_expr, _expr.name)
        return None

    def visit_binary_expr(self, _expr: Expr.Binary) -> None:
        self._resolve(_expr.left)
        self._resolve(_expr.right)
        return None

    def visit_call_expr(self, _expr: Expr.Call) -> None:
        self._resolve(_expr.callee)

        for argument in _expr.arguments:
            self._resolve(argument)

        return None

    def visit_get_expr(self, _expr: Expr.Get) -> None:
        self._resolve(_expr.object)
        return None

    def visit_grouping_expr(self, _expr: Expr.Grouping) -> None:
        self._resolve(_expr.expression)
        return None

    def visit_literal_expr(self, _expr: Expr.Literal) -> None:
        return None

    def visit_logical_expr(self, _expr: Expr.Logical) -> None:
        self._resolve(_expr.left)
        self._resolve(_expr.right)
        return None

    def visit_set_expr(self, _expr: Expr.Set) -> None:
        self._resolve(_expr.value)
        self._resolve(_expr.object)
        return None

    def visit_super_expr(self, _expr: Expr.Super) -> None:
        if self._current_class == ClassType.NONE:
            error_reporter.error(_expr.keyword, "Can't use 'super' outside of a class.")
        elif self._current_class != ClassType.SUBCLASS:
            error_reporter.error(
                _expr.keyword, "Can't use 'super' in a class with no superclass."
            )

        self._resolve_local(_expr, _expr.keyword)
        return None

    def visit_this_expr(self, _expr: Expr.This) -> None:
        if self._current_class == ClassType.NONE:
            error_reporter.error(_expr.keyword, "Can't use 'this' outside of a class.")
            return None

        self._resolve_local(_expr, _expr.keyword)
        return None

    def visit_unary_expr(self, _expr: Expr.Unary) -> None:
        self._resolve(_expr.right)
        return None

    def visit_variable_expr(self, _expr: Expr.Variable) -> None:
        if (
            len(self._scopes) > 0
            and _expr.name.lexme in self._scopes[-1]
            and not self._scopes[-1][_expr.name.lexme]
        ):
            error_reporter.error(
                _expr.name, "Can't read local variable in its own initializer."
            )

        self._resolve_local(_expr, _expr.name)
        return None
