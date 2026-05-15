# analytics.py
# All the analysis functions for habits. Read-only. No db writes.
# Implemented using functional programming: filter(), map(), sorted(), max(), lambda.


class Analytics:
    """Analysis functions for the habit tracker."""

    def get_all_habits(self, habits):
        """Return all habits as a list."""
        return list(habits)

    def get_habits_by_periodicity(self, habits, period):
        """Return only habits that match the given period (daily or weekly)."""
        return list(filter(lambda h: h.periodicity == period, habits))

    def get_longest_run_streak_all(self, habits):
        """Return the highest streak value across all habits.
        Returns 0 if there are no habits to avoid a crash in max()."""
        if not habits:
            return 0
        return max(map(lambda h: h.get_longest_streak(), habits))

    def get_longest_run_streak_for_habit(self, habit):
        """Return the longest streak ever recorded for a single habit."""
        return habit.get_longest_streak()

    def get_habits_with_streaks(self, habits):
        """Return a list of (habit, streak) pairs sorted from highest to lowest.
        Used in the analytics dashboard."""
        pairs = list(map(lambda h: (h, h.get_longest_streak()), habits))
        return sorted(pairs, key=lambda pair: pair[1], reverse=True)

    def get_broken_habits(self, habits, threshold=2):
        """Return habits where the longest streak is at or below the threshold."""
        return list(filter(lambda h: h.get_longest_streak() <= threshold, habits))

