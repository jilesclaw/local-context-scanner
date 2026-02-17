# The Builder's Journey: A Phase 2 Experiment

This document details the second phase of testing for the Local Context Scanner, focusing on the cumulative benefits of local retrieval over a full development lifecycle.

## Objective
To demonstrate that the efficiency gains of local context scanning **compound** as a project grows in complexity.

## Methodology
We simulate a real-world coding session where an AI agent builds a Python CLI To-Do application from scratch. We compare two strategies:

1.  **Agent A (The Bloat):** The control group. Always reads and sends the *entire* project context (all files) at every step.
2.  **Agent B (The Surgeon):** The experimental group. Uses `scanner.py` to retrieve only relevant code snippets based on the current task.

---

## The Lifecycle Steps

### Step 1: Green Field Development
**Task:** "Initialize a Python project. Create a file named `todo.py` that allows adding tasks and listing them via CLI arguments."

*   **Context State:** Empty folder.
*   **Agent A (Bloat):** Reads empty directory. Sends ~50 tokens.
*   **Agent B (Surgeon):** Scans empty directory. Sends ~50 tokens.
*   **Hypothesis:** **Tie.** No existing code to filter.

### Step 2: The Feature Addition
**Task:** "Add a `complete` command to mark tasks as done. Ensure tasks persist to a `storage.json` file."

*   **Context State:** Contains `todo.py` (Version 1).
*   **Agent A (Bloat):** Reads `todo.py` (entire file). Sends ~1,500 tokens.
*   **Agent B (Surgeon):** Scans. Queries "persist tasks json". Retrieves relevant chunks of `todo.py` (imports, file I/O). Sends ~500 tokens.
*   **Hypothesis:** **3x Efficiency Gain.** Agent B ignores unchanged logic (like `list_tasks` CLI parsing).

### Step 3: The Bug Fix
**Task:** "The app crashes if `storage.json` is empty or corrupt. Fix the load function to handle this gracefully."

*   **Context State:** Contains `todo.py` (Version 2), `storage.json` (data), `README.md`.
*   **Agent A (Bloat):** Reads everything. `todo.py` + `storage.json` + `README.md`. Sends ~4,000 tokens.
*   **Agent B (Surgeon):** Scans. Queries "fix crash empty json load". Retrieves *only* the `load_tasks` function. Sends ~300 tokens.
*   **Hypothesis:** **13x Efficiency Gain.** Agent B completely ignores the `add`, `list`, and `complete` logic, focusing solely on the bug.

---

## Projected Results Table

| Step | Task | Agent A (Tokens) | Agent B (Tokens) | Reduction |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Init Project | ~50 | ~50 | 0% |
| 2 | Add Persistence | ~1,500 | ~500 | **66%** |
| 3 | Fix Bug | ~4,000 | ~300 | **92%** |
| **Total** | **Cumulative** | **~5,550** | **~850** | **~85%** |

## Conclusion
The **Local Context Scanner** becomes exponentially more valuable as the codebase grows. While the initial setup cost is the same, maintenance and feature additions become drastically cheaper and faster, allowing developers to work on large projects indefinitely without hitting context window limits.
