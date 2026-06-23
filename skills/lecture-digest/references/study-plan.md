# Generating `study-plan.md`

This runs when the student wants to plan their exam prep — not during a plain
lecture digest. The goal is a realistic, dated plan that fits the time actually
remaining, honestly triaging what to prioritize when there isn't time for
everything. Write the result to `/mnt/user-data/outputs/study-plan.md` and present
it.

## Step 0 — Gather inputs

Ask the student two things (use the topic tracker to ground the conversation):
1. **When is the exam?** (date — you need days-remaining to choose a mode.)
2. **Does `topic-tracker.md` already hold real mastery data** (they've been using it
   through the semester), **or is it effectively a fresh start** (a cold start —
   everything is still `new` because they're only now sitting down to prep)?

Also count the topics in the tracker and note each topic's lecture, current status,
and how heavily it's weighted toward exam angles (from the digests' "Likely exam
angles" sections — topics that generate many/important angles matter more).

## Step 1 — Cold-start handling (self-assessment seeding)

If it's a **cold start AND time is short** (a sprint — see Step 2), don't plan
around a wall of `new`. First run a **self-assessment pass**:

- Present the topic list grouped by lecture.
- Ask the student to rate confidence per topic: **low / medium / high**.
- Seed `topic-tracker.md` from these ratings (low→`weak`, medium→`ok`,
  high→`strong`), so the plan reflects something real instead of treating
  everything as unknown.

(If it's a cold start but there's ample time, full-prep mode will cover everything
anyway, so a full self-assessment is optional — a quick skim is enough.)

## Step 2 — Choose the mode: full-prep vs sprint

Compare days remaining against the number of topics (and their weight):

- **Full-prep mode** — enough time for an even pass through everything (roughly: you
  can give each lecture/topic a real review slot and still have slack).
- **Sprint mode** — not enough time for even coverage; you must prioritize and
  explicitly accept some risk.

There's no magic threshold — use judgment. A rough heuristic: if you can't fit every
topic into the remaining sessions with time for a second look at weak ones, it's a
sprint. State which mode you chose and why (e.g. "18 topics, 4 days, ~2 sessions/day
→ sprint").

## Step 3a — Full-prep plan

Spread lectures/topics across the remaining days, **weighted by topic count per
lecture** (a 12-topic lecture gets more time than a 3-topic one). Give each a target
**review-by date**. Front-load weaker/`new` topics and topics with heavy exam-angle
weight so they get a second pass. Leave the last day or two for mixed review and
mock exams rather than first-time learning. Output as a dated schedule.

## Step 3b — Sprint plan

1. **Quick recall diagnostic** across all topics — 1–2 light questions each — to
   refresh and validate current status. Pay special attention to:
   - topics self-rated **high confidence** (overconfidence check — verify before
     trusting), and
   - any topic with **no recent review history** (status may be stale).
   Update the tracker from what you observe.
2. **Rank into three tiers** (name all three explicitly — nothing gets silently
   dropped):
   - **Must-cover** — weak/new topics with high exam-angle weight.
   - **Worth-a-look** — medium priority.
   - **Accept-risk** — explicitly deprioritized. Say so out loud so the student is
     making an informed bet, not discovering a gap in the exam.
3. **Allocate sessions** to must-cover first, then worth-a-look. Topics confirmed
   **strong** in the diagnostic get only a brief confirmation pass, not a full
   session. Output as a prioritized list with the accept-risk tier clearly labeled.

## Output shape

`study-plan.md` should make the mode obvious at the top (so the tutor can detect it),
then give the dated schedule (full-prep) or the triaged tiers (sprint), plus the
exam date and a one-line note on how to use it. Keep it skimmable. Fold in the
current tracker state rather than overwriting the student's progress.
