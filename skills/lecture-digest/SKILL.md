---
name: lecture-digest
description: >-
  Condense university lecture materials for ONE course into a compact, exam-focused
  knowledge base for use in a Claude Project. Use this whenever a student uploads
  lecture slides, lecture notes, a script, or a transcript (PDF, docx, md, txt) and
  wants to summarize/condense them for studying, build a study knowledge base, set up
  a course project, catch up before an exam, or plan exam revision — even if they
  don't say the word "digest." Triggers include: "summarize these lecture slides",
  "help me study for my [course] exam", "condense this deck into notes", "I have an
  exam in two weeks, make me a study plan", "build a knowledge base from my lectures",
  "I'm behind in [course], help me catch up". Handles ONE lecture file per run, plus
  course-wide tracking and study-plan generation. Subject-agnostic — works for any
  field. Do NOT use for non-study document summarization, single-slide questions, or
  generic note-taking unrelated to a course.
---

# Lecture Digest

Turn a course's lecture materials into a lean knowledge base a student can drop into
a Claude Project and study against — both early-semester setup and last-minute
exam-sprint catch-up. Everything here is **subject-agnostic**: infer structure from
the material itself, never assume a particular field.

## What this skill produces

- **Per-lecture digest files** — one compact, exam-focused digest per lecture.
- **Course-wide files** that accumulate over the semester: `topic-tracker.md`,
  `study-plan.md`, and a cross-course `learning-profile.md`.
- **A ready-to-paste Project instructions block** that turns the student's Claude
  Project into a general course hub (study sessions, checking their own assignments,
  revision planning, quick Q&A) — not a tutor-only project.

This skill builds the knowledge base. Two sibling skills act on it: **`study-tutor`**
runs interactive study/revision sessions against the digests, and **`assignment-check`**
gives a grader's-eye review of the student's own worked solutions. The Project block
below routes between all three.

## Figure out which job this is

Three distinct jobs — route based on what the student is doing:

1. **Digest a lecture** (the most common) → they uploaded a lecture file and want it
   condensed. Go to *Digesting one lecture* below. **One lecture per run.**
2. **Build or update a study plan** → they mention an exam date, catching up, or
   planning revision. Go to `references/study-plan.md`.
3. **Set up the Project** → they want the custom-instructions block for their course
   Project. Hand over `assets/project-instructions.md` (see *The Project instructions
   block* below).

These overlap: a first-ever run for a course usually digests a lecture *and* creates
the course-wide files *and* offers the Project block. Later runs typically just digest
and update the tracker. Read the room.

---

## Digesting one lecture

**Process exactly one lecture file per run.** If several are uploaded, digest one and
tell the student to re-invoke for the rest (one per run keeps each digest focused and
the cost bounded). If it's ambiguous which one, ask.

### 1. Extract text cheaply first

Don't rasterize slides by default — it's ~8x the token cost of text extraction and
usually unnecessary. Pull the text layer first.

**PDF** (slide decks, scripts): use the bundled triage helper. It writes one text file
per page and flags the pages worth a **visual** look. Crucially, it does **not** flag
by "few characters" — that fails on real slides, because headers/footers and in-diagram
labels mean a diagram slide often has *more* text than a sparse bullet slide. Instead it
uses **structural** signals that ignore boilerplate: the number of vector drawing paths
on the page (bullet-text slides have ~0; diagrams/graphs have many) and the fraction of
the page covered by embedded images (figures, screenshots).

```bash
# Best detection needs PyMuPDF; install once if it's not present:
pip install pymupdf --break-system-packages
python scripts/pdf_triage.py triage <lecture.pdf> --outdir /home/claude/<lecture>
```

It prints a per-page signal table (chars · vector_paths · images · image%), the flagged
pages with the reason each tripped, and writes `manifest.json` + `text/page-NNN.txt`.
Read the table — the flag is a strong hint, not gospel. Two cases it calls out: if
**most** pages flag, it's a diagram-heavy deck and rasterizing the whole thing at low
DPI may be simpler; if **nothing** flags on an obvious slide deck, sample a page or two
anyway (or lower `--paths-threshold`) in case it's missing label-only diagrams. If the
PDF is **scanned** (no text layer), treat every page as visual — rasterize and read, or
OCR in bulk (see the pdf-reading skill). Without PyMuPDF the script still runs in a
poppler fallback that detects embedded images and sparse text but **cannot** see vector
diagrams — it warns you, and installing PyMuPDF is the fix. Deeper PDF questions:
`/mnt/skills/public/pdf/SKILL.md`.

**docx / md / txt** (notes, transcripts): just read the text directly — no triage
needed. For docx, the docx skill (`/mnt/skills/public/docx/SKILL.md`) covers
extraction; mammoth or a plain text dump is usually enough for notes.

### 2. Process in sub-batches; rasterize only what's needed

Work through the pages in **sub-batches of ~20–30**. For each sub-batch:

- Read the extracted text for those pages (cheap).
- For the **flagged** pages in that batch (plus any you judge figure-heavy from reading
  the text), rasterize and Read them so you actually see the diagram/figure/equation:

