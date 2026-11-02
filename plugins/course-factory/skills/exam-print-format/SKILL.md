---
name: exam-print-format
description: Final print-formatting pass for a course-factory concept-check exam that is ALREADY published as a Google Doc (one Doc per exam version/temario). Drives Google Docs in Chrome (Claude in Chrome tools) to copy the institutional first-page header and the two-column answer table from a base exam Doc, apply the course's Title style, shrink body text, and fit each version to an exact page count. Part of the course-factory harness; invoked by the `exam` skill as its last step, or deliberately by the conductor with /exam-print-format. Do NOT auto-trigger for generic Google Docs formatting requests.
---

# Exam print format (Google Docs, via Chrome)

Turns a freshly published exam Doc (plain Markdown import: title line, `**N.**` stems, `☐ option`
lines) into the printable layout of the course's **base exam Doc**: institutional header on page 1
only, Title-style banner, small body text, each question's options in the base's 2-column table
(`[  ]` | option), and an **exact page count**.

**Tier:** a **Sonnet** agent executes the whole procedure (mechanical, but it needs screenshots and
judgment at checkpoints). The orchestrator (Opus) launches it **once per Doc, sequentially**, and
verifies the result itself (§Orchestrator verification). Never run two of these in parallel: they
share one Chrome window and the system clipboard. The orchestrator must not use the browser while
a run is in progress.

*(Validated end to end on 2026-11-01: one Doc formatted by hand while the procedure was written,
a second one by a Sonnet agent following only this file — 10/10 questions correct, 2/2 pages.)*

## Inputs (all required — stop and ask if any is missing)

| Input | Where it comes from |
|---|---|
| `TARGET_DOC_ID` | The Doc to format — from the session handover (Published column). |
| `SOURCE_MD` | The `.md` that Doc was published from (e.g. `<folders.exams>/publicar/S18-temario-2.md`). **Source of truth** for stems and option order — the answer key depends on that order. |
| `BASE_DOC_ID` | `course.yaml → publishing.exam_print.base_doc` — the sample exam provided at bootstrap. If empty, this skill does not run (the caller skips it). |
| `TITLE_TEXT` | `course.yaml → publishing.exam_print.title`, with `{n}` filled (e.g. «Examen Parcial 2»). |
| `PAGES` | `course.yaml → publishing.exam_print.pages` (e.g. 2). |
| `BODY_PT` | `course.yaml → publishing.exam_print.body_pt` (e.g. 10). |

