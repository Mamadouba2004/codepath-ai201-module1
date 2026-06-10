"""Milestone 5 — Query interface (Gradio web UI).

Run:  python app.py   then open http://localhost:7860

Type a question about a UW course; the system retrieves the most relevant
student-review chunks, generates a grounded answer, and shows which source
documents the answer drew from.
"""

import gradio as gr

from query import ask


def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(none — not enough info)"
    return result["answer"], sources


EXAMPLES = [
    "Is ECON 101 considered a heavy workload course?",
    "Do students find MATH 137 harder than MATH 135?",
    "How do students generally feel about taking PD 1?",
    "What is the main difficulty associated with CS 246?",
]

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
