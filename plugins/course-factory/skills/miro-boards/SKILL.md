---
name: miro-boards
description: >
  Materializes a session's exercise boards in Miro (a grid of identical per-student canvases per
  exercise) in the course-factory material-production harness, via the Miro REST API driven by a
  Sonnet-authored build-spec JSON and the deterministic `estampar.py` stamper (the MCP is used
  only for read/verification). The "publication" step for class-exercises, analogous to
  publish-google-doc. GATED: only runs when `tool_stack.miro.enabled` is true in
  `course.yaml`. Invoke DELIBERATELY within a course material-production pipeline, after the
  class-exercises spec for a session is validated; do NOT auto-trigger for generic Miro
  board/template requests.
---

# Miro boards (exercise materialization)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` — in particular
> `tool_stack.miro`; **if `tool_stack.miro` is false or `miro-boards` is not in
> `artifacts.enabled`, STOP and warn the conductor** — this entire skill is config-gated; (3)
> read `.claude/refs/PROTOCOL.md` for the course's exercise/Miro conventions; (4) read your
> session handover `.claude/refs/handovers/handover-S<NN>.md`. This skill is the "publication"
> step for exercises: the `class-exercises` skill produces the spec `.md`; here it becomes Miro
> boards.

**Work split — Opus coordinates 4 layers (do NOT do it all yourself):**

| Layer | Who | Does |
|---|---|---|
| 1 · Strategy | **Opus (you)** | With the conductor: reuse a prior-year exercise / clone / build new; runs the **2 gates**. |
| 2 · Format | **Opus (you)** | Chooses the scaffolding **pattern** from the catalog (A/B/C/other) per exercise. |
| 3 · Stamp authoring | **Sonnet** (delegate) | Translates spec+pattern into a **build-spec JSON** (layout of ONE canvas: items, coords, colors, content) + board names. If the pattern needs something new, extends `estampar.py`. |
| 4 · Bulk execution | **Opus via Bash directly** (or Haiku) | Runs **`python estampar.py build <spec.json>`** → stamps every canvas via REST. **The script is deterministic** (it makes the ~N calls, not the model) → running it from Opus via Bash costs less than opening a Haiku agent; delegate to Haiku only to parallelize/offload context. Reports count/URL. |

**Opus (you) also JUDGES** the result (read with the MCP) and answers for quality. **The
conductor has 2 approval gates** (below). Everything fits in this one skill because you
orchestrate it.

## Gate: config

This skill only runs when `course.yaml tool_stack.miro.enabled` is `true`. If it is false or
absent, or `miro-boards` is not in `artifacts.enabled`, stop immediately and tell the conductor
this course has no Miro tool stack configured.

## What you produce

The **Miro boards** for a session's exercises. **One board = one exercise**; each board has a
**grid of per-student canvases** (identical by default, or one variant per grid column — see
**Two stamping modes**; frames titled per the course's convention, e.g. "ID
and Name") where each student claims one, renames it with their identifying info (= attendance
record), and works the exercise's scaffolding inside the frame.

- Board count per session and per exercise type is whatever the class-exercises spec for that
  session states (e.g. N boards for a normal session, fewer for the first session with no warm-up
  exercise, zero for a workshop-format session with no boards). Read it from the spec/handover,
  do not hardcode a specific count.

## How it's built: Miro REST API (MCP is read-only here)

Construction does **not** use the MCP (its write endpoint has proven unreliable for this and
does not duplicate boards well). Use the **Miro REST API v2** via script — more capable and
fully mechanical. **The MCP is used only to READ/verify** (`context_explore`, `context_get`) the
result.

**Reusable stamper — `estampar.py`** at
`"${CLAUDE_PLUGIN_ROOT}/skills/miro-boards/scripts/estampar.py"` (never contains the token; reads
it from `MIRO_TOKEN`). Read its module docstring for the exact CLI usage and the build-spec JSON
shape before invoking it — it documents `board`/`team_id`/`grid`/`items[]` (`shape` / `sticky` /
`text` / `connector`, child coordinates measured center-from-frame-top-left), the optional
`items_by_col[]` (see **Two stamping modes** below) and the three subcommands:
- `python estampar.py build <build-spec.json>` → creates the board, closes its sharing if it is a
  template (see below), and stamps the canvas grid.
  **Sonnet (layer 3) authors the `build-spec.json`.**
