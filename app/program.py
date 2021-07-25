from colorama import Fore

import program_hosts
import program_guests
from models import global_init


def print_header():
    snake = """
            (>.<)
"""

    print(Fore.WHITE + "****************  SNAKE BnB  ****************")
    print(Fore.GREEN + snake)
    print(Fore.WHITE + "*********************************************")
    print()
    print("Welcome to Snake BnB!")
    print("Why are you here?")
    print()


def find_user_intent():
    print("[g] Book a cage for your snake")
    print("[h] Offer extra cage space")
    print()
    choice = input("Are you a [g]uest or [h]ost? ")
    if choice == "h":
        return "offer"

    return "book"


def main():
    global_init()

    print_header()

    try:
        while True:
            if find_user_intent() == "book":
                program_guests.run()
            else:
                program_hosts.run()
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
