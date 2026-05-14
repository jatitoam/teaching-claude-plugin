---
name: gdocs-exam-exporter
description: >
  Exports shuffled MCQ exam versions and a scoring guide to Google Docs in a
  specified Google Drive folder. Uses the exact HTML format defined by the
  course template (Exam model 2): Inter 10pt body, League Spartan headings,
  [ ] checkboxes with soft breaks between options, hard breaks between
  question and options. Produces one Google Doc per exam version plus one
  scoring guide doc with answer tables.

  This skill is called by exam-version-generator and should not be triggered
  directly by users unless they already have exam JSON files and an answer key.

  Triggers on: being called from exam-version-generator, or explicit user
  request like "export the exam JSONs to Google Docs", "upload exams to Drive".

  Prerequisites:
    - Google Drive MCP must be connected (Google Drive:create_file tool available).
    - Node.js must be available for running HTML-generation scripts.
    - Exam version JSON files and answer_key.json must exist.
---

# Google Docs Exam Exporter

Converts exam JSON + answer key into Google Docs using the course HTML template.

---

## Format Specification (Exam Model 2)

This is the canonical template. **Do not deviate from these styles.**

### Google Fonts import (in `<head>`)
```html
<style type="text/css">
 @import url(https://themes.googleusercontent.com/fonts/css?kit=rfSAlb2JfKqknMZbyNv1qbd1z-QJxci6pgsJEDD--sK5C-2JrCr1ABsZF5AjRv96T);
</style>
```

### Body
```
background-color:#ffffff; max-width:468pt; padding:72pt 72pt 72pt 72pt
```

### Section header (H2)
```
padding-top:0pt; margin:0; color:#1836b2; border-bottom-color:#1836b2;
padding-left:0; font-size:16pt; padding-bottom:2pt; line-height:1.15;
page-break-after:avoid; border-bottom-width:1pt;
font-family:"League Spartan"; border-bottom-style:solid;
orphans:2; widows:2; text-align:left; padding-right:0
```
Span inside: `color:#1836b2; font-weight:400; font-size:16pt; font-family:"League Spartan"; font-style:normal`

### All body paragraphs (`<p>`)
```
padding-top:0pt; margin:0; color:#000000; padding-left:0;
font-size:11pt; padding-bottom:10pt;
font-family:"Inter"; line-height:1.15;
orphans:2; widows:2; text-align:left; padding-right:0
```

### Instructions span (10pt, normal weight)
```
color:#000000; font-weight:400; font-size:10pt; font-family:"Inter"; font-style:normal
```

### Question text span (10pt, **bold**)
```
color:#000000; font-weight:700; font-size:10pt; font-family:"Inter"; font-style:normal
```

### Options span (10pt, normal weight)
```
color:#000000; font-weight:400; font-size:10pt; font-family:"Inter"; font-style:normal
```

### Checkbox pattern
`[&nbsp;&nbsp;&nbsp; ]` — exactly 3 non-breaking spaces followed by 1 regular space before `]`

### Paragraph structure per question
```
[question paragraph]  → <p><span style="bold">N. Question text</span></p>
[options paragraph]   → <p><span style="normal">[   ] A<br>[   ] B<br>[   ] C<br>[   ] D</span></p>
```
- Question text → its own `<p>` (hard break before and after)
- Options → single `<p>`, separated by `<br>` (soft break / Shift+Enter)
- No `<br>` after the last option

---

## Part II — Open-Ended Questions Format

Part II begins on a new page and each question starts on its own page.

### Page break (before Part II and before each individual question)
```html
<hr style="page-break-before:always;display:none;">
```

### Empty spacer H2 (appears once, before the Part II header)
```html
<h2 style="padding-top:10pt;margin:0;color:#1836b2;border-bottom-color:#1836b2;
           padding-left:0;font-size:16pt;padding-bottom:2pt;line-height:1.0;
           page-break-after:avoid;border-bottom-width:1pt;
           font-family:&quot;League Spartan&quot;;border-bottom-style:solid;
           orphans:2;widows:2;height:16pt;text-align:left;padding-right:0">
  <span style="color:#1836b2;font-weight:400;font-size:16pt;
               font-family:&quot;League Spartan&quot;;font-style:normal"></span>
</h2>
```

