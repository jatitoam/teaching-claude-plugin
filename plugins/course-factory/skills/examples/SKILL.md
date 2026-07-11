---
name: examples
description: >
  Instructor-only demo & worked-example pack for a course session in the course-factory
  material-production harness. Produces numbered live-demo scripts, worked examples, and
  exercise exemplars in `<folders.examples>/S<NN>/` (one `NN-<slug>.md` per item plus a
  `00-index.md`), driven by the session plan's Examples manifest — the material the later
  class-exercises and slides skills reference instead of re-inventing. Never published to
  students. Invoke DELIBERATELY within a course material-production pipeline (the working
  folder has `.claude/refs/course.yaml`); do NOT auto-trigger for generic "give me some
  examples" requests.
---

# Examples & demos (instructor pack)

> **Bootstrap:** if you start from zero: (1) locate the course root — the nearest ancestor
> folder containing `.claude/refs/course.yaml`; (2) read `course.yaml` (language, folder
> names, enabled artifacts, tool stack, publishing targets); (3) read
> `.claude/refs/PROTOCOL.md` — the course's contract; (4) read your session handover
> `.claude/refs/handovers/handover-S<NN>.md` if it exists; (5) read
> `.claude/refs/shared-context.md`. If `examples` is not in `artifacts.enabled`, STOP and warn
> the conductor. Write ALL generated content in `course.language`.

**Tier:** **Opus** orchestrates + judges · **Sonnet** authors the demo scripts and worked
examples. The harness does not execute the demos — it writes what the instructor runs live
(steps, prompts, commands, expected output, and a fallback for when a live run misbehaves).
You typically run right after session-planning, and your pack is what the later class-exercises
and slides skills **reference** instead of re-inventing.

## Why this artifact exists

Teaching blocks that pair a concept with a live demo need the *depth* — the actual prompts run,
commands typed, code generated, outputs pointed at — to live somewhere other than the slides, so
the deck stays light and later artifacts reference this pack instead of re-inventing it. This
artifact is **instructor-only**: it is never published to students.

## What you produce

- `<folders.examples>/S<NN>/` (default folder name `examples`, per `course.yaml
  naming.folders.examples`) — the instructor demo & examples pack: **one numbered `.md` per
  demo/example** (e.g. `01-a2-weak-to-strong.md`, `02-a3-role-vs-no-role.md`, …), numbered in
  teaching-block order (Block A → Block B → … → exercise exemplars → special-technique demos) so
  they're easy to find and run in sequence, plus a **`00-index.md`** that maps each file to its
  sub-block · kind · surface · the slide/block it pairs with. **Instructor-only — no Google Doc,
  no publication.** One example per file — never a single monolithic pack.

Each file holds one item, of whichever kind the plan's Examples manifest marks for that
sub-block:

1. **Live-demo scripts** — the default for a "concept + live demo" block. Each is *runnable*:
   **goal** (what the student should see/understand) · **setup** (what to have open/ready) ·
   **steps** (the exact prompts to paste / commands to type / clicks) · **expected result & what
   to point out** · **if it fails live** (a captured output/screenshot to fall back on — live
   demos misbehave). Demo surfaces vary by course and session — per the session brief.
2. **Worked examples** — a self-contained static example where showing beats running live (or to
   hand the instructor a reference): **prompt(s)**, a realistic **output** (weak and strong side
   by side, for a contrast), and a one-line **why it's better / what changed**.

Plus, where the manifest lists them, **exercise exemplars** — a model answer per exercise
(instructor reference for demoing/grading; **not** handed to students).

## Inputs (read, don't duplicate)

- `<folders.planning>/S<NN>-plan.md` → the **Examples manifest** (the list of demos/examples to
  build: which sub-block/exercise each supports, kind [live-demo | worked-example | exemplar],
  the surface/type, what it shows, any special reproduction note). **This is your checklist.** If
  the plan has no Examples manifest, derive one from the teaching-block breakdown and note it.
- The session's teaching-block breakdown in the plan → ground every demo in the *actual* content
  and its time range.
- `<folders.sources>/<sources.session_briefs>` → your session's brief (the concrete tools/
  patterns to demo, per the course PROTOCOL.md's session-type sequence).
- `<folders.sources>/<sources.glossary>` → shared vocabulary; use terms the way it defines them.
- `.claude/refs/shared-context.md` → conventions and accumulated lessons.

## Process

1. **Read the Examples manifest** — that is exactly the set of demos/examples to produce, one
   (or more) per teaching sub-block, plus the exercise exemplars.
2. **Delegate authoring to Sonnet** (one agent for the pack). Pass it the manifest rows + the
   relevant sub-block points + the audience note from `course.yaml course.audience` (plain
   language, concrete, glossary terms, no unexplained jargon appropriate to that audience). For
   each live-demo item Sonnet writes the runnable script (goal · setup · steps · expected ·
   fallback); for worked examples the prompt + output + why; for exemplars a full model answer.
3. **For any "special reproduction technique"** the manifest flags (below), you (Opus) build the
   recipe; Sonnet drafts the supporting material.
4. **Audit (judge):** every manifest item present and grounded in the session's actual teaching
   content; live-demo scripts are genuinely runnable with a live-failure fallback; worked
   examples self-contained and plain-language; exemplars realistic. Write **one numbered file per
   manifest item** into `<folders.examples>/S<NN>/` and the `00-index.md` map.

