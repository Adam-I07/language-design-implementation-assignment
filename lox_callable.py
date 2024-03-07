from typing import List

class LoxCallable:
    def __init__(self):
        pass

    def arity(self) -> int:
        pass

    def call(self, interpreter: "Interpreter", arguments: List[object]) -> object:
        pass

    def to_string(self) -> str:
        pass
