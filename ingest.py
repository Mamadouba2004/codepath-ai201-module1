"""Milestone 3 — Document ingestion and chunking pipeline.

Loads the UWFlow review documents from documents/, cleans them, and splits
them into chunks per the spec in planning.md:
  - target chunk size: 500 characters
  - overlap: 100 characters (applied when a single long review must be cut)
  - split on \n\n review boundaries; small reviews are grouped up to the
    target size, oversized reviews are split at sentence boundaries
  - every chunk gets the course name prepended to its text AND carries
    course code / source filename in its metadata

Run:  python ingest.py
Output: chunks.json (list of {text, metadata}) consumed by Milestone 4,
plus a printed sanity report (chunk count + 5 random sample chunks).
"""

import json
import random
import re
from pathlib import Path

DOCUMENTS_DIR = Path("documents")
OUTPUT_FILE = Path("chunks.json")
CHUNK_SIZE = 500
OVERLAP = 100

# Map typographic characters to plain ASCII equivalents.
UNICODE_FIXES = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", " ": " ",
}


def clean_text(text):
    for bad, good in UNICODE_FIXES.items():
        text = text.replace(bad, good)
    text = re.sub(r"[ \t]+", " ", text)          # collapse runs of spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)       # collapse extra blank lines
    return text.strip()


def load_documents(directory=DOCUMENTS_DIR):
    """Load each review .txt file and parse its 3-line header.

    Returns a list of dicts: {source, course_code, course_title, reviews}
    where reviews is the list of review blocks (label line + review text).
    """
    documents = []
    for path in sorted(directory.glob("*.txt")):
        raw = clean_text(path.read_text(encoding="utf-8"))
        header, _, body = raw.partition("\n\n")
        header_lines = header.split("\n")
        # Header line 1: "Student reviews of CS 135: Designing Functional Programs"
        m = re.match(r"Student reviews of ([A-Z]+ \w+): (.+)", header_lines[0])
        if not m:
            raise ValueError(
                f"{path.name}: first line {header_lines[0]!r} does not match the "
                "expected header 'Student reviews of <CODE NUM>: <Title>'"
            )
        reviews = [b.strip() for b in body.split("\n\n") if b.strip()]
        documents.append({
            "source": path.name,
            "course_code": m.group(1),
            "course_title": m.group(2),
            "reviews": reviews,
        })
    return documents


def split_long_review(text, size=CHUNK_SIZE, overlap=OVERLAP):
    """Split one oversized review at sentence boundaries, ~size chars per piece,
    carrying ~overlap chars of trailing context into the next piece."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    pieces, current = [], ""
    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > size:
            pieces.append(current)
            # start next piece with the tail of the previous one for continuity
            current = current[-overlap:].lstrip() + " " + sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces


def chunk_document(doc, size=CHUNK_SIZE):
    """Group whole reviews up to the target size; split reviews that exceed it.

    Reviews are independent opinions, so overlap is only applied inside a
    single long review — never across two different students' reviews.
    """
    prefix = f"[{doc['course_code']}: {doc['course_title']}] "
    units = []
    for review in doc["reviews"]:
        if len(review) > size:
            units.extend(split_long_review(review))
        else:
            units.append(review)

    chunks, current = [], ""
    for unit in units:
        if current and len(current) + len(unit) + 2 > size:
            chunks.append(current)
            current = unit
        else:
            current = f"{current}\n\n{unit}".strip()
    if current:
        chunks.append(current)

    return [
        {
            "text": prefix + chunk,
            "metadata": {
                "source": doc["source"],
                "course_code": doc["course_code"],
                "course_title": doc["course_title"],
                "chunk_index": i,
            },
        }
        for i, chunk in enumerate(chunks)
        if chunk.strip()
    ]


def main():
    documents = load_documents()
    print(f"Loaded {len(documents)} documents "
          f"({sum(len(d['reviews']) for d in documents)} reviews total)\n")

    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  {doc['source']:35s} {len(doc['reviews']):4d} reviews -> {len(chunks):3d} chunks")

    OUTPUT_FILE.write_text(json.dumps(all_chunks, indent=1), encoding="utf-8")
    print(f"\nTotal: {len(all_chunks)} chunks written to {OUTPUT_FILE}")

    lengths = [len(c["text"]) for c in all_chunks]
    print(f"Chunk length: min={min(lengths)} avg={sum(lengths)//len(lengths)} max={max(lengths)}")

    print("\n--- 5 random sample chunks ---")
    random.seed(42)
    for chunk in random.sample(all_chunks, 5):
        print(f"\n[{chunk['metadata']['source']} / chunk {chunk['metadata']['chunk_index']}]")
        print(chunk["text"])


if __name__ == "__main__":
    main()