### Part II section header H2
Differs from Part I: `padding-top:10pt` (not 0pt), `line-height:1.0` (not 1.15).
```html
<h2 style="padding-top:10pt;margin:0;color:#1836b2;border-bottom-color:#1836b2;
           padding-left:0;font-size:16pt;padding-bottom:2pt;line-height:1.0;
           page-break-after:avoid;border-bottom-width:1pt;
           font-family:&quot;League Spartan&quot;;border-bottom-style:solid;
           orphans:2;widows:2;text-align:left;padding-right:0">
  <span style="color:#1836b2;font-weight:400;font-size:16pt;
               font-family:&quot;League Spartan&quot;;font-style:normal">
    PART II — Open-Ended Questions - 10 pts each (20 total)
  </span>
</h2>
```

### Part II instructions paragraph
Uses **11pt spans** (not 10pt like Part I).
```html
<p style="padding-top:0pt;margin:0;color:#000000;padding-left:0;font-size:11pt;
          padding-bottom:10pt;font-family:&quot;Inter&quot;;line-height:1.15;
          orphans:2;widows:2;text-align:left;padding-right:0">
  <span style="color:#000000;font-weight:400;font-size:11pt;
               font-family:&quot;Inter&quot;;font-style:normal">
    Answer the following questions in the space provided. Responses should be
    thorough and well-structured, demonstrating understanding of course concepts.
  </span>
</p>
```

### Each open-ended question (on its own page)
Each question is preceded by a page break. The question uses 10pt bold (same as Part I MCQ text). After the question text, include 18 empty paragraphs to provide writing space on the printed exam.

```html
<!-- page break before each question -->
<hr style="page-break-before:always;display:none;">

<!-- question number + text (bold 10pt) -->
<p style="padding-top:0pt;margin:0;color:#000000;padding-left:0;font-size:11pt;
          padding-bottom:10pt;font-family:&quot;Inter&quot;;line-height:1.15;
          orphans:2;widows:2;text-align:left;padding-right:0">
  <span style="color:#000000;font-weight:700;font-size:10pt;
               font-family:&quot;Inter&quot;;font-style:normal">
    16. Question text here.
  </span>
</p>

<!-- 18 blank answer-space paragraphs -->
<p style="padding-top:0pt;margin:0;color:#000000;padding-left:0;font-size:11pt;
          padding-bottom:10pt;line-height:1.15;font-family:&quot;Inter&quot;;
          orphans:2;widows:2;height:11pt;text-align:left;padding-right:0">
  <span style="color:#000000;font-weight:400;font-size:11pt;
               font-family:&quot;Inter&quot;;font-style:normal"></span>
</p>
<!-- repeat 17 more times -->
```

**Question numbering**: open-ended questions are numbered sequentially continuing from Part I. If Part I has 15 questions, Part II starts at 16, 17, etc.

---

## Open-Ended Question JSON Format

The exam version JSON produced by `shuffle_exam.js` may optionally include an `open_ended` array:

```json
{
  "version": "A",
  "questions": [...],
  "open_ended": [
    {
      "n": 16,
      "session": 1,
      "question": "Full question text here. Must be a single paragraph. Requires 2-3 paragraphs to answer."
    },
    {
      "n": 17,
      "session": 2,
      "question": "Full question text here..."
    }
  ]
}
```

Open-ended questions are **not shuffled** — they are always included in the order provided. The `session` field is metadata only (for the scoring guide).

---

## Step 1 — Build Exam HTML Files

Run `scripts/build_exam_html.js` for each version:

```bash
node scripts/build_exam_html.js \
  --input exam_A.json \
  --output exam_A.html \
  --section-header "PART I — Closed-Ended Questions" \
  --pts-per-question 4 \
  --total-pts 60
```

This produces an HTML file matching the template exactly.

---

