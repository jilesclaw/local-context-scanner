# Experiment Design: Local Context vs. Full Context

## Objective
To quantify the benefits of pre-filtering context using a local retriever (Local Context Scanner) versus the standard practice of dumping large file contexts into an LLM.

## Hypothesis
Using a local retriever to select only relevant code snippets will:
1.  **Reduce Token Usage** by >70%.
2.  **Improve Accuracy** by reducing "distractor" context.
3.  **Lower Latency** due to smaller payloads.

## The Setup

We will create a **Synthetic Codebase** (The "Haystack") containing ~20 files of boilerplate, documentation, and logic. Hidden within this haystack are 3 specific files (The "Needles") required to solve the task.

### The Task
**"Add a rate limiter to the `process_payment` function found in the payment service, using the configuration from `config.json`."**

To solve this, the agent must:
1.  Find `payment_service.py` (Logic).
2.  Find `config.json` (Settings).
3.  Find `utils/rate_limit.py` (Helper function).
4.  Ignore the 17 other irrelevant files (Auth, Logging, UI, Tests, etc.).

## Methodology

We will run two parallel agents:

### Agent A: "The Bloat" (Control Group)
*   **Strategy:** Reads all files in the directory.
*   **Context:** Concatenates everything into the prompt.
*   **Prompt:** "Here is the entire codebase. Add a rate limiter to the payment logic..."

### Agent B: "The Surgeon" (Experimental Group)
*   **Strategy:** Uses `Local Context Scanner` tool.
*   **Step 1:** Queries local index: "Find payment logic", "Find rate limiter utility", "Find configuration".
*   **Context:** Only sends the ~3 retrieved chunks/files.
*   **Prompt:** "Here are the relevant files. Add a rate limiter..."

## Metrics to Capture

| Metric | Agent A (Full Context) | Agent B (Local Scan) | Delta (%) |
| :--- | :--- | :--- | :--- |
| **Input Tokens** | (Measured) | (Measured) | |
| **Output Tokens** | (Measured) | (Measured) | |
| **Time to First Token** | (Measured) | (Measured) | |
| **Success?** | (Pass/Fail) | (Pass/Fail) | |
| **Hallucinations** | (Count) | (Count) | |

## Reproducibility
1.  **Dataset:** A committed folder `fixtures/dummy-project`.
2.  **Prompts:** Fixed system prompts for both agents.
3.  **Model:** Same model (e.g., GPT-4o or Claude 3.5 Sonnet) and temperature (0.0) for both to ensure fair comparison.

## Output
A Markdown report `RESULTS.md` summarizing the findings, suitable for publication/blogging.
