# main.py
# Starting point of the app, run with : python main.py

from sqlite_habit_storage import SqliteHabitStorage
from habit_manager import HabitManager
from analytics import Analytics
from cli import CLI
from user import User


def show_welcome():
    """Print ASCII art banner when the app starts."""
    # ASCII Banner created in https://manytools.org/hacker-tools/ascii-banner/
    # Used Font "ANSI Shadow"
    print("""
██╗  ██╗ █████╗ ██████╗ ██╗████████╗     ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗
██║  ██║██╔══██╗██╔══██╗██║╚══██╔══╝     ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████║███████║██████╔╝██║   ██║           ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██║██╔══██║██╔══██╗██║   ██║           ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║██║  ██║██████╔╝██║   ██║           ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝           ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """)
    print("  Build good habits, break bad ones.")
    print("  IU International University  |  DLBDSOOFPP01")
    print()


def create_user():
    """Asks for a username. Defaults to 'User' if left empty."""
    print("  ┌─────────────────────────────────────┐")
    print("  │            Who are you?             │")
    print("  └─────────────────────────────────────┘")
    print()

    name = input("  Enter your username: ").strip()

    if not name:
        name = "User"

    user = User(name)
    print(f"\n  [✓] Welcome, {user.name}!\n")
    return user


def select_database():
    """Lets the user pick between the real db and the test db with predefined habits."""
    print("  ┌─────────────────────────────────────┐")
    print("  │         Select Database             │")
    print("  ├─────────────────────────────────────┤")
    print("  │  1. Real database  (habits.db)      │")
    print("  │  2. Test database  (test_habits.db) |")
    print("  └─────────────────────────────────────┘")
    print()

    choice = input("  Choose (1/2): ").strip()

    if choice == "2":
        print("\n  [✓] Using test database with predefined habits.\n")
        return "test_habits.db", True
    else:
        print("\n  [✓] Using real database.\n")
        return "habits.db", False


def main():
    """Creates storage, manager, analytics and hands off to CLI"""
    show_welcome()

    user = create_user()

    db_path, use_test_data = select_database()

    storage = SqliteHabitStorage(db_path)
    manager = HabitManager(storage)

    if use_test_data:
        manager.load_predefined_habits()

    analytics = Analytics()

    cli = CLI(manager, analytics, user)
    cli.run()

# only runs if you start this file directly, not when imported
if __name__ == "__main__":
    main()
