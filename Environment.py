"""
Manages a nested scope environment for variable storage and retrieval. Each environment can have a parent environment,
creating a chain. Provides methods to define new variables (define), assign values to existing variables (assign), 
and retrieve variable values (get). It also supports creating isolated environments for different execution contexts, 
facilitating scope management. 
"""
from typing import Self
from Token import Token
from RuntimeError import RuntimeError


class Environment:
   # Initialise the environment with an optional enclosing environment.
    def __init__(self, enclosing: Self = None):
        # The possibly outer environment this one is enclosed by.
        self.enclosing = enclosing
        # Dictionary to hold variable names and their values.
        self.values = {}

    # Retrieve a variable's value by its name, searching in the current and enclosing environments.
    def get(self, name: Token):
        # If the variable exists in the current environment, return its value.
        if name.lexme in self.values:
            return self.values[name.lexme]
        # If not found, attempt to retrieve from an enclosing environment, if one exists.
        if self.enclosing is not None:
            return self.enclosing.get(name)
        # If the variable is not defined in any accessible environment, raise an error.
        raise RuntimeError(name, f"Undefined variable '{name.lexme}'.")

    # Assign a new value to a variable in the current or an enclosing environment.
    def assign(self, name: Token, value: object):
        # If the variable exists in the current environment, update its value.
        if name.lexme in self.values:
            self.values[name.lexme] = value
            return
        # If not found and an enclosing environment exists, attempt to assign there.
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        # If the variable is not defined in any accessible environment, raise an error.
        raise RuntimeError(name, f"Undefined variable '{name.lexme}'")

    # Define a new variable or update an existing variable's value in the current environment.
    def define(self, name: str, value: object):
        # Directly set or update the variable's value in the current environment.
        self.values[name] = value

    # Retrieve the environment at a specified distance away in the enclosure chain.
    def ancestor(self, distance: int):
        # Start with the current environment.
        environment = self
        # Move 'distance' levels up the enclosure chain.
        for _ in range(distance):
            environment = environment.enclosing
        # Return the ancestor environment found at the specified distance.
        return environment

    # Retrieve a variable's value from an environment a specific distance away.
    def get_at(self, distance: int, name: str):
        # Find the ancestor environment and retrieve the variable's value from it.
        return self.ancestor(distance).values[name]

    # Assign a new value to a variable in an environment a specific distance away.
    def assign_at(self, distance: int, name: Token, value: object):
        # Find the ancestor environment and update the variable's value in it.
        self.ancestor(distance).values[name.lexme] = value
