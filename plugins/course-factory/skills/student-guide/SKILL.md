---
name: student-guide
description: >
  Transforms a teacher-facing demo guide or instructor script (with timing markers, pause
  points, and instructor asides) into a clean student-facing README — the document that ships
  in the repo or folder students actually work from. Part of the course-factory harness
  pipeline for building university course material. Invoke DELIBERATELY within a course
  material-production pipeline (the working folder has .claude/refs/course.yaml); do NOT
  auto-trigger for generic "write a README" or "explain this code" requests.
---

# Student guide generator

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder
> names, enabled artifacts, tool stack, publishing targets); (3) read
> `.claude/refs/PROTOCOL.md` — the course's contract; (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md` if it exists; (5) read
> `.claude/refs/shared-context.md`. If `student-guide` is not in `artifacts.enabled`, STOP and
> warn the conductor. Write ALL generated content in `course.language`.

**Tier:** Sonnet (drafts the transform) · Opus (orchestrates and judges — audits the result
against the acceptance criteria before accepting it).

Transforms a teacher guide (with timing, pause points, and instructor notes) into a clean
student-facing README. The output is what goes wherever students consume the material — it
tells them what they'll build, what commands or steps to run, and what to expect at the end.

## What you produce

- A single student-facing guide file — typically `README.md` in the deliverable's own folder
  (e.g. a demo repo, a `<folders.examples>/` or `<folders.exercises>/` entry per
  `course.yaml naming.folders`). The exact path comes from wherever the conductor points you at
  the source teacher guide; this skill does not invent a new folder convention.

## Inputs (read, don't duplicate)

- The teacher guide or instructor script the conductor points you to — a demo write-up,
  session guidance script, or similar artifact built for instructor use, produced earlier in
  the pipeline (e.g. by an `examples`-style skill).
- `.claude/refs/PROTOCOL.md` and `course.yaml` for language and naming conventions only — the
  *content* of the guide comes entirely from the source document.

## What to strip

Remove everything that exists only for the instructor:

- Pre-demo / pre-class checklists
- Start-state or end-state tables
- Timestamps (`[MM:SS]` markers)
- Pause points (`⏸ **PAUSE**` or equivalent) and all quoted talking points
- Adaptation notes ("if running short on time…", "for a smaller cohort…")
- Key-callouts / recap summaries written for the instructor
- Instructor asides ("for the demo:", "in production:", "remember to mention:", etc.)
- References to instructor-only `end/` or "solution" directories
- Setup/build/upload steps the student never runs themselves (anything done before class by
  the instructor)

## What to keep and transform

| Teacher guide element | Student guide equivalent |
|---|---|
| Opening — what the material builds/demonstrates | **What students learn** (bullet list) |
| Directory / project layout | **Project structure** (same tree, shorter inline comments) |
| Pre-demo checklist (tools only) | **Prerequisites** |
| Walkthrough steps (commands only, no timing/talking) | **Workflow** (numbered steps) |
| End-state / solution file references | Inline code blocks inside the relevant step, or a **Reference** section |
| Teardown / cleanup | Last numbered step in the workflow |
| Expected outputs (command output, API responses, tool output) | Shown as `Expected output:` block under the relevant command |

## Step 1 — Read the teacher guide

Read the file the conductor points you to. Identify:

1. The title and session/unit it belongs to
2. The core concept being taught (from the pause points — these reveal the WHY)
3. All commands or actions the student will actually perform (ignore setup/upload steps done
   before class by the instructor)
4. The expected outputs (verbatim, from the teacher guide)
5. Any tools the student needs installed to follow along

## Step 2 — Derive "What students learn"

Scan the pause points — they contain the teaching intent. Distill each pause into one bullet
in plain language, written as a capability ("How to…", "Why…", "The difference between…"). Aim
for 4–6 bullets. Drop anything that's purely instructor context.

Example — from a pause point about a design decision:
> ⏸ "The service doesn't accept the raw credential directly. It needs a wrapper the platform
> understands."

Becomes:
> - Why the service needs a wrapper (not the raw credential) to gain the right permissions

## Step 3 — Build the student workflow

Walk the teacher guide's walkthrough section step by step. For each step:

- Keep the section heading (without the timestamp)
- Keep all code/command blocks verbatim
- Show expected outputs as a code block labeled `Expected output:`
- Drop all talking points and instructor asides
- If a step has no commands (just narration), fold its context into the preceding or following
  step — one sentence max

Number the steps sequentially. The last step is always clean-up/teardown.

## Step 4 — Write the guide

Produce a single guide using this structure:

```
# [Session/unit name] — [Title]

[One sentence describing what is built and what stack or tools it uses.]

## What students learn

- [bullet]
- [bullet]

## Project structure

\`\`\`
[file tree with short inline comments]
\`\`\`

## Prerequisites

- [tool + install link or command]

## Workflow

### 1. [Step title]

[One sentence of context, if needed.]

\`\`\`
[commands or actions]
\`\`\`

Expected output:

\`\`\`
[response]
\`\`\`

### 2. [Step title]
...

### N. Clean up

\`\`\`
[teardown steps]
\`\`\`

## Expected outcomes

By the end of this, students should be able to:

1. [concrete capability]
2. [concrete capability]
```

## Writing rules

- **No instructor voice.** Nothing that starts "For the demo:" or "In production:". Write for
  the person running the steps, not watching someone else run them.
- **Commands are exact.** Copy them verbatim from the teacher guide. Do not paraphrase or
  simplify commands or code.
- **One sentence of context per step.** If you need more than one sentence to explain a step,
  the step needs to be split, or the command needs an inline comment instead.
- **Expected outputs are honest.** Show the actual output/response text from the teacher
  guide. If the teacher guide shows a placeholder, keep it as a placeholder with a note.
- **Prerequisites = tools only.** Don't list instructor-side setup (accounts, provisioned
  resources, credentials) — list only software/tools the student installs on their own
  machine.
- **Expected outcomes derive from pause points.** Each pause point in the teacher guide is a
  learning goal. Restate it as a student capability.
- **Language:** write the guide in `course.language` (per the bootstrap blockquote); this
  section's English examples are illustrative only.

## Acceptance criteria (self-audit)

- [ ] No timing markers, pause-point talking points, checklists, or instructor asides remain
      anywhere in the output.
- [ ] Every command/code block is copied verbatim from the source teacher guide.
- [ ] "What students learn" has 4–6 bullets, each derived from a pause point and phrased as a
      student capability.
- [ ] Every workflow step that produces output shows an honest `Expected output:` block.
- [ ] Prerequisites list only student-installed tools, not instructor-side setup.
- [ ] The guide follows the fixed skeleton (title line, What students learn, Project
      structure, Prerequisites, Workflow, Expected outcomes).
- [ ] Content is written in `course.language`.

## Close

1. Write the guide to the path the conductor specified (or the natural location alongside the
   source teacher guide); self-audit against the criteria above.
2. **Update the handover** (if one applies to this artifact): note the guide's path and any
   judgment calls made while stripping/transforming content.
3. **Add lessons** to `shared-context.md` (e.g. recurring instructor-only patterns worth
   flagging early next time).
4. **Record decisions**, if any were made, in `<folders.sources>/<sources.decisions>`.
5. **Emit the closing block** per `templates/next-agent-prompt.md`: a short summary for the
   conductor, then the **PROMPT FOR THE NEXT AGENT** — the next skill comes from the course
   PROTOCOL's artifact sequence for this session/artifact type; do not hardcode a specific next
   slug.
