---
name: attendance
description: >
  Reviews and records per-MEETING class attendance for a CONCLUDED course session from its Miro
  exercise boards, its lab submissions, or a manual acta present-list, maintaining a per-section
  JSON ledger under `<folders.students>/attendance-<section>.json` with per-meeting evidence, and
  exporting a per-section %-attendance spreadsheet. Part of the course-factory harness pipeline
  for building university course material. Invoke DELIBERATELY within a course material-production
  pipeline (the working folder has `.claude/refs/course.yaml`); do NOT auto-trigger for generic
  attendance, roster, or spreadsheet requests.
---

# Attendance (review & record)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor folder
> containing `.claude/refs/course.yaml`; (2) read `course.yaml` — in particular
> `naming.folders.students`, `naming.folders.labs` (for lab mode), `tool_stack.miro`,
> `evaluation.attendance` (the policy thresholds AND `meetings_by_type` — which meetings each
> session `type` has), and `publishing.drive`; (3) read `.claude/refs/PROTOCOL.md` — attendance is
> defined in §9; (4) for a virtual session, read that session's handover
> `.claude/refs/handovers/handover-S<NN>.md` **ONLY to get the Miro board IDs** (the
> "Materialización en Miro" table) — attendance does NOT otherwise couple to the
> handover/pipeline; (5) read `.claude/refs/shared-context.md`. **GATE:** if `attendance` is not
> in `artifacts.enabled`, STOP and warn the conductor; for the Miro meeting mode, also require
> `tool_stack.miro.enabled` to be `true` (lab and manual modes do not need Miro).
>
> **Guard:** this skill runs **STANDALONE after a session concludes** — it is **NOT** part of the
> session production pipeline. It writes **NO** handover and emits **NO** next-agent prompt.

**Tier / work split:**

| Layer | Who | Does |
|---|---|---|
| Orchestration + judgment | **Opus (you)** | Orchestrates the whole run; JUDGES relevance and authorship flags; decides the deterministic present/absent computation per meeting; writes the ledger; reports to the instructor. |
| Matching + drafting | **Sonnet** (delegate) | Fuzzy-matches frame titles → roster entries; drafts relevance verdicts from each frame's student-created content against the exercise consigna. |
| Mechanical execution | **Haiku / Opus-via-Bash** | Runs the reader scripts `leer_tablero.py` and `leer_lab.py`; publishes the export Sheet via the Drive MCP. |

## Gate: config

This skill only runs when `attendance` is in `course.yaml artifacts.enabled`. For the Miro
meeting mode it additionally requires `tool_stack.miro.enabled: true`; the lab and manual modes do
not need Miro at all. If the gate fails, stop immediately and tell the conductor.

## The per-meeting model

Each course week (S01–S22) carries **one session but two attendance meetings** — attendance is
tracked **per meeting**, each meeting is **one attendance unit**. Which meetings a session has
depends on its `type`, defined in `course.yaml evaluation.attendance.meetings_by_type`:

| `type` | Meetings | Source |
|---|---|---|
| `virtual` | `ejercicios` + `lab` | miro / lab |
| `workshop` | `taller-d1` + `taller-d2` | manual |
| `project` (S21) | `proyecto-d1` + `proyecto-d2` | manual |
| `exam` (S8, S18) | `examen` | manual |
| `final` (S22) | `final` | manual |

That's ~41 attendance units across the term. The course's `max_absences: 8` therefore means
roughly 8/41 ≈ 19.5% absence tolerance, i.e. ≥80.5% attendance — consistent with the program's
≥80% attendance requirement. Keep this arithmetic in mind when explaining alerts to the
instructor; it is computed from `meetings_by_type`, not hardcoded.

## What you produce

Updates `<folders.students>/attendance-<section>.json` — **one combined JSON per section**
(roster + policy + sessions together in the same file; canonical section keys are `Ad` and `Mk`).
Optionally, a per-section **%-attendance Google Sheet** built from the exported CSV.

## The JSON ledger

```jsonc
{
  "section": { "id": "Ad", "label": "Administración" },
  "policy": { "class_present_threshold": 0.5, "max_absences": 8, "absence_alert_fraction": 0.75 },
  "miro_account_map": {},                 // learned carné -> miro_user_id
  "roster": [ { "carne": "24001301", "name": "…", "email": "…", "status": "active",
                "joined_session": "S01", "notes": "" } ],
  "sessions": {
    "S01": {
      "date": "2026-07-06", "type": "virtual",          // virtual|workshop|exam|project|final
      "meetings": {
        "ejercicios": {                                  // source: miro — each meeting = 1 unit
          "source": "miro",
          "boards": { "02": { "id": "uXjVH-3WFJk=", "url": "https://miro.com/app/board/uXjVH-3WFJk=" } },
          "reviewed_at": "2026-07-13",
          "records": {
            "24001301": { "present": true, "located": true, "relevant": true, "authored_by_self": true,
                          "participated": true, "participation_rate": 1.0,
                          "exercises": { "02": { "located": true, "relevant": true,
                                                 "authored_by_self": true, "participated": true,
                                                 "frame_id": "…", "frame_title": "…",
                                                 "content_authors": ["…"], "notes": "" } },
                          "content_authors": ["…"], "flags": [], "notes": "" }
          },
          "flags": { "new_students": [], "unmatched_frames": [] }
        },
        "lab": {
          "source": "lab", "lab_id": "lab01", "reviewed_at": "…",
          "records": { "24001301": { "present": true, "group": "Grupo 1", "source": "lab01/Ad",
                                     "flags": [], "notes": "" } },
          "flags": { "new_students": [] }
        }
      }
    }
    // workshop: meetings {"taller-d1":{source:manual,…}, "taller-d2":{…}}
    // exam:     meetings {"examen":{source:manual,…}}
    // project:  meetings {"proyecto-d1":{…}, "proyecto-d2":{…}}   (S21)
    // final:    meetings {"final":{source:manual,…}}
  },
  "summary": { /* regenerated by build_attendance_sheet.py */ }
}
```

