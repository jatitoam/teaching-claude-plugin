---
name: assignment-solutioner
description: >
  Builds a teacher-facing reference-solution repository for a hands-on course assignment,
  with exactly one git commit per assignment task so students can walk the solution
  commit-by-commit. Part of the course-factory harness pipeline for building university
  course material. Invoke DELIBERATELY within a course material-production pipeline (the
  working folder has .claude/refs/course.yaml); do NOT auto-trigger for generic "solve this"
  or "write me code" requests, or for building a git repo unrelated to a course assignment.
---

# Assignment solutioner

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder
> names, enabled artifacts, tool stack, publishing targets); (3) read
> `.claude/refs/PROTOCOL.md` — the course's contract; (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md` if it exists; (5) read
> `.claude/refs/shared-context.md`. If `assignment-solutioner` is not in `artifacts.enabled`,
> STOP and warn the conductor. Write ALL generated content in `course.language`.

**Tier:** Sonnet (executes each step and writes the README) · Opus (orchestrates and judges —
audits the commit sequence and evidence before accepting it).

## Overview

Build a teacher-facing reference repository for a course assignment. Each task in the
assignment becomes exactly one git commit, so students can walk the history commit-by-commit.
The README is both a pedagogical guide and a running evidence log — it grows in place, one
commit at a time.

This skill is domain-agnostic: the assignment may involve infrastructure-as-code, container
orchestration, a data pipeline, a web app, or any other hands-on deliverable. Wherever the
mechanics below reference a specific technology, treat it as an illustrative example of the
pattern — apply the equivalent for whatever stack the assignment actually uses.

## Commit structure (strict)

**One commit per step. No extra commits. No "finalize" or "polish" commits.**

| Commit | Contents |
|--------|----------|
| `step 1` | README.md (scaffolded with all sections but evidence placeholders), required config/starter files, `.gitignore` |
| `step 2` | Run Task 1 → update README evidence in place → commit |
| `step 3` | Run Task 2 → update README evidence in place → commit |
| `step N` | One task per commit until done |

Evidence for a step must land in the **same commit** as the step. Never pre-create sections
and fill them in later across separate commits.

## Commit message format

Step 1 uses `scaffold` instead of a task number:

```
step 1: scaffold - <short description>

<one-sentence explanation of what files are created and why>
```

All subsequent steps use the task number:

```
step N: task M - <short description>

<one-sentence explanation of what was done and why>
```

Commit authorship (trailers, sign-off, co-author lines) follows the conductor's own git
conventions for this repo — do not add a hardcoded authorship trailer of your own.

## .gitignore

Always create a `.gitignore` in step 1. It must include the standard ignores for whatever
technology the assignment uses, plus:

```
# Claude Code working directory — always exclude
.claude/
```

Claude Code creates a `.claude/` directory in every working directory. It must always be
gitignored.

## Domain-specific gotchas (examples — adapt to the assignment's actual stack)

These are illustrative patterns from prior courses; carry over the ones relevant to this
assignment's actual technology, and add the assignment's own known gotchas the same way.

- **Infrastructure-as-code lock files:** if the tool uses a dependency/provider lock file
  (e.g. Terraform's `.terraform.lock.hcl`), commit it — don't ignore it — so all collaborators
  resolve the same versions. Only ignore the downloaded-binaries/cache directory.
- **Environment-specific variable files:** when an assignment uses per-environment config
  files, place them under an `envs/` directory, one subdirectory per environment, and
  reference them with their full path in the relevant commands.
- **Ordering dependencies:** if applying a set of manifests/resources in one shot fails
  because one resource depends on another that hasn't been created yet (e.g. a namespace or
  a schema), apply the dependency first, then the rest — and note in the README that a
  second, broader apply showing the dependency as "unchanged"/"no-op" is expected and correct.
- **Local-only artifacts:** if the assignment builds something locally with no external
  registry/store involved (e.g. a locally built container image), make sure the runtime
  config says so explicitly (e.g. an image-pull policy of "never pull remotely") — otherwise
  the tool will try to fetch from a remote source and fail.
- **Screenshot evidence:** when the assignment requires a screenshot as evidence, capture a
  specific window/region rather than the full desktop, so the evidence file is legible and
  reproducible. macOS example (set the window bounds first, then capture that region):
  ```bash
  osascript -e 'tell application "Terminal" to set bounds of front window to {50, 50, 1050, 700}'
  screencapture -R "50,50,1050,700" evidence/step-3.png
  ```

## README structure

The README is the teacher's artifact. It serves two roles:
1. **Pedagogical commentary** — explains WHY each step matters, not just WHAT commands to run
2. **Evidence log** — captures real command output and answers to assignment questions

```markdown
# Assignment <ID> — <Title>

**Course:** <course.name>

---

## Teacher's Intent

[2–4 paragraphs explaining the learning objectives. What mental model are students building?
What real-world mistake does this exercise prevent? What confusions does each task resolve?]

---

## Step-by-Step Implementation

[One subsection per step. Each subsection has:
- The commit label
- What files change and why
- The teaching point for that step]

---

## Evidence

[One subsection per step with actual command output and question answers.
Populated commit-by-commit — placeholders are fine in step 1, replaced by real output in each
subsequent commit.]
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Not adding `.claude/` to `.gitignore` | Always include it — Claude Code creates this dir |
| Creating a "finalize" or "summary" commit | Stop after the last task commit |
| Filling evidence sections in a later commit | Evidence goes in the same commit as the step |
| Applying a full manifest set fails on a fresh environment | Apply the dependency resource first, then the rest |
| Local-only artifact triggers a remote fetch | Set the runtime to never pull remotely for that artifact |

## Acceptance criteria (self-audit)

- [ ] Exactly one commit per assignment task, plus one `scaffold` commit — no extra commits.
- [ ] Every step's evidence is committed in the same commit as the step itself.
- [ ] `.gitignore` exists from step 1 and excludes `.claude/`.
- [ ] README has both a Teacher's Intent section and a per-step Evidence section, populated
      commit-by-commit.
- [ ] Domain-specific gotchas relevant to this assignment's actual stack are documented and
      handled (ordering, lock files, local-only artifacts, etc. as applicable).
- [ ] Content is written in `course.language`.

## Close

1. Verify the full commit history matches the strict one-commit-per-step structure; self-audit
   against the criteria above.
2. **Update the handover** (if one applies): note the repo location, task count, and any
   assignment-specific gotchas documented.
3. **Add lessons** to `shared-context.md` (recurring stack-specific traps worth flagging early
   next time).
4. **Record decisions**, if any were made, in `<folders.sources>/<sources.decisions>`.
5. **Emit the closing block** per `templates/next-agent-prompt.md`: a short summary for the
   conductor, then the **PROMPT FOR THE NEXT AGENT** — the next skill comes from the course
   PROTOCOL's artifact sequence for this session/artifact type; do not hardcode a specific next
   slug.
