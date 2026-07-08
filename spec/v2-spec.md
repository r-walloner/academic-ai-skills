# Academic AI Skills — v2.0.0 Framework Specification

**Status:** build specification. This document is the single input for the next work step:
writing the six v2 skills. It defines the architecture, the file formats, the shared
contract, and a per-skill build brief. It deliberately does **not** contain the final
SKILL.md texts — those get written from this spec, re-created from scratch rather than
grown out of v1, with v1's proven material carried over where this spec says so.

**Relationship to v1:** v1 (three skills: `lecture-digest`, `study-tutor`,
`assignment-check`) worked well in practice for one semester. v2 is a re-architecture,
not a patch: the work is re-distributed across six single-purpose skills, state is
separated from content, and the shared conventions become an explicit contract instead
of prose repeated in every file. There is **no backward compatibility** with v1 files
and no migration tooling — v2 starts fresh with new courses.

---

## 1. The three use cases (what the framework is for)

Everything in this spec serves three student workflows:

**UC1 — After-lecture study sessions.** A few days after each lecture, run a short
practice session on the new material plus a light spaced recap of older material that
ties in. Goal: solidify knowledge continuously so end-of-semester prep is faster.
Typical composition: `uni-import` (new slides) → `uni-tutor` (practice session).

**UC2 — Assignment work.** While working on an assignment sheet, get grader's-eye
feedback on completed tasks (where would points be lost, what's wrong, what's missing),
invoked repeatedly as tasks get done. Occasionally, ask for a foothold when genuinely
stuck on a task. Skill: `uni-check` (two modes).

**UC3 — Exam prep.** At semester's end, build a study plan informed by exam
intelligence (format, question styles, professor hints, past exams) and the student's
per-topic confidence, then run interactive study sessions against it. In courses where
UC1 was skipped, prep starts with a quick self-assessment so the plan reflects reality.
Typical composition: `uni-import` (exam info / past exams, if not yet imported) →
`uni-plan` (which invokes `uni-assess` when statuses are cold) → repeated `uni-tutor`
sessions.

The framework is **subject-agnostic** throughout: skills infer structure from the
material, never assume a field. (The one field-specific artifact, the CS pitfalls
checklist, is an optional plug-in reference — see §7.6.)

---

## 2. Design principles

These are the rules the skill-writer must apply everywhere. They come from Anthropic's
skill-authoring guidance, the instruction-drift literature, and the observed failure
modes of v1.

**P1 — Do one thing well.** Each skill covers one job with clear inputs and outputs.
Composition happens by running skills in sequence (the user chains them, or one skill
explicitly invokes another as a workflow step). A skill never duplicates a sibling's
job "for convenience."

**P2 — Progressive disclosure.** SKILL.md is a lean main path; detail that is only
needed on some paths lives in `references/` files loaded on demand. Templates live in
`assets/`; deterministic operations live in `scripts/`. Target sizes are given per
skill in §7 — treat them as budgets, not suggestions. Once a SKILL.md is loaded, every
token competes with the conversation; v1's tutor "forgetting" its instructions was
partly a symptom of a 335-line SKILL.md diluting in a long session.

