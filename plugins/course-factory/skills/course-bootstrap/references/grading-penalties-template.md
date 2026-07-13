<!--
  GRADING-PENALTIES TEMPLATE — course-factory / course-bootstrap
  ===============================================================
  Copied into <course>/.claude/refs/grading-penalties.md. The bootstrap interview picks WHICH
  standard penalty rows apply and adapts their wording to the course (submission channel, grouping,
  integrity rule) and to course.language. DELETE every <!-- bootstrap: ... --> comment from the
  generated file. This is the SINGLE SOURCE for penalties: rubric-bearing skills inject it as the
  JSON `penalties` array (evaluation-rubrics:rubric-creator), OUTSIDE the additive 100.
-->
# Standard penalties ({{penalty_scope_list}}) — scored negatively

> **Single source.** The rubric-bearing skills ({{penalty_skill_list}}) inject this block into
> **every** rubric, in addition to the additive rubric (criteria = steps, summing to 100). These
> elements **only subtract points if NOT met** — they do not add. They do **not** go inside the
> additive 100 (the plugin's `generate_rubric.py` requires the weights to sum to 100); they render
> as a **separate table** in the brief/guide and as a **labeled block** below the rubric in the
> `.xlsx`. When invoking `evaluation-rubrics:rubric-creator`, **say so explicitly**: these rows are
> **penalties**, not additive criteria (pass them in the JSON `penalties` field).

<!-- bootstrap: {{penalty_scope_list}} / {{penalty_skill_list}} = the graded-artifact types + the
     enabled rubric-bearing skill slugs for this course (e.g. project deliveries, labs, in-class
     exercises; project-delivery, lab, class-exercises, presentation-guide). -->

## Canonical block

**Penalties — scored negatively (only lower the grade if not met):**

<!-- bootstrap: keep the rows the interview selects; adapt each "Meets / Does not meet" cell to the
     course's real submission channel and integrity rule; localize to course.language; set the
     penalty magnitudes the conductor confirms. The three rows below are the common options. -->

| Criterion | Meets | Partially meets | Does not meet | Penalty |
|---|---|---|---|---|
| **{{presentation_row_name}}** | Professional, appropriate write-up. Includes a cover page. PDF format. | Good write-up, no cover page. | Sparse write-up, or a format other than PDF. | **−{{presentation_penalty}}** · scored negatively |
| **{{accessible_row_name}}** | {{accessible_meets}} | N/A | {{accessible_fails}} | **−100 %** · invalid if not met |
| **{{integrity_row_name}}** | {{integrity_meets}} | N/A | {{integrity_fails}} | **−100 %** · invalid if not met |

<!-- bootstrap: examples of the three rows' cells to adapt —
  presentation ("Good presentation", −15): a deduction, not a validity condition.
  accessible ("Accessible submission" / "Archivo adjunto", −100%): Meets = "the work is submitted
    where the instructor can open it" (adapt to channel: a shared repo + PDF summary; an attached
    PDF file; a PDF uploaded to the portal assignment). Does not meet = the instructor cannot
    review it → 0.
  integrity ("AI declared & explainable" / "Marco de IA", −100%): Meets = AI-assisted work is
    referenced AND the student can explain every piece submitted. Does not meet = AI used and not
    declared, or the student cannot explain the submission → 0.
-->

## Semantics (for grading)

- **{{presentation_row_name}} (−{{presentation_penalty}}):** a deduction from the grade. Partial
  (no cover) = smaller deduction; "does not meet" (sparse or non-PDF) = up to the full magnitude.
- **{{accessible_row_name}} (−100 %):** a validity condition. If the instructor cannot open the
  work, it **cannot be graded** → 0.
  <!-- bootstrap: INCLUDE-IF class-exercises enabled — the in-class exercise adaptation. -->
  - **Exercise adaptation:** exercises are submitted as {{exercise_submission_short}}, so this row
    reads — **Meets:** the report is submitted through the required channel and opens correctly
    (text and screenshots legible). **Does not meet:** the file is missing, corrupt, unreadable, or
    submitted anywhere else → the instructor cannot review it → 0.
- **{{integrity_row_name}} (−100 %):** a validity condition tied to the course's **academic
  integrity** rule. Using AI is the core skill — but submitting work the student cannot explain, or
  not declaring AI-generated material, makes the work **invalid** → 0, with no resubmission.

## Scope

<!-- bootstrap: list the enabled rubric-bearing artifact types and which skill always adds the
     block; note any grouping (individual vs. group cover page) and any extra rows (e.g. the
     exercise lateness row: in class = full · <24h = half · >24h = 0). -->
- Applies to **{{scope_deliveries}}** — skill `{{scope_delivery_skill}}` always adds it.
- Applies to **{{scope_labs}}** — skill `lab` always adds it{{lab_group_note}}.
<!-- bootstrap: INCLUDE-IF class-exercises enabled. -->
- Applies to **all in-class exercises**: each is submitted as {{exercise_submission_short}}. Skill
  `class-exercises` always adds it — using the **exercise adaptation** above — **plus** the exercise
  **lateness row** (in class = full · <24h = half · >24h = 0, PROTOCOL §9) in the same penalties
  block.
<!-- bootstrap: INCLUDE-IF homework enabled. -->
- Applies to **homework/take-home assignments** — skill `homework` always adds it, adapted to the
  homework submission channel ({{homework_submission_short}}) and the course's late-submission rule.
- Reusable by other graded artifacts submitted with a cover in PDF, if the conductor decides.
  Editing here = changes everywhere.
