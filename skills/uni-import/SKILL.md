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

One run imports **one** piece of material. If several are uploaded, import the most
obvious candidate and tell the student to re-invoke for the rest; ask only if the
choice is ambiguous.

**Contract** (binding, shared across the uni- framework):
- `/mnt/project`, `/mnt/user-data/uploads`, and `/mnt/skills` are read-only — never
  attempt in-place edits. To update a canonical file: read the current version
  (project, then uploads, then conversation), write the new one to
  `/mnt/user-data/outputs/<same-filename>`, present it, remind the student to re-upload.
- **Merge, never clobber** `course-state.md` and `exam-brief.md`: preserve every row,
  status, and date; append; the files' own headers carry the rules.
- State stays lean: content goes into digests and `exam-brief.md`, never into
  `course-state.md` (topic names ≤ 8 words; no prose in that file).

## Route by material type first

- **Lecture material** (slide deck, script, lecture notes, transcript) → Route A.
- **Exam-related material** (past exam, exam announcement, the professor's exam
  info, notes the student relays from the last lecture, an assignment sheet offered
  explicitly as a question-style anchor) → Route B: `references/exam-material.md`.
- A file can be both (first/last-lecture decks often carry exam logistics slides):
  run Route A, then open the Route B reference for those pages, same run, saying so.

If no `course-state.md` exists anywhere, the course isn't set up: say so and offer
to run **uni-setup** first (if it isn't installed, create a minimal state file
inline, saying uni-setup would do it properly).

## Route A — lecture material → digest + topics

### 1. Extract text cheaply first

**PDF:** don't rasterize by default (~5x the tokens of text). The triage helper
writes one text file per page, flags pages worth a *visual* look (vector paths,
image area — signals boilerplate can't fool), and marks **equation pages**, which
is a fidelity marker for step 3, not a raster flag:

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

It prints, per existing digest, the title, Open questions with their citable Q-IDs,
Connections, and Topics line — under 100 lines for a whole course, and all the new
digest needs to write `resolves digest-05 Q2: …` or "builds on T12" in §Connections
(step 5). No digests yet → §Connections is `— none —`.

### 3. Process in sub-batches; rasterize only what's needed

Work through pages in sub-batches of ~20–30. Per sub-batch: read the extracted text;
for flagged pages (plus any you judge figure-heavy), rasterize and Read the images:
`python scripts/pdf_triage.py raster <file.pdf> --pages 2,4,9-11 --dpi 150 --outdir
/home/claude/<unit>`.

Write a short digest **fragment** per sub-batch to `/home/claude/<unit>/` as you go —
this keeps long decks from overflowing context and makes the final digest a stitch,
not a rewrite. Three things are captured *while reading*:

- **Figures — one running counter for the whole import.** The moment a figure is
  worth keeping, write its index line into the fragment (`F<n> · what it shows ·
  source: \`file\` p.N`) and cite it inline by that ID. The merge concatenates index
  lines in order and never renumbers, so `(F7)` written in batch two still means F7
  at the end; another digest's figure is cited as `digest-00 F17`.
- **Formulas — read at the right resolution, then transcribe what is drawn.** The
  text layer destroys typeset math: grouping parens vanish, layout flattens. Read
  from text only when a formula is simple, standard-notation, and its structure
  obviously survived; otherwise rasterize that page first (matrix/multi-line layout,
  grouping you're inferring rather than seeing, the course's own notation). Then
  write what the page shows, not what the formula ought to be: an unfamiliar token
  inside an equation is an **opaque operator** — keep its brackets as drawn,
  `f(A⁻¹x)` never becomes `A_f·A⁻¹x` — and transcribe the connectives around it too
  ("but this needs X" is not "because X"). A hedge forming ("schematic", "roughly")
  means stop and rasterize; deleting the hedge word is not a fix. Every formula ends
  `(p.N)`.
- **Lecturer-posed questions — at first sight, in two classes.** Append each
  verbatim with its page to `/home/claude/<unit>/lecturer-examples.md`. The test is
  what the deck *does* with the question: it answers it there or on the next page →
  `- rhetorical: "…" (p.N)`, a segue; it leaves the answer to the student, or calls
  it an exercise or exam question → `- task: "…" (p.N)`, the strongest
  question-style signal there is. Balanced call → task. Only tasks reach the digest,
  marked `(lecturer example)`; rhetorical prompts go **nowhere** — not an angle, not
  an open question. The validator checks both directions.

Exam logistics/format slides inside a lecture deck: note the pages; handle them via
`references/exam-material.md` after the digest is done.

### 4. Detect the unit and the scale

From the material itself, determine:
- **The course's structural unit** (chapter, lecture, week). Number the digest in
  that scheme, matching existing `digest-*` files; the first import sets the pattern.
- **How many in-class sessions the material spans** (slide count, date markers,
  "Lecture 5+6" titles) — this scales the topic count in step 6.
- If an agenda slide reveals the real unit count and the header says
  `units: 15 (assumed)`, correct the line and say so.

### 5. Merge fragments into the digest

Use `assets/digest-template.md` — fill every section; its comments carry the rules.
The ones that bite: figure IDs stay as assigned; every scratch `task:` lands in
§Likely exam angles verbatim with its marker (marked bullets don't count toward the
3–8); **no hedged formula survives the merge**; **condensing never deletes an exam
angle** — if its data moved to the figure index, the angle stays and points at the
figure; open questions are `Q1 · one specific gap` each — something the material
uses or names without supplying, not only what a slide calls deferred (an overview's
roadmap is never one); **§Connections** links to earlier units (*builds on* /
`resolves digest-NN Qk: …` / *feeds into*) from step 2's output. Name it
`digest-<NN>-<slug>.md` (slug 2–4 lowercase words from the material's own title,
unique — number every part of a multi-part topic).

### 6. Register topics in course-state.md

Read `references/topics.md` **before** choosing rows. The count is arithmetic, not
a per-lecture habit: **target ≈ (35 ÷ `units`) × sessions spanned**, rounded (with
`units: 15` a single lecture gets 2–3 rows); say it in one line. Then granularity:
review-sized themes the student would rate as a unit, never one row per term; when
unsure, coarser. Names ≤ 8 words, parentheticals counted. Append with fresh
sequential IDs, status `new`; match loosely against existing rows. **Every
pre-existing row stays byte-identical — no exceptions**; a resolution lives in the
digest's §Connections, never in this file. Past ~50 rows the table stops being
self-assessable — go coarser.

### 7. Validate, fix, re-run — then deliver

```bash
python scripts/check_import.py --digest /mnt/user-data/outputs/digest-NN-slug.md \
    --state /mnt/user-data/outputs/course-state.md --prev /mnt/project/course-state.md \
    --scratch /home/claude/<unit> --project /mnt/project --sessions <N>
```

Every message names the offending ID or text, and every finding is yours to fix —
not a question for the student. Errors (dangling figure refs, missing file/page, a
`task:` example missing or unmarked, a rhetorical prompt in the digest, a hedged
formula — rasterize and re-transcribe, or point at the figure if truly illegible —
a missing or out-of-sequence Q-ID, a `resolves` citing a Q that doesn't exist,
budget breaches, any changed pre-existing row) mean not deliverable: fix, re-run
until `0 errors`. Warnings are judgment calls — say what you decided. If an error
survives two fix rounds, show the student rather than deliver a broken file.

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
  before removing a row that no longer matches the material.
- **Unit out of order** (chapter 7 before 5): number by the course's scheme.
- **Whole-semester PDF:** one unit per run via page ranges; ask where to start.
- **State file without a `units:` line:** read as `15 (assumed)`; add the line when
  you write the file.
