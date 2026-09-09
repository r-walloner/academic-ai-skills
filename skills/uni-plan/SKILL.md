---
name: uni-plan
description: >-
  Build or update an exam study plan (schedule) for a university course in the uni-
  framework. Use whenever a student mentions an upcoming exam date, says "make me a
  study plan", "plan my revision", "I have an exam on the 24th", "help me schedule
  my prep", "I'm behind, re-plan", or wants the schedule updated after missed days
  or newly imported material. Reads course-state.md, exam-brief.md, and the digests;
  asks for the exam date and the available study days with rough hours each; writes
  the schedule into course-state.md. Invokes uni-assess first when topic statuses
  are cold. Do NOT use for running the actual study sessions (uni-tutor) or for
  importing the professor's exam info or past exams (uni-import — that should
  happen before planning).
---

# uni-plan — a schedule that fits reality

A plan is only as good as three inputs: real exam intelligence, real time
availability, and honest statuses. The flow below gates on each before writing
anything. Read `references/planning.md` before step 4 — it carries the mode
arithmetic, weighting rules, schedule format, and re-planning rules.

**Contract:** project/upload mounts are read-only — write the updated
`course-state.md` directly to `/mnt/user-data/outputs/`, present it, remind the
student to re-upload. If the plugin's experimental
`mcp__plugin_uni_project_sync__replace_doc` tool is available, you may call it
**after** writing the output file(s) to try syncing them back into the Claude
Project; on failure, keep the normal re-upload fallback. Merge, never clobber: the
Schedule section is added/updated;
the Topics table and every status in it stays untouched (the file header
carries the full rules). The schedule lives INSIDE `course-state.md` — never create
a separate plan file.

## Flow

1. **Read `course-state.md`.** Then ask, in one message, only for what's missing:
   the exam date/time (if the header doesn't have it), and the **available study
   days with rough hours each** — invite the natural format ("16th full day, 18th
   almost full −3h, 19th full, 22nd full, 24th morning only"). Don't ask for
   anything already stated in the conversation.

2. **Exam-intelligence gate.** Look for `exam-brief.md`. If it's missing or thin
   (no archetypes, no professor info), tell the student plainly: plans weighted by
   real exam intelligence are much better targeted, and the professor's exam-info
   slides, past exams, or even notes from the last lecture are worth importing
   first — offer to pause so they can run **uni-import** on whatever they have. If
   they have nothing, proceed and say the weighting rests on the digests' exam
   angles alone.

3. **Status gate.** If statuses are mostly `new`, or stale relative to the
   semester (Last dates far in the past), the plan would be built on guesses —
   invoke the **uni-assess** skill now and continue when the ratings are in. (If
   uni-assess isn't installed: present the topic list as a numbered list, collect
   low/medium/high/n ratings in one batch, record them with `(self)` dates —
   compactly, inline.)

4. **Choose the mode and weigh the topics** — read `references/planning.md` now.
   In brief: full-prep vs sprint by honest arithmetic on topics × available hours
   (stated in one line); topic value = exam-brief evidence > digest exam-angle
   density > status; front-load high-value topics so second passes are possible;
   schedule early verification for `strong (self)` topics with high exam value; in
   sprint mode name all three tiers, including accept-risk, out loud.

5. **Write.** Add/update the Schedule section of `course-state.md` in the format
   documented in the file's own header (dated blocks, `~Nh`, topic IDs and
   pointers only — no content in cells). Update the header lines (`exam:`,
   `plan-mode:`, `updated:`). Anything learned during planning that is exam
   intelligence (format facts, priorities like "in-class syntax over tool syntax")
   goes into `exam-brief.md` — deliver both files if both changed. Present, remind
   re-upload, and close with one line on what happens next ("start the first block
   with uni-tutor"). If the experimental
   `mcp__plugin_uni_project_sync__replace_doc` tool is available, you may call it
   for each file you wrote under `/mnt/user-data/outputs/`; if a call fails, note
   the failed sync briefly and keep the normal fallback.

## Edge cases

- **No exam date and none forthcoming** — don't fabricate urgency; offer a light
  rolling-recap schedule (newest topics + spaced review) or defer planning.
- **Exam very close (≤ 2 days)** — sprint with hard triage; say plainly what
  accept-risk means at this range and keep the last hours for mixed recall over
  must-covers, not new material.
- **Re-planning** (missed days, new imports, "I'm behind") — follow the
  re-planning rules in the reference: mark history, redistribute the remainder,
  minimal edits.
