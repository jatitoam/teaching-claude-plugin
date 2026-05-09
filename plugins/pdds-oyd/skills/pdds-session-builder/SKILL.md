---
name: pdds-session-builder
description: >
  Use this skill ONLY when building instructional session materials for the course
  "Optimizaciones y Desempeño / Cloud Deployment Automation" (PDDS, FISICC,
  Universidad Galileo), taught by Tito Alvarez with TA Abner Pérez. Triggers on
  explicit phrases like "build session N", "prepare session N", "let's do session N",
  "work on session N", or "next session" in the context of this specific course.
  Produces session deliverables in this fixed order: demo script(s) → exercise specs
  (DOCX) → deck (PPTX via pptxgenjs) → code examples (zip). Each step is
  approval-gated. Do NOT trigger for project deliveries (use pdds-delivery-builder),
  generic PPTX creation, or sessions from other courses.
---

# PDDS Cloud Deployment Automation — Session Builder

Produces the complete set of instructional materials for one session of the course:
demo scripts, exercise DOCX files, a PowerPoint deck, and a zipped examples directory.

---

## 1. Trigger Conditions

This skill applies when ALL of the following are true:

- The conversation is about the PDDS course at FISICC / Universidad Galileo
- The user says "build", "prepare", "work on", or "let's do" + "session N" (N = 1–10)
  OR refers to "the next session" with enough context to infer N

Do NOT use this skill for:
- Project deliveries — use `pdds-delivery-builder` instead
- Generic PowerPoint, DOCX, or exercise creation for any other course
- Grading or evaluating student work

---

## 2. Approval-Gated Sequence — mandatory, always in this order

Each step requires explicit approval before the next begins. Never skip ahead.

1. **Outline** — present full session structure in chat (time blocks, demo placement,
   exercise titles, K8s extension if applicable). Wait for "Go" or explicit approval.
2. **Demo script(s)** — one `DEMO.md` per demo, numbered steps + talking points.
   Wait for approval.
3. **Exercise specs** — exercises as DOCX files (see Section 5). Wait for approval.
4. **Deck** — PowerPoint via pptxgenjs (see Section 6). Wait for approval.
5. **Code examples** — zip with `start/` and `end/` states for each demo.

Structural corrections to outlines (e.g., repositioning exercises, removing blocks,
re-ordering demos) must be applied *before* any content is developed.

---

## 2a. Handover Document

After each approval-gated step is **approved** and before the next step begins, produce
a handover document at `/mnt/user-data/outputs/session<N>-handover.md` and present it
via `present_files`. This document is the single source of truth for any agent picking
up the build mid-stream.

### Required sections

1. **Session identity** — session number, date, topic, modality, K8s extension flag,
   delivery milestone if relevant
2. **Completed steps** — table of all five steps with ✅ / ⬜ status and a one-line note
   per completed step
3. **Next step** — exact step name, what it produces, and the approval gate that follows
4. **Approved outline** — concept thread, full agenda table, demo roster table
5. **Exercise separation matrix** — full matrix with copy-paste blocking rationale
6. **Style decisions** — which block+demo style was chosen per demo and why (see
   Section 4b); any instructor corrections applied to the default
7. **Constraints honored** — table of course constraints applied, their source, and
   confirmation they were respected
8. **File inventory** — paths of all files produced so far; "None" if outline only
9. **Pending decisions** — any open question the next agent must resolve before proceeding;
   "None" if all decisions are confirmed

### Format rules

- Markdown only; bold labels, no colors (lightweight formatting preference)
- Every table must have a header row
- File paths must be exact and absolute
- Produce the handover after **every** approved step, even if the same agent continues —
  it is the record, not just a relay artifact

---

## 3. Course Constants (hardcoded — never ask the user)

```
Instructor:     Tito Alvarez  (augusto.alvarez@galileo.edu)
TA:             Abner Pérez   (abner.perez@galileo.edu)
Program:        PDDS — FISICC — Universidad Galileo
Course name:    Optimizaciones y Desempeño / Cloud Deployment Automation
Schedule:       Thursdays 6–9 PM, GMT-6
Stack:          Terraform, GitHub Actions, optional Kubernetes/EKS
Footer text:    "Optimizaciones y Desempeño  ·  Cloud Deployment Automation  ·  PDDS · FISICC · Universidad Galileo"
```

### Session map

