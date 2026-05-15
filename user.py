#user.py
# Keeps track of who uses the app
# For now, it is only used for the greeting and goodbye message.

class User:

    def __init__(self, name):
        self.name = name