"""Milestone 4 — Embed chunks and load them into the vector store.

Per planning.md (Retrieval Approach):
  - embedding model: all-MiniLM-L6-v2 via sentence-transformers (local, free)
  - vector store: ChromaDB, persisted to ./chroma_db
  - collection created with {"hnsw:space": "cosine"} so distance scores are
    interpretable (lower = closer; < 0.5 is a good match)

Run:  python embed.py
Reads chunks.json (produced by ingest.py) and rebuilds the collection
from scratch so re-runs stay consistent with the current chunks.
"""

import json

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "chunks.json"
DB_DIR = "chroma_db"
COLLECTION_NAME = "uwflow_reviews"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 256


def main():
    chunks = json.load(open(CHUNKS_FILE, encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=DB_DIR)

    # Rebuild from scratch so the collection always mirrors chunks.json.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        embeddings = model.encode(texts, show_progress_bar=False)
        collection.add(
            ids=[f"{c['metadata']['source']}#{c['metadata']['chunk_index']}" for c in batch],
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=[c["metadata"] for c in batch],
        )
        print(f"  embedded {min(start + BATCH_SIZE, len(chunks))}/{len(chunks)}")

    print(f"Done: collection '{COLLECTION_NAME}' has {collection.count()} chunks in ./{DB_DIR}")


if __name__ == "__main__":
    main()
