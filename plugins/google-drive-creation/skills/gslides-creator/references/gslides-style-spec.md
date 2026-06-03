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

### `concept`

Concept-explainer slide. Light indigo background, nav bar, full-width navy definition
banner below the nav bar, then a 1–2 column layout with purple accent bars for headings.
Use for every new AWS primitive introduced before a demo.

**Fields:**
- `title` (string) — shown in the nav bar; format `"aws_resource_name — Short Description"`
- `definition` (string) — 1–2 sentences in plain English: what this thing is and why it
  exists. Rendered as white text in the navy banner. Required on every concept slide.
- `columns` (array) — 1 or 2 column objects, each with:
  - `heading` (string) — column heading shown with a purple accent bar
  - `bullets` (array) — each item is either:
    - a plain string (rendered as `•  text`)
    - `{ "type": "heading", "text": "..." }` (rendered bold-navy, no bullet — inline sub-heading)

**Column guidelines:**
- 2 columns preferred for two distinct aspects (e.g. "Core settings" + "Design rule")
- 1 column for simple primitives with fewer than 5 bullets
- Each bullet ≤ one line; aim for 3–4 bullets per column

**Example:**
```json
{
  "type": "concept",
  "title": "aws_vpc — The Private Network Boundary",
  "definition": "A Virtual Private Cloud is your own isolated section of the AWS network — a logically separate environment where you declare the IP address space, subnets, routing rules, and security controls.",
  "columns": [
    {
      "heading": "Core settings",
      "bullets": [
        "cidr_block = \"10.0.0.0/16\" — 65 536 private IP addresses",
        "enable_dns_hostnames = true — required for RDS endpoint resolution",
        "enable_dns_support   = true — Route 53 resolves names inside the VPC"
      ]
    },
    {
      "heading": "Design rule",
      "bullets": [
        "One VPC per environment (dev, staging, prod each get their own)",
        "No shared network boundaries between environments",
        "All subnets, route tables, and SGs are scoped to this single VPC"
      ]
    }
  ]
}
```

---

### `diagram`

Visual block-diagram slide. Light indigo background, nav bar, then a layered stack of
colored boxes (top = internet/external, bottom = data layer) with `▼` arrows between
layers. Used as the first pre-demo slide to show what will be built.

**Fields:**
- `title` (string) — shown in the nav bar
- `layers` (array) — ordered list of layer objects (top → bottom):
  - `label` (string) — short text shown to the left of the row; supports `\n` for two lines
  - `boxes` (array) — list of `{ "text", "color", "sub" }` box objects drawn evenly across the row
  - `muted` (boolean, optional) — `true` renders the layer label in muted grey; use for
    pre-existing or external resources the demo *consumes* but does not build
- `caption` (string, optional) — one line of muted italic text at the bottom summarizing
  the module-output contract

**Box `color` tokens:**
| Token | Color | Use |
|-------|-------|-----|
| `"P"` | Purple (`6540A8`) | Primary new resources being built in this demo |
| `"B"` | Royal blue (`2563EB`) | Supporting/routing resources in the same demo |
| `"GR"` | Emerald (`10B981`) | DNS / TLS resources |
| `"M"` | Muted grey (`9CA3AF`) | External (internet) or pre-existing resources |

Each box `"sub"` field (optional string) renders as a smaller label below the main text
inside the box — useful for CIDR ranges, rate-limit specs, or resource sub-type notes.

**Example:**
```json
{
  "type": "diagram",
  "title": "Demo 2 — What We're Building",
  "layers": [
    { "label": "Internet", "muted": true, "boxes": [{ "text": "0.0.0.0 / 0", "color": "M" }] },
    { "label": "WAF (REGIONAL)", "boxes": [{ "text": "WAF Web ACL", "color": "B", "sub": "rate-limit: 2000 req / 5 min / IP" }] },
    { "label": "modules/ingress/", "boxes": [
        { "text": "ALB SG", "color": "P", "sub": "ingress 80/443" },
        { "text": "aws_lb (ALB)", "color": "P", "sub": "application · internet-facing" }
    ]},
    { "label": "Compute\n(pre-existing)", "muted": true, "boxes": [{ "text": "ECS Fargate Tasks", "color": "M" }] }
  ],
  "caption": "modules/ingress/ outputs target_group_arn — compute_ecs receives a plain string and knows nothing about the ALB"
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

Live-coding companion step slide. Two-zone layout: a dark code block (top ~60%)
and a full-width amber WHY strip (bottom ~40%). Nav bar spans the top with the
step badge and title.

**Visual zones:**
- **Nav bar** (navy, full width) — `"N / TOTAL"` badge on left, step title on right
- **Code block** (CB background, Courier New 10.5pt) — the exact HCL or terminal command. Hard limit: 11 lines. Truncate with `[...]` when needed; supply full code in `code_full` for slide notes.
- **WHY strip** (GO / amber, full width) — large white text, one sentence ≤ 10 words. Billboard cue only — the instructor talks around it.

**Slide notes (not rendered on slide):**
- `verify` is always written to notes
- If `code_full` is provided, append it to notes below verify

**Fields:**
- `demo` (string) — demo label for the nav bar, e.g. `"Demo A"`
- `step` (int or string) — current step number
- `total` (int or string) — total steps in this demo
- `title` (string) — short step title
- `code` (string) — exact HCL block or terminal command (≤ 11 lines; use `[...]` for truncation)
- `code_full` (string, optional) — full untruncated code; only when `code` is truncated; written to slide notes
- `why` (string) — one punchy sentence, ≤ 10 words; architectural reason in plain language
- `verify` (string) — expected output or pitfall; written to slide notes only

**Example:**
```json
{
  "type": "step",
  "demo": "Demo A",
  "step": 2,
  "total": 10,
  "title": "Enable S3 Versioning",
  "code": "resource \"aws_s3_bucket_versioning\" \"this\" {\n  bucket = aws_s3_bucket.this.id\n  versioning_configuration {\n    status = \"Enabled\"\n  }\n}",
  "why": "Versioning = your state file's undo button.",
  "verify": "After apply: aws s3api get-bucket-versioning --bucket <name> returns Status: Enabled."
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
