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


def addTask(title, priority="medium", labels=[]):
    taskId = len(tasks) + 1
    labels.append(priority)
    tasks[taskId] = {"title": title, "priority": priority, "done": False,
                     "created": datetime.now().isoformat()}
    return taskId


def completeTask(taskId):
    if taskId in tasks:
        tasks[taskId]["done"] = True
        return True
    print("No task with id", taskId)
    return False


def pendingTasks():
    pending = [task for task in tasks.values() if not task["done"]]
    pending.sort(key=lambda task: PRIORITY_ORDER[task["priority"]])
    return [task["title"] for task in pending]


def findTask(keyword):
    for taskId, task in tasks.items():
        if keyword.lower() in task["title"].lower():
            return taskId


def saveTasks(fileName="tasks_store.json"):
    with open(fileName, "w") as f:
        json.dump(tasks, f, indent=2)


def loadTasks(fileName="tasks_store.json"):
    with open(fileName, "r") as f:
        return {int(key): value for key, value in json.load(f).items()}


def exportJson(fileName="tasks.json"):
    with open(fileName, "w") as f:
        json.dump(tasks, f, indent=2)


def remindByEmail(address):
    # No shell is used and the address is validated, so B603 is a false alarm
    if not EMAIL_PATTERN.fullmatch(address):
        raise ValueError("Invalid e-mail address")
    mail = shutil.which("mail")
    if mail is None:
        raise FileNotFoundError("'mail' command not found")
    with open("tasks.json", "rb") as f:
        subprocess.run([mail, "-s", "Pending tasks", address],
                       stdin=f, check=True)  # nosec B603


def main():
    addTask("Submit lab report", "high")
    addTask("Buy groceries")
    addTask("Call plumber", "low")
    addTask("Book train tickets", "high")
    completeTask(2)
    completeTask(99)
    print("Pending tasks:", pendingTasks())
    print("Task id for 'plumber':", findTask("plumber"))
    print("Task id for 'gym':", findTask("gym"))  # returns None silently
    pending = pendingTasks()
    if pending:
        # Not security related, only a friendly suggestion (nosec is safe)
        suggestion = random.choice(pending)  # nosec B311
        print("Try this next:", suggestion)
    saveTasks()
    restored = loadTasks()
    print("Tasks restored from file:", len(restored))
    exportJson()
    print("Exported tasks to tasks.json")


main()
