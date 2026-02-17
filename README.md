# Local Context Scanner

## Concept
A lightweight, local-first tool designed to pre-process codebases and documents for LLM context optimization.

## Problem
Feeding entire files or large directories to powerful (cloud-based) LLMs is:
1.  **Expensive:** Token costs add up.
2.  **Slow:** Uploading and processing large contexts takes time.
3.  **Noisy:** Irrelevant code distracts the model, leading to hallucinations or missed instructions.
4.  **Privacy:** Sensitive code should stay local whenever possible.

## Solution
A small, local LLM or embedding model runs on consumer hardware (CPU/RAM friendly) to scan files and extract *only* the relevant snippets needed for a specific task.

### Key Features
*   **Local Execution:** Runs entirely on the user's machine.
*   **Low Resource Usage:** Target < 8GB RAM (compatible with quantized 3B-7B models or embedding models).
*   **Precision Retrieval:** Identifies relevant functions, classes, or documentation based on the user's prompt.
*   **Context Minification:** Sends only the necessary lines to the primary "smart" model (e.g., GPT-4, Claude 3, Gemini Pro).

## Architecture Ideas
*   **Embeddings:** Use `all-MiniLM-L6-v2` or similar lightweight embedding models for semantic search.
*   **Small LLM:** Use quantized (4-bit/5-bit) models like Llama-3-8B, Mistral-7B, or Qwen-2.5-1.5B for summarization and extraction.
*   **Tooling:** Python/Go wrapper to handle file I/O and model interfacing (via `ollama`, `llama.cpp`, or `onnx`).

## Goal
Drastically reduce token usage and improve answer quality by curating context *before* it leaves the local machine.
