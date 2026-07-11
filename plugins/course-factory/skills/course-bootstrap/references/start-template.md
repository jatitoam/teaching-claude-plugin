<!--
  START TEMPLATE — course-factory / course-bootstrap
  ===================================================
  Copied into <course>/.claude/refs/START.md and filled from the interview + course.yaml.
  DELETE every <!-- bootstrap: ... --> comment from the generated file. Launch prompts inside
  code blocks are written in course.language (the conductor pastes them); skill slugs stay
  English. Include-if sections are emitted only for enabled skills.
-->
# START — Conductor's guide (how to operate the harness)

> For **you** (the instructor / conductor). Explains how to launch each agent and how a session
> flows. The agents read `PROTOCOL.md`, not this file.

## The idea in 3 lines

You produce the material **one session at a time, one artifact at a time**. For each artifact you
launch **one fresh Opus agent** with a short prompt. The agent produces, self-audits, and **ends by
giving you the prompt for the next one**. You validate each `.md` before moving on.

## Launching the FIRST agent of a session

Open a new chat (Claude Code, in the course folder or a subfolder) and paste:

<!-- bootstrap: write the launch prompt body in course.language; keep /session-planning and the
     path literal. {{course_label}} = "<course_name> <course_code>". -->
```
/session-planning — Session <NN>, course {{course_label}}. Start from zero:
follow .claude/refs/PROTOCOL.md §2 (bootstrap) and the session handover.
```

The Session-Planning agent **creates the session handover** and defines which artifacts apply. When
it finishes it gives you the prompt for the next agent. And so on.

## Session flows

<!-- bootstrap: one block per session-type in course.yaml session_types, listing the ENABLED
     skills in production order with the file each produces (paths via naming.folders). Mirror the
     ET/TIC examples below but keep only enabled skills + this course's folder names. -->

**{{class_session_type_name}} session:**

```
{{class_session_flow}}
```
<!-- bootstrap example (drop skills not enabled):
1. Session-Planning → planning/S<NN>-plan.md   (+ creates the handover + Examples manifest)
2. Examples         → examples/S<NN>/ (numbered NN-*.md + 00-index.md)   (instructor-only)
3. Class-exercises  → exercises/S<NN>-ex1.md + -ex2.md + rubrics → (Google Docs / Miro)
4. [Project-delivery brief]  → only if a delivery is due that session
5. Slides (LAST)    → slides/S<NN>-slides-spec.md → (local HTML build + shareable PDF)
-->

**{{eval_session_type_name}} session:**

```
{{eval_session_flow}}
```
<!-- bootstrap example:
1. Session-Planning → planning/S<NN>-plan.md
2. Exam             → exams/S<NN>-exam.md → (Google Doc)
3. Lab              → labs/S<NN>-lab.md + labs/S<NN>-rubric.{json,xlsx} → (Google Doc + xlsx)
4. Presentation-guide → project/checkpoint-<n>-guide.md + rubric → (Google Doc + xlsx)
-->

{{final_session_flow_block}}
<!-- bootstrap: if a "final" type exists, add its short flow (Session-Planning →
     Presentation-guide (Final)). Reference PROTOCOL.md §10 for all types. -->

See `PROTOCOL.md` §10 for all session types and their sequences.

## Course-level artifacts (not tied to a weekly session)

<!-- bootstrap: include only the enabled course-level skills. -->
{{course_level_launch_block}}
<!-- bootstrap examples (keep enabled ones):
- **Project deliveries D1–Dn** — launch `/project-delivery` for each delivery when you want it
  built. Produces the formal brief (Google Doc) + rubric (xlsx).
- **Recap sign-up sheet** — launch `/recap-signup` ONCE, right after S1. Builds the
  capacity-capped sign-up Google Sheet + the recap guidance.
- **Course docs** — publish with `/publish-course-docs` (or `/publish-google-doc`) when validated;
  re-publish if they change.

```
/project-delivery — Delivery D<n>, course {{course_label}}. Start from zero:
follow .claude/refs/PROTOCOL.md §2 (bootstrap).
```
-->

## Your role in each step

- You read the `.md` the agent produced. If it's good → launch the next prompt. If not → tell the
  agent what to fix (same chat) or relaunch with instructions.
- **You are the gate.** Nothing publishes until you validate the `.md`.

## Prerequisites you own

- **Slides template:** per session, drop a reference **`.pptx`** at
  `{{slides_folder}}/S<NN>-template.pptx` (defines colors/fonts/backgrounds/layouts; may change per
  session). Without the `.pptx`, the build step can't start — the Slides agent will produce the
  content `.md` and alert you. The deck is built as **local HTML** in `{{slides_folder}}/S<NN>-build/`
  (no external hosting; you open `index.html` directly). After you approve the HTML, the agent
  exports a **shareable, notes-free PDF** per deck into `{{slides_folder}}/`.
<!-- bootstrap: {{sheets_prereq}} = " and Google Sheets (from CSV via contentMimeType text/csv)"
     when a Sheet-producing artifact (e.g. recap-signup) is enabled; empty string otherwise. -->
- **Google Drive:** the folder is Drive-synced, so files created locally travel to Drive on their
  own. The Drive **MCP connector** creates **Google Docs**{{sheets_prereq}} (which have no
  local-file equivalent). Do **not** also upload local files (`.xlsx`, `.md`, images) via the
  connector — the folder sync already carries them; a second upload creates a duplicate.
  - **Drive folder IDs** (`publishing.drive.course_folder_id` + per-type subfolder IDs) — resolve
    and record them in `shared-context.md` on first publish. The `course_folder_id` is yours to
    fill in `course.yaml` if not set.
- **{{portal_name}} assignments:** {{portal_name}} has no API — the exercise/delivery skills
  **remind you** to create each assignment by hand. *(Drop this line if `publishing.portal` is
  empty.)*
<!-- bootstrap: INCLUDE-IF miro-boards enabled — else drop. -->
- **Miro token:** the exercise-board build needs `MIRO_TOKEN` set as an **environment variable** on
  your machine (`export MIRO_TOKEN=…`). It is **never** written to any file in the folder. Set the
  Miro `team_id` / `board_prefix` / `spaces` in `course.yaml`.

## Where everything lives

- **The skills are PLUGIN skills** (from the `course-factory` plugin) — invoke with `/<slug>`.
  There is no `.claude/skills/` folder here.
- `.claude/refs/` — the machinery (`course.yaml`, `PROTOCOL.md`, this file, `shared-context.md`,
  `grading-penalties.md`, `templates/`, `handovers/`).
- `{{sources_folder}}/` — **sources of truth** (syllabus, session briefs, glossary, decisions).
  Not duplicated.
- `{{deliverable_folders}}` — the deliverables per type, one file per session (or per
  delivery/presentation).
