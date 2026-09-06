# Changelog

## v2.1.0 — 2026-09-06

Distribution change plus a fix release driven by a field test.

### Packaging: the framework is now one plugin

The six skills ship as a single plugin named `uni`, distributed by adding this
repository as a plugin marketplace, instead of six `.skill` files installed one at a
time. One install brings all six and keeps them in sync; updates arrive when the
plugin version is bumped. The skills work in chat on the web, the Chat tab in Claude
Desktop, and in Cowork.

- **New:** `.claude-plugin/plugin.json` (the plugin manifest: name `uni`, version,
  description, license) and `.claude-plugin/marketplace.json` (a one-entry catalog
  whose plugin source is the repository root). Nothing else moved: `skills/` was
  already the layout a plugin expects.
- **Skill names are namespaced** by the plugin: `uni:uni-import`, `uni:uni-tutor`, and
  so on. Automatic triggering from each skill's description is unchanged, and so is
  skill-to-skill invocation and the project-instructions routing table.
- **Removed:** the per-skill `.skill` packaging workflow. Adding a marketplace is the
  simpler install route and is available on every paid plan by default. CI now runs
  `claude plugin validate` on the plugin and the catalog on every push, and checks on a
  release that the manifest version matches the tag — a version that isn't bumped means
  users never receive the update.
- Adding a seventh skill is now a folder under `skills/`; the manifest needs no change.

### Fixes driven by a field test

Fix release driven by a field test: a v2.0.0 knowledge base built from a real
13-lecture course was compared against the v1 knowledge base for the same course.
The architecture held (state/content split, permanent topic IDs, figure index,
clean condensation on most units); the import pipeline had measurable defects.
**Additive, no migration:** files written by v2.0.0 stay valid (`contract v2`
unchanged); a v2.0 state file without the new header line is read with a default.

#### Findings → fixes

- **Dangling figure references.** Several digests cited figure IDs that their own
  figure index did not define, so the tutor's lookup failed silently. Figure IDs
  are now assigned by one running counter *while reading* (written into the
  fragment with file + page the moment a figure is kept) and never renumbered at
  merge; a new validator refuses any digest with an unresolved `F#`.
- **Topic table over budget.** The per-lecture rule ("~3–6 per lecture") won over
  the course-wide budget, producing far more rows than the stated range, and some
  topic names exceeded 8 words because parentheticals weren't counted. The count is
  now derived from the course's expected unit count: `uni-setup` asks for it (new
  `units:` header line, default `15 (assumed)`), and each import targets
  `(35 ÷ units) × sessions spanned`; soft ceiling ~50 rows, because `uni-assess`
  walks every row. Parentheticals count. The validator checks names and notes.
- **`(lecturer example)` markers eroded.** Digests kept the lecturer's example
  questions but lost the marker that distinguishes them from inferred angles.
  Examples are now captured verbatim at first sight into a scratch file; the
  validator confirms each one reached the digest *with* its marker.
- **Exam angles cut during condensation.** Where a worked example moved to the
  figure index, the exam angle that used it was dropped too. New rule: condensing
  never deletes an exam angle — it stays and points at the figure. Range widened
  to 3–8 bullets.
- **Cross-unit narrative lost.** v1 kept "this resolves what the earlier lecture
  flagged" in the tracker; v2.0 dismantled the tracker without giving the narrative
  a home. Digests gain a **Connections** section (*builds on* / *resolves* / *feeds
  into*); `scripts/prior_digests.py` prints the open questions and connections of
  existing digests so an import can link without reading them whole; the one
  sanctioned import-time edit to an existing topic row is a `→ resolved in
  digest-NN` pointer appended to its note. `uni-tutor` reads Connections when
  picking spaced-recap topics.
- **Subscript rendered as a product.** Digests may use compact unicode, now with a
  stated convention: underscore is subscript, middle dot is multiplication; when
  unicode can't say it unambiguously, use `$$…$$` in the digest too.

#### Skill changes

- `uni-import`: new `scripts/check_import.py` (validate → fix → re-run before
  delivery; also checks `exam-brief.md`) and `scripts/prior_digests.py`; Route B
  (exam-related material) moved to `references/exam-material.md` so lecture runs
  don't load it; Route A keeps capturing lecturer examples and stray exam-info
  slides; `references/topics.md` rewritten around the unit-based arithmetic;
  `assets/digest-template.md` gains the Connections section and the exam-angle,
  provenance, figure-ID, and notation rules.
- `uni-setup`: asks for the expected number of units; state template gains the
  `units:` line and the budget/pointer rules in its contract header.
- `uni-tutor`: spaced-recap picks read the newest digest's Connections section.
- Spec: new principle P9 (verify mechanically before delivery); §5.1 maps each
  field finding to its fix; acceptance scenarios expanded.

## v2.0.0 — 2026-07-07

Full re-architecture of the framework. **Breaking: no backward compatibility** —
v2 does not read v1's `topic-tracker.md`, `study-plan.md`, or `learning-profile.md`,
and there is no migration tooling. Finish running courses on v1; start new courses
on v2.

### Architecture