```bash
python scripts/pdf_triage.py raster <lecture.pdf> --pages 2,4,9-11 --dpi 150 --outdir /home/claude/<lecture>
```

  Then Read the printed image paths. Don't visually inspect plain text slides — the
  extracted text already has them.

### 3. Write an intermediate fragment per sub-batch

As you finish each sub-batch, write a short digest **fragment** to disk (e.g.
`/home/claude/<lecture>/fragment-01.md`) covering just those pages. Writing as you go
keeps long decks from overflowing context and makes the final merge a stitch rather
than a from-scratch summary.

### 4. Merge fragments into the final digest

Combine the fragments into one digest file using the template at
`assets/digest-template.md`. The sections (fill every one; use the lecturer's own
terminology):

- **Title and source reference** — lecture title, filename, slide/page range.
- **Core concepts** — key terms with 1–3 sentence definitions.
- **Key relationships / processes** — how concepts connect, causal chains,
  workflows. **Describe diagrams and figures in words** rather than reproducing them;
  name the slide so the student can find the original.
- **Formulas, algorithms, theorems, proofs** — reproduce short ones precisely; for
  long derivations, summarize the steps and point to where the full version lives.
- **Likely exam angles** — 3–6 bullets predicting the *types* of question this
  material could generate ("compare X and Y", "apply algorithm to a worked example",
  "derive/prove Z"), **not** invented questions. **If the slides contain example exam
  questions the lecturer provided, that's the strongest possible signal — capture
  them verbatim and mark them as lecturer examples.** Watch for them while reading.
- **Open questions / unclear points** — genuine gaps worth following up later.

Write the final digest to `/mnt/user-data/outputs/` and present it. **Use a uniform
filename so digests sort and line up across runs — this is the convention:**

```
digest-<NN>-<slug>.md
```

- `<NN>` — the lecture/unit number, **zero-padded to two digits** (`02`, not `2`).
  Pull it from the source filename or the title slide (e.g. `VL2_KR.pdf`,
  `Lecture 3 — DP`, `ai-ws25-04.pdf` → `02`, `03`, `04`). If the material has no
  discoverable number, use the next sequential index after the existing digests, or
  `00` for a one-off.
- `<slug>` — the lecture's main topic, lowercase, hyphenated, ASCII, ~2–4 words
  (`dynamic-programming`, `knowledge-representation`).

**Before naming, list the digests already in the project/uploads (`digest-*.md`) and
match whatever pattern is already established** — its padding, separators, and casing
win over the example above. Consistency across the course matters more than any single
convention, and re-uploaded files only line up if the names are stable. Only when this
is the first digest do you set the canonical pattern.

### 5. Update the course-wide files

After the digest, create-or-update the course-wide files. **The hard rule is
merge-never-clobber** — these files carry the student's own mastery data and
hand-entered notes across runs. Full rules and templates: `references/course-files.md`.

In brief: append the lecture's **trackable topics** to `topic-tracker.md` as status
`new` while preserving every existing row. A tracker row is a review-sized,
examinable theme — a small handful per lecture — **not** one row per defined term; the
digest already holds the term-level detail. The granularity rule (with a worked
example) is in `references/course-files.md` and is the thing most worth getting right.
Create `learning-profile.md` from its template **only if it doesn't already exist**.
`study-plan.md` is generated by its own flow, not here.

---

## Building / updating the study plan

When the student wants to plan exam prep (exam date mentioned, catching up, "make me
a plan"), follow `references/study-plan.md`. It covers: asking for the exam date and
whether the tracker holds real mastery data or is a cold start; the cold-start
self-assessment seeding pass; choosing **full-prep** vs **sprint** mode by days
remaining vs. topic count; the sprint recall diagnostic and the
must-cover/worth-a-look/accept-risk triage. Don't reproduce that logic here — read
the reference when this job comes up.

---

## The Project instructions block

`assets/project-instructions.md` is a ready-to-paste Claude Project custom-instructions
block (subject-agnostic, under 6000 chars). It turns the student's course Project into
a general **course hub** rather than a tutor-only project: it frames the knowledge
base, enforces the merge-never-clobber discipline on the editable files, and routes
between the activities the student actually does —

- **study / revise / quiz me / mock exam** → the `study-tutor` skill (with a compact
  inline fallback so sessions still work if that skill isn't installed),
- **check my own assignment solution / "where would I lose points"** → the
  `assignment-check` skill, judging the work against the course's methods as captured
  in the digests and any slide decks in the project,
- **plan my revision / "I have an exam on [date]"** → the study-plan flow,
- **quick content question** → answer straight from the digests.

It's static — the same block works for any course — so deliver it as-is when setting up
the course, and tell the student to paste it into their Project's custom instructions.
For the richest study sessions and assignment reviews, they'll want the `study-tutor`
and `assignment-check` skills installed too, but the block degrades gracefully without
them.

---

## A note on scope

One course at a time, one lecture file per run. Keep digests dense and exam-focused
rather than exhaustive — they're study aids, not replacements for the slides. When in
doubt about structure, let the material tell you what it is.
