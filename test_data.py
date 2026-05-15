# test_habit_tracker.py
# Unit tests for the Habit Tracker.
# Run with: pytest test_habit_tracker.py -v
#
# All tests use an in-memory SQLite database so nothing is written to disk.
# Each test function gets a fresh database automatically (via pytest fixtures).

import pytest
from datetime import datetime, timedelta
import sys
import os

# Make sure Python can find the project files
sys.path.insert(0, os.path.dirname(__file__))

from periodicity import Periodicity
from completion import Completion
from habit import Habit
from user import User
from sqlite_habit_storage import SqliteHabitStorage
from habit_manager import HabitManager
from analytics import Analytics


# =============================================================================
# Fixtures — these set up fresh objects for each test
# =============================================================================

@pytest.fixture
def storage():
    """A fresh in-memory SQLite database for each test."""
    return SqliteHabitStorage(db_path=":memory:")


@pytest.fixture
def manager(storage):
    """A HabitManager using the in-memory storage."""
    return HabitManager(storage=storage)


@pytest.fixture
def analytics():
    """A fresh Analytics object."""
    return Analytics()


@pytest.fixture
def daily_habit(manager):
    """A simple daily habit already saved in the database."""
    return manager.add_habit("Morning Run", "Run 20 min", Periodicity.DAILY)


@pytest.fixture
def weekly_habit(manager):
    """A simple weekly habit already saved in the database."""
    return manager.add_habit("Weekly Review", "Review goals", Periodicity.WEEKLY)


# =============================================================================
# Periodicity tests
# =============================================================================

class TestPeriodicity:

    def test_daily_value(self):
        assert Periodicity.DAILY.value == "daily"

    def test_weekly_value(self):
        assert Periodicity.WEEKLY.value == "weekly"

    def test_create_from_string(self):
        # Check that we can create a Periodicity from a string (used when loading from DB)
        assert Periodicity("daily") == Periodicity.DAILY
        assert Periodicity("weekly") == Periodicity.WEEKLY


# =============================================================================
# Habit tests
# =============================================================================

class TestHabit:

    def test_habit_has_correct_defaults(self):
        h = Habit("Test", "Desc", Periodicity.DAILY)
        assert h.name == "Test"
        assert h.description == "Desc"
        assert h.periodicity == Periodicity.DAILY
        assert h.active is True
        assert h.id is None
        assert isinstance(h.created_at, datetime)

    def test_check_off_adds_to_completions(self):
        h = Habit("Test", "Desc", Periodicity.DAILY)
        h.id = 1
        h.check_off()
        assert len(h.completions) == 1

    def test_streak_is_zero_with_no_completions(self):
        h = Habit("Test", "Desc", Periodicity.DAILY)
        assert h.get_current_streak() == 0
        assert h.get_longest_streak() == 0

    def test_daily_streak_three_days_in_a_row(self):
        h = Habit("Test", "Desc", Periodicity.DAILY)
        h.id = 1
        now = datetime(2024, 3, 10, 12, 0, 0)
        # Add completions for day -2, day -1, and today
        h.check_off(now - timedelta(days=2))
        h.check_off(now - timedelta(days=1))
        h.check_off(now)
        assert h.get_current_streak(now=now) == 3

    def test_daily_streak_breaks_after_a_gap(self):
        h = Habit("Test", "Desc", Periodicity.DAILY)
        h.id = 1
        now = datetime(2024, 3, 10, 12, 0, 0)
        # Complete 2 days ago and today, but NOT yesterday — streak should be 1
        h.check_off(now - timedelta(days=2))
        h.check_off(now)
        assert h.get_current_streak(now=now) == 1

    def test_longest_streak_daily(self):
        h = Habit("Test", "Desc", Periodicity.DAILY)
        h.id = 1
        now = datetime(2024, 3, 10, 12, 0, 0)
        # 5 consecutive days a while back
        for i in range(5):
            h.check_off(now - timedelta(days=10 - i))
        # Then only 2 consecutive days recently
        for i in range(2):
            h.check_off(now - timedelta(days=1 - i))
        assert h.get_longest_streak() == 5

    def test_weekly_streak_two_weeks(self):
        h = Habit("Test", "Desc", Periodicity.WEEKLY)
        h.id = 1
        # Use a Monday as "now" to keep things clean
        now = datetime(2024, 3, 11, 12, 0, 0)  # this is a Monday
        h.check_off(now - timedelta(weeks=1))
        h.check_off(now)
        assert h.get_current_streak(now=now) == 2

    def test_longest_streak_weekly_four_weeks(self):
        h = Habit("Test", "Desc", Periodicity.WEEKLY)
        h.id = 1
        now = datetime(2024, 3, 11, 12, 0, 0)  # Monday
        for i in range(4):
            h.check_off(now - timedelta(weeks=3 - i))
        assert h.get_longest_streak() == 4


# =============================================================================
# Completion tests
# =============================================================================

class TestCompletion:

    def test_completion_stores_all_fields(self):
        ts = datetime(2024, 1, 15, 9, 0, 0)
        c = Completion(habit_id=1, timestamp=ts)
        assert c.habit_id == 1
        assert c.timestamp == ts
        assert c.id is None

# =============================================================================
# User tests
# =============================================================================

class TestUser:

    def test_user_stores_id_and_name(self):
        u = User(name="Tomy")
        assert u.name == "Tomy"


# =============================================================================
# HabitManager tests
# =============================================================================

