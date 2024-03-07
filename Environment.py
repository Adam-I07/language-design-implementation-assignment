from typing import Self
from Token import Token
from Runtime_error import RuntimeError


class Environment:
    def __init__(self, enclosing: Self = None):
        self.enclosing = enclosing
        self._values = {}

    def get(self, name: Token) -> object:
        if name.lexme in self._values:
            return self._values[name.lexme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeError(name, f"Undefined variable '{name.lexme}'.")

    def assign(self, name: Token, value: object) -> None:
        if name.lexme in self._values:
            self._values[name.lexme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(name, f"Undefined variable '{name.lexme}'")

    def define(self, name: str, value: object) -> None:
        self._values[name] = value

    def ancestor(self, distance: int) -> Self:
        environment = self
        for _ in range(distance):
            environment = environment.enclosing

        return environment

    def get_at(self, distance: int, name: str) -> object:
        return self.ancestor(distance)._values[name]

    def assign_at(self, distance: int, name: Token, value: object) -> None:
        self.ancestor(distance)._values[name.lexme] = value
