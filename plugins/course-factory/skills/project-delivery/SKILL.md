---
name: project-delivery
description: >
  Formal project-delivery brief + grading rubric for one delivery of a course's project arc, in
  the course-factory material-production harness. Produces `<folders.project>/D<n>-brief.md`
  (the student-facing brief, required-elements checklist, and embedded rubric tables) plus
  `D<n>-rubric.json`/`.xlsx` via the plugin `evaluation-rubrics:rubric-creator`, with the
  course's `.claude/refs/grading-penalties.md` injected as the penalties block, then publishes
  the brief as a Google Doc. Project-LEVEL artifact, not tied to one weekly session. Invoke
  DELIBERATELY within a course material-production pipeline (the working folder has
  `.claude/refs/course.yaml`) to author one delivery `D<n>`; do NOT auto-trigger for generic
  assignment/brief/rubric requests.
---

# Project delivery (formal brief + rubric)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder names,
> enabled artifacts, tool stack, publishing targets); (3) read `.claude/refs/PROTOCOL.md` — the
> course's contract, including its project-delivery arc (count of deliveries, what each covers,
> due dates, points, which checkpoint presents which delivery); (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md` if it exists, and any prior delivery handovers; (5)
> read `.claude/refs/shared-context.md`. If `project-delivery` is not in `artifacts.enabled`,
> STOP and warn the conductor. Write ALL generated content in `course.language`. You are launched
> **for one delivery `D<n>`** (from the launch prompt).

**Tier:** Opus (you orchestrate and judge) · Sonnet (drafts the brief) · Haiku/Bash (materializes
the rubric by running `generate_rubric.py` from the plugin `evaluation-rubrics`).

## What you produce

In `<folders.project>/` (per `course.yaml naming.folders.project`), for the delivery `D<n>` you
were launched for:

1. **`D<n>-brief.md`** — the formal delivery brief for the student (what's due, the
   required-elements checklist, how it's graded), with the rubric embedded as tables at the end.
   This is what gets published as a Google Doc.
2. **`D<n>-rubric.json`** — the rubric source (2–3 broad criteria + `penalties`).
3. **`D<n>-rubric.xlsx`** — the grading rubric (produced by `generate_rubric.py`).

## Inputs

- `<folders.sources>/<sources.session_briefs>` — the course's per-delivery table ("what must
  exist" per `D<n>`) and its project-delivery grading section, plus that delivery's originating
  session(s). **This is your contract for the required elements.**
- `<folders.sources>/<sources.syllabus>` — the delivery schedule (due dates, what feeds which
  checkpoint) and the late-submission policy.
- `<folders.sources>/<sources.glossary>` — shared vocabulary for the course's audience; define
  terms consistently, do not redefine.
- `.claude/refs/PROTOCOL.md` / `<sources.decisions>` — the settled delivery arc: how many
  deliveries, points each, and which checkpoint presents which delivery (per the course's
  evaluation model — do not hardcode a specific count or point value; read it from the course's
  own contract).

## Process

1. **Formal brief (Sonnet).** From the delivery table's "what must exist" for `D<n>`, draft a
   clean, self-contained brief matching the course's audience register, with:
   - **Title + delivery information** (which delivery, due date — per `<sources.syllabus>` /
     `course.yaml schedule` — points, where it is presented, per the course's checkpoint↔delivery
     map).
   - **What this delivery is** (1–2 paragraphs) and **how it builds on prior deliveries** — most
     delivery arcs are cumulative; state what must already exist and what this one adds.
   - **Required elements — checklist**, from "what must exist": each element a checkable line the
     student can self-verify.
   - **How it connects to the sessions** leading up to it (reference the session overview blocks;
     do not duplicate them).
   - **Submission mechanism** — per the course's contract (e.g. a repo update + summary document,
     or a portal upload); do not invent a mechanism not stated in the course's sources.
   - **Late policy pointer** → the syllabus's late-delivery terms. Reference, don't restate in
     full.
   - **Academic-integrity reminder**, if the course's grading-penalties block includes one — the
     student must be able to explain everything they submit.
2. **Rubric (engine `evaluation-rubrics:rubric-creator`).** The delivery needs an analytic
   rubric. Author the JSON yourself and run it through the plugin script:
   - **2–3 BROAD additive criteria** summing to **100** (not one criterion per checklist item) —
     typically (a) the core evidence/product (does the required build exist and work) and (b)
     quality/iteration/spec fidelity. Split into a third criterion only if the delivery clearly
     warrants it. Descriptors in `course.language`, 3 levels — Meets (100%) exhaustive & specific
     · Partially meets (60%) substantial-but-incomplete, name the gap · Does not meet (0%) absent
     or fundamentally wrong. Criterion names 3–6 words, formal register.
   - **Weights MUST sum to 100** (hard assert in `generate_rubric.py`). The rubric is out of 100;
     any category weight from `course.yaml evaluation.weights` is applied separately in the
     grades book — do not encode it here.
   - **Standard penalties (ALWAYS).** Inject the course's standard penalties block. **Single
     source:** `.claude/refs/grading-penalties.md` — copy its rows into the JSON `penalties`
     field (do not reinvent). The plugin renders them as a labeled block below the additive
     table, outside the 100 (so `sum==100` still holds). When invoking the plugin, state
     explicitly these are penalties, not additive criteria.
   - **Materialize:** write `D<n>-rubric.json` with this schema, then run the script. ⚠️ The
     descriptor keys are literally `cumple` / `parcial` / `no_cumple` regardless of language —
     `generate_rubric.py` reads those exact keys (direct dict access; any other name crashes it);
     `language` only switches the rendered column headers.
     ```json
     {
       "language": "en",
       "criteria": [ {"name":"…","cumple":"…","parcial":"…","no_cumple":"…","pts": 60}, … ],
       "penalties": [
         {"name":"…","cumple":"…","parcial":"…","no_cumple":"…","penalty":"-15"},
         {"name":"…","cumple":"…","parcial":"N/A","no_cumple":"…","penalty":"-100%"}
       ]
     }
     ```
     ```bash
     # locate the installed script (search SCOPED to plugins, never `find /`):
     RC=$(find "$HOME"/.claude*/plugins -path "*rubric-creator/scripts/generate_rubric.py" 2>/dev/null | sort -V | tail -1)
     python "$RC" <folders.project>/D<n>-rubric.json <folders.project>/D<n>-rubric.xlsx
     ```
     *(You may instead invoke the skill `evaluation-rubrics:rubric-creator`; its "review in chat"
     step does not apply here — the conductor's md-first gate below IS the approval. Produce the
     files and finish.)*
   - **If the script fails** (missing `openpyxl` → `pip install openpyxl`; weights ≠ 100 → fix
     the JSON and retry; script not found), alert the conductor and leave the `.md` with both
     tables ready anyway.
3. **Embed the rubric in the brief.** At the end of `D<n>-brief.md` put two tables: (a) the
   additive rubric (Criterion · Meets · Partially meets · Does not meet · Pts, sums to 100) and
   (b) the penalties block "scored negatively" (from `.claude/refs/grading-penalties.md`), so the
   student sees both in the Google Doc. In the `.xlsx`, `generate_rubric.py` writes both in one
   pass.
4. **Audit (judge).** Verify against the Acceptance criteria before accepting Sonnet's draft;
   iterate or redo if it fails.

## Publication (this skill owns its pipeline end-to-end)

After the **human validates** the `.md`, publish the brief via the `publish-google-doc` engine
(into the `<folders.project>/` Drive subfolder per `publishing.drive.subfolders`). The `.xlsx`
rides Drive sync — it is a local file in the synced course folder, so it already reaches Drive.
**Do NOT re-upload it** (a second upload duplicates it). The `.json` stays as the editable
source. Follow `publish-google-doc`'s delegation and format conventions as written there.

## Acceptance criteria

- [ ] `D<n>-brief.md` — formal, self-contained brief whose required-elements checklist matches
      that delivery's "what must exist" in the course's session-briefs source.
- [ ] The cumulative nature is explicit where the course's delivery arc is cumulative (what must
      already exist + what this delivery adds), and where it is presented is stated per the
      checkpoint↔delivery map.
- [ ] Submission mechanism and late-policy pointer stated, matching the course's own sources —
      not invented.
- [ ] Rubric generated (`.json` + `.xlsx`): 2–3 broad criteria, weights sum to 100.
- [ ] Standard penalties block included, copied verbatim from `.claude/refs/grading-penalties.md`,
      as a separate "scored negatively" table.
- [ ] Both the additive rubric and the penalties block appear as tables at the end of the `.md`.

## Close

1. Write the three files in `<folders.project>/`; self-audit.
2. **Human gate (md-first):** the conductor validates the brief + rubric. End the turn with a
   summary; do not publish until the green light.
3. **Publish** the brief to a Google Doc (`.xlsx` rides sync — do not re-upload).
4. Record the delivery + link in the relevant handover and `<folders.sources>/<sources.decisions>`,
   add any lessons to `.claude/refs/shared-context.md`, then emit the closing block per
   `.claude/refs/templates/next-agent-prompt.md`: a short summary for the conductor, then the
   PROMPT FOR THE NEXT AGENT — the next artifact in the course PROTOCOL's sequence for the
   session this delivery lands in (e.g. slides for that session, if slides are authored last), or
   if this was a standalone/up-front run, let the conductor choose the next delivery or the next
   session's planning.
