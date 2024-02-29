import sys
import os
from Scanner import Scanner

class BestLanguageEver:
    had_error = False

    @staticmethod
    def run_file(path):
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:  # Read and execute line by line
                BestLanguageEver.run(line)
                if BestLanguageEver.had_error:
                    # Stop processing further if an error occurs
                    sys.exit(65)

    @staticmethod
    def run_prompt():
        try:
            while True:
                print("> ", end="")
                line = input()
                if line is None:
                    break
                BestLanguageEver.run(line)
                BestLanguageEver.had_error = False
        except EOFError:
            pass

    @staticmethod
    def run(source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        print(tokens)
        for token in tokens:
            print(token)

    @staticmethod
    def error(line, message):
        BestLanguageEver.report(line, "", message)

    @staticmethod
    def report(line, where, message):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        BestLanguageEver.had_error = True

def start():
    script_to_run = os.path.join(os.getcwd(), "files_to_run")
    scripts_received = [file for file in os.listdir(script_to_run)]
    
    if scripts_received:
        print("Select a script to run or exit: ")
        for i, file in enumerate(scripts_received, start=1):
            print(f"{i}. {file}")
        print(f"{i + 1}. Exit")

        while True:
            user_choice = input("Enter what you would like to do: ")
            if not user_choice:
                print("Please enter a number.")
                continue

            try:
                user_choice = int(user_choice) - 1
            except ValueError:
                print("Please enter a valid number.")
                continue

            if user_choice < len(scripts_received):
                BestLanguageEver.run_file(f"files_to_run/{scripts_received[user_choice]}")
                run_again()
            elif user_choice == len(scripts_received):
                print("Exited")
                exit_prog()
            else:
                print("Invalid choice, please try again.")

def run_again():
    # Ask user if they want to choose another script or exit
    print("Would you like to exit to run another script?")
    print("1. Run another script")
    print("2. Exit")
    while True:
        again = input("\nEnter your choice: ").strip().lower()
        if again == "1":
            start()
        elif again == "2":
            print("Exited")
            exit_prog()
        else:
            print("Please enter a valid input")
            continue

def exit_prog():
    sys.exit()
        


if __name__ == "__main__":
    start()
    
    
    # script_to_run = os.path.join(os.getcwd(), "files_to_run")
    # scripts_recieved = [file for file in os.listdir(script_to_run)]
    # if scripts_recieved:
    #     print("Select a script to run or exit: ")
    #     for i, file in enumerate(scripts_recieved, start=1):
    #         print(f"{i}. {file}")
    #         current_script_num = i
    #     print(f"{i + 1}" + ". Exit")
    # while True:
    #     user_choice = input("Enter what you would like to do: ")
    #     if not user_choice:
    #         print("Please enter a file number.")
    #         continue
    #     else:
    #         user_choice = int(user_choice) - 1
    #         if  user_choice < len(scripts_recieved):
    #             BestLanguageEver.run_file(f"files_to_run/{scripts_recieved[user_choice]}")
    #             break

    
    # BestLanguageEver.run_file("code_to_run/stage1.txt")
    # if len(sys.argv) > 2:
    #     print("Usage: best_language_ever [script]")
    #     sys.exit(64)
    # elif len(sys.argv) == 2:
    #     BestLanguageEver.run_file(sys.argv[1])
    # else:
    #     BestLanguageEver.run_prompt()
