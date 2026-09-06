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

## How many rows — arithmetic first, then judgment

The count comes from the **course-wide budget**, never from a per-lecture constant.
A full course should land around **35 rows** (typical range 25–45), with a **soft
ceiling of 50**: `uni-assess` walks every row in a form the student fills in a few
minutes, and a 60-row form is no longer a form. Courses package the same amount of
content very differently — 4 fat chapters or 15 thin lectures — so the budget is
spread over the course's own units, read from the `units:` header line of
`course-state.md` (`15 (assumed)` when the student didn't know; treat a missing line
as 15 too):

> **target for this import ≈ (35 ÷ units) × in-class sessions this material spans**,
> rounded, sanity range 1–10.

- `units: 15`, a single lecture → 2–3 rows.
- `units: 4`, a chapter that took ~3 sessions → ~9 rows.
- `units: 12`, a double lecture → ~6 rows.

State the arithmetic in one line before choosing rows. Then check where the table
stands: if this import would push it past 50, say so and go coarser on this one. The
old "3–6 per lecture" rule of thumb is what produced 58 rows on a 13-lecture course —
it's a sanity check for a single session's content at most, not a target.

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

Six rows, not twenty — right for a course of six to eight units. In a `units: 15`
course the arithmetic says 2–3, and the same lecture collapses further:

- Logic foundations: entailment, FOL syntax/semantics, formalization
- Inference & theorem proving: resolution, (un)decidability, TPTP
- Situation & temporal calculus

The "LLMs vs symbolic" slides become a note on the first row, not a row. Fewer rows
is not lost content — every term is still in the digest.

## Appending procedure (every lecture-material import)

1. Read the existing `course-state.md` topic table.
2. Derive the unit's topics from the digest's structure and the lecturer's own
   sectioning — group fine-grained terms under their parent theme.
3. Match each candidate **loosely** against existing rows (same theme under
   different wording = same row; don't create near-duplicates). A genuinely new
   facet of an existing topic goes into that row's note (≤ 120 chars), not a new row.
4. Append the new topics with the next sequential IDs, status `new`, Last `—`, and
   at most one short open question in the note.
5. **The one edit an import may make to an existing row:** when this unit resolves
   the open question an older row's note records (you saw it in the
   `prior_digests.py` output and wrote the `resolves` line in §Connections), append
   `→ resolved in digest-NN` to that note — a pointer of a few words, still within
   120 chars. The resolution itself lives in the digest. This is the whole exception:
   v1's tracker died of notes that grew into prose.
6. Leave every other existing row byte-identical — status, dates, and notes are the
   student's mastery record. Never reset anything to `new`. `check_import.py` compares
   against the pre-import file and refuses anything beyond the pointer append.

Topic names: ≤ 8 words **counting parentheticals** — a clarifier that doesn't fit
moves to the note or goes — in the lecturer's vocabulary, specific enough that the
student recognizes it on a list ("Resource-sharing protocols (NPP/PIP/PCP)", not
"Chapter 3 part 2").