## Step 2 — Build Scoring Guide HTML

Run `scripts/build_guide_html.js`:

```bash
node scripts/build_guide_html.js \
  --input answer_key.json \
  --exam-dir ./ \
  --output scoring_guide.html \
  --section-header "PART I — Closed-Ended Questions"
```

Produces a single HTML file with:
1. Intro paragraph
2. Scoring criteria section
3. Content distribution section (if metadata available)
4. One answer table per version: columns `#` / `Answer` / `Correct answer text`
5. Notes for graders section

---

## Step 3 — Upload to Google Drive

For each HTML file, call `Google Drive:create_file` with:
```
title:          "{Exam Title} — Version {Letter}"   (for exams)
                "{Exam Title} — Scoring Guide"       (for guide)
contentMimeType: "text/html"
parentId:        <gdrive_folder_id>
textContent:     <full HTML string>
```

**Important:** Use `textContent`, not `base64Content`. Pass the raw HTML string directly.

Collect the returned `id` for each file to build the final links:
```
https://docs.google.com/document/d/{id}/edit
```

---

## Step 4 — Report Results

After all uploads succeed, output to the user:

```
Exported to Google Drive folder {folder_id}:

  Version A → https://docs.google.com/document/d/{id}/edit
  Version B → https://docs.google.com/document/d/{id}/edit
  Version C → https://docs.google.com/document/d/{id}/edit
  Scoring Guide → https://docs.google.com/document/d/{id}/edit

No header has been added — paste your institutional header at the top of each exam doc.
```

---

## Scoring Guide Table Format

Use inline HTML tables (no external CSS). The header row uses the course blue
`#1836b2` as background with white text. Data rows alternate readable style.

```html
<table style="border-collapse:collapse;width:100%;margin-bottom:8pt">
  <tr>
    <th style="border:1pt solid #1836b2;padding:6pt 8pt;font-size:10pt;
               font-family:&quot;Inter&quot;;color:#ffffff;background-color:#1836b2;
               font-weight:700;width:28pt">#</th>
    <th style="border:1pt solid #1836b2;padding:6pt 8pt;font-size:10pt;
               font-family:&quot;Inter&quot;;color:#ffffff;background-color:#1836b2;
               font-weight:700;width:40pt">Answer</th>
    <th style="border:1pt solid #1836b2;padding:6pt 8pt;font-size:10pt;
               font-family:&quot;Inter&quot;;color:#ffffff;background-color:#1836b2;
               font-weight:700">Correct answer text</th>
  </tr>
  <tr>
    <td style="border:1pt solid #cccccc;padding:6pt 8pt;font-size:10pt;
               font-family:&quot;Inter&quot;;color:#000000;text-align:center;width:28pt">1</td>
    <td style="border:1pt solid #cccccc;padding:6pt 8pt;font-size:11pt;
               font-family:&quot;Inter&quot;;color:#1836b2;font-weight:700;
               text-align:center;width:40pt">B</td>
    <td style="border:1pt solid #cccccc;padding:6pt 8pt;font-size:10pt;
               font-family:&quot;Inter&quot;;color:#000000">Full correct answer text</td>
  </tr>
</table>
```

---

## HTML Escaping

Before inserting any text into HTML attributes or content, escape these chars:
```
& → &amp;
< → &lt;
> → &gt;
" → &quot;   (in attribute values only)
```

Do **not** escape apostrophes (`'`) in content — they render fine unescaped.

---

## Critical Rules

- **Never use `base64Content`** — always use `textContent` for the Drive upload
- **Font size is 10pt** for body text spans (the `<p>` container uses 11pt but spans override to 10pt)
- **Checkbox**: exactly `[&nbsp;&nbsp;&nbsp; ]` — 3 nbsp then 1 space
- **No trailing `<br>`** after the last option in the options paragraph
- **Question numbers are sequential** from 1 within each version (re-numbered after shuffling)
- **Section header pts** must match `pts_per_question × number_of_questions`
- The scoring guide answer letter column uses blue bold (`color:#1836b2; font-weight:700`)
