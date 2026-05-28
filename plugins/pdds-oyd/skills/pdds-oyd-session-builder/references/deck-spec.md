# Deck — Google Slides via gslides-creator

Read this file when building the **Google Slides deck** (Step 4).

Also read `plugins/google-drive-creation/skills/gslides-creator/references/gslides-style-spec.md`
before generating any slide JSON.

---

## Output path

Write the JSON spec to `/mnt/user-data/outputs/session<N>-deck.json`, then run:

```bash
python plugins/google-drive-creation/skills/gslides-creator/scripts/create-gslides.py \
  /mnt/user-data/outputs/session<N>-deck.json \
  "<folder_url_or_id>" \
  "Session <N> — <Topic>"
```

The script prints the Google Slides URL. Present it to the user.

---

## Color palette

```
N  = "1A237E"   // deep navy       — title bars, section headers, dark backgrounds
P  = "6540A8"   // medium purple   — accents, exercise cards, top bars
B  = "2563EB"   // royal blue      — intro/wrap agenda rows
W  = "FFFFFF"   // white
LB = "EEF2FF"   // light indigo    — alternating content background
D  = "1F2937"   // near-black      — body text
M  = "9CA3AF"   // muted grey      — captions, footer
CB = "13172E"   // very dark navy  — code block background
CT = "D4D4D8"   // light grey      — code block text
AC = "38BDF8"   // sky blue        — live demo accent label
GR = "10B981"   // emerald         — positive, exercise rows, VERIFY card
RE = "EF4444"   // red             — warnings, errors
GO = "F59E0B"   // amber           — WHY card accent
TA = "F5F7FF"   // very light blue — agenda table alternate rows
TB = "C7D2FE"   // periwinkle      — table borders, exercise title text
GR_LIGHT = "D1FAE5"  // light emerald — VERIFY card background
GO_LIGHT = "FEF3C7"  // light amber   — WHY card background
B_LIGHT  = "DBEAFE"  // light blue    — WHAT card background
```

Font: Calibri body, Courier New for all code.

---

## Slide types

The JSON `type` field determines which slide method is called.

| JSON type | When to use |
|-----------|-------------|
| `content` | Standard content, light indigo (LB) or white background — context slides, cold open, wrap-up |
| `concept` | Concept-explainer slide — nav bar + navy definition banner + 1–2 column layout with purple accent bars. Use for every new AWS primitive introduced before a demo. |
| `diagram` | Visual block-diagram slide — colored labeled boxes per layer, ▼ arrows between layers. Use as the first pre-demo slide to show what will be built. |
| `code` | Dark code-heavy slide (CB background, purple nav bar) — reserved for before/after anti-pattern pairs where the code itself is the concept |
| `section_divider` | Section divider — full navy, purple vertical bar, large type |
| `exercise` | Exercise card — purple left panel, navy right |
| `demo_marker` | Live demo marker — very dark bg, sky-blue LIVE DEMO label |
| `step` | Live-coding companion step — white bg, nav bar with "N / TOTAL" badge, three card sections (WHAT / WHY / VERIFY) |
| `callout` | Key concept highlight — navy bg, dark box, purple label pill; used as the final slide of every demo |

---

## Required slides — every session deck

1. **Title slide** (`title_slide`) — session number, topic, date, instructor names
2. **Tonight's Plan** (`agenda`) — agenda table with times; exercise rows highlighted in green
3. **Section divider** (`section_divider`) per content block
4. **Content slides** (`content`) per block (as many as the topic needs)
5. **Block diagram** (`diagram`) + **concept-explainer slides** (`concept`) immediately before each demo marker — see "Pre-demo concept slides" section below
6. **Live demo marker** (`demo_marker`) immediately before each demo
7. **Step slides** (`step`) for each step in a demo sequence
8. **Callout slide** (`callout`) as the closing slide of every demo
9. **Exercise card** (`exercise`) at each exercise slot

Course admin slides — include for Session 1 and any session with a significant
announcement; omit otherwise.

---

## Pre-demo concept slides

**Rule:** Every demo block is preceded by a `diagram` slide followed by one `concept` slide per new primitive. These appear between the section divider (or previous block) and the `demo_marker`. The `demo_marker` is never the first slide a student sees for a demo.

**Order:** `diagram` → `concept` slide(s) → `demo_marker` → step slides → callout

**Scope:** only the *delta* for this demo. Demo 1 introduces VPC primitives; Demo 2 introduces ALB + WAF (VPC is assumed known). Never re-introduce a primitive that a prior demo already covered.

---

### `diagram` slide — visual block diagram

The first pre-demo slide. Shows every service being built in this demo as a layered stack of colored boxes, with the request/dependency flow running top-to-bottom. This is also the connection map — there is no separate connection-map `content` slide.

