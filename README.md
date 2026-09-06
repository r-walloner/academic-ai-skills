# A Claude plugin to help students study effectively

Six composable skills that turn a Claude Project into a study hub for one course:
a lean knowledge base built from your lecture material, exam intelligence collected
in one place, and interactive sessions that always know where you stand.

Everything is **subject-agnostic** — the skills infer structure from your material
rather than assuming a field, so they work for any course.

> v2 is a re-architecture and starts fresh: it does **not** read v1's
> `topic-tracker.md` / `study-plan.md` files, and there is no converter. Finish
> running courses on v1; start new ones on v2.

---

## The three ways you'll use it

**1 — After-lecture study sessions (during the semester).** A few days after each
lecture: `uni-import` the new slides, then `uni-tutor` for a short practice
session — the new material plus a light spaced recap of older topics that tie in.
Solidifying as you go makes exam prep at the end dramatically cheaper.

**2 — Assignment work.** While working on a sheet, you can invoke `uni-check` to get grader's-eye feedback on the tasks you've attempted (where would points go, and why). On its own, `uni-check` will not generate any solutions for you. If you
force it to, and thereby violate the LLM usage policy of your course, that's on you!

**3 — Exam prep (end of semester).** `uni-import` whatever exam intelligence you
have (past exams, the professor's exam-info slides), then `uni-plan` to build a
study schedule that fits your real days and hours — it runs `uni-assess` first if your
topic statuses are cold. Then repeated `uni-tutor` sessions work the plan,
enabling you to study the material in a fun interactive manner. Courses
where you skipped the mid-semester sessions just start here.

## The six skills

| Skill | One job | Typical trigger |
|-------|---------|-----------------|
| **uni-setup** | Scaffold a course project: instructions block + initial state file | "Set up my [course] course" |
| **uni-import** | Import ONE piece of material: lecture → digest + topics; exam material → exam brief | "Digest this chapter", "here's a past exam" |
| **uni-assess** | Minutes-long confidence self-assessment that seeds topic statuses | "Rate my confidence", "I don't know where I stand" |
| **uni-plan** | Build/update the study schedule from exam intelligence + real availability | "Exam is on the 24th, help me plan" |
| **uni-tutor** | Interactive study sessions, with or without a plan | "Quiz me", "let's practice lecture 4", "mock exam" |
| **uni-check** | TA-style review of your own attempted solutions | "Check my solution", "I'm stuck on task 3" |

The skills ship together as one plugin named `uni`, so installing it once gives you all
of them (and updates them together). See [Install](#install).

## The knowledge base — content vs. state

One Claude Project per course. Its files split cleanly into **content** (what the
course teaches) and **state** (where you stand) — keeping these separate is the
core design rule of v2:

- **`digest-NN-*.md`** *(content)* — one per unit of lecture material: concepts,
  relationships, formulas, likely exam angles (with the lecturer's own example
  questions when they exist), connections to earlier units (what this one builds
  on or resolves), and a figure index pointing into the source PDFs. The source of
  truth the tutor teaches from.
- **`exam-brief.md`** *(content)* — everything about the exam: format facts,
  question archetypes, recurring past-exam tasks, professor hints, and your
  personal watch-list of traps the tutor deliberately drills.
- **`course-state.md`** *(state — the only state file)* — the topic registry
  (permanent IDs `T01…`), your mastery status per topic, and the study schedule.
  Kept deliberately tiny: topic names ≤ 8 words, notes ≤ 120 chars, schedule cells
  hold topic IDs and pointers only. The file's own comment header carries the
  binding editing rules, so any skill (or you) editing it sees them.
- **Raw materials** — slide decks, scripts, sheets, past exams. Upload them and
  **keep them in the project**: when a diagram matters, the tutor pulls the
  original page and shows it, rather than describing or redrawing it.

## Install

Add this repository as a plugin marketplace once, install the `uni` plugin, and
all six skills appear. They work in chat on the web, the Chat tab in Claude Desktop,
and in Cowork. Plugins are available on all paid plans.

**In Claude (web or Desktop):**

1. Open **Customize** in the left sidebar, then the **Plugins** tab.
2. Click **Add → Add marketplace**, choose *Add from a
   repository*, and enter this repository's URL: `https://github.com/r-walloner/academic-ai-skills`
3. Install the **uni** plugin from the list.

To update once a new version is released, click **Update** on the marketplace.

## Getting started

1. Create a Claude Project for the course.
2. Run **uni-setup** ("set up my Advanced Mathematics course"). Paste the instructions
   block it gives you into the Project's custom instructions; upload the
   `course-state.md` it generates.
3. Run **uni-import** on your first lecture file (one file per run). Upload the
   digest and updated state file it hands back — and keep the raw deck in the
   project too.
4. From there: sessions with **uni-tutor**, assignment feedback with **uni-check**,
   and when the exam approaches, **uni-import** the exam info, then **uni-plan**.

**The one habit that matters: re-upload what a skill hands back.** Skills can read
your project files but not write them — every run that changes state delivers the
updated file as a download, and the next session is only as good as the state it
starts from. If a skill can't find `course-state.md`, it will say so rather than
silently starting fresh.

## Model & effort recommendations

Match the model to the step — spend reasoning where it pays:

| Task | Recommendation |
|------|----------------|
| **uni-import** | Mid-tier model, medium effort — mostly extraction and condensing; keeps per-lecture cost bounded. Be aware that for large lectures, this step can consume significant tokens. |
| **uni-plan** | Strongest available model, high effort — triage and pacing logic; you plan rarely, so spend here. |
| **uni-tutor** | Mid-tier model, high effort for the first message (it reads the plan, brief, and full digests and sets the agenda), then medium once the session is underway. |
| **uni-check** | High effort whenever real verification is involved (proofs, complexity, derivations) — the value is careful step-by-step checking. Choose the model based on the complexity of the task. |
| **uni-setup / uni-assess** | Anything — they're deliberately trivial. |

## Extending the plugin

v2 is built to grow without editing existing skills:

- **New skills:** drop a folder with a `SKILL.md` into `skills/` — the plugin picks it
  up, no manifest change needed. The conventions travel with the data — read the comment headers
  of `course-state.md` and `exam-brief.md` for the editing contract (merge-never-
  clobber, content budgets, status vocabulary, topic-ID permanence), follow the
  read-only-mounts rule (write updates to outputs, remind re-upload), and add a
  routing line to the project-instructions block.
- Files written by the plugin carry a `uni-v2` / `contract v2` marker so future
  versions can detect the format.
- The full specification of the plugin and its skills is under `spec/` in the repo.

## Tips

- **One course per Project, one file per import run.** Keeps the knowledge base
  clean and each digest focused.
- **The digests are the ground truth for tutoring.** If a digest is thin, the
  tutor feels it — re-import the unit rather than letting sessions improvise.
- **Import exam intelligence the moment you get it** — past exams mid-semester,
  the professor's exam remarks from the last lecture. `uni-plan` is only as
  targeted as `exam-brief.md` is rich.
- **Self-assessments are honest inputs, not tests.** Statuses seeded by
  `uni-assess` carry a `(self)` marker; the plan schedules early verification for
  self-rated-strong, high-value topics, and tutor sessions replace `(self)`
  ratings with demonstrated evidence over time.
- **uni-check reviews your *own* attempts** — a learning tool, not an answer
  service. It won't write solutions to tasks you haven't tried.

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
(CC BY-NC-SA 4.0) — see `LICENSE`.
