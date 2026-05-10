---
name: pdds-session-builder
description: >
  Use this skill ONLY when building instructional session materials for the course
  "Optimizaciones y Desempeño / Cloud Deployment Automation" (PDDS, FISICC,
  Universidad Galileo), taught by Tito Alvarez with TA Abner Pérez. Triggers on
  explicit phrases like "build session N", "prepare session N", "let's do session N",
  "work on session N", or "next session" in the context of this specific course.
  Produces session deliverables in this fixed order: demo script(s) → exercise specs
  (DOCX) → deck (PPTX via pptxgenjs) → code examples (zip). Each step is
  approval-gated. Do NOT trigger for project deliveries (use pdds-delivery-builder),
  generic PPTX creation, or sessions from other courses.
---

# PDDS Cloud Deployment Automation — Session Builder

Produces the complete set of instructional materials for one session: demo scripts,
exercise DOCX files, a PowerPoint deck, and zipped code examples.

---

## 1. Trigger Conditions

This skill applies when ALL of the following are true:

- The conversation is about the PDDS course at FISICC / Universidad Galileo
- The user says "build", "prepare", "work on", or "let's do" + "session N" (N = 1–10)
  OR refers to "the next session" with enough context to infer N

Do NOT use this skill for:
- Project deliveries — use `pdds-delivery-builder` instead
- Generic PowerPoint, DOCX, or exercise creation for any other course
- Grading or evaluating student work

---

## 2. Approval-Gated Sequence — mandatory, always in this order

Each step follows this exact pattern — no exceptions:

```
Produce deliverable(s) → present to user → produce handover → call present_files → STOP
```

The agent must stop after calling `present_files`. The next step begins only after the
user provides explicit approval ("Go" or equivalent) in a new message.

### Steps

1. **Outline** — present full session structure in chat (time blocks, demo placement,
   exercise titles, K8s extension if applicable).
   → Read `references/session-structure.md` and `references/defect-checklist.md` first.
   → Produce and present handover. Stop. Wait for "Go".

2. **Demo script(s) + code example zips** — one `DEMO.md` per demo (numbered steps +
   talking points) **and** the full zip for each demo (`start/` + `end/` + DEMO.md),
   produced together in the same step.
   → Read `references/demo-spec.md` and `references/defect-checklist.md` first.
   → Produce and present handover. Stop. Wait for "Go".

3. **Exercise specs** — exercises as Google Docs.
   → Read `references/exercise-spec.md`, `references/exercise-gdoc-spec.md`, and
     `references/defect-checklist.md` first.
   → Generate the JSON spec for each exercise, run `scripts/create-exercise-gdoc.py`
     for each, and present the resulting Google Doc URLs.
   → Produce and present handover. Stop. Wait for "Go".

4. **Deck** — PowerPoint via pptxgenjs.
   → Read `references/deck-spec.md`, `scripts/pptx-code-box.js`,
     `scripts/pptx-step-slide.js`, and `scripts/pptx-callout-slide.js` first.
   → Session complete. No further handover required.

Structural corrections to outlines (e.g., repositioning exercises, removing blocks,
re-ordering demos) must be applied *before* any content is developed.

---

## 2a. Handover Document

Produced after every approved step. Single source of truth for any agent picking up
mid-stream.

**Path:** `/mnt/user-data/outputs/session<N>-handover.md`
**Delivery:** via `present_files` — always the last action in a turn.

**The handover is a stopping artifact.** After calling `present_files`, the agent must
stop. Do not proceed to the next step in the same turn.

### Required sections

1. **Session identity** — session number, date, topic, modality, K8s extension flag,
   delivery milestone if relevant
2. **Completed steps** — table of all steps with ✅ / ⬜ status and a one-line note
   per completed step
3. **Next step** — exact step name, what it produces, the reference files to read first,
   the output path, the validation command, and the approval gate that follows
4. **Approved outline** — concept thread, full agenda table, demo roster table
5. **Exercise separation matrix** — full matrix with copy-paste blocking rationale
6. **Style decisions** — which block+demo style was chosen per demo and why; any
   instructor corrections applied
7. **Constraints honored** — table of course constraints applied, their source, and
   confirmation they were respected
8. **File inventory** — absolute paths of all files produced so far; "None" if outline only
9. **Pending decisions** — any open question the next agent must resolve; "None" if all confirmed

### Format rules

- Markdown only; bold labels, no colors
- Every table must have a header row
- File paths must be exact and absolute
- Produce after **every** approved step, even if the same agent continues

---

## 3. Course Constants (hardcoded — never ask the user)

```
Instructor:     Tito Alvarez  (augusto.alvarez@galileo.edu)
TA:             Abner Pérez   (abner.perez@galileo.edu)
Program:        PDDS — FISICC — Universidad Galileo
Course name:    Optimizaciones y Desempeño / Cloud Deployment Automation
Schedule:       Thursdays 6–9 PM, GMT-6
Stack:          Terraform, GitHub Actions, optional Kubernetes/EKS
Footer text:    "Optimizaciones y Desempeño  ·  Cloud Deployment Automation  ·  PDDS · FISICC · Universidad Galileo"
```

### Session map

| # | Date | Topic | K8s ext? |
|---|------|-------|----------|
| 1 | Apr 23 | IaC Philosophy + Terraform Foundations | No |
| 2 | Apr 30 | Kubernetes Basics + GitHub Actions CI | No (K8s IS the content) |
| 3 | May 7 | Compute Automation + EKS Provisioning | Yes (10–15 min) |
| 4 | May 14 | Storage + Database + Remote State | No |
| 5 | May 21 | **On-site** — Partial Exam + Mid Presentations | — |
| 6 | May 28 | Networking Automation | Yes (10–15 min) |
| 7 | Jun 4 | Async Infrastructure + Full CD Pipeline | No |
| 8 | Jun 11 | IAM as Code + Security Automation | Yes (10–15 min) |
| 9 | Jun 18 | Observability Automation | Yes (10–15 min) |
| 10 | Jun 25 | **On-site** — Final Exam + Final Presentations | — |

Sessions 5 and 10 are on-site exam/presentation sessions — no session materials to build.

---

## 4. Output File Structure

```
session<N>/
├── Session<N>_<Topic>.pptx
├── demos/
│   ├── demo-<N>-<topic>/
│   │   ├── DEMO.md
│   │   ├── start/
│   │   └── end/         ← always includes optional terraform-ci.yml
│   └── demo-<N>-<topic>.zip
└── exercises/
    ├── exercise-<N>-1.json          ← intermediate spec (kept for reference)
    ├── Exercise_<N>_1 (Google Doc)  ← URL presented to user after script run
    ├── exercise-<N>-2.json
    ├── Exercise_<N>_2 (Google Doc)
    └── Exercise_<N>_3 (Google Doc)  ← optional, e.g. EKS track
```
