# habit_manager.py
# Connects the CLI to the database
# CLI never talks to storage directly, it always goes through here

from datetime import datetime, timedelta
from habit import Habit
from completion import Completion
from periodicity import Periodicity


class HabitManager:
    """The main class that sits between the CLI and the database."""

    def __init__(self, storage):
        """Takes any storage object, makes it easy to swap in a test db."""
        self.storage = storage

    def add_habit(self, name, desc, period):
        """Creates the habit, saves it to db and returns it with the id attached."""
        habit = Habit(name=name, description=desc, periodicity=period)

        # storage expects a dict, not a Habit object
        habit_data = {
            "name": habit.name,
            "description": habit.description,
            "periodicity": habit.periodicity.value,
            "created_at": habit.created_at,
            "active": habit.active,
        }

        # save it and get back the ID that the database assigned
        habit.id = self.storage.save_habit(habit_data)
        return habit

    def delete_habit(self, habit_id):
        """Deletes the habit and all its completions from the db."""
        self.storage.delete_habit(habit_id)

    def get_habit(self, habit_id):
        """Loads a habit by id with completions already attached. Returns None if it doesn't exist."""
        data = self.storage.load_habit(habit_id)
        if data is None:
            return None
        return self._dict_to_habit(data)

    def list_habits(self):
        """Load all habits from the database, each with their completions attached."""
        habit_dicts = self.storage.list_habits()
        habits = []
        for d in habit_dicts:
            habits.append(self._dict_to_habit(d))
        return habits

    def get_completions(self, habit_id):
        """Gets raw completions from storage for a given habit."""
        return self.storage.load_completions(habit_id)

    def list_habits_by_periodicity(self, period):
        """Filters habits to only daily or only weekly."""
        all_habits = self.list_habits()
        result = []
        for habit in all_habits:
            if habit.periodicity == period:
                result.append(habit)
        return result

    def add_completion(self, habit_id, timestamp=None):
        """Logs a completion for the habit. Raises ValueError if already done this period."""
        if timestamp is None:
            timestamp = datetime.now()

        # make sure the habit actually exists
        habit = self.get_habit(habit_id)
        if habit is None:
            raise ValueError("Habit not found.")

        # don't allow checking off twice in the same period
        if self._already_completed_this_period(habit, timestamp):
            raise ValueError("Already completed this habit in the current period.")

        self.storage.save_completion({"habit_id": habit_id, "timestamp": timestamp})
        return Completion(habit_id=habit_id, timestamp=timestamp)

    def load_predefined_habits(self):
        """Load 5 sample habits with 4 weeks of example completions.
        Only runs if the database is empty to avoid adding duplicates."""

        # if there are already habits in the db, do nothing
        if self.storage.list_habits():
            return self.list_habits()

        # the 5 predefined habits — 3 daily and 2 weekly
        predefined = [
            ("Morning Run", "Run at least 20 minutes each morning.", Periodicity.DAILY),
            ("Read a Book", "Read at least 10 pages of a book.", Periodicity.DAILY),
            ("Meditate", "Spend 10 minutes on mindful meditation.", Periodicity.DAILY),
            ("Weekly Review", "Review goals and plan the upcoming week.", Periodicity.WEEKLY),
            ("Grocery Shopping", "Buy fresh ingredients for the week.", Periodicity.WEEKLY),
        ]

        # set noon today as the end point and go back 27 days (= 4 full weeks)
        today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        start = today - timedelta(days=27)

        habits = []
        for name, desc, period in predefined:
            habit = self.add_habit(name, desc, period)
            habits.append(habit)

            if period == Periodicity.DAILY:
                self._add_daily_completions(habit, start, today)
            else:
                self._add_weekly_completions(habit, start, today)

        return habits

    def _add_daily_completions(self, habit, start, end):
        """Adds one completion per day for the date range, skipping a few days to simulate missed habits."""
        skip_days = {3, 10, 17}  # day indexes to skip (0 = first day)
        current = start
        day_index = 0

        while current <= end:
            if day_index not in skip_days:
                self.storage.save_completion({"habit_id": habit.id, "timestamp": current})
            current += timedelta(days=1)
            day_index += 1

    def _add_weekly_completions(self, habit, start, end):
        """Adds one completion per week on Wednesdays for the test data."""
        # weekday() returns 0=Mon, 1=Tue, 2=Wed, etc.
        # this calculation finds how many days until the next Wednesday
        days_until_wednesday = (2 - start.weekday()) % 7
        current = start + timedelta(days=days_until_wednesday)

        while current <= end:
            self.storage.save_completion({"habit_id": habit.id, "timestamp": current})
            current += timedelta(weeks=1)

    def _dict_to_habit(self, data):
        """Convert a dict from the database into a Habit object.
        Also loads and attaches all completions for that habit."""
        habit = Habit(
            name=data["name"],
            description=data["description"],
            periodicity=Periodicity(data["periodicity"]),
            created_at=data["created_at"],
            habit_id=data["id"],
            active=data["active"],
        )

        # load all completions and attach them to the habit
        comp_dicts = self.storage.load_completions(habit.id)
        for d in comp_dicts:
            habit.completions.append(
                Completion(habit_id=d["habit_id"], timestamp=d["timestamp"])
            )

        return habit

    def _already_completed_this_period(self, habit, when):
        """Checks if the habit was already done in the same day or week as 'when'."""

        # daily resets at midnight, weekly resets on monday
        if habit.periodicity == Periodicity.DAILY:
            # daily period = midnight to midnight
            period_start = when.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        else:
            # weekly period = Monday midnight to next Monday midnight
            monday = when - timedelta(days=when.weekday())
            period_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(weeks=1)

        # check if any existing completion falls inside this period
        for c in habit.completions:
            if period_start <= c.timestamp < period_end:
                return True
        return False