- `python estampar.py lock <boardId> [<boardId> …]` → closes an EXISTING board's sharing to the
  template policy. Idempotent; for retro-fixing boards created before this rule.
- `python estampar.py clone <boardId> "<new name>"` → **⚠️ NOT reliable** — `copy_from` creates
  the board but **EMPTY** (0 items). Do not use it. To clone template → sections, **re-run
  `build` with the same build-spec, changing only `board.name`**.

**Two stamping modes — pick one deliberately, in layer 2 with the rest of the pattern:**

1. **Every canvas identical** (default). Omit `items_by_col`. The `items` are stamped into all
   `cols`×`rows` frames. This is the normal case: one exercise, N students, N identical canvases.
2. **One variant per grid column.** Declare `items_by_col` with **exactly `grid.cols` entries**
   (a list of items per column, or `null` for a column that adds nothing). Every frame in column
   `c` gets `items` + `items_by_col[c]`, so **each column carries a different variant, repeated
   down its `rows`**. Use it when one exercise has N different seeded prompts — one per column,
   repeated down the rows to give several instances of each, so **each student does ONE variant**
   and neighbours in different columns cannot copy. Put the shared scaffolding (instruction band,
   work zones) in `items` and **only the seeded input** in `items_by_col`.
   - Connector aliases resolve over the frame's combined list, so a connector may join a common
     item to a variant item. **Aliases must therefore be unique across `items` + the column's
     entry:** a variant item reusing a common item's `alias` silently wins the lookup and any
     connector naming it binds to the wrong item. Prefix variant aliases (e.g. `v3_zona`).
   - The script **aborts before creating the board** if the entry count does not match
     `grid.cols` — a variant stamped into the wrong column is a silent failure that only shows up
     in class.
   - ⚠️ **Equal difficulty is the author's job, not the script's.** When students get different
     variants for the same grade, the variants must be comparable in length and difficulty, or
     the grade measures which column they sat in. Audit them against each other before stamping.
   - The **preview gate** (Gate 2, step 4b) for this mode is **one canvas per variant**
     (`cols = <variants>`, `rows = 1`), not a single 1×1 — the conductor has to see every
     variant, and a 1×1 preview that keeps `items_by_col` aborts the script.

Details for if Sonnet needs to **extend the script** with a new item kind:

**🔑 Token (secret — strict handling):** the API uses an access token for the course's Miro app
(`boards:write/read`, `team:write/read` scopes). **NEVER write it into any file inside the
course folder** (it syncs to Drive) — **the token comes ONLY from the `MIRO_TOKEN` environment
variable**, set by the conductor outside any synced folder. The skill reads it from
`os.environ`/`$MIRO_TOKEN`. If `MIRO_TOKEN` is unset or a call 401s, **stop and alert the
conductor** — do not proceed, do not prompt for the token, do not write it anywhere.
`team_id` (from `tool_stack.miro.team_id`) is plaintext-safe and may appear in config.

**Endpoints used** (base `https://api.miro.com`):
- Validate token: `GET /v1/oauth-token`.
- Create board: `POST /v2/boards` — body `{"name","description","teamId"}`. ⚠️ `name` ≤ 60
  characters (hence the compact naming convention below); the long descriptive name goes in
  `description` (no practical limit).
- Sharing policy: `GET /v2/boards/{id}` → `policy.sharingPolicy`; `PATCH /v2/boards/{id}` with
  `{"policy":{"sharingPolicy":{…}}}` to change it. ⚠️ **Send the whole `sharingPolicy` object**
  (read it, merge your field, send it back) — a partial patch is not reliable. See "Template
  boards are private" below; `estampar.py` does this for you.
- Duplicate board: `POST /v2/boards?copy_from={boardId}` — copies an entire board. This is the
  native path for cloning template → sections (validate on first real use; the script's `clone`
  subcommand is NOT this and is unreliable — see above).
