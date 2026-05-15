# Habit Tracker
**Tomy Monteiro de Almeida | IU14077297 | IU International University | DLBDSOOFPP01**

---
## Overview

The Habit Tracker Application lets users create and maintain positive habits or stopping bad ones by tracking both daily and weekly activities. The application provides a simple command-line interface (CLI) through which users can create, delete, check off, view, and analyse their habits.

There is no GUI, just a simple menu you navigate with your keyboard. All data gets saved in a local SQLite database so your habits are still there next time you open the app.

---

## Core Functionality

- Create and delete daily or weekly habits
- Check off a habit for today (or this week)
- See your current streak for each habit
- See the longest streak you ever had
- Filter habits by daily or weekly
- Show an analytics dashboard with all your streaks ranked
- Load 5 predefined habits with 4 weeks of example data for testing

---

## Project Structure

```
├── main.py                  # start here, run this to launch the app
├── periodicity.py           # just the DAILY / WEEKLY enum
├── user.py                  # stores the username for the greeting
├── habit.py                 # the main Habit class, streak logic lives here
├── completion.py            # created every time you check off a habit
├── habit_storage.py         # abstract interface for storage
├── sqlite_habit_storage.py  # the actual database read/write code
├── habit_manager.py         # connects the CLI to the database
├── analytics.py             # all the analysis functions
├── cli.py                   # menus and user input
└── test_data.py             # 31 pytest unit tests
```

The `.db` files get created automatically when you run the app, you don't need to create them yourself.

---

## Requirements

- Python 3.7 or later
- pytest (only needed to run the tests)

```bash
pip install pytest
```

---

## How to run the app

```bash
python main.py
```

When you start it, it asks for your name and which database you want to use:

- **Option 1** — real database (`habits.db`), starts empty, this is for your actual habits
- **Option 2** — test database (`test_habits.db`), loads 5 predefined habits with 4 weeks of data

The databases are stored locally. If you want to start from scratch you need to manually deleted the .db files.

After that you get the main menu:

```
  ================================
  Hello, User!
  ================================
  1. Create habit
  2. Delete habit
  3. Check off habit
  4. Show all habits
  5. Show habits by periodicity
  6. Longest streak (all habits)
  7. Longest streak (specific habit)
  8. Analytics dashboard
  Q. Quit
  ================================
```

Just type the number and press enter.

---

## How to create a habit

Pick option 1, enter a name and a short description, then choose if it is daily or weekly. That's it, the habit gets saved straight away.

## How to check off a habit

Pick option 3, the app shows you a list of your habits with their IDs, enter the ID of the habit you want to check off. If you already checked it off today (or this week for weekly habits) it will tell you and won't let you do it twice.

---

## How to run the tests

```bash
pytest test_data.py -v
```

You should see **31 passed**. The tests use an in-memory database so nothing gets written to disk when you run them.

Here is what gets tested:

| Area         | What is tested                               |
|--------------|----------------------------------------------|
| Periodicity  | Values and loading from string               |
| Habit        | Defaults, streaks, gap detection             |
| Completion   | Fields are stored correctly                  |
| User         | Name is stored correctly                     |
| HabitManager | Create, delete, list, check off habits       |
| Analytics    | All analytics functions                      |

---

## The 5 predefined habits

| Name             | Periodicity |
|------------------|-------------|
| Morning Run      | Daily       |
| Read a Book      | Daily       |
| Meditate         | Daily       |
| Weekly Review    | Weekly      |
| Grocery Shopping | Weekly      |

The test data covers 4 weeks and has a few intentional gaps so the streaks are not perfectly straight — that makes testing more realistic.

---

## A few things worth knowing

- Daily habits reset at midnight, weekly habits reset every Monday at midnight
- You can only check off a habit once per period
- Missing a period breaks your streak back to 0
- If you create a habit at 23:50 and check it off at 00:10 the next day, the app sees those as two different periods — the first one will show as missed

---

## Why I built it this way

I used SQLite instead of JSON because it is already built into Python so there is nothing extra to install, and it makes querying the data easier. I learned this the hard way when I first tried to store datetimes in JSON and kept running into issues loading them back correctly.

The `HabitStorage` abstract class was a bit tricky at first, but it turned out to be really useful because swapping to an in-memory database for testing became really simple without changing anything else.

The `User` class is very minimal right now, it only stores a name for the greeting. I kept it in because it would make adding multi-user support much easier later.

---

### Github

https://github.com/TM-creates/DLBDSOOFPP01_habits_project
