---
name: rubric-creator
description: >
  Creates analytic grading rubrics for university assignments and outputs them as
  downloadable .xlsx files. Use this skill ONLY when the user wants to CREATE or GENERATE
  a new rubric, scoring guide, or grading criteria grid from an assignment description,
  brief, or prompt. Trigger on phrases like: "create a rubric", "make a rubric", "build a
  rubric", "generate grading criteria", "design a scoring guide", or "how should I grade
  this assignment". Applies to any assignment type: lab reports, essays, written reports,
  code/technical projects, presentations, or research papers, at any university level.
  Do NOT trigger this skill for evaluating or grading student work against an existing
  rubric — that is a separate task.
---

# Rubric Creator

Generates an analytic rubric as a `.xlsx` file from an assignment description.

## Step 1 — Gather Input

Extract from the assignment (PDF, brief, or text):
- What students must deliver (drives the criteria)
- Total points — default **100**
- Language — auto-detect from assignment content (see `references/performance-levels.md`)

Do not ask the user to list criteria manually — derive them from the assignment.

## Step 2 — Design the Rubric

### Criteria & Weights

**Align criteria to assignment steps, not abstract themes.**
- Each step or section explicitly listed in the assignment must produce at least one criterion.
- Do not collapse multiple steps into one criterion.
- Do not add criteria that do not map to any step.
- Name each criterion after its originating step (e.g., "Paso 1 — …").

**A step with two distinct deliverables may be split into two criteria.**
- Only split when the two deliverables would be graded independently (e.g., a step that asks students to *group events* AND *explain how a concept differs*).
- Label both criteria with the originating step.
- Do not split arbitrarily.

**Do not add synthesizing or "holistic" criteria.**
- Avoid criteria that ask students to connect everything together (e.g., "diagnosis of business pain points") unless the assignment explicitly includes such a reflection step.
- Extra criteria inflate the rubric beyond what was assigned.

**Weights:**
- Distribute weights proportionally to complexity and effort.
- Weights **must sum exactly** to total points regardless of criteria count.

### Performance Level Descriptions
Read `references/performance-levels.md` for:
- Score mapping (100% / 60% / 0%)
- Description quality rules per level — including the rule against inventing numeric thresholds
- Language and register rules

## Step 3 — Generate the .xlsx

Build a JSON file matching this structure:

```json
{
  "language": "es",
  "criteria": [
    {
      "name": "Criterion Name",
      "cumple": "Full description...",
      "parcial": "Partial description...",
      "no_cumple": "None description...",
      "pts": 20
    }
  ]
}
```

Save the JSON to `/mnt/user-data/outputs/rubrica_<slug>.json`, then run:

```bash
python scripts/generate_rubric.py /mnt/user-data/outputs/rubrica_<slug>.json /mnt/user-data/outputs/rubrica_<slug>.xlsx
```

See `references/column-layout.md` for column definitions and formatting rules.

## Step 4 — Deliver

- Present the file with `present_files`.
- Report: criteria count and total points — nothing else.
