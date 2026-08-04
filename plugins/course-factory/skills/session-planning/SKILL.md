---
name: session-planning
description: Produces a course session's master plan (planning/S<NN>-plan.md) — the timeline, teaching-block breakdown, downstream artifact specs, and (when enabled) the Examples manifest — plus the session handover. Part of the course-factory harness pipeline for building university course material; it is always the FIRST agent of a session. Invoke DELIBERATELY within that pipeline (the working folder has .claude/refs/course.yaml); do NOT auto-trigger for generic planning, agenda, or scheduling requests.
---

# Session planning

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor folder
> containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder names, enabled
> artifacts, tool stack, publishing targets); (3) read `.claude/refs/PROTOCOL.md` — the course's
> contract; (4) read your session handover `.claude/refs/handovers/handover-S<NN>.md` if it exists;
> (5) read `.claude/refs/shared-context.md`. If `session-planning` is not in `artifacts.enabled`,
> STOP and warn the conductor. Write ALL generated content in `course.language`.
>
> As the Planning agent, **YOU create** the session handover — no earlier skill does.

**Tier:** Opus (you; not delegated — planning is judgment, not bulk work). **You are the FIRST
agent of every session.**

## What you produce

- `<folders.planning>/S<NN>-plan.md` (typically `planning/S<NN>-plan.md` — the exact folder name
  comes from `course.yaml naming.folders.planning`) — the **master plan**: the **contract**
  consumed by every downstream artifact skill enabled for this course (`artifacts.enabled`) that
  applies to this session's type. When `examples` is enabled, the plan also carries the
  **Examples manifest** (see Process step 6).
- `.claude/refs/handovers/handover-S<NN>.md` — created from `.claude/refs/templates/handover-session.md`;
  you fill the header and the checklist rows for the session type.

## Inputs (read, don't duplicate)

1. `<folders.sources>/<sources.session_briefs>` → **your session's brief** (topics, teaching
   blocks, drafted exercises, and whichever of lab/exam/checkpoint/delivery applies) plus the
   course's session-shape reference (PROTOCOL.md — see §Process step 2).
2. `<folders.sources>/<sources.syllabus>` → structure, weighting, policies.
3. `<folders.sources>/<sources.glossary>` → shared vocabulary (enrich if a new core term appears).
4. `.claude/refs/shared-context.md` → conventions and accumulated lessons.
5. `<folders.sources>/<sources.decisions>` → decisions log.
6. *(Optional, for technical/hands-on courses)*
   `${CLAUDE_PLUGIN_ROOT}/skills/course-bootstrap/references/pdds-salvage/session-structure.md`
   — proven outline-design principles and block+demo styles (live-coding companion vs. classic),
   and `.../pdds-salvage/defect-checklist.md` — per-deliverable defect gates worth adapting into
   the plan's downstream artifact specs.

If the course protocol defines a mandatory review of prior-year/prior-offering material before
planning (some courses require this — check PROTOCOL.md §2/§4), follow it: for each element decide
explicitly reuse / adapt / reconstruct / new, and record the verdict in the plan's notes, with an
exact pointer (path or design ID) per source in the handover so downstream skills don't re-search.
Match prior-offering sources by **topic/title, never by session number alone** (offerings drift:
sessions get reordered, titles reworded), and treat every match as **PROPOSED until the conductor
confirms it**: mark it "proposed/unconfirmed" in the plan and the handover's sources table, and
surface it prominently in your closing summary so the conductor confirms or corrects it at the
md-first gate. Downstream agents use only conductor-confirmed pointers.

## Process

1. **Determine the session type** from `course.yaml schedule.session_types` (the set of type names
   and which session numbers belong to each is per-course) and any **special case** flagged in the
   brief or PROTOCOL.md (e.g. an opening session with no recap, a session whose lab/homework is
   take-home, a delivery due or presented this session). Resolve deliverable-timing questions
   (what's due, what's presented) from the course's decisions log / PROTOCOL, never invent one.
2. **Pick the correct timeline SHAPE for the session type** from `PROTOCOL.md`'s session-shapes
   section (§8 in the ET/TIC harnesses; the shapes — block names, minutes, sacred/empty blocks,
   break placement — are course-specific, not hardcoded here) and lay it out in blocks (minutes in
   **multiples of 5**, per the course's timeline rules). If `schedule.sections` is non-empty, the
   timeline table carries one start–end column per section — **one per configured entry, however
   many there are** — each derived from its section's start time. Respect any "sacred" block the protocol defines (e.g. an empty join/setup
   block at the very start) and the mandated break.
3. **Choose the AI tool(s) featured this session** with a one-line reason, per `tool_stack` and any
   per-session tool-adoption sequence the course defines (e.g. "tool X enters from session N").
   Record the choice — and, when the course assigns a per-activity AI-permission level (a
   "semáforo"/traffic-light or similar mechanic — check PROTOCOL.md), the levels for this session's
   activities — in the handover.
4. **Break each teaching block into thematic sub-blocks**, each with **name · minutes ·
   points-to-cover**. This is exactly what the `slides` skill converts into slide groups — make it
   actionable. If the course's pedagogy is "concept + live demo" per block, note for each sub-block
   which points are *taught* vs. *shown live* (step 6 turns the "shown live" beats into the
   Examples manifest).
