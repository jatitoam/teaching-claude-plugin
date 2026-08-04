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
| Matching + drafting | **Sonnet** (delegate) | Fuzzy-matches frame titles → roster entries; drafts relevance verdicts from each frame's student content (`is_student_content` — created items **and** seeded zones written into) against the exercise consigna. |
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
          "source": "lab", "lab_id": "S01", "reviewed_at": "…",
          "records": { "24001301": { "present": true, "group": "Grupo 1", "source": "S01/Ad",
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
  - `miro` meeting: per exercise, `participated = located AND relevant AND authored_by_self`
    (control #3 is a GATE — a `located` frame whose work is verifiably done by someone else is
    NOT participation); the meeting's `present = participation_rate ≥
    policy.class_present_threshold` (≥50% of that meeting's exercises).
  - `lab` meeting: `present = the student is a member of a submitting group` for that lab.
  - `manual` meeting: `present = the carné is in the acta present-list` for that meeting.
- **The controls DETERMINE present/absent; flags ride alongside for review.** A `located` frame
  that is irrelevant, or verifiably authored entirely by another student, is **absent** — and
  carries a **flag** (`name_only`, `authored_by_other`, `content_by_shared_account`,
  `authorship_unverifiable`, carné-typo) so the instructor can review and **manually override** the
  computed value if warranted. There is still **no third status**: the stored value is always
  present or absent; flags live in the per-record `flags[]` and the meeting-level `flags` block.
- **Denominator = attendance units (meetings), not weeks.** Max 8 absences over ~41 units, not
  over 22 weeks.

## Inputs

- The session's Miro board IDs, from `.claude/refs/handovers/handover-S<NN>.md` (read ONLY for
  this — see Guard above).
- The exercise slots/consignas, from `<folders.exercises>/S<NN>-*.md`.
- The lab submissions folder, from `<folders.labs>/submissions/S<NN>/<Ad|Mk>` (session-numbered).
- The acta present-list supplied by the conductor, for manual meetings.
- The section roster + policy, from `<folders.students>/attendance-<section>.json` itself.
- Environment: `MIRO_TOKEN` (never written to any file), read by `leer_tablero.py`.

## The three controls (Miro meeting)

1. **`located`** — the frame TITLE parses to a carné/name that fuzzy-matches the roster. Titles
   are messy (`24001301 - Fabricio`, `Germayoni Murillos - 24005311`, `Maria Soto-24001216`) —
   match on the **carné digits primarily**, name secondarily.
2. **`relevant`** — the frame contains **student content**, representing a real attempt rather than
   an empty/name-only frame. Sonnet drafts the verdict, Opus confirms.

   **⚠️ Student content arrives by TWO routes — judging only the first marks present students
   absent.** Use the reader's **`is_student_content`** field, which is the union of both:
   - **`is_student_created`** — the student CREATED the item (`created_by_id` ≠ `service_account_id`).
   - **`is_student_edited`** — the student WROTE INSIDE a seeded shape (a colored zone of the
     scaffolding) instead of creating a new sticky. That item keeps the instructor script's
     `created_by_id`, so route 1 cannot see it; the reader detects it because its **text differs
     from the factory text** (baseline = the children of the frames nobody claimed on that same
     board, reported under `baseline`).

   Never judge on the raw count of *created* items alone: on a zone-based canvas, a fully answered
   frame can legitimately have **zero** created items. Give the judge the item text, and tell it
   that each `is_student_edited` item starts with the factory instruction and the student's answer
   follows it.

   **Known blind spot — very short answers.** The baseline is a board-wide *set* of factory texts,
   not one scoped per zone. A genuine one-word answer that happens to match *some other* zone's
   placeholder verbatim (`Sí`, `No`, `1`) reads as unedited, so a present student can come back
   `is_student_edited: false`. The error only ever runs in the safe direction (undercount, never a
   false present), but when a frame looks empty and the exercise invites terse answers, **open that
   frame in Miro before recording an absence**.

   **The signal is the TEXT, not `modified_by_id`.** Dragging a seeded sticky — which several
   exercises explicitly ask for — changes `modified_by_id` without adding a single word; counting
   that credits students who wrote nothing.

   **Sanity check before writing the ledger:** if an exercise yields many renamed-but-empty frames,
   suspect the reader, not the class. Check `summary.frames_with_student_content` and
   `baseline.reliable` — if `reliable` is `false` the board had too few unclaimed frames to derive
   the factory text, in-place edits are undetectable, and you must **stop and tell the conductor**
   instead of recording absences.
3. **`authored_by_self` — a GATE against a friend covering for the student.** The spirit: make sure
   the frame's work is really the claimed student's, not another student doing it in their place.
   Gather **every authorship signal** the reader exposes for that frame and resolve each to a person
   via board members:
   - the frame's **`modified_by_name`** — the last account to edit/rename the frame (the best proof
     the claiming student actually touched it), and
   - the **`created_by_name`** of each **student-created** content item in the frame.

   Then decide:
   - **≥1 signal resolves to the claimed student** → `authored_by_self = true` (present, if also
     relevant). One genuine trace is enough — the student did participate.
   - **Signals exist and resolve, but NONE is the claimed student** (every editor/author is a
     different identified person) → `authored_by_self = false` → the exercise is **NOT
     participation → ABSENT + flag** `authored_by_other` with the offending name(s). This is the
     "someone covered for me" case — do **not** award it.
   - **No signal is verifiable** (Miro returned no author ids, or none resolve to a name — e.g.
     non-Enterprise limits) → `authored_by_self = true` but **flag** `authorship_unverifiable`.
     Never punish a student for an API gap; the instructor can spot-check the flag.

   Also raise a `content_by_shared_account` flag when **one** Miro account authored content in
   **many different students'** frames (`author_frame_counts`) or was the last modifier of many of
   them (`modifier_frame_counts`) — the proxy signal, even if that account also includes the
   student. NOTE the frame TITLE itself is not attributable (it was
   created by the instructor's build script); authorship is judged from `modified_by` + the
   student-created content, matched on **names** (email is Enterprise-gated).

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
   title + children with `is_student_created`/`is_student_edited`/`is_student_content` +
   per-frame `student_items` + `baseline` (factory-text detection) + author info +
   `modified_by`/`modified_by_name` +
   `service_account_id` + `author_frame_counts` + `modifier_frame_counts`.
3. **Match** (Sonnet): parse each frame title → carné/name, fuzzy-match to roster. An
   unmatched-but-parseable carné → auto-append to roster (`status:"active"`,
   `joined_session:"S<NN>"`) AND record in meeting `flags.new_students`. A title with no
   parseable carné → meeting `flags.unmatched_frames`.
4. **Assess** the three controls per matched student/exercise; set `located`/`relevant`/
   `authored_by_self`, then `participated = located AND relevant AND authored_by_self` (control #3
   is a GATE — a located+relevant frame authored entirely by someone else is NOT participation →
   absent). Store evidence (`frame_id`, `frame_title`, `content_authors`, `modified_by_name`).
   Attach `flags[]` for every non-obvious case (`name_only`, `authored_by_other`,
   `content_by_shared_account`, `authorship_unverifiable`).
5. Roll up per student: `exercises` map, `participation_rate`, deterministic meeting `present`.
6. Write into `sessions[S<NN>].meetings.ejercicios`; run the export script to refresh `summary`.
7. **Report to the instructor**: new students auto-added, the flag/manual-review queue, and any
   absence-alert students (≥75% of max).

### (b) Review a lab meeting — (source: lab)

Fills the **`lab`** meeting of a `virtual` session's week from the section's lab submissions.

**Prerequisite / data source — the plugin does NOT create this.** Lab-mode auto-fill needs, per
submitting group, its **members with carnés**. The reader looks for
`<folders.labs>/submissions/S<NN>/<section>/evaluations/row_*.json` files carrying a `members`
array of `"Nombre (carné)"` strings. Both that folder layout and the `members` field are a
**course convention the conductor arranges**: the base `evaluation-rubrics:assignment-evaluator`
skill writes `row_<slug>.json` as `{name, scores, observations, penalties}` with **no `members`**
and defaults its output to the submission's own folder — so it does not, by itself, populate this.
Before relying on auto-fill, confirm the course actually drops member-bearing group JSONs under
`submissions/S<NN>/<section>/`.

Run the reader (Haiku/Bash):
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/attendance/scripts/leer_lab.py" <folders.labs>/submissions/S<NN>/<Ad|Mk>`
→ returns `groups` + `present_members` + `present_carnes` (folders are session-numbered, so the
folder matches the session directly).

**If `present_carnes` is non-empty** (member-bearing JSONs found), match each submitter to the
roster in this order (so a typo'd carné doesn't become a phantom student):
1. **Carné match** → that roster student is `present:true`; record `group` and `source`
   (`"S<NN>/<section>"`).
2. **No carné match, but NAME matches a roster student** (typo'd carné — e.g. `25005453` where the
   roster has `24005453`) → map to that roster student, mark `present:true` **under the roster's
   carné** (authoritative), and **flag** `carne_typo` with the submitted vs roster carné. NOT a new
   student.
3. **Neither carné nor name matches** → genuinely new: auto-append (`status:"active"`,
   `joined_session:"S<NN>"`) AND record in `flags.new_students`.
4. An enrolled roster member in NO submitting group → `present:false` (absent for the lab).

**Fallback — if `present_carnes` is empty** (the reader returned only group PDFs, or JSONs without
a `members` field — the common case for a fresh course): **do NOT mark the whole section absent.**
Membership isn't machine-readable, so obtain it another way and fill the meeting like a manual one
— the instructor provides the group→members mapping or a lab present-list, or you read membership
from the `groups`/PDF names the reader surfaced. Record `source` accordingly (e.g.
`"S<NN>/<section> (manual)"`) and **report to the instructor** that lab membership was resolved
manually.

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
      `participated = located AND relevant AND authored_by_self`, `present = participation_rate ≥
      policy.class_present_threshold`; `lab` → present iff member of a submitting group; `manual`
      → present iff carné is in the acta list.
- [ ] **Authorship gate applied:** a located+relevant frame whose authorship signals
      (`modified_by` + student-created content) resolve but include **none** of the claimed student
      is **absent + `authored_by_other`**; ≥1 matching signal → present; no verifiable signal →
      present + `authorship_unverifiable` (never punished for an API gap).
- [ ] Lab-mode matching tolerates carné typos by cross-checking name (mapping to the roster carné,
      flagging `carne_typo`, NOT creating a phantom student).
- [ ] **`relevant` judged on `is_student_content`** (created items **plus** seeded zones the
      student wrote into), never on the count of created items alone; `baseline.reliable`
      confirmed `true` before any absence is recorded.
- [ ] Fishy cases carry **flags** for manual override; the stored value is always present/absent,
      never a third status.
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
