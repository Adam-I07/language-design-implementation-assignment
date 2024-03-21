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
    def __init__(self):
        self.globals = Environment()
        self._environment = self.globals
        self._locals = {}
        self.globals.define("input", LoxInput())

        def _arity(self) -> int:
            return 0

        def _call(self, interpreter: Self, arguments: List[object]) -> object:
            return float(time())

        def _to_string(self) -> str:
            return "<native fn>"

        clock = LoxCallable()
        clock.arity = MethodType(_arity, clock)
        clock.call = MethodType(_call, clock)
        clock.to_string = MethodType(_to_string, clock)

        self.globals.define("clock", clock)

    def interpret(self, statements: List[Stmt.Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            error_reporter.runtime_error(error)

    def visit_literal_expr(self, _expr: Expr.Literal) -> object:
        return _expr.value

    def visit_logical_expr(self, _expr: Expr.Logical) -> object:
        left = self.evaluate(_expr.left)

        if _expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(_expr.right)

    def visit_set_expr(self, _expr: Expr.Set) -> object:
        _object = self.evaluate(_expr.object)

        if not isinstance(_object, LoxInstance):
            raise RuntimeError(_expr.name, "Only instances have fields.")

        value = self.evaluate(_expr.value)
        _object.set(_expr.name, value)
        return value

    def visit_super_expr(self, _expr: Expr.Super) -> object:
        distance = self._locals.get(_expr)
        superclass = self._environment.get_at(distance, "super")

        _object = self._environment.get_at(distance - 1, "this")

        method = superclass.find_method(_expr.method.lexme)

        if method is None:
            raise RuntimeError(
                _expr.method, f"Undefined property '{_expr.method.lexme}'."
            )

        return method.bind(_object)

    def visit_this_expr(self, _expr: Expr.This) -> object:
        return self.look_up_variable(_expr.keyword, _expr)

    def visit_unary_expr(self, _expr: Expr.Unary) -> object:
        right = self.evaluate(_expr.right)

        if _expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        elif _expr.operator.type == TokenType.MINUS:
            self.check_number_operand(_expr.operator, right)
            return -float(right)

        # Unreachable
        return None

    def visit_variable_expr(self, _expr: Expr.Variable) -> object:
        return self.look_up_variable(_expr.name, _expr)

    def look_up_variable(self, name: Token, _expr: Expr.Expr) -> object:
        if _expr in self._locals:
            distance = self._locals[_expr]
            return self._environment.get_at(distance, name.lexme)
        else:
            return self.globals.get(name)

    def check_number_operand(self, operator: Token, operand: object) -> None:
        if isinstance(operand, float):
            return
        raise RuntimeError(operand, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: object, right: object) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RuntimeError(operator, "Operands must be numbers.")

    def visit_grouping_expr(self, _expr: Expr.Grouping) -> object:
        return self.evaluate(_expr.expression)

    def is_truthy(self, object: object) -> bool:
        if object is None:
            return False
        if isinstance(object, bool):
            return bool(object)
        return True

    def is_equal(self, a: object, b: object) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False

        # Only objects of same types can be equal
        return type(a) == type(b) and a == b

    def stringify(self, object: object) -> str:
        if object is None:
            return "nil"
        if isinstance(object, float):
            text = str(object)
            if text.endswith(".0"):
                text = text[: len(text) - 2]
            return text
        return str(object)

    def evaluate(self, _expr: Expr.Expr) -> object:
        return _expr.accept(self)

    def execute(self, _stmt: Stmt.Stmt) -> None:
        _stmt.accept(self)

    def resolve(self, _expr: Expr.Expr, depth: int) -> None:
        self._locals[_expr] = depth

    def execute_block(
        self, statements: List[Stmt.Stmt], environment: Environment
    ) -> None:
        previous = self._environment
        try:
            self._environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self._environment = previous

    def visit_block_stmt(self, _stmt: Stmt.Block) -> None:
        self.execute_block(_stmt.statements, Environment(self._environment))
        return None

    def visit_class_stmt(self, _stmt: Stmt.Class) -> None:
        superclass = None
        if _stmt.superclass is not None:
            superclass = self.evaluate(_stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(_stmt.superclass.name, "Superclass must be a class.")

        self._environment.define(_stmt.name.lexme, None)

        if _stmt.superclass is not None:
            self._environment = Environment(self._environment)
            self._environment.define("super", superclass)

        methods = {}
        for method in _stmt.methods:
            function = LoxFunction(
                method, self._environment, method.name.lexme == "init"
            )
            methods[method.name.lexme] = function

        klass = LoxClass(_stmt.name.lexme, superclass, methods)

        if superclass is not None:
            self._environment = self._environment.enclosing

        self._environment.assign(_stmt.name, klass)
        return None

    def visit_expression_stmt(self, _stmt: Stmt.Stmt) -> None:
        self.evaluate(_stmt.expression)
        return None

    def visit_function_stmt(self, _stmt: Stmt.Function) -> None:
        function = LoxFunction(_stmt, self._environment, False)
        self._environment.define(_stmt.name.lexme, function)
        return None

    def visit_if_stmt(self, _stmt: Stmt.If) -> None:
        if self.is_truthy(self.evaluate(_stmt.condition)):
            self.execute(_stmt.then_branch)
        elif _stmt.else_branch is not None:
            self.execute(_stmt.else_branch)
        return None

    def visit_print_stmt(self, _stmt: Stmt.Stmt) -> None:
        value = self.evaluate(_stmt.expression)
        print(self.stringify(value))
        return None

    def visit_return_stmt(self, _stmt: Stmt.Return) -> None:
        value = None
        if _stmt.value is not None:
            value = self.evaluate(_stmt.value)

        raise Return(value)

    def visit_var_stmt(self, _stmt: Stmt.Var) -> None:
        value = None
        if _stmt.initializer is not None:
            value = self.evaluate(_stmt.initializer)

        self._environment.define(_stmt.name.lexme, value)
        return None

    def visit_while_stmt(self, _stmt: Stmt.While) -> None:
        while self.is_truthy(self.evaluate(_stmt.condition)):
            self.execute(_stmt.body)
        return None

    def visit_assign_expr(self, _expr: Expr.Assign) -> object:
        value = self.evaluate(_expr.value)

        if _expr in self._locals:
            distance = self._locals[_expr]
            self._environment.assign_at(distance, _expr.name, value)
        else:
            self.globals.assign(_expr.name, value)

        return value

    def visit_binary_expr(self, _expr: Expr.Binary) -> object:
        left = self.evaluate(_expr.left)
        right = self.evaluate(_expr.right)

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
            raise RuntimeError(
                _expr.operator, "Operands must be two numbers or two strings."
            )
        elif _expr.operator.type == TokenType.SLASH:
            return float(left) / float(right)
        elif _expr.operator.type == TokenType.STAR:
            self.check_number_operands(_expr.operator, left, right)
            return float(left) * float(right)
        elif _expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif _expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        # Unreachable
        return None

    def visit_call_expr(self, _expr: Expr.Call) -> object:
        callee = self.evaluate(_expr.callee)

        arguments = []
        for argument in _expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(_expr.paren, "Can only call functions and classes.")

        function = callee
        if len(arguments) != function.arity():
            raise RuntimeError(
                _expr.paren,
                f"Expected {function.arity()} arguments but got {len(arguments)}.",
            )

        return function.call(self, arguments)

    def visit_get_expr(self, _expr: Expr.Get) -> object:
        _object = self.evaluate(_expr.object)
        if isinstance(_object, LoxInstance):
            return _object.get(_expr.name)

        raise RuntimeError(_expr.name, "Only instances have properties.")