**P3 — State and content never mix.** Course *content* (what is taught) lives in
digests and `exam-brief.md`. Course *state* (what the student knows, what's scheduled)
lives in exactly one file, `course-state.md`, which is small, cheap to regenerate, and
carries hard field-length budgets. The v1 failure to prevent: tracker rows swelling
into mini-digests and the study plan absorbing an exam knowledge base. v2 gives that
valuable content designated homes (§4) so it never needs to squat in state cells.

**P4 — The contract travels with the data.** Skills cannot read each other's folders,
so shared conventions cannot live in a shared library. Instead: every canonical
project file carries a short comment header stating its own editing rules, and the
project instructions block states the file inventory and the global rules. Each
SKILL.md then references the contract in 2–3 lines instead of restating it (v1
restated merge-never-clobber in five places — that's how drift starts). A future
seventh skill learns the conventions by opening the files it will edit.

**P5 — Explain the why; reserve imperatives for fragile steps.** Rules carry a short
reason so the model can generalize to unanticipated cases ("Don't tutor from topic
names alone — you'll invent framings the course never used" beats "ALWAYS read the
digest"). Bare MUST-style imperatives are kept for the few genuinely fragile steps
(file-writing rules, merge rules, the read-only-mount rule).

**P6 — Deterministic where determinism matters.** Page triage, rasterization, and any
repeatable file operation go through bundled scripts (v1's `pdf_triage.py` carries
over). Scripts are run, not read into context.

**P7 — Degrade gracefully.** When a skill wants to invoke a sibling that isn't
installed, it performs a compact inline fallback and tells the user the sibling skill
would do this better. Nothing hard-fails because a skill is missing.

**P8 — Anchor against drift at structural checkpoints.** Long interactive sessions
(the tutor) re-read a compact rules card at natural boundaries (agenda-block
transitions), because models reliably follow "when X happens, do Y" but cannot count
turns, and re-injecting a small anchor restores instruction adherence nearly as well
as a full re-read.

---

## 3. Architecture overview

### 3.1 The six skills

| Skill | One-line job | Reads | Writes |
|---|---|---|---|
| `uni-setup` | Scaffold a course project: instructions block + initial state file | — | `course-state.md` (initial), project-instructions block (to paste) |
| `uni-import` | Import ONE piece of course material into the knowledge base | the uploaded material, existing `course-state.md`, existing digests | a `digest-…` file **or** `exam-brief.md` update; topic rows appended to `course-state.md` |
| `uni-assess` | Quick per-topic confidence self-assessment (minutes, not a session) | `course-state.md` | `course-state.md` (statuses seeded) |
| `uni-plan` | Build/update the exam-prep schedule | `course-state.md`, `exam-brief.md`, digests (exam angles) | schedule section of `course-state.md` |
| `uni-tutor` | Run an interactive study session | `course-state.md`, `exam-brief.md`, digests (full), source PDFs (figures) | `course-state.md` (statuses), `exam-brief.md` (watch-list appends) |
| `uni-check` | Grader's-eye feedback on the student's own assignment work; foothold mode when stuck | sheet + solution, digests/slides for course expectations | — (chat feedback only; no state write-back in v2) |

Naming: the `uni-` prefix groups the family, aids `/uni-…` discovery in the skill
picker, and gives descriptions a shared keyword. All names lowercase-hyphenated,
matching their folder names.

### 3.2 Composition flows

```
UC1 (after a lecture):      uni-import ──► uni-tutor            (uni-check when the sheet is attempted)
UC2 (assignment work):      uni-check (mode A: review) / (mode B: foothold)
UC3 (exam prep):            [uni-import exam info/past exams] ──► uni-plan ──►(invokes)── uni-assess
                                                                     │
                                                          repeated uni-tutor sessions
```

Skill-to-skill invocation is done by instruction inside a SKILL.md ("now use the
`uni-assess` skill to …"); Claude loads the second skill mid-workflow. Every such
invocation point specifies a P7 fallback.

### 3.3 The course project (runtime hub)

One Claude Project per course. Its files are the knowledge base; project files are
mounted **read-only** at `/mnt/project` at runtime. The project holds:

- the canonical files (§4): `course-state.md`, `exam-brief.md`, `digest-*.md`
- the raw source materials: slide decks, scripts, assignment sheets, past exams —
  these **stay in the project permanently**; the tutor pulls original figures from
  them on demand
- the project instructions block (pasted into the Project's custom instructions by the
  user during setup)

The student's loop: skills write updated files to `/mnt/user-data/outputs/`, the
student downloads and re-uploads them to the project. Every skill that writes a
canonical file ends by presenting the file and reminding the user to re-upload it.

---

## 4. The knowledge base: canonical files and formats

Three canonical file types. Fixed names (state, brief) or fixed convention (digests)
so re-uploads line up across runs.

### 4.1 `course-state.md` — the single state file

The **only** file that carries per-student, per-course state: topic registry, mastery
statuses, and the study schedule. One file means one download/re-upload after any
session. Design targets: short (a full course fits in ~60–90 lines), regenerable,
hand-editable, hard content budgets.

Format (the skeleton `uni-setup` generates; comment header abridged here — the full
header text is specified in §6.1):

```markdown
<!-- COURSE STATE FILE — contract v2
Rules for ANY skill or person editing this file:
1. MERGE, NEVER CLOBBER. [full rule text per §6.1]
2. CONTENT BUDGETS. Topic names ≤ 8 words. Notes ≤ 120 characters, plain text.
   Schedule cells contain topic IDs and pointers only — never formulas, definitions,
   question content, or session play-by-play. That material belongs in the digests
   (course content) or exam-brief.md (exam intelligence / personal watch-list).
3. STATUS values: new | weak | ok | strong. "Last" is YYYY-MM-DD, suffix "(self)"
   when the evidence is self-assessment rather than a demonstrated session result.
4. Topic IDs are permanent. Never renumber, reuse, or delete a row without the
   student's explicit confirmation.
-->

# Course State — [course name]

framework: uni-v2
exam: [YYYY-MM-DD HH:MM | — if unknown]   ·   plan-mode: [none | full-prep | sprint]
updated: [YYYY-MM-DD]

## Topics

| ID | Unit | Topic | Status | Last | Note |
|----|------|-------|--------|------|------|
| T01 | Ch.1 | [short examinable theme] | new | — | |

## Schedule
_(section absent until uni-plan writes it)_

| Date | Block | Topics | Focus |
|------|-------|--------|-------|
| Jun 25 AM | ~1.5h | T04 T16 | T04 second pass · T16 first pass · see exam-brief §archetypes |

**Sprint tiers** _(sprint mode only)_: must-cover: T…, T… · worth-a-look: T… ·
accept-risk (explicitly deprioritized): T…
```

Field semantics:

- **ID** — `T` + two-digit sequence, assigned by `uni-import` at import time,
  permanent for the course's lifetime. Everything else (schedule, sessions, chat)
  refers to topics by ID. This is the mechanism that keeps content out of the
  schedule: a schedule cell that may only hold IDs cannot swell.
- **Unit** — the course's own structural unit (chapter, lecture, week — whatever the
  course uses; see §7.2 on unit detection).
- **Topic** — a review-sized examinable theme, ≤ 8 words. The granularity rule
  (v1's most valuable lesson, preserved): a row is something the student would rate
  as a unit and a session would spend real time on — **not** one row per defined
  term. ~3–6 per in-class lecture of content, calibrated to the course (§7.2).
- **Status / Last** — mastery record. `(self)` suffix distinguishes self-assessed
  from session-demonstrated evidence; `uni-plan` uses this for its overconfidence
  check, and `uni-tutor` treats `(self)`-strong topics with mild suspicion.
- **Note** — ≤ 120 chars, e.g. an open question or "split from T07". A trap the
  student keeps falling into does NOT go here — it goes to the exam-brief watch-list.

### 4.2 `exam-brief.md` — exam intelligence + personal watch-list

The designated home for everything v1 had no home for — the content that colonized
the v1 tracker and plan. Semi-stable course-specific intelligence about *the exam*,
plus the student's personal error patterns. Created on first import of exam-related
material (not by `uni-setup` — no empty boilerplate files).

```markdown
<!-- EXAM BRIEF — contract v2
Written by uni-import (exam info, past exams, assignment-sheet style notes) and
uni-plan (synthesis, priorities). uni-tutor APPENDS to §Watch-list only.
Merge, never clobber: preserve existing entries; append and update with sources.
Keep entries compact and sourced ("Oct 2025 exam", "prof, last lecture").
-->

# Exam Brief — [course name]

## Exam facts
| | |
|--|--|
| Date/time | … |
| Format | e.g. closed-book, 60 min, MC + open, negative MC points |
| Grading | … |
| Logistics | registration, location |

## Question archetypes
One entry per recurring question *type*: what it looks like, one concrete example
(lecturer example verbatim if available), source, and which topic IDs it hits.
- **[Archetype name]** (hits T04, T09) — [description]. Example: "[…]" (source: Jun 2024 exam)

## Recurring past-exam tasks
High-value specifics: tasks that appeared in multiple past exams, with the known
answer sketch and source. (This is where v1's "the exact LSTS task set appeared in
Sep 2021 AND Oct 2025" intelligence belongs.)

## Priorities & professor hints
What the professor said matters / doesn't; student-stated priorities (e.g. "in-class
formal syntax over real-world syntax"). Sourced.

## Watch-list (personal traps — uni-tutor appends here)
Dated, 1–2 lines each, most recent last. E.g.:
- 2026-06-28 · T17 · MC trap fired twice: "Lamport helps detect causality" is wrong — reject on sight.
- 2026-06-25 · T04 · Break-even sign error is a persistent pattern: −(T_sd+T_wu)·P_s, always subtract.
```

Read by `uni-plan` (weighting, archetypes) and `uni-tutor` (question style
calibration, watch-list drilling). `uni-check` may consult §archetypes when judging
style, but never writes.

### 4.3 Digest files — `digest-<NN>-<slug>.md`

One per imported unit of lecture material. Format carries over from v1's template
with two additions. Sections:

1. **Title & source** — unit title, source filename, page range, import date.
2. **Core concepts** — key terms, 1–3 sentence definitions, lecturer's own wording.
3. **Key relationships / processes** — how concepts connect; diagrams *described* in
   words with a pointer to the figure index entry.
4. **Formulas, algorithms, theorems, proofs** — short ones reproduced precisely
   (using the math conventions of §6.3); long derivations summarized with a pointer
   to the exact slides.
5. **Likely exam angles** — 3–6 bullets predicting question *types*; lecturer-provided
   example questions captured **verbatim** and marked `(lecturer example)` — v1's
   strongest-signal rule, preserved.
6. **Open questions** — genuine gaps only.
7. **Figure index** *(new)* — every figure worth ever showing the student again, one
   line each: `F1 · [what it shows, ≤ 10 words] · source: <filename> p.<N>`. This is
   what lets `uni-tutor` retrieve and present the *original* image in one command
   instead of describing or (worse) regenerating it.
8. **Topics registered** *(new)* — one line: `Topics: T07–T10 (see course-state.md)`.
   Cross-link for traceability; the state file remains the registry of record.

Naming: `digest-<NN>-<slug>.md` — NN = two-digit unit number in the course's own
unit scheme; slug = 2–4 lowercase hyphenated words. Before naming, list existing
`digest-*` files and match the established pattern; only the first digest sets it.
Re-importing a unit that already has a digest replaces the digest file (same name)
but **preserves** existing topic rows/statuses in the state file, appending only
genuinely new topics and asking before removing any.

### 4.4 What is deliberately NOT a file anymore

- **`topic-tracker.md`** — replaced by the Topics section of `course-state.md`.
- **`study-plan.md`** — replaced by the Schedule section of `course-state.md`.
- **`learning-profile.md`** — dropped. In practice the tutor rarely read it and
  sessions worked without it; per-course traps now live in the exam-brief watch-list.

---

## 5. Where v1 content goes (traceability map)

The skill-writer should mine these v1 sources — preserving the *spirit and the proven
details*, re-writing the text:

| v1 source | v2 destination |
|---|---|
| `lecture-digest/SKILL.md` §Digesting one lecture (triage → sub-batches → fragments → merge) | `uni-import` SKILL.md main flow |
| `lecture-digest/scripts/pdf_triage.py` | `uni-import/scripts/pdf_triage.py`, unchanged code |
| `lecture-digest/references/course-files.md` granularity rule + worked example | `uni-import/references/topics.md` (and a 1-line version in the state-file header) |
| `lecture-digest/references/study-plan.md` (modes, cold start, sprint triage) | `uni-plan` SKILL.md + its reference |
| `lecture-digest/assets/digest-template.md` | `uni-import/assets/digest-template.md`, + Figure index + Topics registered sections |
| `lecture-digest/assets/project-instructions.md` | `uni-setup/assets/project-instructions.md`, re-written for six skills |
| `study-tutor/SKILL.md`: read-material-first · locate-the-student · one-step-per-turn · impatient-vs-stuck · modes · propose-don't-impose · pausing-vs-finishing · tight replies · grading & calibration | `uni-tutor`: rules card distills the always-on essence; SKILL.md keeps the session flow; the long-form pedagogy moves to `references/` (§7.5) |
| `assignment-check/SKILL.md`: verify-don't-vibe-check · severity tiers · right-answer-≠-complete-answer · severity calibration · report format · tone | `uni-check` SKILL.md (mode A) |
| `assignment-check/references/cs-pitfalls.md` | `uni-check/references/pitfalls-cs.md`, unchanged content, made an optional plug-in (§7.6) |
| v1 tracker/plan *example files* (the state/content bleed) | negative examples informing §4.1 budgets and §4.2 sections — the exam-format table, archetypes, recurring tasks, and trap notes in those files show exactly what exam-brief.md must be able to hold |

---

## 6. The framework contract (cross-cutting rules)

These rules bind every skill. They are implemented as: (a) the self-describing file
headers of §4, (b) a short **Contract** block near the top of every SKILL.md —
maximum ~10 lines, phrased once, never restated elsewhere in the skill — and (c) the
project instructions block. The full texts below are normative.

### 6.1 File handling (fixes v1's wasted cycles)

> **Project and upload files are read-only.** `/mnt/project`, `/mnt/user-data/uploads`
> and `/mnt/skills` cannot be edited in place — do not try. To update a canonical
> file: read the current version (search `/mnt/project` first, then uploads, then
> conversation context), build the updated content, and write it **directly** to
> `/mnt/user-data/outputs/<same-filename>`. Present every written file and remind the
> student to re-upload it to the project so the next run starts from current state.

> **Merge, never clobber.** Canonical files carry the student's own data across runs.
> Read the existing version first; preserve every row, status, date, and note; change
> only cells you have fresh evidence for; append new entries rather than regenerating
> sections. If no existing version can be found anywhere, say so explicitly before
> creating a fresh one (a silent fresh start destroys a semester of state if the
> student simply forgot to upload).

### 6.2 State hygiene

> Content lives in digests and `exam-brief.md`; state lives in `course-state.md` and
> respects its budgets (topic ≤ 8 words, note ≤ 120 chars, schedule cells = IDs +
> pointers only). When you catch yourself writing a formula, definition, question
> text, or session narrative into `course-state.md`, stop — that content has a home:
> course knowledge → digest; exam intelligence or a personal trap → `exam-brief.md`.

### 6.3 Mathematical notation (output to the student)

> When showing mathematics to the student, use LaTeX with `$$…$$` delimiters for
> anything that matters (display it on its own line). Avoid single-`$` inline math and
> `\(…\)` delimiters — they fail to render on several Claude surfaces and show raw
> markup. Never put math inside backticks or code fences (it will never render).
> Keep LaTeX simple (fractions, subscripts, standard operators); for a short inline
> symbol where display math would be clumsy, prefer clean unicode (`T_be`, `V_dd`,
> `⊨`) over inline LaTeX. Digests and state files may use compact unicode notation
> freely — the rendering rule is about what the *student is shown in chat*.

### 6.4 Original figures over descriptions

> When a figure, diagram, or exam-task image matters to the discussion, retrieve the
> **original** from the source material and present it as-is (rasterize the page from
> the PDF in the project; the digest's Figure index says which file and page). Do not
> describe an image the student could be shown, and never attempt to regenerate or
> redraw a diagram — a redrawn diagram teaches the wrong picture.

### 6.5 Miscellany

- Subject-agnostic: infer structure from material; never assume a field.
- Every canonical file the framework writes states `framework: uni-v2` (state file)
  or `contract v2` (headers) so future versions can detect the format.
- Skills stay scoped: no skill overrides global behavior or another skill's job.
- Tone with the student: honest, specific, warm; no flattery; find weak spots before
  the exam does (v1's line, kept as the framework's voice).

---

## 7. Per-skill build briefs

Each brief: purpose · frontmatter description draft · workflow · bundled files ·
size budget · v1 carry-over · edge cases. Descriptions are drafts to refine at build
time; keep them "pushy" (skills under-trigger) with explicit positive triggers and
DO-NOTs, under 1024 chars.

### 7.1 `uni-setup`

**Purpose:** scaffold a new course project in one run: hand over the project
instructions block, generate the initial `course-state.md`, explain the loop.

**Description draft:** "Set up a new Claude Project for a university course using the
uni- study framework (v2). Use when a student starts a new course, says 'set up this
course', 'create a course project', 'initialize the study framework', or asks how to
begin using the uni- skills for a class. Produces the project-instructions block to
paste into the Project and the initial course-state.md to upload. Do NOT use for
importing lecture material (uni-import) or planning (uni-plan)."

**Workflow:**
1. Ask (once, together): course name, and exam date if already known. Nothing else.
2. Generate `course-state.md` from the template: header filled, empty Topics table,
   no Schedule section. Write to outputs.
3. Hand over `assets/project-instructions.md` **verbatim** as a copy-paste block
   (it is static — same text for every course).
4. Close with a compact "what happens next": upload the state file to the project,
   paste the instructions, then run `uni-import` on the first lecture material. Note
   that raw slide decks / sheets / past exams should be uploaded to the project and
   *kept* there — the tutor pulls original figures from them.

**Bundled files:** `assets/course-state-template.md` (the §4.1 skeleton, including
the full contract header), `assets/project-instructions.md` (§8).

**Budget:** SKILL.md ≤ 60 lines. No references needed.

**Edge cases:** invoked in a project that already has a `course-state.md` → do not
regenerate; point the user at what exists and offer the instructions block only.

### 7.2 `uni-import`

**Purpose:** the single door into the knowledge base. Takes ONE uploaded piece of
course material per run, detects its type, and routes it: lecture material → a digest
+ topic registration; exam-related material → `exam-brief.md` update.

**Description draft:** "Import ONE piece of university course material into the
uni- framework knowledge base: lecture slides, scripts, or notes (→ a compact digest +
topic registration), or past exams, exam announcements, and professor exam hints
(→ exam-brief update). Use whenever a student uploads course material and wants it
digested, summarized, condensed, imported, or added to their course project — also
'summarize these slides', 'add this lecture', 'here's a past exam', 'the prof told us
about the exam'. One file per run. Do NOT use for study sessions (uni-tutor), planning
(uni-plan), or reviewing the student's own solutions (uni-check)."

**Workflow — route by material type first:**

*A. Lecture material* (slides, script, notes, transcript) — the v1 pipeline, kept:
1. One file per run; if several uploaded, do one and say re-invoke.
2. Cheap-first extraction: `scripts/pdf_triage.py triage` for PDFs (structural
   vector-path/image-area signals, not char counts — keep v1's reasoning in a short
   form); direct text reading for docx/md/txt. Scanned PDFs → all-visual note.
3. Sub-batches of ~20–30 pages; rasterize only flagged/judged pages
   (`pdf_triage.py raster`); write a fragment per sub-batch to `/home/claude`.
4. Merge fragments into the digest per `assets/digest-template.md` (§4.3, including
   Figure index and Topics registered). While reading, watch for lecturer-provided
   example questions (capture verbatim) — and if any pages carry exam logistics or
   format info (common in first/last lectures), route those to `exam-brief.md` too,
   in the same run.
5. **Unit & scale detection:** infer the course's structural unit from the material
   itself (chapter, lecture, week) and estimate how many in-class sessions it spans
   (slide count, date markers, "Lecture 5+6" titles, agenda slides). Number the
   digest in the course's own scheme.
6. **Topic registration:** derive trackable topics and append them to
   `course-state.md` as `new` rows with fresh sequential IDs. Granularity: the v1
   rule verbatim in spirit — review-sized themes the student would rate as a unit,
   ~3–6 per in-class session of content, scaled by the multi-session estimate, and
   calibrated against a **course-wide budget of roughly 15–40 topics**: a course
   with 4 fat chapters gets more topics per chapter than one with 15 thin ones.
   When unsure, go coarser (splitting later is easy). Match loosely against existing
   rows to avoid near-duplicates. Full guidance + v1's worked example (the ~20-term
   KR lecture collapsing to ~6 rows) in `references/topics.md`.
7. Write digest + updated state file to outputs, present both, remind re-upload.

*B. Exam-related material* (past exam, exam announcement, professor hints relayed by
the student, assignment sheet offered explicitly as a question-style anchor):
1. Create `exam-brief.md` from `assets/exam-brief-template.md` if absent, else merge.
2. Extract into the brief's sections: facts; question archetypes (typed, with one
   example each, mapped to topic IDs where identifiable); recurring tasks (when the
   same task appears across past exams, say so explicitly with sources — this is the
   highest-value intelligence there is); priorities/hints.
3. For past-exam PDFs, the triage/raster pipeline applies (exam sheets are often
   figure-heavy); capture task figures in a small figure index inside the brief so
   the tutor can present original exam figures.
4. Write, present, remind re-upload.

**Bundled files:** `scripts/pdf_triage.py` (v1 code unchanged);
`assets/digest-template.md`; `assets/exam-brief-template.md`;
`references/topics.md` (granularity + worked example); `references/pdf-notes.md`
(the longer triage-interpretation guidance from v1 — most-pages-flagged,
nothing-flagged, scanned, poppler-fallback cases — moved out of the main path).

**Budget:** SKILL.md ≤ 140 lines; the two references carry the depth.

**Edge cases:** no `course-state.md` found anywhere → say so, offer to run
`uni-setup` (invoke if user agrees; P7 fallback: create a fresh state file inline).
Re-import of an existing unit → §4.3 rule. Material arrives after a plan exists →
register topics as `new` and note "run uni-plan to fold new topics into the
schedule." Ambiguous type (e.g. a sheet with both content and exam info) → do both
routes in one run, saying so.

### 7.3 `uni-assess`

**Purpose:** a minutes-long self-assessment pass that seeds statuses, so plans and
sessions start from something real instead of a wall of `new`. Standalone (run
anytime) and invokable by `uni-plan`.

**Description draft:** "Quick self-assessment of a student's confidence per course
topic in the uni- framework: presents the topic list from course-state.md grouped by
unit, collects low/medium/high ratings in one or two batches, and seeds the status
column. Takes a few minutes, not a study session. Use when a student says 'self
assessment', 'rate my confidence', 'I don't know where I stand', when starting exam
prep for a course with no session history, or when another uni- skill needs statuses
seeded. Do NOT use for actual tutoring or quizzing (uni-tutor) — this collects the
student's own ratings, it does not verify them."

**Workflow:**
1. Read `course-state.md`. If every topic already has session-verified status, ask
   whether re-assessment is really wanted.
2. Present topics grouped by unit, compactly (ID + name), and ask for ratings in
   batch form — explicitly invite shorthand ("T01 h, T02 m, T03–T05 l" or per-unit
   "Ch.2: all medium except T07 low"). One or two exchanges total; this must feel
   like a 3-minute form, not a conversation.
3. Map low→`weak`, medium→`ok`, high→`strong`; write date with `(self)` suffix.
   Never downgrade a session-verified status on the basis of a self-rating without
   asking (self-report is weaker evidence than demonstration).
4. Write, present, remind re-upload. One line of orientation ("8 weak, 9 ok, 4
   strong — a plan or session can start from this"), nothing more.

**Bundled files:** none.

**Budget:** SKILL.md ≤ 50 lines. This skill's virtue is smallness.

**Edge cases:** empty topic table → nothing to assess; point to `uni-import`.
Student volunteers commentary mid-rating ("T07 low because I never got recursion") →
capture as a ≤ 120-char note, keep moving.

### 7.4 `uni-plan`

**Purpose:** build or update the exam-prep schedule in `course-state.md`, informed by
exam intelligence, real time availability, and honest statuses.

**Description draft:** "Build or update an exam study plan (schedule) for a course in
the uni- framework. Use when a student mentions an exam date, says 'make me a study
plan', 'plan my revision', 'I have an exam on …', 'I'm behind, help me catch up', or
wants the schedule updated after missed days or new material. Reads course-state.md,
exam-brief.md, and digests; asks for exam date and available study time; writes the
schedule into course-state.md. Invokes uni-assess first when statuses are cold. Do NOT
use for running the actual study sessions (uni-tutor) or importing exam info
(uni-import — run that first if the professor's exam details aren't imported yet)."

**Workflow:**
1. **Inputs.** Read `course-state.md`. Then, in one message, ask for: exam date (if
   not in the state header), and the available study days **with rough hours per
   day** ("18th almost full day −3h" style input is expected and fine).
2. **Exam intelligence gate.** Look for `exam-brief.md`. If missing or thin: tell
   the student that plans built on exam intelligence are much better targeted, and
   prompt them to run `uni-import` on whatever they have (past exams, the
   professor's exam-info slides, notes from the last lecture) — offer to pause here.
   If they have nothing, proceed and say the plan weights on digest exam-angles only.
3. **Status gate.** If statuses are cold (mostly `new`) or stale (last-reviewed long
   ago given the semester), invoke the **`uni-assess`** skill now. P7 fallback: run
   the batch-rating inline. Statuses that are `strong (self)` get flagged for an
   early verification pass in the plan (overconfidence check — v1 rule, kept).
4. **Mode.** Full-prep vs sprint by honest arithmetic on topics × hours available
   (v1's heuristic kept: if every topic can't get a real slot plus a second look at
   weak ones, it's a sprint). State the choice and the arithmetic in one line.
5. **Weighting.** Topic value = exam-brief archetypes/recurring-tasks it appears in
   (strongest signal) + digest "likely exam angles" density + status. The user's
   established strategy is the default and should be encoded: **front-load
   high-value topics** so a second pass is possible, push low-reward topics to the
   later days, and in sprint mode name all three tiers explicitly — must-cover /
   worth-a-look / accept-risk — so deprioritization is an informed bet, never
   silent (v1 rule, kept). Sprint cold-start also keeps v1's quick recall diagnostic
   idea: schedule a short verification of self-rated-strong topics early.
6. **Write.** Schedule section of `course-state.md` per §4.1: dated blocks with hour
   estimates, topic IDs, terse focus pointers. Also update the state header
   (`exam:`, `plan-mode:`). Any newly learned exam facts or priorities go to
   `exam-brief.md`, not the schedule. Write, present, remind re-upload.
7. **Re-planning** (invoked when days were missed or new topics arrived): fold
   reality in — completed blocks stay as history (mark done/missed tersely),
   remaining topics redistribute over remaining time. Never regenerate the topic
   table.

**Bundled files:** `references/planning.md` — the mode arithmetic, weighting detail,
and re-planning rules; SKILL.md keeps the flow and gates.

**Budget:** SKILL.md ≤ 110 lines + one reference.

**Edge cases:** no exam date known and student doesn't have one → offer a
rolling-recap pseudo-plan or defer; don't fabricate urgency. Exam already very close
(≤ 2 days) → sprint with triage, and say plainly what accept-risk means this close.

### 7.5 `uni-tutor`

**Purpose:** interactive study sessions — both UC1 after-lecture recap sessions and
UC3 exam-prep sessions. The largest skill; the one that must survive long contexts.

**Description draft:** "Run an interactive study/tutoring session against a course
knowledge base built with the uni- framework (digests, course-state.md,
exam-brief.md). Use whenever a student wants to be quizzed, drilled, tutored, or
mock-examined: 'quiz me', 'study session', 'let's practice lecture 4', 'mock exam',
'revise topic X', 'drill my weak topics', 'test me before the exam'. Works with or
without a study plan: with one it follows the schedule; without one it defaults to
practicing the newest material plus spaced recap of related older topics. Do NOT use
for importing material (uni-import), building the plan (uni-plan), or checking the
student's own assignment solutions (uni-check)."

**Structure of the SKILL.md — this is the anti-drift design:**

- **Session Rules Card** — the first section, ≤ 15 lines, clearly delimited. The
  distilled always-on rules: ground every question in the digests (re-open them when
  unsure — never tutor from topic names or memory); one focused question + one small
  scaffold per turn, never a wall of questions; don't cave to impatience, do give
  footholds to the genuinely stuck; confirm correct answers in a few words and spend
  the turn on what's new; math per contract (`$$…$$`, never single-`$`, never in
  backticks); figures per contract (present originals, never redraw); propose
  transitions at block boundaries, don't impose them; honest statuses — evidence
  over optimism.
- **Re-anchoring instruction**, immediately after the card: *at every agenda-block
  boundary (a topic wraps, a drill set ends, the student returns from a tangent or a
  pause), re-read the Session Rules Card from this skill's SKILL.md file (under
  `/mnt/skills/`) before proceeding. In a long session your adherence to these rules
  decays without you noticing; the re-read is cheap and the boundary is the natural
  moment.* Boundary-triggered, not turn-counted, deliberately.
- **Main flow** (compact): session start → main block → boundaries → end.
- **references/** for the long-form pedagogy, loaded once per session at start or
  when the situation arises: `references/pedagogy.md` (locate-the-student before
  drilling; impatient-vs-stuck diagnosis with v1's full treatment; the four
  modes — explain-it-back, mock-exam, teach-it-to-Claude, adversarial-only-when-
  strong; parallel-worked-example scaffolding; hint-that's-really-the-answer
  warning), `references/session-shapes.md` (no-plan default session; extra-practice
  when the agenda's done early; pausing vs finishing with v1's full rules).

**Main flow spec:**

1. **Session start.** Read `course-state.md`; detect situation: plan exists →
   surface today's slice and on-track/behind; no plan (UC1) → default session =
   newest-digest topics + 1–2 related older topics due for spaced recap (pick by
   status + last-reviewed + thematic ties). Read `exam-brief.md` if present
   (question archetypes calibrate everything; watch-list items for today's topics
   get deliberately drilled). **Read the full digest files for today's topics — the
   whole file, not a project search snippet;** this is a hard rule (v1's biggest
   observed failure was skipping it). Then a 2–4 question recall warm-up, then a
   one-line agenda with minute estimates the student can redirect before time is
   sunk (v1 format kept: `topic ~Nm · topic ~Nm — total ~N`).
2. **Main block.** Mode per topic (from pedagogy reference), announce the mode, vary
   modes. Question style: lecturer examples and exam-brief archetypes are the
   template when they exist; otherwise ask the exam format once. Mid-session
   unknowns → back to the digest, and to the original slides when the digest points
   there. Figures: when a diagram or past-exam figure is the subject, rasterize the
   source page (digest/brief figure index → file + page) and present the original
   image. Tangents: one-line answer if quick, then steer back; anything deferred
   becomes a ≤ 120-char note in the state file.
3. **Boundaries.** v1's propose-don't-impose, kept whole: name the block done, offer
   1–2 *targeted* extra reps, show the refreshed one-line remaining agenda with
   time, advance only on confirmation. **This is also the re-anchoring checkpoint.**
4. **Session end (and pause).** Update `course-state.md`: statuses for topics
   actually covered (evidence-based, today's date, no `(self)` suffix — this is
   demonstrated evidence), untouched topics stay untouched; new traps observed →
   append dated watch-list lines to `exam-brief.md`. Write file(s) to outputs — never
   inline code blocks — present, remind re-upload. Pause ≠ finish: v1's rule kept
   (pause = resuming later today; update only what was covered; don't redistribute
   the plan; hand off with a one-line "still to do today").

**Bundled files:** `references/pedagogy.md`, `references/session-shapes.md`.

**Budget:** SKILL.md ≤ 150 lines including the rules card; each reference ≤ 120
lines. (v1 was a 335-line monolith; the split is the point.)

**Edge cases:** no digests at all → point to `uni-import`, don't improvise a session
from raw slides. Asked to check an assignment solution mid-session → that's
`uni-check`; offer to switch. Digest thin/missing for a scheduled topic → say so,
offer to work from original slides for this session and suggest a re-import.

### 7.6 `uni-check`

**Purpose:** grader's-eye feedback on the student's own attempted assignment work
(mode A), and a tutoring-style foothold when genuinely stuck on a task (mode B).

**Description draft:** "Review a student's OWN attempted assignment solutions like a
sharp TA: verify correctness, flag where a grader would deduct points, sorted by
severity — or, in foothold mode, give a genuinely stuck student a starting point on a
task without solving it. Use when a student supplies an assignment/problem sheet with
their worked solution and asks 'check my solution', 'did I get this right', 'where
would I lose points', 'is my proof correct', 'grade my attempt' — invoked repeatedly
while working through a sheet — or when they say they're stuck on a task and need a
hint or a place to start. Reviews the student's own work for learning (not a
plagiarism concern). Do NOT write solutions to unattempted tasks, and do NOT use for
general study sessions (uni-tutor)."

**Mode A — grader review.** v1's core, preserved with its teeth:
1. **Gather:** sheet + solution required; before asking, check `/mnt/project` and
   uploads — the sheet and slides usually live in the project. Pull in the relevant
   digests and slide decks as the course's frame: methods, notation, definitions
   being tested (state this project-context step explicitly — it was implicit in v1
   and got skipped).
2. **Read the sheet like a grader wrote it:** precise ask per sub-task; rubric cues;
   point values anchor proportion.
3. **Map** attempted vs unattempted; unattempted tasks are only ever a one-line
   closing note.
4. **Verify, don't vibe-check** (v1 text mined heavily): work problems independently
   first; check proofs step-wise; trace algorithms on small + adversarial inputs;
   re-derive complexity; run runnable code with edge cases; flag uncertainty plainly
   — calibration is the product. Severity tiers kept: Wrong / Likely deduction /
   Correct-but-presentation. Kept rules: right answer ≠ complete answer (the
   derivation is the graded object; check the work starts where the hint said);
   severity calibrated to the task's bar, not the reviewer's strictness; corrections
   explain enough to fix, never hand over the rewritten solution by default.
5. **Report compactly:** one-line overall read → per-task verdict labels with
   specifics only where there's something to say → one-line missing-tasks note. No
   padding, no restating the assignment, no closing summary.
6. If exam-brief archetypes exist, a task matching a known archetype may be noted
   ("this is the Type-A trace style from the past exams") — one line, no more.

**Mode B — foothold (new).** Triggered by "I'm stuck", "I don't know how to start",
"give me a hint" on a specific task:
1. Confirm what they've tried (their partial attempt or dead ends — a sentence, not
   an interrogation). Pull the relevant digest/slides to anchor in the course's
   method.
2. Give a **foothold, not the summit**: name the technique the course expects, or do
   the first step, or work a *parallel* example and have them apply it — then hand
   the wheel back. One foothold per exchange; escalate gradually if still stuck.
   Never produce the task's solution; the impatient-vs-stuck distinction from tutor
   pedagogy applies (a deadline stated up front is a real constraint; one that
   appears after pushback usually isn't).
3. No state write-back, no report format — this mode is conversational.

**Bundled files:** `references/pitfalls-cs.md` (v1 content, unchanged) — reframed as
a **plug-in**: SKILL.md says "consult a `pitfalls-*.md` reference matching the
course's field for a second pass, if one exists" — so users extend the framework by
dropping in `pitfalls-law.md` or `pitfalls-medicine.md` without touching SKILL.md.
The SKILL.md itself stays subject-agnostic (v1's "the field is CS at master's level"
line is removed).

**Budget:** SKILL.md ≤ 130 lines + the pitfalls plug-in(s).

**Edge cases:** solution supplied with no sheet findable anywhere → one brief
question, never guess the assignment. Handwritten-scan solutions → read visually
(rasterize if PDF). Repeated invocation on the same sheet → don't re-review
unchanged tasks; diff against what was said before.

---

## 8. The project instructions block (`uni-setup/assets/project-instructions.md`)

Static, identical for every course, pasted once into the Project's custom
instructions. Target < 4500 characters. Contents, in order:

1. **What this project is** — one course's knowledge base — and the file inventory
   in one line each: digests (content source of truth), `exam-brief.md` (exam
   intelligence + personal watch-list), `course-state.md` (the ONLY state file:
   topics, statuses, schedule), plus raw materials kept for figure retrieval.
2. **The two global rules,** stated once: merge-never-clobber with re-upload
   reminder; state hygiene (budgets; content goes to digests/brief, never into
   state).
3. **Routing table** — read what the student is actually asking, don't assume
   tutoring: study/quiz/practice → `uni-tutor` skill; import/summarize material or
   exam info → `uni-import`; plan/exam date/catching up → `uni-plan`; rate my
   confidence → `uni-assess`; check my own solution / stuck on a task → `uni-check`;
   quick content question → answer straight from the digests, pointing to the source
   lecture. Each routing line carries a one-clause fallback ("if the skill isn't
   installed: <two-line inline behavior>") so the project degrades gracefully — but
   fallbacks stay drastically compact; the skills are the real implementations.
4. **Voice:** subject-agnostic; honest and specific, not flattering.

The v1 block is the model for tone and compression; it gets re-written for the
six-skill routing and the v2 file inventory.

---

## 9. Packaging

```
academic-ai-skills-2.0.0/
├── README.md
├── LICENSE                      # CC BY-NC-SA 4.0, unchanged
└── skills/
    ├── uni-setup/    (SKILL.md, assets/course-state-template.md, assets/project-instructions.md)
    ├── uni-import/   (SKILL.md, scripts/pdf_triage.py, assets/digest-template.md,
    │                  assets/exam-brief-template.md, references/topics.md, references/pdf-notes.md)
    ├── uni-assess/   (SKILL.md)
    ├── uni-plan/     (SKILL.md, references/planning.md)
    ├── uni-tutor/    (SKILL.md, references/pedagogy.md, references/session-shapes.md)
    └── uni-check/    (SKILL.md, references/pitfalls-cs.md)
```

**README.md** (re-written): the three use cases with their skill compositions; the
six-skill table; the knowledge-base file inventory with the state/content split
explained; the setup walkthrough (create project → uni-setup → paste + upload →
uni-import per unit); the re-upload loop explained once, prominently; the
extendability story (add a skill: read the file headers for the contract; add a
pitfalls plug-in for a new field); a model/effort recommendation table in the spirit
of v1's (import = mid-effort, plan = highest reasoning, tutor = high first message
then mid, check = high when verifying proofs) phrased generically so it survives
model renames. No migration section — v2 states plainly that it starts fresh.

---

## 10. Acceptance scenarios (verify each skill against these when built)

1. **Setup:** fresh chat, "set up my Embedded Systems course, exam June 30" → one
   run produces a pasteable block + a valid `course-state.md` with filled header and
   empty topic table; no other files.
2. **Import, lecture:** a 60-page chapter deck spanning ~3 in-class lectures → one
   digest numbered in the course's scheme, figure index present, ~8–14 topics (not
   20+, not 4) appended as `new` with fresh IDs; existing rows byte-identical; no
   in-place edit attempt on `/mnt/project` (the v1 wasted-cycle log must not appear).
3. **Import, past exam:** a past-exam PDF → `exam-brief.md` created/merged with
   archetypes mapped to topic IDs and a recurring-task entry when it matches an
   earlier import; `course-state.md` is left untouched.
4. **Assess:** 21 topics, all `new` → batch rating completes in ≤ 2 user replies;
   statuses seeded with `(self)` dates; a session-verified `ok` from earlier is not
   downgraded without asking.
5. **Plan:** "exam on the 24th, I have the 16th, 18th (−3h), 19th, 22nd, 24th
   morning" → asks nothing already answered; prompts about missing exam-brief;
   invokes uni-assess on cold statuses; produces a Schedule section whose cells
   contain only IDs/hours/pointers; front-loads high-value topics; sprint tiers
   named including accept-risk.
6. **Tutor, UC1 (no plan):** after an import, "let's practice" → reads the full new
   digest before the first question; agenda = new topics + 1–2 recap topics; at the
   first block boundary the rules card is demonstrably re-read; session end updates
   only covered topics and delivers the state file as a downloadable file.
7. **Tutor, figures:** "show me that pipeline diagram from the slides" → the
   original page is rasterized and presented; no textual re-description substitutes,
   no redrawn diagram.
8. **Tutor, math:** formulas shown as `$$…$$` display math; no single-`$` inline
   math, none in backticks.
9. **Check, mode A:** sheet in project + solution uploaded → pulls sheet and
   relevant digest from the project unprompted; verdict-labeled per-task report;
   correct tasks get one line; unattempted tasks only listed, never solved.
10. **Check, mode B:** "I'm completely stuck on task 3" → asks what they tried,
    gives one course-anchored foothold, does not solve the task even under "just
    tell me" pushback without the genuine-stuck signals.
11. **Contract, everywhere:** any skill updating a canonical file writes to
    `/mnt/user-data/outputs/` directly, presents it, reminds re-upload; a
    hand-entered note in the state file survives every skill's touch verbatim.

— end of specification —