Invariants — respect these exactly:

- **present/absent is ALWAYS deterministic, now PER MEETING.** There is **no third status**.
  - `miro` meeting: per exercise, `participated = located AND relevant`; the meeting's
    `present = participation_rate ≥ policy.class_present_threshold` (≥50% of that meeting's
    exercises).
  - `lab` meeting: `present = the student is a member of a submitting group` for that lab.
  - `manual` meeting: `present = the carné is in the acta present-list` for that meeting.
- **"Fishy" findings are FLAGS, never a status.** They alert the instructor for manual review and
  **never**, by themselves, flip present↔absent (the instructor may manually override a record and
  re-export). Flags live in the per-record `flags[]` and the meeting-level `flags` block.
- **Denominator = attendance units (meetings), not weeks.** Max 8 absences over ~41 units (see
  above), not over 22 weeks.

## Inputs

- The session's Miro board IDs, from `.claude/refs/handovers/handover-S<NN>.md` (read ONLY for
  this — see Guard above).
- The exercise slots/consignas, from `<folders.exercises>/S<NN>-*.md`.
- The lab submissions folder, from `<folders.labs>/submissions/<lab_id>/<Ad|Mk>`.
- The acta present-list supplied by the conductor, for manual meetings.
- The section roster + policy, from `<folders.students>/attendance-<section>.json` itself.
- Environment: `MIRO_TOKEN` (never written to any file), read by `leer_tablero.py`.

## The three controls (Miro meeting)

1. **`located`** — the frame TITLE parses to a carné/name that fuzzy-matches the roster. Titles
   are messy (`24001301 - Fabricio`, `Germayoni Murillos - 24005311`, `Maria Soto-24001216`) —
   match on the **carné digits primarily**, name secondarily.
2. **`relevant`** — the frame contains **student-created** content: child items whose
   `created_by_id` ≠ the board's `service_account_id` (i.e. not the seeded scaffolding),
   representing a real attempt, not an empty/name-only frame. Sonnet drafts the verdict, Opus
   confirms.
3. **`authored_by_self` (FLAG layer only)** — from the student-created items' authorship, PLUS the
   frame's **last-modified-by** signal the reader exposes: `modified_by` / `modified_by_name` (the
   last account to touch the frame, e.g. who renamed the title). Use it as **corroborating
   evidence**: if the frame's `modified_by_name` AND the content `created_by_name`(s) both match
   the student named in the title → strong `authored_by_self:true`. **Flag** when (a) the frame's
   last modifier or the content authors are a DIFFERENT account than the claimed student, (b) one
   Miro account authored content/modified frames across many different students (see
   `author_frame_counts`) — the proxy/impersonation signal. IMPORTANT: the frame TITLE itself is
   **not** attributable to the student (it was created by the instructor's build script); `modified_by`
   is the best available proof that the claiming student actually edited their own frame, but it is
   still corroborating evidence, not a status — mismatches are flags, never auto-absent.

## Modes & Process

There are four modes; (a)–(c) each fill one or two meetings of a session, (d) exports.

### (a) Review a virtual session's Miro meeting — default for "Review attendance for S<NN>"

Fills the **`ejercicios`** meeting (source: miro) of a `virtual` session, covering every enabled
section (Ⓐ→`Ad`, Ⓑ→`Mk`).

1. Get each section's board id(s) from `handover-S<NN>.md`; get the exercise slots + consignas
   from `<folders.exercises>/S<NN>-*.md`.
2. For each section board, run the reader (Haiku/Bash):
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/attendance/scripts/leer_tablero.py" <board_id> --out <scratch>/S<NN>-<section>-frames.json`
   (reads `MIRO_TOKEN` from env; if unset/401 → stop, alert the conductor). Output = per-frame
   title + student-created children + author info + `modified_by`/`modified_by_name` +
   `service_account_id` + `author_frame_counts`.
3. **Match** (Sonnet): parse each frame title → carné/name, fuzzy-match to roster. An
   unmatched-but-parseable carné → auto-append to roster (`status:"active"`,
   `joined_session:"S<NN>"`) AND record in meeting `flags.new_students`. A title with no
   parseable carné → meeting `flags.unmatched_frames`.
4. **Assess** the three controls per matched student/exercise; set `located`/`relevant`/
   `authored_by_self`, `participated = located AND relevant`, store evidence (`frame_id`,
   `frame_title`, `content_authors`, `modified_by_name`). Attach `flags[]` for fishy cases
   (`name_only`, `authored_by_other`, `content_by_shared_account`).
5. Roll up per student: `exercises` map, `participation_rate`, deterministic meeting `present`.
6. Write into `sessions[S<NN>].meetings.ejercicios`; run the export script to refresh `summary`.
7. **Report to the instructor**: new students auto-added, the flag/manual-review queue, and any
   absence-alert students (≥75% of max).

### (b) Review a lab meeting — NEW (source: lab)

Fills the **`lab`** meeting of a `virtual` session's week. Read the section's lab submissions with
the new reader (Haiku/Bash):

`python3 "${CLAUDE_PLUGIN_ROOT}/skills/attendance/scripts/leer_lab.py" <folders.labs>/submissions/<lab_id>/<Ad|Mk>`

→ returns `present_carnes` + `groups` + `present_members`.

1. A roster student who is a member of ANY submitting group → `present:true`, record `group` and
   `source` (`"<lab_id>/<section>"`). An enrolled roster member in NO group → `present:false`.
2. **Fuzzy-match carné AND name** — lab JSONs can have typo'd carnés (e.g. `25005453` vs roster
   `24005453`), so cross-check by name too, and **flag** the mismatch (do not silently correct
   present/absent from a fuzzy match without a flag trail).
