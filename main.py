import datetime
import json
import os

class FileManager:
    @staticmethod
    def read_file_exists(file_name: str):
        """True when the file exists and holds something other than whitespace."""

        if not os.path.exists(file_name):
            return False

        return os.path.getsize(file_name) > 0

    @staticmethod
    def read_file(file_name: str):
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def write_file(file_name: str, mode: str, content: str):
        with open(file_name, mode, encoding="utf-8") as file:
            file.write(content)

    @staticmethod
    def read_json(file_name: str):
        content = FileManager.read_file(file_name)

        if content == "":
            return []

        return json.loads(content)

    @staticmethod
    def write_json(file_name: str, data):
        FileManager.write_file(
            file_name,
            "w",
            json.dumps(data, indent=4)
        )

    @staticmethod
    def append_json(file_name: str, data):
        FileManager.write_file(
            file_name,
            "a",
            json.dumps(data, indent=4)
        )

class Utilities:
    @staticmethod
    def clear_terminal():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def today():
        """Returns today's date as YYYY-MM-DD."""

        return datetime.date.today().isoformat()

    @staticmethod
    def parse_date(value: str):
        """Turns YYYY-MM-DD into a date object, or returns None."""

        try:
            return datetime.date.fromisoformat(value.strip())
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def format_number(value):
        """Displays 95.0 as 95 but keeps 95.5 as 95.5."""

        number = float(value)

        if number.is_integer():
            return str(int(number))

        return str(round(number, 2))

    @staticmethod
    def date_converter(date: str):
        """Turns input like "1/5/2024" or "January 5, 2024" into "2024-01-05".

        Raises ValueError on anything unparseable or out of range.
        """

        if date.strip() == "":
            return ""

        month_list = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]
        month_names = [name.casefold() for name in month_list]

        cleaned = date

        for separator in ("/", ".", "-", ","):
            cleaned = cleaned.replace(separator, " ")

        parts = cleaned.split()

        if len(parts) != 3:
            raise ValueError(f"'{date}' is not a month, day, and year.")

        # Accept "January 5 2024" and "5 January 2024" alike. A number is never
        # a month name, so purely numeric input stays month-first as mm/dd/yyyy.
        if (
            parts[0].casefold() not in month_names
            and parts[1].casefold() in month_names
        ):
            parts[0], parts[1] = parts[1], parts[0]

        if parts[0].casefold() in month_names:
            month = month_names.index(parts[0].casefold()) + 1
        else:
            # Accept three-letter abbreviations like "jan"; every month's
            # first three letters are distinct.
            abbreviation = parts[0].casefold()[:3]

            if abbreviation in [name[:3] for name in month_names]:
                month = [name[:3] for name in month_names].index(abbreviation) + 1
            else:
                month = int(parts[0])

        day = int(parts[1])
        year = int(parts[2])

        if year < 1000:
            raise ValueError(f"'{date}' needs a four digit year.")

        return datetime.date(year, month, day).isoformat()

class Prompts:
    """Shared input helpers that re-ask until the answer is usable."""

    @staticmethod
    def text(prompt, allow_blank=False):
        """Returns non-blank text, or a blank string when that is allowed."""

        while True:
            value = input(prompt).strip()

            if value or allow_blank:
                return value

            print("That cannot be empty.")

    @staticmethod
    def number(prompt, allow_blank=False):
        """Returns a non-negative number, or None when blank is allowed."""

        while True:
            value = input(prompt).strip()

            if not value and allow_blank:
                return None

            try:
                number = float(value)
            except ValueError:
                print("Enter a number.")
                continue

            if number < 0:
                print("Numbers cannot be negative.")
                continue

            return number

    @staticmethod
    def whole_number(prompt):
        """Returns an integer, re-asking until it gets one."""

        while True:
            value = input(prompt).strip()

            try:
                return int(value)
            except ValueError:
                print("Enter a whole number.")

    @staticmethod
    def date(prompt, allow_blank=False):
        """Returns a YYYY-MM-DD string, or None when blank is allowed.

        Accepts 'today' as a shortcut.
        """

        while True:
            value = input(prompt).strip()

            if not value and allow_blank:
                return None

            if value.casefold() == "today":
                return Utilities.today()

            try:
                return Utilities.date_converter(value)
            except ValueError:
                print("Not a valid date. Try mm/dd/yyyy, or 'today'.")

    @staticmethod
    def find_by_id(items, prompt, label):
        """Returns the item whose id matches, re-asking until one does."""

        while True:
            goal_id = Prompts.whole_number(prompt)

            for item in items:
                if item["id"] == goal_id:
                    return item

            print(f"No {label} with id {goal_id}.")

    @staticmethod
    def confirmed(prompt):
        """True only when the answer starts with y."""

        return input(prompt).strip().casefold().startswith("y")



