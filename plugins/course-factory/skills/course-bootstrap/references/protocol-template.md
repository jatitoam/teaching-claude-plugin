<!--
  PROTOCOL TEMPLATE — course-factory / course-bootstrap
  ======================================================
  The bootstrap skill copies this file into <course>/.claude/refs/PROTOCOL.md and
  fills every {{placeholder}} from the interview + course.yaml. Bootstrap guidance is in
  <!-- bootstrap: ... --> comments; DELETE every such comment from the generated file.
  Sections marked "INCLUDE-IF <slug>" are emitted only when that slug is in
  artifacts.enabled — otherwise drop the whole section and renumber.
  The generated file names the course and its settled facts directly; it must contain NO
  {{placeholders}} and NO bootstrap comments once written.
-->
# PROTOCOL — Material-production harness for *{{course_name}}* ({{course_code}})

> **This is the contract that EVERY fresh agent reads and obeys on startup.**
> If you are a freshly launched agent producing one part of one session, start here.

---

## 0. What this harness is (one paragraph)

We produce the course material **session by session, one artifact at a time**. For each
artifact, the **human conductor** (the instructor) launches **one fresh, front-line Opus agent**
that: starts from zero, orients itself from the on-disk documents, produces its artifact
(delegating the heavy lifting to cheaper agents), self-audits, updates the living documents,
and **ends by emitting a "PROMPT FOR THE NEXT AGENT"** that the conductor copies to launch the
next part. The relay baton is **the documents** (the session handover + shared context), not the
conversational memory. This optimizes tokens and context: each agent loads only what it needs.

<!-- bootstrap: fill {{language_line}} from course.yaml language. For an English course write
     "The whole course is in English. Every artifact — slides, exercise guides, labs, exams,
     delivery briefs, rubrics — is written in English." For a non-English course name the
     language and note the only exception if any (e.g. an English course title). -->
{{language_line}}

## 1. Roles

- **Conductor (human):** coordinates the global work, launches each agent, **validates every
  artifact** before moving on, and decides whether to adjust or advance. **The approval gate is
  theirs.**
- **Orchestrator (you, fresh Opus):** responsible for **one** artifact of **one** session. You
  orient, delegate production, **judge** quality, write the artifact and the docs, and emit the
  next prompt. **You do not chat with the human mid-run** (agents cannot pause and ask). You leave
  everything ready and finish with a summary for the human to validate.
- **Cheap agents (Sonnet/Haiku):** production under your direction (see tier map §6).

## 2. Bootstrap — what you do on startup (in order)

1. **Locate the course root.** It is the **nearest ancestor folder containing
   `.claude/refs/course.yaml`** (the root marker). You may be launched from the root **or** from a
   subfolder; resolve all paths from the root.
   - The course lives in a **Google Drive-synced folder**, so everything in it (including
     `.claude/`) travels with Drive and is visible to **any agent on any device**. Publications
     (§7) go to this same Drive folder and its per-type subfolders.
2. **Read `course.yaml`** — language, folder names (`naming.folders`), enabled artifacts
   (`artifacts.enabled`), tool stack, publishing targets. Every generated word follows
   `course.language`; file/folder names stay English.
3. **Read the sources of truth** (§4) that apply to your task. **Do not duplicate them.**
4. **Identify your `(session, artifact)`** from the launch prompt.
5. **Read your session handover** `.claude/refs/handovers/handover-S<NN>.md` if it exists.
   (If you are the **Session-Planning** agent, you **create** it from the template.)
