# The Unofficial Guide — Project 1

A Retrieval-Augmented Generation (RAG) system that answers plain-language questions
about University of Waterloo courses using real student reviews, with grounded answers
and source citations.

---

## Domain

Student course reviews at the University of Waterloo. This knowledge is valuable because
official course syllabi and university descriptions rarely reflect the true difficulty,
real workload, helpfulness of professors, or the "hidden rules" of a course (e.g., that
quizzes drop your lowest marks, that you must do textbook practice problems, or that a
course is effectively a repeat of grade-12 material). This honest, subjective, student-to-student
feedback is normally scattered across forums and word-of-mouth and is hard to search
systematically — which is exactly what this system makes possible.

---

## Document Sources

All documents are real student reviews written on [UWFlow](https://uwflow.com), the
student-run UW course review site. The raw data comes from the publicly available
UWaterloo Course Reviews dataset (mirrored on GitHub at
[jpbower14/uwaterloo_data](https://github.com/jpbower14/uwaterloo_data),
`course_data_clean.csv` — 14,838 review rows across 1,974 courses). The twelve
most-reviewed courses were selected for subject variety, and each course's reviews
were exported to one plain-text document under `documents/`.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | UWFlow — MATH 135 (Algebra for Honours Mathematics) | Student reviews (.txt) | `documents/uwflow_math135_reviews.txt` · https://uwflow.com/course/math135 |
| 2 | UWFlow — ECON 101 (Introduction to Microeconomics) | Student reviews (.txt) | `documents/uwflow_econ101_reviews.txt` · https://uwflow.com/course/econ101 |
| 3 | UWFlow — MATH 137 (Calculus 1 for Honours Mathematics) | Student reviews (.txt) | `documents/uwflow_math137_reviews.txt` · https://uwflow.com/course/math137 |
| 4 | UWFlow — CS 135 (Designing Functional Programs) | Student reviews (.txt) | `documents/uwflow_cs135_reviews.txt` · https://uwflow.com/course/cs135 |
| 5 | UWFlow — ENGL 109 (Introduction to Academic Writing) | Student reviews (.txt) | `documents/uwflow_engl109_reviews.txt` · https://uwflow.com/course/engl109 |
| 6 | UWFlow — STAT 230 (Probability) | Student reviews (.txt) | `documents/uwflow_stat230_reviews.txt` · https://uwflow.com/course/stat230 |
| 7 | UWFlow — PD 1 (Career Fundamentals) | Student reviews (.txt) | `documents/uwflow_pd1_reviews.txt` · https://uwflow.com/course/pd1 |
| 8 | UWFlow — SPCOM 223 (Public Speaking) | Student reviews (.txt) | `documents/uwflow_spcom223_reviews.txt` · https://uwflow.com/course/spcom223 |
| 9 | UWFlow — MATH 239 (Introduction to Combinatorics) | Student reviews (.txt) | `documents/uwflow_math239_reviews.txt` · https://uwflow.com/course/math239 |
| 10 | UWFlow — CHEM 120 (General Chemistry 1) | Student reviews (.txt) | `documents/uwflow_chem120_reviews.txt` · https://uwflow.com/course/chem120 |
| 11 | UWFlow — CS 246 (Object-Oriented Software Development) | Student reviews (.txt) | `documents/uwflow_cs246_reviews.txt` · https://uwflow.com/course/cs246 |
| 12 | UWFlow — CS 240 (Data Structures and Data Management) | Student reviews (.txt) | `documents/uwflow_cs240_reviews.txt` · https://uwflow.com/course/cs240 |

Full provenance is recorded in `documents/SOURCES.md`.

---

## Chunking Strategy

**Chunk size:** 500 characters (target)

**Overlap:** 100 characters — applied *only inside* a single long review that must be
split, never across two different students' reviews (see reasoning below).

**Preprocessing before chunking (`ingest.py`):**
- Parsed each document's 3-line header to extract the course code and title.
- Normalized Unicode typography to ASCII (curly quotes → `'`/`"`, em/en dashes → `-`,
  `…` → `...`, non-breaking spaces → spaces) and collapsed redundant whitespace and
  blank lines. There was no HTML to strip because the corpus came from a cleaned dataset
  rather than scraped pages.

**Why these choices fit the documents:** The documents are collections of short,
opinion-dense student reviews — the median review is ~174 characters and 90% are under
~484 characters. A 500-character target keeps most individual reviews intact as a single
self-contained chunk, so a chunk reads as one coherent opinion rather than a fragment or
a dilution of several unrelated topics. Reviews shorter than the target are grouped
together (up to ~500 chars) so we don't waste embeddings on 5-word reviews; the ~10% of
reviews longer than 500 chars are split at sentence boundaries with 100 characters of
overlap to preserve continuity across the cut. Overlap is deliberately *not* applied
between two different reviews, because bleeding one student's sentiment into another
student's chunk would corrupt the meaning of both.

**Final chunk count:** 1,177 chunks across the 12 documents (1,738 reviews total),
averaging 421 characters per chunk — comfortably inside the 50–2,000 sanity band.

---

## Sample Chunks

Five representative chunks as produced by `ingest.py` (each chunk text is prefixed with
its course in brackets, which is also stored in metadata for attribution):

| # | Source document | Chunk text |
|---|----------------|------------|
| 1 | `uwflow_cs240_reviews.txt` | `[CS 240: Data Structures and Data Management]` Review 46 (student liked the course): The midterm was very difficult and I failed it miserably, and don't be surprised if you do bad on the midterm. If you buckle down and study everything for the final, you should do ok... A lot of people say that the midterm is hard but the final is easier since there is more computation than proofs. |
| 2 | `uwflow_chem120_reviews.txt` | `[CHEM 120: General Chemistry 1]` Review 42 (student liked the course): CHEM 120 is a course that basically all science students have to take. There are 2 midterms and a final. The first midterm is about stoichiometry... The 2nd midterm is more theory based and is about things like Lewis structures and periodic trends... they were both VERY fair. |
| 3 | `uwflow_math135_reviews.txt` | `[MATH 135: Algebra for Honours Mathematics]` Review 23 (student liked the course): Learned a lot on how to properly write proofs and different mathematical ways of thinking. If you were even a bit serious about contest maths in high school, this course is an easy 90+. Also, Anton is just absolutely goated... |
| 4 | `uwflow_engl109_reviews.txt` | `[ENGL 109: Introduction to Academic Writing]` Review 76 (student disliked the course): Would be the worlds easiest class if there was some structure to it. My ta screwed me every way she could. Said she didn't have office hours every week until the course was over and she realized she did. Lowered my mark when I asked for help. |
| 5 | `uwflow_engl109_reviews.txt` | `[ENGL 109: Introduction to Academic Writing]` Review 25 (student liked the course): Course really depends on your TA. They are the ones that mark everything anyways. If you get a difficult TA that is hard to please, you may not end up with the marks you hope for. |

Each chunk is readable and answerable on its own. (Chunk #4 also illustrates honest
corpus noise — a frustrated, partly anecdotal review — which the system must handle.)

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. It runs locally with no
API key and no rate limits, produces 384-dimensional embeddings, and is fast enough to
embed all 1,177 chunks in seconds — a good fit for short, opinion-based review text and
a free local stack. Vectors are stored in **ChromaDB** with the collection created using
`metadata={"hnsw:space": "cosine"}` so distance scores are interpretable (lower = closer;
< 0.5 = a good match).

**Production tradeoff reflection:** If deploying for real users with cost not a
constraint, I'd weigh:
- **Accuracy on domain-specific text:** Reviews are full of UW-specific jargon and
  abbreviations ("bird course," "the curve," "PD," course codes like "cs246"). A larger
  model such as OpenAI `text-embedding-3-large` or a domain-adapted retriever would
  likely separate near-duplicate opinions more sharply.
- **Context length:** MiniLM truncates at 256 word-pieces, which is fine for our ~500-char
  chunks but would force chunking on long-form guides; an 8k-token model could embed
  whole documents and reduce chunking pressure (at the cost of less precise retrieval).
- **Latency & cost:** API-hosted models add per-call latency and cost and a network
  dependency; a local model keeps latency low and data private — for a free student tool,
  local wins, but at scale a hosted model with batching might be worth it.
- **Multilingual support:** Not needed here (all reviews are English), but a multilingual
  model would matter for an international student body.

---

## Retrieval Test Results

Run with `python evaluate.py --retrieval-only` (top-k = 5, cosine distance).

**Query 1:** "How do students generally feel about taking PD 1?"

Top returned chunks (all from `uwflow_pd1_reviews.txt`):
- (dist 0.279) "Somewhat pointless, IMO. Taught about finding a job... it should stop at PD1..."
- (dist 0.313) "What an absolute shit course. I actually tried to give PD 1 a chance..."
- (dist 0.363) "Huge waste of time..."

Relevance explanation: All five hits come from the correct source document and directly
express sentiment about PD 1, with the lowest distances in the whole eval set (0.279).
The query word "feel" has no lexical overlap with "pointless"/"waste of time," yet
semantic search surfaces them — demonstrating embeddings capturing sentiment, not
keywords.

---

**Query 2:** "Does CHEM 120 involve a lot of new concepts compared to high school chemistry?"

Top returned chunks (all from `uwflow_chem120_reviews.txt`):
- (dist 0.257) "It's a good review of high school chemistry with only a few new concepts thrown in."
- (dist 0.291) "CHEM 120 was an extension of grade 12 chemistry and delves a little deeper into thermochemistry, gases..."
- (dist 0.279) "The content is not really that hard..."

Relevance explanation: The top hit is an almost verbatim answer to the question, and the
#5 hit independently corroborates it ("extension of grade 12 chemistry"). The system
retrieved the precise comparison the user asked about from two different reviewers,
which is exactly the corroborating evidence grounded generation needs.

---

**Query 3:** "Is ECON 101 considered a heavy workload course?"

Top returned chunks (all from `uwflow_econ101_reviews.txt`):
- (dist 0.357) "so fking easy ... you can get 80+ even [if] you are not [going to lectures]"
- (dist 0.383) "Got an 82 in the class but had to work for it... boosted on a bell curve."
- (dist 0.392) "...the course was overall really [easy]..."

Relevance explanation: All hits are on-topic and from the right source; note that the #2
hit ("had to work for it") mildly dissents from the "bird course" consensus, giving the
generator honest nuance to work with rather than a one-sided answer.

---

## Grounded Generation

Grounding is enforced both by the **system prompt** and by **pipeline structure**, so the
model cannot quietly fall back on training knowledge.

**System prompt grounding instruction** (verbatim, from `query.py`):

```
You answer questions about University of Waterloo courses using ONLY the student
reviews supplied in the user message. Follow these rules exactly:
1. Use only facts stated in the provided reviews. Never add outside or general
   knowledge, even if you are confident.
2. If the reviews do not contain enough information to answer, reply with exactly
   this sentence and nothing else: "I don't have enough information on that."
3. When reviews disagree, report the disagreement honestly instead of inventing a
   consensus or a middle ground.
4. Be concise (2-5 sentences). Do not list sources yourself — they are attached
   separately by the system.
```

The model used is `llama-3.3-70b-versatile` (Groq), called at `temperature=0.1` for
deterministic, faithful answers. The only course content in the prompt is the retrieved
chunks, formatted as labeled excerpts (`[Review excerpt N from <source>]`), so there is
no other material for the model to draw on.

**How source attribution is surfaced in the response:** Source filenames are **not**
generated by the LLM — they are attached programmatically in code (`query.py`) from the
metadata of the retrieved chunks (de-duplicated, order preserved). On a refusal, the
code attaches **no** sources, so an unanswerable query never shows phantom citations.
This makes attribution a guarantee of the pipeline rather than something the model could
hallucinate or forget.

---

## Example Responses

**Grounded response 1**

Query: "Do students find MATH 137 harder than MATH 135?"

Response: "According to Review 57, MATH 135 is 'not that hard compared with MATH 137.'
However, Review 68 indicates MATH 135 is harder because of its emphasis on proofs, which
contradicts Review 57. Therefore there is disagreement among students about which course
is harder."

Source attribution: `uwflow_math135_reviews.txt`, `uwflow_math137_reviews.txt`

> *Note: the wording above is paraphrased from the local run. Paste the exact verbatim
> `evaluate.py` output here before submitting.*

---

**Grounded response 2**

Query: ⟨paste a second answered query from your local `evaluate.py` run⟩

Response: ⟨paste the exact system answer⟩

Source attribution: ⟨paste the sources line⟩

---

**Out-of-scope query**

Query: "Which professor teaches PHYS 234 and what are their office hours?"

System response (refusal): "I don't have enough information on that."

(No sources attached — the system declined rather than answering from the loosely-related
professor/office-hours chunks it retrieved at distance ≥ 0.51.)

---

## Query Interface

A **Gradio** web UI (`app.py`), launched with `python app.py` at `http://localhost:7860`.

**Input fields:** A single text box, "Your question," plus an "Ask" button (pressing
Enter also submits). A set of example questions is provided as one-click inputs.

**Output format:** Two read-only panels — **"Answer"** (the grounded response) and
**"Retrieved from"** (a bulleted list of the source documents the answer drew from). On
an out-of-scope question the Answer shows the refusal and the sources panel shows
"(none — not enough info)."

---

**Sample Interaction Transcript**

> **User:** How do students generally feel about taking PD 1?

> **System (Answer):** ⟨paste the exact PD 1 answer from your local run⟩
>
> **System (Retrieved from):** • uwflow_pd1_reviews.txt

> *Paste the verbatim answer text above from your local `python app.py` or
> `python query.py "How do students generally feel about taking PD 1?"` run.*

---

## Evaluation Report

Test questions and expected answers are from `planning.md`. Retrieval quality is judged
from the `evaluate.py --retrieval-only` output (already verified). Response accuracy
should be confirmed against the verbatim answers from your local full run.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Is ECON 101 considered a heavy workload course? | No — an easy/bird course. | ⟨paste/summarize verbatim answer⟩ | Relevant (5/5 from ECON 101, best dist 0.357) | ⟨Accurate / Partial — confirm⟩ |
| 2 | Do students find MATH 137 harder than MATH 135? | Cross-doc: MATH 135 often harder (proofs new); 137 a continuation of HS calculus. | Reported the disagreement between Review 57 and Review 68 instead of forcing a verdict. | Relevant (mix of MATH 135 & 137, best dist 0.327) | Accurate — correctly surfaced conflicting evidence |
| 3 | How do students generally feel about taking PD 1? | Widely disliked — useless busy work. | ⟨paste/summarize verbatim answer⟩ | Relevant (5/5 from PD 1, best dist 0.279) | ⟨Accurate — confirm⟩ |
| 4 | What is the main difficulty associated with CS 246? | The long, heavy assignments. | ⟨paste/summarize verbatim answer⟩ | Partially relevant (3/5 from CS 246; drift to CS 240 & CS 135; conflicting claims) | ⟨likely Partially accurate — confirm; see Failure Case⟩ |
| 5 | Does CHEM 120 involve a lot of new concepts vs high school? | No — largely repeats grade-12 chemistry. | ⟨paste/summarize verbatim answer⟩ | Relevant (5/5 from CHEM 120, best dist 0.257) | ⟨Accurate — confirm⟩ |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Q4 — "What is the main difficulty associated with CS 246?"
(partial failure in retrieval).

**What the system returned:** The retrieved context was mixed and partly contradictory.
The top chunk actually *downplays* difficulty ("the difficulty of each assignment... was
on par to... CS135 or CS136... a tad bit easier"), and two of the five chunks drifted to
the *wrong courses* — CS 240 (dist 0.464) and CS 135 (dist 0.475) — rather than CS 246.
The expected answer (assignments are long/heavy on C++ design and memory management) is
supported by some reviews but is not cleanly the dominant retrieved signal.

**Root cause (tied to a specific pipeline stage):** This is a **retrieval/embedding**
failure, not a generation one. Two factors combine: (1) the query word "difficulty" is
generic and semantically close to *any* CS course's difficulty discussion, so the
embedding model pulls in chunks from sibling CS courses that share vocabulary; and (2)
CS 246 reviews genuinely disagree about whether the course is hard, so the corpus signal
is noisy. The distances here are the highest in the eval set (0.444–0.475, vs. 0.257 for
CHEM 120), which quantitatively flags the weaker match.

**What you would change to fix it:** Add **metadata filtering** so that when a query
names a specific course (e.g., "CS 246"), retrieval is restricted to that course's
chunks via a ChromaDB `where={"course_code": "CS 246"}` filter — eliminating the CS 240
/ CS 135 drift entirely. (This is also a listed stretch feature.) A secondary improvement
would be a hybrid keyword+semantic search so the exact token "246" is weighted.

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing the chunking strategy in
`planning.md` *before* coding forced a concrete decision — 500 chars / 100 overlap, split
on review boundaries — that made `ingest.py` straightforward to implement and verify
against a target. The "Anticipated Challenges" section, which named missing source
attribution as a risk, directly shaped the design: course code was prepended to every
chunk's text *and* stored in metadata from the very first version, so attribution worked
without a later rewrite.

**One way your implementation diverged from the spec, and why:** The original plan named
LangChain's `RecursiveCharacterTextSplitter`, but during implementation that dependency
wasn't in the curated `requirements.txt`, and the documents already had clean `\n\n`
boundaries between reviews. So the spec was updated and the splitter was hand-written
(~40 lines) to split on review boundaries and only overlap *within* a long review — a
better fit than a generic character splitter, which would have cut across separate
students' opinions.

---

## AI Usage

> *These instances describe the real AI-assisted workflow for this project. Review and
> edit them so they reflect your own voice and any further changes you made.*

**Instance 1 — Ingestion & chunking pipeline**

- *What I gave the AI:* My `planning.md` Chunking Strategy section (500 chars / 100
  overlap), the Architecture diagram, and the document format (3-line header + labeled
  reviews separated by blank lines).
- *What it produced:* `ingest.py` — a loader that parses the header, normalizes Unicode,
  groups short reviews and sentence-splits long ones, and prepends the course code to
  each chunk while storing it in metadata.
- *What I changed or overrode:* I directed it to *not* apply overlap across separate
  reviews (only within a single long review), since overlapping different students'
  opinions would corrupt chunk meaning — a refinement beyond the original spec.

**Instance 2 — Grounding enforcement in generation**

- *What I gave the AI:* The Milestone 5 grounding requirement (answer from retrieved
  context only; refuse when insufficient) and the required source-attribution behavior.
- *What it produced:* `query.py` with a numbered system prompt and an `ask()` function
  that builds context from retrieved chunks and calls Groq `llama-3.3-70b-versatile`.
- *What I changed or overrode:* I required source attribution to be attached
  **programmatically** from chunk metadata rather than asked of the LLM, and added logic
  to attach **no** sources on a refusal — so an out-of-scope query can never surface
  phantom citations.
