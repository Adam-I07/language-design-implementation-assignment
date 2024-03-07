from Token import Token

class RuntimeError(Exception):
    def __init__(self, token: Token, msg: str):
        super().__init__(msg)
        self.token = token
