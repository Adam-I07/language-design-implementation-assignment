class Return(Exception):
    # Initialise Return exception with a value to be returned
    def __init__(self, value: object):
        super().__init__(value)  # Call the base class constructor with the return value
        self.value = value  # Store the return value for later retrieval