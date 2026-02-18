
import sys
import json

TASKS_FILE = 'tasks.json'

def load_tasks():
    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def list_tasks():
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        status = "[x]" if task['done'] else "[ ]"
        print(f"{i + 1}. {status} {task['title']}")

def add_task(title):
    tasks = load_tasks()
    tasks.append({"title": title, "done": False})
    save_tasks(tasks)
    print(f"Added task: {title}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: todo.py [add|list] [args]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "list":
        list_tasks()
    elif cmd == "add":
        add_task(sys.argv[2])

    elif cmd == "complete":
        tasks = load_tasks()
        idx = int(sys.argv[2]) - 1
        tasks[idx]['done'] = True
        save_tasks(tasks)
        print("Marked as done.")