class GoalManager:
    FILE_NAME = "goals.json"
    DATA_KEY = "goals"

    def __init__(self):
        # Create the store the first time the goal app is opened.
        if not FileManager.read_file_exists(self.FILE_NAME):
            self.goals = []
            self.save()
        else:
            data = FileManager.read_json(self.FILE_NAME)

            if not isinstance(data, dict) or not isinstance(
                data.get(self.DATA_KEY), list
            ):
                raise ValueError(
                    f"{self.FILE_NAME} must contain a JSON object "
                    f'with a "{self.DATA_KEY}" list.'
                )

            self.goals = data[self.DATA_KEY]

    def save(self):
        FileManager.write_json(self.FILE_NAME, {self.DATA_KEY: self.goals})

    def _next_id(self):
        if not self.goals:
            return 1
        return max(goal["id"] for goal in self.goals) + 1

    def create_goal(self, name, description="", category="",
                    start_date="", target_date="",
                    target=0, progress_unit=""):
        goal = {
            "id": self._next_id(),
            "name": name,
            "description": description,
            "category": category,
            "start_date": start_date,
            "target_date": target_date,
            "progress": 0,
            "target": target,
            "progress_unit": progress_unit,
            "status": "active",
            "milestones": []
        }
        self.goals.append(goal)
        self.save()
        return goal

    def find_goal(self, goal_id):
        for goal in self.goals:
            if goal["id"] == goal_id:
                return goal
        return None

    def delete_goal(self, goal_id):
        self.goals = [g for g in self.goals if g["id"] != goal_id]
        self.save()

    def update_progress(self, goal_id, progress):
        """Sets progress, refusing negatives and anything past the target.

        Returns False when the goal is unknown or the value is rejected.
        """

        goal = self.find_goal(goal_id)

        if not goal:
            return False

        if progress < 0:
            return False

        if goal["target"] > 0 and progress > goal["target"]:
            return False

        goal["progress"] = progress
        self.save()
        return True

    def mark_complete(self, goal_id):
        goal = self.find_goal(goal_id)
        if not goal:
            return False
        goal["status"] = "completed"
        goal["progress"] = goal["target"]
        self.save()
        return True

    @staticmethod
    def percent(progress, target):
        if target <= 0:
            return None
        return round((progress / target) * 100, 1)

    def edit_goal(self, goal_id, **changes):
        """Applies only the keys present in changes, leaving the rest alone."""

        goal = self.find_goal(goal_id)

        if not goal:
            return False

        allowed = (
            "name", "description", "category", "start_date",
            "target_date", "target", "progress_unit"
        )

        for key, value in changes.items():
            if key in allowed and value is not None:
                goal[key] = value

        self.save()
        return True

    def add_milestone(self, goal_id, name):
        goal = self.find_goal(goal_id)

        if not goal:
            return False

        goal["milestones"].append({"name": name, "complete": ""})
        self.save()
        return True

    def toggle_milestone(self, goal_id, index):
        goal = self.find_goal(goal_id)

        if not goal or not 0 <= index < len(goal["milestones"]):
            return False

        milestone = goal["milestones"][index]
        milestone["complete"] = "" if milestone["complete"] == "x" else "x"
        self.save()
        return True

    def goals_by_status(self, status):
        return [goal for goal in self.goals if goal["status"] == status]

    def days_remaining(self, goal):
        target = Utilities.parse_date(goal["target_date"])

        if not target:
            return None

        remaining = (target - Utilities.parse_date(Utilities.today())).days
        return remaining

    def progress_text(self, goal):
        unit = goal["progress_unit"]
        suffix = f" {unit}" if unit else ""
        target = Utilities.format_number(goal["target"])
        progress = Utilities.format_number(goal["progress"])
        text = f"{progress} / {target}{suffix}"

        percent = self.percent(goal["progress"], goal["target"])

        if percent is None:
            return f"{text} (no target set)"

        return f"{text} ({percent}%)"

    def display_goals(self, goals=None):
        goals = self.goals if goals is None else goals

        if not goals:
            print("You have no goals.")
            return

        for goal in goals:
            mark = "x" if goal["status"] == "completed" else " "
            category = f" [{goal['category']}]" if goal["category"] else ""

            print(
                f"[{mark}] {goal['id']}. {goal['name']}{category} "
                f"— {self.progress_text(goal)}"
            )

    def display_goal(self, goal):
        print(f"Goal {goal['id']}: {goal['name']}")

        if goal["description"]:
            print(f"  Description: {goal['description']}")

        if goal["category"]:
            print(f"  Category: {goal['category']}")

        print(f"  Progress: {self.progress_text(goal)}")
        print(f"  Status: {goal['status']}")

        if goal["start_date"]:
            print(f"  Start date: {goal['start_date']}")

        if goal["target_date"]:
            remaining = self.days_remaining(goal)

            if remaining is None:
                print(f"  Target date: {goal['target_date']}")
            elif remaining < 0:
                overdue = abs(remaining)
                print(f"  Target date: {goal['target_date']} ({overdue} days overdue)")
            elif remaining == 0:
                print(f"  Target date: {goal['target_date']} (due today)")
            else:
                print(f"  Target date: {goal['target_date']} ({remaining} days left)")

        if not goal["milestones"]:
            print("  No milestones yet.")
        else:
            print("  Milestones:")

            for index, milestone in enumerate(goal["milestones"], start=1):
                print(f"    [{milestone['complete']}] {index}. {milestone['name']}")

    @staticmethod
    def ask_text(prompt, allow_blank=False):
        """Keeps asking until it gets text, or a blank answer if that is allowed."""

        return Prompts.text(prompt, allow_blank)

    @staticmethod
    def ask_number(prompt, allow_blank=False):
        """Returns a non-negative number, or None when blank is allowed."""

        return Prompts.number(prompt, allow_blank)

    @staticmethod
    def ask_date(prompt, allow_blank=False):
        """Returns a YYYY-MM-DD string, or None when blank is allowed."""

        return Prompts.date(prompt, allow_blank)

    @staticmethod
    def ask_id(goals, prompt="Enter a goal id: "):
        """Returns the goal with the id the user enters."""

        return Prompts.find_by_id(goals, prompt, "goal")

    def create_goal_interactively(self):
        print("Creating a goal. Press enter to skip anything optional.")

        name = self.ask_text("Goal name: ")
        description = self.ask_text("Description (optional): ", True)
        category = self.ask_text("Category (optional): ", True)
        start_date = self.ask_date("Start date (optional): ", True)
        target_date = self.ask_date("Target date (optional): ", True)
        target = self.ask_number("Target amount (optional): ", True)
        unit = self.ask_text("Progress unit, e.g. lb (optional): ", True)

        goal = self.create_goal(
            name,
            description=description,
            category=category,
            start_date=start_date or "",
            target_date=target_date or "",
            target=target or 0,
            progress_unit=unit
        )

        print(f"Created goal {goal['id']}.")
        return goal

    @staticmethod
    def show_help():
        print("""Goal commands:
1. create                  create a goal
2. view                    view every goal
3. view <id>               view one goal
4. progress <id>           update progress toward a goal
5. edit <id>               edit a goal's details
6. complete <id>           mark a goal completed
7. delete <id>             delete a goal
8. active                  view active goals
9. completed               view completed goals
10. milestone <id> <name>  add a milestone to a goal
11. toggle <id> <n>        toggle milestone n on goal id
/back, /exit               return to the apps menu
/quit                      quit the whole program""")

    def run(self):
        Utilities.clear_terminal()
        print("Entered Goals. Type /help for commands, numbers for the menu.")

        while True:
            self.show_menu()

            choice = input("Goals: What do you want to do? ").strip().lower()

            if choice in ("/quit", "quit"):
                raise SystemExit

            if choice in ("/exit", "/back", "back", "8", ""):
                Utilities.clear_terminal()
                return

            if choice in ("/help", "help", "?"):
                self.show_help()
            elif choice in ("1", "create", "create goal"):
                self.create_goal_interactively()
            elif choice in ("2", "view", "view goals"):
                self.display_goals()
            elif choice == "3":
                self.display_goal(self.ask_id(self.goals, "Goal id to view: "))
            elif choice in ("4", "progress", "update goal progress"):
                self.update_progress_interactively()
            elif choice in ("5", "edit", "edit goal"):
                self.edit_goal_interactively()
            elif choice in ("6", "complete", "complete goal"):
                goal = self.ask_id(self.goals, "Goal id to complete: ")

                if self.mark_complete(goal["id"]):
                    print(f"Completed goal {goal['id']}.")
            elif choice in ("7", "delete", "delete goal"):
                self.delete_goal_interactively()
            elif choice == "8":
                self.display_goals(self.goals_by_status("active"))
            elif choice == "9":
                self.display_goals(self.goals_by_status("completed"))
            elif choice in ("10", "milestone"):
                self.add_milestone_interactively()
            elif choice in ("11", "toggle"):
                self.toggle_milestone_interactively()
            else:
                print("That is not a goal command. Try /help.")

    def show_menu(self):
        print("""
Goals
1. Create Goal
2. View Goals
3. View Goal
4. Update Goal Progress
5. Edit Goal
6. Complete Goal
7. Delete Goal
8. Active Goals
9. Completed Goals
10. Add Milestone
11. Toggle Milestone
/back: return to apps
""")

    def update_progress_interactively(self):
        if not self.goals:
            print("You have no goals.")
            return

        goal = self.ask_id(self.goals, "Goal id to update: ")

        print(f"Current: {self.progress_text(goal)}")

        amount = self.ask_number("New progress amount: ")

        if goal["target"] > 0 and amount > goal["target"]:
            print(
                f"That is over the target of "
                f"{Utilities.format_number(goal['target'])}. Try again."
            )
            return

        if goal["status"] == "completed" and amount < goal["target"]:
            goal["status"] = "active"

        self.update_progress(goal["id"], amount)
        print(f"{goal['name']} is now {self.progress_text(goal)}.")

    def edit_goal_interactively(self):
        if not self.goals:
            print("You have no goals.")
            return

        goal = self.ask_id(self.goals, "Goal id to edit: ")
        print("Press enter to keep the current value.")

        changes = {
            "name": self.ask_text(f"Name [{goal['name']}]: ", True) or None,
            "description": self.ask_text(
                f"Description [{goal['description']}]: ", True
            ),
            "category": self.ask_text(
                f"Category [{goal['category']}]: ", True
            ),
            "target_date": self.ask_date(
                f"Target date [{goal['target_date']}]: ", True
            ),
            "target": self.ask_number(
                f"Target [{Utilities.format_number(goal['target'])}]: ", True
            ),
            "progress_unit": self.ask_text(
                f"Unit [{goal['progress_unit']}]: ", True
            )
        }

        # A blank answer keeps the old value, so only send real edits through.
        self.edit_goal(goal["id"], **{
            key: value for key, value in changes.items()
            if value is not None and value != ""
        })

        print(f"Updated goal {goal['id']}.")

    def delete_goal_interactively(self):
        if not self.goals:
            print("You have no goals.")
            return

        goal = self.ask_id(self.goals, "Goal id to delete: ")
        confirmation = input(
            f"Delete '{goal['name']}'? (y/n): "
        ).strip().casefold()

        if confirmation == "y":
            self.delete_goal(goal["id"])
            print(f"Deleted goal {goal['id']}.")
        else:
            print("Nothing was deleted.")

    def add_milestone_interactively(self):
        if not self.goals:
            print("You have no goals.")
            return

        goal = self.ask_id(self.goals, "Goal id: ")
        name = self.ask_text("Milestone: ")

        if self.add_milestone(goal["id"], name):
            print(f"Added milestone to goal {goal['id']}.")

    def toggle_milestone_interactively(self):
        goal = self.ask_id(self.goals, "Goal id: ")

        if not goal["milestones"]:
            print("That goal has no milestones.")
            return

        for index, milestone in enumerate(goal["milestones"], start=1):
            print(f"  [{milestone['complete']}] {index}. {milestone['name']}")

        number = self.ask_number("Milestone number: ")

        if number is None or number != int(number):
            print("Enter a milestone number.")
            return

        if self.toggle_milestone(goal["id"], int(number) - 1):
            print("Milestone toggled.")
        else:
            print("That milestone does not exist.")

