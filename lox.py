import sys
import os
from Scanner import Scanner
from Parser import Parser
from ErrorReporter import error_reporter
from Interpreter import Interpreter
from Resolver import Resolver


class Lox:
    def __init__(self):
        self._interpreter = Interpreter()

    def main(self):
        # Construct the path to the directory containing scripts to run.
        script_to_run = os.path.join(os.getcwd(), "lox_scripts")
        # List all files in the directory and store them.
        scripts_received = [file for file in os.listdir(script_to_run)]
        # Sort the list of scripts alphabetically for display.
        scripts_received.sort()
        if '.DS_Store' in scripts_received:
            scripts_received.remove('.DS_Store')  # Remove MacOS
        # Check if there are any scripts received; if so, proceed to display them.
        if scripts_received:
            print("Select a script to run or exit: ")
            # Enumerate and print each script with an index for the user to select.
            for i, file in enumerate(scripts_received, start=1):
                print(f"{i}. {file}")
            # Add an option for the user to exit the program.
            print(f"{i + 1}. Exit")
            # Enter a loop to handle user input.
            while True:
                user_choice = input("Enter the number associated with the script you would like to run: ")
                # Ensure the user enters a choice.
                if not user_choice:
                    print("Please enter a number.")
                    continue
                # Attempt to convert the user's choice to an integer and adjust for 0-based indexing.
                try:
                    user_choice = int(user_choice) - 1
                except ValueError:
                    # Handle non-integer inputs gracefully.
                    print("Please enter a valid number.")
                    continue
                # Check if the choice corresponds to a script in the list.
                if user_choice < len(scripts_received):
                    # Run the selected script and then prompt for running another script.
                    print()
                    self.run_file(f"lox_scripts/{scripts_received[user_choice]}")
                    self.run_again()
                # Check if the user chose to exit the program.
                elif user_choice == len(scripts_received):
                    print("Exited")
                    self.exit_prog()
                else:
                    # Handle any numerical input that is outside the valid range.
                    print("Invalid choice, please try again.")
            
    def run_again(self):
        # Prompt the user to decide between running another script or exiting the program.
        print()
        print("Would you like to exit to run another script?")
        print("1. Run another script")
        print("2. Exit")  
        # Enter a loop to handle user input.
        while True:
            # Read user input, remove leading/trailing spaces, and convert to lowercase for comparison.
            again = input("\nEnter your choice: ").strip().lower()     
            if again == "1":
                # If the user chooses to run another script, call the start function to restart the process.
                self.main()
            elif again == "2":
                # If the user chooses to exit, print a message and call the function to terminate the program.
                print("Exited")
                self.exit_prog()
            else:
                # If the user enters an invalid input, prompt them again.
                print("Please enter a valid input")
                continue

    def exit_prog(self):
        # Terminate the program immediately without an error message.
        sys.exit()

    # Executes a Lox script from a file, handling syntax and runtime errors.
    def run_file(self, path: str):
        # Opens the file for reading.
        with open(path, "r") as f: 
            # Reads and executes the script content.
            self.run(f.read())  
            # Exits with error code 65 if a syntax error occurred.
            if error_reporter.had_error:
                sys.exit(65)
            # Exits with error code 70 if a runtime error occurred.
            if error_reporter.had_runtime_error:
                sys.exit(70)

    # Interprets the Lox source code provided as a string.
    def run(self, src: str):
        # Initialises the scanner with the source code.
        scanner = Scanner(src)  
        # Scans the source code into tokens.
        tokens = scanner.scan_tokens()  
        # Initialises the parser with the scanned tokens.
        parser = Parser(tokens)  
        # Parses the tokens into statements.
        statements = parser.parse()  
        # Returns early if a syntax error was reported during parsing.
        if error_reporter.had_error:
            return
        # Initialises the resolver.
        resolver = Resolver(self._interpreter)  
        # Resolves variables and scopes in the statements.
        resolver.resolve(statements)  
        # Stops if there was a resolution error.
        if error_reporter.had_error:
            return
        self._interpreter.interpret(statements)  # Interprets the resolved statements.



if __name__ == "__main__":
    lox = Lox()
    lox.main()
