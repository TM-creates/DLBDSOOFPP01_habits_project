# cli.py
# Place for all Menus and user Input
# Uses a simple while loop with input() as required.

from datetime import datetime
from periodicity import Periodicity


class CLI:
    """Shows menus and handles all interaction with the user."""

    def __init__(self, manager, analytics, user=None):
        """Create the CLI with a manager, analytics, and optional user."""
        self.manager = manager
        self.analytics = analytics
        self.user = user

    def run(self):
        """Shows menu until Q is given"""
        while True:
            self._print_menu()
            choice = input("  Your choice: ").strip().upper()

            if choice == "1":
                self.create_habit()
            elif choice == "2":
                self.delete_habit()
            elif choice == "3":
                self.check_off_habit()
            elif choice == "4":
                self.show_all_habits()
            elif choice == "5":
                self.show_habits_by_periodicity()
            elif choice == "6":
                self.show_longest_streak_overall()
            elif choice == "7":
                self.show_longest_streak_for_habit()
            elif choice == "8":
                self.show_analytics_dashboard()
            elif choice == "Q":
                if self.user:
                    name = self.user.name
                else:
                    name = "friend"
                print(f"\n  Goodbye, {name}!, see you next time\n")
                break
            else:
                print("\n  [!] Invalid choice. Please try again.\n")

    def create_habit(self):
        """Ask for name, description and periodicity then saves it."""
        print("\n  --- Create New Habit ---")

        name = input("  Habit name: ").strip()
        if not name:
            print("  [!] Name cannot be empty.")
            return

        desc = input("  Description: ").strip()

        print("  Periodicity: 1 = Daily  |  2 = Weekly")
        period_choice = input("  Choose (1/2): ").strip()

        if period_choice == "1":
            period = Periodicity.DAILY
        elif period_choice == "2":
            period = Periodicity.WEEKLY
        else:
            print("  [!] Invalid choice. Habit not created.")
            return

        habit = self.manager.add_habit(name, desc, period)
        print(f"\n  [✓] Habit '{habit.name}' created! (ID: {habit.id})\n")

    def delete_habit(self):
        """Shows the list, asks for an id, confirms, then deletes it."""
        habits = self.manager.list_habits()
        if not habits:
            print("\n  [!] No habits found.\n")
            return

        print("\n  --- Delete Habit ---")
        self._print_habit_list(habits)

        try:
            habit_id = int(input("  Enter the ID to delete: ").strip())
        except ValueError:
            print("  [!] Please enter a valid number.")
            return

        habit = self.manager.get_habit(habit_id)
        if habit is None:
            print(f"  [!] No habit with ID {habit_id}.")
            return

        confirm = input(f"  Delete '{habit.name}'? (y/n): ").strip().lower()
        if confirm == "y":
            self.manager.delete_habit(habit_id)
            print(f"\n  [✓] '{habit.name}' deleted.\n")
        else:
            print("  Cancelled.\n")

    def check_off_habit(self):
        """Logs a completion for the chosen habit and shows the updated streak."""
        habits = self.manager.list_habits()
        if not habits:
            print("\n  [!] No habits yet. Create one first.\n")
            return

        print("\n  --- Check Off Habit ---")
        self._print_habit_list(habits)

        try:
            habit_id = int(input("  Enter habit ID: ").strip())
        except ValueError:
            print("  [!] Please enter a valid number.")
            return

        try:
            self.manager.add_completion(habit_id, datetime.now())

            # reload to get the updated streak
            habit = self.manager.get_habit(habit_id)
            streak = habit.get_current_streak()

            if habit.periodicity == Periodicity.DAILY:
                unit = "day(s)"
            else:
                unit = "week(s)"

            print(f"\n  [✓] Done! Current streak: {streak} {unit}.\n")

        except ValueError as e:
            print(f"\n  [!] {e}\n")

    def show_all_habits(self):
        """Prints all habits in a table with their current streak."""
        habits = self.manager.list_habits()
        if not habits:
            print("\n  [!] No habits found.\n")
            return

        print("\n  --- All Habits ---")
        print("  ID    Name                   Period      Streak      Created")
        print("  " + "-" * 62)

        for h in self.analytics.get_all_habits(habits):
            streak = h.get_current_streak()
            if h.periodicity == Periodicity.DAILY:
                unit = "days"
            else:
                unit = "weeks"
            streak_text = str(streak) + " " + unit

            print("  " + str(h.id).ljust(5) + h.name.ljust(22) + h.periodicity.value.ljust(10) + streak_text.ljust(10) + h.created_at.strftime("%d-%m-%Y"))
        print()

    def show_habits_by_periodicity(self):
        """Asks daily or weekly, then shows only those habits."""
        print("\n  --- Habits by Periodicity ---")
        print("  1. Daily habits")
        print("  2. Weekly habits")
        choice = input("  Choose (1/2): ").strip()

        if choice == "1":
            period = Periodicity.DAILY
        elif choice == "2":
            period = Periodicity.WEEKLY
        else:
            print("  [!] Invalid choice.\n")
            return

        habits = self.manager.list_habits()
        filtered = self.analytics.get_habits_by_periodicity(habits, period)

        if not filtered:
            print(f"\n  [!] No {period.value} habits found.\n")
            return

        print(f"\n  {period.value.capitalize()} habits:")
        print("  ID    Name                   Current Streak")
        print("  " + "-" * 45)

        for h in filtered:
            streak = h.get_current_streak()
            if period == Periodicity.DAILY:
                unit = "days"
            else:
                unit = "weeks"
            print("  " + str(h.id).ljust(5) + h.name.ljust(22) + str(streak) + " " + unit)
        print()

    def show_longest_streak_overall(self):
        """Shows the single highest streak across all habits."""
        habits = self.manager.list_habits()
        if not habits:
            print("\n  [!] No habits found.\n")
            return

        longest = self.analytics.get_longest_run_streak_all(habits)
        print(f"\n  [★] Longest streak across all habits: {longest} period(s).\n")

    def show_longest_streak_for_habit(self):
        """Lets the user pick a habit and shows its personal best streak."""
        habits = self.manager.list_habits()
        if not habits:
            print("\n  [!] No habits found.\n")
            return

        print("\n  --- Longest Streak for a Habit ---")
        self._print_habit_list(habits)

        try:
            habit_id = int(input("  Enter habit ID: ").strip())
        except ValueError:
            print("  [!] Please enter a valid number.")
            return

        habit = self.manager.get_habit(habit_id)
        if habit is None:
            print(f"  [!] No habit with ID {habit_id}.")
            return

        longest = self.analytics.get_longest_run_streak_for_habit(habit)

        if habit.periodicity == Periodicity.DAILY:
            unit = "day(s)"
        else:
            unit = "week(s)"

        print(f"\n  [★] Longest streak for '{habit.name}': {longest} {unit}.\n")

    def show_analytics_dashboard(self):
        """Shows all habits ranked by streak plus a list of struggling ones."""
        habits = self.manager.list_habits()
        if not habits:
            print("\n  [!] No habits found.\n")
            return

        print("\n  --- Analytics Dashboard ---")
        print(f"\n  Total habits: {len(habits)}")

        print("\n  Habit                  Type       Longest Streak")
        print("  " + "-" * 50)

        for habit, streak in self.analytics.get_habits_with_streaks(habits):
            if habit.periodicity == Periodicity.DAILY:
                unit = "days"
            else:
                unit = "weeks"
            print("  " + habit.name.ljust(22) + habit.periodicity.value.ljust(10) + str(streak) + " " + unit)

        overall = self.analytics.get_longest_run_streak_all(habits)
        print(f"\n  [★] Overall longest streak: {overall} period(s)")

        broken = self.analytics.get_broken_habits(habits, threshold=2)
        if broken:
            print("\n  [!] Habits to work on (streak of 2 or less):")
            for h in broken:
                print(f"      - {h.name}")
        else:
            print("\n  [✓] Great job! No broken habits!")
        print()

    def _print_menu(self):
        """Prints the main menu with the user's name at the top."""
        if self.user:
            name = self.user.name
        else:
            name = "User"
        print("\n  ================================")
        print(f"  Hello, {name}!")
        print("  ================================")
        print("  1. Create habit")
        print("  2. Delete habit")
        print("  3. Check off habit")
        print("  4. Show all habits")
        print("  5. Show habits by periodicity")
        print("  6. Longest streak (all habits)")
        print("  7. Longest streak (specific habit)")
        print("  8. Analytics dashboard")
        print("  Q. Quit")
        print("  ================================")

    def _print_habit_list(self, habits):
        """Helper to print a simple habit list with id, name and periodicity."""
        print("  ID    Name                   Periodicity")
        print("  " + "-" * 40)
        for h in habits:
            print("  " + str(h.id).ljust(5) + h.name.ljust(22) + h.periodicity.value)
        print()