import datetime



class HabitManager:
    FILE_NAME = "habits.json"
    DATA_KEY = "habits"
    FREQUENCIES = ("daily", "weekly")

    def __init__(self):
        # Create the store the first time the habit app is opened.
        if not FileManager.read_file_exists(self.FILE_NAME):
            self.habits = []
            self.save()
        else:
            data = FileManager.read_json(self.FILE_NAME)

            if not isinstance(data, dict) or not isinstance(
                data.get(self.DATA_KEY), list
            ):
                raise ValueError(
                    f"{self.FILE_NAME} must contain a JSON object "
                    f'with a "{self.DATA_KEY}" list.'
                )

            self.habits = data[self.DATA_KEY]

    def save(self):
        FileManager.write_json(self.FILE_NAME, {self.DATA_KEY: self.habits})

    def _next_id(self):
        if not self.habits:
            return 1
        return max(habit["id"] for habit in self.habits) + 1

    def create_habit(self, name, description="", category="",
                     frequency="daily", created_date=None):
        habit = {
            "id": self._next_id(),
            "name": name,
            "description": description,
            "category": category,
            "frequency": frequency,
            "created_date": created_date or Utilities.today(),
            "completion_history": []
        }
        self.habits.append(habit)
        self.save()
        return habit

    def find_habit(self, habit_id):
        for habit in self.habits:
            if habit["id"] == habit_id:
                return habit
        return None

    def delete_habit(self, habit_id):
        self.habits = [h for h in self.habits if h["id"] != habit_id]
        self.save()

    def edit_habit(self, habit_id, **changes):
        habit = self.find_habit(habit_id)

        if not habit:
            return False

        allowed = ("name", "description", "category", "frequency")

        for key, value in changes.items():
            if key in allowed and value:
                habit[key] = value

        self.save()
        return True

    @staticmethod
    def week_start(day):
        """Returns the Monday of the week containing day."""

        return day - datetime.timedelta(days=day.weekday())

    @staticmethod
    def _within_week(day, start):
        """True when day falls inside the seven days starting at start."""

        if not day:
            return False

        return start <= day < start + datetime.timedelta(days=7)

    def _completed_dates(self, habit):
        """Returns the habit's completions as a sorted list of date objects."""

        return HabitManager._completed_dates_static(habit)

    def is_completed_on(self, habit, day):
        if habit["frequency"] == "weekly":
            target = HabitManager.week_start(day)
            return any(
                (parsed - target).days < 7 and parsed >= target
                for parsed in self._completed_dates(habit)
            )

        return day in set(self._completed_dates(habit))

    def complete_today(self, habit_id, day=None):
        habit = self.find_habit(habit_id)

        if not habit:
            return False

        day = day or datetime.date.today()

        if self.is_completed_on(habit, day):
            return False

        habit["completion_history"].append(day.isoformat())
        habit["completion_history"] = sorted(set(habit["completion_history"]))
        self.save()
        return True

    def uncomplete_today(self, habit_id, day=None):
        habit = self.find_habit(habit_id)

        if not habit:
            return False

        day = day or datetime.date.today()

        if habit["frequency"] == "weekly":
            target = HabitManager.week_start(day)
            habit["completion_history"] = [
                entry for entry in habit["completion_history"]
                if not HabitManager._within_week(
                    Utilities.parse_date(entry), target
                )
            ]
        else:
            habit["completion_history"] = [
                entry for entry in habit["completion_history"]
                if entry != day.isoformat()
            ]

        self.save()
        return True

    @staticmethod
    def _completed_dates_static(habit):
        """Returns completions as a sorted list of date objects.

        Duplicates are dropped so one entry can never count twice.
        """

        dates = set()

        for entry in habit["completion_history"]:
            parsed = Utilities.parse_date(entry)

            if parsed:
                dates.add(parsed)

        return sorted(dates)

    @staticmethod
    def _periods(habit):
        """Returns one canonical date per completed period.

        Daily habits use the day itself; weekly habits use the Monday of the
        week, so a week counts once no matter how many completions land in it.
        """

        dates = HabitManager._completed_dates_static(habit)

        if habit["frequency"] == "weekly":
            return sorted({HabitManager.week_start(d) for d in dates})

        return dates

    @staticmethod
    def _today_for(habit):
        """Never looks past the habit's creation date."""

        today = datetime.date.today()
        created = Utilities.parse_date(habit["created_date"])

        if created and created > today:
            return created

        return today

    def current_streak(self, habit):
        """Length of the run of periods ending today or yesterday.

        Yesterday still counts so an unfinished day does not read as a broken
        streak before the user has had a chance to complete it.
        """

        periods = self._periods(habit)

        if not periods:
            return 0

        step = datetime.timedelta(days=7 if habit["frequency"] == "weekly" else 1)
        today = self._today_for(habit)
        anchor = today if today in periods else None

        if anchor is None:
            previous = today - step

            if previous not in periods:
                return 0

            anchor = previous

        streak = 0
        cursor = anchor

        while cursor in periods:
            streak += 1
            cursor -= step

        return streak

    def longest_streak(self, habit):
        """The longest run of consecutive periods ever recorded."""

        periods = self._periods(habit)

        if not periods:
            return 0

        step = datetime.timedelta(days=7 if habit["frequency"] == "weekly" else 1)
        longest = 1
        run = 1

        for index in range(1, len(periods)):
            if periods[index] - periods[index - 1] == step:
                run += 1
                longest = max(longest, run)
            else:
                run = 1

        return longest

    def completion_percentage(self, habit, today=None):
        """Share of periods since creation that were completed."""

        created = Utilities.parse_date(habit["created_date"])

        if not created:
            return 0.0

        today = today or datetime.date.today()

        if habit["frequency"] == "weekly":
            elapsed = (
                (
                    HabitManager.week_start(today)
                    - HabitManager.week_start(created)
                ).days // 7
            ) + 1
        else:
            elapsed = (today - created).days + 1

        if elapsed <= 0:
            return 0.0

        return round((len(self._periods(habit)) / elapsed) * 100, 1)

    def is_completed_today(self, habit):
        return self.is_completed_on(habit, datetime.date.today())

    def display_habits(self, habits=None):
        habits = self.habits if habits is None else habits

        if not habits:
            print("You have no habits.")
            return

        for habit in habits:
            mark = "x" if self.is_completed_today(habit) else " "
            category = f" [{habit['category']}]" if habit["category"] else ""

            print(
                f"[{mark}] {habit['id']}. {habit['name']}{category} "
                f"({habit['frequency']}) — "
                f"streak {self.current_streak(habit)}, "
                f"{self.completion_percentage(habit)}%"
            )

    def display_habit(self, habit):
        print(f"Habit {habit['id']}: {habit['name']}")

        if habit["description"]:
            print(f"  Description: {habit['description']}")

        if habit["category"]:
            print(f"  Category: {habit['category']}")

        print(f"  Frequency: {habit['frequency']}")
        print(f"  Created: {habit['created_date']}")
        print(f"  Current streak: {self.current_streak(habit)}")
        print(f"  Longest streak: {self.longest_streak(habit)}")
        print(f"  Completion rate: {self.completion_percentage(habit)}%")

        done_today = self.is_completed_today(habit)
        print(f"  Completed today: {'yes' if done_today else 'no'}")

        history = habit["completion_history"]

        if not history:
            print("  No completions yet.")
        else:
            print(f"  History ({len(history)}): {', '.join(history)}")

    def display_today(self):
        today = datetime.date.today().isoformat()
        print(f"Habits for {today}:")
        self.display_habits()

    def display_history(self, habit):
        dates = HabitManager._completed_dates_static(habit)

        if not dates:
            print(f"'{habit['name']}' has no completions yet.")
            return

        print(f"History for {habit['name']} ({len(dates)} completions):")

        for day in dates:
            print(f"  {day.isoformat()}")

    @staticmethod
    def show_help():
        print("""Habit commands:
1. create                  create a habit
2. view                    view every habit
3. view <id>               view one habit
4. complete <id>           mark a habit complete for today
5. uncomplete <id>         undo today's completion
6. today                   view today's habits
7. history <id>            view completion history
8. edit <id>               edit a habit
9. delete <id>             delete a habit
/back, /exit               return to the apps menu
/quit                      quit the whole program""")

    def show_menu(self):
        print("""
Habits
1. Create Habit
2. View Habits
3. View Habit
4. Complete Habit Today
5. Uncomplete Habit Today
6. View Today's Habits
7. View Habit History
8. Edit Habit
9. Delete Habit
/back: return to apps
""")

    def run(self):
        Utilities.clear_terminal()
        print("Entered Habits. Type /help for commands, numbers for the menu.")

        while True:
            self.show_menu()

            choice = input("Habits: What do you want to do? ").strip().lower()

            if choice in ("/quit", "quit"):
                raise SystemExit

            if choice in ("/exit", "/back", "back", ""):
                Utilities.clear_terminal()
                return

            if choice in ("/help", "help", "?"):
                self.show_help()
            elif choice in ("1", "create", "create habit"):
                self.create_habit_interactively()
            elif choice in ("2", "view", "view habits"):
                self.display_habits()
            elif choice == "3":
                self.display_habit(self.ask_id("Habit id: "))
            elif choice in ("4", "complete", "complete habit today"):
                self.complete_interactively()
            elif choice in ("5", "uncomplete", "uncomplete habit today"):
                self.uncomplete_interactively()
            elif choice in ("6", "today", "view today's habits"):
                self.display_today()
            elif choice in ("7", "history"):
                habit = self.ask_id("Habit id: ")
                self.display_history(habit)
            elif choice in ("8", "edit", "edit habit"):
                self.edit_habit_interactively()
            elif choice in ("9", "delete", "delete habit"):
                self.delete_habit_interactively()
            else:
                print("That is not a habit command. Try /help.")

    def ask_id(self, prompt="Enter a habit id: "):
        """Returns the habit with the id the user enters."""

        return Prompts.find_by_id(self.habits, prompt, "habit")

    def create_habit_interactively(self):
        print("Creating a habit. Press enter to skip anything optional.")

        name = Prompts.text("Habit name: ")
        description = Prompts.text("Description (optional): ", True)
        category = Prompts.text("Category (optional): ", True)

        while True:
            frequency = Prompts.text(
                f"Frequency, {' or '.join(HabitManager.FREQUENCIES)}: ", True
            ).casefold()

            if not frequency:
                frequency = "daily"
            elif frequency not in HabitManager.FREQUENCIES:
                print(f"Pick one of: {', '.join(HabitManager.FREQUENCIES)}.")
                continue

            break

        created = Prompts.date("Creation date (optional, default today): ", True)

        habit = self.create_habit(
            name,
            description=description,
            category=category,
            frequency=frequency,
            created_date=created
        )

        print(f"Created habit {habit['id']} ({habit['frequency']}).")
        return habit

    def complete_interactively(self):
        if not self.habits:
            print("You have no habits.")
            return

        habit = self.ask_id()

        if self.complete_today(habit["id"]):
            print(f"Completed '{habit['name']}' for today.")
        else:
            print(f"'{habit['name']}' is already done for today.")

    def uncomplete_interactively(self):
        if not self.habits:
            print("You have no habits.")
            return

        habit = self.ask_id()

        if self.uncomplete_today(habit["id"]):
            print(f"Undid today's completion for '{habit['name']}'.")
        else:
            print(f"'{habit['name']}' was not completed today.")

    def edit_habit_interactively(self):
        if not self.habits:
            print("You have no habits.")
            return

        habit = self.ask_id()
        print("Press enter to keep the current value.")

        changes = {
            "name": Prompts.text(f"Name [{habit['name']}]: ", True),
            "description": Prompts.text(
                f"Description [{habit['description']}]: ", True
            ),
            "category": Prompts.text(f"Category [{habit['category']}]: ", True),
            "frequency": Prompts.text(
                f"Frequency, {' or '.join(HabitManager.FREQUENCIES)} "
                f"[{habit['frequency']}]: ", True
            ).casefold()
        }

        frequency = changes["frequency"]

        if frequency and frequency not in HabitManager.FREQUENCIES:
            print(f"'{frequency}' is not a valid frequency. Nothing changed.")
            return

        # A blank answer keeps the old value, so only send real edits through.
        self.edit_habit(habit["id"], **{
            key: value for key, value in changes.items() if value
        })

        print(f"Updated habit {habit['id']}.")

    def delete_habit_interactively(self):
        if not self.habits:
            print("You have no habits.")
            return

        habit = self.ask_id()

        if Prompts.confirmed(f"Delete '{habit['name']}'? (y/n): "):
            self.delete_habit(habit["id"])
            print(f"Deleted habit {habit['id']}.")
        else:
            print("Nothing was deleted.")

