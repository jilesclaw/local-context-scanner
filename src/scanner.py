import click
import os
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import fnmatch

# --- Configuration ---
DEFAULT_MODEL = "all-MiniLM-L6-v2"
DB_PATH = "./.context_db"
CHUNK_SIZE = 500  # Characters per chunk (approx)
OVERLAP = 50      # Overlap between chunks

# --- Helper: Should we ignore this file? ---
IGNORE_PATTERNS = [
    ".git*", "__pycache__", "node_modules", ".DS_Store", "*.pyc", 
    "package-lock.json", "yarn.lock", "*.lock", ".context_db"
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

@click.group()
def cli():
    """Local Context Scanner: Index and Retrieve code context."""
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
                # click.echo(f"⚠️ Skipped {file}: {e}")
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
@click.option('--n', default=3, help='Number of results to return')
def search(query, n):
    """Search the index for relevant context."""
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name="code_context")
    model = SentenceTransformer(DEFAULT_MODEL)

    query_embedding = model.encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n
    )

    click.echo(f"\n🔎 Results for: '{query}'\n")
    
    for i in range(n):
        if i < len(results['documents'][0]):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            score = results['distances'][0][i]  # Lower is better in some metrics, usually cosine dist
            
            click.echo(f"--- Result {i+1} (Path: {meta['path']}) ---")
            click.echo(doc.strip())
            click.echo("\n")

if __name__ == '__main__':
    cli()