6. **Read `.claude/refs/shared-context.md`** (accumulated lessons and conventions).
7. **Invoke your skill from the `course-factory` plugin** (`/<slug>`). This course's live skills
   are: {{enabled_skill_slugs}}.
   <!-- bootstrap: {{enabled_skill_slugs}} = the artifacts.enabled list rendered as
        `session-planning`, `class-exercises`, … (only the enabled ones). -->
   - **The skills are PLUGIN skills, not folder skills.** They ship with the `course-factory`
     plugin; there is no `.claude/skills/` in this folder. If a skill you were asked to run is
     **not** in `artifacts.enabled`, **STOP and warn the conductor** — it may be a mistaken
     trigger.
   - **Deliberate invocation, not auto-trigger.** Skills fire **on purpose** (you invoke them when
     running the pipeline, or the conductor with `/<slug>`), **never** by auto-detection on a
     generic request. Their `description` fields carry an explicit guard against auto-firing
     outside course-material production.

## 3. Artifact cycle

```
Orient → Delegate production (right tier) → Audit (judge) → Write .md
       → Update handover + shared-context + decisions → Emit next-agent prompt
```

- **Audit (judge):** before accepting a cheap agent's output, review it against the **acceptance
  criteria** in your skill. If it fails, iterate or redo it yourself. Do not ship material you did
  not audit.
- **md-first:** every content artifact is delivered **first as `.md`** for the human to validate
  (**the human is the gate**). After your sign-off, **the same orchestrator continues** in the same
  run and produces the artifact's publication/materialization (Google Doc, local HTML slide
  build{{publish_targets_inline}}), with **additional human gates where they apply**. There is
  **no** separate "batch publication step": each skill runs its pipeline end to end (§7).
  <!-- bootstrap: {{publish_targets_inline}} = ", Miro boards" if miro-boards enabled, ",
       sign-up Sheet" if recap-signup enabled; else empty. -->
