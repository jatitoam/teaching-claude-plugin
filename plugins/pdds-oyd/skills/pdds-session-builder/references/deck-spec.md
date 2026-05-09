# Deck — PowerPoint via pptxgenjs

Read this file when building the **PowerPoint deck** (Step 4).

Also read `/mnt/skills/public/pptx/SKILL.md` before writing any generation code.

For the JS helper implementations used in deck generation, read:
- `scripts/pptx-code-box.js`
- `scripts/pptx-step-slide.js`
- `scripts/pptx-callout-slide.js`

---

## Output path

Generate to `/home/claude/session<N>/Session<N>_<Topic>.pptx`, then copy to
`/mnt/user-data/outputs/`.
Validate by converting to PDF (`soffice`) and rendering to JPG (`pdftoppm`).

---

## Color palette

```
N  = "1A237E"   // deep navy       — title bars, section headers, dark backgrounds
P  = "6540A8"   // medium purple   — accents, exercise cards, code header bars
B  = "2563EB"   // royal blue      — table headers, callouts
W  = "FFFFFF"   // white
LB = "EEF2FF"   // light indigo    — alternating content background
D  = "1F2937"   // near-black      — body text
M  = "9CA3AF"   // muted grey      — captions, footer
CB = "13172E"   // very dark navy  — code block background
CT = "D4D4D8"   // light grey      — code block text
AC = "38BDF8"   // sky blue        — live demo accent label
GR = "10B981"   // emerald         — positive, exercise rows, "after" state
RE = "EF4444"   // red             — warnings, "before" state, errors
GO = "F59E0B"   // amber           — notes, caution rows
TA = "F5F7FF"   // very light blue — table alternate rows
TB = "C7D2FE"   // periwinkle      — table borders
```

Font: Calibri body, Courier New for all code.

---

## Slide types

| Type | When to use |
|------|-------------|
| `cSlide(title)` | Standard content, white background |
| `lSlide(title, bullets)` | Standard content, light indigo (LB) background — context slides, cold open, wrap-up |
| `dSlide(title, code, fileLabel?)` | Dark code-heavy slide (CB background, purple nav bar) — reserved for before/after anti-pattern pairs where the code itself is the concept |
| `sdSlide(title, sub)` | Section divider — full navy, purple vertical bar, large type |
| `exSlide(n, title, desc)` | Exercise card — purple left panel, navy right |
| `demoSlide(title)` | Live demo marker — very dark bg, sky-blue LIVE DEMO label |
| `stepSlide(demo, n, total, title, bullets)` | Live-coding companion step — LB bg, navy bar with "N/TOTAL" badge, 3 context bullets (what / why / verify) |
| `calloutSlide(title, label, body)` | Key concept highlight — navy bg, dark box, purple label pill; used as the final slide of every demo |

---

## Required slides — every session deck

1. **Title slide** — session number, topic, date, instructor names
2. **Tonight's Plan** — agenda table with times; exercise rows highlighted in green
3. **Section divider** (`sdSlide`) per content block
4. **Content slides** per block (as many as the topic needs)
5. **Live demo marker** (`demoSlide`) immediately before each demo — both styles
6. **Exercise card** (`exSlide`) at each exercise slot

Course admin slides (schedule, assessment, policies) — include for Session 1 and
any session with a significant announcement; omit otherwise.

---

## Slide density

Prefer many small focused slides over large dense ones. Split when a slide has
more than ~5 bullet points or two unrelated ideas. Exception: comparison slides
(before/after, A vs B) stay together.

---

## Before/after and anti-pattern slides

When a content block introduces a concept that is better shown than described
(module design, dependency chains, copy-paste drift), use a dedicated before/after
slide pair:
- **Before slide** (`RE` accent): the problematic pattern with code example
- **After slide** (`GR` accent): the correct pattern with code example
- Keep both on adjacent slides — never split across a section divider

---

## Code blocks

See `scripts/pptx-code-box.js` for the implementation.

**Hard line limit:** at `fontSize: 10.5`, each line ≈ `0.175"`. Inner text height = `h - 0.24"`.
**Never exceed 11 lines** in a single code box — truncate with `[...]` or split across slides.
Overflow is invisible during generation but visible in every render.

---

## stepSlide

See `scripts/pptx-step-slide.js` for the implementation.

Used for every step in a live-coding companion demo. The "N/TOTAL" badge gives the
instructor instant location awareness mid-demo; the three bullets replace the terminal
as the thing students read.

**Bullet discipline:** three bullets per `stepSlide`, no more:
- Bullet 1 — **What:** the imperative action ("Write aws_s3_bucket_versioning referencing the bucket.id...")
- Bullet 2 — **Why:** the concept or architectural decision behind it
- Bullet 3 — **Verify/Watch:** what correct output looks like, or the common pitfall to name

Inline code references (argument names, resource types) are acceptable in prose — e.g.,
"set `sensitive = true`". Full resource blocks or command output are not.

---

## calloutSlide

See `scripts/pptx-callout-slide.js` for the implementation.

Used as the closing slide of every demo (replaces the old final `lSlide` callout).
