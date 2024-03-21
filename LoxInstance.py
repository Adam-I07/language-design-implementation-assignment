from Token import Token
from RuntimeError import RuntimeError


class LoxInstance:
    def __init__(self, klass: "LoxClass"):
        self._klass = klass
        self._fields = {}

    def __str__(self) -> str:
        return f"{self._klass._name} instance"

    def get(self, name: Token) -> object:
        if name.lexme in self._fields:
            return self._fields[name.lexme]

        method = self._klass.find_method(name.lexme)
        if method is not None:
            return method.bind(self)

        raise RuntimeError(name, f"Undefined property '{name.lexme}'.")

    def set(self, name: Token, value: object) -> None:
        self._fields[name.lexme] = value
