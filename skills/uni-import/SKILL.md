---
name: uni-import
description: >-
  Import ONE piece of university course material into a uni- framework course
  project. Lecture slides, scripts, or notes become a compact digest plus topic
  registration in course-state.md; past exams, exam announcements, and professor
  exam hints go into exam-brief.md. Use whenever a student uploads course material
  and wants it digested, summarized, condensed, imported, or added to their course
  knowledge base — "summarize these slides", "add lecture 5", "digest this chapter",
  "here's a past exam", "the prof told us about the exam format", "import this" —
  even if they don't say "import". One file per run. Do NOT use for study sessions
  (uni-tutor), building the study plan (uni-plan), self-assessment (uni-assess), or
  reviewing the student's own solutions (uni-check).
---

# uni-import — the single door into the knowledge base

One run imports **one** piece of material. If several files are uploaded, import the
most obvious candidate and tell the student to re-invoke for the rest — one per run
keeps each digest focused and the cost bounded; ask only if the choice is ambiguous.

**Contract** (binding, shared across the uni- framework):
- `/mnt/project`, `/mnt/user-data/uploads`, and `/mnt/skills` are read-only. Never
  attempt in-place edits. To update a canonical file: read the current version
  (project first, then uploads, then conversation), build the new content, write it
  directly to `/mnt/user-data/outputs/<same-filename>`, present it, and remind the
  student to re-upload it to the project.
- **Merge, never clobber** `course-state.md` and `exam-brief.md`: preserve every
  existing row, status, date, and note; append; update only with fresh evidence. The
  files' own comment headers carry the full rules — honor them.
- State stays lean: content goes into digests and `exam-brief.md`, never into
  `course-state.md` (topic ≤ 8 words, note ≤ 120 chars).

## Route by material type first

- **Lecture material** (slide deck, script, lecture notes, transcript) → Route A.
- **Exam-related material** (past exam, exam announcement, the professor's exam
  info, notes the student relays from the last lecture, an assignment sheet offered
  explicitly as a question-style anchor) → Route B.
- A file can be both (first/last-lecture decks often carry exam logistics slides):
  run Route A and fold the exam pages into Route B in the same run, saying so.

If no `course-state.md` exists anywhere, the course isn't set up: say so and offer
to run the **uni-setup** skill first (if it isn't installed, create a minimal state
file inline from the structure described in an existing digest or, failing that,
this skill's own outputs — but say that uni-setup would do this properly).

---

## Route A — lecture material → digest + topics

### 1. Extract text cheaply first

Don't rasterize slides by default — it costs ~5x the tokens of text extraction and
is usually unnecessary.

**PDF:** run the bundled triage helper; it writes one text file per page and flags
the pages worth a *visual* look using structural signals (vector paths, embedded
image area) that boilerplate text can't fool:

```bash
pip install pymupdf --break-system-packages   # once, if missing
python scripts/pdf_triage.py triage <file.pdf> --outdir /home/claude/<unit>
```

Skim the printed per-page table. When the report needs judgment — most pages
flagged, nothing flagged, scanned PDF, poppler fallback warning — read
`references/pdf-notes.md`.

**docx / md / txt:** read the text directly; no triage needed.

### 2. Process in sub-batches; rasterize only what's needed

Work through pages in sub-batches of ~20–30. Per sub-batch: read the extracted text;
for flagged pages (plus any you judge figure-heavy from the text), rasterize and
Read the images:

```bash
python scripts/pdf_triage.py raster <file.pdf> --pages 2,4,9-11 --dpi 150 --outdir /home/claude/<unit>
```

Write a short digest **fragment** per sub-batch to `/home/claude/<unit>/` as you go —
this keeps long decks from overflowing context and makes the final digest a stitch,
not a from-scratch rewrite. While reading, watch for two high-value finds:
**lecturer-provided example questions** (capture verbatim — strongest question-style
signal there is) and **exam logistics/format slides** (route to B).

### 3. Detect the unit and the scale

From the material itself, determine:
- **The course's structural unit** (chapter, lecture, week — whatever this course
  uses). Number the digest in the course's own scheme, matching the pattern of any
  existing `digest-*` files; only the first import sets the pattern.
- **How many in-class sessions the material spans** (slide count, date markers,
  "Lecture 5+6" titles, agenda slides). This scales the topic count in step 5.

### 4. Merge fragments into the digest

Use `assets/digest-template.md` — fill every section, including the **Figure index**
(every figure worth showing the student again, with exact file + page; the tutor
depends on this to present originals instead of redrawing) and the **Topics
registered** cross-link. Name it `digest-<NN>-<slug>.md` (NN = unit number matching
the established pattern; slug = 2–4 hyphenated lowercase words).

### 5. Register topics in course-state.md

Read `references/topics.md` **before** choosing rows — granularity is the part
that's easy to get wrong. In brief: review-sized themes the student would rate as a
unit (never one row per term), ~3–6 per in-class session of content scaled by step
3's estimate, calibrated against a course-wide budget of roughly 15–40 rows. Append
with fresh sequential IDs, status `new`; match loosely against existing rows to
avoid near-duplicates; leave every existing row byte-identical.

### 6. Deliver

Write the digest and the updated `course-state.md` to `/mnt/user-data/outputs/`,
present both, and remind the student to upload them to the project (and to keep the
raw source file in the project — figure retrieval depends on it). If a study plan
already exists in the state file, note that new topics aren't scheduled yet:
"run uni-plan to fold them in."

---

## Route B — exam-related material → exam-brief.md

1. If `exam-brief.md` doesn't exist yet, create it from
   `assets/exam-brief-template.md`; otherwise merge into the existing one.
2. Extract into its sections, **sourcing every entry**:
   - **Exam facts** — date, duration, format, grading, MC penalties, logistics.
   - **Question archetypes** — one entry per question *type*, with one concrete
     example (verbatim when possible) and the topic IDs it hits (read the state
     file's topic table to map them).
   - **Recurring past-exam tasks** — when a task in this material matches one from
     previously imported exams, say so explicitly with both sources; recurrence is
     the highest-value intelligence in the file. Record exam-task figures with file
     + page so the tutor can present the originals.
   - **Priorities & professor hints** — what was said to matter or not matter.
3. Past-exam PDFs are often figure-heavy: the Route-A triage/raster pipeline
   applies to reading them.
4. **Only update `course-state.md`'s `exam:` header line when the material states
   the upcoming exam's own date/time** (e.g. the professor's announcement). A past
   exam paper is a source of question-style intelligence, not a date to adopt —
   never set the header from a past exam's date. Deliver both files per the
   contract.

---

## Edge cases

- **Re-import of a unit that already has a digest:** replace the digest file (same
  name), but topic rows keep their IDs and statuses — append genuinely new topics,
  and ask before removing any row that no longer matches the material.
- **Material for a unit out of order** (e.g. chapter 7 before 5): fine — number by
  the course's scheme, not by import order.
- **Huge combined script (whole-semester PDF):** import it one unit per run using
  page ranges; ask the student which unit to start with.