## Special reproduction techniques (forcing a failure the real tool won't show in class)

Some teaching beats depend on the tool **failing**, and the real tool won't reliably fail inside
a class. When the manifest flags one, provide a controlled way to force it:

- **Gated on `tool_stack.ollama_forced_failure` (course.yaml).** When true, the manifest may call
  for a demo built on a **small local model** run at a deliberately small context window, so a
  degradation (e.g. "the window fills → an earlier decision gets cut") happens fast and
  reproducibly. Provide the long, decision-laden script + the recall probe, then the recovery
  step the course's tooling provides (e.g. a handover document that restores the lost decision).
  Name concrete small-model options and a `num_ctx` in the few-hundred-to-1k range. **The skill
  only GUIDES this; it does NOT install anything**, and the local model is optional. State
  explicitly: this is an **instructor demo tool ONLY** — never presented to students as a tool
  they use (students stay on the session's featured tools per `tool_stack.student_tools`).
- When `tool_stack.ollama_forced_failure` is false or unset, do not introduce a local-model
  demo — use a frontier-model fallback and note plainly that it is less reliable at forcing the
  failure on cue.
- **General rule:** any block whose lesson is a failure mode the real tool resists (a
  hallucination, a refusal, a silent wrong answer) can use the same idea — a deliberately
  constrained or misconfigured setup that makes the failure show on cue. Keep it instructor-side
  and label it as such.

## Optional demo format: hands-on demo folders (start/ + end/ + DEMO.md)

Suited to **technical courses** (infra, backend, data, code-heavy material) where a demo is best
delivered as a runnable code folder the instructor clones and drives live, rather than (or in
addition to) a live-demo script file. When the manifest calls for this format:

- Each demo is a `start/` (working state) + `end/` (target state) folder pair, plus a `DEMO.md`
  teacher script — numbered steps, verbatim commands, timed pause points with talking-point
  annotations. Delivered as a plain directory, **never zipped**.
- If the demo builds on a repo from a prior session, fork it rather than inventing a start state
  from scratch; `start/` then holds only the new/modified files, and `DEMO.md` opens with a
  `## Fork & Clone` section.
- Full mechanics (naming convention, fork-vs-self-contained rules, what belongs in `start/`):
  `${CLAUDE_PLUGIN_ROOT}/skills/course-bootstrap/references/pdds-salvage/demo-spec.md`.

## Output format (`<folders.examples>/S<NN>/`)

**One file per item, numbered** in teaching-block order: `NN-<slug>.md` (e.g.
`01-a2-weak-to-strong.md`, `07-b1-same-prompt-twice.md`, `10-ex1-exemplar.md`). Keep the number
2-digit and the slug tied to the manifest label. Each file:
- **Title line** — the manifest label + kind (e.g. `# A2 · weak→strong — worked-example
  (prompting)`).
- **Pairs with** — the slide group / block + its time range (from the plan), so the instructor
  knows when to run it.
- **Body** — a live-demo script (goal · setup · steps · expected result & what to point out · if
  it fails live fallback) **or** a worked example (prompt(s) · output — weak+strong for a
  contrast · why) **or** an exercise exemplar (a full model answer) **or**, when the manifest
  calls for it, a hands-on demo folder pair (`start/`, `end/`, `DEMO.md`) alongside its index
  entry. Special-technique files also carry the forced-failure recipe when config-gated on.

**`00-index.md`** — a table mapping every file → sub-block · kind · surface · the slide/block it
pairs with (and its time range), so the instructor can scan the whole pack at a glance.

## Acceptance criteria (self-audit)

- [ ] Every item in the plan's Examples manifest is present and grounded in the session's actual
      teaching content, as one numbered file per item (`NN-<slug>.md`) in
      `<folders.examples>/S<NN>/`, numbered in teaching-block order, plus a `00-index.md` map.
      Each file names the slide/block it pairs with and its time range.
- [ ] Each live-demo script is runnable (goal · setup · exact steps · expected result ·
      live-failure fallback).
- [ ] Worked examples are self-contained (prompt + output + why); prompt-contrast examples show
      weak and strong side by side; exemplars are realistic model answers.
- [ ] Any special reproduction technique flagged by the manifest is fully specified **and gated
      on `tool_stack.ollama_forced_failure`** when it depends on a local model; the skill does
      not install anything.
- [ ] If the manifest calls for hands-on demo folders, each has a `start/`/`end/` pair and a
      `DEMO.md` per the referenced demo-spec, never zipped.
- [ ] **Instructor-only:** no publication, no student-facing framing. Any instructor-only demo
      tool is never presented as something students use.

## Close

1. Write the numbered files + `00-index.md` into `<folders.examples>/S<NN>/` and self-audit.
   (No publication — instructor reference only.)
2. **Human gate:** the conductor validates the pack.
3. Update `handover-S<NN>.md` (check the Examples box; note which demos/examples the later
   class-exercises and slides skills should reference rather than re-invent).
4. Add any new lesson to `.claude/refs/shared-context.md` (only what helps future sessions).
5. Record any new decision in `<folders.sources>/<sources.decisions>`.
6. Emit the closing block per `.claude/refs/templates/next-agent-prompt.md`: a short summary for
   the conductor + the PROMPT FOR THE NEXT AGENT — the next artifact in the session type's
   sequence per the course PROTOCOL.md (do not hardcode a specific next slug).
