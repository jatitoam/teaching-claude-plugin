---
name: practical-exam-print-format
description: Final print-formatting pass for a course-factory practical exam whose statement(s) are ALREADY published as Google Docs (one Doc per case/version). Drives Google Docs in Chrome (Claude in Chrome tools) to match a base practical-exam Doc — Title/Subtitle banners, headings, table header colour and sizes, printed (unlinked, scheme-less) addresses — without changing the text. Part of the course-factory harness; invoked by the `practical-exam` skill as its last step, or deliberately by the conductor with /practical-exam-print-format. Do NOT auto-trigger for generic Google Docs formatting requests.
---

# Practical exam print format (Google Docs, via Chrome)

Turns a freshly published practical-exam Doc (plain Markdown import: title line, subtitle line,
`#` sections, native tables, clickable URLs) into the printable layout of the course's **base
practical-exam Doc**: Title and Subtitle banners touching each other, headings as in the base, every
table with the base's header colour, addresses printed big and unlinked so students can copy them
by hand — and **not one word of the text changed**.

**Tier:** a **Sonnet** agent executes the procedure on **one Doc per run**. The orchestrator (Opus)
launches the runs **sequentially** — they share one Chrome window — and verifies each result
itself (§Orchestrator verification) before launching the next. The orchestrator does not use the
browser while a run is in progress.

*(Procedure proven on 2026-11-02 with the course-local predecessor of this file: 10 statement Docs
of one partial exam formatted by Sonnet agents and verified by the lead with course-specific
scripts. The generalized scripts were then run live on 2026-11-02: `doc-report.js` on the base and
on one formatted Doc gave the expected values, and `text-fingerprint.py` reproduces the verified
fingerprints.)*

## Inputs (all required — stop and ask if any is missing)

| Input | Where it comes from |
|---|---|
| `TARGET_DOC_ID` | The Doc to format — from the session handover (Published column). |
| `SOURCE_MD` | The **exact** `.md` passed to `publish-google-doc` for that Doc (the per-Doc file, not a master file that also holds keys or notes). **Source of truth** for the text. |
| `SKILL_DIR` | Absolute path of this skill's folder (the caller passes it — the Skill tool's «Base directory»); `scripts/…` below means `<SKILL_DIR>/scripts/…`. |
| `BASE_DOC_ID` | `course.yaml → publishing.practical_print.base_doc` — the sample practical exam provided at bootstrap. If empty, this skill does not run (the caller skips it). |
| `RUBRIC_TABLE_PT` · `TABLE_PT` · `URL_PT` | `publishing.practical_print.{rubric_table_pt, table_pt, url_pt}` (e.g. 9 · 11 · 16). |
| `RUBRIC_COLS_CM` · `PENALTY_COLS_CM` | `publishing.practical_print.{rubric_cols_cm, penalty_cols_cm}` (e.g. `[4.1, 10.7, 1.8]` · `[4.8, 9.1, 2.5]`). |
| `STRIP_SCHEME` | `publishing.practical_print.strip_scheme` (default `true`): remove `https://` from printed addresses. |

**Rubric and penalty tables** = the tables whose header row matches the rubric and the penalties
tables of `SOURCE_MD`'s rubric section (normally the last two tables of the Doc). Every other table
is an «other table».

