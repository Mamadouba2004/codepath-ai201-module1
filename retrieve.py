"""Milestone 4 — Semantic retrieval over the ChromaDB collection.

Provides retrieve(query, k) for the rest of the pipeline (Milestone 5 imports
it), and a CLI for testing retrieval on its own:

  python retrieve.py "Is ECON 101 considered a heavy workload course?"
  python retrieve.py            # runs the planning.md test queries

Top-k default is 5 per planning.md. Distances are cosine (lower = closer);
results under ~0.5 are good matches, above ~0.6-0.7 are weak.
"""

import sys

import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = "chroma_db"
COLLECTION_NAME = "uwflow_reviews"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

_model = None
_collection = None


def _load():
    global _model, _collection
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=DB_DIR)
        _collection = client.get_collection(COLLECTION_NAME)
    return _model, _collection


def retrieve(query, k=TOP_K):
    """Return the top-k chunks for a query as a list of
    {text, source, course_code, distance} dicts, closest first."""
    model, collection = _load()
    embedding = model.encode([query])[0].tolist()
    result = collection.query(query_embeddings=[embedding], n_results=k)
    return [
        {
            "text": doc,
            "source": meta["source"],
            "course_code": meta["course_code"],
            "distance": round(dist, 3),
        }
        for doc, meta, dist in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        )
    ]


# Test queries from the planning.md Evaluation Plan.
TEST_QUERIES = [
    "Is ECON 101 considered a heavy workload course?",
    "Do students find MATH 137 harder than MATH 135?",
    "How do students generally feel about taking PD 1?",
    "What is the main difficulty associated with CS 246?",
    "Does CHEM 120 involve a lot of new concepts compared to high school chemistry?",
]


def main():
    queries = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else TEST_QUERIES
    for query in queries:
        print(f"\n{'=' * 70}\nQUERY: {query}")
        for i, hit in enumerate(retrieve(query), 1):
            print(f"\n  #{i}  distance={hit['distance']}  source={hit['source']}")
            text = hit["text"] if len(hit["text"]) <= 300 else hit["text"][:300] + "..."
            print(f"  {text}")


if __name__ == "__main__":
    main()