- Frame: `POST /v2/boards/{id}/frames`.
- Shape/text: `POST /v2/boards/{id}/shapes`, with `"parent":{"id":<frameId>}` to nest in a frame.
- Sticky note: `POST /v2/boards/{id}/sticky_notes`.
- Connector: `POST /v2/boards/{id}/connectors`.
- Delete: `DELETE /v2/boards/{id}/{type}/{itemId}`.
- **Child coordinates**: `origin=center`, `relativeTo=parent_top_left` → `x,y` = center of the
  item measured from the frame's top-left corner.
- **Robustness**: the script retries on `429/500/502/503` (5 attempts). If an error persists
  (auth, a 400 validation error, an outage), **alert the conductor**.

## Naming convention (≤60 chars) — MANDATORY

A board is created loose (the API cannot place it into a Space) and the conductor moves it
later; so the **name carries a prefix identifying its destination Space**, to find and sort it
even while loose. Generalized pattern, driven entirely by `course.yaml tool_stack.miro`:

```
<board_prefix>-<space>-<session>-<exercise>-<Name>
```

- `<board_prefix>` = `tool_stack.miro.board_prefix` (e.g. a course/year code).
- `<space>` = one entry from `tool_stack.miro.spaces` (a short code per destination Space the
  conductor will move the board into — read the space↔code mapping from the conductor/handover,
  since the codes are course-specific).
- `<session>` = the session number, 2 digits.
- `<exercise>` = the exercise number within the session, 2 digits (e.g. `01` = warm-up/review
  exercise, `02`/`03` = working exercises — per the course's own exercise convention).
- `<Name>` = a short exercise name, trimmed so the whole string stays ≤60 chars; the full
  descriptive name goes in `description`.
- A template board and its section clones share `<session>-<exercise>-<Name>`; only `<space>`
  changes between them.

## Template boards are PRIVATE — MANDATORY

A **template** board (the one whose `<space>` is the course's template space, i.e.
`tool_stack.miro.template_space` in `course.yaml`) is **instructor material, not team material**.
The Miro API creates every board with the team already holding `edit`, so a template left alone
is silently readable and editable by the whole Miro team. **Close it at creation:**

- Target policy — `teamAccess: "private"`, `access: "private"`, `organizationAccess: "private"`.
  In the Miro UI that reads as the team row and *Anyone with the link* both on **"No access"**.
- The instructor and their invited collaborators keep access **through the Space**, which this
  policy does not touch. Do **not** remove board members to achieve it.
- **How:** every build-spec MUST carry `"template_space"` (copied from
  `course.yaml tool_stack.miro.template_space`). `estampar.py build` then compares it against the
  `<space>` segment of `board.name`, applies the policy right after creating the board (before
  stamping, so a mid-run failure never leaves an open template), reads it back, and **aborts** if
  it did not stick. It prints a `SHARING …` line — that line is the evidence for the audit. It also
  **aborts** when `template_space` is set but `board.name` does not parse into a `<space>`
  (otherwise the board would be created open with nothing to show for it), and prints
  `SHARING (no es plantilla) …` for every board it decides is *not* a template, so the sharing
  decision is always visible in the log, board by board.
  Without `template_space` the script prints a warning and leaves the default (team has access).
- **Retro-fix / existing boards:** `python estampar.py lock <boardId> [<boardId> …]` — idempotent.
- **Section clones (student boards) are NOT touched** by this rule; they keep the course's normal
  access so students can reach them.

## Canvas geometry

The **pattern** is fixed; the **frame size is NOT** — it depends on the exercise.

- Grid dimensions (rows × columns, and total canvas count) come from the exercise spec / the
  conductor — size it to the actual enrollment.
- Frame size follows the scaffolding (dimension it to fit with margin) — different patterns
  (a table pattern vs. a mind-map pattern vs. a blank pasted-screenshot pattern) want different
  sizes.
- Grid step derives from frame size: `step_x = frame_w + ~100`, `step_y = frame_h + ~130`. Frame
  center `(c,f)`: `x = c·step_x`, `y = f·step_y`. All frames in a board share the same size for a
  clean grid.

## Scaffolding pattern catalog (Opus chooses per exercise — open to more)

Common rule across all patterns: the scaffolding **fills the frame**, the **instructions sit
top-left** (out of the way), and there are **clear empty zones for the student to work in**
(sticky notes, nodes, frames). The frame size adapts to the pattern. These three are proven;
**Opus may propose others** (timeline, 2×2 matrix, column table, ranking, empathy map, etc.).

### The consigna repeats INSIDE each work zone — MANDATORY

The instructions band top-left is **not the only place the consigna lives**. **Every work zone
carries its own title + a short instruction directly under it**, so the student works looking at
the box where they write, not scrolling back to re-read the canvas header:

- Each zone's `content` is a **bold title, then one or two sentences** stating what goes in that
  zone. Never a title alone (a `text`/`shape` item whose `content` is just the zone's name, with
  the actual instruction living only in the top-left band, fails this rule).
- The zone's instruction text sits **one size below the zone title** (e.g. title at 24pt, the
  instruction at 20pt; or both at 20pt with the title in bold) — visually subordinate, but present.
