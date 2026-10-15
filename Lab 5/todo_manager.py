"""Simple to-do manager used for the Lab 5 static code analysis exercise."""
import json
import random
import re
import shutil
import subprocess  # nosec B404
from datetime import datetime

tasks = {}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def add_task(title, priority="medium", labels=None):
    """Create a task and return its id."""
    task_id = len(tasks) + 1
    labels = list(labels) if labels else []
    labels.append(priority)
    tasks[task_id] = {"title": title, "priority": priority, "done": False,
                      "labels": labels,
                      "created": datetime.now().isoformat()}
    return task_id


def complete_task(task_id):
    """Mark a task as done. Return False if the id does not exist."""
    if task_id in tasks:
        tasks[task_id]["done"] = True
        return True
    print("No task with id", task_id)
    return False


def pending_tasks():
    """Return titles of unfinished tasks, highest priority first."""
    pending = [task for task in tasks.values() if not task["done"]]
    pending.sort(key=lambda task: PRIORITY_ORDER[task["priority"]])
    return [task["title"] for task in pending]


def find_task(keyword):
    """Return the id of the first task whose title contains keyword."""
    for task_id, task in tasks.items():
        if keyword.lower() in task["title"].lower():
            return task_id
    return None


def save_tasks(file_name="tasks_store.json"):
    """Persist the tasks to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)


def load_tasks(file_name="tasks_store.json"):
    """Load tasks from a JSON file (JSON turns int keys into strings)."""
    with open(file_name, "r", encoding="utf-8") as file:
        return {int(key): value for key, value in json.load(file).items()}


def export_json(file_name="tasks.json"):
    """Export the tasks to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)


def remind_by_email(address):
    """Mail the exported task file to address (not called by the demo)."""
    # No shell is used and the address is validated, so B603 is a false alarm
    if not EMAIL_PATTERN.fullmatch(address):
        raise ValueError("Invalid e-mail address")
    mail = shutil.which("mail")
    if mail is None:
        raise FileNotFoundError("'mail' command not found")
    with open("tasks.json", "rb") as file:
        subprocess.run([mail, "-s", "Pending tasks", address],
                       stdin=file, check=True)  # nosec B603


def main():
    """Run the demo."""
    add_task("Submit lab report", "high")
    add_task("Buy groceries")
    add_task("Call plumber", "low")
    add_task("Book train tickets", "high")
    complete_task(2)
    complete_task(99)
    print("Pending tasks:", pending_tasks())
    print("Task id for 'plumber':", find_task("plumber"))
    print("Task id for 'gym':", find_task("gym"))  # returns None
    pending = pending_tasks()
    if pending:
        # Not security related, only a friendly suggestion (nosec is safe)
        suggestion = random.choice(pending)  # nosec B311
        print("Try this next:", suggestion)
    save_tasks()
    restored = load_tasks()
    print("Tasks restored from file:", len(restored))
    export_json()
    print("Exported tasks to tasks.json")


if __name__ == "__main__":
    main()
