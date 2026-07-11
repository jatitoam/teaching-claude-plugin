<!--
  HANDOVER-SESSION TEMPLATE — course-factory / course-bootstrap
  ==============================================================
  Copied to <course>/.claude/refs/templates/handover-session.md. Content-facing headers are
  localized to course.language at bootstrap. The Session-Planning agent copies THIS to
  .claude/refs/handovers/handover-S<NN>.md and generates the artifact-checklist rows for the
  session's TYPE from PROTOCOL.md §10 (enabled skills only). DELETE bootstrap comments when
  generating; the checklist-generation guidance below stays as an instruction to Session-Planning.
-->
# Handover — Session <NN>: <Title>

> **Relay baton for this session.** Created by the Session-Planning agent and updated by every
> orchestrator. The next agent reads it to pick up exactly where the previous one left off.

## Header

- **Session:** S<NN> · **Date:** <…> · **Modality:** <…>
- **Type:** <one of course.yaml session_types>
- **Special case:** <e.g. first session has no recap → intro + setup; a delivery is due; a holiday
  shifts the lab to take-home; etc.>
- **AI tool(s) featured this session:** <set by Session-Planning>

## Artifact checklist

*(Session-Planning generates these rows for THIS session's type from `.claude/refs/PROTOCOL.md`
§10 — one row per **enabled** artifact in production order, with its file path (via
`naming.folders`) and its publication target. Examples of the row shapes per type below; keep only
enabled artifacts.)*

<!-- Session-Planning: pick the block matching the session type and drop skills not enabled.
     Slides ALWAYS come last in a class session so the deck reflects the exercises + any delivery. -->

**Class session (example rows):**

| # | Artifact | Status | File | Published |
|---|---|---|---|---|
| 1 | Session planning | ☐/✅ | `planning/S<NN>-plan.md` | n/a |
| 2 | Examples pack | ☐ | `examples/S<NN>/` (numbered `NN-*.md` + `00-index.md`) | n/a (instructor-only) |
| 3 | Exercise N.1 | ☐ | `exercises/S<NN>-ex1.md` (+ rubric json/xlsx) | ☐ Google Doc / Miro |
| 4 | Exercise N.2 | ☐ | `exercises/S<NN>-ex2.md` (+ rubric json/xlsx) | ☐ Google Doc / Miro |
| 5 | Submission assignments | ☐ | n/a — conductor creates them by hand in the portal | n/a |
| (6) | Delivery brief (if due) | ☐ | `project/D<n>-brief.md` | ☐ Google Doc + xlsx |
| 7 | Slides (whole-session deck) | ☐ | `slides/S<NN>-slides-spec.md` | ☐ Local HTML build + ☐ PDF |

**On-site / evaluation session (example rows):**

| # | Artifact | Status | File | Published |
|---|---|---|---|---|
| 1 | Session planning | ☐/✅ | `planning/S<NN>-plan.md` | n/a |
| 2 | Exam | ☐ | `exams/S<NN>-exam.md` | ☐ Google Doc |
| 3 | Lab (guide + rubric) | ☐ | `labs/S<NN>-lab.md` + `…-rubric.{json,xlsx}` | ☐ Google Doc + xlsx |
| 4 | Presentation/checkpoint guide | ☐ | `project/checkpoint-<n>-guide.md` + rubric | ☐ Google Doc + xlsx |

## Decisions made this session

- <decision · why> *(if relevant to the future, replicate it in the decisions log)*

## Notes for the next orchestrator

- <what the producer of the next artifact needs to know>

## Pending / blockers

- <unresolved things, waiting on the conductor, or dependent on an MCP / prerequisite>