- The top-left instructions band stays **fully self-contained** (it still carries the complete
  consigna, unabridged) — what changes is that it stops being the *only* place carrying it.
- This applies to every catalog pattern (colored cells in A, branch/child nodes in B, capture
  frames in C) and to any pattern Opus proposes.
- **Sonnet (layer 3)** authors this per zone when writing the build-spec; **Opus (layer 2)**
  checks it when judging the preview (Gate 2) before the bulk run.

### Per-column variants: the question must be concretized per variant — MANDATORY

When an exercise uses **per-column variants** (`items_by_col`, see **Two stamping modes**), the
scaffolding cannot leave open a variable the case doesn't fix. Concretely:

- If the exercise's question depends on a quantity/dimension that changes by variant (e.g. "if
  the business doubled" without saying doubled **in what** — headcount? messages? customers? —
  and each seeded variant implies a different one), **the question must name that dimension
  explicitly, per variant**, not once in the shared instructions band.
- That concretized question travels in the **same read-only element as the seeded case** (so it
  is part of `items_by_col`, not `items` — each variant's case and its fully-specified question
  are one inseparable unit).
- **All variants' questions end in the same words** — vary only the part that must vary (the
  dimension/quantity), never the phrasing around it, so no column is easier to read or parse than
  another.

### "A business you know" prompts must define what counts — MANDATORY

Any exercise that asks the student to use "a business you know" (or equivalent — not all students
work) must state, on the canvas itself, both of the following:

- **What counts:** where you work today, your family's business, somewhere you worked before, or
  one you know closely as a regular customer.
- **What may be assumed:** anything not known with certainty may be assumed — the only thing that
  does not count is inventing a business that does not exist.

This text lives in the same read-only element as the rest of the case/instructions for that zone
(top-level instructions band, or the per-variant element in `items_by_col` when the exercise has
variants) — never left implicit or assumed obvious.

**A · Table / colored zones + sticky notes** *(analyze, classify, answer defined fields)*
- Frame divided into colored cells (one per question/field) covering it; instruction text
  top-left (light text on color); empty sticky notes (1–2 per zone) to answer in. REST: `shapes`
  (cells) + `sticky_notes`, all with `parent.id`=frame.

**B · Mind map** *(brainstorming, decomposing a concept into branches)*
- A central node with the concept (pill/rounded rectangle, colored border) + branches with EMPTY
  child nodes for the student to fill. REST: nodes = `shapes` `round_rectangle` + `connectors`
  joining central→branches→children. Instructions top-left of the frame. Frame large and square
  (more breathing room than pattern A).

**C · Screenshots / work in an external tool** *(any tool outside Miro)*
- 1–2 empty frames (bordered rectangles, white background) where the student pastes their
  screenshot from the external tool, with a label below stating what goes in each. REST: `shapes`
  (frames) + `shapes`/text for labels. Frame landscape-oriented.

