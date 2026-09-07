<!--
Per-unit digest template — uni- framework, contract v2.
Fill every section from the lecture material only. Keep it compact: this file goes
into a Claude Project as reference, so density matters more than polish. Use the
lecturer's own terminology. A digest CONDENSES, never supplements: background you
know that the material doesn't state (the physical cause of an effect, a standard
qualifier) is left out, or marked as outside the material — the tutor otherwise
drills it as something the lecturer said. If a section has nothing in it, write
"— none in this unit —" rather than padding it.
Notation: compact unicode/inline notation is fine IN THIS FILE (it saves space) as
long as it doesn't change or obscure a formula's meaning. Convention: underscore is
subscript (A_norm, T_be), middle dot is multiplication — never expand a subscript
into a product. If unicode can't say it unambiguously, use $$…$$ here too — and that is REQUIRED, not optional, for sums/products with
index bounds, braced or stacked subscripts, and transposes on a subscripted symbol.
Never write LaTeX fragments in plain text (J^T_{k−1}, min_{K,R,t}): markdown
italicizes the span between underscores and mangles the formula. The
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
     an exam angle that names that task and points at the figure.
     Fidelity (a PDF's text layer destroys typeset math — grouping parens vanish,
     layout flattens):
     (1) Transcribe from the TEXT layer only when the formula is simple, in standard
         notation, and its structure clearly survived extraction.
     (2) RASTERIZE the page and transcribe from the image when the extracted text
         shows matrix/multi-line layout, when you are inferring grouping rather
         than seeing it, or when the notation is the course's own.
     (3) TRANSCRIBE WHAT IS DRAWN, not what the formula ought to be. Reading the
         page removes the ambiguity; it doesn't remove the pull toward the familiar
         form. A token inside an equation that isn't a standard symbol name is an
         OPAQUE OPERATOR: keep it and its brackets exactly as drawn — f(A⁻¹x) never
         becomes A_f·A⁻¹x. Transcribe a deviation from the standard form as drawn
         (the lecturer's version is what the exam uses); if it looks like a slip,
         say so in the same bullet instead of silently correcting it. Same for the
         sentence around the formula: connectives are transcribed, not paraphrased
         — turning "but this needs X" into "because X" invents a claim.
     (4) Never hedge a formula. Writing "schematic"/"approximate"/"roughly" IS the
         signal you haven't read the source — rasterize and re-transcribe. DELETING
         THE HEDGE IS NOT THE FIX: an unhedged wrong formula claims a verification
         that never happened. Still unsure after reading the rendered page → don't
         transcribe it; point at the figure-index entry instead.
     Every transcribed formula ends with its source page: (p.N) or an F#. That says
     where it came from, not that it is right — (3) is what makes it right. -->
- **[Name]:** [statement / formula / steps] (p.[N]). [Pointer if abbreviated.]

## Likely exam angles
<!-- 3–8 bullets predicting the TYPES of question this material could generate — not
     invented questions ("compare X and Y", "trace algorithm on an example",
     "derive/prove Z", "interpret the output in F4"). Marked *(lecturer example)*
     bullets sit here too but DON'T count toward the 3–8. Three rules:
     (1) POSED TASKS are lecturer examples: a question the deck leaves for the
         STUDENT to answer, or labels as an exercise or exam question. They arrive
         here VERBATIM from the scratch file lecturer-examples.md (`task:` entries),
         each marked *(lecturer example)*; dropping the marker is the same as
         dropping the question.
     (2) RHETORICAL teaching prompts — questions the deck ANSWERS ITSELF on that
         page or the next — appear NOWHERE in the digest: not here, not in Open
         questions. The test is what the deck does with the question, not how it
         is phrased; a balanced call goes to task, since discarding one costs more
         than over-drilling one. Examples:
           task:       "Compute the result for the values given on this slide."
                       (no answer follows — the student is meant to work it out)
           rhetorical: "But how would this transform?"
                       (the next two slides derive exactly that)
           task:       "Exam question: state the two conditions and prove one."
           rhetorical: "Why is it called X?"  (answered in the next sentence)
     (3) Condensing never deletes an angle. If the data an angle relies on (a worked
         example, a table, a numeric output) moved to the figure index, the angle
         stays and points at the figure. The index keeps the data; only the angle
         keeps the prediction that the student will be asked about it. -->
- [Angle.]
- [Angle that uses a figure: "interpret each value in F4 and judge it".]
- [Lecturer-provided example question, verbatim.]  *(lecturer example)*

## Open questions / to follow up
<!-- Genuine gaps: something the MATERIAL USES OR NAMES BUT DOESN'T SUPPLY — a step
     referenced but not derived, a term used before it is defined, a condition
     asserted without justification, an unclear or contradictory statement. A slide
     that says "covered later" is one such case, not the definition: decks rarely
     announce their gaps, so don't wait for the announcement (a unit that is
     visibly "part 1" of a topic is where these live).
     One specific gap per bullet, each with a per-digest ID (Q1, Q2, …) — the IDs
     are what later imports cite when they resolve one. NEVER open questions:
     rhetorical teaching prompts (ignored entirely) and roadmap/agenda previews —
     an overview "teases" later topics by design; that is at most a Connections
     "feeds into", usually nothing. -->
- Q1 · [One specific gap.]

## Connections
<!-- The cross-unit narrative — one line per link, naming the digest and topic IDs.
     Three kinds: "builds on" (a prerequisite this unit assumes), "resolves" (a
     specific open question an earlier digest recorded, cited BY ITS Q-ID), and,
     only when the lecturer says so, "feeds into" (a later unit this one prepares).
     Source: what the material itself says, plus the Open questions / Connections
     of existing digests as printed by scripts/prior_digests.py (it prints every
     question's citable Q-ID). Resolution linkage lives HERE and only here — the
     state file is never edited for it. Write "— none —" for a unit that genuinely
     stands alone. -->
- builds on digest-[NN] ([T##]) — [what is assumed, a few words].
- resolves digest-[NN] Q[k]: [the answer in one clause] ([T##]).
- feeds into [later unit] per the lecturer.

## Figure index
<!-- Every figure worth ever showing the student again — diagrams, plots, worked
     schematics, example-task figures, numeric outputs. One line each; ≤ 10 words of
     description; exact file and page. IDs come from ONE running counter across the
     whole import, assigned while reading, and are never renumbered at merge — so
     an inline "(F7)" written early still means F7 here. IDs are per-digest: cite
     another digest's figure as "digest-00 F17", never as a bare F17. Every F-ID cited in the
     body must resolve to a line below; scripts/check_import.py refuses the digest
     otherwise. This index is what lets the tutor present the ORIGINAL image later
     instead of describing or redrawing it, so be generous about inclusion. -->
- F1 · [what it shows] · source: `[filename]` p.[N]

## Topics registered
<!-- Cross-link only; course-state.md is the registry of record. -->
Topics: [T##–T##] (see course-state.md)
