# Registering topics in course-state.md

Read this before deciding a unit's topic rows. Granularity is the thing most worth
getting right in an import: it determines whether the state file is a usable review
index or a useless wall.

## What a topic row is

A row is a **review-sized chunk the student would rate as a unit** — something a
study session spends real time on and the student can meaningfully say "weak" or
"strong" about. It is **not** a glossary entry. The digest already stores every term
and definition; the topic table is the *review index over* the digest, not a second
copy of it.

Operational test: *would the student plausibly rate their confidence in this
separately, and would a study session spend a real block of time on it?* A single
definition covered in two minutes belongs inside a topic, not as its own row.

## How many rows

Two dials, applied together:

1. **Per in-class session of content: ~3–6** for a broad session, as few as 1–2 for a
   tightly focused one. If the imported material spans several in-class sessions
   (see unit detection in SKILL.md), scale accordingly — a chapter deck covering ~3
   lectures lands around 8–14 topics, not 4 and not 20.
2. **Course-wide budget: roughly 15–40 topics total.** Courses package the same
   amount of content very differently — one course has 4 fat chapters, another has
   15 thin ones. Calibrate each import against the whole: with 4 chapters, each
   chapter carries more rows; with 15, each carries fewer. Check how many rows exist
   already and how much of the course remains.

When unsure, go **coarser**: the student (or the tutor, mid-session) can split a row
later when it turns out to hide two differently-rated things — that's cheap. Wading
through a glossary-shaped tracker all semester is not.

## Worked example

A broad first lecture on knowledge representation with ~20 digest terms (entailment
vs provability, vocabulary Σ, terms vs wffs, free/bound variables, interpretations,
satisfaction, reification, deduction/induction/abduction, situation calculus,
temporal reasoning, resolution, TPTP/Vampire, undecidability of FOL, LLMs vs symbolic
reasoning, …) collapses to about six rows:

- KR&R foundations & logical entailment (⊨ vs ⊢)
- First-order logic: syntax, semantics, formalization
- Inference: reasoning modes, resolution, (un)decidability
- Situation & temporal calculus
- Automated theorem proving in practice (TPTP/Vampire)
- LLMs vs symbolic reasoning

Six rows, not twenty. Fewer would also be fine.

## Appending procedure (every lecture-material import)

1. Read the existing `course-state.md` topic table.
2. Derive the unit's topics from the digest's structure and the lecturer's own
   sectioning — group fine-grained terms under their parent theme.
3. Match each candidate **loosely** against existing rows (same theme under
   different wording = same row; don't create near-duplicates). A genuinely new
   facet of an existing topic goes into that row's note (≤ 120 chars), not a new row.
4. Append the new topics with the next sequential IDs, status `new`, Last `—`, and
   at most one short open question in the note.
5. Leave every existing row byte-identical — status, dates, and notes are the
   student's mastery record. Never reset anything to `new`.

Topic names: ≤ 8 words, in the lecturer's vocabulary, specific enough that the
student recognizes it on a list ("Resource-sharing protocols (NPP/PIP/PCP)", not
"Chapter 3 part 2").
