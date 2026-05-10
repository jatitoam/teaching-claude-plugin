# Google Slides Style Spec

This document describes the JSON schema accepted by `create-gslides.py` and the
visual design of every slide type it produces.

---

## Script invocation

```bash
python plugins/google-drive-creation/skills/gslides-creator/scripts/create-gslides.py \
  <json_file> \
  <folder_url_or_id> \
  "<presentation_title>"
```

- `json_file` — path to the JSON spec (e.g. `/mnt/user-data/outputs/session4-deck.json`)
- `folder_url_or_id` — Google Drive folder URL or bare folder ID
- `presentation_title` — becomes the presentation filename in Drive

Prints the Google Slides URL to stdout on success.

---

## Color palette

| Name | Hex | Use |
|------|-----|-----|
| N | `1A237E` | Deep navy — title bars, dark backgrounds, accents |
| P | `6540A8` | Medium purple — section panels, pills, exercise left column |
| B | `2563EB` | Royal blue — intro/wrap agenda rows |
| W | `FFFFFF` | White |
| LB | `EEF2FF` | Light indigo — content slide background |
| D | `1F2937` | Near-black — body text |
| M | `9CA3AF` | Muted grey — captions, footer, metadata |
| CB | `13172E` | Very dark navy — code slide background |
| CT | `D4D4D8` | Light grey — code text |
| AC | `38BDF8` | Sky blue — live demo label |
| GR | `10B981` | Emerald — verify card accent, exercise rows |
| RE | `EF4444` | Red — warnings |
| GO | `F59E0B` | Amber — WHY card accent |
| TA | `F5F7FF` | Very light blue — agenda table alternate rows |
| TB | `C7D2FE` | Periwinkle — table borders, exercise title text |
| GR_LIGHT | `D1FAE5` | Light emerald — VERIFY card background |
| GO_LIGHT | `FEF3C7` | Light amber — WHY card background |
| B_LIGHT | `DBEAFE` | Light blue — WHAT card background |

Font: Calibri (body), Courier New (all code). Slide dimensions: 10" × 5.625" (16:9).

---

## Top-level JSON structure

```json
{
  "slides": [
    { "type": "title_slide", ... },
    { "type": "agenda", ... },
    ...
  ]
}
```

The `slides` array is processed in order. Each object must have a `"type"` field.

---

## Slide types

### `title_slide`

Full-screen navy slide with purple left accent panel.

**Fields:**
- `session` (int or string) — session number shown above the topic
- `topic` (string) — large bold headline
- `date` (string) — displayed below the topic
- `instructor` (string, optional, default `"Tito Alvarez"`)
- `ta` (string, optional, default `"Abner Pérez"`)

**Example:**
```json
{
  "type": "title_slide",
  "session": 4,
  "topic": "Storage, Databases & Remote State",
  "date": "May 14, 2025",
  "instructor": "Tito Alvarez",
  "ta": "Abner Pérez"
}
```

---

### `agenda`

Light indigo background, navy nav bar, header row + data rows.

**Row fields:**
- `time` (string) — e.g. `"6:00–6:15"`
- `block` (string) — description of the block
- `type` (string, optional) — one of `"exercise"`, `"demo"`, `"intro"`, `"wrap"`. Controls row color. Even/odd rows alternate white/light blue when type is absent.

**Example:**
```json
{
  "type": "agenda",
  "rows": [
    { "time": "6:00–6:10", "block": "Cold Open — last session recap", "type": "intro" },
    { "time": "6:10–7:00", "block": "Demo 1 — S3 + Remote State", "type": "demo" },
    { "time": "7:00–7:20", "block": "Exercise 1", "type": "exercise" },
    { "time": "7:20–8:00", "block": "Demo 2 — RDS Automation", "type": "demo" },
    { "time": "8:00–8:15", "block": "Wrap-up", "type": "wrap" }
  ]
}
```

---

### `section_divider`

Full-screen navy with purple left vertical bar and large title text.

**Fields:**
- `title` (string)
- `subtitle` (string, optional)

**Example:**
```json
{
  "type": "section_divider",
  "title": "Remote State",
  "subtitle": "Why your state file must never live on your laptop"
}
```

---

### `content`

Standard content slide with nav bar and bullet list.

**Fields:**
- `title` (string)
- `bullets` (array) — each item is either:
  - a plain string (rendered as `•  text`)
  - `{ "type": "heading", "text": "..." }` (rendered bold in navy, no bullet)
- `background` (string, optional) — `"light"` (default, LB) or `"white"`

**Example:**
```json
{
  "type": "content",
  "title": "Why Remote State?",
  "background": "light",
  "bullets": [
    { "type": "heading", "text": "Problems with local state" },
    "State file contains sensitive values in plaintext",
    "No locking — concurrent applies corrupt state",
    { "type": "heading", "text": "S3 + DynamoDB solution" },
    "S3 stores the state file with versioning enabled",
    "DynamoDB provides a distributed lock"
  ]
}
```

---

