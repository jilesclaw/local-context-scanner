# Local Context Scanner

A lightweight, local-first tool designed to pre-process codebases and retrieve relevant context for LLMs.

## Problem
Feeding entire files or large directories to powerful (cloud-based) LLMs is expensive, slow, and noisy.

## Solution
This tool scans your local codebase, chunks files, and stores embeddings in a local vector database (`ChromaDB`). You can then:
1.  **Search:** Find the exact code snippets relevant to your query.
2.  **Ask:** Retrieve context and send it to a local/remote LLM (Ollama) for an answer.

## Installation

```bash
git clone https://github.com/jilesclaw/local-context-scanner.git
cd local-context-scanner
pip install -r requirements.txt
```

## Usage

### 1. Index a Directory
Scan your project to build the vector database.
```bash
python src/scanner.py index /path/to/your/project
```

### 2. Search for Code (Retrieve Only)
Find the top 3 relevant chunks and see the project structure.
```bash
python src/scanner.py search "how does authentication work?"
```

### 3. Ask an LLM (RAG)
Retrieve context and send it to a local/remote Ollama instance.
```bash
python src/scanner.py ask "how does authentication work?" \
  --url http://localhost:11434 \
  --model mistral \
  --max-tokens 4096
```

## Features
*   **Hybrid Search:** Combines semantic search (embeddings) with file tree structure.
*   **Smart Context Filling:** Automatically fills the LLM's context window with as many relevant chunks as possible (up to `--max-tokens`).
*   **Remote LLM Support:** Compatible with Ollama (local or remote server).
*   **Privacy First:** Your code never leaves your network.

## Architecture
*   **Database:** ChromaDB (Local vector store)
*   **Embeddings:** `all-MiniLM-L6-v2` (Fast, runs on CPU)
*   **LLM Client:** Python `requests` to Ollama API