3. Any submitter carné not in the roster → auto-append (`status:"active"`, `joined_session`) AND
   record in meeting `flags.new_students`.
4. **Lab folder ≠ session number.** Lab folders are numbered by sequence (`lab01`, `lab02`, …),
   which maps to the ordered `schedule.session_types.virtual` weeks (`lab01`=S01, `lab02`=S03,
   …), NOT to the session number directly. Confirm the `lab_id` for the session with the
   conductor before running the reader.
5. Write into `sessions[S<NN>].meetings.lab`.

### (c) Manual meeting — (source: manual) for taller/exam/project/final

The instructor supplies an acta present-list (carnés present) for the session's manual meeting(s).

1. Set each present carné `present:true`; enrolled roster members not listed → `present:false`;
   store `acta` (e.g. "acta con firmas <fecha>") and `source:"manual"` per meeting.
2. A `workshop`/`project` week has **two** manual meetings (`taller-d1`/`taller-d2` or
   `proyecto-d1`/`proyecto-d2`). By default, one present-list marks **both** meetings identically;
   if the instructor supplies per-day lists, honor them per meeting instead.
3. `exam` and `final` weeks have a single manual meeting (`examen` / `final`).

### (d) Export

Run:
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/attendance/scripts/build_attendance_sheet.py" <students>/attendance-Ad.json <students>/attendance-Mk.json`
→ refreshes each JSON's `summary`, writes `<id>-asistencia.csv` per section with **one column per
meeting** (e.g. `S01·ejercicios`, `S01·lab`, `S08·examen`), prints alerts/flags. Then delegate
CSV→Google Sheet publish to Haiku via the Drive MCP `Google_Drive.create_file` with
`contentMimeType: text/csv` (the same pattern `recap-signup` uses) into the appropriate Drive
subfolder; **VERIFY** it converted to a real Sheet; record the link. One Sheet per section.

**Policy source:** read `max_absences`, `class_present_threshold`, `absence_alert_fraction` from
`course.yaml evaluation.attendance` (mirrored into each JSON's `policy` block).

## Acceptance criteria

- [ ] Every enrolled roster student has a record for EACH meeting reviewed.
- [ ] Present/absent is deterministic **per meeting**: `miro` →
      `participated = located AND relevant`, `present = participation_rate ≥
      policy.class_present_threshold`; `lab` → present iff member of a submitting group; `manual`
      → present iff carné is in the acta list.
- [ ] Lab-mode matching tolerates carné typos by cross-checking name, and flags any mismatch it
      resolves.
- [ ] Fishy cases are **flags**, never silently resolved and never a third status.
- [ ] New students are auto-appended with `joined_session` AND reported to the instructor.
- [ ] The denominator used for alerts/summary is attendance units (meetings), not weeks.
- [ ] Absence alerts (≥ ceil(0.75 × max_absences)) are surfaced.
- [ ] Evidence (`frame_id` / `frame_title` / `content_authors` / `modified_by_name` for miro;
      `group` / `source` for lab; `acta` for manual) is stored for every record, for disputes.
- [ ] Both section JSONs remain valid JSON after the write.
- [ ] `MIRO_TOKEN` never appears written in any file.
- [ ] Any persistent API failure is escalated to the conductor.

## Close

- Write/refresh the ledger; run the export; **report to the instructor** (new students, flag
  queue, absence alerts).
- Optionally record a durable new lesson in `.claude/refs/shared-context.md` (e.g. matching
  quirks, Miro authorship calibration, lab carné-typo patterns).
- **Explicitly:** this skill writes **no** session handover and emits **no** next-agent prompt — it
  runs standalone after the session concludes.