| # | Date | Topic | K8s ext? |
|---|------|-------|----------|
| 1 | Apr 23 | IaC Philosophy + Terraform Foundations | No |
| 2 | Apr 30 | Kubernetes Basics + GitHub Actions CI | No (K8s IS the content) |
| 3 | May 7 | Compute Automation + EKS Provisioning | Yes (10–15 min) |
| 4 | May 14 | Storage + Database + Remote State | No |
| 5 | May 21 | **On-site** — Partial Exam + Mid Presentations | — |
| 6 | May 28 | Networking Automation | Yes (10–15 min) |
| 7 | Jun 4 | Async Infrastructure + Full CD Pipeline | No |
| 8 | Jun 11 | IAM as Code + Security Automation | Yes (10–15 min) |
| 9 | Jun 18 | Observability Automation | Yes (10–15 min) |
| 10 | Jun 25 | **On-site** — Final Exam + Final Presentations | — |

Sessions 5 and 10 are on-site exam/presentation sessions — no session materials to build.

---

## 4. Session Structure (3 hours, no break, no debrief)

### Hard constraints
- **Two exercises minimum, 30 min each** — fixed
- **No break block, no debrief block**
- Exercises are pacing breaks — isolated, standalone tasks
- Optional extensions (K8s/EKS, advanced topics) are a clean cutoff block at the
  end of the session — never embedded mid-session; always carry their own demo and
  optional exercise

### Preferred flow pattern — interleaved learn → demo → exercise

When a session covers multiple parallel primitives of equal weight (e.g., three compute
targets, two storage backends), prefer this interleaved pattern over batching all content
then all exercises:

```
Block N (lean theory for primitive N) → Demo N → Exercise N → Block N+1 → ...
```

This keeps cognitive load bounded: students practice each primitive before seeing the next.
Content blocks in this pattern should be short (10–15 min) — the demo carries the teaching.

When a session covers a single coherent topic, the classic arrangement is still appropriate:

| Slot | Block | Duration |
|------|-------|----------|
| Opening | Cold open + context setting | 10–15 min |
| Content | Block 1 (lean theory) | 20–30 min |
| Content | Block 2 + live demo | 30–40 min |
| Pacing | Exercise 1 | 30 min |
| Content | Block 3 + live demo | 25–35 min |
| Pacing | Exercise 2 | 30 min |
| Optional | Extension block + demo + exercise | 20–30 min |

---

## 4b. Block + Demo Styles

Two named styles govern how content blocks and demos are combined. **Declare the style
per demo in the outline** and apply it consistently through demo scripts and deck generation.

---

### Style 1 — Classic (default)

Content slides precede the demo. A `demoSlide` marker separates theory from live coding.
Students read the theory, then watch the demo with no concurrent slides.

```
[Theory slides — prose + diagrams] → [demoSlide marker] → [live demo, terminal only]
```

**Use when:** the topic requires conceptual grounding before code is shown — state
management models, distributed locking theory, IAM trust policy structure. The concept
is harder to grasp from code alone.

**Deck implication:** one or more `cSlide` / `lSlide` theory slides followed by a single
`demoSlide`. No slides during the live coding segment.

---

### Style 2 — Live-coding companion

Slides advance in sync with the terminal. No separate theory block precedes the demo.
The slides ARE the demo — each slide corresponds to exactly one action in the terminal.

**Use when:** students are ready to follow along in real time (Session 3+), the session
covers multiple parallel primitives of the same shape (e.g., four module types), and
watching the instructor type is itself the tutorial.

**Slide sequence per demo — strictly in this order:**

| Slide | Type | Content |
|---|---|---|
| 1 — Context | `lSlide` | One sentence: what we're building and why. Optional resource diagram or directory tree. |
| 2 — Module structure | `dSlide` | Directory tree of files to be created (`tree` output style in code block) |
| Per file | `dSlide` | Exact HCL content of one file. One file per slide — never combine two files. |
| Per command | `dSlide` | Exact command in a code block. Expected output truncated to ≤ 8 lines; use `[...]` for the rest. |
| Final — Callout | `lSlide` | One key concept from this demo highlighted. Bold label + two sentences max. |

**Hard rules for live-coding companion slides:**
- One terminal action per slide — never combine two commands on one slide
- `demoSlide` marker still appears at the very start of the demo sequence — it signals
  the live segment is beginning even in companion style
- Code blocks on per-file and per-command slides use the standard `codeBox` helper
  (see Section 7); never exceed 11 lines
