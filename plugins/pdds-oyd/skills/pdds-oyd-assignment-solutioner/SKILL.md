---
name: pdds-oyd-assignment-solutioner
description: >
  Use when a teacher of the OyD (Optimizaciones y Desempeño) course in the PDDS program at
  FISICC, Universidad Galileo asks to solve, demonstrate, or set up a step-by-step reference
  solution for a student assignment in a git repository. Do NOT trigger for assignments from
  other courses.
---

# PDDS Assignment Solutioner

## Overview

Build a teacher-facing reference repository for a PDDS course assignment. Each task in the assignment becomes exactly one git commit, so students can walk the history commit-by-commit. The README is both a pedagogical guide and a running evidence log — it grows in place, one commit at a time.

## Commit Structure (strict)

**One commit per step. No extra commits. No "finalize" or "polish" commits.**

| Commit | Contents |
|--------|----------|
| `step 1` | README.md (scaffolded with all sections but evidence placeholders), required config files (e.g. `main.tf`), `.gitignore` |
| `step 2` | Run Task 1 commands → update README evidence in place → commit |
| `step 3` | Run Task 2 commands → update README evidence in place → commit |
| `step N` | One task per commit until done |

Evidence for a step must land in the **same commit** as the step. Never pre-create sections and fill them later across separate commits.

## Commit Message Format

Step 1 uses `scaffold` instead of a task number:

```
step 1: scaffold - <short description>

<one-sentence explanation of what files are created and why>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

All subsequent steps use the task number:

```
step N: task M - <short description>

<one-sentence explanation of what was done and why>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## .gitignore

Always create a `.gitignore` in step 1. It must include the standard ignores for whatever technology the assignment uses, plus:

```
# Claude Code working directory — always exclude
.claude/
```

Claude Code creates a `.claude/` directory in every working directory. It must always be gitignored.

**Terraform-specific:** Do NOT ignore `.terraform.lock.hcl`. The lock file must be committed so that all collaborators use the same provider versions. Only ignore the `.terraform/` directory (downloaded provider binaries).

## Kubernetes-specific notes

**Namespace ordering:** `kubectl apply -f k8s/` processes files alphabetically. If `configmap.yaml` or `deployment.yaml` appears before `namespace.yaml`, the apply fails with `namespaces "X" not found` on a fresh cluster. Always apply the namespace manifest first, then apply the directory:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

The second apply will show the namespace as `unchanged` — that is expected and correct.

**Local images:** Use `imagePullPolicy: Never` in the Deployment when the image is built locally and no registry is involved. Without it, Kubernetes will try to pull from Docker Hub and fail.

**Screenshot evidence:** When the assignment requires a browser screenshot (e.g. `evidence/k8s-run.png`), use `screencapture -R` to capture a specific screen region rather than the full desktop:

```bash
# Resize browser window to known bounds first
osascript -e 'tell application "Google Chrome" to set bounds of front window to {50, 50, 1100, 750}'
sleep 1
screencapture -R "50,50,1050,700" evidence/k8s-run.png
```

## Terraform tfvars layout

When an assignment uses tfvars files, place them under an `envs/` directory, one subdirectory per environment:

```
envs/
├── dev/
│   └── dev.tfvars
└── prod/
    └── prod.tfvars
```

Reference them with the full path in plan commands: `terraform plan -var-file=envs/dev/dev.tfvars`.

## README Structure

The README is the teacher's artifact. It serves two roles:
1. **Pedagogical commentary** — explains WHY each step matters, not just WHAT commands to run
2. **Evidence log** — captures real command output and answers to assignment questions

```markdown
# Exercise N.N — <Title>

**Course:** Optimizaciones y Desempeño ...

---

## Teacher's Intent

[2–4 paragraphs explaining the learning objectives. What mental model are students building? What production mistake does this exercise prevent? What confusions does each task resolve?]

---

## Step-by-Step Implementation

[One subsection per step. Each subsection has:
- The commit label
- What files change and why
- The teaching point for that step]

---

## Evidence

[One subsection per step with actual command output and question answers.
Populated commit-by-commit — placeholders are fine in step 1, replaced by real output in each subsequent commit.]
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Not adding `.claude/` to `.gitignore` | Always include it — Claude Code creates this dir |
| Creating a "finalize" or "summary" commit | Stop after the last task commit |
| Filling evidence sections in a later commit | Evidence goes in the same commit as the step |
| Kubernetes: `kubectl apply -f k8s/` fails on fresh cluster | Apply namespace first: `kubectl apply -f k8s/namespace.yaml && kubectl apply -f k8s/` |
| Kubernetes: image pull errors with local image | Set `imagePullPolicy: Never` in the Deployment container spec |
