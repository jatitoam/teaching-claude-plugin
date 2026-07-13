<!--
  SHARED-CONTEXT SEED — course-factory / course-bootstrap
  ========================================================
  Copied into <course>/.claude/refs/shared-context.md. It starts EMPTY-but-structured: the fixed
  conventions block is filled from the interview; the tier-calibration table is seeded with the
  default rows below (drop rows for disabled skills); the per-session lessons and verified-Drive-IDs
  sections start empty; open technical items is seeded with the known limitations to re-verify.
  DELETE every <!-- bootstrap: ... --> comment from the generated file. Content in course.language.
-->
# Shared context — material production ({{course_code}})

> **Persistent brain between sessions.** Every orchestrator reads this on startup and **adds what's
> new** that helps future sessions: discovered conventions, tier calibration, traps, patterns that
> worked. **Only what is NOT already** in the sources of truth (see `.claude/refs/PROTOCOL.md` §4).
> Keep it concise and actionable.

---

## Fixed conventions (base — in force from harness start)

<!-- bootstrap: fill these from the interview + course.yaml. Keep only the ones that apply; write
     the real values (language, session rhythm/shapes, exercise rules, tool stack, project spine,
     publishing conventions). Mirror the ET shared-context density. Examples of rows to include: -->
- **Language:** {{language_line}} Audience: {{audience}} — write for that level (define terms; the
  glossary is the shared vocabulary).
- **Session rhythm ({{session_length}}):** {{session_shapes_oneline}} Blocks in multiples of 5 min;
  {{break_and_sacred_block_rule}}.
- **md-first + skill owns its pipeline:** every `.md` is validated before publishing, and the
  **same orchestrator** that produced it publishes/materializes it (Google Docs{{publish_targets_inline}})
  in the same run, after the human gate. **No separate batch publication.**
- **Placeholders when hard info is missing:** if a fact isn't in a source of truth, leave an
  explicit `[placeholder]` + a note to the conductor. **Never invent.**
- **Don't re-upload synced files:** local files (`.md`, `.xlsx`, `.json`, images) already reach
  Drive via folder sync. Use the Drive MCP **only** to create Google Docs/Sheets or to read/verify.
<!-- bootstrap: add course-specific fixed conventions surfaced in the interview (exercise
     convention, examples-pack rule, recap rule, project spine, provisional couplings, etc.). -->

## Tier calibration (adjusts with experience)

<!-- bootstrap: seed with the default rows below; DELETE rows for skills not in artifacts.enabled.
     "Evidence / notes" starts empty ("—") for a fresh course. -->

| Skill | Current tier | Evidence / notes |
|---|---|---|
| Session planning | Opus | — |
| Examples (instructor pack) | Sonnet author · Opus orch+judge | — |
| Slides (spec) | Sonnet + Opus header | — |
| Slides (local HTML build) | Sonnet (HTML) + Opus (extract/index/QA) | — |
| Class exercises | Sonnet · Opus judge | — |
| Readings | Sonnet | — |
| Homework / Tarea | Opus orch · Sonnet draft · Haiku/Bash rubric | — |
| Miro boards | Opus decide+judge · Sonnet build-spec · Haiku/Bash `estampar.py` | — |
| Lab | Sonnet (↑Opus if tool complex) · Haiku/Bash rubric | — |
| Exam (MCQ) | Sonnet + Haiku (format) | — |
| Practical exam | Sonnet → Opus (calibration) | — |
| Project delivery | Opus orch · Sonnet draft · Haiku/Bash rubric | — |
| Presentation guide | Sonnet → Opus · Haiku/Bash rubric | — |
| Publish Google Doc | **Haiku (mandatory)** · lead verifies only | — |

> If a cheap agent underperforms on a skill, note it here with the example and bump the tier.
> **Publish is a mandatory Haiku delegation** (§6): the lead never makes `create_file` calls itself.

## Per-session lessons

*(Orchestrators add entries here as they produce. Format: `S<NN> · <artifact> · lesson`.)*

<!-- bootstrap: leave this section EMPTY (just the note above) for a fresh course. -->

## Verified Drive IDs

<!-- bootstrap: seed with the course_folder_id from course.yaml if known, else a placeholder row;
     orchestrators append per-type subfolder IDs as they first publish into them. -->
- **Course root** = `{{course_folder_id_or_placeholder}}`
- **`{{sources_folder}}/`** = `[resolve on first publish]` — publish course-level Docs here.
- **Per-type deliverable subfolders** (`{{deliverable_folders}}`): resolve each folder's ID with
  `search_files` (`title = '<name>' and parentId = '<root>'`) the first time you publish into it,
  and record the ID here.

## Open technical items (verify on first use)

- **Google Docs via Drive MCP (re-verify on first publish):** the connector creates/copies files
  but **does not expose the Google Docs API** (`batchUpdate`). So programmatically you **cannot**
  apply Title/Subtitle styles, header/footer, page breaks, or insert images by anchor.
  `publish-google-doc` automates what it can (title/subtitle as normal text + a header shift
  computed from the source's actual heading structure — not a blind `##`→`#`) and **always raises a
  reminder** to the conductor with the manual steps. Method: `Google_Drive.create_file` with
  `contentMimeType: text/markdown` → converts headers, bold, and **tables to native tables**;
  links/emails become clickable.
<!-- bootstrap: INCLUDE-IF recap-signup enabled. -->
- **Google Sheets via Drive MCP (re-verify):** `Google_Drive.create_file` with `textContent` = CSV
  + `contentMimeType: text/csv` (default conversion) → produces a real Sheet. `fileSize:"1"` is a
  native-file metadata quirk, not an error.
- **Emoji in Docs (inherited trap):** the Drive Markdown→Doc converter has mangled traffic-light
  emoji (🔴🟡🟢) in the past. If publishing a `.md` with such emoji, consider substituting the
  color word — and **tell the conductor**. Re-check on first publish.
- **Slides build is LOCAL-ONLY:** no external sync/hosting. Each slide's HTML is authored from the
  slide-spec into `{{slides_folder}}/S<NN>-build/` (self-contained files + navigable `index.html`
  from `file://`). After HTML approval, a **shareable, notes-free PDF** per deck is exported into
  `{{slides_folder}}/` with `export-slides-pdf.sh` — PNG-rasterized (vector `--print-to-pdf` shows
  gray shadow rectangles in Quartz viewers), spot-check with `sips`. **Prerequisite:** a per-session
  `.pptx` at `{{slides_folder}}/S<NN>-template.pptx`; if missing, the Slides agent **alerts the
  conductor** and leaves the `.md` ready.
<!-- bootstrap: INCLUDE-IF miro-boards enabled. -->
- **Miro REST API v2 (re-verify on first board):** boards are built via `curl`/`estampar.py` with
  the token from `$MIRO_TOKEN` (**env var only, never in a file**); the Miro MCP is read/verify
  only. `copy_from`/`clone` creates **empty** boards → clone to sections by re-`build` per section.
  The conductor manually moves each board to its Space (the API doesn't place it).
- **Rubric plugin:** rubrics use the plugin `evaluation-rubrics:rubric-creator` (`generate_rubric.py`,
  produces xlsx+json). Locate the script scoped to `~/.claude*/plugins` (never `find /`). It accepts a
  `penalties` field (standard block from `.claude/refs/grading-penalties.md`) rendered outside the
  additive 100. `openpyxl` required.