### `demo_marker`

Very dark navy background with sky-blue LIVE DEMO pill. Placed immediately before
each demo sequence.

**Fields:**
- `demo` (string) — short label shown in muted grey, e.g. `"Demo 1"`
- `title` (string) — large white title beneath the label

**Example:**
```json
{
  "type": "demo_marker",
  "demo": "Demo 1",
  "title": "S3 Bucket + Remote State Backend"
}
```

---

### `step`

Live-coding companion step slide. White background with nav bar showing a step
badge and three visually distinct cards: WHAT (light blue), WHY (light amber),
VERIFY (light emerald).

**Fields:**
- `demo` (string) — demo label for the nav bar, e.g. `"Demo 1"`
- `step` (int or string) — current step number
- `total` (int or string) — total steps in this demo
- `title` (string) — short step title
- `what` (string) — the imperative action the student executes
- `why` (string) — the architectural or conceptual reason behind this step
- `verify` (string) — what correct output looks like, or a common pitfall to watch for

Note: `what`, `why`, and `verify` are **separate string fields**, not a bullets array.

**Example:**
```json
{
  "type": "step",
  "demo": "Demo 1",
  "step": 2,
  "total": 5,
  "title": "Enable S3 Versioning",
  "what": "Add an aws_s3_bucket_versioning resource referencing bucket.id and set status = \"Enabled\".",
  "why": "Versioning lets Terraform recover a previous state file if a bad apply corrupts it — it's the safety net under your safety net.",
  "verify": "After apply, aws s3api get-bucket-versioning --bucket <name> returns Status: Enabled."
}
```

---

### `callout`

Key concept highlight. Navy background with purple top bar, a label pill, a large
headline (the memorable takeaway), a thin separator, and a dark detail box.

**Fields:**
- `title` (string) — shown in the purple top bar
- `label` (string) — short pill label above the headline, e.g. `"Key Insight"`, `"Gotcha"`, `"Rule"`
- `headline` (string) — the single memorable statement (~24pt billboard). Keep it short and quotable.
- `detail` (string) — elaboration on the headline (~14pt). Can be a paragraph or a few lines.

Note: `headline` replaces the old `body` field from earlier versions.

**Example:**
```json
{
  "type": "callout",
  "title": "Demo 1 — Takeaway",
  "label": "Key Insight",
  "headline": "State is the source of truth — not your code.",
  "detail": "Terraform reconciles reality against state, not against your .tf files. If state drifts from reality (manual edits, deleted resources), your next plan will be wrong. Remote state + locking prevents drift at the team level."
}
```

---

### `exercise`

Exercise card with purple left panel (number + title) and navy right panel (description).

**Fields:**
- `n` (int or string) — exercise number
- `title` (string) — short title shown in the left panel
- `description` (string) — instructions shown in the right panel

**Example:**
```json
{
  "type": "exercise",
  "n": 1,
  "title": "Remote State",
  "description": "Migrate your existing S3 bucket configuration to use a remote backend.\n\n1. Create the backend bucket and DynamoDB table manually.\n2. Add the backend block to your Terraform root module.\n3. Run terraform init and confirm the state is migrated.\n4. Verify that a second terminal cannot run terraform plan while yours is in progress."
}
```

---

### `code`

Dark code slide. Very dark navy background, purple top bar, dark code box with
optional file label bar.

**Fields:**
- `title` (string) — shown in the purple top bar
- `code` (string) — code content (plain text; no syntax highlighting applied)
- `file_label` (string, optional) — filename shown in a small purple bar above the code

**Hard line limit:** at 10.5pt with Courier New, keep code to 11 lines maximum.
Overflow is invisible during generation but clipped in the rendered slide.

**Example:**
```json
{
  "type": "code",
  "title": "backend.tf — Remote State Configuration",
  "file_label": "backend.tf",
  "code": "terraform {\n  backend \"s3\" {\n    bucket         = \"my-tfstate-bucket\"\n    key            = \"prod/terraform.tfstate\"\n    region         = \"us-east-1\"\n    dynamodb_table = \"terraform-locks\"\n    encrypt        = true\n  }\n}"
}
```

---

## Credentials and setup

### First-time setup

1. Create a Google Cloud project and enable the **Google Slides API** and **Google Drive API**.
2. Create an OAuth 2.0 Client ID (Desktop application).
3. Download the credentials JSON and save to:
   ```
   ~/.config/teaching-claude-plugin/credentials.json
   ```
4. Install required packages:
   ```
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```
5. Run the script once — it opens a browser tab for authorization and saves the token to:
   ```
   ~/.config/teaching-claude-plugin/token-slides.json
   ```
   Subsequent runs are fully silent.

### Token refresh

The token auto-refreshes using the stored refresh token. If refresh fails (revoked
access or expired scope), delete `token-slides.json` and re-run to re-authorize.

### Folder targeting

Pass a full Drive folder URL or a bare folder ID. The script extracts the ID from
the URL automatically using the `/folders/<id>` path segment.
