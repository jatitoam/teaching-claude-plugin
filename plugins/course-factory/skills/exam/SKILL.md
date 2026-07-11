---
name: exam
description: Produces a lightweight printable concept-check exam for an evaluation session — numbered items (multiple-choice plus a few short-reasoning items) with a separate answer key, plus publication. Part of the course-factory harness pipeline for building university course material. Invoke DELIBERATELY within a course material-production pipeline (the working folder has .claude/refs/course.yaml); do NOT auto-trigger for generic quiz, test, or question-bank requests.
---

# Exam (printable concept check)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder
> names, enabled artifacts, tool stack, publishing targets); (3) read
> `.claude/refs/PROTOCOL.md` — the course's contract; (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md` if it exists; (5) read
> `.claude/refs/shared-context.md`. If `exam` is not in `artifacts.enabled`, STOP and warn
> the conductor. Write ALL generated content in `course.language`.

**Tier:** Sonnet (writes the items) · Haiku (formats the printable exam + builds the key) ·
Opus (you orchestrate, calibrate difficulty/coverage, and judge).

## What you produce

- **`<folders.exams>/S<NN>-exam.md`** (or `P<n>-exam.md` for a term-partial exam, per the
  course's naming convention) — a **closed-book, no-devices concept check**: numbered items,
  printable, with a clearly separated **Answer Key** section (with brief justifications).

This is the lightweight, single-session concept-check exam. It is **not** the right tool when
the conductor wants N shuffled distribution-ready versions — see §HANDOFF below.

## Exam conventions

- **Individual, closed-book, no devices.** Duration and point value come from the session
  plan / `course.yaml evaluation.weights` for this exam slot — do not hardcode a duration or
  point total; state whatever the plan specifies.
- **Tests CONCEPTUAL reasoning, NOT syntax or coding-from-memory.** Never ask a student to write
  code or recall exact commands/UI paths verbatim. Item types:
  - **interpret an AI output** (given a model's answer, what's right/wrong/missing);
  - **read a simple data structure** (what does this data say / what field is off);
  - **evaluate a spec, brief, or prompt** (what's weak, ambiguous, or missing);
  - **reason about a trade-off** (which option fits, and why).
- **Combine item types:** mostly **multiple-choice** (one correct answer, **plausible
  distractors** built from common conceptual mistakes — not absurd), plus **a few
  short-reasoning items** (2–4 sentences), or an option-only exam if the course's exam
  convention (PROTOCOL.md) calls for that instead.
- **Coverage:** per the session plan's exam scope (which sessions/topics this exam covers) —
  read it from the plan, never invent a scope.
- Difficulty matches the course's audience (per its glossary) and stays concept-level. Plain
  language, no unexplained jargon; avoid ambiguity, double negatives, and "all/none of the
  above" unless intentional.

## Inputs (read, don't duplicate)

- The session plan (`<folders.planning>/S<NN>-plan.md`) — the plan's exam scope (sessions and
  topics to cover, duration, point value).
- `sources.session_briefs` → the briefs of the covered sessions (topics, teaching blocks,
  exercises) and the course's exam grading-category notes.
- `sources.glossary` — shared vocabulary for the course's audience.

## Process

1. **(Opus) Set coverage + difficulty.** Map a balanced spread of items across the covered
   sessions' key topics, at the audience's level. Decide the item mix (multiple-choice count +
   short-reasoning count) so the exam fits the plan's stated duration.
2. **Delegate to Sonnet** the drafting of items across the covered topics:
   - Clear **multiple-choice** items — one correct answer, plausible distractors (common
     conceptual errors), homogeneous in length/style.
   - A few **short-reasoning** items grounded in one of the item types above, each answerable in
     2–4 sentences.
   - No code-writing or command-recall items.
3. **Delegate to Haiku** the printable formatting + the separate answer key: a header (name /
   ID / section / date), instructions (closed-book, no devices, duration), numbered items, and a
   distinct Answer Key section with the correct option per MC item and a brief justification (+
   a model-answer sketch and what earns credit for each short-reasoning item).
4. **Judge (Opus):** verify each MC item has exactly one correct answer and homogeneous options;
   that coverage matches the plan's scope; that it stays concept-level (no syntax); and that the
   length is realistic for the stated duration.

## Output format (`S<NN>-exam.md`)

- **Header** — name / ID / section / date fields + instructions (closed-book, no devices,
  duration, point value) — printable.
- **Items** — numbered; multiple-choice with labeled options (A–D); short-reasoning items with
  answer space.
- **Answer Key** — a clearly separated section (own heading, at the end): correct option per MC
  item with a brief justification, and a model-answer sketch + credit notes per short-reasoning
  item.

## Acceptance criteria

- [ ] Concept-level, not syntax / coding-from-memory — no code-writing or command-recall items.
- [ ] Covers the right sessions/topics per the plan's exam scope, balanced.
- [ ] Realistic for the plan's stated duration; individual, closed-book, no-devices.
- [ ] Item mix present: multiple-choice with plausible distractors (+ a few short-reasoning
      items, if the course's exam convention includes them).
- [ ] Each MC item: one correct answer + homogeneous options; no ambiguity/double-negatives.
- [ ] Answer Key is a separate section, correct, with brief justifications.

## HANDOFF — when N shuffled versions with a ready answer key are needed

This skill produces **one** printable exam for a single session/room. If the conductor instead
wants **N shuffled versions** of a multiple-choice exam (different question and option order per
version) with a consolidated answer key ready for distribution — a different, heavier need than
this skill covers — **do not duplicate that pipeline here**. Hand off to the `exam-creator`
plugin instead:

1. `exam-creator:mcq-generator` — generates the MCQ item bank as structured JSON from course
   content.
2. `exam-creator:exam-version-generator` — shuffles questions and options into N versions and
   builds the answer key.
3. `exam-creator:gdocs-exam-exporter` — exports the versions + scoring guide to Google Docs.

**Prerequisite:** the `exam-creator` plugin must be installed for this handoff to apply. If it
is not installed, tell the conductor and stop — do not attempt to replicate the shuffling
pipeline inside this skill.

## Publication (this skill owns its pipeline end-to-end)

After the **human validates** the `.md`:

- **Publish the exam** `S<NN>-exam.md` → Google Doc via the `publish-google-doc` engine (into
  the exams Drive subfolder per `publishing.drive.subfolders`), structured for printing. Record
  the link in the handover.
- **Answer key stays SEPARATE:** note to the conductor that the key section must be printed and
  kept apart from the student copies (do not hand it out with the exam).

## Close

1. Write `S<NN>-exam.md` (items + separate Answer Key) and self-audit against the criteria.
2. **Human gate (md-first):** the conductor validates the `.md`. *(End the turn with a summary;
   do not publish until the green light.)*
3. **Publish** the exam to a printable Google Doc; remind the conductor to keep the key
   separate.
4. **Update the handover** (check the exam box; note the Doc link), **add lessons** to
   `shared-context.md` (tier calibration, traps), **record decisions** in
   `<folders.sources>/<sources.decisions>` if any were made, and **emit the closing block** per
   `templates/next-agent-prompt.md`: a human summary, then the PROMPT FOR THE NEXT AGENT — the
   next artifact slug comes from the course PROTOCOL's artifact sequence for this session type
   (do not hardcode a specific next slug).
