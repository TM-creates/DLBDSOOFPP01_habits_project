# completion.py
# created every time a user checks off a habit
# Needs habit id and timestamp


class Completion:

    def __init__(self, habit_id, timestamp, completion_id=None):
        """completion_id is None until saved to the db."""
        self.id = completion_id
        self.habit_id = habit_id
        self.timestamp = timestamp