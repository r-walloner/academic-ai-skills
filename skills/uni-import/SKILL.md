---
name: uni-import
description: >-
  Import ONE piece of university course material into a uni- framework course project. Lecture
  slides, scripts, or notes become a compact digest plus topic registration in course-state.md;
  past exams, exam announcements, and professor exam hints go into exam-brief.md. Use whenever a
  student uploads course material and wants it digested, summarized, condensed, imported, or added
  to their course knowledge base — "summarize these slides", "add lecture 5", "digest this
  chapter", "here's a past exam", "the prof told us about the exam format", "import this" — even
  if they don't say "import". One file per run. Do NOT use for study sessions (uni-tutor),
  building the study plan (uni-plan), self-assessment (uni-assess), or reviewing the student's own
  solutions (uni-check).
---

# uni-import — the single door into the knowledge base

One run imports **one** piece of material. If several files are uploaded, import the
most obvious candidate and tell the student to re-invoke for the rest — one per run
keeps each digest focused and the cost bounded; ask only if the choice is ambiguous.

**Contract** (binding, shared across the uni- framework):
- `/mnt/project`, `/mnt/user-data/uploads`, and `/mnt/skills` are read-only — never
  attempt in-place edits. To update a canonical file: read the current version
  (project, then uploads, then conversation), write the new one directly to
  `/mnt/user-data/outputs/<same-filename>`, present it, remind the student to re-upload.
- **Merge, never clobber** `course-state.md` and `exam-brief.md`: preserve every
  existing row, status, date, and note; append; the files' own headers carry the rules.
- State stays lean: content goes into digests and `exam-brief.md`, never into
  `course-state.md` (topic ≤ 8 words, note ≤ 120 chars).

## Route by material type first

- **Lecture material** (slide deck, script, lecture notes, transcript) → Route A.
- **Exam-related material** (past exam, exam announcement, the professor's exam
  info, notes the student relays from the last lecture, an assignment sheet offered
  explicitly as a question-style anchor) → Route B: `references/exam-material.md`.
- A file can be both (first/last-lecture decks often carry exam logistics slides):
  run Route A, then open the Route B reference for those pages, same run, saying so.

If no `course-state.md` exists anywhere, the course isn't set up: say so and offer
to run the **uni-setup** skill first (if it isn't installed, create a minimal state
file inline — and say that uni-setup would do this properly).

## Route A — lecture material → digest + topics

### 1. Extract text cheaply first

**PDF:** don't rasterize by default (~5x the tokens of text). The triage helper
writes one text file per page and flags the pages worth a *visual* look, using
structural signals (vector paths, embedded image area) that boilerplate can't fool:

```bash
pip install pymupdf --break-system-packages   # once, if missing
python scripts/pdf_triage.py triage <file.pdf> --outdir /home/claude/<unit>
```

Skim the per-page table; when the report needs judgment (most pages flagged, none
flagged, scanned PDF, poppler fallback) read `references/pdf-notes.md`.
**docx / md / txt:** read the text directly; no triage needed.

### 2. Pull the cross-linking context of existing digests — cheaply

```bash
python scripts/prior_digests.py            # searches /mnt/project, then uploads
```

It prints, per existing digest, only the title, Open questions, Connections, and
Topics line — under 100 lines for a whole course, and all the new digest needs to
write "resolves the question digest-05 left open" or "builds on T12" in
§Connections (step 5). No digests yet → §Connections is `— none —`.

### 3. Process in sub-batches; rasterize only what's needed

Work through pages in sub-batches of ~20–30. Per sub-batch: read the extracted text;
for flagged pages (plus any you judge figure-heavy from the text), rasterize and
Read the images: `python scripts/pdf_triage.py raster <file.pdf> --pages 2,4,9-11
--dpi 150 --outdir /home/claude/<unit>`.

Write a short digest **fragment** per sub-batch to `/home/claude/<unit>/` as you go —
this keeps long decks from overflowing context and makes the final digest a stitch,
not a from-scratch rewrite. Two things are captured *while reading*:

