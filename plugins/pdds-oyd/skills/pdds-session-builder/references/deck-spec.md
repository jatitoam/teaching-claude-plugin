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
5. **Live demo marker** (`demo_marker`) immediately before each demo
6. **Step slides** (`step`) for each step in a demo sequence
7. **Callout slide** (`callout`) as the closing slide of every demo
8. **Exercise card** (`exercise`) at each exercise slot

Course admin slides — include for Session 1 and any session with a significant
announcement; omit otherwise.

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

**Three required fields — not bullets — separate strings:**
- `what` — the imperative action (`"Write aws_s3_bucket_versioning referencing the bucket.id..."`)
- `why` — the concept or architectural decision behind it
- `verify` — what correct output looks like, or the common pitfall to name

**Visual layout:**
- Nav bar (navy) spans full width with the badge (`step / total`) on the left and title on the right
- **WHAT card** (full width, light blue background, navy left bar, navy ▶ WHAT pill)
- **WHY card** (left half, light amber background, amber left bar, amber WHY pill)
- **VERIFY card** (right half, light emerald background, emerald left bar, emerald ✓ VERIFY pill)

Inline code references in prose are acceptable. Full resource blocks or command
output belong on a `code` slide, not in a step field.

**Example:**
```json
{
  "type": "step",
  "demo": "Demo 1",
  "step": 2,
  "total": 5,
  "title": "Enable S3 Versioning",
  "what": "Add an aws_s3_bucket_versioning resource referencing bucket.id and set status = \"Enabled\".",
  "why": "Versioning lets Terraform recover a previous state file if a bad apply corrupts it — the safety net under your safety net.",
  "verify": "After apply, aws s3api get-bucket-versioning --bucket <name> returns Status: Enabled."
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
