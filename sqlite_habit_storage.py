# sqlite_habit_storage.py
# Does all the reading and writing to the sqlite db
# I chose SQLite because it comes built into Python, no extra installation needed.
# All the habit and completion data gets stored in a local .db file.

import sqlite3
from datetime import datetime
from habit_storage import HabitStorage

# SQLite can only store text, not Python datetime objects.
# So I convert datetimes to a string before saving, and back to datetime when loading.
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class SqliteHabitStorage(HabitStorage):
    """Reads and writes to a local .db file using sqlite3."""

    def __init__(self, db_path="habits.db"):
        """Connects to the db file and sets up the tables if they don't exist yet."""
        self.db_path = db_path

        # When running tests I use ":memory:" instead of a real file.
        # A memory database disappears when the test ends, which is what I want.
        # But it only works if I keep the same connection open the whole time —
        # opening a new connection would give an empty database every time.
        if db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self._shared_conn = None

        self._setup_tables()

    def _connect(self):
        """Open and return a connection to the database."""
        if self._shared_conn is not None:
            return self._shared_conn
        return sqlite3.connect(self.db_path)

    def _setup_tables(self):
        """Creates the two tables. IF NOT EXISTS means its safe to run every time."""
        conn = self._connect()

        # habits table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                description TEXT,
                periodicity TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                active      INTEGER NOT NULL DEFAULT 1
            )
        """)

        # completions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id  INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        conn.commit()

    def save_habit(self, habit_data):
        """Inserts a new habit row and returns the id sqlite gave it."""
        conn = self._connect()

        # ? placeholders prevent sql injection
        cursor = conn.execute(
            "INSERT INTO habits (name, description, periodicity, created_at, active) VALUES (?, ?, ?, ?, ?)",
            (
                habit_data["name"],
                habit_data["description"],
                habit_data["periodicity"],
                habit_data["created_at"].strftime(DATE_FORMAT),
                1 if habit_data["active"] else 0,  # store True/False as 1/0
            )
        )
        conn.commit()
        return cursor.lastrowid  # this is the ID SQLite gave the new row

    def load_habit(self, habit_id):
        """Loads one habit by id. Returns None if it doesn't exist."""
        conn = self._connect()
        conn.row_factory = sqlite3.Row  # lets us access columns by name like row["name"]
        row = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_habit_dict(row)

    def delete_habit(self, habit_id):
        conn = self._connect()
        # delete completions first, then the habit
        conn.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
        conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        conn.commit()

    def list_habits(self):
        """Loads all habits where active=1 as a list of dicts."""
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM habits WHERE active = 1").fetchall()
        result = []
        for r in rows:
            result.append(self._row_to_habit_dict(r))
        return result

    def save_completion(self, completion_data):
        """Saves a completion with the habit id and timestamp."""
        conn = self._connect()
        conn.execute(
            "INSERT INTO completions (habit_id, timestamp) VALUES (?, ?)",
            (
                completion_data["habit_id"],
                completion_data["timestamp"].strftime(DATE_FORMAT),
            )
        )
        conn.commit()

    def load_completions(self, habit_id):
        """Load all completions for one habit, sorted oldest first."""
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM completions WHERE habit_id = ? ORDER BY timestamp ASC",
            (habit_id,)
        ).fetchall()
        result = []
        for r in rows:
            result.append(self._row_to_completion_dict(r))
        return result

    def _row_to_habit_dict(self, row):
        """Turns a sqlite row into a dict with proper Python types, strings become datetimes, 1/0 becomes True/False."""
        return {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "periodicity": row["periodicity"],
            "created_at": datetime.strptime(row["created_at"], DATE_FORMAT),  # string back to datetime
            "active": bool(row["active"]),  # 1/0 back to True/False
        }

    def _row_to_completion_dict(self, row):
        return {
            "habit_id": row["habit_id"],
            "timestamp": datetime.strptime(row["timestamp"], DATE_FORMAT),  # string back to datetime
        }