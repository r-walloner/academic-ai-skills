<!-- COURSE STATE FILE — uni- framework, contract v2

Rules for ANY skill or person editing this file:

1. MERGE, NEVER CLOBBER. This file carries the student's mastery data across many
   sessions. Read the existing version first; preserve every row, status, and date;
   change only cells you have fresh evidence for; append new topics rather than
   regenerating the table. If you cannot find an existing version, say so explicitly
   before creating a fresh one — a silent fresh start can destroy a semester of state.

2. CONTENT BUDGETS. Topic names ≤ 8 words (parentheticals count). Schedule cells
   contain topic IDs, hours, and pointers only — never formulas, definitions,
   question text, or session play-by-play. This file is a registry, not a summary:
   it holds IDs, names, statuses, dates, and schedule cells, and nothing in it is
   prose. Course knowledge lives in the digest files; exam intelligence and personal
   traps in exam-brief.md; cross-unit links (what resolves what) in the digests'
   Connections sections. If you catch yourself writing content into this file, stop
   and put it where it belongs. The Topics table stays under ~50 rows: uni-assess
   walks every row in a form the student fills in minutes.

3. STATUS values: new | weak | ok | strong. "Last" is YYYY-MM-DD; add the suffix
   "(self)" when the evidence is the student's self-assessment rather than a
   demonstrated result in a session. Self-assessed statuses are weaker evidence.

4. TOPIC IDs (T01, T02, …) are permanent for the course's lifetime. Never renumber,
   reuse, or delete a row without the student's explicit confirmation. Everything
   else (schedule, sessions, chat) refers to topics by ID.

5. The "units:" header line is the expected number of units in the course (lectures,
   chapters, weeks — whatever it is organized by). uni-import derives how many topics
   each import registers from it, which is what keeps this table short enough to
   self-assess in minutes (soft ceiling: ~50 rows). "15 (assumed)" means the student
   didn't know; any import may replace it once the material reveals the real count.

6. This file is mounted read-only inside the project. To update it: build the new
   content and write it directly to /mnt/user-data/outputs/course-state.md, present
   it, and remind the student to re-upload it to the project.
-->

# Course State — [course name]

framework: uni-v2
exam: [YYYY-MM-DD HH:MM, or — if unknown]   ·   plan-mode: none
units: [expected number of lectures / chapters / weeks, or "15 (assumed)" if unknown]
updated: [YYYY-MM-DD]

## Topics

| ID | Unit | Topic | Status | Last |
|----|------|-------|--------|------|

<!-- The Schedule section is added by the uni-plan skill when a plan is made:

## Schedule

| Date | Block | Topics | Focus |
|------|-------|--------|-------|
| Jun 25 AM | ~1.5h | T04 T16 | T04 second pass · T16 first pass · see exam-brief §archetypes |

**Sprint tiers** (sprint mode only): must-cover: … · worth-a-look: … · accept-risk (explicitly deprioritized): …
-->