`publishing.practical_print` is filled at bootstrap (`course-bootstrap` question 7c). Colours, fonts
and banner styles are **not** configured: they are read from the base Doc in step 0. Menu names below
are the Spanish UI (the course account's language); in an English UI they are Format › Line &
paragraph spacing, Edit › Find and replace, Table properties, etc.

## Hard rules (each one broke a Doc during development)

1. **Text is frozen.** The only text change allowed is removing the URL scheme (step 3), and only
   with **Editar › Buscar y reemplazar** — never by deleting characters by hand: manual deletion
   took one character too many in 3 of 4 Docs. Any other wording problem is reported, not fixed:
   it belongs in `SOURCE_MD` and a republish, which is the conductor's call.
2. **Never republish to "fix" formatting** — all formatting is lost and the old Doc is orphaned.
3. **Never «Guardar como mis estilos predeterminados» / «Usar mis estilos predeterminados»** — that
   changes the account's defaults for every future Doc.
4. **Touch the base Doc only to read it** (screenshots, `doc-report.js`). Never edit any Doc other
   than `TARGET_DOC_ID`.
5. **Table formatting stays inside tables.** Select only table cells before applying the table size
   or spacing; body paragraphs keep their size and spacing. (An agent once applied the table's
   no-spacing to the whole body and had to undo it.)
6. **No comments.** Clicks in the margin open «Añadir comentario» easily: cancel it. Never post one.
7. **Checkpoints:** screenshot and look before every `Delete`, after every Buscar y reemplazar and
   after formatting each table. If something went wrong: `cmd+z` back to the last good state.
8. If an action fails 2–3 times, stop and report — do not insist.

## Procedure

### 0 · Setup and base readout
- Load tools in ONE ToolSearch call:
  `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__tabs_close_mcp`
- `tabs_context_mcp` with `createIfEmpty: true` → navigate that tab to **BASE**
  `https://docs.google.com/document/d/<BASE_DOC_ID>/edit`; `tabs_create_mcp` → **TARGET**
  `https://docs.google.com/document/d/<TARGET_DOC_ID>/edit`.
- In BASE, run `scripts/doc-report.js` (paste its content into `javascript_tool`) → keep the JSON
  as **EXPECTED**. The tool truncates long results: the script leaves a global `report`, so read
  the rest with a second short call, e.g.
  `JSON.stringify({urls: report.urls, tables: report.tables.map(t => [t.index, t.header.join('|'), t.headerBg, t.pt, t.spacing])})`.
  Keep from EXPECTED: `title`, `subtitle`, `h1` (pt, font, weight, colour, band), and the
  `tables[].headerBg` of the **rubric** table = the header colour to use everywhere.
- **Validate BASE:** `title.band` and `subtitle.band` are coloured (not `rgba(0, 0, 0, 0)`) and its
  rubric table has a coloured `headerBg` with white `headerText`. If not, the sample is not usable:
  STOP and report «base_doc is not a formatted practical-exam sample» — do not improvise.
- In TARGET, run `doc-report.js` → keep as **BEFORE** (its `fingerprint` must equal
  `python3 scripts/text-fingerprint.py <SOURCE_MD>` on `n` and `sha` — compare values, the Python
  prints a dict. If not, STOP and report both values: the Doc was edited or `SOURCE_MD` is the wrong
  file — the caller decides). If BEFORE already shows the banners and `links: []`, it was already
  formatted: STOP, report.

### 1 · Title and Subtitle
1. Click line 1 → toolbar style dropdown → **Título**. Click line 2 → clear the manual bold/italic the
   Markdown import left (`cmd+\` on the selected line) → **Subtítulo**.
2. Compare with EXPECTED. If the target's Title/Subtitle differ from the base's (other font, size,
   band), format one paragraph to match the base and use Formato › Estilos de párrafo › Título ›
   «Actualizar "Título" para que coincida» (same for Subtítulo) — only in this Doc.
3. **Remove the space after the Title:** caret in the Title → Formato › Interlineado y espacio entre
   párrafos → «Eliminar espacio después del párrafo» (if the menu offers it, the space was there).
   Zoomed screenshot: the Title band and the Subtitle band must touch — no white strip.

### 2 · Headings
Compare `h1` with EXPECTED. If it already matches, do nothing. If not, match one Título 1 paragraph
to the base and «Actualizar "Título 1" para que coincida». Same for Título 2 if the Doc has them.

### 3 · Addresses (template links, folders, any URL)
1. If `STRIP_SCHEME`: Editar › Buscar y reemplazar (`cmd+shift+h`) → find `https://`, replace with
   nothing → «Reemplazar todo». Repeat for `http://`. Close the dialog. Checkpoint screenshot.
2. **Unlink everything:** for every entry of BEFORE's `links` (in a sentence, in a table, or an
   address), click inside the linked text → in the link bubble, «Quitar vínculo».
3. For each address paragraph (BEFORE's `urls` lists them): select the whole paragraph (`Home`,
   `shift+End`) and set: **centred** (`cmd+shift+e`), **bold**, size `URL_PT`, text colour **black** (#000000), no underline. If the
   paragraph is a list item, turn the bullet off. Its label line («Use la plantilla…») stays above it,
   unchanged.

### 4 · Tables (all of them)
For each table: click in the first cell, `shift+click` in the last cell (whole table selected), then:
1. Size: `RUBRIC_TABLE_PT` for the rubric and the penalty table, `TABLE_PT` for every other table.
2. Formato › Interlineado y espacio entre párrafos → remove space **before and after** the paragraph
   (with the table selected the menu applies to every cell). Done when, with the table selected, the
   menu offers «Agregar espacio antes» and «Agregar espacio después».
3. Header row: select only row 1's cells → Formato › Tabla › Propiedades de tabla › Color › cell
   background = EXPECTED rubric `headerBg` (convert `rgb(r, g, b)` to hex, enter it as a custom
   colour) → text **white** and **bold**.
4. Column widths (Propiedades de tabla › Columna, values in cm; usable width ≈ the page width minus
   margins): rubric `RUBRIC_COLS_CM`, penalty `PENALTY_COLS_CM`; other tables — short columns
   (codes, prices, numbers) narrow, long text wide, no word broken across lines.
5. Checkpoint screenshot of the table.

### 5 · No blank last page
`cmd+End` and screenshot: the caret must be on the same page as the last table. If a page holds only
the empty paragraph Docs keeps after the last table: with the caret there, «Eliminar espacio después»
and font size **1**. Check again.

### 6 · Verify and report
- Run `doc-report.js` in TARGET → **AFTER**. Required: `fingerprint` = BEFORE's; `links` `[]`;
  `schemes` 0 (if `STRIP_SCHEME`); `comments` 0; title/subtitle/h1 = EXPECTED on pt, font, weight,
  color, band, align (ignore `text` and `spacing` — see §Orchestrator verification for the Title
  space); every url centred, `URL_PT`, weight 700, black, no decoration, `spanStyles` 1; every table
  `headerBg` = EXPECTED's, white bold header, `spacing` `["0px/0px"]`, `pt` as in step 4; `body` and
  `bodyStyles` = BEFORE's (same set of pt|spacing over every body paragraph — proves table
  formatting did not leak). Column widths are
  judged on the screenshots.
- Screenshots: cover page (both banners), every address, every table, the last page.
- Close every tab you opened.
- Report: Doc ID, AFTER vs EXPECTED/BEFORE (mismatches only), incidents and how they were undone, and
  a «Friction» list of steps that were ambiguous or wrong.

## Orchestrator verification (the caller does this, not the agent)

Do not accept the agent's report on its word. In a tab of your own on TARGET:
1. Run `scripts/doc-report.js` and `python3 scripts/text-fingerprint.py <SOURCE_MD>`: same `n` and
   `sha` — this is what catches a character lost while touching the addresses. Check every field
   listed in step 6.
2. **What the export cannot show:** caret in the Title → Formato › Interlineado: the menu must offer
   «Agregar espacio después» (= none left), plus a zoomed screenshot with the two bands touching; and
   `cmd+End` + screenshot: the Doc ends on the page of its last table.
3. Close your tab before launching the next run. Any mismatch → the same agent (SendMessage) fixes it
   before the next Doc. Never judge by the Drive connector's `read_file_content`: it shows empty
   header rows and `\*\*` the Doc does not have.

## course.yaml block

```yaml
publishing:
  practical_print:
    base_doc: "<Doc ID of a practical-exam statement already formatted by hand>"
    rubric_table_pt: 9        # rubric and penalty tables
    table_pt: 11              # every other table
    url_pt: 16                # printed addresses
    rubric_cols_cm: [4.1, 10.7, 1.8]
    penalty_cols_cm: [4.8, 9.1, 2.5]
    strip_scheme: true        # print "host/path", not "https://host/path"
```

## Who calls it

- The `practical-exam` skill, **automatically**, as the last step of its publication whenever
  `publishing.practical_print.base_doc` is set: once per published student-facing statement Doc
  (never the conductor notes or answer keys), sequentially, delegating each run to a Sonnet agent
  and verifying it per §Orchestrator verification.
- The conductor, deliberately, to (re)format a single Doc.
