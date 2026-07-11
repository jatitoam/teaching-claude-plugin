---
name: readings
description: Produces the short session reading (~10-15 min, non-technical) that feeds the next session's warm-up exercise, plus its publication. Part of the course-factory harness pipeline for building university course material. Invoke DELIBERATELY within a course material-production pipeline (the working folder has .claude/refs/course.yaml); do NOT auto-trigger for generic reading, article, or summary-writing requests.
---

# Readings (short session reading)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder
> names, enabled artifacts, tool stack, publishing targets); (3) read
> `.claude/refs/PROTOCOL.md` — the course's contract; (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md` if it exists; (5) read
> `.claude/refs/shared-context.md`. If `readings` is not in `artifacts.enabled`, STOP and warn
> the conductor. Write ALL generated content in `course.language`.

**Tier:** Sonnet (produces) · Opus (you orchestrate and judge).

## What you produce

**`<folders.readings>/S<NN>-reading.md`** — a reference reading for the session, **~10–15
minutes of reading (~2000–2800 words)**, written in `course.language`, for the course's stated
audience (non-technical unless `course.yaml course.audience` says otherwise). Rich in examples
but with no filler. **Feeds the next session's warm-up/review exercise** and some in-class
exercises.

## Inputs (read, don't duplicate)

- The session plan (`<folders.planning>/S<NN>-plan.md`) → the reading's spec (topic + points to
  cover).
- `sources.session_briefs` for the session's thematic arc.
- `sources.glossary` — use its canonical vocabulary.
- Any prior-year source material the course PROTOCOL points to for this artifact (open it via
  the handover's source-pointer table before writing, if the course keeps one — read it
  targeted/scoped, never whole, if it's large). Reuse what's good **without copying** its tone —
  this reading stays short per the length target above.

## Process

1. **Delegate to Sonnet** the writing, with these constraints in the agent's prompt:
   - **~10–15 min of reading (~2000–2800 words)**, clear non-technical language, local/relevant
     business examples where it helps. Rich but no filler (distill any dense source material,
     don't copy it).
   - Structure: **title + subtitle** (a tagline) · one hook ("why this matters to me") · **4–6
     sections with subheadings** (each point from the plan's spec developed with an everyday +
     business example) · one **integrating mini-example** · **5–7 "key takeaways"** at the end
     (feeds the next session's warm-up exercise) · a **quick glossary** of the canonical terms
     used.
   - Respect the course's glossary (canonical terms from `sources.glossary`).
   - The reading itself is informational (not submitted for a grade), but its content is the
     basis for the following session's graded warm-up, per the course's AI-use/grading policy
     for that exercise.
2. **Judge** against the acceptance criteria; iterate with Sonnet or correct directly if
   something falls short.

## Acceptance criteria

- [ ] ~10–15 min of reading (~2000–2800 words); no filler; readable by the course's stated
      non-technical audience.
- [ ] Covers **all** points from the plan's spec, each developed with examples.
- [ ] Uses glossary terms correctly (no invented synonyms).
- [ ] Closes with 5–7 clear key takeaways (for the next session's warm-up exercise) + a quick
      glossary.
- [ ] No dubious invented content; data is verifiable or clearly marked as illustrative.

## Publication (this skill owns its pipeline end-to-end)

This skill produces the `.md`, self-audits, and — after the conductor's md-first gate —
publishes the Google Doc in the same run.

- **Licensing:** the source course this skill was generalized from attaches a **CC BY-NC-SA
  4.0** license to readings by default. Treat the license as a **config question**: use whatever
  `course.yaml` / the course's own decision states for readings' license (check
  `sources.decisions` and the course PROTOCOL first); if the course hasn't decided, default to
  CC BY-NC-SA 4.0 as the pattern this skill was built from, and note in the closing summary that
  it is adjustable per course.
- Publish via the `publish-google-doc` engine (into the readings Drive subfolder per
  `publishing.drive.subfolders`); the engine applies the license line, any heading-level shift,
  and the manual-steps reminder. The source `.md` keeps standard Markdown hierarchy (H1 title,
  H2 sections).

## Close

1. Write the `.md`, check the handover's checklist item for this artifact, note any lesson
   learned.
2. **Human gate (md-first):** the conductor validates the `.md`. *(End the turn with a summary;
   do not publish until the green light.)*
3. **Publish to Google Doc** via the `publish-google-doc` engine (see §Publication for the
   license note).
4. **Add lessons** to `shared-context.md` if any, **record decisions** in
   `<folders.sources>/<sources.decisions>` if any were made (e.g. a license decision), and
   **emit the closing block** per `templates/next-agent-prompt.md`: a human summary, then the
   PROMPT FOR THE NEXT AGENT — the next artifact slug comes from the course PROTOCOL's artifact
   sequence for this session type (do not hardcode a specific next slug).
