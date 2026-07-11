---
name: publish-google-doc
description: Reusable ENGINE that publishes a human-VALIDATED .md (exercise guide, lab guide, exam, project-delivery brief, presentation guide, reading, etc.) as a well-structured Google Doc in the right Drive subfolder. Part of the course-factory harness pipeline for building university course material. Use it ONLY in a course artifact skill's publication step (invoked by the owning artifact skill, e.g. class-exercises); NOT as a general-purpose .md→Google Doc converter and NOT triggered directly for generic requests.
---

# Publish Google Doc

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor folder
> containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder names,
> `publishing.drive` targets); (3) read `.claude/refs/PROTOCOL.md` — the course's contract,
> including its md-first → publication convention; (4) confirm in the session handover
> `.claude/refs/handovers/handover-S<NN>.md` what is validated. No handover applies to this skill
> itself — it is invoked as another artifact skill's final step and inherits that skill's session
> context. Write ALL generated content in `course.language`.

**Tier:** Haiku/Sonnet (mechanical: `.md`→Doc mapping + Drive MCP calls) · Opus (coordinates a
batch and verifies the links).

> **Delegate to Haiku — the orchestrator never makes the `create_file` calls itself.** Spawn a
> **Haiku agent** (Agent tool, `model: haiku`) that applies the Format convention below and makes
> the MCP calls (loading them via ToolSearch, `select:mcp__claude_ai_Google_Drive__create_file`),
> and returns each file's **ID + mimeType + viewUrl** for the orchestrator to verify and record.
> This rule exists because a conductor caught the lead model doing this mechanical work itself in
> a past session — keep the delegation, don't quietly reabsorb it.

## What it does

Converts a `.md` **already validated by the conductor** into a **well-structured Google Doc** in
the matching per-type Drive subfolder (`publishing.drive.subfolders`; we are on a Drive-synced
folder). Applies to exercise guides, lab guides, exams, project-delivery briefs, presentation
guides, readings, and any other course artifact whose owning skill calls this engine as its
publication step. *(Slides do NOT go here — they are built as local HTML by the `slides` skill.)*

## Principle

No pixel-perfect needed. With **correct headers and structure**, the conductor's default visual
style is inherited. Priority: **clear hierarchy** (Title → H1 → H2 → body/lists/tables) and
**printable** output when it applies (exams).

## Format convention

Drive's Markdown import maps `#`→Heading 1, `##`→Heading 2, etc., **but CANNOT apply the Google
Docs "Title"/"Subtitle" style** (no Markdown syntax exists for them). Therefore:

- **Title and subtitle go as NORMAL TEXT** in the first two lines of the `.md` you upload (title in
  **bold**, subtitle in *italic*). The conductor applies the Title/Subtitle style by hand (1 click
  each).
- **Shift every heading up one level on publish:** the source `.md`'s H1 (title) becomes normal
  text, and **each `##` becomes `#`** (sections become Heading 1), and so on. *(The source `.md`
  keeps its standard Markdown hierarchy; the shift is a transformation of the publish step, not of
  the source.)*
- **Method:** `Google_Drive.create_file` with `contentMimeType: text/markdown`, `parentId` =
  destination folder (resolved from `course.yaml publishing.drive.subfolders` for this artifact
  type; if not yet recorded there, check `.claude/refs/shared-context.md` for a verified folder ID
  before asking the conductor). Converts headings, bold, and tables → native tables; links/emails
  become clickable.
- If the course's artifact type carries a mandatory closing section (e.g. a license/attribution
  block some courses require on certain document types — check PROTOCOL.md/§publication for this
  artifact type), append it before publishing, ideally on its own page (the import can't force a
  page break, so add that to the manual-steps reminder below).

## Inputs

- The **validated `.md`** (the artifact from the calling skill).
- The **handover** `handover-S<NN>.md` — to confirm what is approved.
- Any **images** the calling skill sends (see §Images) — by default there are none.

## Process

1. **Confirm validated** in the handover (never publish drafts).
2. **Apply the Format convention** above (title/subtitle as normal text + heading shift `##`→`#`;
   any mandatory closing section for this artifact type).
3. **Create the Doc** in the **per-type subfolder** via `Google_Drive.create_file` (`text/
   markdown`, `parentId` = destination folder from `publishing.drive.subfolders`).
4. **The connector does NOT delete files:** if re-publishing, the old Doc is orphaned → **ask the
   conductor to trash it** by ID (give the old ID).
5. **Record the link/ID** in the handover ("Published" column) and, if it's a newly-verified
   folder ID, add it to `.claude/refs/shared-context.md` so future publishes don't re-resolve it.
6. **Raise the manual-steps reminder** to the conductor (see below) — ALWAYS, no exceptions.

## Connector limits (Drive MCP)

The Drive MCP **creates/copies files** but **does NOT expose the Google Docs API** (`batchUpdate`).
So programmatically you **cannot**: apply Title/Subtitle styles · create header/footer · force
page breaks · insert images by anchor · trash/move files. The conductor does all of that **by
hand** after publishing → the skill **ALWAYS raises a reminder**.

## Images (only when the calling skill sends them)

By default there are no images. When a calling skill does pass images (each with a file path +
anchor point + suggested size/alignment), the Drive MCP still **cannot** insert them by anchor
(no Docs API `batchUpdate`) — insertion stays **manual**: leave the image ready in Drive and
**raise it in the manual-steps reminder** with its anchor, for the conductor to place it. If a
referenced image doesn't exist on disk, do not publish partially — alert the conductor instead.

## Mandatory reminder to the conductor (raise it ALWAYS on publish)

Include a **manual-steps** block in your summary, because the connector cannot do these:

1. **Title/Subtitle:** apply the **Title** style to line 1 and **Subtitle** to line 2.
2. **Header/Footer:** insert them with the document titles (course / artifact type / session).
3. **Any mandatory closing section** for this artifact type (e.g. a license block), on its own
   page if the course requires that.
4. **Images**, if any were sent, placed at their anchor.
5. **If re-published:** send the **previous Doc** to the trash (pass the old ID).

## Batch mode

If the course's publication convention batches artifacts (e.g. "publish everything validated when
the session closes" rather than one at a time — check `.claude/refs/shared-context.md`/PROTOCOL.md
for the course's preference), publish the whole validated batch together instead of one artifact
at a time; otherwise publish incrementally as each artifact is validated.

## Acceptance criteria

- [ ] Correct, consistent heading hierarchy; tables/lists well formed; exams (or other
      print-facing types) printable.
- [ ] Title/subtitle as normal text + headings shifted up one level.
- [ ] Created in the **correct per-type subfolder**; link recorded in the handover.
- [ ] Only **validated** material was published.
- [ ] Images (if sent) placed at their correct anchor, or alerted if missing.
- [ ] Any artifact-type-mandatory closing section present, on its own page if required.
- [ ] **Manual-steps reminder raised** to the conductor (title/subtitle, header/footer, closing
      section pagination, trash old Doc if re-published).

## Close

Mark **"Published"** in the handover, **raising the mandatory reminder** (above) with the manual
steps the conductor must do in the Doc, and **return control to the owning skill**. This is a
**reusable engine invoked as another skill's final step** — it does **not** emit its own next-agent
routing. The **owning orchestrator** (e.g. `class-exercises`, or whichever skill called this
engine) is the one that emits the closing block and the PROMPT FOR THE NEXT AGENT per its own
§Close.