import os
import sys





class TaskManager:
    FILE_NAME = "tasks.json"

    def __init__(self):
        self.tasks = FileManager.write_file(self.FILE_NAME, "a", "")
        self.tasks = FileManager.read_json(self.FILE_NAME)

    def save(self):
        FileManager.write_json(self.FILE_NAME, self.tasks)

    def display_tasks(self):
        if not self.tasks:
            print("You have no tasks.")
            return

        for task in self.tasks:
            print(
                f"[{task['complete']}] "
                f"{task['name']} "
                f"(@{task['due_date']})"
            )

    def add_task(self, name: str, due_date: str):
        task = {
            "name": name,
            "due_date": due_date,
            "complete": ""
        }

        self.tasks.append(task)
        self.save()

    def delete_all_tasks(self):
        self.tasks = []
        self.save()

    @staticmethod
    def _matches(task: dict, name: str):
        """Compares task names case-insensitively, ignoring surrounding space."""

        return task["name"].strip().casefold() == name.strip().casefold()

    def clear_task(self, name: str):
        remaining = [
            task for task in self.tasks
            if not self._matches(task, name)
        ]

        removed = len(self.tasks) - len(remaining)
        self.tasks = remaining

        self.save()

        return removed

    def toggle_complete(self, name: str):
        found = False

        for task in self.tasks:
            if self._matches(task, name):
                found = True

                if task["complete"] == "x":
                    task["complete"] = ""
                else:
                    task["complete"] = "x"

        self.save()

        return found

    def run(self):
        """Runs the task application."""

        Utilities.clear_terminal()
        print("Entered Tasks...")

        while True:
            self.display_tasks()

            task_input = input("Tasks: What do you want to do? ")

            if task_input.startswith("/"):
                if task_input == "/exit":
                    Utilities.clear_terminal()
                    break

                elif task_input == "/quit":
                    sys.exit()

                elif task_input == "/help":
                    Utilities.clear_terminal()
                    print(
                        """Task commands:
/exit: exits tasks
/quit: quits the whole program
/apps: shows available apps

Task functions:
add <task>
delete all tasks
clear <task>
complete <task>
"""
                    )

                elif task_input == "/apps":
                    print(
                        "Apps:\n"
                        "tasks: task tracker\n"
                        "goals: goal tracker\n"
                        "habits: habit tracker\n"
                        "workouts: workout tracker"
                    )

                else:
                    print("Command doesn't exist.")

                continue

            if task_input.startswith("add "):
                Utilities.clear_terminal()
                task_name = task_input[4:]

                due_date = input(
                    "When is your task due "
                    "(format mm/dd/yyyy, and words are fine)? "
                )

                try:
                    due_date = Utilities.date_converter(due_date)

                    self.add_task(task_name, due_date)

                    Utilities.clear_terminal()

                except ValueError:
                    Utilities.clear_terminal()
                    print("Not a valid date.")

            elif task_input in (
                "delete all task",
                "delete all tasks"
            ):
                Utilities.clear_terminal()

                self.delete_all_tasks()

                print("Tasks cleared.")

            elif task_input.startswith("clear "):
                task_name = task_input[6:]

                Utilities.clear_terminal()

                if not task_name.strip():
                    print("Usage: clear <task>")
                elif self.clear_task(task_name):
                    print(f"Cleared {task_name.strip()}.")
                else:
                    print(f"No task called '{task_name.strip()}'.")

            elif task_input.startswith("complete "):
                task_name = task_input[9:]

                Utilities.clear_terminal()

                if not task_name.strip():
                    print("Usage: complete <task>")
                elif self.toggle_complete(task_name):
                    print(f"Toggled {task_name.strip()}.")
                else:
                    print(f"No task called '{task_name.strip()}'.")

            else:
                Utilities.clear_terminal()
                print("That does not exist.")

