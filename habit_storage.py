# habit_storage.py
# Defines what a storage class needs to be able to do.
# If I ever want to switch from SQLite to JSON, I just write a new class and nothing else in the app needs to change.

from abc import ABC, abstractmethod


class HabitStorage(ABC):
    """Any storage class must implement these methods. ABC is used so Python throws an error if I forget one."""

    @abstractmethod
    def save_habit(self, habit_data):
        pass

    @abstractmethod
    def load_habit(self, habit_id):
        pass

    @abstractmethod
    def delete_habit(self, habit_id):
        pass

    @abstractmethod
    def list_habits(self):
        pass

    @abstractmethod
    def save_completion(self, completion_data):
        pass

    @abstractmethod
    def load_completions(self, habit_id):
        pass