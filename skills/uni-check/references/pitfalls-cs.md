# Where CS submissions lose points

A checklist of the specific, recurring places master's-level CS work bleeds marks. Use it as a second pass after your own verification — scan the sub-areas relevant to the task. These are *patterns to check for*, not a script to run blindly; only flag what's actually present.

## Proofs (induction, contradiction, construction)

- Base case missing, or proven for the wrong value, or doesn't actually connect to the inductive step.
- Inductive step assumes the thing being proven (begging the question), or uses strong induction while only stating the weak hypothesis.
- A case left unhandled — even/odd, n=0, empty set, the boundary.
- Proving the converse, or only one direction of an "if and only if."
- A quantifier silently swapped (∀∃ vs ∃∀) — a classic, high-value error.
- "Clearly", "obviously", "it follows that" hiding the one step that actually needed the argument.
- Existence shown but uniqueness (or vice versa) asked for and skipped.
- Non-constructive where the task wanted a construction, or an algorithm given where a proof of correctness was also required.

## Algorithms & complexity

- Correctness argued informally when a proof was asked for; or correct algorithm, no correctness argument at all.
- Complexity *asserted* but not derived; the derivation has an error; or best/average/worst-case conflated.
- Recurrence set up but solved wrong (Master Theorem case misapplied, or the case conditions not checked).
- Space complexity ignored when the task said "time and space."
- Edge cases the algorithm silently mishandles: empty input, single element, all-equal, already-sorted, negative weights, cycles, disconnected graph.
- Tightness: a bound given when the *tightest* bound was asked; or upper bound given, lower bound omitted.
- Off-by-one in loop bounds or indices; integer overflow in the analysis.

## Code

- Doesn't compile/run, or runs but fails on an edge case (empty, single, duplicates, boundary value).
- Solves a slightly different problem than specified (wrong output format, wrong return type, 0- vs 1-indexed).
- Correct output, wrong complexity — accepted logically but would time out / violate a stated constraint.
- Missing input validation or error handling the task required.
- Mutating shared state, off-by-one, uninitialized accumulator, wrong comparison operator.
- When runnable, *run it* on the task's own examples plus adversarial inputs before judging.

## Theory (automata, languages, logic, complexity classes)

- DFA/NFA accepts or rejects a string it shouldn't — test specific strings, including the empty string.
- Regular/context-free claims without the pumping-lemma argument the task wanted.
- Reduction in the wrong direction (reducing from the wrong problem proves nothing about hardness).
- Confusing a problem's membership in a class with hardness for it; "NP" used loosely for "NP-complete."
- Closure-property claims stated without justification.

## Probability, statistics & ML derivations

- Independence assumed without justification; conditioning done wrong (P(A|B) vs P(B|A)).
- Normalization constant dropped, or a distribution that doesn't integrate/sum to 1.
- Expectation/variance algebra slips; linearity of expectation misapplied to a product.
- Gradient derivation: sign error, missing chain-rule factor, dimensions that don't conform.
- Assumptions of a method (i.i.d., Gaussian, convexity) used silently when the task expected them stated.
- Stating a result that matches the lecture's notation but skips the derivation steps the rubric wanted.

## Cross-cutting (any sub-area)

- **Answered a near-miss of the question** — the single most common silent deduction. Re-read the task verb: prove vs. show vs. compute vs. *justify*.
- **Half a multi-part task done** — (a) and (b) solved, (c) quietly absent within an otherwise "attempted" task.
- **Required justification missing** — right answer, no "why," when the sheet said "explain" or "show your work."
- **Derivation skipped or outsourced** — the answer is right but reached by jumping to a known closed form, or by citing a source ("by the standard formula", "from Wikipedia") for a result the task said to *derive/show/prove*. The derivation is the graded object; a correct endpoint doesn't earn it. Also check the work *starts where the task/hint specified* (e.g. "begin from the product of densities") — starting elsewhere loses marks even if the algebra is flawless.
- **Notation/definitions** redefined or clashing with what the course (slides) fixed.
- **Assumptions unstated** — the task said "state your assumptions" and they're baked in invisibly.
