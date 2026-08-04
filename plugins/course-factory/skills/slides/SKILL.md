---
name: slides
description: Produces a course session's slide specification (slides/S<NN>-slides-spec.md) and then builds it as a fully LOCAL HTML deck in slides/S<NN>-build/ (self-contained files + navigable index.html/presenter.html — no external sync or hosting), plus a shareable PDF export. Part of the course-factory harness pipeline for building university course material; it is the LAST artifact of a session's production sequence. Invoke DELIBERATELY within that pipeline (the working folder has .claude/refs/course.yaml); do NOT auto-trigger for generic slide or presentation requests.
---

# Slides (slide-spec → local HTML build)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor folder
> containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder names, enabled
> artifacts, tool stack, publishing targets); (3) read `.claude/refs/PROTOCOL.md` — the course's
> contract, including its slide conventions; (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md`; (5) read `.claude/refs/shared-context.md`. If
> `slides` is not in `artifacts.enabled`, STOP and warn the conductor. Write ALL generated content
> in `course.language`.

**Tier — two phases (Opus coordinates both):**
- **Phase 1 · Slide-spec:** **Sonnet** authors the slide content + note bodies (NO header) ·
  **Opus** stamps the mechanical speaker-note header (block marker + time range + `k/K` **within
  that time window** — see §Slide conventions) directly when assembling the `.md` — it is 100%
  derivable from the outline Opus already built from the plan, so no separate agent is needed.
- **Phase 2 · Build:** **Opus** runs the mechanical/deterministic steps directly via Bash (extract
  the style from the `.pptx`, assemble `index.html`/`presenter.html`) · **Sonnet** authors each
  slide's HTML (the expensive part — one agent per deck, or one per section if the course produces
  multiple parallel decks) reading the `.md` from disk.

*(Opus never hand-authors slide HTML — that always goes to Sonnet. Opus does run the `.pptx`
extraction and the viewer assembly itself, because they are mechanical and cheap.)*

## What you produce

- `<folders.slides>/S<NN>-slides-spec.md` — a **slide-spec** clean and complete enough that the
  Build phase can author each slide's HTML **without re-thinking content or layout**. One entry
  per slide. Because Slides are authored **last**, the deck is the **visual guide of the whole
  session**, in **timeline order**: a title slide on the sacred join/setup slot → opening/agenda →
  each teaching block (with its demo/example highlights, when `examples` is enabled) → a single
  exercise-launch slide per exercise (when `class-exercises` is enabled) → wrap-up (previewing any due
  delivery). A student-led recap that opens a session, if the course has one, is NOT authored here.
- The **built deck**, fully local: `<folders.slides>/S<NN>-build/` (one build folder per session,
  with one subfolder per deck if the course produces more than one per session — e.g. an
  intro-and-logistics deck plus a content deck) with one self-contained HTML file per slide + a
  navigable `index.html` and `presenter.html`. Nothing is synced or hosted externally.
- A **shareable PDF** per deck, generated after the HTML is approved (see §Export to PDF).

## Inputs (read, don't duplicate)

- `planning/S<NN>-plan.md` → the **teaching-block breakdown** (sub-blocks · minutes · points, and
  the timeline for the note time ranges). This is your source outline — do not re-derive it.
- `<folders.examples>/S<NN>/` (only if `examples` is enabled) → the instructor demo & examples pack
  built from the plan's Examples manifest. Where the manifest marks an item as **slides-
  referenced**, keep the slide **light** and let the speaker note point to the pack (e.g. `Demo:
  see pack B1`) instead of re-authoring what the pack already owns. The pack is instructor-only —
  don't copy its bulk onto slides.
- `<folders.exercises>/S<NN>-ex*.md` (only if `class-exercises` is enabled) → the finalized
  exercise guides. Build **exactly ONE condensed exercise-launch slide per exercise**,
  placed right after the block that enables it (per the plan's timeline): the one-line objective,
  what the student does, what to submit, the time box, and the submission-mechanism pointer
  (per `publishing.portal` or the Miro-variant equivalent). **This single slide MAY exceed the ≤6×6
  guideline** — condense as much as possible, but keep it to one slide, not a group. The full numbered
  steps live in the guide; the slide launches and frames the exercise. Its note header is
  `Exercise <N.x> · <hh:mm–hh:mm> · 1/1`.
- The current delivery/project brief, if the course tracks project deliveries and one is due this
  session, so the **wrap-up** slide previews it accurately. Reference it; don't reproduce it.
- `<folders.sources>/<sources.glossary>` → consistent, non-technical terms.
- `<folders.slides>/S<NN>-template.pptx` (or per-deck template, if the session produces more than
  one) → the conductor's reference `.pptx`. **BLOCKING prerequisite for the build** — see §Build.
  The spec `.md` can be produced without it; the design cannot.

## Slide conventions

- **Light slides:** something visual, guideline ≤6 lines / ≤6 words per line (not a hard rule).
- **"Long block" = several light slides.** Prefer many small, low-content slides over few dense
  ones.
- **Opening title slide on the sacred join/setup slot:** the deck **always opens with a title/cover
  slide** placed on the session's first (sacred) window — the empty Zoom-join block for a virtual
  session (e.g. 6:00–6:05), or the setup block otherwise — so something identifies the session on
  screen while students connect. **Title only — no agenda, no teaching content** (the sacred slot
  stays empty of *content*; a bare session title is not content). Note header
  `<join-block label> (sacred) · <hh:mm–hh:mm> · 1/1`. The agenda lives in its own opening/agenda
  window, after any student-led recap.
- **Break slides show the DURATION only, never a resume clock time:** on-screen content is the break
  length ("Break · 15 minutes"), **not** an absolute resume time ("Back at 8:20") — the class drifts
  and a printed clock time goes stale. The instructor reads the real resume time off the presenter
  clock; the note-header time range stays as the planning aid.
- **Each exercise launch = ONE condensed slide** (not a group) — see §Inputs.
- The spec follows the **plan's timeline**: title (sacred slot) → opening/agenda → each teaching
  block, split into its sub-blocks, each followed by a single exercise-launch slide where the plan
  places one → wrap-up.
- **Speaker note — per-slide format:** a **header** built by Opus + a **body** built by Sonnet.

```
### Slide <n> — <short title>
Content (what's on screen, ≤6 lines):
  • …
Visual: <suggested image/diagram>
Speaker note:
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Block <label> · <time-range(s)> · <k>/<K>
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Key points:
  • …  • …
  Example: …
  🔴 DEMO: run pack <label> here (~<m> min)   ← only on a demo slide / a slide that carries a live demo
  😄  (only if it fits — cap per session per the course's humor budget, if it defines one)
```

When `schedule.sections` is non-empty (dual-schedule courses), the time-range line carries one
start–end pair **per section**, each derived from that section's start time in the plan's timeline
(e.g. `Ⓐ <hh:mm–hh:mm> · Ⓑ <hh:mm–hh:mm>`), instead of a single range.

**⚠️ The counter is scoped to the TIME WINDOW, not the teaching block.** A **timing block** is a run
of consecutive slides that share the **exact same time range** (all sections' ranges move together,
so it's enough to anchor on one). Within it:

- every slide carries the **identical time range(s)**, and
- the counter `k/K` runs `1/K … K/K`, where **K = the number of slides in that time window** — so
  the teacher always knows *how many slides remain before this window ends* (a fixed target, not a
  moving one).

**The moment the time range changes, a new timing block begins:** the counter **resets to `1/K′`**
and the teaching-block marker simply carries over. **Never let the time range drift between two
slides that share a counter** — that is the moving-target bug (`1/11 @ 6:00–6:05`,
`2/11 @ 6:05–6:15`, …: one climbing counter over shifting times, so the target was never fixed).

```
Block A · 6:05–6:15 · 1/3
Block A · 6:05–6:15 · 2/3
Block A · 6:05–6:15 · 3/3      ← teacher knows: 3 slides to land in this 10-min window
Block A · 6:15–6:25 · 1/4      ← time changed → new timing block, counter resets to 1
```

Not this (the moving-target bug):
```
Block A · 6:00–6:05 · 1/11
Block A · 6:05–6:15 · 2/11     ← WRONG: time drifted while the counter kept climbing
```

The plan's timeline gives the windows: each sub-block's minute span is one time range → one timing
block. **Standalone slides (agenda, wrap-up) each get their own window** (`1/1` unless the plan
groups several under one span). A **dedicated demo slide** or a `🔴 DEMO`-extended range is just
another window — the demo minutes sit inside a shared time range, so its slides count within it
like any other block.

**Work split:**
- **Sonnet** builds the body (visible content + key points + one example), **without** the block/
  time header. Give it the full outline (slide count, title, block, time range, what each covers)
  so it never re-derives structure. Assign humor slots yourself (Opus) so any per-session cap
  holds, especially if 2+ decks are delegated to parallel Sonnet agents that can't see each other's
  choices.
- **Opus** stamps the header: teaching-block marker + **time range(s)** + `k/K` **within that time
  window** (from the plan's timeline). Group slides by their time range first, then number
  `1/K … K/K` inside each range; reset the counter whenever the range changes.

## Live demos in the deck (from the Examples manifest — only when `examples` is enabled)

Demos consume class minutes — the deck must **show that time, not hide it**. For each **live-demo**
item in the plan's Examples manifest, do **one** of these, at the point the demo runs:

- **(a) A dedicated demo slide** — a light slide with its own speaker-note header + time range,
  just like any other slide. If the demo has its own distinct time span it is its own timing block
  (`1/1` or more); if it shares a window with the concept slides around it, it counts inside that
  window. Use when the demo is a distinct beat.
- **(b) A `🔴 DEMO` note on a concept slide** — keep the concept slide and add to its speaker notes
  a `🔴 DEMO: run pack <label> here (~<m> min)` line, **extending that slide's/its block's time
  range** to cover the demo. Use when the demo is woven into a concept slide.

Either way the demo minutes are **explicit in the note time ranges**, and the block still sums to
its planned duration (demos are *part of* the block, not extra). Reference the demo — don't
re-author its content on the slide; it lives in the examples pack.

**⚠️ The exact pack reference is presenter-only — never on the visible slide.** The examples pack is
instructor-only (never published), so a pack label means nothing to students and leaks internal
material. The slide's **visible content may carry a demo/example MARKER** (a `LIVE DEMO` /
`WORKED EXAMPLE` badge) but **must not print the pack label in any form** — no on-screen `run pack
<label>`, no `→ pack <label>`. This covers **every** label format the pack uses (`B1`, `03`,
`02-carga-diferida`), not just numeric ones. The `🔴 DEMO: run pack <label> here (~<m> min)` line and
any `Worked example: pack <label>` reference live **only in the speaker notes**. This applies to the
Build phase too: do not render a "run pack"/"pack `<label>`" chip in the slide HTML.

## Process

1. From `planning/S<NN>-plan.md`, build the **outline** in **timeline order**: opening/agenda → one
   slide group per sub-block of each teaching block → an exercise-launch slide where the plan
   places one → wrap-up (with any due-delivery preview). Split each "long" sub-block into several
   light slides. Draw launch slides from the finalized exercise guides (objective · what to submit
   · time box · submission-mechanism pointer).
2. Delegate the **body authoring to Sonnet** (one agent per deck — parallel agents if the session
   produces more than one deck), passing the outline. Write for the course's actual audience —
   plain language, concrete examples, terms defined per the glossary, no unexplained jargon.
3. **Opus** stamps each slide's header and assembles `<folders.slides>/S<NN>-slides-spec.md`.
   Self-audit.
4. **Human gate:** the conductor validates the spec. Do not build until the green light **and**
   the `.pptx` is in place.
5. **Build** the local HTML deck (§Build).

## Build (local HTML — final step of this same skill)

The deck is built as **local HTML only** — no design tool sync, no external hosting of any kind.
The build is this skill's final step, after the conductor's validation, and everything it produces
stays on disk in the agreed folders.

**BLOCKING prerequisite — if it fails, do NOT invent a style: produce the `.md` and ALERT the
conductor, leave the deck unbuilt.**
- `<folders.slides>/S<NN>-template.pptx` present (colors, fonts, backgrounds, layouts — **per
  session**, may change; per deck if the session produces more than one).

**Build folder (fixed convention):** all HTML/assets/fonts go in
`<folders.slides>/S<NN>-build/` — **with the session number**, never a generic `build/`. One
self-contained HTML file per slide (`slide-01.html`, `slide-02.html`, …) plus `index.html`,
`presenter.html`, and a `fonts/`/`assets/` subfolder if needed. A subfolder per deck
(`S<NN>-build/S<NN>-01/`, `.../S<NN>-02/`) when the session produces more than one.

1. **Extract the style** *(Opus, direct via Bash — mechanical)*: `unzip -o
   <folders.slides>/S<NN>-template.pptx -d tmp/`, then pull from the raw XML:
   - **Colors:** `<a:clrScheme>` in `ppt/theme/theme1.xml` (dk1/lt1/dk2/lt2/accent1-6).
   - **Real background:** usually in `ppt/slideMasters/slideMaster1.xml` (`<p:bg>`), not the slide/
     layout — walk the inheritance chain up to the master before assuming there's none.
   - **Real fonts (⚠️ don't trust the theme `fontScheme`):** count actual usage —
     `grep -roE 'typeface="[^"]+"' ppt/slides ppt/slideLayouts ppt/slideMasters | sort | uniq -c | sort -rn`
     — the top 2–4 are the real ones. If they're Google Fonts (common in templates made in design
     tools), download the `latin` `.woff2` subset into the build's `fonts/`; **never link the
     Google Fonts CDN** — each slide must stay self-contained. (python-pptx is an alternative to
     unzip+XML.)
2. **Build HTML templates** *(Sonnet, inside the same agent as step 3)* from those tokens (title,
   content, section divider…).
3. **Author each slide's HTML** *(Sonnet — one agent per deck, parallel if 2+ decks)*: give the
   agent the `.md` path so it **reads the content itself** (keep the expensive tokens off Opus's
   context), writing straight into `<folders.slides>/S<NN>-build/[<deck>/]`. Each file:
   self-contained (inline CSS, no CDNs, no third-party JS — must render from a `file://` open with
   no network), fixed 1280×720 canvas, speaker note hidden (`<div class="speaker-notes"
   style="display:none">…`, full text incl. the block/time header). Inject `@font-face` + per-tag
   rules (`h1,h2,h3{…}` / `body,p,li,div,span{…}`) so fonts apply regardless of class names.
4. **Add `index.html` + `presenter.html`** *(Opus, direct — generated by the reusable script)*: the
   build folder is loose HTML files, so without a viewer the conductor only sees scattered slides —
   and in class they present with speaker notes. **Run:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/slides/scripts/build-presenter.py" <build-dir> <label> "<title>"
   ```
   e.g. `python3 "${CLAUDE_PLUGIN_ROOT}/skills/slides/scripts/build-presenter.py" slides/S01-build S01 "S01 — …"`
   (`<build-dir>` is the deck's own folder — `S<NN>-build/` itself, or `S<NN>-build/<deck>/` when
   there's more than one; `<label>` should be unique per deck so two open decks' presenter popups
   don't collide; `<title>` is optional, defaults to `<label>`). This writes both files with every
   known gotcha baked in. **Re-run it whenever any slide's speaker notes change** — the presenter's
   notes are extracted at build time into a static JS array. What the generated pair guarantees
   (don't hand-reinvent it; fix the script if something's off):
   - **`index.html`** (audience/projector view): prev/next buttons, keyboard arrows (← → plus
     Space/PageUp/PageDown, Home/End, F for fullscreen), an `N/total` counter, a fullscreen button,
     and a **presenter-view** button. Works opened directly from disk (`file://`, relative paths
     only).
     - The slide `<iframe>` carries `pointer-events:none` (a stray click steals keyboard focus and
       breaks arrow nav).
     - **Fullscreen hides the bottom bar** (a class toggled on `fullscreenchange`; the stage
       rescale stops subtracting the bar height when hidden).
     - Clicking **presenter view opens the popup AND auto-triggers fullscreen** — the presenter
       can't forget and leave the bar visible to the room.
   - **`presenter.html`** (presenter-only window): current slide large, next-slide thumbnail,
     speaker notes, **real system clock** (`HH:MM:SS`, not an elapsed timer — compares directly
     against the time ranges in the note headers), prev/next buttons + arrow keys (same
     `pointer-events:none` fix on its iframes).
     - **⚠️ `file://` origin gotcha (Safari and potentially others):** every `file://` document can
       be a **distinct origin**. So (a) never read the opener's variables/DOM — all index↔presenter
       sync goes through **`postMessage`**; (b) never read notes via `iframe.contentDocument` —
       they are **baked into `presenter.html` as a static `NOTES` array** extracted from each
       slide's hidden `speaker-notes` div at build time.
     - The presenter's current-slide iframe needs **`flex:0 0 auto`** — as a flex child its 1280px
       width otherwise gets flex-shrunk, clipping the slide's right side before the transform scale
       applies.
     - The popup window name is **unique per deck** so two open decks don't collide.
   - **Test in a real browser before closing** — don't assume it renders: open `index.html`, click
     the presenter-view button, and confirm the popup shows notes from the first render (not stuck
     "syncing…" — the origin gotcha's symptom), that arrows/buttons navigate **both** windows, and
     that fullscreen hides the bar.

**Opus** orchestrates these sub-phases: runs the mechanical steps (1, 4) directly via Bash,
delegates step 3 (HTML authoring, the expensive part) to Sonnet, and **judges** the final result
(fidelity to the template, readability, correct fonts).

## Export to PDF (final step, after the conductor approves the HTML)

Once the conductor **approves the HTML** (not before), generate the **shareable PDF** of each deck
(project without the viewer, send to students, offline backup). It is a mechanical, deterministic
render → **Opus runs it directly via Bash**, no delegation.

**No speaker notes — free by construction:** notes live in each slide as a hidden `display:none`
div, so the rasterized PDF comes out clean without filtering anything.

**Reusable script:**
```
bash "${CLAUDE_PLUGIN_ROOT}/skills/slides/scripts/export-slides-pdf.sh" <deck-dir> <pdf-path> [scale]
```
It **rasterizes each slide to PNG** with headless Chrome (`--screenshot`, 2× by default) and
**assembles the PNGs into the PDF with Pillow**. Chrome and Python+Pillow must be present on the
conductor's machine. Run **once per deck**.

**⚠️ Why PNG and not vector PDF:** with `--print-to-pdf` (vector), Chrome encodes
`box-shadow`/`filter` as **transparency masks** that **Quartz** viewers (Apple Preview, Quick Look,
the Google Drive preview) paint as **gray rectangles** behind circles and cards — even though
poppler draws them fine. Rasterizing flattens everything → **any viewer shows exactly what was
approved**. Cost: no selectable text, heavier file (~2.5 MB) — irrelevant for slides that are
projected/shared.

**Naming convention — the PDF goes DIRECTLY in `<folders.slides>/`:**
- **Single deck (the normal case):** `S<NN> - <Session name>.pdf`
- **2+ decks in one session:** `S<NN> - <index> - <Deck name>.pdf`

Example:
```bash
SH="${CLAUDE_PLUGIN_ROOT}/skills/slides/scripts/export-slides-pdf.sh"
bash "$SH" slides/S02-build "slides/S02 - From Idea to Spec.pdf"
```

**Gotchas already solved inside the script (listed here only for diagnosis):** renders **in-place**
with the `file://` path **percent-encoded** (spaces → %20) — Chrome hangs on unencoded spaces, and
copying to a temp dir would break assets referenced outside the deck folder; iterates over the
**glob array**, never `for f in $(ls …)` (a space anywhere in the path causes word-splitting →
Chrome renders `ERR_INVALID_URL` error pages that file size alone won't catch); does **not** use
`--user-data-dir` (it hung Chrome).

**Mandatory verification:** after generating, render 1–2 pages with **`sips`** (the Quartz engine)
and look at them — it is the only renderer that exposes both the shadow rectangles and the error
pages:
```bash
pdfseparate -f 4 -l 4 "slides/S<NN> - ….pdf" /tmp/p.pdf
sips -s format png /tmp/p.pdf --out /tmp/p.png    # open /tmp/p.png and confirm it looks clean
```

## Acceptance criteria

- [ ] Each slide: ≤6 lines / ≤6 words per line, with a suggested visual. *(Exception: an
      exercise-launch slide may exceed 6×6 — condensed, one slide per exercise.)*
- [ ] The deck **opens with a title slide on the sacred join/setup slot** (title only — no agenda, no
      content); note header `<join-block> (sacred) · <hh:mm–hh:mm> · 1/1`.
- [ ] Break slides show the **duration only** ("Break · 15 minutes") — **no absolute resume clock
      time** on screen.
- [ ] **Exactly one** condensed exercise-launch slide per exercise (not a group), placed after the
      block that enables it; note header `Exercise <N.x> · <hh:mm–hh:mm> · 1/1`.
- [ ] **No examples-pack label, in any format, on any visible slide** (no `run pack <label>`, no
      `→ pack <label>`) — only a `LIVE DEMO` / `WORKED EXAMPLE` marker; the pack reference stays in
      the speaker notes.
- [ ] Speaker notes carry the correct header: teaching-block marker + time range(s) + `k/K`
      **scoped to the time window**. Slides that share a time range share the identical range and
      are counted `1/K … K/K`; the counter resets the moment the range changes (no moving target).
- [ ] Times coherent with `S<NN>-plan.md` (block ranges add up); dual-schedule sections (if any)
      stay in lockstep.
- [ ] Every **live-demo** in the plan's Examples manifest (when `examples` is enabled) is reflected
      in the deck — either a dedicated demo slide with its own time range, or a `🔴 DEMO … (~m
      min)` note on a concept slide — with the demo minutes **included** in the time ranges and the
      block still summing to its planned duration.
- [ ] Key points are brief (not paragraphs); humor kept within the course's per-session cap, if
      defined.
- [ ] Consistent language and terms; defined per the glossary.
- [ ] Slide-spec covers the **whole session** in timeline order: a title slide (sacred slot),
      opening/agenda, every teaching block, one exercise-launch slide per exercise (when
      `class-exercises` is enabled), and a wrap-up that previews any due delivery.
- [ ] Built deck: `<folders.slides>/S<NN>-build/` (session-numbered, never generic `build/`) with
      one self-contained HTML file per slide + `index.html` and `presenter.html` generated by
      `build-presenter.py`, everything working from `file://` with no network — verified in a real
      browser. **Nothing synced or hosted externally.**
- [ ] `index.html`: arrows navigate (tested after a click inside the stage, not only on load);
      fullscreen hides the bottom bar; the presenter-view button opens the popup AND
      auto-triggers fullscreen.
- [ ] `presenter.html`: notes visible from the first render (not stuck "syncing…" — the
      `file://`-origin symptom), next-slide thumbnail, real system clock, arrows/buttons navigate
      both windows, current slide fully visible (no right-edge clipping). Re-generated after any
      speaker-note change.
- [ ] If the `.pptx` is missing: `.md` produced, conductor alerted, **no invented style**.
- [ ] **Shareable PDF** generated after the conductor approves the HTML (one per deck), directly in
      `<folders.slides>/` with the naming convention, no speaker notes, same page count as slides,
      exact 16:9 pages — and spot-checked via `sips`.

## Close

1. Write `<folders.slides>/S<NN>-slides-spec.md` (per deck, if more than one) and self-audit.
2. **Human gate (md-first):** the conductor validates the spec. *(End the turn with a summary; do
   not build until the green light and the `.pptx` is in place.)*
3. **Build** the local HTML deck (§Build) — final step of this same skill.
4. **Human gate (HTML):** the conductor reviews the built deck (opens `index.html` locally). On
   approval, **export to PDF** (§Export to PDF) — one PDF per deck, directly in
   `<folders.slides>/` with the naming convention.
5. Update the handover and emit the closing block
   (`.claude/refs/templates/next-agent-prompt.md`): summary + **PROMPT FOR THE NEXT AGENT**. Next =
   **`session-planning`** for the next session — slides are the **last** artifact of this session.