class TestHabitManager:

    def test_add_habit_returns_habit_with_id(self, manager):
        h = manager.add_habit("Run", "Daily run", Periodicity.DAILY)
        assert h.id is not None
        assert h.name == "Run"

    def test_list_habits_is_empty_at_start(self, manager):
        assert manager.list_habits() == []

    def test_list_habits_returns_all_created(self, manager):
        manager.add_habit("Run", "Run", Periodicity.DAILY)
        manager.add_habit("Review", "Review", Periodicity.WEEKLY)
        assert len(manager.list_habits()) == 2

    def test_delete_habit_removes_it(self, manager, daily_habit):
        manager.delete_habit(daily_habit.id)
        assert manager.get_habit(daily_habit.id) is None

    def test_get_habit_returns_correct_habit(self, manager, daily_habit):
        fetched = manager.get_habit(daily_habit.id)
        assert fetched.name == daily_habit.name

    def test_add_completion_saves_it(self, manager, daily_habit):
        manager.add_completion(daily_habit.id)
        completions = manager.get_completions(daily_habit.id)
        assert len(completions) == 1

    def test_cannot_complete_same_habit_twice_in_same_period(self, manager, daily_habit):
        manager.add_completion(daily_habit.id, datetime(2024, 1, 10, 9, 0))
        with pytest.raises(ValueError):
            manager.add_completion(daily_habit.id, datetime(2024, 1, 10, 18, 0))

    def test_list_habits_by_periodicity(self, manager):
        manager.add_habit("Run", "Run", Periodicity.DAILY)
        manager.add_habit("Review", "Review", Periodicity.WEEKLY)
        daily = manager.list_habits_by_periodicity(Periodicity.DAILY)
        weekly = manager.list_habits_by_periodicity(Periodicity.WEEKLY)
        assert len(daily) == 1
        assert len(weekly) == 1

    def test_load_predefined_creates_five_habits(self, manager):
        habits = manager.load_predefined_habits()
        assert len(habits) == 5

    def test_load_predefined_does_not_duplicate(self, manager):
        manager.load_predefined_habits()
        manager.load_predefined_habits()  # call it a second time
        assert len(manager.list_habits()) == 5  # still only 5


# =============================================================================
# Analytics tests
# =============================================================================

class TestAnalytics:

    def test_get_all_habits_returns_all(self, manager, analytics):
        manager.add_habit("A", "a", Periodicity.DAILY)
        manager.add_habit("B", "b", Periodicity.WEEKLY)
        habits = manager.list_habits()
        result = analytics.get_all_habits(habits)
        assert len(result) == 2

    def test_filter_by_daily(self, manager, analytics):
        manager.add_habit("A", "a", Periodicity.DAILY)
        manager.add_habit("B", "b", Periodicity.WEEKLY)
        habits = manager.list_habits()
        daily = analytics.get_habits_by_periodicity(habits, Periodicity.DAILY)
        assert len(daily) == 1
        assert daily[0].name == "A"

    def test_filter_by_weekly(self, manager, analytics):
        manager.add_habit("A", "a", Periodicity.DAILY)
        manager.add_habit("B", "b", Periodicity.WEEKLY)
        habits = manager.list_habits()
        weekly = analytics.get_habits_by_periodicity(habits, Periodicity.WEEKLY)
        assert len(weekly) == 1
        assert weekly[0].name == "B"

    def test_longest_streak_all_returns_the_max(self, manager, analytics):
        h1 = manager.add_habit("A", "a", Periodicity.DAILY)
        h2 = manager.add_habit("B", "b", Periodicity.DAILY)
        now = datetime(2024, 3, 10, 12, 0)
        # h1 gets 3 days, h2 gets 5 days
        for i in range(3):
            manager.add_completion(h1.id, now - timedelta(days=2 - i))
        for i in range(5):
            manager.add_completion(h2.id, now - timedelta(days=4 - i))
        habits = manager.list_habits()
        assert analytics.get_longest_run_streak_all(habits) == 5

    def test_longest_streak_all_returns_zero_when_empty(self, analytics):
        assert analytics.get_longest_run_streak_all([]) == 0

    def test_longest_streak_for_one_habit(self, manager, analytics):
        h = manager.add_habit("A", "a", Periodicity.DAILY)
        now = datetime(2024, 3, 10, 12, 0)
        for i in range(4):
            manager.add_completion(h.id, now - timedelta(days=3 - i))
        habit = manager.get_habit(h.id)
        assert analytics.get_longest_run_streak_for_habit(habit) == 4

    def test_broken_habits(self, manager, analytics):
        h1 = manager.add_habit("A", "a", Periodicity.DAILY)
        h2 = manager.add_habit("B", "b", Periodicity.DAILY)
        now = datetime(2024, 3, 10, 12, 0)
        # h1 only has 1 completion, h2 has 5 in a row
        manager.add_completion(h1.id, now)
        for i in range(5):
            manager.add_completion(h2.id, now - timedelta(days=4 - i))
        habits = manager.list_habits()
        broken = analytics.get_broken_habits(habits, threshold=2)
        assert len(broken) == 1
        assert broken[0].name == "A"

    def test_habits_sorted_by_streak(self, manager, analytics):
        h1 = manager.add_habit("A", "a", Periodicity.DAILY)
        h2 = manager.add_habit("B", "b", Periodicity.DAILY)
        now = datetime(2024, 3, 10, 12, 0)
        # h1 has 1 day, h2 has 3 days
        manager.add_completion(h1.id, now)
        for i in range(3):
            manager.add_completion(h2.id, now - timedelta(days=2 - i))
        habits = manager.list_habits()
        pairs = analytics.get_habits_with_streaks(habits)
        # B should come first because streak 3 > streak 1
        assert pairs[0][0].name == "B"
        assert pairs[1][0].name == "A"