`publishing.exam_print` is filled at bootstrap (`course-bootstrap` question 7b). If `base_doc` is
empty this skill is not run; if another field is missing, stop and report it to the caller. Menu
names below are the Spanish UI (the course account's language); in an English UI they are
Format › Paragraph styles / Line & paragraph spacing, etc.

## Hard rules (each one broke a Doc during development)

1. **Paste is asynchronous in Google Docs.** After every `cmd+v`, use the `wait` action (**≥ 1.5 s**)
   before sending ANY other key. Keys sent right after a paste create a selection that the paste then
   **replaces** — it silently eats the stem and the options.
2. **Undo of a paste leaves the restored text SELECTED.** After any `cmd+z`, click in the document to
   collapse the selection before typing or pasting.
3. **The font-size box keeps focus.** After typing in it, focus stays there (and its dropdown list may
   stay open — click the same value in the list to close it): `cmd+End`/`Backspace` would then act on
   the old caret position in the text. Always **click in the page** before navigating with keys.
4. **Never pick «Texto normal» from the toolbar style dropdown** — clicking it *applies* the style and
   wipes inline bold. Update styles only through Formato › Estilos de párrafo (step 3).
5. **«Actualizar … para que coincida» copies the formatting at the caret.** Put the caret inside a
   **non-bold** word first, or bold leaks into the Normal style.
6. **Coordinates are in the full frame.** If you take a scaled screenshot (e.g. `scale: 0.6`), divide
   its pixel positions by the scale before clicking. Take a screenshot before every click whose target
   you have not seen yet — positions vary with window size.
7. **Checkpoints are mandatory.** Any batch that pastes or before any `Delete` ends with a screenshot
   that you LOOK at. If something went wrong: `cmd+z` (screenshot after each) back to the last good
   state — never fix forward over a mangled question.
8. The Doc is canvas-rendered: `get_page_text`/`read_page`/fetch return nothing useful. Verification is
   visual (full-resolution screenshots) against `SOURCE_MD`.
9. Touch the base Doc only to select and copy. Never edit any other Doc.

## Procedure

### 0 · Setup
- Load tools in ONE ToolSearch call:
  `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__tabs_close_mcp`
- `tabs_context_mcp` with `createIfEmpty: true` (it gives you one empty tab) → navigate it to **BASE**
  `https://docs.google.com/document/d/<BASE_DOC_ID>/edit`; `tabs_create_mcp` → navigate it to
  **TARGET** `https://docs.google.com/document/d/<TARGET_DOC_ID>/edit`. Screenshot both.
- Read `SOURCE_MD` and build the ordered list: for each question N, its 4 options exactly as written
  after `☐ ` (keep accents and punctuation).
- **Validate BASE** (screenshot of its page 1): it must show a first-page header (logo / name
  fields), a title banner and, under question 1, a 2-column answer table (`[  ]` | option). If any
  is missing, the sample is not usable: STOP and report «base_doc is not a formatted sample» — do
  not improvise a layout.
- If TARGET already shows the header, banner or answer tables, it was already formatted: STOP, report.

### 1 · Header (page 1 only)
1. BASE: double-click **on the header area itself** (beside the logo / on the name fields). The bar
   «Encabezado de la primera página» appears. `cmd+a` (selects only the header content), `cmd+c`,
   `Escape`.
2. TARGET: double-click in the top margin above the title → an empty header opens. *(While it is
   open its bar covers the first body line — the title has not disappeared.)* Screenshot, then tick
   **«Primera página diferente»** on the header bar. Click inside the (now «primera página») header →
   `cmd+v` → wait 1.5 s → `BackSpace` once (removes the empty trailing line) → `Escape`.
3. Screenshot: logo + fields visible on page 1, no blank line under them.

### 2 · Title and instructions
1. Click on the title line. Open the toolbar style dropdown: the entries right under «Texto normal»
   render **blank** (white text). Click the **first blank entry** = Título. The banner appears.
2. Replace the title text: `cmd+Up` (start of the document = start of the title), then
   `shift+alt+Down` (selects the whole paragraph), type `TITLE_TEXT`. It must fit on ONE line.
3. Delete the instructions line under the title (e.g. «Preguntas 1 a 10 — 10 puntos cada una»):
   click on it, `Home`, `shift+End`, `Delete`, `Delete`.

### 3 · Normal style: BODY_PT, no space after paragraph
1. Triple-click question 1's stem. Toolbar size box: triple-click it, type `BODY_PT`, `Return` (close
   the size list if it stays open — rule 3). Check the bold words are still bold (if not, `cmd+z`).
2. Click inside a **non-bold** word of that stem. Formato › Interlineado y espacio entre párrafos ›
   «Eliminar espacio después del párrafo».
3. Same caret: Formato › Estilos de párrafo › Texto normal › click the **arrow at the right edge** of
   that row → in the third-level menu click «Actualizar el Texto Normal para que coincida con la
   selección». All body text shrinks and the `☐` lines lose their gaps.

### 4 · Copy the answer table from BASE (once)
BASE: click on the **last line** of question 1's stem, `End`, then `shift+Down` once — the selection
jumps over the whole table. If it reaches into question 2's stem, `shift+Up` until the selection is
exactly «end of stem → whole table» (screenshot to confirm). `cmd+c`. The clipboard now holds
«paragraph break + table» and is reused for every question — copy nothing else until you finish.