- **Three skills become six**, re-distribute work according to "do one thing well" philosophy:
  - `uni-setup` *(new)* — project scaffolding, split out of v1 `lecture-digest`.
  - `uni-import` — succeeds v1 `lecture-digest`'s digest pipeline; now the single
    door for **all** material types, routing lecture material to digests and exam
    material (past exams, professor exam info) to the new `exam-brief.md`.
  - `uni-assess` *(new)* — the self-assessment pass, previously buried in v1's
    study-plan flow; now standalone and invokable by other skills.
  - `uni-plan` — succeeds v1's study-plan reference flow as its own skill; gates
    on exam intelligence and honest statuses before writing a schedule.
  - `uni-tutor` — succeeds v1 `study-tutor`.
  - `uni-check` — succeeds v1 `assignment-check`, plus a new foothold mode.
- **Skills compose**: uni-plan invokes uni-assess when statuses are cold;
  uni-import offers uni-setup when no course exists. Every invocation point has a
  compact inline fallback if the sibling skill isn't installed.
- **`uni-` prefix** groups the family in the skill picker and in descriptions.

### State/content separation (the core v2 design rule)

- **One state file per course**: `course-state.md` — topic registry with permanent
  IDs (`T01…`), statuses, and the study schedule — replaces v1's `topic-tracker.md`
  + `study-plan.md` pair. One file to re-upload after any session.
- **Hard content budgets** stop the v1 failure mode where tracker rows swelled
  into mini-digests and the plan absorbed an exam knowledge base: topic names ≤ 8
  words, notes ≤ 120 chars, schedule cells hold topic IDs/hours/pointers only.
- **`exam-brief.md`** *(new canonical file)* — the designated home for what used
  to squat in state: exam format facts, question archetypes, recurring past-exam
  tasks, professor hints, and a personal **watch-list** of traps (appended by the
  tutor, drilled deliberately in sessions).
- **The contract travels with the data**: `course-state.md` and `exam-brief.md`
  carry their own editing rules in comment headers (merge-never-clobber, budgets,
  status vocabulary `new/weak/ok/strong`, ID permanence), instead of the rules
  being restated across skill files. Files are stamped `uni-v2` / `contract v2`.
- **`(self)` evidence marker**: self-assessed statuses are distinguished from
  session-demonstrated ones; uni-plan schedules early verification for self-rated
  strong topics, and uni-assess ratings may downgrade freely (confidence decays).
- **Dropped:** `learning-profile.md` — rarely read in practice; per-course traps
  now live in the exam-brief watch-list.

### Robustness fixes (v1 pain points)

- **Read-only mount handling**: every writing skill writes updated files directly
  to outputs — eliminating v1's recurring "Failed to edit topic-tracker.md → copy
  to writable location" wasted cycles.
- **Anti-drift tutor**: uni-tutor opens with a ≤15-line Session Rules Card and
  re-reads it at every agenda-block boundary (boundary-triggered, not
  turn-counted) — addressing v1's tutor getting fuzzy on its instructions in long
  sessions. Long-form pedagogy moved to references loaded once per session.
- **Read-the-material enforcement**: the tutor reads the *full* digest files for
  the session's topics (not project-search snippets), stated as a hard rule with
  its rationale.
- **Original figures, never redrawn**: digests now include a **figure index**
  (figure → source file + page); the tutor pulls and presents the original page
  via a tested one-line command instead of describing or regenerating diagrams.
  Raw materials are kept in the project to guarantee availability.
- **Math rendering rule** (framework-wide): display math in `$$…$$` only; no
  single-`$` inline math, no `\(…\)`, never math in backticks (these fail on
  several Claude surfaces); clean unicode for short inline symbols.
- **Unit & scale detection** in uni-import: digests are numbered in the course's
  own unit scheme; multi-lecture material is detected and scales topic counts,
  calibrated against a course-wide budget of ~15–40 topics.
- **Past-exam vs upcoming-exam distinction**: importing a past exam never sets the
  course's exam date (found and fixed during validation on real material).

### Per-skill changes worth knowing

- `uni-plan`: asks for available study days **with rough hours each**; front-loads
  high-value topics so second passes remain possible; names sprint tiers including
  an explicit accept-risk tier; student-stated priorities are written to
  `exam-brief.md` so the tutor inherits them; re-planning marks history (`✓` /
  `missed`) and redistributes only the remainder.
- `uni-tutor`: no-plan sessions are now a first-class default (newest material +
  spaced recap of thematically tied older topics) instead of an awkward "want a
  plan?" prompt; watch-list traps are deliberately drilled; session-end appends
  new traps to the exam-brief.
- `uni-check`: new **foothold mode** for the genuinely stuck (starting point,
  never the solution); explicitly pulls the course's digests/slides as the frame
  for judging expected methods; `pitfalls-*.md` references are now a plug-in
  extension point per field (bundled: `pitfalls-cs.md`, unchanged from v1);
  repeated invocations review only what changed.

### Packaging

- Each skill ships as an individually installable `.skill` package.
- README rewritten around the three use cases and the content/state split.
- License unchanged: CC BY-NC-SA 4.0.

## v1.0.0

Initial release consisting of three skills: `lecture-digest`, `study-tutor`, `assignment-check`.