- Expected output on command slides must be truncated — graders and students cannot
  read 40-line plan outputs on a slide; show the signal lines only

**Demo script implication:** in live-coding companion mode, the DEMO.md steps map
1-to-1 to slides. Number the DEMO.md steps to match slide numbers so the instructor
can call out "slide 4" without mental translation.

---

## 5. Outline Design Principles

Apply these when constructing the outline (Step 1). They are checked before presenting
the outline to the user.

### 5.1 — Lead with the concept thread
State the core concept that unifies the session as the first element of the outline,
before the agenda table. The thread answers: *what is the one thing every demo and
exercise proves?* All timing, demo sequencing, and exercise design follow from it.

Example: "One app, three compute primitives, same module interface" is a concept thread.
"We will cover EC2, Lambda, and ECS" is not — it is a topic list.

### 5.2 — Derive time blocks from content, not the reverse
Size content blocks based on what the topic actually needs. If a demo will teach the
concept better than slides, shorten the preceding content block and let the demo carry
the weight. Never pad a content block to fill a predetermined slot.

### 5.3 — Never telegraph finality on student decisions
Do not use language like "decision is final", "you must commit tonight", or "no changes
after this session" for architectural or tooling choices students are still exploring.
State that students will have the full picture after the relevant content, and that
decisions have a deadline in the delivery document — not in the session.

---

## 6. Exercise Specs — DOCX

Read `/mnt/skills/public/docx/SKILL.md` before writing any generation code.

### Design rules

- Each exercise: exactly 30 min
- Complexity must match only what has been shown in class *before* the exercise
- **Standalone**: not tied to the course project, works in isolation
- **Demos ≠ Exercises**: different language runtime, different AWS resource type,
  copy-paste from demo to exercise must not be possible
- **Order by complexity, not by topic order**: if the session covers multiple concepts,
  assign the simpler concept to Exercise 1 regardless of which demo came first in the
  session. Students should build confidence before encountering nuance.
- **One primitive per exercise**: do not combine multiple unrelated resource types in
  a single exercise. If a concept requires two resources that always travel together
  (e.g., EC2 + Security Group), that is one primitive — include both. If two concepts
  are independently teachable, they belong in separate exercises.

### Copy-paste blocking

The preferred blocker is **same app scenario, different runtime**:
- Same endpoint contract, curl-testable with identical commands across all exercises
- Different language runtime per exercise — verified in the separation matrix

When additional differentiation is needed (e.g., to prevent cross-exercise copying),
use **different app scenario** as a secondary blocker. State the scenario difference
explicitly in the outline's separation matrix.

Always produce a separation matrix in the outline:

| | Demo A | Demo B | Ex 1 | Ex 2 |
|---|---|---|---|---|
| Runtime | Go | Python | Ruby | Node.js |
| AWS resource | EC2 | Lambda | EC2 | Lambda |
| App scenario | health+echo | health+echo | health+echo | currency API |
| Copy-paste blocked? | — | — | ✓ runtime | ✓ runtime+scenario |

### Evidence requirement

Every exercise must include a verifiable artifact:

- **Running resource**: CLI command output saved as `evidence/<n>.txt`, rendered
  inline in `README.md` under `## Evidence`
- **Visual output** (K8s, running apps): screenshot saved as `evidence/<n>.png`,
  rendered inline in `README.md` under `## Evidence`
- **Pipeline output** (CI/CD, GitHub Actions): link to the PR + screenshot of the
  result, saved as `evidence/<n>.png`

Test: *can a grader verify this passed without access to the student's machine?*

### Submission instructions (verbatim in every exercise)

```
Initialize a new repository called oyd-exercise-<session>-<n> and commit/push
everything into it. Submit the repository URL only.
```

### DOCX section order

1. **H1 title** — `Exercise <session>.<n> — <Title>`
2. **Header block** — Course name, Session date, Time allowed, Submission instructions
   (plain paragraphs, bold labels)
3. **H2 Context** — scenario / starter code; inline in Courier New if file is provided
4. **H2 Setup** — prerequisites (CLI tools, credentials, starter file location)
5. **H2 Tasks** — H3 per task, numbered sub-questions as a numbered list
6. **H2 Acceptance Criteria** — bullet list of what a passing submission looks like

### DOCX formatting

- Body: Calibri 12pt; code: Courier New — no color, bold and font size only
- Produce as DOCX via the `docx` npm skill
- Validate with `/mnt/skills/public/docx/scripts/office/validate.py`

