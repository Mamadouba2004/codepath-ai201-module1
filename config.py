"""Shared configuration — the single source of truth for pipeline constants.

Imported by embed.py, retrieve.py, query.py, and evaluate.py so that a change
here (e.g., a new embedding model) cannot leave half the pipeline behind.
"""

CHUNKS_FILE = "chunks.json"
DB_DIR = "chroma_db"
COLLECTION_NAME = "uwflow_reviews"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5
LLM_MODEL = "llama-3.3-70b-versatile"
REFUSAL = "I don't have enough information on that."
