import os
import shutil
import tiktoken
import subprocess
import json
import sys

# Configuration
BASE_DIR = "experiments/work"
SCANNER_SCRIPT = "src/scanner.py"
MODEL_ENCODING = "cl100k_base"  # GPT-4 / GPT-3.5 encoding

def count_tokens(text):
    """Returns token count using tiktoken."""
    encoding = tiktoken.get_encoding(MODEL_ENCODING)
    return len(encoding.encode(text))

def run_scanner(query, directory):
    """Runs the scanner.py script and returns the retrieved context."""
    # Index first
    subprocess.run([sys.executable, SCANNER_SCRIPT, "index", directory], check=True, capture_output=True)
    
    # Search
    result = subprocess.run(
        [sys.executable, SCANNER_SCRIPT, "search", query, "--n", "3"], 
        check=True, capture_output=True, text=True
    )
    return result.stdout

def get_full_context(directory):
    """Reads all files in directory (naive approach)."""
    context = ""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith("."): continue
            if "__pycache__" in root: continue
            
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                context += f"\n--- {path} ---\n"
                context += f.read()
    return context

def setup_stage(stage_name, files):
    """Sets up the directory for a stage."""
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
    os.makedirs(BASE_DIR)
    
    for filename, content in files.items():
        with open(os.path.join(BASE_DIR, filename), 'w') as f:
            f.write(content)
            
    print(f"\n--- Setting up Stage: {stage_name} ---")

def run_experiment():
    print("🚀 Starting Builder's Journey Simulation...\n")
    
    results = []

    # --- Stage 1: The Initial Feature (Add 'complete' command) ---
    # Context: Basic Todo App
    todo_v1 = """
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
"""
    setup_stage("1. Feature Add", {"todo.py": todo_v1, "README.md": "# Simple Todo App\nUsage: python todo.py add 'Buy Milk'"})
    
    task_query = "implement complete command to mark task as done"
    
    # Measure
    full_ctx = get_full_context(BASE_DIR)
    scanned_ctx = run_scanner(task_query, BASE_DIR)
    
    results.append({
        "stage": "Feature Add",
        "full_tokens": count_tokens(full_ctx),
        "scanned_tokens": count_tokens(scanned_ctx),
        "relevant_found": "complete" in scanned_ctx or "todo.py" in scanned_ctx # Rough check
    })

    # --- Stage 2: The Bug Fix (Crash on Empty JSON) ---
    # Context: Todo App v2 (bigger) + Corrupt Data
    todo_v2 = todo_v1 + """
    elif cmd == "complete":
        tasks = load_tasks()
        idx = int(sys.argv[2]) - 1
        tasks[idx]['done'] = True
        save_tasks(tasks)
        print("Marked as done.")
"""
    # Add some "bloat" files that shouldn't be read
    bloat_file = "# Just a long changelog\n" + ("* Fixed stuff\n" * 100)
    
    setup_stage("2. Bug Fix", {
        "todo.py": todo_v2, 
        "tasks.json": "", # Empty file causes crash!
        "CHANGELOG.md": bloat_file,
        "README.md": "# Simple Todo App v2\nNow with complete command!"
    })
    
    task_query = "fix crash when tasks.json is empty in load_tasks"
    
    full_ctx = get_full_context(BASE_DIR)
    scanned_ctx = run_scanner(task_query, BASE_DIR)
    
    results.append({
        "stage": "Bug Fix",
        "full_tokens": count_tokens(full_ctx),
        "scanned_tokens": count_tokens(scanned_ctx),
        "relevant_found": "load_tasks" in scanned_ctx
    })

    # --- Output Results ---
    print("\n📊 Simulation Results:\n")
    print(f"{'Stage':<15} | {'Full Tokens':<12} | {'Scanned Tokens':<15} | {'Reduction':<10}")
    print("-" * 60)
    
    for r in results:
        reduction = (1 - (r['scanned_tokens'] / r['full_tokens'])) * 100
        print(f"{r['stage']:<15} | {r['full_tokens']:<12} | {r['scanned_tokens']:<15} | {reduction:.1f}%")

if __name__ == "__main__":
    run_experiment()
