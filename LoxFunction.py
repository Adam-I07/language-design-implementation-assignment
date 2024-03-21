from typing import List, Self
from Return import Return
from Environment import Environment
from LoxCallable import LoxCallable
from LoxInstance import LoxInstance
from Stmt import Function


class LoxFunction(LoxCallable):
    def __init__(
        self, declaration: Function, closure: Environment, is_initializer: bool
    ):
        self._is_initializer = is_initializer
        self._closure = closure
        self._declaration = declaration

    def bind(self, instance: LoxInstance) -> Self:
        environment = Environment(self._closure)
        environment.define("this", instance)
        return LoxFunction(self._declaration, environment, self._is_initializer)

    def to_string(self) -> str:
        return f"fn {self._declaration.name.lexme}>"

    def arity(self) -> int:
        return len(self._declaration.params)

    def call(self, interpreter: "Interpreter", arguments: List[object]) -> object:
        environment = Environment(self._closure)
        for idx, param in enumerate(self._declaration.params):
            environment.define(param.lexme, arguments[idx])

        try:
            interpreter.execute_block(self._declaration.body, environment)
        except Return as return_value:
            if self._is_initializer:
                return self._closure.get_at(0, "this")

            return return_value.value

        if self._is_initializer:
            return self._closure.get_at(0, "this")
        return None