- **No internal shorthand in anything a student reads.** Decision IDs (`D12`, `D50`), section
  marks (`§4`), harness vocabulary ("the pack", "the manifest", "the second scored row", "Block
  A") are **our** conventions. A student learns nothing from them and is shut out of a private
  language. **Cite the substance, never the reference.**
  - **This binds rubric text too** — criterion names, level descriptors and the penalties block
    are read by students. Write "submitted late" and the actual percentage, never a pointer to a
    decision record.
  - **Spell out identifiers students do share.** Where a course numbers deliveries/assignments,
    write **"Delivery 2"**, **"Delivery 3, due Sunday 23 August"** — not `D3`. ⚠️ **Watch the
    collision:** in a course with both, `D2` may read as *Delivery 2* while `D50` is a decision
    record. **If a number could be read either way, write the word.**
  - **Less text, simple bullets, written to the student.** Short lines over full sentences, plain
    words over harness vocabulary. If a line only parses for someone who has read the planning
    documents, it belongs in the speaker notes or instructor-only material — or nowhere.
  - **Verification:** grep student-facing artifacts (including rubric `.json`/`.xlsx` cell text)
    for a capital `D` followed by digits and for `§`. ⚠️ **The grep is necessary but NOT
    sufficient** — harness shorthand hides in ordinary English ("the second scored row", "the
    first block"). **Read for it as well.**

## 4. Sources of truth and the no-redundancy rule

Read from here; **do not rewrite** what already lives in these files. Only **reference** it.

> **The harness is the single source of truth.** All project knowledge, decisions, and conventions
> live **inside this folder** (`.claude/refs/` plus `{{sources_folder}}/`), which travels with
> Drive and is seen by **any agent on any device**. **Do not** store project things in external
> memories or in the assistant's **global** `~/.claude*` (outside this folder): that does not sync
> and other agents will not see it. If something is worth remembering, write it into the right
> harness file.

<!-- bootstrap: {{sources_folder}} = naming.folders.sources. Fill the table rows from the
     sources: map (syllabus, session_briefs, glossary, decisions) with real filenames. -->

| You need… | It's in | You… |
|---|---|---|
| Student-facing program (schedule, weighting, policies) | `{{sources_folder}}/{{sources.syllabus}}` | read |
| Per-session briefs (topics, teaching blocks, exercises, milestones) + grading detail | `{{sources_folder}}/{{sources.session_briefs}}` | read (and **enrich** your session's block if needed) |
| Glossary / shared terminology | `{{sources_folder}}/{{sources.glossary}}` | read (and **enrich** if a new core term appears) |
| Decisions log | `{{sources_folder}}/{{sources.decisions}}` | **append** (D1+) |
| Production lessons/conventions | `.claude/refs/shared-context.md` | **write** (only what's new) |
| Session relay state | `.claude/refs/handovers/handover-S<NN>.md` | **write** (the baton) |

<!-- bootstrap: if the course has extra sources of truth from the interview, add rows. -->

<!-- bootstrap: INCLUDE-IF the interview (8b) captured prior-offering material — else drop this
     whole block. {{prior_year_sources}} = one bullet per source: kind (docs folder / Canva
     designs / LMS export / repo / readings embedded in per-class docs), exact location (path,
     Canva search terms, URL), and reading constraints (e.g. big files → offset/limit reads
     only). If a catalog/index file was seeded in {{sources_folder}}/ (recommended), its bullet
     points there FIRST. The confirm-with-conductor bullet below is MANDATORY whenever this
     block is included — never drop it. -->
**Prior-offering material (mandatory review before producing):** when planning and when
producing content, **review the previous offering's material first** and use it as the base:
for each element decide **reuse / adapt / rebuild / new** and record the verdict in the plan.
Write from scratch only when nothing exists or the approach changed completely.
{{prior_year_sources}}
- **⚠️ Every match must be CONFIRMED by the conductor before it counts as the base.** Courses
  drift between offerings — sessions get reordered and titles reworded — so a match by number
  or title can be the wrong source. Match by **topic/title, never by session number alone**.
  The planning agent records each matched source as **proposed** (in the plan and the
  handover's per-artifact sources table), surfaces it prominently in the conductor-facing
  closing summary, and only after the conductor validates it at the md-first gate do
  downstream agents use it. Unconfirmed pointers are marked as such and never silently adopted.

## 5. Settled facts (do NOT re-litigate)

<!-- bootstrap: {{settled_facts}} = a compact prose block of the course's fixed facts, drawn from
     course.yaml + the interview: session count × length, meeting day/time + timezone, section
     schedule if any, audience, session-type split, the full evaluation model (each weight with
     its point derivation), the tool stack, and any delivery→presentation map the course uses.
     Mirror ET §5's density. End with "We build ON TOP of this, we do not reopen it. (Full detail
     in the {{sources_folder}}/ docs.)" Do NOT invent facts not established in the interview —
     leave an explicit [placeholder] + a conductor note where a fact is still missing. -->
{{settled_facts}}

<!-- bootstrap: INCLUDE-IF the interview surfaced a provisional external coupling (e.g. a project
     shared with another course, an unsettled co-teaching split). Otherwise DROP this blockquote. -->
> **{{provisional_coupling_title}} (provisional).** {{provisional_coupling_body}} Do **not**
> assume the other side's curriculum, topics, or deliverables in any artifact.

## 6. Tier map (which model produces what)

<!-- bootstrap: {{tier_map}} = one row per ENABLED skill, in production order, drawn from the
     default tier map in shared-context-seed.md (Session planning = Opus; Examples = Sonnet
     author + Opus judge; Slides spec = Sonnet content + Opus mechanical header; Slides build =
     Sonnet HTML + Opus extract/index/QA; Class exercises = Sonnet + Opus judge; Lab = Sonnet →
     Opus if tool complex + Haiku/Bash rubric; Exam = Sonnet + Haiku; Project delivery = Opus
     orch + Sonnet draft + Haiku/Bash rubric; Presentation guide = Sonnet → Opus + Haiku/Bash
     rubric; Publish Google Doc = Haiku MANDATORY; Miro boards = Opus decide + Sonnet build-spec
     + Haiku/Bash estampar.py; Readings/Homework/etc. per the source skill). Drop rows for
     skills not enabled. -->

| Skill | Production tier | Notes |
|---|---|---|
{{tier_map}}

<!-- bootstrap: {{publish_rows_inline}} and (§7) {{publish_targets_inline}} / {{publish_engines_inline}}
     = the extra publication surfaces this course enables beyond Slides build + Google Doc — e.g.
     ", Miro boards" when miro-boards is enabled, ", submission/sign-up Sheets" when recap-signup
     is enabled. Empty string when the course has none. Keep all three consistent. -->
**Opus (you) always orchestrates and does the final QA.** The **publication rows** (Slides
build, Google Doc{{publish_rows_inline}}) are **not steps launched separately**: they are
**engines the owning orchestrator invokes** as its final step, after the human gate (§7). Tier
calibration is live: if a cheap agent underperforms on a skill, **note it in `shared-context.md`**
and bump the tier.

> **Mandatory-Haiku publish (hard rule).** The mechanical `.md`→Google Doc transform and **all**
> Drive MCP calls are delegated to **one Haiku agent** (loads Drive tools via ToolSearch, returns
> id/mimeType/viewUrl); the lead only verifies + records. The lead calling `create_file` itself
> is a process violation.

## 7. md-first → the same skill publishes/materializes

**Each artifact skill owns its complete pipeline.** There is no "separate batch publication": the
**same orchestrator** that produced the `.md`, **after your validation**, publishes/materializes it
in the same run. The **human is the gate** at each natural cut (the orchestrator ends its turn with
a summary; you validate; green light to continue).

**Generic per-artifact flow:**
1. The orchestrator produces the `.md` in its per-type folder (per `naming.folders`) and
   **self-audits**.
2. **Human gate:** you validate the `.md`.
3. The **same orchestrator** produces the final artifact (Google Doc / local slide build{{publish_targets_inline}}),
   with additional gates where they apply.
4. It finishes and emits the prompt for the **next artifact**.

The publication skills (`publish-google-doc`, the local slide build{{publish_engines_inline}})
**are not launched separately**: they are **reusable engines the owning orchestrator invokes** as
its final step. *(The heavy part runs on Sonnet/Haiku per §6; you, Opus, orchestrate and QA.)*

**Detail by destination (reference):**
- **Google Docs** (exercise guides, lab guides, exams, delivery briefs, presentation guides) →
  engine `publish-google-doc`. We are on a Drive-synced folder: structure with clean headers; the
  visual style is inherited. Target: the course folder and its per-type subfolders. Via MCP
  `Google_Drive.create_file` with `parentId` = destination folder.
  - **Connector limit + convention (re-verify on first use):** the Drive MCP **does not expose the
    Google Docs API** → programmatically you **cannot** apply Title/Subtitle styles, create
    header/footer, force page breaks, or insert images by anchor. The skill automates what it can
    (title/subtitle as normal text + **header shift** `##`→`#`, computed from the source's actual
    heading structure, not a blind shift) and **ALWAYS raises a reminder** to the conductor with
    the manual steps. `contentMimeType: text/markdown` converts headers, bold, and **tables to
    native tables**; links/emails become clickable. Detail in `publish-google-doc`.
<!-- bootstrap: INCLUDE-IF recap-signup enabled — else drop this bullet. -->
- **Google Sheets** (sign-up / capacity Sheets) → create from CSV via `Google_Drive.create_file`
  with `contentMimeType: text/csv` (default conversion to a Sheet). If a conversion fails, **alert
  the conductor** and leave the CSV/`.md` ready.
<!-- bootstrap: INCLUDE-IF miro-boards enabled — else drop this bullet. -->
- **Miro boards** (interactive exercise spaces) → built via the Miro **REST API v2** (`curl` /
  `estampar.py`; token from the **`$MIRO_TOKEN` environment variable ONLY, never in a file**); the
  Miro **MCP is read/verify only**. Two conductor gates: reuse-vs-build (Opus), and approve the
  **single-canvas preview (1×1)** before stamping the full grid. Detail in `miro-boards`.
- **Slides** → **local HTML build** (no external sync or hosting): everything lands on disk in
  `{{slides_folder}}/S<NN>-build/`. Per session: (a) the conductor provides a **reference `.pptx`**
  (`{{slides_folder}}/S<NN>-template.pptx`, may change per session, **blocking prerequisite**); (b)
  a Claude agent **extracts the style** from the `.pptx` and builds HTML templates; (c) authors
  each slide's HTML from the slide-spec `.md`; (d) adds a **navigable `index.html`** that works
  from `file://`; (e) after the conductor approves the HTML, exports a **shareable, notes-free
  PDF** per deck (`{{slides_folder}}/S<NN> - <Name>.pdf`, script `export-slides-pdf.sh`).
  *(Conductor prerequisite: the `.pptx` in place. If it is missing, **do not invent a style: alert
  the conductor** and leave the `.md` ready.)*

## 8. Class conventions (for Session-Planning and Slides)

<!-- bootstrap: {{session_shapes}} = one bullet per session-type in course.yaml session_types,
     each giving the type's minute-by-minute timeline shape from the interview/session_briefs.
     Mirror ET §8's virtual / on-site-eval / final shapes as the illustrative pattern, but write
     THIS course's real shapes. State the session length and break policy. -->
**Every session runs {{session_length}} and includes a break.** Session shapes:

{{session_shapes}}

**Timeline rules:** {{timeline_rules}}
<!-- bootstrap: {{timeline_rules}} carries the invariants this course keeps — blocks in multiples
     of 5 min; any sacred/empty opening block (e.g. a Zoom-join block kept content-free); minimum
     exercise duration; break placement; a conservative content-minute ceiling if the course uses
     one. For evaluation-heavy session types, offer the proven heuristic: front-load the
     individual high-stakes work (exam, presentations) and let a flexible late block (e.g. the
     lab's later steps) absorb overruns — never the guidance/teaching block. Keep only the rules
     the interview establishes. -->

**Slides:**
- **Whole-session deck, authored LAST.** Slides are produced *after* the other session artifacts,
  so the deck is the **visual guide of the entire session** — not just the theory. It carries the
  opening/agenda, the teaching blocks (with demo/example highlights from any pack), an
  **exercise-launch slide per exercise** (what to do · what to submit · time · submission
  pointer), and a wrap-up. **Students read the exercises and the slides** — the deck must surface
  the exercise details, not bury them.
- **Light:** something visual, **≤6 lines and ≤6 words/line** (guideline, not a strict rule).
- **"Long blocks" = several small, low-content slides.** Prefer more light slides over few dense
  ones.
- **Speaker notes — per-slide format:** a **header** (`Block · {{schedule_header}} · k/K`) built by
  Opus, and a **body** (key talking points — brief, not paragraphs — + an example + occasional
  humor, max 2–3 humor notes per session) built by Sonnet. **The counter is scoped to the TIME
  WINDOW, not the teaching block:** consecutive slides that share one time range form a *timing
  block* — same time header on every slide, counter `1/K … K/K` (K = slides in that window), reset
  the moment the range changes. This gives the teacher a **fixed target** (how many slides left in
  this window), not a climbing counter over shifting times. Full spec + worked example in the
  `slides` skill.
<!-- bootstrap: {{schedule_header}} = "hh:mm–hh:mm" for a single-schedule course; for a course
     with schedule.sections non-empty use the multi-section form
     "Ⓐ hh:mm–hh:mm · Ⓑ hh:mm–hh:mm · Ⓒ hh:mm–hh:mm · …" — ONE circled letter per entry in
     schedule.sections, in that order (Ⓐ Ⓑ Ⓒ Ⓓ Ⓔ …), however many there are; do not stop at two.
     Note each section's fixed offset from the first. -->

**By session type:** exams and labs have **no** opening/agenda/exercises/slides structure — an exam
is the printable sheet; a lab is a **teacher-led guidance** (instructor script + live demo, no
deck) followed by the step-by-step guide. Only the **class session** has the full slide-deck
structure above.

<!-- ================= INCLUDE-IF class-exercises enabled ================= -->
## 9. Exercise convention (in-class exercises)

- **{{exercises_per_session}} graded in-class exercise(s) per class session**, each **{{exercise_points}}**,
  individual, practical, specific to that session's topic, completed **during class** in a
  {{exercise_block_min}} block. They are **not** project components — they reinforce the session's
  content. Grading: full (complete, on time, genuine engagement) / half (partial or slightly late)
  / 0 (missing or >24h late).
- **Numbered by session.** Each exercise is labeled `<session>.<slot>` (S1 → 1.1 / 1.2, …).
  Use this label in the guides, the plan's specs, the submission columns, and the handover.
  (Filenames stay `S<NN>-ex1.md` / `-ex2.md`.)
- **Each exercise is a written guide** (numbered steps, each producing a submittable result) →
  published as a **Google Doc** via `publish-google-doc`.
- **Submission = {{exercise_submission}}.** {{exercise_submission_detail}}
  <!-- bootstrap: fill from the interview — e.g. "ONE PDF report per exercise uploaded to the
       course portal; the timestamped in-class upload IS the attendance record; the portal has no
       API → the skill REMINDS the conductor to create the assignments." For a Miro-based course,
       exercises may live in Miro instead (see §Miro model). -->
- **Exercise rubrics carry the standard penalties**: the rows of
  `.claude/refs/grading-penalties.md` (in their exercise adaptation) **plus** the lateness row, as
  a penalties block outside the additive 100.
- **Grounded to the topic, realistic in the block.** Each exercise lands on the single most
  important, session-specific topic and is scoped to fit the block right after the teaching block
  that enables it.
<!-- ================= END INCLUDE-IF class-exercises ================= -->

<!-- ================= INCLUDE-IF miro-boards enabled ================= -->
## 9b. Miro model (interactive exercise spaces)

**Tool-agnostic in spirit:** the exercise spaces default to **Miro** but any canvas tool meeting
the conditions below works — the tool is fixed when planning each session. Below, **"space"** = the
per-student board/canvas.

- **One board = one exercise**; each board has **~{{miro_canvases}} identical canvases** (titled
  frames) in a grid. The student **renames their frame with ID + name** (= attendance record) and
  fills the scaffolding (colored cells, top-left text, sticky notes to answer).
- **Organized in Spaces** (`{{miro_spaces}}`). Board **nace suelto** (born loose) → its **name
  carries a compact prefix identifying its Space** (REST limit: name ≤60 chars):
  **`{{miro_board_prefix}}-<Sp>-<xx>-<yy>-<Name>`**; `xx` = session #, `yy` = exercise # (2 digits);
  the long name goes in `description`.
- **The materialization is the final step of `class-exercises`'s own orchestrator** (not a
  separately launched skill). After you validate the spec `.md`, it invokes the `miro-boards`
  engine (`estampar.py`, Haiku tier) to build the **template**, **stops for your approval**
  (single-canvas 1×1 preview before stamping the grid), then **clones** to the sections.
- **Build via the Miro REST API v2** (`curl` / script; token in `$MIRO_TOKEN`, **never in repo
  files**); the **Miro MCP is read/verify only**. **Cloning to sections = `build` per section**
  (same spec, changes `name`); `copy_from`/`clone` does **not** copy content. The **only manual
  step** is the conductor moving each board to its Space. **Any persistent API failure is ALERTED
  to the conductor** and the spec `.md` is left ready.
<!-- ================= END INCLUDE-IF miro-boards ================= -->

## 10. Artifact sequence by session type

The first agent of every session is **Session-Planning**, which creates the handover and defines
which artifacts apply.

<!-- bootstrap: {{artifact_sequences}} = one bullet per session-type, listing the ENABLED skills
     in production order for that type, with each step's publication as its close. Mirror ET §10 /
     TIC §10 but include only enabled skills. Common patterns:
       Class/virtual: Session-Planning → [Examples] → Class-exercises → [Readings] → [Homework]
         → [Project-delivery brief IF due] → Slides (LAST).
       On-site / evaluation: Session-Planning → Exam → Lab → Presentation-guide.
       Final: Session-Planning → Presentation-guide (Final).
       Workshop (if the course has one): Session-Planning → [Readings] → Slides (continuous
         exposition) → Lab-style workshop guide.
     Note each publication close: Examples → none (instructor-only) · Exercises → Google Docs (or
     Miro) · Delivery brief → Google Doc + rubric · Slides → local HTML build + PDF. -->
{{artifact_sequences}}

- **Project-level / course-level artifacts (not tied to one weekly session):**
  {{course_level_artifacts}}
  <!-- bootstrap: list only the enabled course-level skills — e.g. project-delivery (D1–Dn
       briefs + rubrics with the standard penalties block), recap-signup (run ONCE after S1),
       publish-course-docs (Syllabus + briefs to Docs, re-publish when they change). Each has no
       session handover. -->

Special session cases are noted in that session's handover and in `shared-context.md`.

## 11. Artifact close (mandatory)

Before finishing, always:
1. **Write the artifact** in its per-type folder (per `naming.folders`).
2. **Update `handover-S<NN>.md`:** check your checklist box, leave notes for the next orchestrator
   (decisions, pendings, what it needs to know).
3. **Add new lessons** to `shared-context.md` (only what helps future sessions: tier calibration,
   conventions you discovered, traps).
4. **Record new decisions** in `{{sources_folder}}/{{sources.decisions}}` (D1+).
5. **Emit the closing block** (see template `.claude/refs/templates/next-agent-prompt.md`):
   - a **short summary for the human** (what you produced, what to validate, decisions made), and
   - the **PROMPT FOR THE NEXT AGENT**, ready to copy. The next skill comes from the artifact
     sequence for this session type (§10) — do not hardcode a specific next slug.

<!-- ================= INCLUDE-IF examples enabled ================= -->
## 12. Examples/demos convention (instructor demo & examples pack)

- **One pack per class session** in `{{examples_folder}}/S<NN>/` (**one numbered `NN-<slug>.md`
  per demo/example** + a `00-index.md`), produced by the `examples` skill **after Session-Planning**
  (2nd artifact), ahead of the Exercises and the (last) Slides that reference it. It is
  **instructor-only — never published** (no Google Doc). Every teaching block is **"concept + live
  demo"**: the pack holds the **depth the light slides can't** — the demos the instructor *runs
  live* and the worked examples they *show* — so Slides and Exercises **reference** these instead of
  re-inventing.
- **Driven by the plan's Examples manifest** (§ Session-Planning): per sub-block, a **live-demo**, a
  **worked-example**, or theory-only. Each **live-demo script** is runnable (goal · setup · steps ·
  expected · **live-failure fallback**). Plus an **exemplar** per exercise (use a *different*
  scenario than the live demos so students can't copy the demo answer).
<!-- bootstrap: INCLUDE-IF tool_stack.ollama_forced_failure is true — else DROP this bullet. -->
- **Forced-failure demos (special technique).** Some beats need the tool to *fail*, which the real
  tool won't reliably do in class. The easy path is a **small local model** (e.g. ollama
  `llama3.2:1b` / `qwen2.5:0.5b`) at a **small `num_ctx`** so the break happens fast and
  reproducibly, plus the recovery. The skill only **guides** this (which model, what setting) — it
  does **not** install anything, **ollama is optional**, and such a model is **instructor-only,
  never** presented to students as a tool they use. The lead authors the forced-failure recipe
  file itself (exact turns, probe, `num_ctx` values, reference break transcript).
<!-- ================= END INCLUDE-IF examples ================= -->
