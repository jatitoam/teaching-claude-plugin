# Common Defects — check before presenting each deliverable

---

## Outline defects
- **No concept thread**: outline starts with a topic list, not a unifying concept — add
  the thread before the agenda table
- **Blocks sized to fill time, not content**: a content block that is 30+ min when a
  demo follows — shrink it, the demo carries the teaching
- **Finality language**: "decision is final", "commit tonight", "no changes after" —
  remove; reference the delivery deadline instead
- **Optional extension embedded mid-session**: K8s/EKS segments must be a clean cutoff
  block at the end, never inserted between core content and exercises

---

## Demo defects
- **Demo = Exercise**: verify different runtime and different resource type
- **Bridging resource missing**: resource with no public interface lacks its access
  layer — add it to the block and demo (see demo-spec.md §8.3)
- **CI workflow absent from end/**: every demo end/ must include terraform-ci.yml
- **Demo folder misnamed**: use `session-<N>-demo-<X>-<topic>/`, never `demo-<N>-<topic>/`
  or `example-<N>/`
- **Demo folder was zipped**: deliver demos as plain directories — do not produce `.zip` files

---

## Exercise defects
- **Ordered by topic, not complexity**: simpler exercise must come first regardless of
  demo order
- **Multiple unrelated primitives in one exercise**: split into separate exercises
- **No separation matrix in outline**: always produce the matrix before exercises are written
- **Exercise has debrief or break block**: not permitted — remove
- **Exercise references project**: exercises must be standalone
- **Evidence not specified**: every exercise needs a verifiable artifact
- **Submission instructions missing or paraphrased**: use verbatim wording from exercise-spec.md

---

## Deck defects
- **Code mirroring on companion slides**: `dSlide` with full HCL content, simulated
  `terraform plan` output, or directory tree output in the demo sequence — replace
  every instance with `stepSlide`. The terminal is the code; the slide is the guide
- **stepSlide has more than three bullets**: each step slide gets exactly three bullets
  (what / why / verify). A fourth bullet means the step is trying to teach two concepts
  — split it into two `stepSlide` calls
- **calloutSlide missing at end of demo**: every demo must close with a `calloutSlide`
  (navy bg, dark box, label pill), not a plain `lSlide`
- **demoSlide missing**: every demo must open with a `demoSlide` marker — both Classic
  and Live-coding companion styles require it
- **Before/after concept taught with only prose**: use a before/after slide pair with
  `dSlide` code examples — the one valid use of `dSlide` in a demo context

---

## Style defects
- **Style not declared in outline**: every demo entry in the agenda table must name its
  style (Classic or Live-coding companion) — absence means the deck builder has no spec
  to follow
- **Live-coding companion without `demoSlide` marker**: the marker is required even in
  companion style — it signals the live segment boundary in the deck
- **Two actions on one `stepSlide`**: one terminal action per slide is a hard rule;
  split into separate `stepSlide` calls
- **DEMO.md steps not numbered to match slides**: in companion mode, step N in DEMO.md
  must correspond to slide N so the instructor can call out slide numbers live

---

## Handover defects
- **Handover not produced after an approved step**: every approval gate must produce
  a handover file before the next step begins — skipping it breaks agent relay
- **Handover missing a required section**: all nine sections are mandatory; "None"
  is a valid value but the section must still appear
- **File inventory lists relative paths**: all paths in the inventory must be absolute
- **Handover produced before approval**: the handover is a post-approval artifact;
  producing it speculatively (before the user says Go) is incorrect
- **Agent continued past the handover in the same turn**: after `present_files` is
  called with the handover, the agent must stop — no further step content, no file
  generation, no reading of the next skill. Producing handover + next step in one
  turn silently skips an approval gate
- **Next step section missing build notes**: the "Next step" section must include the
  skill to read first, the output path, the validation command, and the approval gate —
  not just the step name
