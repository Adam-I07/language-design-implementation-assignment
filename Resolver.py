import Expr
import Stmt
from Token import Token
from Interpreter import Interpreter
from ErrorReporter import error_reporter
from enum import Enum
from typing import List, overload
from functools import singledispatchmethod

# Enum defining types of functions to distinguish between regular functions, initializers, and class methods.
class FunctionType(Enum):
    NONE = 1
    FUNCTION = 2
    INTIALIZER = 3
    METHOD = 4

# Enum defining types of classes to differentiate between base classes, subclasses, or no class.
class ClassType(Enum):
    NONE = 1
    CLASS = 2
    SUBCLASS = 3


class Resolver(Expr.Visitor[None], Stmt.Visitor[None]):
    def __init__(self, interpreter: Interpreter):
        # Store a reference to the Interpreter instance passed during the creation of this object.
        self.interpreter = interpreter
        # Initialise an empty list to manage scopes. This will be used to track variable scopes and their bindings.
        self.scopes = []
        # Set the initial function context to NONE, indicating that the current context is not within a function.
        self.current_function = FunctionType.NONE
        # Set the initial class context to NONE, indicating that the current context is not within a class.
        self.current_class = ClassType.NONE

    # Utilises singledispatchmethod for method overloading based on argument type, enabling different handling for various input types.
    @singledispatchmethod
    def overloaded_resolve(self, arg):
        # Default implementation of overloaded_resolve that returns NotImplemented if the argument type isn't explicitly handled.
        return NotImplemented

    # Register a specific implementation of overloaded_resolve for lists, allowing batch processing of items
    @overloaded_resolve.register
    def _(self, statements: list):
        # Iterates over each statement in the list, recursively calling overloaded_resolve to handle each one based on its type.
        for statement in statements:
            self.overloaded_resolve(statement)

    # Register an implementation for handling statements, defining specific behavior for statement objects.
    @overloaded_resolve.register
    def _(self, _stmt: Stmt.Stmt):
        # Directs the statement object to accept a visitor (in this case, 'self'), following the Visitor design pattern.
        _stmt.accept(self)

    # Register an implementation for handling expressions, defining specific behavior for expression objects.
    @overloaded_resolve.register
    def _(self, _expr: Expr.Expr):
        # Directs the expression object to accept a visitor (in this case, 'self'), following the Visitor design pattern.
        _expr.accept(self)

    # Type hints for the resolve method indicating it can handle different types of arguments through overloading.
    @overload
    def resolve(self, statements: List[Stmt.Stmt]):
        ...

    @overload
    def resolve(self, _stmt: Stmt.Stmt):
        ...

    @overload
    def resolve(self, _expr: Expr.Expr):
        ...

    # The main resolve method that delegates to overloaded_resolve, utilising the method overloading mechanism to handle various argument types.
    def resolve(self, *args, **kwargs):
        return self.overloaded_resolve(*args, **kwargs)

    # Prepares and resolves the environment for a function, handling scope and parameters based on the function type.
    def resolve_function(self, function: Stmt.Function, type: FunctionType):
        # Save the current function context to restore it after resolving the new function.
        enclosing_function = self.current_function
        # Set the current function context to the type of the function being resolved.
        self.current_function = type
        # Start a new scope for the function's parameters and body.
        self.begin_scope()
        # Iterate over each parameter in the function's definition.
        for param in function.params:
            # Declare the parameter in the current scope to ensure it's recognized before it's defined.
            self.declare(param)
            # Define the parameter in the scope, making it available for use within the function.
            self.define(param)
        # Resolve the body of the function, handling any variables or nested functions.
        self.resolve(function.body)
        # End the current scope, popping it off the scope stack and cleaning up.
        self.end_scope()
        # Restore the previous function context now that the function's resolution is complete.
        self.current_function = enclosing_function

    # begin scope starts a new scope. Scopes are used to track variables and their states.
    def begin_scope(self):
        # Append a new, empty dictionary to the scopes list to represent a new scope.
        self.scopes.append({})

    # end scope ends the current scope, effectively removing the most recent scope.
    def end_scope(self):
        # Remove the last dictionary from the scopes list, which represents ending the current scope.
        self.scopes.pop()

    # declares a new variable in the current scope. It checks for variable name uniqueness within the scope.
    def declare(self, name: Token):
        # If there are no scopes, do nothing. This means we're not within a valid scope to declare variables.
        if len(self.scopes) == 0:
            return
        # If the variable name already exists in the current scope, report an error.
        if name.lexme in self.scopes[-1]:
            error_reporter.error(name, "Already a variable with this name in this scope.")
        # Add the variable to the current scope and mark it as not yet defined (False).
        self.scopes[-1][name.lexme] = False

    # define marks a previously declared variable in the current scope as defined.
    def define(self, name: Token):
        # If there are no scopes, do nothing. This means we're not within a valid scope to define variables.
        if len(self.scopes) == 0:
            return
        # Mark the variable in the current scope as defined (True).
        self.scopes[-1][name.lexme] = True

    # Finds and resolves the scope depth of a local variable.
    def resolve_local(self, _expr: Expr.Expr, name: Token):
        # Loop over scopes from innermost to outermost to find variable's scope.
        for idx in range(len(self.scopes) - 1, -1, -1):
            # If variable found in current scope
            if name.lexme in self.scopes[idx]:  
                # Tell interpreter variable's depth.
                self.interpreter.resolve(_expr, len(self.scopes) - 1 - idx)  
                # Exit after resolving to avoid unnecessary iterations.
                return  

    # Processes a block statement, handling scopes for statements within it.
    def visit_block_stmt(self, _stmt: Stmt.Block):
        # Start a new scope for the block.
        self.begin_scope()  
        # Resolve all statements within the block.
        self.resolve(_stmt.statements) 
        # End the block's scope.
        self.end_scope() 
        # Explicitly return None for clarity.
        return None  

    # Processes an expression statement.
    def visit_expression_stmt(self, _stmt: Stmt.Expression):
        # Resolve the expression in the statement.
        self.resolve(_stmt.expression)  
        # Explicitly return None for clarity.
        return None  
    
    # Handles the declaration and setup of classes, including inheritance.
    def visit_class_stmt(self, _stmt: Stmt.Class):
        # Save the current class context.
        enclosing_class = self.current_class 
        # Set current class type to CLASS. 
        self.current_class = ClassType.CLASS  
        # Declare the class name in the current scope.
        self.declare(_stmt.name) 
        # Define the class name in the current scope. 
        self.define(_stmt.name)  
        # Prevent a class from inheriting from itself.
        if (_stmt.superclass is not None and _stmt.name.lexme == _stmt.superclass.name.lexme):
            error_reporter.error(_stmt.superclass.name, "A class can't inherit from itself.")
        # Setup for a subclass.
        if _stmt.superclass is not None:  
            # Mark the current class as a SUBCLASS.
            self.current_class = ClassType.SUBCLASS  
            # Resolve the superclass.
            self.resolve(_stmt.superclass)
        # If there is a superclass
        if _stmt.superclass is not None: 
            # Begin a new scope for the superclass.
            self.begin_scope()  
            # Add "super" to the scope to access superclass methods.
            self.scopes[-1]["super"] = True  
        # Start a new scope for "this".
        self.begin_scope()  
        # Add "this" to the scope to refer to the current instance.
        self.scopes[-1]["this"] = True 
        # Resolve each method in the class. 
        for method in _stmt.methods:  
            # Default declaration type is METHOD.
            declaration = FunctionType.METHOD 
            # If method is an initialiser 
            if method.name.lexme == "init":  
                # Set declaration type to INITIALIZER.
                declaration = FunctionType.INTIALIZER  
            # Resolve the method with its type.
            self.resolve_function(method, declaration)  
        # End the scope for "this".
        self.end_scope()  
        # If there was a superclass
        if _stmt.superclass is not None:  
            # End the scope related to the superclass.
            self.end_scope()  
        # Restore the previous class context.
        self.current_class = enclosing_class  
        # Explicitly return None for clarity.s
        return None  

    # Resolves the components of an if statement (condition, then branch, and optional else branch).
    def visit_if_stmt(self, _stmt: Stmt.If):
        # Resolve the condition of the if statement.
        self.resolve(_stmt.condition) 
        # Resolve the then branch. 
        self.resolve(_stmt.then_branch)  
        # If there's an else branch, resolve it too.
        if _stmt.else_branch is not None:  
            self.resolve(_stmt.else_branch)
        # Explicitly return None for clarity.
        return None  

    # Resolves the expression within a print statement.
    def visit_print_stmt(self, _stmt: Stmt.Print):
        # Resolve the expression to be printed.
        self.resolve(_stmt.expression) 
        # Explicitly return None for clarity. 
        return None 

    # Validates and resolves return statements within functions.
    def visit_return_stmt(self, _stmt: Stmt.Return):
        # If not inside a function, error.
        if self.current_function == FunctionType.NONE:  
            error_reporter.error(_stmt.keyword, "Can't return from top-level code.")
        # If there's a return value
        if _stmt.value is not None:  
            # But we're in an initialiser, error.
            if self.current_function == FunctionType.INTIALIZER:  
                error_reporter.error(_stmt.keyword, "Can't return a value from an initialiser.")
                # Resolve the return value.
            self.resolve(_stmt.value)  
        # Explicitly return None for clarity.
        return None  

    # Processes function declarations, setting up their scope and resolving their bodies.
    def visit_function_stmt(self, _stmt: Stmt.Function):
        # Declare the function in the current scope.
        self.declare(_stmt.name)  
        # Define the function, marking it as available in the current scope.
        self.define(_stmt.name)
        # Resolve the function's body.
        self.resolve_function(_stmt, FunctionType.FUNCTION)  
        # Explicitly return None for clarity.
        return None  

    # Handles variable declarations, including optional initializers.
    def visit_var_stmt(self, _stmt: Stmt.Var):
        # Declare the variable in the current scope.
        self.declare(_stmt.name)  
        # If the variable has an initializer, resolve it.
        if _stmt.initializer is not None:  
            self.resolve(_stmt.initializer)
        # Define the variable, marking it as initialised.
        self.define(_stmt.name)  
        # Explicitly return None for clarity.
        return None  

    # Processes while loops, resolving their condition and body.
    def visit_while_stmt(self, _stmt: Stmt.While):
        # Resolve the loop's condition.
        self.resolve(_stmt.condition)  
        # Resolve the loop's body.
        self.resolve(_stmt.body)  
        # Explicitly return None for clarity.
        return None  

    # Processes assignment expressions, resolving the value and the variable being assigned.
    def visit_assign_expr(self, _expr: Expr.Assign):
        # Resolve the expression to be assigned.
        self.resolve(_expr.value)  
        # Resolve the variable to which the value is assigned.
        self.resolve_local(_expr, _expr.name)  
        return None

    # Processes binary expressions, resolving both operands.
    def visit_binary_expr(self, _expr: Expr.Binary):
        # Resolve the left operand.
        self.resolve(_expr.left)  
        # Resolve the right operand.
        self.resolve(_expr.right)  
        return None
    
    # Processes function call expressions, resolving the callee and each argument.
    def visit_call_expr(self, _expr: Expr.Call):
        # Resolve the function or method being called.
        self.resolve(_expr.callee) 
        # Resolve each argument passed to the call. 
        for argument in _expr.arguments:  
            self.resolve(argument)
        return None
    
    # Processes property access expressions, resolving the object being accessed.
    def visit_get_expr(self, _expr: Expr.Get):
        # Resolve the object whose property is being accessed.
        self.resolve(_expr.object)  
        return None

    # Processes expressions within parentheses, resolving the inner expression.
    def visit_grouping_expr(self, _expr: Expr.Grouping):
        # Resolve the expression inside the parentheses.
        self.resolve(_expr.expression)  
        return None

    # Processes literal expressions, which do not need resolution as they are values.
    def visit_literal_expr(self, _expr: Expr.Literal):
        # Literals do not require resolution.
        return None  
    
    # Processes logical expressions, resolving both operands.
    def visit_logical_expr(self, _expr: Expr.Logical):
        # Resolve the left operand.
        self.resolve(_expr.left) 
        # Resolve the right operand. 
        self.resolve(_expr.right)  
        return None

    # Processes set expressions, resolving the value being set and the object being accessed.
    def visit_set_expr(self, _expr: Expr.Set):
        # Resolve the value to be set on the property.
        self.resolve(_expr.value)  
        # Resolve the object whose property is being set.
        self.resolve(_expr.object)  
        return None

    # Processes 'super' expressions, used in subclasses to access superclass methods.
    def visit_super_expr(self, _expr: Expr.Super):
        # Validate 'super' is used within a subclass.
        if self.current_class == ClassType.NONE:  
            error_reporter.error(_expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            error_reporter.error(_expr.keyword, "Can't use 'super' in a class with no superclass.")
        # Resolve 'super' in the current scope.
        self.resolve_local(_expr, _expr.keyword)  
        return None

    # Processes 'this' expressions, used within classes to refer to the current object.
    def visit_this_expr(self, _expr: Expr.This):
        # Validate 'this' is used within a class.
        if self.current_class == ClassType.NONE:  
            error_reporter.error(_expr.keyword, "Can't use 'this' outside of a class.")
        # Resolve 'this' in the current scope.
        self.resolve_local(_expr, _expr.keyword)  
        return None

    # Processes unary expressions, resolving the operand.
    def visit_unary_expr(self, _expr: Expr.Unary):
        # Resolve the operand of the unary operator.
        self.resolve(_expr.right)  
        return None

    # Processes variable expressions, resolving the variable being referenced.
    def visit_variable_expr(self, _expr: Expr.Variable):
        if (len(self.scopes) > 0 and _expr.name.lexme in self.scopes[-1] and not self.scopes[-1][_expr.name.lexme]):
            error_reporter.error(_expr.name, "Can't read local variable in its own initialiser.")
        # Resolve the variable in the current scope.
        self.resolve_local(_expr, _expr.name)  
        return None