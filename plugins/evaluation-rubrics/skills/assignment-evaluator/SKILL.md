---
name: assignment-evaluator
description: >
  Evaluates student or group assignment submissions against an existing rubric and records
  results in a cumulative grades .xlsx file. Use this skill when the user provides a student
  submission (PDF, docx, md, txt, or a video — YouTube link or local video file) and a rubric, and wants to score or grade the work. Trigger on phrases
  like: "evaluate this submission", "grade this assignment", "score this lab", "add this
  student to the grades file", "evaluate against the rubric", or any request to assess
  student work using a rubric. Each invocation appends one row to the grades file.
  Do NOT trigger this skill for creating or generating rubrics — that is a separate task.
---

# Assignment Evaluator

Reads a student/group submission (document or video), scores it against a rubric xlsx, and
appends one row to a cumulative grades file.

## Step 1 — Gather Inputs

Required each time:
1. **Submission file** — the student or group's work. Supported formats:
   - PDF — read directly; name extracted from cover page.
   - `.docx` — read via the docx skill; name extracted from cover page.
   - `.md` / `.txt` — read as plain text; no cover page expected (see name rules below).
   - **Video** — a YouTube URL (public/unlisted), a local video file (`.mp4`, `.mov`, `.mkv`,
     `.webm`, …), or a document whose deliverable is a video link. Graded from an evidence pack;
     see **Video submissions** below before Step 3.
2. **Rubric xlsx** — produced by rubric-creator; defines criteria and weights.
3. **Assignment brief** (PDF or text) — provides context for what was expected.

Derived automatically:
- **Student/group name** — resolution order:
  1. Explicitly provided in the user's prompt → use it, no questions asked.
  2. Present in the submission filename (e.g., `lab01_grupo3.pdf`) → use it, confirm with user if ambiguous.
  3. Found on a cover page (PDF or docx only) → extract it.
  4. None of the above → ask the user before proceeding. Do not guess.
- **Output directory**:
  - If the user specified a destination folder, use that folder.
  - Otherwise, default to the **same folder as the submission file**.
- **Evaluations subfolder**: row JSONs are always stored in `<output_dir>/evaluations/`.
  Create this subfolder if it doesn't exist.
- **Grades output filename**: derive from the assignment name or rubric filename.
  - Pattern: `grades_<assignment_slug>.xlsx` in `<output_dir>`.
  - If a file with that name already exists, it will be appended to by `/build-grades`. If not, it will be created.

## Step 2 — Read the Rubric

Parse the rubric xlsx to extract criteria names and weights (column A and column E, rows 2+).
This determines the column structure of the grades file.

**Two scoring modes — pick by the rubric, never mix them in one grades file:**

- **Level mode** (default; rubric `.xlsx`): Meets = 100 %, Partially = 60 %, Does Not Meet = 0 of
  each criterion's weight, summed to 100.
- **Piece mode** (rubric `.json` with `"scoring": "piezas"`): each criterion is a *piece* with a
  `code`, fixed `pts` and a fixed partial value `pts_parcial` (a number, or `"50 %"` of `pts`). A
  group earns only the pieces it delivers; the sum is capped at `cap`, then converted to the
  grade with `conversion` (a number, `{"divide_by": 100, "multiply_by": 3}`, or the string
  `MIN(puntos;300)/100*3`). Open pieces whose `pts` is a range (`"10–25"`) need the agreed value
  per row in `piece_points`. Pass the **JSON** (not the xlsx) to the scripts in this mode.
  Pieces outside the group's approved plan are **`not_applicable`** — they score 0 and are
  excluded, never "Does Not Meet".

Rubrics may also carry an **optional penalties block** below the additive table (a bold heading
row whose text starts with "Penal…", a header row, then one row per penalty with a free-text
amount like `-15` or `-100%` in column E). `append_grade.py` parses this block separately — note
which penalties exist so you can assess them in Step 3. Rubrics with no penalties block behave
exactly as before.

## Video submissions

If the submission is, or contains, a video link/file (several links → one pack each), you are
the **judge**; `video-evidence` (same plugin) only captures, indexes and selects evidence.

