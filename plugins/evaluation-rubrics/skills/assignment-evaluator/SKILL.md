---
name: assignment-evaluator
description: >
  Evaluates student or group assignment submissions against an existing rubric and records
  results in a cumulative grades .xlsx file. Use this skill when the user provides a student
  submission (PDF, docx, md, or txt) and a rubric, and wants to score or grade the work. Trigger on phrases
  like: "evaluate this submission", "grade this assignment", "score this lab", "add this
  student to the grades file", "evaluate against the rubric", or any request to assess
  student work using a rubric. Each invocation appends one row to the grades file.
  Do NOT trigger this skill for creating or generating rubrics — that is a separate task.
---

# Assignment Evaluator

Reads a student/group PDF submission, scores it against a rubric xlsx, and appends one row
to a cumulative grades file.

## Step 1 — Gather Inputs

Required each time:
1. **Submission file** — the student or group's work. Supported formats:
   - PDF — read directly; name extracted from cover page.
   - `.docx` — read via the docx skill; name extracted from cover page.
   - `.md` / `.txt` — read as plain text; no cover page expected (see name rules below).
2. **Rubric xlsx** — produced by rubric-creator; defines criteria and weights.
3. **Assignment brief** (PDF or text) — provides context for what was expected.

Derived automatically:
- **Student/group name** — resolution order:
  1. Explicitly provided in the user's prompt → use it, no questions asked.
  2. Present in the submission filename (e.g., `lab01_grupo3.pdf`) → use it, confirm with user if ambiguous.
  3. Found on a cover page (PDF or docx only) → extract it.
  4. None of the above → ask the user before proceeding. Do not guess.
- **Output directory**:
  - If the user specified a destination folder, use that folder.
  - Otherwise, default to the **same folder as the submission file**.
- **Evaluations subfolder**: row JSONs are always stored in `<output_dir>/evaluations/`.
  Create this subfolder if it doesn't exist.
- **Grades output filename**: derive from the assignment name or rubric filename.
  - Pattern: `grades_<assignment_slug>.xlsx` in `<output_dir>`.
  - If a file with that name already exists, it will be appended to by `/build-grades`. If not, it will be created.

## Step 2 — Read the Rubric

Parse the rubric xlsx to extract criteria names and weights (column A and column E, rows 2+).
This determines the column structure of the grades file.

## Step 3 — Evaluate the Submission

For each criterion in the rubric, read the submission and assign one of three labels.
Consult `references/performance-levels.md` for scoring rules and thresholds.

Score label must be exactly one of:
- `Meets Expectations`
- `Partially Meets`
- `Does Not Meet`

For every criterion scored as **Partially Meets** or **Does Not Meet**, write a concise
observation explaining why. Be specific — reference actual content (or absence of it) from
the submission. Example: "only 2 of the 10 required items were completed."

**Language rule**: write observations in the language of the assignment brief. If the
assignment brief language cannot be determined, fall back to the rubric language.

## Step 4 — Build the Row JSON

`observations` is an object with one key per criterion. Set the value to an empty string
for criteria that meet expectations; write the reason for those that don't.

```json
{
  "name": "Group 1",
  "scores": {
    "Hardware Empresarial (Servidores)": "Meets Expectations",
    "Hardware Personal (PCs)": "Partially Meets",
    "Software Empresarial (Sistemas Críticos)": "Does Not Meet"
  },
  "observations": {
    "Hardware Empresarial (Servidores)": "",
    "Hardware Personal (PCs)": "specs documented for only 1 of 3 group members.",
    "Software Empresarial (Sistemas Críticos)": "no software investigated."
  }
}
```

Save to `<output_dir>/evaluations/row_<slug>.json`.

**Pause here.** Present the evaluation to the user in chat as a summary table (name, each
criterion with its score, and any observations). Ask the user to confirm or request
corrections before writing the grades file. Do not run Step 5 until the user approves.

## Step 5 — Append to Grades File

Once the user confirms the evaluation:

```bash
python scripts/append_grade.py <rubric_xlsx> <grades_xlsx> <output_dir>/evaluations/row_<slug>.json
```

The script:
- Creates the grades file with the correct header if it doesn't exist yet.
- Appends the row and calculates the total automatically from rubric weights.
- Compiles the `observations` dict into a single string for the xlsx cell.
- See `references/column-layout.md` for output file structure and formatting rules.

## Step 6 — Deliver

- Present the grades file with `present_files`.
- Report: student/group name and total score — nothing else.
