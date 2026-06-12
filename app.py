"""Milestone 5 — Query interface (Gradio web UI).

Run:  python app.py   then open http://localhost:7860

Type a question about a UW course; the system retrieves the most relevant
student-review chunks, generates a grounded answer, and shows which source
documents the answer drew from.
"""

import startup; startup.build_if_needed()

import gradio as gr

from evaluate import EVAL
from query import ask


def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    try:
        result = ask(question)
    except RuntimeError as e:  # missing API key / vector store, with fix hint
        return str(e), ""
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(none — not enough info)"
    return result["answer"], sources


# UI example chips come straight from the evaluation set so the demo and the
# eval harness can never drift apart.
EXAMPLES = [question for question, _ in EVAL[:4]]

with gr.Blocks(title="The Unofficial Guide — UW Course Reviews") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask what a University of Waterloo course is *actually* like — answered "
        "from real student reviews, with sources cited."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. What is the workload like in CS 246?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    gr.Examples(EXAMPLES, inputs=inp)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