- **Figures — one running counter for the whole import.** The moment a figure is
  worth keeping, write its index line into the fragment (`F<n> · what it shows ·
  source: \`file\` p.N`) and cite it inline by that ID. The merge concatenates index
  lines in order and never renumbers, so `(F7)` written in batch two still means F7
  at the end. A reference to a figure the index doesn't define sends the tutor to a
  page that doesn't exist — silently.
- **Lecturer-posed example questions — captured at first sight.** Append each one
  verbatim, with its page, to `/home/claude/<unit>/lecturer-examples.md` (`- "…"
  (p.N)`). Strongest question-style signal there is; the validator checks that
  every entry reached the digest with its `(lecturer example)` marker.

Exam logistics/format slides inside a lecture deck: note the pages; handle them via
`references/exam-material.md` after the digest is done.

### 4. Detect the unit and the scale

From the material itself, determine:
- **The course's structural unit** (chapter, lecture, week — whatever this course
  uses). Number the digest in that scheme, matching any existing `digest-*` files;
  only the first import sets the pattern.
- **How many in-class sessions the material spans** (slide count, date markers,
  "Lecture 5+6" titles, agenda slides) — this scales the topic count in step 6.
- If an overview/agenda slide reveals the course's real unit count and the state
  header says `units: 15 (assumed)`, correct the line and say so.

### 5. Merge fragments into the digest

Use `assets/digest-template.md` — fill every section; its comments carry the rules.
The ones that bite: figure IDs stay as assigned; every scratch lecturer example
lands in §Likely exam angles verbatim with its marker; **condensing never deletes
an exam angle** — if its data moved to the figure index, the angle stays and points
at the figure; **§Connections** links this unit to earlier ones (*builds on* /
*resolves* / *feeds into*) from step 2's output and what the material says. Name it
`digest-<NN>-<slug>.md` (NN per the established pattern; slug 2–4 lowercase words).

### 6. Register topics in course-state.md

Read `references/topics.md` **before** choosing rows. The count is arithmetic, not
a per-lecture habit: **target ≈ (35 ÷ `units`) × sessions spanned**, rounded (with
`units: 15` a single lecture gets 2–3 rows); say it in one line. Then granularity:
review-sized themes the student would rate as a unit, never one row per term; when
unsure, coarser. Names ≤ 8 words, parentheticals counted. Append with fresh
sequential IDs, status `new`; match loosely against existing rows. The one edit
allowed on an existing row: a `→ resolved in digest-NN` pointer appended to a note
whose open question this unit answered; everything else stays byte-identical. Past
~50 rows the table stops being self-assessable — go coarser.

### 7. Validate, fix, re-run — then deliver

```bash
python scripts/check_import.py --digest /mnt/user-data/outputs/digest-NN-slug.md \
    --state /mnt/user-data/outputs/course-state.md --prev /mnt/project/course-state.md \
    --scratch /home/claude/<unit> --sessions <N>
```

Every message names the offending ID or text. Errors (dangling figure references,
missing file/page, a lecturer example missing or unmarked, budget breaches, a
pre-existing row changed beyond the pointer) mean not deliverable: fix, re-run until
`0 errors`. Warnings are judgment calls — say what you decided. If the same error
survives two fix rounds, show it to the student rather than deliver a broken file.

### 8. Deliver

Write the digest and the updated `course-state.md` to `/mnt/user-data/outputs/`,
present both, remind the student to upload them (and to keep the raw source file in
the project — figure retrieval depends on it). If a schedule already exists, note
that the new topics aren't in it yet: "run uni-plan to fold them in."

## Route B — exam-related material → exam-brief.md

Lives in `references/exam-material.md` — read it when the routing says so. Create
or merge the brief; sourced facts, archetypes mapped to topic IDs, recurring tasks,
hints; never set `exam:` from a past exam's date; validate with `--brief`; deliver.

## Edge cases

- **Re-import of a unit that already has a digest:** replace the digest file (same
  name); topic rows keep their IDs and statuses — append genuinely new topics, ask
  before removing any row that no longer matches the material.
- **Unit out of order** (chapter 7 before 5): number by the course's scheme, not
  by import order.
- **Whole-semester PDF:** one unit per run via page ranges; ask where to start.
- **State file without a `units:` line** (v2.0): read as `15 (assumed)`; add the
  line when you write the file.
