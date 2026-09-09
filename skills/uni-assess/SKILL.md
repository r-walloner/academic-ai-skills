---
name: uni-assess
description: >-
  Quick self-assessment of a student's confidence per course topic in the uni-
  framework: presents the topic list from course-state.md grouped by unit, collects
  low/medium/high ratings in one or two batches, and seeds the status column. Takes
  a few minutes, not a study session. Use whenever a student says "self assessment",
  "rate my confidence", "I don't know where I stand", "let me tell you what I know",
  when starting exam prep for a course with little or no session history, or when
  another uni- skill (typically uni-plan) needs statuses seeded before it can work.
  Do NOT use for actual tutoring, quizzing, or verification of knowledge (uni-tutor)
  — this collects the student's own ratings, it does not test them.
---

# uni-assess — seed statuses in minutes

This is a form, not a conversation. The whole value is that it takes ~3 minutes and
turns a wall of `new` statuses into something a plan or session can work with. Every
extra exchange erodes that value — aim for two user replies total.

**Contract:** project/upload mounts are read-only — write the updated file directly
to `/mnt/user-data/outputs/course-state.md`, present it, remind the student to
re-upload. If the plugin's experimental `mcp__plugin_uni_project_sync__replace_doc`
tool is available, you may call it **after** writing the file to try syncing
`course-state.md` back into the Claude Project; on failure, keep the normal fallback.
Merge, never clobber: the state file's own header carries the full rules.

## Flow

1. **Read `course-state.md`** (project, then uploads, then conversation). Empty
   topic table → nothing to assess; point to `uni-import` and stop. Re-assessment
   of already-rated or session-verified topics is always legitimate — confidence
   changes over time, and the student's current read is the point.

2. **Present the topics as one numbered list (1…N), grouped by unit** — number,
   ID, name, nothing else. The numbering exists so the student can answer as a bare
   list ("1. low", "2. L", "3. n", …) without retyping topic IDs; numbers follow
   presentation order and are mapped back to topic IDs when recording — they are
   NOT the topic IDs, which may not be contiguous. Show the reply format once:
   ratings are **l**ow / **m**edium / **h**igh, plus **n** = "haven't actually
   learned this yet". Ranges and per-unit shorthand are also fine ("4–7 l",
   "Ch.2 all m"). For long lists (25+), offer unit-sized batches so no single
   reply is a wall. Don't offer finer gradations — false precision costs time and
   adds nothing.

3. **Record:** l → `weak`, m → `ok`, h → `strong`, each with Last = today and the
   `(self)` suffix — planning and tutoring treat self-assessed confidence
   differently from demonstrated results, so the marker matters. n → `new` with
   Last = `—` (no exposure means no evidence, not weak evidence). Record what the
   student says even when it downgrades an earlier session-verified status —
   confidence genuinely decays when a topic hasn't been seen for a while, and the
   student's current read is the point of this exercise. Topics the student skips
   stay untouched. If the student volunteers a reason ("T07 low, never got
   recursion"), acknowledge it, let it inform the rating, and keep moving; a
   recurring trap worth keeping goes to the exam-brief watch-list. Don't open a
   discussion; that's the tutor's job.

4. **Deliver:** write the file, present it, remind re-upload. If the experimental
   `mcp__plugin_uni_project_sync__replace_doc` tool is available, you may call it
   for `/mnt/user-data/outputs/course-state.md`; if it fails, say so briefly and
   keep the normal fallback. One line of orientation and stop: "8 weak, 9 ok, 4
   strong — uni-plan or uni-tutor can start from this."
