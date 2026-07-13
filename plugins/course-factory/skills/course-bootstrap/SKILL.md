---
name: course-bootstrap
description: >
  Produces a complete per-course material-production harness (course.yaml + PROTOCOL.md + START.md
  + shared-context.md + grading-penalties.md + handover/next-agent templates + material folders +
  root CLAUDE.md + a starter settings.local.json) from a structured interview. Part of the
  course-factory harness pipeline for building university course material. Invoke DELIBERATELY when
  a conductor wants to CREATE a new course harness from scratch ("bootstrap a course", "set up a new
  course harness", "create a class from scratch", "scaffold a course"); do NOT auto-trigger for
  generic course-planning, syllabus, or "make me a class" requests. Course-agnostic.
---

# Course Bootstrap

> **Bootstrap (this skill is the one exception to the usual startup):** you run from an **empty or
> near-empty target course folder that does NOT yet have `.claude/refs/course.yaml`** — you are the
> skill that CREATES it. Do **not** look for a course root or a handover; there is none yet.
> Confirm the target folder path with the conductor, then run the interview (§Process) and generate
> the harness into it. Every generated content file is written in the language the interview
> settles (`course.language`); file/folder names and skill slugs stay English. After you finish,
> the first real agent is **`/session-planning` for S01** — no handover applies to this skill.

**Tier:** Opus orchestrates the interview, judges the settled facts for internal consistency, and
writes every generated file itself (these are precise, load-bearing files whose current state it
knows — not delegated). Haiku/Bash may run mechanical folder creation. No cheap-agent authoring:
the harness files are the contract every future agent obeys.

## What you produce

Into the target course folder (paths shown with the default `naming.folders`; use the values the
interview settles):

| File | From reference | Notes |
|---|---|---|
| `.claude/refs/course.yaml` | `references/course-yaml-schema.md` | the config seam; **validate** (see below) |
| `.claude/refs/PROTOCOL.md` | `references/protocol-template.md` | the course's contract — settled facts, session shapes, artifact sequences, tier map; only enabled skills |
| `.claude/refs/START.md` | `references/start-template.md` | conductor's guide; launch prompts in `course.language`, English slugs |
| `.claude/refs/shared-context.md` | `references/shared-context-seed.md` | empty-but-structured; tier table seeded, lessons empty |
| `.claude/refs/grading-penalties.md` | `references/grading-penalties-template.md` | the standard penalties block, rows the interview selects |
| `.claude/refs/templates/handover-session.md` | `references/templates/handover-session.md` | headers localized where content-facing |
| `.claude/refs/templates/next-agent-prompt.md` | `references/templates/next-agent-prompt.md` | headers localized where content-facing |
| `.claude/refs/handovers/` | — | created empty (Session-Planning fills it per session) |
| material folders | `references/folder-scaffold.md` | only for enabled artifacts + the always-created ones |
| `CLAUDE.md` (root) | — | short orientation file (see §Generate → CLAUDE.md) |
| `.claude/settings.local.json` | — | starter permissions allowlist (see §Generate → settings) |

**Never** write a token/secret into any generated file — `MIRO_TOKEN` and any API key live in the
conductor's environment only.

## Inputs (read, don't duplicate)

- `references/course-yaml-schema.md` — **read it FIRST**; it defines every field you must fill.
- `references/*.md` and `references/templates/*.md` — the templates you instantiate.
- Whatever the conductor already has: an existing syllabus, session briefs, glossary, decisions log
  — note them in `sources:` and place/point to them under `<folders.sources>/`. If a source of
  truth does not exist yet, record it as a **to-author** item in the final report (do NOT invent
  its contents).
- `references/pdds-salvage/` — optional battle-tested material from a retired technical course:
  `session-structure.md` (outline principles, block+demo styles), `demo-spec.md` (hands-on demo
  folders), `defect-checklist.md` (per-deliverable defect gates). For technical/hands-on courses,
  offer in the interview to adapt the defect checklist into the generated PROTOCOL's artifact-close
  guidance.

## Process

### 1. Interview (structured; ask in these groups, adapt follow-ups)

Ask the conductor, in order — batch related questions, confirm before generating:

1. **Course identity & language.** Display name, short code (`XX-2026-II`), program/faculty/
   university, audience (count, profile, technical level), instructor + TAs, and the **content
   language** (`en`/`es` — every generated artifact is written in it).
2. **Schedule & sections.** Total session count, session length, meeting day/time, timezone, dates.
   Does the course run **multiple sections with different times**? If so capture them as
   `schedule.sections` (`[{id, time}]`) → the slides get dual-schedule Ⓐ/Ⓑ speaker-note headers.
3. **Session types & timeline shapes.** The set of session-type names (common: `virtual`/`onsite`/
   `final`; or `class`/`workshop`/`exam`/`project`) and **which session numbers** fall in each
   (every session in exactly one list). For each type, the **minute-by-minute timeline shape**
   (opening/sacred block, teaching blocks, exercise blocks, break, close) and its timeline rules
   (multiples of 5, any sacred empty opening block, min exercise duration, any content-minute
   ceiling).
4. **Evaluation model.** The activity names and their **weights (must sum to 100)**, plus how each
   weight derives into point values, and any delivery→presentation map. **Cross-check on the spot:**
   every weight key must have a producing artifact in `artifacts.enabled` (step 5) — if a weight has
   no producer (e.g. a `project` weight with `project-delivery` disabled), ask the conductor who/what
   produces it before generating.
5. **Artifact set to enable.** Walk the conductor through the available slugs and confirm
   `artifacts.enabled`: `session-planning` (always), `examples`, `class-exercises`, `readings`,
   `homework`, `slides`, `lab`, `exam`, `practical-exam`, `project-delivery`, `presentation-guide`,
   `recap-signup`, `publish-google-doc`, `publish-course-docs`, `miro-boards`, `student-guide`,
   `assignment-solutioner`. Only enabled skills appear in PROTOCOL/START and get folders. For
   `homework`, also settle its **cadence** (per-session vs. occasional) and its position in the
   session's artifact sequence.
6. **Tool stack.** Slides engine (`local-html`), the **student tool stack** (in adoption order),
   whether **Miro** is used (→ `team_id`, `board_prefix`, `spaces`, and the **canvas-count rule per
   board** — e.g. a fixed number or a multiple of enrollment), and whether **forced-failure/ollama**
   demos are wanted (`ollama_forced_failure`).
7. **Publishing targets & submission channels.** Drive `course_folder_id` (if known) + any per-type
   subfolder IDs; the student-submission **portal** name (or none); and the **concrete submission
   mechanism per graded artifact type** (e.g. exercises = one PDF per exercise uploaded to the
   portal before end of class, with any attendance linkage; homework = channel + deadline rule) —
   the protocol's exercise/homework conventions and the penalties wording need these.
8. **Sources of truth.** Which of syllabus / session briefs / glossary / decisions the conductor
   **already has** (record filenames in `sources:`) vs. which must be **authored later** (flag in
   the report; never fabricate their contents).
   **8b. Prior-offering material.** Ask whether material from a **previous offering** of the
   course exists to use as reference (docs folders, Canva designs, LMS exports, slide decks,
   repos, readings embedded in per-class docs…). For each source capture: the **kind**, its
   **exact location** (path, Canva team/search terms, URL), any **reading constraints** (e.g.
   big files → offset/limit reads only), and whether the sessions **drifted in order or title**
   between offerings. If any source exists: include the **prior-offering review block** in the
   generated PROTOCOL §4 (include-if, with the mandatory **confirm-with-conductor** rule — see
   the template), and recommend seeding a **catalog/index file** in `<folders.sources>/` (one
   table per source kind, IDs/paths verified once) so agents never re-search.
9. **Penalties.** Which standard penalty rows apply (good-presentation deduction; accessible-
   submission validity; AI-declared-&-explainable integrity), their magnitudes, and the real
   submission channel/wording — for `grading-penalties.md`.

If a fact is missing and the conductor can't settle it, leave an explicit `[placeholder]` + a note
in the report. **Never invent** facts, names, dates, or point values.

### 2. Generate

Write each file from its reference, replacing every `{{placeholder}}` with the settled facts and
**deleting every `<!-- bootstrap: ... -->` comment**. Emit only enabled artifacts in every list;
drop `INCLUDE-IF <slug>` sections whose slug isn't enabled and renumber.

- **`course.yaml`** — fill the schema. **Validate before writing:** (a) `evaluation.weights` sum to
  **exactly 100**; (b) every session number appears in **exactly one** `session_types` list and the
  union covers `1..sessions`; (c) `session_types` names match the timeline shapes you write in
  PROTOCOL §8; (d) `artifacts.enabled` uses only real slugs; (e) no secrets anywhere; (f) **every
  `evaluation.weights` key has a producing artifact in `artifacts.enabled`** (or an explicit
  conductor-confirmed note in PROTOCOL §5 about who produces it); (g) every timeline shape sums to
  `schedule.session_length_min` in multiples of 5 — if the interview's shape doesn't, resolve it
  with the conductor (or fix minimally and flag the fix as an unconfirmed decision in PROTOCOL §8,
  START.md, and shared-context.md).
- **`PROTOCOL.md`** — instantiate `protocol-template.md`: settled facts (§5), session shapes (§8),
  the tier map (§6, one row per enabled skill), the artifact sequences (§10, enabled skills only),
  and the §2 bootstrap contract pointing to `.claude/refs/course.yaml` as the root marker and to
  **plugin** skills (`/<slug>` from the `course-factory` plugin — there is no `.claude/skills/`).
  Keep ALL mechanics verbatim in spirit (roles, artifact cycle, single-source-of-truth/no-
  redundancy, md-first→same-skill-publishes with the Drive-MCP/Docs-API limitation text, mandatory
  artifact close). §9 exercise convention, §9b Miro model, and §12 examples convention are
  include-if their slug is enabled; the §4 **prior-offering review block** is include-if the
  interview (8b) captured prior-year sources.
- **`START.md`** — instantiate `start-template.md`: the 3-line idea, the first-agent launch prompt
  (in `course.language`), per-session-type flows (enabled skills only), the conductor's
  prerequisites (`.pptx` per session, Drive IDs, portal assignments, `MIRO_TOKEN` if Miro), and the
  gate role.
- **`shared-context.md`** — from `shared-context-seed.md`: fill fixed conventions, seed the tier
  table (drop disabled rows), leave per-session lessons empty, seed open-technical-items with the
  Drive-MCP limitation to re-verify.
- **`grading-penalties.md`** — from `grading-penalties-template.md`: the rows the interview picked,
  adapted to the course's channel and language, as the JSON `penalties`-array pattern for
  `evaluation-rubrics:rubric-creator`.
- **`templates/handover-session.md`, `templates/next-agent-prompt.md`** — copy, localizing
  content-facing headers to `course.language`; keep the checklist-generation guidance.
- **Material folders** — per `folder-scaffold.md`: always-created (`.claude/refs/templates`,
  `.claude/refs/handovers`, `<folders.sources>`, `<folders.planning>`) + one per enabled artifact.
  Do not pre-create per-session files.
- **Root `CLAUDE.md`** — short: what this folder is (the course's material factory); the harness in
  one paragraph (session-by-session, one artifact at a time, fresh Opus agent per artifact,
  documents are the baton); pointers to `.claude/refs/PROTOCOL.md`, `START.md`, and `course.yaml`;
  and the key rules — **single source of truth is this folder** (nothing in external/global
  `~/.claude*`), **md-first + human gate**, and **skills are deliberate, plugin-provided, never
  auto-triggered**. Model it on a short course CLAUDE.md; keep it tight.
- **`.claude/settings.local.json`** — a starter allowlist (see below).

### 3. settings.local.json (starter permissions)

Write a minimal allowlist that lets the harness run without repeated prompts. Base rules (always):

```json
{
  "permissions": {
    "allow": [
      "mcp__claude_ai_Google_Drive__create_file",
      "mcp__claude_ai_Google_Drive__search_files",
      "mcp__claude_ai_Google_Drive__read_file_content",
      "mcp__claude_ai_Google_Drive__get_file_metadata",
      "Read(<HOME>/.claude-personal/plugins/cache/teaching-claude-plugin/**)",
      "WebFetch(domain:docs.google.com)"
    ]
  }
}
```

- Replace `<HOME>` with the conductor's real home path (resolve `$HOME` on this machine); the rule
  lets skills read the plugin-cached scripts (`generate_rubric.py`, `estampar.py`, etc.).
- **Only if `tool_stack.miro.enabled`** add the Miro **read** tools and the curl rule:
  `mcp__claude_ai_Miro__user_who_am_i`, `mcp__claude_ai_Miro__board_search_boards`,
  `mcp__claude_ai_Miro__board_list_items`, `mcp__claude_ai_Miro__context_get`,
  `mcp__claude_ai_Miro__context_explore`, `mcp__claude_ai_Miro__board_create`, and
  `Bash(curl -s https://api.miro.com/*)`.
- **Only if `tool_stack.ollama_forced_failure`** add `Bash(ollama list *)`.
- **NEVER** put a token, bearer string, or any secret in any rule (no `export MIRO_TOKEN=…`, no
  `Authorization: Bearer …`). The token is read from the environment at run time.

## Cross-plugin prerequisites

- **`evaluation-rubrics` (required)** for any rubric-bearing artifact enabled (`class-exercises`,
  `lab`, `homework`, `project-delivery`, `presentation-guide`): rubrics are built with
  `evaluation-rubrics:rubric-creator`, which renders the `penalties` array. `openpyxl`
  required.
- **`exam-creator` (optional)** if the course wants **multi-version shuffled MCQ** exams
  (`exam-version-generator` + `gdocs-exam-exporter`); the base `exam` slug alone produces a single
  sheet.
- No other plugin is required: publishing goes through the Google Drive MCP connector
  (`publish-google-doc`) and slides build locally — the `google-drive-creation` plugin is NOT a
  dependency of this harness.

Note any missing prerequisite plugin in the final report.

## Acceptance criteria (self-audit)

Before reporting done, verify:

- [ ] `course.yaml` validates: weights **sum to 100**; every session in **exactly one**
  `session_types` list; union covers all sessions; `session_types` names match PROTOCOL §8 shapes;
  `artifacts.enabled` are real slugs; **every weight key has an enabled producing artifact** (or a
  conductor-confirmed note); every shape sums to the session length; **no secrets** anywhere.
- [ ] Every generated file has **zero `{{placeholders}}`** and **zero `<!-- bootstrap: ... -->`
  comments** left.
- [ ] PROTOCOL/START/handover checklists/folders list **only enabled** artifacts; include-if
  sections for disabled slugs are gone and sections renumbered.
- [ ] Prior-offering review block present in PROTOCOL §4 **iff** interview 8b captured prior-year
  sources — always carrying the **confirm-with-conductor** rule (offerings drift in order/title);
  absent otherwise.
- [ ] PROTOCOL §2 points to `.claude/refs/course.yaml` as the root marker and to **plugin** skills
  (`/<slug>`), not `.claude/skills/`.
- [ ] The Drive-MCP/Docs-API limitation text, the md-first→same-skill-publishes doctrine, the tier
  map, and the mandatory artifact close all survive in PROTOCOL.
- [ ] Content files are in `course.language`; slugs, folder names, and paths are English.
- [ ] The folder tree matches `folder-scaffold.md` for the enabled set; `handovers/` exists and is
  empty.
- [ ] `settings.local.json` has the base rules; Miro/ollama rules present **iff** enabled; **no
  token** in any rule.
- [ ] Root `CLAUDE.md` is short and points to PROTOCOL/START/course.yaml with the key rules.

## Close (report to the conductor)

This skill has no next-artifact handover. Finish with a report:

```
✅ Course harness bootstrapped: <course_name> <course_code>
Generated:
  .claude/refs/course.yaml, PROTOCOL.md, START.md, shared-context.md, grading-penalties.md
  .claude/refs/templates/{handover-session.md, next-agent-prompt.md}
  .claude/refs/handovers/ (empty)
  <material folders created>
  CLAUDE.md, .claude/settings.local.json
Validated: weights=100 · every session typed once · enabled artifacts only · no secrets

Manual prerequisites (yours):
  - Drive folder IDs to fill in course.yaml / verify on first publish: <course_folder_id + subfolders>
  - Per-session slide templates: drop slides/S<NN>-template.pptx before each Slides build
  - Portal assignments: <portal> has no API — create each assignment by hand
  - MIRO_TOKEN env var (only if Miro enabled) — set in your environment, never in a file
  - Sources of truth to author (if any): <syllabus / session briefs / glossary / decisions still missing>
  - Cross-plugin prerequisites: evaluation-rubrics for rubrics; exam-creator (optional) for multi-version MCQs

Next: launch the first real agent —
```

```
/session-planning — Session 01, course <course_name> <course_code>. Start from zero:
follow .claude/refs/PROTOCOL.md §2 (bootstrap) and the session handover.
```
