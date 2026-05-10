# Exercise Google Doc Spec

Read this file when building exercise Google Docs (Step 3).
Also read `references/exercise-spec.md` for content rules (design, copy-paste blocking, evidence, section order).

---

## Output format

Each exercise is a **Google Doc** created via `scripts/create-exercise-gdoc.py`.
The script uses the Google Docs API to create the document and apply formatting in one pass.

**Run command:**
```
python plugins/pdds-oyd/skills/pdds-session-builder/scripts/create-exercise-gdoc.py \
  /mnt/user-data/outputs/exercise-<N>-<n>.json
```

The script prints the Google Doc URL to stdout. Present that URL to the user.

**Dependencies** (must be installed):
```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Credentials:** OAuth token at `~/.config/teaching-claude-plugin/credentials.json`.
First run opens a browser tab for authorization; subsequent runs are silent.

---

## Style mapping

Named paragraph styles (title, subtitle, heading1–4, normal text) use the
instructor's Google account defaults — do not override font, size, or color for
these. The script applies only the style name; the account theme does the rest.

| JSON `type`      | Google Docs style applied  |
|------------------|---------------------------|
| `title`          | TITLE                     |
| `subtitle`       | SUBTITLE                  |
| `heading1`       | HEADING_1                 |
| `heading2`       | HEADING_2                 |
| `heading3`       | HEADING_3                 |
| `heading4`       | HEADING_4                 |
| `paragraph`      | NORMAL_TEXT (default)     |
| `code`           | NORMAL_TEXT + code style  |
| `bullet_list`    | NORMAL_TEXT + bullet      |
| `numbered_list`  | NORMAL_TEXT + numbered    |
| `table`          | rendered as code block    |

---

## Code block style (only custom style — everything else inherits account defaults)

| Property    | Value                        |
|-------------|------------------------------|
| Font        | Courier New                  |
| Size        | 9.5 pt                       |
| Background  | #f3f3f3 (light gray)         |
| Line spacing| 100% (single, no extra gaps) |
| Space above/below | 0 pt                   |

Apply to: standalone code blocks (`type: "code"`) AND tables (rendered as code).
Do NOT apply to inline code spans — use the `"style": "code"` span field instead.

---

## JSON schema

Produce one JSON file per exercise. Save to `/mnt/user-data/outputs/exercise-<N>-<n>.json`.

```json
{
  "title": "Exercise 3.1 — EC2 Compute Module",
  "header": {
    "course": "Optimizaciones y Desempeño — Cloud Deployment Automation",
    "session": "3 — May 7, 2026",
    "time_allowed": "30 minutes",
    "submission": "Initialize a new repository called oyd-exercise-3-1 and commit/push everything into it. Submit the repository URL only."
  },
  "body": []
}
```

### Body element types

**Headings and paragraphs**

```json
{ "type": "heading1", "text": "Context" }
{ "type": "heading2", "text": "Setup" }
{ "type": "heading3", "text": "Prerequisites" }
{ "type": "heading4", "text": "Sub-section" }
{ "type": "paragraph", "text": "Plain body text." }
```

**Paragraph with inline formatting** — use `spans` instead of `text`:

```json
{
  "type": "paragraph",
  "spans": [
    { "text": "Declare ", "style": "normal" },
    { "text": "ami_id", "style": "code" },
    { "text": " and ", "style": "normal" },
    { "text": "instance_type", "style": "code" },
    { "text": " as input variables.", "style": "normal" }
  ]
}
```

Allowed `style` values for spans: `normal`, `bold`, `italic`, `bold_italic`, `code`.

Headings also support `spans` when inline formatting is needed inside a heading.

**Code block** — use for file contents, CLI commands, directory trees:

```json
{ "type": "code", "text": "require 'socket'\nrequire 'json'\n\nPORT = 8080" }
```

Preserve indentation exactly. The script splits on `\n` and applies gray background per line.

**Lists**

```json
{ "type": "bullet_list", "items": ["AWS credentials configured", "Terraform CLI >= 1.8"] }
{ "type": "numbered_list", "items": ["Step one", "Step two"] }
```

List items may also use span arrays for inline formatting:

```json
{
  "type": "bullet_list",
  "items": [
    {
      "spans": [
        { "text": "environment", "style": "code" },
        { "text": " — string, no default", "style": "normal" }
      ]
    }
  ]
}
```

**Table** — rendered as a monospace code block (no native Docs table):

```json
{
  "type": "table",
  "headers": ["Option", "Instance type", "AMI (us-west-2)", "Best for"],
  "rows": [
    ["arm64 (Graviton2)", "t4g.nano", "ami-0ddb64e71e68cf624", "macOS M-series, Linux"],
    ["x86_64", "t3.micro", "ami-0d43f0bb92e485897", "Windows, Intel Mac, CI runners"]
  ]
}
```

---

## Section order (matches exercise-spec.md)

```
title       → "Exercise <N>.<n> — <Title>"
header      → course, session, time_allowed, submission
heading1    → "Context"
  paragraph / code / table as needed
heading1    → "Setup"
  heading2  → "Prerequisites"  (bullet_list)
  heading2  → "Architecture"   (table if multiple options)
  heading2  → "Repository structure"  (code block)
heading1    → "Tasks"
  heading2  → "Task 1 — <name>"
    paragraph + bullet_list / numbered_list / code
  heading2  → "Task 2 — ..."
  ...
heading1    → "Acceptance Criteria"
  bullet_list
```

---

## Validation

After the script prints the URL, open it in a browser and verify:
- Title style applied to the exercise title
- Heading 1 on Context / Setup / Tasks / Acceptance Criteria
- Code blocks have gray background and monospace font
- Inline code spans appear in Courier New within body text
- Bold labels in the header block (Course:, Session:, etc.)
