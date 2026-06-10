"""Milestone 5 — Grounded answer generation.

Ties retrieval (Milestone 4) to the Groq LLM. The system prompt forces the
model to answer ONLY from the retrieved reviews, and source attribution is
attached programmatically from chunk metadata — never left to the LLM to
invent. Per planning.md the model is llama-3.3-70b-versatile.

  ask(question) -> {"answer": str, "sources": [filenames], "chunks": [...]}

CLI:
  python query.py "What is the main difficulty associated with CS 246?"
  python query.py          # interactive loop
"""

import os
import sys

from dotenv import load_dotenv
from groq import Groq

from config import LLM_MODEL, REFUSAL, TOP_K
from retrieve import retrieve

load_dotenv()

SYSTEM_PROMPT = (
    "You answer questions about University of Waterloo courses using ONLY the "
    "student reviews supplied in the user message. Follow these rules exactly:\n"
    "1. Use only facts stated in the provided reviews. Never add outside or "
    "general knowledge, even if you are confident.\n"
    f'2. If the reviews do not contain enough information to answer, reply with '
    f'exactly this sentence and nothing else: "{REFUSAL}"\n'
    "3. When reviews disagree, report the disagreement honestly instead of "
    "inventing a consensus or a middle ground.\n"
    "4. Be concise (2-5 sentences). Do not list sources yourself — they are "
    "attached separately by the system."
)

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set — copy .env.example to .env and add "
                "your free key from https://console.groq.com"
            )
        _client = Groq(api_key=api_key)
    return _client


def _is_refusal(answer):
    """True if the answer is the refusal sentence, tolerating quote-wrapping,
    trailing whitespace, or punctuation variants from the model."""
    return REFUSAL.rstrip(".").lower() in answer[:120].lower()


def _build_context(chunks):
    return "\n\n".join(
        f"[Review excerpt {i} from {c['source']}]\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    )


def ask(question, k=TOP_K):
    """Retrieve, generate a grounded answer, and attach sources programmatically."""
    chunks = retrieve(question, k=k)
    context = _build_context(chunks)

    response = _get_client().chat.completions.create(
        model=LLM_MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Student reviews:\n\n{context}\n\nQuestion: {question}"},
        ],
    )
    answer = response.choices[0].message.content.strip()

    # Source attribution is guaranteed by code, not the LLM. On a refusal we
    # attach no sources, since the retrieved chunks did not actually answer.
    if _is_refusal(answer):
        sources = []
    else:
        sources = list(dict.fromkeys(c["source"] for c in chunks))

    return {"answer": answer, "sources": sources, "chunks": chunks}


def _print(result):
    print(f"\nANSWER:\n{result['answer']}\n")
    if result["sources"]:
        print("SOURCES:")
        for s in result["sources"]:
            print(f"  - {s}")
    else:
        print("SOURCES: (none — system declined to answer)")


def main():
    if len(sys.argv) > 1:
        _print(ask(" ".join(sys.argv[1:])))
        return
    print("Ask a question about UW courses (Ctrl-C to quit).")
    try:
        while True:
            q = input("\n> ").strip()
            if q:
                _print(ask(q))
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    main()
