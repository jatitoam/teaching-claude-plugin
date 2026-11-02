---
name: practical-exam
description: Produces the practical part of a partial/term exam — a live, integrated challenge with no explicit steps, plus a criteria-based rubric. Part of the course-factory harness pipeline for building university course material. Invoke DELIBERATELY within a course material-production pipeline (the working folder has .claude/refs/course.yaml), typically after the concept-check exam of the same evaluation; do NOT auto-trigger for generic exam, challenge, or assessment requests.
---

# Practical exam (live integrated challenge)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder
> names, enabled artifacts, tool stack, publishing targets); (3) read
> `.claude/refs/PROTOCOL.md` — the course's contract; (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md` if it exists; (5) read
> `.claude/refs/shared-context.md`. If `practical-exam` is not in `artifacts.enabled`, STOP and
> warn the conductor. Write ALL generated content in `course.language`.

**Tier:** Sonnet (drafts) · **Opus (calibration and judge — this is delicate).**

## What you produce

**`<folders.exams>/P<n>-practical.md`** (or `S<NN>-practical-exam.md`, per the course's exam
naming convention) — the practical part of an evaluation, worth the larger share of that
evaluation's weight per `course.yaml evaluation.weights`. Lab-like in format, but with **no
explicit step-by-step guidance**: it evaluates whether the student knows what to do *without*
being told step by step. Resolved live, in the session, on paper and/or machine depending on the
challenge — per the course's AI-use policy in its sources/PROTOCOL (the course's semáforo or
equivalent declaration convention).

## Key difference vs. a lab

A lab **guides**; the practical exam **poses the challenge and the expected result, not the
steps**. The student decides the "how." Calibrating difficulty is the delicate part of this
skill — that is why it runs at the Opus tier, not Sonnet: Sonnet drafts the scenario and rubric,
Opus calibrates and judges whether the difficulty is right.

## Inputs (read, don't duplicate)

- Content from the covered sessions (`<folders.planning>/`, readings, labs of those sessions).
- The sibling concept-check exam for this same evaluation (so the two don't overlap and their
  weights balance per `course.yaml evaluation.weights`).
- Any prior-year practical exams the course PROTOCOL points to, as a level reference (evaluate
  and keep what serves; never copy wholesale).

## Process

1. **(Opus) Define the integrated challenge.** Design a realistic, integrated challenge scoped
   to the covered sessions' content (e.g. build/configure/reason through something that draws on
   multiple topics at once) — this design and difficulty decision belongs to Opus, not Sonnet.
2. **Delegate to Sonnet** the draft of:
   - **Business/technical scenario** + **expected deliverable** (what must exist at the end).
   - **Constraints** (tool, time, and the AI-use declaration per the course's AI-use policy in
     its sources/PROTOCOL).
   - **Rubric by criteria (not by steps):** functionality/outcome, judgment/decisions made, and
     the ability to **explain and defend** those decisions.
   - **NO step-by-step instructions.** At most, minimal hints if the challenge is very open-ended.
3. **Opus judges:** Is it achievable in the available time? Does it actually discriminate
   between students who understand the material and those who don't? Does the rubric evaluate
   judgment, not just the end result?

## Acceptance criteria

- [ ] Clear challenge with an expected deliverable, **no steps given**.
- [ ] Achievable within the session's time; difficulty calibrated (neither trivial nor
      impossible) — Opus signed off on this calibration.
- [ ] Rubric is criteria-based, and includes an "explain/defend" criterion.
- [ ] Weight matches `course.yaml evaluation.weights` for this evaluation's practical share;
      complements (does not overlap) the sibling concept-check exam.
- [ ] AI-use constraints stated per the course's AI-use policy in its sources/PROTOCOL.

## Publication (this skill owns its pipeline end-to-end)

After the **human validates** the `.md`:

- **Publish** each student-facing statement (one Doc per case/version when the exam has several)
  via the `publish-google-doc` engine, into the exams Drive subfolder per
  `publishing.drive.subfolders`. Rubric keys and conductor notes are never published for students.
  Record every Doc ID in the handover together with the `.md` it was published from.
- **Print format (last step — AUTOMATIC, do not ask):** read `course.yaml →
  publishing.practical_print.base_doc` (the sample practical exam the conductor provided at
  bootstrap).
  - **Non-empty →** right after publishing, run the `practical-exam-print-format` skill on **each
    published statement Doc**, without asking the conductor (brief each agent with the Doc ID, the
    exact per-Doc `.md` it was published from, and that skill's folder path): one Sonnet agent per Doc,
    **sequentially** (they share the browser), each verified by you per that skill's §Orchestrator
    verification (text fingerprint against its source `.md`, plus the Title-space and last-page
    checks the export cannot show) before launching the next. Record in the handover that each Doc
    is print-ready (or what failed). If a run reports «base_doc is not a formatted practical-exam
    sample», **stop the remaining runs** — the same base would fail every Doc — and report it.
  - **Empty or absent →** skip it, and say so in the closing summary in one line («print format
    skipped: no sample practical exam was provided at bootstrap — add
    `publishing.practical_print.base_doc` to enable it»). Never invent or pick a base Doc yourself.
- **If a statement is republished later**, its formatting is lost: run the print format again on
  the new Doc and ask the conductor to trash the old one.

## Close

1. Write the `.md` and self-audit against the acceptance criteria.
2. **Human gate (md-first):** the conductor validates the `.md`. *(End the turn with a summary;
   do not publish until the green light.)*
3. **Publish** via the `publish-google-doc` engine (into the exams Drive subfolder per
   `publishing.drive.subfolders`). Then, automatically, apply **`practical-exam-print-format`** to
   each statement Doc when `publishing.practical_print.base_doc` is set (see §Publication).
4. **Update the handover** (check the practical-exam box; note the Doc link), **add lessons** to
   `shared-context.md` (tier calibration, calibration traps), **record decisions** in
   `<folders.sources>/<sources.decisions>` if any were made, and **emit the closing block** per
   `templates/next-agent-prompt.md`: a human summary, then the PROMPT FOR THE NEXT AGENT — the
   next artifact slug comes from the course PROTOCOL's artifact sequence for this session type
   (do not hardcode a specific next slug).
