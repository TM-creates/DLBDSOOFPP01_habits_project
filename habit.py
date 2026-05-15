# habit.py
# The main class. A Habit has a name, description, periodicity

from datetime import datetime, timedelta
from periodicity import Periodicity


class Habit:

    def __init__(self, name, description, periodicity, created_at=None, habit_id=None, active=True):
        self.id = habit_id
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self.active = active
        self.completions = []  # loaded separately by HabitManager

        if created_at is None:
            self.created_at = datetime.now()
        else:
            self.created_at = created_at

    def check_off(self, when=None):
        """Log a completion in memory"""
        from completion import Completion
        if when is None:
            when = datetime.now()
        self.completions.append(Completion(habit_id=self.id, timestamp=when))

    def _get_period_start(self, dt):
        """ Daily = midnight of that day, Weekly = midnight of Monday that week."""
        if self.periodicity == Periodicity.DAILY:
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # weekday() returns 0 for Monday, so subtracting it gives us Monday
            monday = dt - timedelta(days=dt.weekday())
            return monday.replace(hour=0, minute=0, second=0, microsecond=0)

    def get_current_streak(self, now=None):
        """Count how many periods in a row the habit was completed, going back from today."""
        if now is None:
            now = datetime.now()

        if not self.completions:
            return 0

        # collect all the period-start dates that have a completion
        completed_periods = []
        for c in self.completions:
            completed_periods.append(self._get_period_start(c.timestamp))

        if self.periodicity == Periodicity.DAILY:
            step = timedelta(days=1)
        else:
            step = timedelta(weeks=1)

        # start from today and go back one period at a time until there's a gap
        streak = 0
        period = self._get_period_start(now)

        while period in completed_periods:
            streak += 1
            period -= step

        return streak

    def get_longest_streak(self):
        """Finds the best streak this habit has ever had, not just the current one."""
        if not self.completions:
            return 0

        periods = []
        for c in self.completions:
            periods.append(self._get_period_start(c.timestamp))

        unique_periods = list(set(periods)) #remove duplicates if checked off twice in a period

        all_periods = sorted(unique_periods)

        if self.periodicity == Periodicity.DAILY:
            step = timedelta(days=1)
        else:
            step = timedelta(weeks=1)

        longest = 1
        current = 1

        for i in range(1, len(all_periods)):
            if all_periods[i] - all_periods[i - 1] == step:
                current += 1
                if current > longest:
                    longest = current
            else:
                # streak broke -> reset to 1
                current = 1

        return longest