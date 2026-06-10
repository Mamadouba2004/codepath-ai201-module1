"""Milestone 4 — Semantic retrieval over the ChromaDB collection.

Provides retrieve(query, k) for the rest of the pipeline (query.py imports
it), and a CLI for ad-hoc single-query testing:

  python retrieve.py "Is ECON 101 considered a heavy workload course?"

(For the full evaluation set, run: python evaluate.py --retrieval-only)

Top-k default is 5 per planning.md. Distances are cosine (lower = closer);
results under ~0.5 are good matches, above ~0.6-0.7 are weak.
"""

import sys

import chromadb
from sentence_transformers import SentenceTransformer

from config import COLLECTION_NAME, DB_DIR, EMBEDDING_MODEL, TOP_K

_model = None
_collection = None


def _load():
    """Lazy-init the embedding model and collection exactly once.

    Globals are only assigned after BOTH succeed, so a failure here doesn't
    leave the module half-initialized for later calls.
    """
    global _model, _collection
    if _collection is None:
        model = SentenceTransformer(EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=DB_DIR)
        try:
            collection = client.get_collection(COLLECTION_NAME)
        except Exception as exc:
            raise RuntimeError(
                f"Vector store '{COLLECTION_NAME}' not found in ./{DB_DIR} — "
                "run `python embed.py` first to build it."
            ) from exc
        _model, _collection = model, collection
    return _model, _collection


def retrieve(query, k=TOP_K):
    """Return the top-k chunks for a query as a list of
    {text, source, course_code, course_title, distance} dicts, closest first."""
    model, collection = _load()
    embedding = model.encode([query])[0].tolist()
    result = collection.query(query_embeddings=[embedding], n_results=k)
    return [
        {
            "text": doc,
            "source": meta["source"],
            "course_code": meta["course_code"],
            "course_title": meta["course_title"],
            "distance": round(dist, 3),
        }
        for doc, meta, dist in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        )
    ]


def main():
    if len(sys.argv) < 2:
        print('usage: python retrieve.py "your question"')
        print("(for the full evaluation set: python evaluate.py --retrieval-only)")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    print(f"QUERY: {query}")
    for i, hit in enumerate(retrieve(query), 1):
        print(f"\n  #{i}  distance={hit['distance']}  source={hit['source']}")
        text = hit["text"] if len(hit["text"]) <= 300 else hit["text"][:300] + "..."
        print(f"  {text}")


if __name__ == "__main__":
    main()
