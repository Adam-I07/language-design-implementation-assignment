from LoxCallable import LoxCallable

class LoxInput(LoxCallable):
    def call(self, interpreter, arguments):
        prompt = ""
        if len(arguments) > 0:
            prompt = str(arguments[0])
        return input(prompt)

    def arity(self):
        return 1