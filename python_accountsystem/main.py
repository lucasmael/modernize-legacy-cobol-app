import sys
from data import DataProgram
from operations import Operations


MENU = (
    "--------------------------------\n"
    "Account Management System\n"
    "1. View Balance\n"
    "2. Credit Account\n"
    "3. Debit Account\n"
    "4. Exit\n"
    "--------------------------------\n"
)


def main() -> int:
    data = DataProgram(initial_balance=1000.00)
    ops = Operations(data)

    while True:
        sys.stdout.write(MENU)
        sys.stdout.write("Enter your choice (1-4): \n")
        sys.stdout.flush()

        choice_line = sys.stdin.readline()
        if not choice_line:
            break

        choice_line = choice_line.strip()
        if not choice_line.isdigit():
            sys.stdout.write("Invalid choice, please select 1-4.\n")
            continue

        choice = int(choice_line)

        if choice == 1:
            sys.stdout.write(ops.total())
        elif choice == 2:
            sys.stdout.write("Enter credit amount: \n")
            sys.stdout.flush()
            amount_line = sys.stdin.readline()
            try:
                amount = float(amount_line.strip())
            except Exception:
                amount = 0.0
            sys.stdout.write(ops.credit(amount))
        elif choice == 3:
            sys.stdout.write("Enter debit amount: \n")
            sys.stdout.flush()
            amount_line = sys.stdin.readline()
            try:
                amount = float(amount_line.strip())
            except Exception:
                amount = 0.0
            sys.stdout.write(ops.debit(amount))
        elif choice == 4:
            break
        else:
            sys.stdout.write("Invalid choice, please select 1-4.\n")

    sys.stdout.write("Exiting the program. Goodbye!\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


