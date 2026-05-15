# periodicity.py
# Defines two possible periods a habit can have "daily" and "weekly"

from enum import Enum

class Periodicity(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"