# Exercise Google Doc Spec

Read this file when building exercise Google Docs (Step 3).
Also read `references/exercise-spec.md` for content rules (design, copy-paste blocking,
evidence requirements, section order).

For the JSON schema, style mapping, script usage, and code block formatting, read:
`plugins/google-drive-creation/skills/gdoc-creator/references/gdoc-style-spec.md`

---

## Creation workflow

1. Generate one JSON file per exercise (schema below) → save to
   `/mnt/user-data/outputs/exercise-<N>-<n>.json`
2. Run the `gdoc-creator` script for each file:
   ```
   python plugins/google-drive-creation/skills/gdoc-creator/scripts/create-gdoc.py \
     /mnt/user-data/outputs/exercise-<N>-<n>.json \
     "<exercises_folder_id from handover>" \
     "Exercise <N>.<n>"
   ```
   The folder arg accepts a full Drive URL or a bare folder ID — both work.
3. Present the printed Google Doc URL to the user.

---

## Exercise JSON structure

Title and folder are CLI args — do not include them in the JSON file.

```json
{
  "header": [
    { "label": "Course",       "value": "Optimizaciones y Desempeño — Cloud Deployment Automation" },
    { "label": "Session",      "value": "<N> — <Month Day, Year>" },
    { "label": "Time allowed", "value": "30 minutes" },
    { "label": "Submission",   "value": "Initialize a new repository called oyd-exercise-<N>-<n> and commit/push everything into it. Submit the repository URL only." }
  ],
  "body": [
    { "type": "heading1", "text": "Context" },
    ...,
    { "type": "heading1", "text": "Setup" },
    { "type": "heading2", "text": "Prerequisites" },
    ...,
    { "type": "heading1", "text": "Tasks" },
    { "type": "heading2", "text": "Task 1 — <name>" },
    ...,
    { "type": "heading1", "text": "Acceptance Criteria" },
    { "type": "bullet_list", "items": [...] }
  ]
}
```

---

## Section order

| Element      | Content |
|--------------|---------|
| `title`      | `Exercise <N>.<n> — <Title>` |
| `header`     | Course, Session, Time allowed, Submission (exactly as shown above) |
| H1 Context   | Scenario description + starter code (`code` blocks) + reference scripts (`heading3` + `code`) |
| H1 Setup     | H2 Prerequisites (bullet list) · H2 Architecture if multiple options (table) · H2 Repository structure (code block) |
| H1 Tasks     | One H2 per task; use bullet/numbered lists and code blocks for sub-requirements |
| H1 Acceptance Criteria | Single bullet list — one criterion per item |

---

## Validation

After the script prints the URL, open it and confirm:
- Title style on the exercise title
- Heading 1 on Context / Setup / Tasks / Acceptance Criteria
- Bold labels in the header block
- Gray background + Courier New on all code blocks
- Inline `code` spans render in monospace within body text