> Detailed instructions for the exercise live on the exercise's slide/spec; the board carries
> only the minimal scaffolding to work in. Choose the pattern per what the exercise spec asks
> for.

## Two conductor gates (harness rule — respect them)

- **Gate 1 · Reuse-vs-build:** reusing a prior-year exercise vs. building a new one is decided by
  **the conductor with the Opus orchestrator**, *before* invoking this skill (it arrives decided
  in the spec/handover). This skill **executes**; it does not choose on its own.
- **Gate 2 · DESIGN approval (preview), BEFORE the bulk run:** the conductor's visual gate is
  **one canvas per variant**, never the full board — grid **1×1** in the identical mode, and
  **`cols = <variants>`, `rows = 1`** when the board uses `items_by_col` (the conductor has to
  see every variant, and a 1×1 preview aborts the script in that mode). Stamp that single row as
  a preview, the conductor reviews/adjusts it in the Miro UI, iterate on THAT ONE row (each
  iteration costs a handful of calls, not hundreds), and **only after their approval** stamp the
  full grid and clone to sections. Rename the preview `…(PREVIEW <n> canvas)` and **delete it**
  on approval. **Never stamp the full grid or clone to sections without preview approval.**

## The one thing that stays manual: Spaces

The API cannot reliably place a board inside a Space → **moving each board to its Space is done
by the conductor** in the UI (hence the naming prefix). (Duplicating boards IS solved by the API
via `copy_from`, unlike the write path through the MCP.)

## Inputs

- The session's validated exercise spec (produced by `class-exercises`) — instructions + the
  canvas layout for each exercise.