class WorkoutManager:
    FILE_NAME = "workout.json"

    def __init__(self):
        # Create a valid empty store the first time the workout app is opened.
        if not os.path.exists(self.FILE_NAME) or os.path.getsize(self.FILE_NAME) == 0:
            FileManager.write_json(self.FILE_NAME, [])
        self.workout = FileManager.read_json(self.FILE_NAME)
        if not isinstance(self.workout, list):
            raise ValueError(f"{self.FILE_NAME} must contain a JSON list of workout days.")

    def save(self):
        FileManager.write_json(self.FILE_NAME, self.workout)

    def display_days(self):
        print("Workout days:")
        if not self.workout:
            print("You have no workout days.")
            return

        for index, day in enumerate(self.workout, start=1):
            category = f" [{day['category']}]" if day.get("category") else ""
            print(f"{index}. Day {index}{category} — {len(day['exercises'])} exercise(s)")

    @staticmethod
    def _day_index(value, count):
        try:
            index = int(value) - 1
        except ValueError:
            return None
        return index if 0 <= index < count else None

    def display_day(self, day_number):
        index = self._day_index(day_number, len(self.workout))
        if index is None:
            print("That workout day does not exist.")
            return
        day = self.workout[index]
        label = f" ({day['category']})" if day.get("category") else ""
        print(f"Day {index + 1}{label}:")
        if not day["exercises"]:
            print("  No exercises yet.")
            return
        for exercise_index, exercise in enumerate(day["exercises"], start=1):
            print(f"  {exercise_index}. {exercise['name']}")
            if not exercise["sets"]:
                print("     No sets yet.")
            for set_index, workout_set in enumerate(exercise["sets"], start=1):
                print(f"     Set {set_index}: {workout_set['weight']} weight x {workout_set['reps']} reps")

    def add_day(self, category=""):
        self.workout.append({"category": category.strip(), "exercises": []})
        self.save()
        print(f"Added day {len(self.workout)}.")

    def delete_day(self, day_number):
        index = self._day_index(day_number, len(self.workout))
        if index is None:
            print("That workout day does not exist.")
            return
        del self.workout[index]
        self.save()
        print(f"Deleted day {day_number}.")

    def add_exercise(self, day_number, name):
        index = self._day_index(day_number, len(self.workout))
        if index is None:
            print("That workout day does not exist.")
            return
        if not name.strip():
            print("Exercise name cannot be empty.")
            return
        self.workout[index]["exercises"].append({"name": name.strip(), "sets": []})
        self.save()
        print(f"Added {name.strip()} to day {day_number}.")

    def delete_exercise(self, day_number, exercise_number):
        index = self._day_index(day_number, len(self.workout))
        if index is None:
            print("That workout day does not exist.")
            return
        exercises = self.workout[index]["exercises"]
        exercise_index = self._day_index(exercise_number, len(exercises))
        if exercise_index is None:
            print("That exercise does not exist on this day.")
            return
        name = exercises[exercise_index]["name"]
        del exercises[exercise_index]
        self.save()
        print(f"Deleted {name} from day {day_number}.")

    def add_set(self, day_number, exercise_number, weight, reps):
        index = self._day_index(day_number, len(self.workout))
        if index is None:
            print("That workout day does not exist.")
            return
        exercises = self.workout[index]["exercises"]
        exercise_index = self._day_index(exercise_number, len(exercises))
        if exercise_index is None:
            print("That exercise does not exist on this day.")
            return
        try:
            parsed_weight = float(weight)
            parsed_reps = int(reps)
            if parsed_weight < 0 or parsed_reps < 0:
                raise ValueError
        except ValueError:
            print("Weight must be a non-negative number and reps a non-negative whole number.")
            return
        exercises[exercise_index]["sets"].append({"weight": parsed_weight, "reps": parsed_reps})
        self.save()
        print("Added set.")

    def delete_set(self, day_number, exercise_number, set_number):
        index = self._day_index(day_number, len(self.workout))
        if index is None:
            print("That workout day does not exist.")
            return
        exercises = self.workout[index]["exercises"]
        exercise_index = self._day_index(exercise_number, len(exercises))
        if exercise_index is None:
            print("That exercise does not exist on this day.")
            return
        sets = exercises[exercise_index]["sets"]
        set_index = self._day_index(set_number, len(sets))
        if set_index is None:
            print("That set does not exist.")
            return
        del sets[set_index]
        self.save()
        print("Deleted set.")

    def display_category(self, category):
        matches = [i for i, day in enumerate(self.workout, 1)
                   if day.get("category", "").casefold() == category.casefold()]
        if not matches:
            print(f"No workout days found in category '{category}'.")
            return
        for day_number in matches:
            self.display_day(str(day_number))

    @staticmethod
    def show_help():
        Utilities.clear_terminal()
        print("""Workout commands:
days                         show the number and list of workout days
view day <day>               view a specific day, its exercises, and sets
view category <name>         view all days in a category
add day [category]           add a day; category is optional
delete day <day>             delete a day and its contents
add exercise <day> <name>   add an exercise to a day
delete exercise <day> <exercise>  delete an exercise by its number on that day
add set <day> <exercise>     then enter weight and reps when prompted
delete set <day> <exercise> <set>  delete a set
/help, /exit, /quit          help, return to apps, or quit the program
Day, exercise, and set numbers are one-based, as shown by the display.""")

    def run(self):
        Utilities.clear_terminal()
        while True:
            print("Use /help for commands.")
            command = input("Workouts: What do you want to do? ").strip()
            lower = command.lower()
            if lower == "/exit":
                Utilities.clear_terminal()
                return
            if lower == "/quit":
                sys.exit()
            if lower in ("/help", "help"):
                self.show_help()
            elif lower == "/apps":
                print(
                    "Apps:\n"
                    "tasks: task tracker\n"
                    "goals: goal tracker\n"
                    "habits: habit tracker\n"
                    "workouts: workout tracker"
                )
            elif lower in ("days", "view days", "count days"):
                Utilities.clear_terminal()
                print(f"You have {len(self.workout)} workout day(s).")
                self.display_days()
            elif lower.startswith("view day "):
                self.display_day(command[9:].strip())
            elif lower.startswith("view category "):
                category = command[len("view category "):].strip()
                if category:
                    self.display_category(category)
                else:
                    print("Enter a category name.")
            elif lower == "add day" or lower.startswith("add day "):
                self.add_day(command[7:].strip())
            elif lower.startswith("delete day "):
                self.delete_day(command[len("delete day "):].strip())
            elif lower.startswith("add exercise "):
                parts = command.split(maxsplit=3)
                if len(parts) == 4:
                    self.add_exercise(parts[2], parts[3])
                else:
                    print("Usage: add exercise <day> <exercise name>")
            elif lower.startswith("delete exercise "):
                parts = command.split()
                if len(parts) == 4:
                    self.delete_exercise(parts[2], parts[3])
                else:
                    print("Usage: delete exercise <day> <exercise number>")
            elif lower.startswith("add set "):
                parts = command.split()
                if len(parts) == 4:
                    weight = input("Weight: ").strip()
                    reps = input("Reps: ").strip()
                    self.add_set(parts[2], parts[3], weight, reps)
                else:
                    print("Usage: add set <day> <exercise number>")
            elif lower.startswith("delete set "):
                parts = command.split()
                if len(parts) == 5:
                    self.delete_set(parts[2], parts[3], parts[4])
                else:
                    print("Usage: delete set <day> <exercise number> <set number>")
            else:
                print("Unknown workout command. Use /help to see commands.")

