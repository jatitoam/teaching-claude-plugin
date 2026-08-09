# Folder scaffold — enabled artifact → material folders

The bootstrap skill creates the course's on-disk folder tree from this mapping. Folder **names**
come from `course.yaml` `naming.folders` (look up by the fixed key; a course may override the
value — always use the resolved value, not the literal below). Create a folder **only** when its
owning artifact slug is in `artifacts.enabled` (plus the always-created ones).

## Always created (independent of enabled artifacts)

| Path | Purpose |
|---|---|
| `.claude/refs/` | harness machinery (`course.yaml`, `PROTOCOL.md`, `START.md`, `shared-context.md`, `grading-penalties.md`) |
| `.claude/refs/templates/` | `handover-session.md`, `next-agent-prompt.md` |
| `.claude/refs/handovers/` | per-session relay batons `handover-S<NN>.md` (starts empty) |
| `<folders.sources>/` | sources of truth (syllabus, session briefs, glossary, decisions) — key `sources` |
| `<folders.planning>/` | session plans `S<NN>-plan.md` — key `planning` (session-planning is always enabled) |

## Per enabled artifact slug

| Enabled slug | Folder(s) to create | `naming.folders` key(s) | Notes |
|---|---|---|---|
| `session-planning` | `<folders.planning>/` | `planning` | always enabled; the first agent of every session |
| `examples` | `<folders.examples>/` | `examples` | instructor-only packs `S<NN>/NN-*.md` + `00-index.md` |
| `class-exercises` | `<folders.exercises>/` | `exercises` | guides + rubric `.json/.xlsx` |
| `readings` | `<folders.readings>/` | `readings` | short readings `S<NN>-reading.md` |
| `homework` | `<folders.homework>/` | `homework` | homework/tarea brief + rubric |
| `slides` | `<folders.slides>/` | `slides` | slide-spec `.md`, `S<NN>-template-archetypes.md`, `S<NN>-build/` HTML, `S<NN> - <Name>.pdf`; conductor drops `S<NN>-template.pptx` here |
| `lab` | `<folders.labs>/` | `labs` | lab guide + rubric `.json/.xlsx` |
| `exam` | `<folders.exams>/` | `exams` | MCQ exam sheets |
| `practical-exam` | `<folders.exams>/` | `exams` | shares the exams folder |
| `project-delivery` | `<folders.project>/` | `project` | `D<n>-brief.md` + `D<n>-rubric.{json,xlsx}` |
| `presentation-guide` | `<folders.project>/` | `project` | checkpoint/final guides + rubrics (shares project folder) |
| `recap-signup` | `<folders.project>/` | `project` | one-time `recap-signup.md` + sign-up Sheet CSV (shares project folder) |
| `miro-boards` | *(none — boards live in Miro)* | — | no local material folder; the build-spec lives with `class-exercises` |
| `publish-google-doc` | *(none — engine)* | — | reusable publish engine; no folder of its own |
| `publish-course-docs` | *(none — engine)* | — | publishes the `<folders.sources>/` docs; no folder of its own |
| `student-guide` | `<folders.sources>/` | `sources` | course-level student guide alongside the syllabus |
| `assignment-solutioner` | *(none — writes to a git repo, not a material folder)* | — | teacher reference repo; out of the material tree |

## Rules

- **Never create a folder for a disabled slug.** The generated `PROTOCOL.md`/`START.md` list only
  enabled artifacts; the folder tree must match.
- **Shared folders are created once.** `project`, `exams`, and `sources` are shared by several
  slugs — create each once if any of its owners is enabled.
- **Do not pre-create per-session files** — only the folders. Skills create `S<NN>-*.md` at run
  time.
- **The `.pptx` templates are the conductor's** — `slides/` is created empty; the conductor drops
  `S<NN>-template.pptx` per session (blocking prerequisite for the build).
