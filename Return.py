# Exception class used for returning values from functions.
class Return(Exception):
    # Initialises a new Return exception with a specific value.
    def __init__(self, value: object):
        super().__init__(value)  # Pass the value to the base class constructor.
        self.value = value  # Store the value to be returned.