class CLI:
    APPS = {
        "task": "task tracker",
        "tasks": "task tracker",
        "goal": "goal tracker",
        "goals": "goal tracker",
        "habit": "habit tracker",
        "habits": "habit tracker",
        "workout": "workout tracker",
        "workouts": "workout tracker"
    }

    def __init__(self):
        self.task_manager = TaskManager()
        self.workout_manager = WorkoutManager()
        self.goal_manager = GoalManager()
        self.habit_manager = HabitManager()

    def show_apps(self):
        print(
            "Apps:\n"
            "tasks: task tracker\n"
            "goals: goal tracker\n"
            "habits: habit tracker\n"
            "workouts: workout tracker"
        )

    def handle_command(self, command: str):
        Utilities.clear_terminal()

        if command == "/quit":
            sys.exit()

        elif command == "/exit":
            return "exit"

        elif command == "/help":
            print(
                """Commands:
/quit: quits the whole program
/exit: exits application
/apps: shows available apps"""
            )

        elif command == "/apps":
            return "apps"

        else:
            print("Command doesn't exist.")

    def open_app(self, app: str):
        app = app.strip().casefold()

        if app in ("task", "tasks"):
            self.task_manager.run()
        elif app in ("goal", "goals"):
            self.goal_manager.run()
        elif app in ("habit", "habits"):
            self.habit_manager.run()
        elif app in ("workout", "workouts"):
            self.workout_manager.run()

        else:
            print("App doesn't exist. Try /apps.")

    def run(self):
        Utilities.clear_terminal()

        print("Welcome to CLImprovement!")
        
        while True:
            try:
                user_input = input("What do you want to open ('/help' for commands)? ")
                if user_input.startswith("/"):
                    result = self.handle_command(user_input)
                    if result == "exit":
                        break
                    elif result == "apps":
                        self.show_apps()
                else:
                    self.open_app(user_input)
            except KeyboardInterrupt:
                print("\nYou have to use /quit because I say so.")

def main():
    app = CLI()
    app.run()

if __name__ == "__main__":
    main()
