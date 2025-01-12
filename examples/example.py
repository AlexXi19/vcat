import sys
import os
import json

TASKS_FILE = "tasks.json"

def load_tasks():
    """Load tasks from a JSON file, return a list of tasks."""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as file:
        try:
            tasks = json.load(file)
        except json.JSONDecodeError:
            tasks = []
    return tasks

def save_tasks(tasks):
    """Save the current list of tasks to a JSON file."""
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)

def list_tasks():
    """Print out all tasks in a formatted list."""
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    print("\nYour To-Do List:")
    for i, task in enumerate(tasks, start=1):
        status = "✓" if task["completed"] else " "
        print(f"{i}. [{status}] {task['description']}")
    print()

def add_task(description):
    """Add a new task with the given description."""
    tasks = load_tasks()
    tasks.append({"description": description, "completed": False})
    save_tasks(tasks)
    print(f"Added task: {description}")

def complete_task(task_id):
    """Mark a task as completed by task ID (1-based)."""
    tasks = load_tasks()
    idx = task_id - 1  # Convert to 0-based index
    if idx < 0 or idx >= len(tasks):
        print(f"Task #{task_id} does not exist.")
        return
    tasks[idx]["completed"] = True
    save_tasks(tasks)
    print(f"Marked task #{task_id} as complete.")

def delete_task(task_id):
    """Delete a task by task ID (1-based)."""
    tasks = load_tasks()
    idx = task_id - 1  # Convert to 0-based index
    if idx < 0 or idx >= len(tasks):
        print(f"Task #{task_id} does not exist.")
        return
    deleted_task = tasks.pop(idx)
    save_tasks(tasks)
    print(f"Deleted task #{task_id}: {deleted_task['description']}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python todo.py add \"task description\"")
        print("  python todo.py list")
        print("  python todo.py complete <task_id>")
        print("  python todo.py delete <task_id>")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "add":
        if len(sys.argv) < 3:
            print("Please provide a task description.")
        else:
            task_description = " ".join(sys.argv[2:])
            add_task(task_description)

    elif command == "list":
        list_tasks()

    elif command == "complete":
        if len(sys.argv) < 3:
            print("Please provide the task ID to mark complete.")
        else:
            try:
                task_id = int(sys.argv[2])
                complete_task(task_id)
            except ValueError:
                print("Invalid task ID. Please provide a number.")

    elif command == "delete":
        if len(sys.argv) < 3:
            print("Please provide the task ID to delete.")
        else:
            try:
                task_id = int(sys.argv[2])
                delete_task(task_id)
            except ValueError:
                print("Invalid task ID. Please provide a number.")
    else:
        print(f"Unknown command: {command}")
        print("Available commands: add, list, complete, delete")

if __name__ == "__main__":
    main()

