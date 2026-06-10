"""Milestones 4 & 6 — Evaluation harness.

Runs the five planning.md test questions through the full pipeline and prints,
for each: the question, the retrieved chunks with cosine distances (Milestone 4
checkpoint evidence), and the grounded answer with sources (Milestone 6 report
evidence). Also runs one out-of-scope question to confirm the refusal path.

Prerequisites (run locally, where huggingface.co is reachable and GROQ_API_KEY
is set in .env):
    python embed.py        # builds the ChromaDB collection once
    python evaluate.py     # prints retrieval + generation results

Use --retrieval-only to print just the retrieval results (no LLM / API key
needed) — useful for verifying the Milestone 4 checkpoint on its own.
"""

import argparse

from retrieve import retrieve

# Test questions and expected answers from planning.md (Evaluation Plan).
EVAL = [
    ("Is ECON 101 considered a heavy workload course?",
     "No — reviews call it an easy/bird course."),
    ("Do students find MATH 137 harder than MATH 135?",
     "Cross-document: MATH 135 is often harder (proofs are new); 137 reads as "
     "a continuation of high-school calculus."),
    ("How do students generally feel about taking PD 1?",
     "Widely disliked — described as useless busy work."),
    ("What is the main difficulty associated with CS 246?",
     "The long, heavy assignments (C++ design / memory management)."),
    ("Does CHEM 120 involve a lot of new concepts compared to high school chemistry?",
     "No — reviews say it largely repeats grade-12 chemistry."),
]

# Should retrieve nothing useful and trigger the refusal path.
OUT_OF_SCOPE = "Which professor teaches PHYS 234 and what are their office hours?"


def show_retrieval(question):
    hits = retrieve(question)
    for i, h in enumerate(hits, 1):
        snippet = h["text"][:200].replace("\n", " ")
        print(f"   #{i} dist={h['distance']:<5} {h['source']}")
        print(f"       {snippet}...")
    best = hits[0]["distance"]
    flag = "OK (<0.5)" if best < 0.5 else "WEAK (>=0.5)"
    print(f"   -> best distance {best} [{flag}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--retrieval-only", action="store_true",
                    help="skip LLM generation (no GROQ_API_KEY needed)")
    args = ap.parse_args()

    if not args.retrieval_only:
        from query import ask  # imported lazily so retrieval-only needs no key

    for n, (question, expected) in enumerate(EVAL, 1):
        print(f"\n{'=' * 72}\nQ{n}: {question}\nExpected: {expected}\n{'-' * 72}")
        print("Retrieved chunks:")
        show_retrieval(question)
        if not args.retrieval_only:
            result = ask(question)
            print(f"\nSystem answer:\n   {result['answer']}")
            print(f"Sources: {', '.join(result['sources']) or '(none)'}")

    print(f"\n{'=' * 72}\nOUT-OF-SCOPE: {OUT_OF_SCOPE}\n{'-' * 72}")
    show_retrieval(OUT_OF_SCOPE)
    if not args.retrieval_only:
        result = ask(OUT_OF_SCOPE)
        print(f"\nSystem answer:\n   {result['answer']}")
        print(f"Sources: {', '.join(result['sources']) or '(none — refused, as expected)'}")


if __name__ == "__main__":
    main()
