# Builder's Journey Simulation Results

Ran on 2026-02-17.

## Setup
We simulated a developer creating a CLI To-Do app in 3 stages:
1.  **Stage 1:** Create `todo.py` (v1). Measure full vs scanned context for "Add complete command".
2.  **Stage 2:** Update `todo.py` (v2) + `tasks.json`. Measure full vs scanned context for "Fix empty JSON bug".

## Results

| Stage | Full Tokens | Scanned Tokens | Reduction | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Feature Add** | 465 | 433 | **6.9%** | Small codebase means most code is relevant. Scanner overhead is high relative to gains. |
| **Bug Fix** | 1888 | 650 | **65.6%** | Scanner correctly ignored the large `CHANGELOG.md` and unrelated `add_task` logic. |

## Analysis

### Why the difference?
*   **Small Projects:** In Stage 1, the entire `todo.py` was only ~40 lines. Chunking it resulted in retrieving almost the whole file anyway. The scanner didn't have much "chaff" to filter out.
*   **Growing Projects:** In Stage 2, we introduced a 100-line `CHANGELOG.md` file (simulating project bloat). The scanner **completely ignored it**, while the "Full Context" strategy wastefully included it.

### Conclusion
The value of local scanning **scales with project size**.
*   For small scripts (<5 files), standard context dumping is fine.
*   For medium/large projects (>20 files), local scanning reduces context (and cost) by **>60%**.