5. **Spec the in-class exercises**, only if `class-exercises` is in `artifacts.enabled`. Pull the
   drafted exercises for this session from the session brief, then **re-review** each against the
   finalized teaching blocks: each must be grounded in the session's most important topic, fit its
   allotted block right after the teaching block that enables it, and produce a **submittable
   result**. Adjust or replace if the drafted version no longer fits. **Label them
   `<session>.<slot>`** (e.g. session 3 → 3.1 / 3.2), matching the session-brief numbering and the
   course's exercise convention (PROTOCOL.md). Note the exercise count and duration per the
   course's own rules — do not assume a fixed number or length; read them from PROTOCOL.md /
   the brief for this session type.
6. **Plan the demos & examples per block → the Examples manifest**, only if `examples` is in
   `artifacts.enabled`. If the course's pedagogy pairs each teaching block with a live demo or
   worked example, decide for each sub-block whether it carries a **live-demo**, a
   **worked-example**, or is theory-only — aim for a demo/example to accompany each slide group
   where it makes sense (most of them), while keeping enough theory that a block is never all demo.
   This becomes the contract the `examples` skill consumes, so depth lives in an instructor-only
   pack and the slides stay light. For each item give: a **label**, the **sub-block or exercise**
   it supports, the **kind** (`live-demo` | `worked-example` | `exercise-exemplar`), the
   **surface/type** (tool/medium used), **what it shows**, and whether **slides** should reference
   it. Add a **model answer (`exercise-exemplar`)** for each exercise spec'd in step 5.
   **Forced-failure beats:** if `tool_stack.ollama_forced_failure` is true and a lesson depends on
   a tool behavior that's hard to reproduce live reliably, flag a special reproduction technique
   (instructor-only; never a student tool) — per PROTOCOL.md's guidance for this course.
7. **For sessions of a type that includes an exam, lab, or checkpoint** (per `session_types` and
   PROTOCOL.md's artifact sequence for that type), spec each one's scope/objective per the course
   protocol: exam scope (which prior sessions it covers), lab objective + transferable pattern,
   checkpoint scope (state through which delivery). For a final-presentation session type, spec the
   presentation scope. Only spec what the session type actually requires — check
   `artifacts.enabled` and the PROTOCOL's artifact sequence, don't assume every session has all of
   these.
8. **Note the delivery milestone** if one is due or presented this session, per the course's
   decisions log / PROTOCOL — which deliverable, what must exist, whether it maps to a checkpoint.
9. **Create the handover** from `.claude/refs/templates/handover-session.md`: fill the header + the
   checklist rows for the session type (PROTOCOL.md's artifact-close section).

## Output format (`S<NN>-plan.md`)

- **Header/ID** — session, date, modality, type, AI tool(s), special case.
- **Objectives** — from the brief.
- **Timeline** — table: `Block | Activity | Min | Start–End` (one Start–End column per
  `schedule.sections` entry — all of them — when the course has multiple sections).
- **Teaching-block breakdown** — per sub-block: name · min · points-to-cover (the `slides` skill's
  input).
- **Examples manifest** (when `examples` is enabled) — per sub-block, the demo/example the
  `examples` skill will build: label · sub-block/exercise · kind (live-demo | worked-example |
  exemplar) · surface/type · what it shows · slides-referenced?; plus an exemplar per exercise and
  any forced-failure reproduction note.
- **Downstream artifact specs** (in production order per the course's artifact sequence) —
  exercises · delivery note (if one is due) · **slides** (authored last — see the `slides` skill) ·
  lab/exam/checkpoint/final-presentation as applicable to the session type.
- **Notes** — anything the next orchestrators need (tool prerequisite, provisional coordination,
  placeholders, prior-material reuse verdicts).

## Acceptance criteria (self-audit)

- [ ] Timeline **sums to the session length** (`schedule.session_length_min`) and matches the shape
      for the session type per PROTOCOL.md.
- [ ] All blocks in **multiples of 5 min**; the mandated break is present; any sacred/empty block
      the protocol defines is present and kept empty.
- [ ] If `schedule.sections` is non-empty, the timeline gives a coherent start–end pair per
      section.
- [ ] Depending on session type (per PROTOCOL.md's sequence for it):
  - Sessions with `class-exercises` enabled: the exercises are correctly numbered `<session>.<slot>`,
    each grounded to the topic and scoped per the course's exercise convention; and — if `examples`
    is enabled — an Examples manifest giving each teaching sub-block a live demo / worked example
    (or theory-only), an exemplar per exercise, and any forced-failure note the lesson needs.
  - Sessions with an on-site/exam/lab/checkpoint type: exam scope + lab objective + checkpoint
    scope, per PROTOCOL.md.
  - A final-type session: presentation scope.
  - Any session-specific special case noted in the brief or PROTOCOL.md is honored (e.g. an
    opening-session recap slot repurposed to intro + setup).
- [ ] Each downstream artifact has an **actionable spec** (the next agent can execute it without
      re-reading the brief).
- [ ] **AI tool chosen** with a one-line reason, consistent with the course's tool-adoption
      sequence.
- [ ] Delivery milestone noted if one is due or presented.
- [ ] **Handover created** with the correct checklist for the session type.

## Close

1. Write `<folders.planning>/S<NN>-plan.md` and self-audit.
2. Update the handover (check the planning box, leave notes for the next orchestrator).
3. Add any new lesson to `.claude/refs/shared-context.md` (only what helps future sessions).
4. Record any new design decision in `<folders.sources>/<sources.decisions>`.
5. Emit the closing block per `.claude/refs/templates/next-agent-prompt.md`: a short summary for
   the conductor + the **PROMPT FOR THE NEXT AGENT**. The next skill is whichever artifact comes
   first in this session type's sequence per `PROTOCOL.md` and `artifacts.enabled` — do not
   hardcode a specific next slug.
