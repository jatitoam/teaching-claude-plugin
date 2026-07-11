---
name: class-exercises
description: Produces the in-class exercise guides for a course session (exercises/S<NN>-ex<slot>.md, one per exercise), each a numbered-steps guide yielding a submittable result, published via publish-google-doc (or materialized as Miro boards when the course's tool stack enables Miro) and submitted through the course's publishing.portal. Part of the course-factory harness pipeline for building university course material. Invoke DELIBERATELY within that pipeline (the working folder has .claude/refs/course.yaml), after the Examples pack (if enabled) and before Slides; do NOT auto-trigger for generic "exercises", practice sets, or worksheets.
---

# Class exercises

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor folder
> containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder names, enabled
> artifacts, tool stack, publishing targets); (3) read `.claude/refs/PROTOCOL.md` — the course's
> contract, including its exercise convention; (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md`; (5) read `.claude/refs/shared-context.md`. If
> `class-exercises` is not in `artifacts.enabled`, STOP and warn the conductor. Write ALL generated
> content in `course.language`.

**Tier:** Sonnet (writes each guide) · Opus (you orchestrate and judge).

## What you produce

- `<folders.exercises>/S<NN>-ex<slot>.md` — one **exercise guide** per exercise spec'd in the
  session plan (typically two; the count and slot numbering come from `planning/S<NN>-plan.md` and
  the course's exercise convention in PROTOCOL.md).
- **One grading rubric per exercise** — `<folders.exercises>/S<NN>-ex<slot>-rubric.{json,xlsx}`
  (same folder), generated with the plugin **`evaluation-rubrics:rubric-creator`** and **embedded
  as a table in the guide** (the guide has NO prose "how it's graded" section — the rubric table
  IS the grading section). Every rubric carries the course's **standard penalties block**
  (`.claude/refs/grading-penalties.md`, injected as the rubric's `penalties` array) plus a
  lateness row, outside the additive 100.
- If `publishing.portal` is set: a **reminder to the conductor** to create one submission
  assignment per exercise on that portal before class — the portal has no API, so this is always a
  manual conductor step; the skill produces no submission Sheet.
- If `tool_stack.miro.enabled` is true and the course PROTOCOL routes exercises through Miro
  instead of Docs: see §Miro-exercise variant below — the guide becomes a canvas spec and the
  publication step materializes Miro boards instead of Google Docs.

## Exercise convention (from the course's PROTOCOL.md — read it before assuming numbers)

- **Numbered by session:** label them **`<session>.<slot>`** (e.g. session 1 → 1.1 / 1.2) in the
  guide titles and the portal assignment names. Filenames stay `S<NN>-ex<slot>.md`.
- The exercise **count, duration, and point value per session** are defined in the session plan and
  the course's PROTOCOL — do not assume a fixed count; read it from `planning/S<NN>-plan.md`. Each
  exercise is grounded in that session's topic and reinforces it (exercises are not project
  components unless the course explicitly says so).
- **Each exercise is a WRITTEN GUIDE** — numbered steps, each producing a submittable result →
  published as a Google Doc via **`publish-google-doc`** (default), or as a Miro board when the
  Miro variant applies (see below).
- **Submission goes through `publishing.portal`** (per `course.yaml`). Portals typically have no
  API: the skill **reminds the conductor** to create the assignment(s) by hand; it never invents a
  submission mechanism the course doesn't have (e.g. no ad hoc spreadsheet, no chat-app links,
  unless PROTOCOL.md says otherwise). If the course ties the submission's timestamp to attendance,
  say so in the guide's "What to submit" section, per PROTOCOL.md.
- Grading follows the course's rubric convention (see below) — never write a prose "how it's
  graded" paragraph when a rubric table is required.

## Inputs

- `planning/S<NN>-plan.md` — the plan's exercise specs and their time-slot placement.
- The **drafted exercises for this session** in `<folders.sources>/<sources.session_briefs>` (the
  current best version, provisional — re-review against the finalized teaching blocks and adjust).
- `<folders.sources>/<sources.glossary>` — shared vocabulary for the course's audience.
- `.claude/refs/grading-penalties.md` — the course's standard penalties block (single source; use
  its exercise adaptation for the "Accessible submission" row).

## Process

For **each** exercise, delegate to **Sonnet** the writing of a guide with:

- a **one-line objective** tied to the session's single most important, session-specific topic;
- **a handful of numbered steps** (the source guides use ~4–6), each producing a **concrete result
  the student can submit**;
- a clear **"What to submit"** section naming the submission mechanism from `publishing.portal`
  (or the Miro-variant equivalent, see below) and any attendance-linkage the course defines;
- a **"Done" criterion** (how the student knows the exercise is complete);
- scoped to fit the time block the plan assigned it, placed right after the teaching block that
  enables it;
- when the submission is an assembled report (e.g. one PDF of the steps' results), an early tip
  telling students to **keep one working document open from step 1 and paste each step's result
  as they go** — so exporting/submitting at the end takes a minute instead of a scramble.

Then **build each exercise's rubric** (BEFORE the human gate — the conductor reviews guides with
their rubrics embedded, not prose grading):

- Generate with the plugin **`evaluation-rubrics:rubric-creator`** (xlsx+json).
- **2–3 criteria maximum**, out of **100** (grades scale to the exercise's point value from
  `evaluation.weights`) — group the guide's steps into 2–3 gradeable clusters; criteria weights
  sum to 100.
- The rubric's **`penalties` block** (outside the additive 100 — never as criteria) carries the
  standard penalty rows copied from `.claude/refs/grading-penalties.md`, adapted to this
  submission's mechanism (e.g. "Accessible submission" phrased for the actual portal/format used),
  **plus** a lateness row per the course's late-submission rule (PROTOCOL.md).
- Write `<folders.exercises>/S<NN>-ex<slot>-rubric.json` + `.xlsx` (same folder as the guides), and
  **embed the rubric as Markdown tables in the guide** (additive criteria + the penalties block),
  replacing any "How it's graded" prose.

**Judge (Opus):** audit each guide against the Acceptance criteria before accepting it; iterate or
redo with Sonnet if it fails. Ground everything in plain language (per the glossary), no
unexplained jargon.

## Miro-exercise variant (config-gated — only when `tool_stack.miro.enabled`)

When the course's tool stack routes exercises through Miro instead of Google Docs, each exercise's
guide still specs the instructions, but its **materialization** is a Miro board, not a Doc:

- The guide's `.md` additionally specs a **canvas layout** per exercise: what zones/elements each
  student's canvas/frame has (e.g. a labeled table, a mind-map skeleton, capture frames), written
  so the `miro-boards` engine can stamp it directly. Name which pattern in the `miro-boards`
  catalog fits (table/zones + sticky notes · mind map · capture frames · or another pattern you
  propose).
- **Reuse-vs-build gate:** if an equivalent exercise exists from a prior course offering, resolve
  reuse-vs-build **with the conductor** before materializing — do not default to one choice alone;
  record the decision in the spec and handover.
- **Materialize as a final step of this same skill**, after the human validates the `.md`: invoke
  the **`miro-boards`** skill (mechanical stamping, Haiku tier) to build the **template board
  first**, stop for the conductor to approve it, then clone to the course's other sections/spaces
  (`tool_stack.miro.spaces`) per that skill's process. The `$MIRO_TOKEN` comes only from the
  environment — never write it to a file.
- Submission in this variant is participation on the board itself (name+ID on a canvas), verified
  per the course's attendance rule — not a portal upload. Say so explicitly in the guide.
- **No penalties-block or rubric change is implied** by the Miro variant unless the course's
  grading convention for these exercises differs (check PROTOCOL.md).

When `tool_stack.miro.enabled` is false or absent, ignore this section entirely — exercises publish
as Google Docs via `publish-google-doc`.

## Publication (this skill owns its pipeline end-to-end)

After the **human validates** the `.md` guide(s):

> **Delegation is MANDATORY here** (per the course's conductor-set publication rule, if one
> exists — check `.claude/refs/shared-context.md`). The orchestrator (Opus/lead) **never calls
> `Google_Drive.create_file` (or the Miro API) itself.** Spawn a **Haiku agent** (Agent tool,
> `model: haiku`) that does ALL the mechanical publication: the `.md`→publish transform (per
> `publish-google-doc`'s Format convention) **and** the Drive MCP calls, or — in the Miro variant —
> the `miro-boards` engine's mechanical build call. Give it: the source file paths, the exact
> titles, the destination folder/board target, the transform rules, and tell it to load the
> needed tools via ToolSearch. It returns each created artifact's ID/link. The orchestrator only
> **verifies** (correct type, correct folder/board) and **records** the links.

1. **Publish each guide** as a Google Doc via **`publish-google-doc`** (into the exercises Drive
   subfolder from `publishing.drive.subfolders`), or materialize it via `miro-boards` in the Miro
   variant — mechanical part by the Haiku agent above. Record each link/board ID in the handover.
2. **Remind the conductor** (in the closing summary) to create the portal assignment(s) if
   `publishing.portal` is set — no API, so this is a manual conductor step.

Do not re-upload local files that already sync to Drive — use the MCP only to create the Docs.

## Acceptance criteria

- [ ] One exercise guide per exercise spec'd in the session plan, correctly labeled
      `<session>.<slot>`.
- [ ] Each is grounded in the session's key topic and fits its planned time block.
- [ ] Each has **numbered steps that each yield a submittable result**, a **"What to submit"**
      section naming the actual submission mechanism (`publishing.portal` or the Miro variant),
      and a **"Done"** criterion.
- [ ] Each guide has a **rubric** (2–3 criteria, out of 100) embedded as a table, with its
      `-rubric.json` + `.xlsx` in the exercises folder — no prose "how it's graded" section.
- [ ] Each rubric's **penalties block** carries the course's standard rows from
      `.claude/refs/grading-penalties.md` (adapted to the actual submission format) **plus** a
      lateness row — all outside the additive 100.
- [ ] If `publishing.portal` is set: no invented submission mechanism; the portal-assignment
      reminder for the conductor is in the closing summary.
- [ ] If `tool_stack.miro.enabled`: canvas layout spec'd per exercise, reuse-vs-build gate resolved
      with the conductor, template approved before cloning to other sections/spaces.
- [ ] If Miro is not enabled: no Miro/canvas mechanics appear anywhere.

## Close

1. Write the guide(s) in `<folders.exercises>/`; self-audit against the criteria.
2. **Update the handover:** check the exercise boxes; note the Doc/board links, the portal-
   assignment reminder for the conductor, and anything the next orchestrator needs.
3. **Add lessons** to `.claude/refs/shared-context.md` (tier calibration, traps).
4. Record any new design decision in `<folders.sources>/<sources.decisions>`.
5. **Emit the closing block** (`.claude/refs/templates/next-agent-prompt.md`): a short summary for
   the human, then the **PROMPT FOR THE NEXT AGENT** — whichever artifact comes next in this
   session type's sequence per `PROTOCOL.md` (e.g. a delivery note if one is due this session, then
   `slides` — `slides` is typically the LAST artifact of a session so the deck can surface these
   exercises; leave the guides final and note in the handover what the deck should show per
   exercise, objective and what to submit).
