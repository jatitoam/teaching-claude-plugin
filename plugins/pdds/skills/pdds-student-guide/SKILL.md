---
name: pdds-student-guide
description: Transforms a teacher/instructor guide into a clean student-facing README. Use this skill whenever the user wants to convert a teacher guide into a student guide, adapt instructor notes for students, produce a student README from a demo guide, or strip timing and pause points to create a student-facing document. Trigger on phrases like "convert this to a student guide", "make a student README", "adapt this for students", "turn the teacher guide into something students can follow", or "create the student version of this guide".
---

# PDDS Student Guide Generator

Transforms a teacher guide (with timing, pause points, and instructor notes) into a clean student-facing README. The output is what goes in the repo the students clone — it tells them what they'll build, what commands to run, and what to expect at the end.

## What to strip

Remove everything that exists only for the instructor:

- Pre-Demo Checklist
- Start State table
- Timestamps (`[MM:SS]` markers)
- Pause points (`⏸ **PAUSE**`) and all quoted talking points
- Adaptation notes
- Key Callouts Summary
- Instructor asides ("for the demo:", "in production:", "remember:", etc.)
- References to `end/` directories
- Build/upload steps the student never runs (e.g., uploading the binary to S3 before class)

## What to keep and transform

| Teacher guide section | Student guide equivalent |
|---|---|
| Demo opening — what the code does | **What students learn** (bullet list) |
| Directory Layout | **Project structure** (same tree, shorter inline comments) |
| Pre-Demo Checklist (tools only) | **Prerequisites** |
| Demo Flow (commands only, no timing/talking) | **Demo workflow** (numbered steps) |
| Module Files end-state reference | Inline code blocks inside the relevant workflow step or a **Reference** section |
| Cleanup | Last numbered step in Demo workflow |
| Expected outputs (`curl` responses, `terraform output`) | Shown as `Expected output:` block under the relevant command |

## Step 1 — Read the teacher guide

Read the file the user points to. Identify:

1. The demo title and session name
2. The core concept being taught (from pause points — these reveal the WHY)
3. All commands the student will actually run (ignore build/upload steps done before class)
4. The expected outputs (curl responses, terraform outputs, kubectl output)
5. Any tools/CLIs the student needs installed

## Step 2 — Derive "What students learn"

Scan the pause points — they contain the teaching intent. Distill each pause into one bullet in plain language, written as a capability ("How to…", "Why…", "The difference between…"). Aim for 4–6 bullets. Drop anything that's purely instructor context.

Example — from a pause point about instance profiles:
> ⏸ "EC2 doesn't accept a role ARN directly. It needs an instance profile — a wrapper that EC2 understands."

Becomes:
> - Why EC2 instances need an instance profile (not a role ARN) to assume IAM permissions

## Step 3 — Build the student workflow

Walk the Demo Flow. For each step:

- Keep the section heading (without the timestamp)
- Keep all `bash` code blocks verbatim
- Show expected outputs as a code block labeled `Expected output:`
- Drop all talking points and instructor asides
- If a step has no commands (just narration), fold its context into the preceding or following step — one sentence max

Number the steps sequentially. The last step is always clean up.

## Step 4 — Write the README

Produce a single `README.md` using this structure:

```
# [Session Name] — [Demo Title]

[One sentence describing what is built and what stack it uses.]

## What students learn

- [bullet]
- [bullet]

## Project structure

\`\`\`
[file tree with short inline comments]
\`\`\`

## Prerequisites

- [tool + install link or command]

## Demo workflow

### 1. [Step title]

[One sentence of context, if needed.]

\`\`\`bash
[commands]
\`\`\`

Expected output:

\`\`\`json
[response]
\`\`\`

### 2. [Step title]
...

### N. Clean up

\`\`\`bash
[teardown commands]
\`\`\`

## Expected outcomes

By the end of this demo, students should be able to:

1. [concrete capability]
2. [concrete capability]
```

## Writing rules

- **No instructor voice.** Nothing that starts "For the demo:" or "In production:". Write for the person running the commands, not watching someone else run them.
- **Commands are exact.** Copy them verbatim from the teacher guide. Do not paraphrase or simplify commands.
- **One sentence of context per step.** If you need more than one sentence to explain a step, the step needs to be split or the command needs a comment.
- **Expected outputs are honest.** Show the actual JSON/table/text from the teacher guide. If the teacher guide shows a placeholder (e.g., `YOUR_IP`), keep it as a placeholder with a note.
- **Prerequisites = tools only.** Don't list "an S3 bucket" or "an AMI ID" — those are instructor concerns. List only software the student installs on their machine.
- **Expected outcomes derive from pause points.** Each pause point in the teacher guide is a learning goal. Restate it as a student capability.
