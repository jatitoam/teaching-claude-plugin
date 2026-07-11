---
name: presentation-guide
description: >
  Student-facing presentation guide + grading rubric for a project checkpoint or final
  presentation, in the course-factory material-production harness. Produces
  `<folders.project>/<name>-guide.md` (what to show, timing, automatic-zero conditions, with the
  rubric embedded as tables) plus `<name>-rubric.json`/`.xlsx` via the plugin
  `evaluation-rubrics:rubric-creator`, with the course's `.claude/refs/grading-penalties.md`
  injected as the penalties block, then publishes the guide as a Google Doc. Invoke DELIBERATELY
  within a course material-production pipeline (the working folder has
  `.claude/refs/course.yaml`) for one checkpoint/final; do NOT auto-trigger for generic
  presentation-guide or rubric requests.
---

# Presentation guide (checkpoint / final + rubric)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder names,
> enabled artifacts, tool stack, publishing targets); (3) read `.claude/refs/PROTOCOL.md` — the
> course's contract, including which sessions carry a checkpoint/final and what each one
> presents (per the delivery↔presentation map); (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md` if it exists; (5) read
> `.claude/refs/shared-context.md`. If `presentation-guide` is not in `artifacts.enabled`, STOP
> and warn the conductor. Write ALL generated content in `course.language`. You are launched for
> **one** checkpoint or the final presentation (from the launch prompt).

**Tier:** Sonnet (drafts the guide) → Opus (you calibrate and judge) · Haiku/Bash (materializes
the rubric by running `generate_rubric.py` from the plugin `evaluation-rubrics`).

## What you produce

In `<folders.project>/` (per `course.yaml naming.folders.project`), for the presentation you were
launched for:

1. **`<name>-guide.md`** (e.g. `checkpoint-1-guide.md`, `final-guide.md` — name from the launch
   prompt / the course's session-type vocabulary) — the student-facing guide (what to show,
   timing, automatic-zero conditions), with the rubric embedded as tables at the end. Published
   as a Google Doc.
2. **`<name>-rubric.json`** — the rubric source (2–3 broad criteria + `penalties`).
3. **`<name>-rubric.xlsx`** — the grading rubric (produced by `generate_rubric.py`).

## Inputs

- `<folders.sources>/<sources.session_briefs>` — the checkpoint/final presentation section for
  this presentation (points, required elements, timing, automatic-zero conditions). **This is
  your contract.**
- The delivery this presentation shows — per the course's delivery↔presentation map in
  `.claude/refs/PROTOCOL.md` / `<sources.decisions>` (e.g. a checkpoint presents the last
  delivered project milestone; the final presents the completed project). Read that delivery's
  `D<n>-brief.md` if it exists.
- `<folders.sources>/<sources.glossary>` — shared vocabulary for the course's audience.

## Process

1. **Guide (Sonnet).** Draft a clean, student-facing guide with:
   - **Presentation information** (which checkpoint/final, session, points — per
     `course.yaml evaluation.weights`) and **what it presents** (the delivery above) — state
     explicitly that it is a **live demonstration**, not a reading of the delivery document.
   - **Required elements to show** — per the course's session-briefs section for this
     presentation: typically a live working demo, at least one concrete moment demonstrating the
     course's tool stack in use, one trade-off navigated, and what's next. A final presentation
     commonly adds deeper elements (e.g. a public-URL demo, a couple of live interaction
     exchanges, an "under the hood" explanation moment, a business/technical case) — take the
     exact list from the course's own source, do not assume ET's or any other course's specific
     checklist.
   - **Timing** — per the course's session-briefs / PROTOCOL.md timeline for this session type;
     do not hardcode a specific number of minutes.
   - **Automatic-zero conditions** (state prominently) — per the course's grading section: e.g. a
     product that does not run, or that the student cannot explain, does not earn full credit;
     the final commonly escalates this to an automatic zero. Take the exact conditions from the
     course's own source.
   - **What this course grades** — build + technical depth, or whatever the course's evaluation
     model states; if another course shares the same presentation slot for a different grading
     layer, reference that only — do not assume its split.
2. **Rubric (engine `evaluation-rubrics:rubric-creator`).** The presentation needs an analytic
   rubric.
   - **2–3 BROAD additive criteria** summing to **100** (not one per checklist item) — typically
     (a) working live demo, (b) technical depth/explanation, and (c) communication/business case.
     Merge to 2 if a criterion is thin. Descriptors in `course.language`, 3 levels — Meets (100%)
     · Partially meets (60%, name the gap) · Does not meet (0%). Criterion names 3–6 words,
     formal register.
   - **Weights MUST sum to 100** (hard assert). Any category weight from
     `course.yaml evaluation.weights` is applied separately in the grades book — do not encode it
     here.
   - **Standard penalties (ALWAYS).** Inject the course's standard penalties block. **Single
     source:** `.claude/refs/grading-penalties.md` — copy its rows into the JSON `penalties`
     field. The plugin renders them as a labeled block below the additive table, outside the 100.
     State explicitly these are penalties, not additive criteria. (The automatic-zero conditions
     above commonly map onto a −100% penalty row.)
   - **Materialize:** write `<name>-rubric.json` with this schema, then run the script. ⚠️ The
     descriptor keys are literally `cumple` / `parcial` / `no_cumple` regardless of language;
     `language` only switches the rendered column headers.
     ```json
     {
       "language": "en",
       "criteria": [ {"name":"…","cumple":"…","parcial":"…","no_cumple":"…","pts": 40}, … ],
       "penalties": [
         {"name":"…","cumple":"…","parcial":"…","no_cumple":"…","penalty":"-15"},
         {"name":"…","cumple":"…","parcial":"N/A","no_cumple":"…","penalty":"-100%"}
       ]
     }
     ```
     ```bash
     RC=$(find "$HOME"/.claude*/plugins -path "*rubric-creator/scripts/generate_rubric.py" 2>/dev/null | sort -V | tail -1)
     python "$RC" <folders.project>/<name>-rubric.json <folders.project>/<name>-rubric.xlsx
     ```
     *(You may instead invoke `evaluation-rubrics:rubric-creator`; its "review in chat" step does
     not apply here — the conductor's md-first gate below IS the approval.)*
   - **If the script fails** (missing `openpyxl`, weights ≠ 100, script not found), alert the
     conductor and leave the `.md` with both tables ready.
3. **Embed the rubric in the guide.** At the end put two tables: (a) the additive rubric (sums
   to 100) and (b) the penalties block "scored negatively" (from
   `.claude/refs/grading-penalties.md`). `generate_rubric.py` writes both into the `.xlsx` in one
   pass.
4. **Calibrate & audit (Opus).** As lead, verify the required elements, timing, and
   automatic-zero conditions match the course's session-briefs section exactly; iterate or redo
   if the draft drifts.

## Publication (this skill owns its pipeline end-to-end)

After the **human validates** the `.md`, publish the guide via the `publish-google-doc` engine
(into the `<folders.project>/` Drive subfolder). Record the link/ID in the handover. The `.xlsx`
rides Drive sync — a local file in the synced course folder already reaches Drive. **Do NOT
re-upload it.** The `.json` stays as the editable source.

## Acceptance criteria

- [ ] The correct `<name>-guide.md` is produced, and its required elements match the course's
      session-briefs section for this presentation exactly.
- [ ] **Timing correct** per the course's own timeline for this session type.
- [ ] **Automatic-zero conditions stated**, matching the course's grading section.
- [ ] Rubric generated: 2–3 broad criteria, weights sum to 100, plus the standard penalties block
      from `.claude/refs/grading-penalties.md`.
- [ ] Both tables (additive rubric + penalties) appear at the end of the `.md`.

## Close

1. Write the three files in `<folders.project>/`; self-audit.
2. **Human gate (md-first):** the conductor validates the guide + rubric. End the turn with a
   summary; do not publish until the green light.
3. **Publish** the guide to a Google Doc (`.xlsx` rides sync — do not re-upload).
4. Update the handover (link, which presentation) and `<sources.decisions>`, add lessons to
   `.claude/refs/shared-context.md`, then emit the closing block per
   `.claude/refs/templates/next-agent-prompt.md`: a short summary, then the PROMPT FOR THE NEXT
   AGENT — a checkpoint guide typically closes an on-site session's artifact sequence (next =
   session-planning for the next session per PROTOCOL.md); the final guide typically closes the
   course (no next session) — follow whichever the course PROTOCOL's artifact sequence states.
