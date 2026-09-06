---
name: uni-setup
description: >-
  Set up a new Claude Project for a university course using the uni- study framework
  (v2). Use this whenever a student starts a new course and wants to prepare it for
  studying with Claude — "set up my [course] course", "create a course project",
  "initialize the study framework", "how do I start using the uni skills for this
  class", or when another uni- skill finds no course-state.md and the student agrees
  to set up. Produces two things in one run: the project-instructions block to paste
  into the Project's custom instructions, and the initial course-state.md to upload.
  Do NOT use for importing lecture material (uni-import), planning revision
  (uni-plan), study sessions (uni-tutor), or checking solutions (uni-check).
---

# uni-setup — scaffold a course project

One course = one Claude Project. This skill turns an empty Project into a working
hub in a single run: the instructions block that routes requests to the right
sibling skill, and the state file everything else reads and writes. Nothing else —
digests and the exam brief come later, from `uni-import`, with real material.

## Before anything: check for an existing setup

Look for `course-state.md` in `/mnt/project`, the uploads, and the conversation. If
one exists, this course is already set up — do **not** generate a fresh state file
(a duplicate invites the student to overwrite a semester of state). Say what exists,
and offer only the pieces that are genuinely missing (usually just the instructions
block, verbatim from `assets/project-instructions.md`).

## Setup run

1. **Ask once, together:** the course name, the exam date if already known, and how
   many units the course will have (lectures, chapters, weeks — whatever it is
   organized by). Nothing else; don't re-ask what the student already said, and a
   missing exam date is fine (`—`). Unknown unit count → `15 (assumed)`, one per
   teaching week; say a later import can correct it. The count matters because it
   sets how many topics each import registers — that is what keeps the topic table
   short enough to self-assess in minutes.

2. **Generate `course-state.md`** from `assets/course-state-template.md`: fill in
   the course name, the exam line (or `—`), the `units:` line, and today's date; keep
   the entire comment header verbatim — it is the framework contract other skills and
   future sessions rely on; leave the Topics table empty. Write it directly to
   `/mnt/user-data/outputs/course-state.md` and present it.

3. **Hand over the instructions block** — the full contents of
   `assets/project-instructions.md`, verbatim, as one copy-pasteable block. It is
   static and course-independent; don't tailor it, don't summarize it.

4. **Close with the loop, compactly** (a few lines, not a tutorial):
   - Paste the block into the Project's custom instructions; upload
     `course-state.md` to the Project.
   - Upload raw course materials (slide decks, scripts, sheets, past exams) to the
     Project and **keep them there** — the tutor pulls original figures from them.
   - Run `uni-import` on the first lecture material to start building the knowledge
     base. From then on: import each unit as it arrives, practice with `uni-tutor`,
     check assignment work with `uni-check`, and near the exam build a plan with
     `uni-plan`.
   - Whenever a skill hands back an updated file, re-upload it to the Project —
     that's how state carries forward.

That's the whole job. Keep the run short and let the sibling skills do theirs.
