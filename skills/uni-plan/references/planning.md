# Planning depth — modes, weighting, schedule format, re-planning

Read alongside the main flow in SKILL.md. Everything here writes into the
**Schedule section of `course-state.md`** — never a separate plan file.

## Mode choice: full-prep vs sprint

Compare available study hours against what the topic table needs. Honest arithmetic
in one line, not vibes — e.g. "21 topics, ~26h available → sprint" or "11 topics,
5 full days → full-prep with second passes." The heuristic: **if every topic can't
get a real slot plus a second look at the weak ones, it's a sprint.** Say which mode
you chose and show the arithmetic; write it into the state header (`plan-mode:`).

There's no magic threshold — a topic's "real slot" depends on its weight (a
derivation-heavy topic needs a working block; a definitions topic needs twenty
minutes), so weigh, don't just count.

## Weighting: what earns early, big blocks

Topic value combines three signals, strongest first:

1. **Exam-brief evidence** — topics hit by question archetypes and (especially)
   recurring past-exam tasks. A topic that matches a recurring task is near-certain
   exam material; treat it as must-cover regardless of status.
2. **Digest exam-angle density** — how many/how central the "Likely exam angles"
   bullets are for the topic's digest.
3. **Status** — `weak`/`new` topics need real time; `ok` needs a solid pass;
   `strong` needs a brief confirmation, not a session.

Two standing strategies (the framework's defaults, from proven practice):

- **Front-load high-value topics.** High-value topics go on the *earliest* days so
  a second pass remains possible before the exam; low-reward topics go on the later
  days where running out of time costs least. Resist the natural urge to schedule
  chronologically by chapter.
- **Verify self-rated strength early.** Statuses marked `(self)` are the student's
  own estimate, not demonstrated. Schedule a short verification pass (a few recall
  questions in the first session) for `strong (self)` topics with high exam value —
  overconfidence discovered on day one is recoverable; on exam morning it isn't.

If the student states priorities during planning ("formal in-class syntax over tool
syntax"), record them in `exam-brief.md` §Priorities — sourced "student, planning" —
so the tutor respects them too; don't leave them only in the schedule.

## Sprint mode specifics

1. Name **all three tiers explicitly** in the Schedule section — must-cover /
   worth-a-look / accept-risk. The accept-risk tier is said out loud so
   deprioritization is an informed bet, never a silent gap the exam discovers.
2. Tier assignment: must-cover = high exam value AND (`weak`/`new`/unverified);
   worth-a-look = medium value or `ok` topics needing a refresh; accept-risk = low
   exam value, regardless of status ("nice-to-know" side topics).
3. Cold or shaky statuses in a sprint: schedule the **first block as a quick recall
   diagnostic** across must-cover topics (1–2 light questions each, run by
   uni-tutor) — it refreshes, validates `(self)` ratings, and may re-tier topics.
4. `strong` (session-verified) topics get a brief confirmation slot late, not a
   full block.

## Schedule format

Match the format documented in the state file's own comment header:

| Date | Block | Topics | Focus |
|------|-------|--------|-------|
| Jun 25 AM | ~1.5h | T04 T16 | T04 second pass · T16 first pass · see exam-brief §archetypes |

- One row per block the student actually has (from their stated days & hours —
  respect stated deductions like "18th −3h"). Estimate `~Nh` per block honestly.
- **Cells contain topic IDs, pass labels, hour estimates, and pointers only.**
  Never formulas, definitions, or question content — that's what the digests and
  exam-brief are for; a schedule that restates content rots the state file.
- Last block(s) before the exam: mixed review / mock-exam style over must-covers,
  not first-time learning.
- Below the table, sprint tiers on one line each; and one line telling the tutor
  how to use it ("work blocks top to bottom; question style per exam-brief").

## Re-planning (plan exists; reality diverged)

Invoked when days were missed, new topics were imported, or the student says
they're behind:

- Mark past blocks tersely: append `✓` (done) or `missed` in the Date cell — they
  are history, keep them.
- Redistribute *remaining* topics over *remaining* real blocks — re-ask available
  hours only if they've plausibly changed.
- Newly imported (`new`) topics enter the weighting like any other; in a sprint
  they compete for tiers — re-tier honestly rather than cramming them in.
- Never regenerate the Topics table, and don't reshuffle for elegance: minimal
  edits, so the student's mental model of their own plan survives.