---

## 7. Deck — PowerPoint via pptxgenjs

Read `/mnt/skills/public/pptx/SKILL.md` before writing any generation code.

### Output path

Generate to `/home/claude/session<N>/Session<N>_<Topic>.pptx`, then copy to
`/mnt/user-data/outputs/`.
Validate by converting to PDF (`soffice`) and rendering to JPG (`pdftoppm`).

### Color palette

```
N  = "1A237E"   // deep navy       — title bars, section headers, dark backgrounds
P  = "6540A8"   // medium purple   — accents, exercise cards, code header bars
B  = "2563EB"   // royal blue      — table headers, callouts
W  = "FFFFFF"   // white
LB = "EEF2FF"   // light indigo    — alternating content background
D  = "1F2937"   // near-black      — body text
M  = "9CA3AF"   // muted grey      — captions, footer
CB = "13172E"   // very dark navy  — code block background
CT = "D4D4D8"   // light grey      — code block text
AC = "38BDF8"   // sky blue        — live demo accent label
GR = "10B981"   // emerald         — positive, exercise rows, "after" state
RE = "EF4444"   // red             — warnings, "before" state, errors
GO = "F59E0B"   // amber           — notes, caution rows
TA = "F5F7FF"   // very light blue — table alternate rows
TB = "C7D2FE"   // periwinkle      — table borders
```

Font: Calibri body, Courier New for all code.

### Slide types

| Type | When to use |
|------|-------------|
| `cSlide(title)` | Standard content, white background |
| `lSlide(title)` | Standard content, light indigo (LB) background |
| `dSlide(title)` | Dark code-heavy slide (CB background, purple nav bar) |
| `sdSlide(title, sub)` | Section divider — full navy, purple vertical bar, large type |
| `exSlide(n, title, desc)` | Exercise card — purple left panel, navy right |
| `demoSlide(title)` | Live demo marker — very dark bg, sky-blue LIVE DEMO label |

### Required slides — every session deck

1. **Title slide** — session number, topic, date, instructor names
2. **Tonight's Plan** — agenda table with times; exercise rows highlighted in green
3. **Section divider** (`sdSlide`) per content block
4. **Content slides** per block (as many as the topic needs)
5. **Live demo marker** (`demoSlide`) immediately before each demo
6. **Exercise card** (`exSlide`) at each exercise slot

Course admin slides (schedule, assessment, policies) — include for Session 1 and
any session with a significant announcement; omit otherwise.

### Slide density

Prefer many small focused slides over large dense ones. Split when a slide has
more than ~5 bullet points or two unrelated ideas. Exception: comparison slides
(before/after, A vs B) stay together.

### Before/after and anti-pattern slides

When a content block introduces a concept that is better shown than described
(module design, dependency chains, copy-paste drift), use a dedicated before/after
slide pair:
- **Before slide** (`RE` accent): the problematic pattern with code example
- **After slide** (`GR` accent): the correct pattern with code example
- Keep both on adjacent slides — never split across a section divider

### Code blocks

```javascript
const codeBox = (slide, code, x, y, w, h) => {
  slide.addShape(pres.shapes.RECTANGLE,
    { x, y, w, h, fill:{color:"0D1021"}, line:{color:"2E3A59"} });
  slide.addText(code, { x:x+0.15, y:y+0.12, w:w-0.3, h:h-0.24,
    fontSize:10.5, color:"D4D4D8", fontFace:"Courier New",
    align:"left", valign:"top", margin:0 });
};
```

**Hard line limit:** at `fontSize: 10.5`, each line ≈ `0.175"`. Inner text height = `h - 0.24"`.
**Never exceed 11 lines** in a single code box — truncate with `[...]` or split across slides.
Overflow is invisible during generation but visible in every render.

---

## 8. Demo Script Rules

### Structure

Each demo:
- Has a `start/` state (instructor opens this) and `end/` state (target)
- `DEMO.md` contains: numbered steps, verbatim bash commands, pause points with
  talking-point annotations, key conceptual callouts, timing guide
- Zipped as `demo-<N>-<topic>.zip` for download — never `example-<N>.zip`

Demo names are concrete (e.g., `demo-3-ec2/`) — never `example-1/`.

### 8.1 — Demos carry the teaching weight
Content blocks preceding a demo should be lean (10–20 min max for complex topics).
The demo is the tutorial; the block is the map. Do not duplicate in slides what the
live demo will show in code.

