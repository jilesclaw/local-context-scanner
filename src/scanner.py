import click
import os
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import fnmatch
import requests
import json

# --- Configuration ---
DEFAULT_MODEL = "all-MiniLM-L6-v2"
DB_PATH = "./.context_db"
CHUNK_SIZE = 500  # Characters per chunk (approx)
OVERLAP = 50      # Overlap between chunks

# --- Helper: Should we ignore this file? ---
IGNORE_PATTERNS = [
    ".git*", "__pycache__", "node_modules", ".DS_Store", "*.pyc", 
    "package-lock.json", "yarn.lock", "*.lock", ".context_db", ".venv"
]

def should_ignore(path):
    filename = os.path.basename(path)
    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False

# --- Helper: Chunk Text ---
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

# --- Helper: Generate File Tree ---
def generate_tree(startpath):
    tree_str = f"📂 Project Structure ({startpath}):\n"
    for root, dirs, files in os.walk(startpath):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if not should_ignore(d)]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        if level > 0:
            tree_str += f"{indent}{os.path.basename(root)}/\n"
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not should_ignore(f):
                tree_str += f"{subindent}{f}\n"
    return tree_str

# --- Helper: Call Remote LLM ---
def query_llm(url, model, prompt, context):
    """Sends prompt + context to a remote Ollama instance."""
    full_prompt = f"""
You are a helpful coding assistant. Use the following context to answer the user's question.
If the answer is not in the context, say so.

### Context:
{context}

### Question:
{prompt}
"""
    try:
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }
        response = requests.post(f"{url}/api/generate", json=payload)
        response.raise_for_status()
        return response.json().get('response', 'Error: No response from model.')
    except Exception as e:
        return f"⚠️ LLM Error: {e}"

@click.group()
def cli():
    """Local Context Scanner: Index, Retrieve, and Ask."""
    pass

@cli.command()
@click.argument('directory', type=click.Path(exists=True), default=".")
def index(directory):
    """Scan a directory and build the vector index."""
    click.echo(f"🔍 Scanning directory: {directory}")
    
    # 1. Initialize DB and Model
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="code_context")
    model = SentenceTransformer(DEFAULT_MODEL)

    # 2. Walk and Chunk
    documents = []
    metadatas = []
    ids = []
    
    file_count = 0
    chunk_count = 0

    for root, dirs, files in os.walk(directory):
        # Filter ignored directories in-place
        dirs[:] = [d for d in dirs if not should_ignore(d)]
        
        for file in files:
            if should_ignore(file):
                continue
                
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create chunks
                file_chunks = chunk_text(content)
                
                for i, chunk in enumerate(file_chunks):
                    documents.append(chunk)
                    metadatas.append({"path": filepath, "chunk_index": i})
                    ids.append(f"{filepath}#{i}")
                    chunk_count += 1
                
                file_count += 1
                
            except Exception as e:
                pass

    if not documents:
        click.echo("⚠️ No valid files found to index.")
        return

    click.echo(f"📊 Found {file_count} files, generated {chunk_count} chunks.")
    click.echo("🧠 Generating embeddings (this may take a moment)...")

    # 3. Embed and Upsert (Batch processing for speed)
    batch_size = 100
    for i in tqdm(range(0, len(documents), batch_size)):
        batch_docs = documents[i : i + batch_size]
        batch_meta = metadatas[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        
        # SentenceTransformer encodes automatically if passed to Chroma, 
        # but we do it explicitly here to show the logic or if we want to swap models later.
        embeddings = model.encode(batch_docs).tolist()
        
        collection.upsert(
            embeddings=embeddings,
            documents=batch_docs,
            metadatas=batch_meta,
            ids=batch_ids
        )

    click.echo("✅ Indexing complete!")

@cli.command()
@click.argument('query')
@click.option('--root', default=".", help='Root directory to generate tree from')
@click.option('--n', default=3, help='Number of results to return')
def search(query, root, n):
    """Search the index and print context."""
    
    # 1. Print File Tree (Hybrid Context)
    click.echo("--- Project Map ---")
    click.echo(generate_tree(root))
    click.echo("-------------------\n")

    # 2. Retrieve Specific Chunks
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        collection = client.get_collection(name="code_context")
    except Exception:
        click.echo("⚠️ No index found! Run 'scanner index' first.")
        return

    model = SentenceTransformer(DEFAULT_MODEL)
    query_embedding = model.encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n
    )

    click.echo(f"🔎 Top {n} Results for: '{query}'\n")
    
    for i in range(n):
        if i < len(results['documents'][0]):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            
            click.echo(f"--- Result {i+1} (Path: {meta['path']}) ---")
            click.echo(doc.strip())
            click.echo("\n")

@cli.command()
@click.argument('query')
@click.option('--root', default=".", help='Root directory for context')
@click.option('--url', default="http://localhost:11434", help='Ollama API URL')
@click.option('--model', default="mistral", help='Ollama model name')
@click.option('--max-tokens', default=4096, help='Maximum context tokens to send')
def ask(query, root, url, model, max_tokens):
    """Retrieve context and ask a remote LLM."""
    
    # 1. Build Base Context (System Prompt + Tree)
    # Estimate tokens: 1 token ~= 4 chars
    tree = generate_tree(root)
    base_prompt = f"""
You are a helpful coding assistant. Use the following context to answer the user's question.
If the answer is not in the context, say so.

### Project Structure:
{tree}

### Question:
{query}

### Relevant Code:
"""
    current_tokens = len(base_prompt) / 4
    
    # Reserve 1000 tokens for the answer
    available_tokens = max_tokens - current_tokens - 1000
    
    if available_tokens < 0:
        click.echo("⚠️ Warning: Project structure is too large for context window!")
        available_tokens = 500 # Try anyway with minimal space

    # 2. Retrieve & Fill Context
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        collection = client.get_collection(name="code_context")
        embed_model = SentenceTransformer(DEFAULT_MODEL)
        query_embedding = embed_model.encode([query]).tolist()
        
        # Fetch more candidates than we likely need (e.g. 20)
        results = collection.query(query_embeddings=query_embedding, n_results=20)
        
        added_chunks = 0
        code_context = ""
        
        if results['documents']:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            
            for i, doc in enumerate(docs):
                meta = metas[i]
                chunk_text = f"\n--- File: {meta['path']} ---\n{doc}\n"
                chunk_tokens = len(chunk_text) / 4
                
                if available_tokens - chunk_tokens > 0:
                    code_context += chunk_text
                    available_tokens -= chunk_tokens
                    added_chunks += 1
                else:
                    break # Context full!

        click.echo(f"📝 Added {added_chunks} code chunks to context.")
        
    except Exception as e:
        click.echo(f"⚠️ Index unavailable or search failed: {e}")
        code_context = ""

    full_prompt = base_prompt + code_context

    click.echo(f"🤖 Asking {model} at {url}...")
    click.echo(f"📊 Total Prompt Tokens: ~{int(len(full_prompt)/4)}")
    
    # 3. Call LLM
    answer = query_llm(url, model, query, full_prompt)
    
    click.echo("\n--- Answer ---")
    click.echo(answer)

if __name__ == '__main__':
    cli()