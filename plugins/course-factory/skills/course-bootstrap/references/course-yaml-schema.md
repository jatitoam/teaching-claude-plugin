# `course.yaml` — the per-course configuration seam

Every course harness has exactly one `course.yaml` at `.claude/refs/course.yaml` inside the
course folder. It is **the seam between the generic plugin skills and the specific course**:
every artifact skill resolves the course root by finding this file, reads it, and lets its
values drive language, folder names, enabled artifacts, tooling, and publishing targets.

Rules:

- **YAML, machine-readable.** Skills read specific fields; keep keys exactly as specified.
- **Values, not prose.** Anything narrative (course description, pedagogy, policies) belongs in
  the course's source-of-truth documents (`sources:` below), not here.
- **This file syncs with the course folder** (Google Drive). Never put secrets in it — tokens
  live in environment variables on the conductor's machine (e.g. `MIRO_TOKEN`).
- **The bootstrap skill generates it** from the interview; the conductor edits it afterwards as
  the course evolves. Skills must tolerate missing optional keys (documented defaults below).

## Schema

```yaml
course:
  name: "Course Display Name"        # in the course's own language
  code: "XX-2026-II"                 # short id: course + cycle
  language: en                       # en | es — EVERY generated artifact is written in this
                                     # language (student- and instructor-facing). Skill
                                     # machinery and file/folder names stay English.
  program: "Program — Faculty — University"
  audience: "free text: who the students are (count, profile, technical level)"
  instructor:
    name: "Full Name"
    email: "who@university.edu"
  tas: []                            # list of {name, email}; empty if none

schedule:
  sessions: 10                       # total session count
  session_length_min: 240
  timezone: "GMT-6"
  meeting: "Fridays 18:00–22:00"     # free text; if the course runs multiple sections with
                                     # different times, describe them here and set `sections:`
  dates: "2026-07-10 to 2026-09-11"
  sections: []                       # optional. e.g. [{id: "A", time: "17:30"}, {id: "B",
                                     # time: "20:00"}] — when non-empty, slide speaker-note
                                     # headers carry the dual-schedule Ⓐ/Ⓑ times
  session_types:                     # every session number appears in exactly one list;
    virtual: [1, 2, 3, 5, 6, 8, 9]   # the set of type names is per-course (virtual / onsite /
    onsite: [4, 7]                   # final are the common ones) — the generated PROTOCOL.md
    final: [10]                      # defines each type's timeline shape and artifact sequence

evaluation:
  weights:                           # must sum to 100; keys are per-course activity names
    deliveries: 30
    checkpoints: 12
    final: 15
    exercises: 21
    labs: 8
    recaps: 4
    exams: 10

artifacts:
  enabled:                           # skill slugs that are LIVE for this course. Skills not
    - session-planning               # listed here must warn the conductor before proceeding.
    - class-exercises                # The generated PROTOCOL.md / START.md list only these.
    - slides
    - publish-google-doc
    # …plus any of: examples, readings, homework, lab, exam, practical-exam,
    # project-delivery, presentation-guide, recap-signup, publish-course-docs,
    # miro-boards, student-guide, assignment-solutioner

tool_stack:
  slides: local-html                 # only supported value today: local-html
  miro: false                        # false, or a block:
  # miro:
  #   enabled: true
  #   team_id: "1234567890"          # plaintext OK (not a secret); the TOKEN is not — it
  #   board_prefix: "TIC26"          # comes ONLY from the $MIRO_TOKEN environment variable
  #   spaces: ["P", "Ad", "Mk"]
  ollama_forced_failure: false       # true → the examples skill may guide forced-failure
                                     # demos with a small local model (ollama, optional)
  student_tools: "free text: the tool stack students use, in adoption order"

publishing:
  drive:
    course_folder_id: ""             # Drive folder ID of the course root
    subfolders: {}                   # per-type folder IDs, e.g. {exercises: "…", labs: "…"};
                                     # verified IDs also accumulate in shared-context.md
  portal: "GES"                      # student-submission portal name ("" if none). No API —
                                     # skills REMIND the conductor to create assignments.

naming:
  session_prefix: "S"                # S01, S02, … (two digits)
  folders:                           # canonical English names; a course may override values
    sources: Syllabus                # (keys are fixed — skills look up by key)
    planning: planning
    examples: examples
    exercises: exercises
    slides: slides
    labs: labs
    exams: exams
    project: project
    readings: readings
    homework: homework

sources:                             # filenames inside <folders.sources>/ — the course's
  syllabus: "Course Syllabus.md"     # sources of truth. Skills READ these, never duplicate.
  session_briefs: "Course Details and Development.md"
  glossary: "glossary.md"
  decisions: "decisions.md"
```

## Field notes

- **`course.language`** governs *content*, never *structure*: an `es` course still uses
  `planning/S03-plan.md`, `PROTOCOL.md`, English skill slugs — but every word written *inside*
  the artifacts, handovers' new entries, and conductor-facing summaries is Spanish.
- **`artifacts.enabled`** is the gate. All course-factory skills ship with the plugin; this list
  decides which are live here. A skill invoked while not listed must stop and warn (it may be a
  mistaken trigger).
- **`session_types`** names are free but must match the timeline shapes defined in the generated
  `PROTOCOL.md` — the bootstrap interview establishes both together.
- **`evaluation.weights`** keys should match the artifact vocabulary used in the syllabus; the
  session-planning skill and rubric steps read them for point values.
- **Secrets:** never in this file, never in `settings.local.json`, never anywhere in the synced
  folder. Environment variables only.

## Examples

**ET (English, no Miro, ollama demos):** `language: en`, `tool_stack.miro: false`,
`ollama_forced_failure: true`, `artifacts.enabled` = session-planning, examples,
class-exercises, slides, lab, exam, project-delivery, presentation-guide, publish-google-doc,
recap-signup.

**TIC (Spanish content, Miro, dual schedule):** `language: es`, `sections: [{id: "A", time:
"17:30"}, {id: "B", time: "20:00"}]`, `tool_stack.miro: {enabled: true, team_id: "…",
board_prefix: "TIC26", spaces: [P, Ad, Mk]}`, `artifacts.enabled` = session-planning, readings,
class-exercises, homework, slides, lab, exam, practical-exam, publish-google-doc,
publish-course-docs, miro-boards.
