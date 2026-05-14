---
name: exam-version-generator
description: >
  Creates N shuffled versions of a multiple-choice exam from an MCQ JSON source
  (produced by the mcq-generator skill), shuffles both question order and option
  order independently per version, builds an answer key, and exports everything
  to Google Docs by calling the gdocs-exam-exporter skill.

  Triggers on: "generate N versions of the exam", "create exam versions",
  "shuffle exam", "make N exam versions", "create exam with answer key",
  or any request to produce multiple shuffled MCQ exam versions ready for
  distribution to students.

  Prerequisites:
    - The mcq-generator skill must have already run and produced a JSON file
      where answers[0] is always the correct answer for each question.
    - The gdocs-exam-exporter skill must be available for the export step.
    - Node.js must be available (node command).
    - Google Drive MCP must be connected for the export step.
---

# Exam Version Generator

Orchestrates the full pipeline:
**mcq-generator JSON → N shuffled versions → answer key → Google Docs export**

---

## Quick Reference

| Step | What happens |
|------|-------------|
| 1 | Gather parameters from user |
| 2 | Read source MCQ JSON (from mcq-generator) |
| 3 | Run `scripts/shuffle_exam.js` to produce N shuffled exam JSON files |
| 4 | Run `scripts/build_answer_key.js` to produce `answer_key.json` |
| 5 | Run `scripts/validate_key.js` to confirm 0 unresolved answers |
| 6 | Call `gdocs-exam-exporter` skill with all generated data |

---

## Step 1 — Gather Parameters

Before doing anything, collect from the user:

| Parameter | Example | Notes |
|-----------|---------|-------|
| `source_json` | `exam_questions.json` | Output of mcq-generator; `answers[0]` must be correct |
| `n_versions` | `3` | Number of shuffled versions to produce (A, B, C, …) |
| `exam_title` | `Midterm Exam — Sessions 1–4` | Added to doc title; user adds header to doc later |
| `section_header` | `PART I — Closed-Ended Questions` | H2 in the doc |
| `pts_per_question` | `4` | Points each question is worth |
| `total_pts` | `60` | Total exam points (shown in section header) |
| `gdrive_folder_id` | `1nUY8k7...` | Google Drive folder ID where docs will be created |

Ask for all of these if not provided. The folder ID can be extracted from a
Google Drive URL: `https://drive.google.com/drive/folders/{FOLDER_ID}`.

---

## Step 2 — Validate Source JSON Format

The source JSON must follow this structure (mcq-generator output):

```json
{
  "questions": [
    {
      "number": 1,
      "question": "Question text here.",
      "answers": [
        "Correct answer",
        "Wrong answer 1",
        "Wrong answer 2",
        "Wrong answer 3"
      ]
    }
  ]
}
```

**Critical:** `answers[0]` is always the correct answer. The skill relies on
this invariant to build the answer key after shuffling.

Read the file and confirm this structure before proceeding. If the file has a
different shape, adapt the extraction logic in Step 3.

---

## Step 3 — Run Shuffle Script

Copy `scripts/shuffle_exam.js` to the working directory and run it:

```bash
node scripts/shuffle_exam.js \
  --input <source_json> \
  --versions <n_versions> \
  --output-dir <output_dir>
```

This produces:
- `<output_dir>/exam_A.json`, `exam_B.json`, `exam_C.json`, … (one per version)
- Each JSON records `correct_index` per question — the shuffled position of the
  correct answer (0=A, 1=B, 2=C, 3=D)

---

## Step 4 — Build Answer Key

```bash
node scripts/build_answer_key.js \
  --input-dir <output_dir> \
  --versions <comma-separated-letters> \
  --output answer_key.json
```

Produces `answer_key.json`:

```json
{
  "A": [
    { "n": 1, "letter": "B", "correct_text": "Correct answer" },
    ...
  ],
  "B": [...],
  "C": [...]
}
```

---

## Step 5 — Validate

```bash
node scripts/validate_key.js --input answer_key.json
```

Must print `Total: N | Missing: 0`. If missing > 0, stop and report which
questions failed matching.

---

## Step 6 — Export to Google Docs

Call the `gdocs-exam-exporter` skill with:

```
exam_versions_dir:   <output_dir>
answer_key_file:     answer_key.json
gdrive_folder_id:    <gdrive_folder_id>
exam_title:          <exam_title>
section_header:      <section_header>
pts_per_question:    <pts_per_question>
total_pts:           <total_pts>
```

The exporter creates one Google Doc per version plus one scoring guide doc,
all in the specified folder.

---

## Output Summary

After the full pipeline completes, report to the user:

```
Generated N exam versions + 1 scoring guide in Google Drive folder <id>:

  Version A → https://docs.google.com/document/d/{id}/edit
  Version B → https://docs.google.com/document/d/{id}/edit
  ...
  Scoring Guide → https://docs.google.com/document/d/{id}/edit

Answer key written to: answer_key.json
No header added — paste your institutional header into each doc.
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Source JSON not found | Ask user for correct path |
| `answers` array missing or < 4 items | Report which question and stop |
| Missing answers in key (validate step) | Report affected questions; do not export |
| Google Drive upload fails | Retry once; if fails again, report the error and offer to save HTML files locally |
| gdocs-exam-exporter skill not available | Stop and alert: "The gdocs-exam-exporter skill is not loaded." |
