---
name: publish-course-docs
description: >
  Course-level artifact in the course-factory material-production harness. (Re)publishes the
  course's syllabus/program source(s) — `<folders.sources>/<sources.syllabus>` (already validated
  by the conductor) — as the official Google Doc for students, reusing the `publish-google-doc`
  engine, and inserts course assets (e.g. a QR code, a logo) at the anchors the source doc marks
  for them. Invoke DELIBERATELY, only for publishing/republishing the course's syllabus/program,
  within a course material-production pipeline (the working folder has
  `.claude/refs/course.yaml`); do NOT auto-trigger for generic document-publishing requests.
---

# Publish course docs (syllabus/program)

> **Bootstrap:** course-level artifact, not session-level — do not read or write a session
> handover. If you start from zero: (1) locate the course root — the nearest ancestor folder
> containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder names,
> publishing targets); (3) read `.claude/refs/PROTOCOL.md` for the course's sources-of-truth
> convention; (4) read `.claude/refs/shared-context.md`. If `publish-course-docs` is not in
> `artifacts.enabled`, STOP and warn the conductor. Write ALL generated content in
> `course.language`.

**Tier:** Sonnet/Haiku (mechanical) · Opus only if a structural decision is needed.

## What it does

Converts `<folders.sources>/<sources.syllabus>` (already validated by the conductor) into the
official Google Doc for students — the source of truth they receive. **Reuses the
`publish-google-doc` skill** as the publication engine; this skill adds what's specific to the
syllabus/program: which course assets go where.

## Course-level artifact (not per-session)

The syllabus/program does not belong to a session. This skill runs once when the source is
approved, and is **re-run** if the source changes (a new version = republish). Do not read or
write session handovers — the witness here is the source document itself and
`.claude/refs/shared-context.md`.

## Inputs

- `<folders.sources>/<sources.syllabus>` (validated) — source of truth.
- **Course assets to place** — whatever the source document marks with an anchor (e.g. a
  WhatsApp/communication QR code next to a group-communication section, an institution logo in
  the header/cover). Read the anchors from the source document itself or from the conductor;
  pass each asset + its anchor to `publish-google-doc`.
- The conductor's reference style doc, if `publish-google-doc` uses one.

## Process

1. **Confirm with the conductor that the source is validated** (never publish a draft).
2. Map the `.md` to Google Doc structure: title → Heading 1 per top-level section → subtitles,
   tables, and lists. Preserve tables (evaluation weights, schedule, requirements, late-policy,
   or whatever tables the source contains).
3. **Delegate to `publish-google-doc`** the creation of the Google Doc in the syllabus's Drive
   subfolder (`publishing.drive.subfolders`), **passing it the list of assets with their
   anchors** (see Inputs). That skill performs the insertion; you decide which asset and where.
   - ⚠️ **Known connector limitation:** the Drive MCP cannot insert images into a Doc by anchor
     (no Google Docs API access — see `publish-google-doc`'s Connector limits section). Until a
     Docs-API-capable MCP exists, publish the text/tables and **leave each anchored asset for
     manual insertion**; alert the conductor with the asset's path and its anchor section. Do not
     block publication on this.
4. **Verify** that every anchored asset is where the source marks it once the conductor inserts
   it (or that the manual-step reminder was raised for each), and that any link the source
   contains (e.g. a communication-channel link) is present and correct.
5. Report the Google Doc link to the conductor and record it where the course's own convention
   indicates (e.g. a course-level `START.md` or a course-level note in
   `.claude/refs/shared-context.md`).

## Acceptance criteria

- [ ] All top-level sections present with correct hierarchy; tables and lists well formed.
- [ ] Every course asset the source marks with an anchor is either inserted or flagged with a
      manual-step reminder naming the asset and its anchor.
- [ ] Any link the source specifies (e.g. a communication-channel link) is clickable and correct.
- [ ] Created in the syllabus's Drive subfolder; link reported to the conductor.
- [ ] Only the **validated** version of the source was published.

## Close

Mark the syllabus/program as published (a note + the link, wherever the conductor's convention
indicates), and add any new lesson (e.g. connector behavior) to
`.claude/refs/shared-context.md`. If the source is edited afterward, **republish** (re-run this
skill) rather than patching the Doc by hand.