### 8.2 — Multiple parallel primitives → labeled phases or sequential demos
When a session covers multiple resource types that share a concept (e.g., three
compute targets that all expose an HTTP endpoint), structure the session as sequential
demos (Demo A, Demo B, Demo C) each covering one primitive, rather than one large
demo with crowded phases. Each demo has its own content block, its own exercise, and
its own start/end zip.

### 8.3 — Bridging resources belong in the block and demo from the start
If a resource has no public interface on its own, identify the required bridging
resource during outline design and include it in the same content block and demo.
Do not add it as a mid-session afterthought.

Examples:
- Lambda has no public URL → API Gateway is a first-class part of the Lambda block
- ECS Fargate has no stable public IP → ALB is a first-class part of the ECS block
- EKS cluster has no app exposure → Service + port-forward or Ingress belongs in the demo

### 8.4 — Optional CI/CD workflow in every demo end/ state
Every demo's `end/` directory includes `.github/workflows/terraform-ci.yml`
implementing the standard CI pipeline (fmt check, init -backend=false, validate,
plan with PR comment). Flagged as instructor-paced — shown if time permits, never
required for exercises in the same session.

---

## 9. Output File Structure

```
session<N>/
├── Session<N>_<Topic>.pptx
├── demos/
│   ├── demo-<N>-<topic>/
│   │   ├── DEMO.md
│   │   ├── start/
│   │   └── end/         ← always includes optional terraform-ci.yml
│   └── demo-<N>-<topic>.zip
└── exercises/
    ├── Exercise_<N>_1.docx
    ├── Exercise_<N>_2.docx
    └── Exercise_<N>_3.docx   ← optional, e.g. EKS track
```

---

## 10. Common Defects — check before presenting

### Outline defects
- **No concept thread**: outline starts with a topic list, not a unifying concept — add
  the thread before the agenda table
- **Blocks sized to fill time, not content**: a content block that is 30+ min when a
  demo follows — shrink it, the demo carries the teaching
- **Finality language**: "decision is final", "commit tonight", "no changes after" —
  remove; reference the delivery deadline instead
- **Optional extension embedded mid-session**: K8s/EKS segments must be a clean cutoff
  block at the end, never inserted between core content and exercises

### Demo defects
- **Demo = Exercise**: verify different runtime and different resource type
- **Bridging resource missing**: resource with no public interface lacks its access
  layer — add it to the block and demo (see 8.3)
- **CI workflow absent from end/**: every demo end/ must include terraform-ci.yml
- **Demo zip name is generic**: use `demo-<N>-<topic>.zip`, never `example-<N>.zip`

### Exercise defects
- **Ordered by topic, not complexity**: simpler exercise must come first regardless of
  demo order
- **Multiple unrelated primitives in one exercise**: split into separate exercises
- **No separation matrix in outline**: always produce the matrix before exercises are written
- **Exercise has debrief or break block**: not permitted — remove
- **Exercise references project**: exercises must be standalone
- **Evidence not specified**: every exercise needs a verifiable artifact
- **Submission instructions missing or paraphrased**: use verbatim wording from Section 6

### Deck defects
- **Code block overflow**: count lines before placing — never exceed 11 at fontSize 10.5
- **Before/after concept taught with only prose**: use before/after slide pair with
  code examples (see Section 7, before/after slides)

### Style defects (Section 4b)
- **Style not declared in outline**: every demo entry in the agenda table must name
  its style (Classic or Live-coding companion) — absence means the deck builder has
  no spec to follow
- **Live-coding companion without `demoSlide` marker**: the marker is required even in
  companion style — it signals the live segment boundary in the deck
- **Two terminal actions on one companion slide**: one action per slide is a hard rule;
  split into separate slides
- **Command slide output not truncated**: expected output longer than 8 lines on a
  companion slide overflows invisibly — always trim with `[...]`
- **DEMO.md steps not numbered to match slides**: in companion mode, step N in DEMO.md
  must correspond to slide N so the instructor can call out slide numbers live

### Handover defects (Section 2a)
- **Handover not produced after an approved step**: every approval gate must produce
  a handover file before the next step begins — skipping it breaks agent relay
- **Handover missing a required section**: all nine sections are mandatory; "None"
  is a valid value but the section must still appear
- **File inventory lists relative paths**: all paths in the inventory must be absolute
- **Handover produced before approval**: the handover is a post-approval artifact;
  producing it speculatively (before the user says Go) is incorrect
