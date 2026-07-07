# Reusable LLM skills to help students learn more effectively

A small toolkit of three skills that support two distinct parts of student life:

- **Exam prep** — `lecture-digest` and `study-tutor` work together to turn a semester's
  worth of lecture material into a lean knowledge base and then drill you against it in
  the run-up to an exam.
- **Ongoing coursework** — `assignment-check` is a standalone tool you reach for
  throughout the semester whenever you've done an assignment and want a grader's-eye
  read on it, independent of any exam-prep setup.

Everything here is **subject-agnostic** — the skills infer structure from your material
rather than assuming a field, so they work for any course.

---

## The three skills

| Skill | What it does | You give it | You get back |
|-------|-------------|-------------|--------------|
| **lecture-digest** | Condenses lecture slides/notes into a lean, exam-focused knowledge base — and builds your study plan | One lecture file per run (PDF, docx, md, txt) | A per-lecture `digest`, plus course-wide `topic-tracker.md`, `study-plan.md`, and a Project-instructions block |
| **study-tutor** | Runs interactive study sessions — quizzes, mock exams, explain-it-back — grounded in your digests | "Quiz me on lecture 4", "mock exam", "revise topic X" | A live tutoring session + an updated `topic-tracker.md` |
| **assignment-check** | Reviews **your own** completed solutions like a sharp TA, flagging where you'd lose points | An assignment sheet + your worked solution | Per-task, grader's-eye feedback |

`lecture-digest` and `study-tutor` share one **course knowledge base** — a Claude
Project holding your digests, tracker, and plan; the first builds it, the second reads
from it. `assignment-check` stands on its own: it just needs the assignment sheet and
your solution (lecture slides are an optional bonus), so you can use it with or without a
Project set up.

---

## Track A — Preparing for an exam (`lecture-digest` + `study-tutor`)

This is the multi-step arc: build a knowledge base from your lectures, plan the
revision, then drill against it.

### 1. Set up a Claude Project for the course

Make one Claude Project per course. This is your exam-prep hub — all digests, the
tracker, and the plan live here so every session starts from your current state.

On your first run, `lecture-digest` also hands you a ready-to-paste **Project
instructions block**. Paste it into the Project's custom instructions so requests route
to the right skill automatically ("quiz me" → tutor, "I have an exam on [date]" →
planning).

### 2. Digest your lectures (`lecture-digest`)

Upload **one lecture file at a time** and ask Claude to digest it. Each run produces a
compact digest capturing the core concepts, key relationships, formulas/theorems, likely
exam angles, and any example questions the lecturer provided. Re-invoke for each
lecture; upload the resulting digest files back into the Project.

The digests are the **source of truth** study-tutor teaches from, so this step is the
foundation — do it as you go through the semester, or in a batch before an exam.

### 3. Build a study plan (`lecture-digest`)

When you know your exam date, ask for a plan. Claude picks **full-prep** (spread review
across the days available) or **sprint** (triage into must-cover / worth-a-look /
accept-risk) based on how much time versus material you have, and writes it to
`study-plan.md`. Keep this in the Project.

### 4. Run study sessions (`study-tutor`)

Ask to be quizzed, drilled, or mock-examined. A session reads your plan and digests,
warms you up with recall questions, then works through topics using a mix of modes —
explain-it-back, mock exams (using the lecturer's own question style when available),
teach-it-back, and trick questions for topics you're already solid on. At the end it
updates `topic-tracker.md` with your current mastery per topic. **Re-upload the updated
tracker** so your next session starts from where you actually are.

---

## Track B — Ongoing coursework (`assignment-check`)

Use this throughout the semester, whenever an assignment is due — no Project or digests
required. When you've attempted a sheet, give Claude the **assignment sheet** and **your
solution** (drop in the lecture slides too if you want it judged against the course's
expected methods). It verifies the work independently rather than just plausibility-
checking it, then flags issues by severity — outright wrong, likely deduction, or
correct-but-loses-presentation-points — and points you toward the fix without writing
the solution for you.

It's built to be invoked **repeatedly** as you work through a sheet: check a task, fix
it, check the next one. It only ever reviews tasks you've actually attempted, so it's
feedback on your own work rather than an answer key.

If you happen to have a course Project set up for exam prep, assignment-check will
happily use the slides and digests already in it — but it doesn't need them, and using it
never requires building the knowledge base first.

---

## Recommended models

These skills vary a lot in how much reasoning each step needs. Matching the model to the
task keeps quality high where it matters and cost down where it doesn't:

| Task | Recommended model |
|------|------------------|
| **Lecture digest** | **Sonnet 5, Medium** — mostly extraction and condensing; a mid-effort Sonnet handles it well and keeps per-lecture cost bounded |
| **Building the study plan** | **Opus 5, High** — the triage and pacing logic benefits from the strongest reasoning; you build a plan rarely, so spend here |
| **Tutor mode** | **Sonnet 5, High for the first message, then Medium** — the first turn does the heavy lifting (reading the plan and digests, setting the agenda); once the session is underway, Medium keeps it responsive and economical |

Assignment-check is best run at a higher effort setting when correctness verification
matters (proofs, complexity arguments), since the whole value is careful step-by-step
checking rather than a quick read.

---

## Tips

- **For exam prep: one course per Project, one lecture per digest run.** Keeps
  everything focused and the knowledge base clean.
- **Always re-upload the files study-tutor hands back** (updated tracker, and any
  revised plan). They carry your mastery data forward — the next session is only as good
  as the state it starts from.
- **The digests are the ground truth for tutoring.** Richer, more accurate digests make
  for sharper study sessions. If a digest is thin, the tutor feels it.
- **assignment-check reviews your *own* attempts** — it's a learning tool, not an
  answer service. It won't write solutions to tasks you haven't tried, and you can use
  it any time without setting up a Project.