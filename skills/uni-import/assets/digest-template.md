<!--
Per-unit digest template — uni- framework, contract v2.
Fill every section from the lecture material only. Keep it compact: this file goes
into a Claude Project as reference, so density matters more than polish. Use the
lecturer's own terminology. If a section has nothing in it, write
"— none in this unit —" rather than padding it.
Notation: compact unicode/inline notation is fine IN THIS FILE (it saves space) as
long as it doesn't change or obscure a formula's meaning. Convention: underscore is
subscript (A_norm, T_be), middle dot is multiplication — never expand a subscript
into a product. If unicode can't say it unambiguously, use $$…$$ here too. The
$$…$$ rendering rule otherwise applies to what the student is shown in chat.
-->

# [Unit title] — Digest

**Source:** `[filename]`, slides/pages [range]
**Course:** [course name]  ·  **Unit:** [the course's own unit label, e.g. Ch. 3 / Lecture 05 / Week 7]  ·  **Imported:** [YYYY-MM-DD]

## Core concepts
<!-- Key terms with 1–3 sentence definitions, in the lecturer's wording. One bullet per term. -->
- **[Term]** — [definition].

## Key relationships / processes
<!-- How concepts connect: causal chains, workflows, comparisons. Describe what
     diagrams SHOW in words here, and reference the figure index entry so the
     original can be pulled ("see F2"). -->
- [Relationship / process / what a diagram shows (F#)].

## Formulas, algorithms, theorems, proofs
<!-- Reproduce SHORT items precisely (formulas, statements, pseudocode). For long
     derivations or proofs, summarize the steps and point to where the full version
     lives ("full derivation: slides 22–25"). Worked NUMERIC examples are not
     transcribed: give them a figure-index line whose description says what the
     numbers are, and — if an exam could ask the student to read such an output —
     an exam angle that names that task and points at the figure. -->
- **[Name]:** [statement / formula / steps]. [Pointer if abbreviated.]

## Likely exam angles
<!-- 3–8 bullets predicting the TYPES of question this material could generate — not
     invented questions ("compare X and Y", "trace algorithm on an example",
     "derive/prove Z", "interpret the output in F4"). Two rules:
     (1) Lecturer-provided example questions are the strongest signal for question
         style that exists: they arrive here VERBATIM from the scratch file
         lecturer-examples.md, each marked *(lecturer example)*. The marker is what
         lets the tutor tell "the lecturer posed this" from "the digest inferred
         this" — dropping it is the same as dropping the question.
     (2) Condensing never deletes an angle. If the data an angle relies on (a worked
         example, a table, a numeric output) moved to the figure index, the angle
         stays and points at the figure. The index keeps the data; only the angle
         keeps the prediction that the student will be asked about it. -->
- [Angle.]
- [Angle that uses a figure: "interpret each value in F4 and judge it".]
- [Lecturer-provided example question, verbatim.]  *(lecturer example)*

## Open questions / to follow up
<!-- Points that were unclear, glossed over, or flagged "covered later". Genuine gaps
     only — these feed the topic notes in course-state.md, and later imports check
     their material against them (see Connections). -->
- [Open question.]

## Connections
<!-- The cross-unit narrative — one line per link, naming the digest and topic IDs.
     Three kinds: "builds on" (a prerequisite this unit assumes), "resolves" (an open
     question an earlier digest recorded that this material answers — quote it
     briefly), and, only when the lecturer says so, "feeds into" (a later unit this
     one prepares). Source: what the material itself says, plus the Open questions /
     Connections of existing digests as printed by scripts/prior_digests.py. This
     section is content, so it lives here, not in the state file; the state file
     gets at most a "→ resolved in digest-NN" pointer. Write "— none —" for a unit
     that genuinely stands alone. -->
- builds on digest-[NN] ([T##]) — [what is assumed, a few words].
- resolves digest-[NN] open question: [the question] — [the answer in one clause] ([T##]).
- feeds into [later unit] per the lecturer.

## Figure index
<!-- Every figure worth ever showing the student again — diagrams, plots, worked
     schematics, example-task figures, numeric outputs. One line each; ≤ 10 words of
     description; exact file and page. IDs come from ONE running counter across the
     whole import, assigned while reading, and are never renumbered at merge — so
     an inline "(F7)" written early still means F7 here. Every F-ID cited in the
     body must resolve to a line below; scripts/check_import.py refuses the digest
     otherwise. This index is what lets the tutor present the ORIGINAL image later
     instead of describing or redrawing it, so be generous about inclusion. -->
- F1 · [what it shows] · source: `[filename]` p.[N]

## Topics registered
<!-- Cross-link only; course-state.md is the registry of record. -->
Topics: [T##–T##] (see course-state.md)
