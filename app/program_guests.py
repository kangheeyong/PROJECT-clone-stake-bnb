import datetime
from collections import defaultdict

from dateutil import parser

import program_hosts as hosts
import services.data_service as svc
import infrastructure.state as state
from infrastructure.messages import success_msg, error_msg


def show_commands():
    print("What action would you like to take:")
    print("[C]reate an account")
    print("[L]ogin to your account")
    print("[B]ook a cage")
    print("[A]dd a snake")
    print("View [y]our snakes")
    print("[V]iew your bookings")
    print("[M]ain menu")
    print("e[X]it app")
    print("[?] Help (this info)")
    print()


def add_a_snake():
    print(" ****************** Add a snake **************** ")

    if not state.active_account:
        error_msg("You must login first to register a case.")
        return

    name = input("What is your snake's name? ")
    if not name:
        error_msg("Cancelled")
        return

    length = float(input("How long is yout snake (in meters)? "))
    species = input("Species? ")
    is_venomous = input("Is your sname venomous [y]es, [n]o? ").lower().startswith("y")

    snake = svc.add_snake(state.active_account, name, length, species, is_venomous)
    state.reload_account()
    success_msg(f"Created {snake.name} with id {snake.id}")


def view_your_snakes():
    print(" ****************** Your snakes **************** ")

    if not state.active_account:
        error_msg("You must login first to register a case.")
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    print(f"You have {len(snakes)} snakes.")

    for s in snakes:
        print(
            " * {} is a {} that id {}m ling and is {}venomous".format(
                s.name, s.species, s.length, "" if s.is_venomous else "not "
            )
        )


def book_a_cage():
    print(" ****************** Book a cage **************** ")

    if not state.active_account:
        error_msg("You must login first to register a case.")
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    if not snakes:
        error_msg("You must first [a]dd a snake before you can book a cage.")
        return

    print("Let's start by finding available cages.")
    start_text = input("Check-in data [yyyy-mm-dd]: ")
    if not start_text:
        error_msg("Cancelled")
        return

    checkin = parser.parse(start_text)
    checkout = parser.parse(input("Check-out date [yyyy-mm-dd]: "))
    if checkin >= checkout:
        error_msg("Check in must be before check out")
        return

    print()
    for idx, s in enumerate(snakes):
        print(
            "{}. {} (length: {}, venomous: {})".format(
                idx + 1, s.name, s.length, "Yes" if s.is_venomous else "No"
            )
        )

    snake = snakes[int(input("Which snake do you want to book (number)")) - 1]

    cages = svc.get_available_cage(checkin, checkout, snake)

    print(f"There are {len(cages)} cages available in that time")
    for idx, c in enumerate(cages):
        print(
            " {}. {} with {}m carpeted: {}, has_toys: {}.".format(
                idx + 1,
                c.name,
                c.square_meters,
                "Yes" if c.is_carpeted else "No",
                "Yes" if c.has_toys else "No",
            )
        )

    if not cages:
        error_msg("Sorry, no cages are available for that date.")
        return

    cage = cages[int(input("Which cage do you want to book (number)")) - 1]
    svc.book_case(state.active_account, snake, cage, checkin, checkout)

    success_msg(
        f"Successfully booked {cage.name} for {snake.name} at ${cage.price}/night"
    )


def view_bookings():
    print(" ****************** Your bookings **************** ")
    if not state.active_account:
        error_msg("You must login first to register a case.")
        return

    snakes = {s.id: s for s in svc.get_snakes_for_user(state.active_account.id)}
    bookings = svc.get_booking_for_user(state.active_account.email)

    print(f"You have {len(bookings)} bookings.")
    for b in bookings:
        print(
            " * Snake: {} is booked at {} from {} for {} days".format(
                snakes.get(b.guest_snake_id).name,
                b.cage.name,
                datetime.date(
                    b.check_in_date.year, b.check_in_date.month, b.check_in_date.day
                ),
                (b.check_out_date - b.check_in_date).days,
            )
        )


def run():
    print(" ****************** Welcome guest **************** ")
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        switch = defaultdict(
            lambda: hosts.unknown_command,
            {
                "c": hosts.create_account,
                "l": hosts.log_into_account,
                "a": add_a_snake,
                "y": view_your_snakes,
                "b": book_a_cage,
                "v": view_bookings,
                "m": lambda: "change_mode",
                "?": show_commands,
                "x": hosts.exit_app,
                "": lambda: None,
            },
        )
        result = switch[action]()

        state.reload_account()

        if action:
            print(f"action: {action}")

        if result == "change_mode":
            return
