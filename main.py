import json
import os
import sys

#hi

class FileManager:
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

class Utilities:
    @staticmethod
    def clear_terminal():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def date_converter(date: str):
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

        if date == "":
            return ""

        date = date.replace("/", " ")
        date = date.replace(".", " ")
        date = date.replace("-", " ")
        date = date.replace(",", "")

        month, day, year = date.split(" ")

        try:
            month = month_list.index(month) + 1
        except ValueError:
            pass

        return f"{year}-{month:02}-{day:02}"

class TaskManager:
    FILE_NAME = "tasks.json"

    def __init__(self):
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

    def clear_task(self, name: str):
        self.tasks = [task for task in self.tasks if task["name"].lower() != name]

        self.save()

    def toggle_complete(self, name: str):
        for task in self.tasks:
            if task["name"].lower() == name:
                if task["complete"] == "x":
                    task["complete"] = ""
                else:
                    task["complete"] = "x"

        self.save()

    def run(self):
        """Runs the task application."""

        Utilities.clear_terminal()
        print("Entered Tasks...")

        while True:
            self.display_tasks()

            task_input = input("Tasks: What do you want to do? ")

            if task_input.startswith("/"):
                if task_input == "/exit":
                    break

                elif task_input == "/quit":
                    sys.exit()

                elif task_input == "/help":
                    print(
                        """
Task commands:
/exit: exits tasks
/quit: quits the whole program
/apps: shows available apps

Task functions:
add (task)
delete all tasks
clear (task)
complete (task)
"""
                    )

                elif task_input == "/apps":
                    print("Apps:\ntasks: task tracker")

                else:
                    print("Command doesn't exist.")

                continue

            if task_input.startswith("add "):
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

                self.clear_task(task_name)

                Utilities.clear_terminal()

            elif task_input.startswith("complete "):
                task_name = task_input[9:]

                self.toggle_complete(task_name)

                Utilities.clear_terminal()

            else:
                Utilities.clear_terminal()
                print("That does not exist.")

class WorkoutManager:
    FILE_NAME = "workout.json"
    
    def __init__(self):
        self.workout = FileManager.read_json(self.FILE_NAME)

    def save(self):
        FileManager.write_json(self.FILE_NAME, self.workout)

    def display_tasks(self):
        print("Workouts:")
        if not self.workout:
            print("You have no workouts.")
            return
        for x in self.workout:
            print(x['name'])

    def run(self):
        Utilities.clear_terminal()
        self.display_tasks()
        workout_input = input("What do you want to do? ")
        Utilities.clear_terminal()
        print(workout_input + " program works")
        sys.exit()

class CLI:
    def __init__(self):
        self.task_manager = TaskManager()
        self.workout_manager = WorkoutManager()

    def show_apps(self):
        print("Apps:\ntasks: task tracker")

    def handle_command(self, command: str):
        Utilities.clear_terminal()

        if command == "/quit":
            sys.exit()

        elif command == "/exit":
            return "exit"

        elif command == "/help":
            print(
                """
Commands:
/quit: quits the whole program
/exit: exits application
/apps: shows available apps
"""
            )

        elif command == "/apps":
            return "apps"

        else:
            print("Command doesn't exist.")

    def open_app(self, app: str):
        app = app.lower()

        if app in ("task", "tasks"):
            self.task_manager.run()
        elif app in ("workout", "workouts"):
            self.workout_manager.run()

        else:
            print("App doesn't exist.")

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