- From the handover/conductor: the reuse-vs-build decision (Gate 1) and the canvas count
  (default per the course's convention).
- Environment: `MIRO_TOKEN` available (never in repo files).

## Process

0. **Verify the token:** `GET /v1/oauth-token`. If missing/401 → alert the conductor and stop.
1. **Confirm Gate 1** (reuse-vs-build) from the handover/spec.
2. **If REUSE:** locate the prior-year board with the MCP `board_search_boards` (query = the
   exercise name); review it with `context_explore`/`layout_read`. Bring the scaffolding to this
   year's template (re-stamp, or the conductor Duplicates it).
3. **Choose the PATTERN and the stamping MODE** (layer 2, Opus) per exercise: the pattern from
   the catalog, per what the spec asks for; and the mode — every canvas identical, or **one
   variant per grid column** (`items_by_col`, see **Two stamping modes**). Both are decided
   here, by Opus, not by Sonnet while authoring.
4. **Build the build-spec and PREVIEW one canvas per variant:**
   a. **Layer 3 — Sonnet:** authors the `build-spec.json` (board `{name, description}`, `team_id`,
      **`template_space`**, `grid`, `items[]` of the chosen pattern with coords/colors/content;
      **plus `items_by_col[]` with exactly `grid.cols` entries when layer 2 chose the per-column
      variant mode** — only the seeded input goes there, the shared scaffolding stays in
      `items`). Save it in scratchpad.
      (Fine coordinate edits after conductor feedback can be Opus directly — mechanical editing.)
   b. **Preview one row (layer 4):** copy the spec with `name:"…(PREVIEW <n> canvas)"` and the
      grid cut to a single row — `grid.cols=1,rows=1` in the identical mode, or
      `grid.cols=<variants>,rows=1` **keeping every `items_by_col` entry** in variant mode
      (cutting `cols` to 1 there aborts the script, by design) — and run
      `python "${CLAUDE_PLUGIN_ROOT}/skills/miro-boards/scripts/estampar.py" build <preview.json>`.
      Opus runs the script via Bash directly (deterministic, cheaper than opening a Haiku agent
      — see the work-split table). Report the URL.
   c. **⛔ Gate 2 — the conductor validates the DESIGN in the UI** (colors, text, sizes, zones;
      in variant mode **also that the variants are comparable in length and difficulty**, since
      they are graded against one rubric). Iterate on this one row (re-stamp a new preview,
      delete the old) until approved.
5. **Stamp the full grid (after preview approval):** run `estampar.py build` with the complete
   spec (full grid) → the template board. Delete the preview. Verify via REST/MCP: the expected
   frame count + scaffolding items, **and the `SHARING teamAccess=private access=private` line**
   for the template board. Audit (Opus) against the acceptance criteria.
6. **Clone to sections — `build` per section (NOT `clone`/`copy_from`, which creates empty
   boards):** for each destination Space, copy the spec changing only `board.name` (swap
   `<space>`), and run `estampar.py build`. Verify the full frame count in each. **The conductor
   moves** each board to its Space (manual step).

## Acceptance criteria

- [ ] **Layer split respected:** Opus decided strategy+pattern and judged; **Sonnet** authored
      the build-spec; **`estampar.py` ran the stamping** (Opus via Bash directly, or Haiku).
      Opus did not hand-author every canvas item by item — the script does that.
- [ ] **Preview approved by the conductor BEFORE the bulk run** (Gate 2) — 1 canvas in the
      identical mode, **one canvas per variant** (`cols = <variants>`, `rows = 1`) in the
      per-column variant mode.
- [ ] **The template board is closed to the team** — `estampar.py` printed a `SHARING …` line
      reading `teamAccess=private access=private organizationAccess=private` for it (the line
      reads `SHARING (ya correcto) …` when it was already closed), or `lock` was run on it.
      A template still showing the team with `edit`/`view` is a defect.
- [ ] **No board was silently left open** — every board in the run printed either a `SHARING …`
      line or `SHARING (no es plantilla) space=<x> template_space=<y>`. A missing line, or a
      `space=` that is not the code you expect, means the name did not parse and the board's
      sharing was never decided.
- [ ] Section clones made with **`build` per section** (never `clone`/`copy_from`).
- [ ] Board count per exercise matches the session's exercise spec.
- [ ] Each board: the expected number of identically-named frames in a clean grid.
- [ ] **If per-column variants were used:** the board carries **`grid.cols` different
      variants**, each repeated down its own column, verified by spot-checking the first frame of
      **every** column against the variant the spec assigns to it. `estampar.py` only checks the
      entry *count* — a variant written into the wrong entry is caught nowhere else.
- [ ] **If per-column variants were used:** the variants were audited against each other for
      comparable length and difficulty (one rubric grades them all — otherwise the grade measures
      which column the student sat in), and no `alias` collides between `items` and a column's
      entry.
- [ ] Each frame: scaffolding per the spec using the **chosen catalog pattern** (A table+sticky /
      B mind map / C screenshots / or another), instructions top-left, clear empty zones to work
      in.
- [ ] **No work zone's `content` is a title alone** — every zone carries a bold title plus one or
      two sentences of instruction under it, at a smaller size than the title. Verifiable by
      script over the build-spec JSON: every zone item's `content` has more than just the title
      line/phrase.
- [ ] **If per-column variants were used:** any question whose answer depends on a
      variant-specific dimension (e.g. "if it doubled" without saying in what) names that
      dimension explicitly per variant, in the same element as the seeded case, and every
      variant's question ends in identical wording.
- [ ] **If the exercise asks for "a business you know":** the canvas states what counts (current
      job, family business, past job, or a business known closely as a regular customer) and that
      anything uncertain may be assumed — only an invented, non-existent business is disallowed.
- [ ] **Name matches the EXACT convention** `<board_prefix>-<space>-<session>-<exercise>-<Name>`
      (≤60 chars; session/exercise 2 digits); long descriptive name in `description`.
- [ ] **Gate 2 respected:** no clone to sections without preview approval.
- [ ] Instructions given to the conductor to **move boards to Spaces** (manual step).
- [ ] The **token never appears written** in any repo file.
- [ ] Any persistent API failure was **escalated to the conductor**.

## Close

Write the **board URLs** in the handover (so the conductor can share them and move boards to
Spaces). Check your box, add any new Miro lessons to `.claude/refs/shared-context.md`
(Haiku/REST calibration, geometry, colors, pitfalls), and emit the summary + the PROMPT FOR THE
NEXT AGENT per `.claude/refs/templates/next-agent-prompt.md`.
