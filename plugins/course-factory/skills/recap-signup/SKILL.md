---
name: recap-signup
description: >
  One-time, course-level artifact in the course-factory material-production harness. Produces
  the student-facing recap guidance doc (`<folders.project>/recap-signup.md`) and a
  capacity-capped sign-up Google Sheet (built from a CSV via the Drive MCP's text/csv
  conversion), for a course whose sessions include student-led recap slots. Invoke DELIBERATELY,
  and only ONCE per course (re-run only if the recap rules change), within a course
  material-production pipeline (the working folder has `.claude/refs/course.yaml`); do NOT
  auto-trigger for generic sign-up-sheet requests.
---

# Recap sign-up (guidance + sign-up Sheet)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder names,
> enabled artifacts, tool stack, publishing targets); (3) read `.claude/refs/PROTOCOL.md` — the
> course's contract, including its recap-slot rules (which sessions carry a recap, the
> per-student sign-up count, points); (4) read `.claude/refs/shared-context.md`. No per-session
> handover applies — this is a course-level, one-time artifact. If `recap-signup` is not in
> `artifacts.enabled`, STOP and warn the conductor. Write ALL generated content in
> `course.language`.
>
> **Guard:** this is a **one-time, course-level** artifact, not a per-session one. It typically
> runs right after the first session is planned; re-run only if the recap rules change.

**Tier:** Sonnet/Haiku (writes the guidance + builds the CSV) · Opus (you orchestrate and judge).

## What you produce

In `<folders.project>/`:

1. **`recap-signup.md`** — the recap guidance for students (what a recap is, what makes a good
   one, the slots, the rules), published as a Google Doc.
2. A **capacity-capped sign-up Google Sheet** (created from a CSV): one row per recap slot, name
   columns students self-fill, plus the per-student sign-up rule as a note.

## Inputs

- `<folders.sources>/<sources.syllabus>` — the recap-presentation section: which sessions carry a
  recap slot, the per-student sign-up count, capacity-capping intent, when sign-up opens.
- `<folders.sources>/<sources.session_briefs>` — the recap grading detail (good recap vs.
  read-back, any under-filled-slot fallback).
- `course.yaml schedule` — student count, session count/types, and dates, to compute slot dates
  and target presenters-per-slot.

## Process

1. **Guidance (`recap-signup.md`).** Write, in the register appropriate to the course's audience:
   - **What a recap is:** a short, student-led opener at the start of a session that recaps the
     previous session — key concepts in the student's own words, one real experiment/attempt
     tried between sessions, and one open question for discussion. (Exact length and placement
     per the course's own sources — do not assume a specific minute count.)
   - **What makes a good recap vs. a read-back:** full credit rewards genuine exploration and a
     real example; a bullet-point read-back earns partial credit only.
   - **The recap slots:** the exact session list from `schedule.session_types` / the syllabus
     recap section — each slot recaps the immediately preceding session.
   - **The rule:** each student signs up for the course's stated number of slots, at the
     course's stated points per slot (from `course.yaml evaluation.weights`) — read the exact
     count and point value from the course's own sources; do not assume a fixed number.
   - **Capacity cap:** each slot is capped so presentations spread across the term and avoid
     clustering. Compute a target presenters-per-slot from `schedule` (student count × sign-ups
     per student ÷ number of slots) and size the name columns accordingly.
   - **Fallback:** if a slot is under-filled after the course's stated grace period, the
     instructor assigns students to it.
2. **Sign-up Sheet (CSV → Google Sheet).** Build a CSV with one row per recap slot and
   capacity-capped name columns students self-fill:
   `Session | Date | Topic recapped (previous session) | Presenter 1 | Presenter 2 | …`
   — one row per recap slot (dates from the syllabus schedule; "Topic recapped" = the previous
   session's title). Add a top note stating the per-student sign-up rule, the points per slot,
   and the under-filled-slot fallback. The Presenter columns start empty for students to fill in.
3. **Create the Sheet** from the CSV via `Google_Drive.create_file` with
   `contentMimeType: text/csv` (`parentId` = the destination Drive subfolder from
   `publishing.drive.subfolders`). **VERIFY** it converted to a real Google Sheet — this
   conversion is not guaranteed on every Drive MCP setup. If it does not convert, alert the
   conductor, leave the CSV ready, and note the outcome in `.claude/refs/shared-context.md`
   (Open technical items). Record the Sheet link.
4. **Audit (judge).** Verify against the Acceptance criteria before accepting.

Do not re-upload local files that already sync to Drive — use the MCP only to create the
Doc/Sheet.

## Publication (this skill owns its pipeline end-to-end)

After the **human validates** `recap-signup.md`:

- **Guidance** → Google Doc via the `publish-google-doc` engine (into the `<folders.project>/`
  Drive subfolder). Record the link.
- **Sign-up Sheet** → created and verified as above; record the link. This is the Sheet
  introduced at the point in the course the course's own sources specify (e.g. right after the
  first recap-eligible session).

## Acceptance criteria

- [ ] `recap-signup.md` explains what a recap is and good recap vs. read-back (grading note
      included).
- [ ] The **recap slots** are present exactly as the course defines them, each mapped to the
      previous session it recaps.
- [ ] The **per-student sign-up count** and **capacity cap** (spread, no clustering) are stated,
      matching the course's own sources; the under-filled → instructor-assigns fallback is
      present.
- [ ] The **Sheet** has one row per slot with capacity-capped, self-fillable name columns and the
      sign-up-count note; it converted to a real Google Sheet (or the conductor was alerted).

## Close

1. Write `recap-signup.md` + the CSV; self-audit.
2. **Human gate (md-first):** the conductor validates the guidance + Sheet layout.
3. **Publish** the guidance to a Google Doc and create + verify the sign-up Sheet.
4. Update the relevant handover (link the Doc + Sheet) and add lessons to
   `.claude/refs/shared-context.md` (including the Sheet-conversion result), then emit the
   closing block per `.claude/refs/templates/next-agent-prompt.md`. This is one-time — note it is
   re-run only if the recap rules change; the next artifact is whatever the course PROTOCOL's
   sequence calls for next.
