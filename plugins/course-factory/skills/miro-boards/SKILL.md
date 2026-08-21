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
**grid of identical per-student canvases** (frames titled per the course's convention, e.g. "ID
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
`text` / `connector`, child coordinates measured center-from-frame-top-left) and the three
subcommands:
- `python estampar.py build <build-spec.json>` → creates the board, closes its sharing if it is a
  template (see below), and stamps the canvas grid.
  **Sonnet (layer 3) authors the `build-spec.json`.**
- `python estampar.py lock <boardId> [<boardId> …]` → closes an EXISTING board's sharing to the
  template policy. Idempotent; for retro-fixing boards created before this rule.
- `python estampar.py clone <boardId> "<new name>"` → **⚠️ NOT reliable** — `copy_from` creates
  the board but **EMPTY** (0 items). Do not use it. To clone template → sections, **re-run
  `build` with the same build-spec, changing only `board.name`**.

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
- **Gate 2 · Single-canvas DESIGN approval (preview), BEFORE the bulk run:** the conductor's
  visual gate is **one canvas** (grid **1×1**), not the full board. Stamp **1 frame** as a
  preview, the conductor reviews/adjusts it in the Miro UI, iterate on THAT ONE (each iteration
  costs a handful of calls, not hundreds), and **only after their approval** stamp the full grid
  and clone to sections. Rename the preview `…(PREVIEW 1 canvas)` and **delete it** on approval.
  **Never stamp the full grid or clone to sections without preview approval.**

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
3. **Choose the PATTERN** (layer 2, Opus) per exercise, from the catalog, per what the spec asks
   for.
4. **Build the build-spec and PREVIEW with 1 canvas:**
   a. **Layer 3 — Sonnet:** authors the `build-spec.json` (board `{name, description}`, `team_id`,
      **`template_space`**, `grid`, `items[]` of the chosen pattern with coords/colors/content).
      Save it in scratchpad.
      (Fine coordinate edits after conductor feedback can be Opus directly — mechanical editing.)
   b. **Preview 1×1 (layer 4):** copy the spec with `grid.cols=1,rows=1` and
      `name:"…(PREVIEW 1 canvas)"`, and run
      `python "${CLAUDE_PLUGIN_ROOT}/skills/miro-boards/scripts/estampar.py" build <preview.json>`.
      Opus runs the script via Bash directly (deterministic, cheaper than opening a Haiku agent
      — see the work-split table). Report the URL.
   c. **⛔ Gate 2 — the conductor validates the DESIGN in the UI** (colors, text, sizes, zones).
      Iterate on this one canvas (re-stamp a new preview, delete the old) until approved.
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
- [ ] **1-canvas preview approved by the conductor BEFORE the bulk run** (Gate 2).
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
- [ ] Each frame: scaffolding per the spec using the **chosen catalog pattern** (A table+sticky /
      B mind map / C screenshots / or another), instructions top-left, clear empty zones to work
      in.
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