1. **Evidence.** Run `video-evidence` Steps 0–3 with `--out <output_dir>/evidence/ --id <slug>
   --rubric <rubric JSON, else xlsx>` (+ `--max-duration` / `--lang` when the brief implies them).
   Preflight fails → stop and point the user to `/evaluation-rubrics:install-video-deps`.
   **You coordinate sources.** If capture exits **3** (`manual_download_needed` JSON on stdout),
   ask the instructor — one message per batch, listing for each submission: the student/group,
   the original URL, the reason, and the exact `save_to` path to save the file to. Optionally,
   if this session has an authenticated connector that can export the file (e.g. Canva →
   export MP4), use it instead and pass `--obtained-via connector`. Then resume with the JSON's
   `resume_args`. Never guess a source or skip a submission silently.
   Late-delivery and similar items that no video can show (submission timestamps) go straight
   to REVIEW_REQUIRED with reason "outside the video" — don't spend evidence work on them.
   Model tiers are fixed: capture = script, index = Haiku, select = Sonnet, judge = you (the lead;
   or one Sonnet per video when you delegate judging of many submissions — keep borderline items).
2. **Judge from `evidence-map.json`.** For each item read its candidates and `coverage`, open
   **every cited frame** at full resolution (open more frames if a candidate is ambiguous; follow
   `static_until` spans), read cited quotes in context in `transcript.json`, and decide the
   verdict against the rubric's level texts. Rules (non-negotiable):
   - **Absence of evidence ≠ evidence of absence.** If the requirement could have appeared
     between sampled frames, during a fast scroll/transition, or the text is unreadable →
     `REVIEW_REQUIRED` with a `{from, to, reason}` window. Never Does Not Meet / not_met for that.
   - `Does Not Meet` / `not_met` needs **positive** evidence: a frame showing the wrong thing, a
     transcript statement, or a metadata fact (e.g. `probe.duration_s` 412 vs a 300 s cap).
   - `metadata.transcript.sparse` → the transcript is not narration evidence (Whisper invents
     filler over music); judge narration from frames or flag REVIEW_REQUIRED.
   - YouTube description not fetched (`youtube` null / `download.status` ≠ `ok`) →
     description-based items are REVIEW_REQUIRED.
   - Small-text questions (product name vs code, exact values) are decided only from the
     full-resolution frame — never from the Haiku index.
   - **Accessibility is not inferred from download failures.** A failed automatic download
     (yt-dlp 403, bot check, unsupported host) says nothing about whether the instructor can open
     the link. Never mark an accessibility/"video accesible" item `not_met` on that basis. When
     `metadata.source.obtained_via` is `manual` or `connector`, the accessibility verdict comes
     from the instructor's confirmation that they could open the original link with their own
     account — record it in the note with its source (e.g. "instructor opened the Drive link
     2026-11-02"); until confirmed, it is REVIEW_REQUIRED. Non-YouTube hosts (Drive, Canva, …) are
     not a defect in themselves.
   - On-screen text (`on_screen` in a candidate: slides, text boxes, overlays) is evidence like a
     transcript quote — cite it as `{"t", "frame", "on_screen": "<verbatim text>"}` after checking
     it on the frame.
3. **Write `<pack>/verdicts.json`** (shape in video-evidence `references/output-contract.md`): one
   entry per evidence-map item with `verdict`, `note`, `cites` (t + frame/quote/metadata_field),
   `review_required` windows, plus 5–10 chronological `key_moments` (cover → … → final state).
   Optional verdict fields: `"not_applicable"` verdict (pieces outside the plan: no cites, excluded
   from review); `outside_video: true` on items no video can show (rendered without window or
   link); `confirmation: {by, via: "direct"|"relayed", relayed_by?, at?, note?}` recording who
   confirmed accessibility and how (a relayed confirmation names the relaying session); top-level
   `extra_sections: [{title, markdown}]` for instructor sections (e.g. plan vs delivered). Render
   with `--preamble <file>` for a header block (file view link, notes). Both live in inputs, so
   re-rendering never loses them — don't hand-edit review.md.
   Then render the audit page:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/video-evidence/scripts/render_review.py" <pack> <pack>/verdicts.json
   ```
   It validates citations, adds `watch` links (YouTube `youtu.be/<id>?t=` ~3 s early; local
   files `mm:ss path`) and writes `<pack>/review.md`: REVIEW_REQUIRED first, then verdicts with
   watch links and thumbnails, then the key-moments sequence. `review.md` is student data — keep
   it local, never publish it.
4. **Step 3 below** maps verdicts 1:1 to score labels / penalty levels. Every Partially Meets /
   Does Not Meet observation carries the watch link or mm:ss, e.g. "chart at 02:14 shows product
   codes, not names (https://youtu.be/abc123?t=131)", so the xlsx points to the minute.
5. **REVIEW_REQUIRED is not a score.** Present those items first at the Step 4 pause (with watch
   links and the `review.md` path) and get the instructor's call; never convert one yourself. The
   row JSON and `append_grade.py` accept only the three labels, so nothing is written until every
   item is resolved. Steps 4–6 are otherwise unchanged; the pack stays as the audit trail and the
   downloaded video itself is deleted.

## Step 3 — Evaluate the Submission

For each criterion in the rubric, read the submission and assign one of three labels.
Consult `references/performance-levels.md` for scoring rules and thresholds.

Score label must be exactly one of:
- `Meets Expectations`
- `Partially Meets`
- `Does Not Meet`

For every criterion scored as **Partially Meets** or **Does Not Meet**, write a concise
observation explaining why. Be specific — reference actual content (or absence of it) from
the submission. Example: "only 2 of the 10 required items were completed."

**Penalties (only if the rubric has a penalties block).** Assess each penalty row and pick a
level:
- `met` / `cumple` — the requirement is satisfied → no deduction.
- `partial` / `parcial` — partially satisfied → 40% of the penalty magnitude is deducted
  (the mirror of the 60% partial credit on the additive side). Use only if the penalty defines
  a real partial level; many (e.g. a `-100%` penalty) have no partial and are met-or-not.
- `not_met` / `no_cumple` — the requirement is violated → the full penalty applies.

The deduction amounts come from the rubric itself: a numeric amount (`-15`) subtracts points; a
percentage (`-100%`) removes that share of the total, so a `-100%` penalty scored `not_met`
zeroes the grade (invalid work). Add a short `note` on each penalty you score as partial or
not-met — it is surfaced in the observations cell alongside the deduction.

**Language rule**: write observations in the language of the assignment brief. If the
assignment brief language cannot be determined, fall back to the rubric language.

## Step 4 — Build the Row JSON

`observations` is an object with one key per criterion. Set the value to an empty string
for criteria that meet expectations; write the reason for those that don't.

Add a `penalties` object **only if the rubric has a penalties block**. Each key is a penalty
name from the rubric; the value is either a bare level string or `{"level": ..., "note": ...}`.
Omit `penalties` entirely for penalty-free rubrics (backward compatible).

```json
{
  "name": "Group 1",
  "scores": {
    "Hardware Empresarial (Servidores)": "Meets Expectations",
    "Hardware Personal (PCs)": "Partially Meets",
    "Software Empresarial (Sistemas Críticos)": "Does Not Meet"
  },
  "observations": {
    "Hardware Empresarial (Servidores)": "",
    "Hardware Personal (PCs)": "specs documented for only 1 of 3 group members.",
    "Software Empresarial (Sistemas Críticos)": "no software investigated."
  },
  "penalties": {
    "Buena presentación": "met",
    "Archivo adjunto": "met",
    "Marco de IA": {"level": "not_met", "note": "used AI but never declared it"}
  }
}
```

Save to `<output_dir>/evaluations/row_<slug>.json`.

**Pause here.** Present the evaluation to the user in chat as a summary table (name, each
criterion with its score, and any observations; for videos, REVIEW_REQUIRED items first with
their watch links, and the path to `review.md`). Ask the user to confirm or request
corrections before writing the grades file. Do not run Step 5 until the user approves.

## Step 5 — Append to Grades File

Once the user confirms the evaluation:

```bash
python scripts/append_grade.py <rubric_xlsx|rubric_json> <grades_xlsx> <output_dir>/evaluations/row_<slug>.json
```

**Piece mode** (rubric JSON with `"scoring": "piezas"`): the row JSON's `scores` keys may be the
piece code (`"D8"`), its name, or `"D8 · name"`; values are the three labels or
`"not_applicable"` (`"N/A"`); pieces not listed count as not_applicable. Add
`"piece_points": {"O9": 20}` for range pieces. The grades sheet is
`Name | <code · name> per piece | Puntos | Nota | Observations`: Puntos = Σ pieces − point
penalties (e.g. −15, partial −6), then capped (a `CAP — puntos 320 → 300` note is added); Nota =
Puntos × conversion, then percentage penalties (−50 %, −100 %) apply to the Nota. Puntos and
Nota round half-up to 2 decimals. The script refuses to append a row of one mode into a sheet of
the other, and errors on unknown piece/penalty names (piece mode is strict on purpose).

The script (level mode):
- Creates the grades file with the correct header if it doesn't exist yet.
- Appends the row and calculates the total automatically from rubric weights.
- Applies any `penalties` from the row JSON against the rubric's penalties block (point
  deductions first, then percentage deductions, clamped at 0), and appends a short
  `PENALTY — …` note to the observations cell for each deduction.
- Compiles the `observations` dict into a single string for the xlsx cell.
- See `references/column-layout.md` for output file structure and formatting rules.

## Step 6 — Deliver

- Present the grades file with `present_files`.
- Report: student/group name and total score — nothing else.
