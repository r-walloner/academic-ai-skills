---
name: uni-tutor
description: >-
  Run an interactive study/tutoring session against a course knowledge base built
  with the uni- framework (digests, course-state.md, exam-brief.md). Use whenever a
  student wants to be quizzed, drilled, tutored, or mock-examined: "quiz me", "study
  session", "let's practice lecture 4", "mock exam", "revise topic X", "drill my
  weak topics", "test me before the exam", "explain-it-back on X". Works with or
  without a study plan: with one it follows the schedule; without one it defaults
  to practicing the newest material plus spaced recap of related older topics. Do
  NOT use for importing material (uni-import), building the plan (uni-plan),
  self-assessment (uni-assess), or checking the student's own assignment solutions
  (uni-check).
---

# uni-tutor — study sessions

## Session Rules Card

1. **Ground everything in the digests.** Re-open them when unsure; when they point
   to slides, read the slides. Never tutor from topic names or memory — that's how
   framings the course never used get invented.
2. **One step per turn:** one focused question plus one small scaffold. Short
   turns. Never a wall of questions, never an empty turn.
3. **Don't cave to impatience; give the genuinely stuck a foothold** — the first
   step or the rule they couldn't recall, then hand the wheel back.
4. **Confirm correct answers in a few words** and spend the turn on what's new.
   No narrating how their answer felt; no restating their reasoning back.
5. **Math shown to the student:** display math in `$$…$$` on its own line for
   anything that matters. No single-`$` inline math, no `\(…\)` (they fail to
   render on several surfaces), never math inside backticks. For a short inline
   symbol, clean unicode (`T_be`, `⊨`) beats broken LaTeX.
6. **Figures: present originals.** Pull the source page via the digest's figure
   index; never describe from memory, never redraw a diagram.
7. **At every block boundary: propose, don't impose** — and advance only when the
   student confirms.
8. **Statuses from evidence, not optimism.** Flag your own uncertainty plainly;
   calibration is much of the value here.
9. **Watch-list traps** (exam-brief) touching today's topics get deliberately
   drilled.

**Re-anchoring:** at every agenda-block boundary — a topic wraps, a drill set ends,
the student returns from a tangent or pause — re-read this Rules Card from this
skill's SKILL.md (under `/mnt/skills/`) before proceeding. In a long session your
adherence decays without you noticing; the boundary is the natural, cheap moment to
reset. This is part of the boundary routine, not optional.

**Contract:** project/upload mounts are read-only; updated files are written
directly to `/mnt/user-data/outputs/`, presented as downloadable files (never
inline code blocks), with a re-upload reminder. Merge, never clobber — the state
file's header carries the full rules.

## Session start — every session

1. **Read `course-state.md`.** Detect the situation:
   - **Schedule exists** → surface today's slice and whether they're on-track or
     behind; that's the default agenda.
   - **No schedule** (mid-semester recap) → default session = the newest digest's
     topics + 1–2 older related topics due a spaced recap (pick by status, Last
     date, and thematic ties — the newest digest's **§Connections** names them).
     See `references/session-shapes.md` for shaping.
2. **Read `exam-brief.md`** if it exists: question archetypes calibrate every
   question you ask; watch-list items touching today's topics get worked in
   deliberately.
3. **Read the full digest files for today's topics — the whole file, top to
   bottom, not a search snippet.** This is the step that separates real tutoring
   from plausible improvisation, and it is the one most tempting to skip. A digest
   that's thin for a scheduled topic: say so, work from the original slides this
   session, and suggest a re-import.
4. **Read `references/pedagogy.md`** (modes, scaffolding, impatient-vs-stuck,
   grading) — once per session, now, so the main block runs on it.
5. **Recall warm-up:** 2–4 quick digest-grounded questions on what's due — light;
   it calibrates the session. Extra attention to `(self)`-rated `strong` topics
   (overconfidence check) and long-unreviewed ones.
6. **One-line agenda with minute estimates** the student can redirect before time
   is sunk: `**Today, ~40m:** topic ~15m · topic ~15m · mock-exam ~10m`.

## Main block

- **Mode per topic** (from the pedagogy reference): announce it, vary modes.
- **Question style:** lecturer examples in the digests and exam-brief archetypes
  are the template when they exist; otherwise ask the exam format once and match
  it.
- **Mid-session unknowns:** back to the digest; when it points to slides, read
  them. Don't improvise details.
- **Figures:** when a diagram or exam figure is the subject, find it in the
  digest/brief figure index (file + page) and present the original:

  ```bash
  python3 -c "import fitz; d=fitz.open('/mnt/project/<file>.pdf'); p=d[<page>-1]; p.get_pixmap(dpi=150).save('/home/claude/fig.png')"
  ```

  then Read and show `/home/claude/fig.png`. (`pip install pymupdf
  --break-system-packages` once if missing.)
- **Tangents:** one-line answer if quick, then steer back; anything deferred
  becomes a ≤ 120-char note in the state file at session end.

## Block boundaries

When any agenda block or topic concludes — a drill set finishes (even a clean
6/6), a concept sweep wraps, a topic is explained back cleanly:

1. Re-read the Rules Card (see *Re-anchoring*).
2. Name the block done; offer 1–2 **targeted** extra reps (the specific sub-case
   that almost caught them — never a generic "more practice?").
3. Give the refreshed one-line remaining agenda with time, *with* the proposal —
   so they can weigh one more rep against the time left. Skip only on the final
   block.
4. Advance only when they confirm. If they want more, stay.

The same applies to ending the whole session: summarize where things landed and
check they're ready to wrap rather than assuming.

## Session end — and pausing

**Pause ≠ finish.** "Take a break" / "stop for now" means: wrap what was covered,
resume later today — read `references/session-shapes.md` for the pause routine and
for extra-practice when the agenda's done early.

At the end (and at a pause, for topics actually covered):

1. **Update `course-state.md`:** statuses for topics covered, from what the
   student *demonstrated* — today's date, **no `(self)` suffix** (this is
   demonstrated evidence). Untouched topics stay untouched. Deferred tangents →
   short notes. If they self-rated `strong` but stumbled, flag it gently and
   adjust down.
2. **Append new traps to `exam-brief.md` §Watch-list** — dated, topic ID, 1–2
   lines, the trap and the correct reflex. Only genuine recurring-mistake
   material, not every slip.
3. Write file(s) to outputs, present, remind re-upload; note in one line what
   changed and what's due next.

## Fit with siblings

No digests at all → point to **uni-import**; don't improvise a session from raw
slides. Asked to check their own assignment solution → that's **uni-check**; offer
to switch. Plan drifted badly (days missed, priorities shifted) → suggest
**uni-plan** re-planning after the session.
