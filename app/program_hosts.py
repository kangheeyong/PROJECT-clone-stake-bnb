import datetime
from collections import defaultdict

from colorama import Fore
from dateutil import parser

import infrastructure.state as state
import services.data_service as svc
from infrastructure.messages import success_msg, error_msg


def show_commands():
    print("What action would you like to take:")
    print("[C]reate an account")
    print("Login to your [a]ccount")
    print("[L]ist your cages")
    print("[R]egister a cage")
    print("[U]pdate cage availability")
    print("[V]iew your bookings")
    print("Change [M]ode (guest or host)")
    print("e[X]it app")
    print("[?] Help (this info)")
    print()


def create_account():
    print(" ****************** REGISTER **************** ")

    name = input("What id your name? ")
    email = input("What id your email? ").strip().lower()

    old_account = svc.find_account_by_email(email)
    if old_account:
        error_msg(f"ERROR: Acount with email {email} already exists.")
        return

    state.active_account = svc.create_account(name, email)
    success_msg(f"Created new account with id {state.active_account.id}")


def log_into_account():
    print(" ****************** LOGIN **************** ")

    email = input("What id your email? ").strip().lower()
    account = svc.find_account_by_email(email)

    if not account:
        error_msg(f"Coudl not find account with email {email}.")
        return

    state.active_account = account
    success_msg("logged in successfully.")


def register_cage():
    print(" ****************** REGISTER CAGE **************** ")

    if not state.active_account:
        error_msg("You must login first to register a case.")
        return
    
    meters = input("How many squere meters is the case? ")
    if not meters:
        error_msg("Cancelled")
        return

    meters = float(meters)
    carpeted = input("Is it carpeted [y, n]? ").lower().startswith("y")
    has_toys = input("Have snake toys [y, n]? ").lower().startswith("y")
    allow_dangerous = input("Can you host venomous snakes [y, n]? ").lower().startswith("y")
    name = input("Give your case a name: ")
    price = float(input("How much are you charging?  "))

    cage = svc.register_cage(
        state.active_account, name, allow_dangerous, has_toys, carpeted, meters, price
    )

    state.reload_account()
    success_msg(f"Register new cage with id {cage.id}")


def list_cages(supress_header=False):
    if not supress_header:
        print(" ******************     Your cages     **************** ")

    if not state.active_account:
        error_msg("You must login first to register a case.")
        return

    cages = svc.find_cages_for_user(state.active_account)
    print(f"You have {len(cages)} cages.")
    for idx, c in enumerate(cages):
        print(f" {idx+1} {c.name} is {c.square_meters} meters.")
        for b in c.bookings:
            print("    * Booking: {}, {} days, booked? {}".format(
                b.check_in_date,
                (b.check_out_date - b.check_in_date).days,
                "Yes" if b.booked_date is not None else 'No'
            ))
    

def update_availability():
    print(" ****************** Add available date **************** ")

    if not state.active_account:
        error_msg("You must login first to register a case.")
        return

    list_cages(supress_header=True)

    cage_number = input("Enter cage number: ")
    if not cage_number.strip():
        error_msg("Cancelled")
        print()
        return

    cage_number = int(cage_number)

    cages = svc.find_cages_for_user(state.active_account)
    selected_cage = cages[cage_number - 1]

    success_msg(f"Selected cage {selected_cage.name}")

    start_date = parser.parse(
        input("Enter available date [yyyy-mm-dd]: ")
    )
    days = int(input("How many days is this block of time? "))

    svc.add_available_date(
        selected_cage,
        start_date,
        days
    )

    success_msg(f"Date added to cage {selected_cage.name}")


def view_bookings():
    print(" ****************** Your bookings **************** ")

    if not state.active_account:
        error_msg("You must login first to register a case.")
        return

    cages = svc.find_cages_for_user(state.active_account)

    bookings = [
        (c, b)
        for c in cages
        for b in c.bookings
        if b.booked_date is not None
    ]
    
    print(f"You have {len(bookings)} bookings.")
    for c, b in bookings:
        print(" * Cage: {}, booked date: {}, from {} for {} days".format(
            c.name,
            datetime.date(b.booked_date.year, b.booked_date.month, b.booked_date.day),
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            b.duration_in_days
        ))


def exit_app():
    print()
    print("bye")
    raise KeyboardInterrupt()


def get_action():
    text = "> "
    if state.active_account:
        text = f"{state.active_account.name}> "

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")





def run():
    print(" ****************** Welcome host **************** ")
    print()

    show_commands()

    while True:
        action = get_action()

        switch = defaultdict(
            lambda: unknown_command,
            {
                "c": create_account,
                "a": log_into_account,
                "l": list_cages,
                "r": register_cage,
                "u": update_availability,
                "v": view_bookings,
                "m": lambda: "change_mode",
                "x": exit_app,
                "": lambda: None,
            },
        )
        result = switch[action]()

        if action:
            print(f"action: {action}")

        if result == "change_mode":
            return
