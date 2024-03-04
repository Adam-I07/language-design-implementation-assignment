import sys
import os
from Scanner import Scanner

class BestLanguageEver:
    # This variable is used to keep track of whether an error has occurred.
    had_error = False

    @staticmethod
    def run_file(path):
        # This static method opens a file for reading. The file's path is specified by the 'path' parameter.
        with open(path, 'r', encoding='utf-8') as file:
            # This loop iterates over each line in the opened file.
            for line in file:
                # Executes the line of code by calling the run method on the BestLanguageEver class.
                BestLanguageEver.run(line)
                # Checks if an error has occurred during the execution of the line.
                if BestLanguageEver.had_error:
                    # If an error has occurred, the program is terminated with an exit code of 65.
                    sys.exit(65)

    @staticmethod
    def run_prompt():
        try:
            # Starts an infinite loop to continuously accept input from the user.
            while True:
                # Prints a prompt character '>' without moving to a new line afterwards
                print("> ", end="")
                # Reads the input from the user and stores it in the variable 'line'.
                line = input()
                if line is None:
                    # If the user input is None, break out of the loop to stop processing further input.
                    break
                # This method is expected to execute or evaluate the line inputted
                BestLanguageEver.run(line)
                # After processing the input line, resets the 'had_error' flag to False.
                BestLanguageEver.had_error = False                
        # If an EOFError is caught, the loop is exited gracefully.   
        except EOFError:
            pass


    def run(source):
        # Initialize a Scanner object with the source text.
        scanner = Scanner(source)      
        # Scan the source text and return a list of tokens.
        tokens = scanner.scan_tokens() 
        # Print the list of tokens for overview.
        print(tokens) 
        # Iterate over each token in the list and print it.
        for token in tokens:
            print(f"Token: {token}")

    @staticmethod
    def error(line, message):
        # Delegate error reporting to the 'report' method with an empty 'where' string.
        BestLanguageEver.report(line, "", message)

    @staticmethod
    def report(line, where, message):
        # Print an error message to stderr, including the line number and specific location (if provided).
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        # Flag that an error has occurred.
        BestLanguageEver.had_error = True


def start():
    # Construct the path to the directory containing scripts to run.
    script_to_run = os.path.join(os.getcwd(), "files_to_run")
    # List all files in the directory and store them.
    scripts_received = [file for file in os.listdir(script_to_run)]
    # Sort the list of scripts alphabetically for display.
    scripts_received.sort()
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
            user_choice = input("Enter what you would like to do: ")
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
                BestLanguageEver.run_file(f"files_to_run/{scripts_received[user_choice]}")
                run_again()
            # Check if the user chose to exit the program.
            elif user_choice == len(scripts_received):
                print("Exited")
                exit_prog()
            else:
                # Handle any numerical input that is outside the valid range.
                print("Invalid choice, please try again.")
        
def run_again():
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
            start()
        elif again == "2":
            # If the user chooses to exit, print a message and call the function to terminate the program.
            print("Exited Language")
            exit_prog()
        else:
            # If the user enters an invalid input, prompt them again.
            print("Please enter a valid input")
            continue

def exit_prog():
    # Terminate the program immediately without an error message.
    sys.exit()


if __name__ == "__main__":
    start()
