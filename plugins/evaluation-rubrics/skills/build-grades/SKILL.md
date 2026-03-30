---
name: build-grades
description: >
  Rebuilds the cumulative grades .xlsx file from scratch using all saved evaluation
  JSON files in an evaluations/ folder. Use this skill when the user wants to
  regenerate or recalculate the grades file after editing one or more row JSONs.
  Trigger on phrases like: "rebuild grades", "build grades", "recalculate grades",
  "I edited the JSON", "regenerate the xlsx", "update the scores", or the slash
  command /build-grades. Do NOT trigger this skill for evaluating new submissions —
  use assignment-evaluator for that.
---

# Build Grades

Rebuilds the grades `.xlsx` from all `row_*.json` files in an `evaluations/` folder.
Use this after editing one or more row JSONs to apply corrections and recalculate totals.

## Slash command usage

```
/build-grades <evaluations_dir> <rubric_xlsx> [<grades_xlsx>]
```

- `<evaluations_dir>` — path to the folder containing `row_*.json` files (required)
- `<rubric_xlsx>` — path to the rubric xlsx used when the evaluations were created (required)
- `<grades_xlsx>` — path for the output grades file (optional; defaults to
  `<evaluations_dir>/../grades_<slug>.xlsx` where `<slug>` is derived from the rubric filename)

## Step 1 — Parse Arguments

Extract the three values above from the command arguments.

- If `<evaluations_dir>` or `<rubric_xlsx>` are missing, stop and ask the user to provide them. Do not guess paths.
- If `<grades_xlsx>` is omitted, derive it: take the rubric filename slug and place the output one level above `<evaluations_dir>`.
  Example: rubric `rubrica_lab01.xlsx`, evaluations at `/home/user/lab01/evaluations/`
  → grades at `/home/user/lab01/grades_lab01.xlsx`

## Step 2 — Rebuild the Grades File

```bash
python scripts/build_grades.py <rubric_xlsx> <grades_xlsx> <evaluations_dir>/
```

The script:
- Reads all `row_*.json` files in `<evaluations_dir>/`, sorted alphabetically.
- Recreates the grades xlsx from scratch with the correct header.
- Appends one row per JSON, recalculating totals from rubric weights.
- Compiles each `observations` dict into a single string for the xlsx cell.

## Step 3 — Deliver

- Present the rebuilt file with `present_files`.
- Report: number of rows rebuilt — nothing else.
