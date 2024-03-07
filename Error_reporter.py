import sys
from functools import singledispatchmethod
from Token import Token
from Token_type import TokenType
from Runtime_error import RuntimeError


class ErrorReporter:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    @singledispatchmethod
    def error(self, arg, msg: str) -> None:
        pass

    @error.register
    def _(self, line: int, msg: str) -> None:
        self.report(line, "", msg)

    def report(self, line: int, where: str, msg: str) -> None:
        print(f"[line {line}] Error{where}: {msg}", file=sys.stderr)
        self.had_error = True

    @error.register
    def _(self, token: Token, msg: str) -> None:
        if token.type == TokenType.EOF:
            self.report(token.line, " at end", msg)
        else:
            self.report(token.line, f" at '{token.lexme}'", msg)

    def runtime_error(self, error: RuntimeError) -> None:
        print(f"{repr(error)}\n[line {error.token.line}]", file=sys.stderr)
        self.had_runtime_error = True


error_reporter = ErrorReporter()
