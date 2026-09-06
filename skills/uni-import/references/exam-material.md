# Route B — exam-related material → exam-brief.md

Read this when the material is a past exam, an exam announcement, the professor's
exam-info slides, notes the student relays from the last lecture, or an assignment
sheet offered explicitly as a question-style anchor — and when a lecture deck
imported via Route A turned out to carry exam logistics/format pages (first and last
lectures often do): finish the digest first, then come here for those pages, and say
you did both.

Everything about *the exam* lives in `exam-brief.md`: course content stays in the
digests, study state stays in `course-state.md`. The brief's own comment header
carries its editing rules (merge-never-clobber, every entry sourced, compact) —
honor them.

## Steps

1. **Find or create the brief.** Look for `exam-brief.md` in `/mnt/project`, then
   uploads, then the conversation. If it doesn't exist yet, create it from
   `assets/exam-brief-template.md`; otherwise merge into the existing one — preserve
   every entry, append and refine, never regenerate a section.

2. **Read the material.** Past-exam PDFs are often figure-heavy: the Route-A
   triage/raster pipeline applies (`scripts/pdf_triage.py triage`, then `raster` for
   flagged pages; judgment cases → `references/pdf-notes.md`). Read the state file's
   topic table alongside, so archetypes and tasks can be mapped to topic IDs.

3. **Extract into the brief's sections, sourcing every entry** ("Oct 2025 exam",
   "prof, last lecture", "digest-04 slides 34–36") — unsourced exam intelligence is
   rumor:
   - **Exam facts** — date/time of the *upcoming* exam, duration, format, grading,
     MC penalties, allowed aids, logistics.
   - **Question archetypes** — one entry per question *type*: what it asks for, one
     concrete example (the lecturer's or the exam's wording verbatim when possible),
     the source, and the topic IDs it hits.
   - **Recurring past-exam tasks** — when a task in this material matches one from a
     previously imported exam, say so explicitly with both sources: recurrence is the
     highest-value intelligence in the file. Give a compact answer sketch. Record
     exam-task figures with file + page (`Figure: \`file.pdf\` p.N`) so the tutor
     can present the original.
   - **Priorities & professor hints** — what was said to matter or not to matter.
   Leave the **Watch-list** alone — that section is the tutor's.

4. **The exam date rule.** Only update the `exam:` header line of `course-state.md`
   when the material states the *upcoming* exam's own date/time (an announcement,
   the professor's slides). A past exam paper is a source of question-style
   intelligence, not a date to adopt — never set the header from a past exam's date.
   Otherwise `course-state.md` is untouched by this route.

5. **Validate.** Run the validator on the brief before delivering:

   ```bash
   python scripts/check_import.py --brief /mnt/user-data/outputs/exam-brief.md --state <course-state.md>
   ```

   It refuses a figure entry without file + page and an archetype that cites a
   topic ID the state file doesn't have. Fix and re-run until clean.

6. **Deliver.** Write `exam-brief.md` (and `course-state.md` only if step 4 changed
   its header) to `/mnt/user-data/outputs/`, present the file(s), and remind the
   student to re-upload — and to keep the exam PDF in the project, since figure
   retrieval depends on it.

## Two things worth saying to the student

- If archetypes now exist and a plan doesn't: `uni-plan` weights topics by exactly
  this file, so planning gets much better targeted from here.
- If this was the first past exam imported: recurrence can only be detected from the
  second one on — importing further past exams is the cheapest high-value move left.