### 5 · Per question N = 1 … last
1. **Caret at the end of stem N.** N = 1: click after the stem's last word, `End`, zoom-check that the
   caret is right after the final `?`. N > 1: from the last answer cell of the previous table press
   `Down` (start of stem N) then `alt+Down` (end of that paragraph) — reliable for 1- to 3-line stems.
2. `cmd+v` → **wait 1.5 s** → `Home` → `shift+Down` ×5 (last question: ×4 then `shift+End`).
   **Checkpoint screenshot:** the selection must cover exactly the empty line the paste left under the
   table + the 4 `☐` lines, and nothing of the next stem. If not: `cmd+z`, rule 2, redo.
3. `Delete`. The caret is now at the start of stem N+1 (or, for the last question, in the empty
   paragraph after the table). Either way: `Up` ×4, then `Tab` → row 1's answer cell is selected.
4. Type option 1, `Tab Tab`, option 2, `Tab Tab`, option 3, `Tab Tab`, option 4 — exact text from
   `SOURCE_MD`, same order. Typing replaces the cell text and keeps the table's formatting.

**Efficient pattern (proven):** one `browser_batch` per question = [type the 4 options of question N]
+ [`Down`, `alt+Down`, `cmd+v`, wait 1.5 s, `Home`, `shift+Down`×5] + screenshot. Look at the
screenshot; if the selection is right, the next batch starts with `Delete`, `Up`×4, `Tab`.
**Do not judge the layout during step 5:** tables may look split across pages and big gaps may
appear; that resolves in step 6.

### 6 · Fit to PAGES
1. Click in the body, `cmd+a`, Formato › Interlineado y espacio entre párrafos › **Sencillo**. Collapse
   the selection with a **mouse click** on plain stem text (outside any table) — not in the grey
   area, which may be outside the window. **No keys here:** `cmd+Up` at this point opens the page-2
   header editor (harmless if you `Escape`, but don't).
2. Scroll to the end. If a last page holds only an empty line (the paragraph Docs keeps after the last
   table): **click directly on that empty line**, set size **1** in the toolbar box, `Return`. If
   there is no such page, skip this.
3. Scroll through the document; the «N de M» counter shows next to the right scrollbar while
   scrolling. Required: M = `PAGES`, header only on page 1, **no question's table split across
   pages**. If a table still splits or M > `PAGES`, report it — do not shrink fonts on your own.
   A blank band (~90 px) at the top of page 2 and later pages is **expected**: it is the margin of
   the empty non-first-page header. Do not report it or try to remove it.

### 7 · Verify and report
- Full-resolution screenshots covering every page. Compare, question by question, each stem and the
  4 options **in order** against `SOURCE_MD`. List any difference.
- Close every tab you opened (both of them).
- Report: Doc ID, page count, header only on p.1 (yes/no), table per question (N · stem ok · options
  ok and in order), any incident and how it was undone, and a «Friction» list of steps that were
  ambiguous or wrong.

## Orchestrator verification (the caller does this, not the agent)

Do not accept the agent's table on its word. Open TARGET yourself, take full-resolution screenshots
of every page, and compare against `SOURCE_MD` (print it with the `**` stripped for easy reading).
Check page count and header only on page 1. Close your tab before launching the next run.

## course.yaml block

```yaml
publishing:
  exam_print:
    base_doc: "<Doc ID of an exam already formatted by hand>"
    title: "Examen Parcial {n}"
    pages: 2
    body_pt: 10
```

## Who calls it

- The `exam` skill, **automatically**, as the last step of its publication whenever
  `publishing.exam_print.base_doc` is set: once per published student Doc (never the key),
  sequentially, delegating each run to a Sonnet agent and verifying it per §Orchestrator verification.
- The conductor, deliberately, to (re)format a single Doc.