**`layers`** — ordered list (top = internet/external, bottom = data layer). Each layer:
- `label` — short text shown to the left of the row (e.g. `"Public subnets\n10.0.1–2.0/24"`)
- `boxes` — list of `{ "text", "color", "sub" }` boxes drawn evenly across the row
- `muted: true` — for pre-existing or external resources (rendered grey); use for resources the demo *consumes* but does not build

**Box colors** (use named tokens — they resolve via the color map):
- `"P"` (purple) — primary new resources being built in this demo
- `"B"` (royal blue) — supporting/routing resources in the same demo
- `"GR"` (emerald) — DNS/TLS resources
- `"M"` (muted grey) — external (internet) or pre-existing resources; also set `muted: true` on the layer

**`caption`** — one line of muted text at the bottom summarizing the module-output contract.

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

### `concept` slide — one per new primitive

One slide per new AWS primitive (or tightly related pair, e.g. IGW + route table). Uses a full-width navy definition banner immediately below the nav bar, then a two-column layout with purple accent bars for sub-headings.

**Fields:**
- `title` — matches the nav bar; format `"aws_resource_name — Short Description"`
- `definition` — 1–2 sentences in plain English: what is this thing and why does it exist. This is the banner text. Required on every concept slide.
- `columns` — list of 1 or 2 column objects, each with `heading` (string) and `bullets` (array of strings or `{ "type": "heading", "text": "..." }` for inline sub-headings)

**Column guidelines:**
- 2 columns preferred when there are two distinct aspects (e.g. "Core settings" + "Design rule", "Public path" + "Private path")
- 1 column for simple primitives with fewer than 5 bullets
- No ASCII trees, no code-formatted strings — prose bullets only
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

## Slide density

Prefer many small focused slides over large dense ones. Split when a slide has
more than ~5 bullet points or two unrelated ideas. Exception: comparison slides
(before/after, A vs B) stay together.

---

## Before/after and anti-pattern slides

When a content block introduces a concept that is better shown than described
(module design, dependency chains, copy-paste drift), use a dedicated before/after
slide pair using the `code` type:
- **Before slide** (include `"// BEFORE"` in the title): the problematic pattern
- **After slide** (include `"// AFTER"` in the title): the correct pattern
- Keep both on adjacent slides — never split across a section divider

---

## Code blocks

**Hard line limit:** at `10.5pt` Courier New, keep code to **11 lines maximum**.
Overflow is invisible during generation but clipped in every render. Truncate with
`[...]` or split across slides.

---

## `step` slide

Used for every step in a live-coding companion demo. The `"N / TOTAL"` badge in
the nav bar gives the instructor instant location awareness mid-demo.

**Visual layout:**
- Nav bar (navy) spans full width with the badge (`step / total`) on the left and title on the right
- **Code block (top ~60%)** — dark background (CB), Courier New, the exact HCL or command to type. Hard limit: 11 lines. If the full code exceeds 11 lines, show the key sections with `[...]` to indicate omissions and supply the full version in `code_full` (written to slide notes).
- **WHY strip (bottom ~40%)** — full-width amber panel, large white text. One punchy sentence. **≤ 10 words target.** The instructor will elaborate verbally — the strip is a billboard cue, not a paragraph.

**Slide notes (not visible on slide):**
- Always include `verify` in the notes so the instructor has the expected output / pitfall cue
- If `code_full` is provided, append it to the notes below the verify line

**Fields:**
- `demo` — demo label for the nav bar
- `step` — current step number
- `total` — total steps in this demo
- `title` — short step title
- `code` — the exact HCL block or terminal command to show (≤ 11 lines; truncate with `[...]` if needed)
- `code_full` (optional) — full untruncated code; only include when `code` is truncated; written to slide notes
- `why` — one punchy sentence, ≤ 10 words; the architectural reason in plain language
- `verify` — expected output or pitfall; written to slide notes only, never rendered on the slide

**Example:**
```json
{
  "type": "step",
  "demo": "Demo 1",
  "step": 2,
  "total": 5,
  "title": "Enable S3 Versioning",
  "code": "resource \"aws_s3_bucket_versioning\" \"this\" {\n  bucket = aws_s3_bucket.this.id\n  versioning_configuration {\n    status = \"Enabled\"\n  }\n}",
  "why": "Versioning = your state file's undo button.",
  "verify": "After apply: aws s3api get-bucket-versioning --bucket <name> returns Status: Enabled."
}
```

---

## `callout` slide

Used as the closing slide of every demo. Replaces the old final content slide summary.

**Two content fields — not a `body` field:**
- `headline` — the short memorable takeaway (~24pt billboard). One sentence, quotable.
- `detail` — elaboration on the headline (~14pt). One paragraph or a few lines.

**Visual layout:**
- Purple top bar with the slide title
- Label pill (e.g. `"Key Insight"`, `"Gotcha"`, `"Rule"`) in purple beneath the bar
- Large white `headline` text — the billboard
- Thin purple separator line
- Dark navy detail box with `detail` text in light grey

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
