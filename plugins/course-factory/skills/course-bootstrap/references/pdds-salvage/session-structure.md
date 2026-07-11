# Session Structure, Block/Demo Styles, and Outline Principles

> Salvaged from the retired pdds-oyd plugin (technical/hands-on course, cloud-automation
> domain). Course-specific details (AWS-only policy, repo/tag naming, footer text, person
> names) are EXAMPLES of the pattern, not rules — adapt per course.yaml.

Read this file when building the **outline** (Step 1).

---

## Session Structure (3 hours, no break, no debrief)

### Hard constraints
- **Two exercises minimum, 30 min each** — fixed
- **No break block, no debrief block**
- Exercises are pacing breaks — isolated, standalone tasks
- Optional extensions (K8s/EKS, advanced topics) are a clean cutoff block at the
  end of the session — never embedded mid-session; always carry their own demo and
  optional exercise

### Default flow pattern — show-n-tell: cold open → demo → exercise → demo → exercise

For any session where students are ready to follow along live (typically once Terraform
fundamentals are established — Sessions 3+), this is the default structure. There are **no
standalone theory blocks**: the lean theory a block would have carried (primitive recap,
key trade-offs, the module interface) moves into the demo's opening context slide (the
first slide after the `demoSlide` marker in Live-coding companion style). The demo carries
the teaching; a separate preceding block only duplicates it.

```
Cold open → Demo 1 → Exercise 1 → Demo 2 → Exercise 2 → [optional extension demo + exercise]
```

This keeps cognitive load bounded: students practice each primitive before seeing the next.

| Slot | Block | Duration |
|------|-------|----------|
| Opening | Cold open + context setting | 10–15 min |
| Content | Demo 1 (theory folded into context slide) | 30–40 min |
| Pacing | Exercise 1 | 30 min |
| Content | Demo 2 (theory folded into context slide) | 30–40 min |
| Pacing | Exercise 2 | 30 min |
| Optional | Extension demo + exercise | 20–30 min |

Reserve standalone content blocks only for concepts that genuinely cannot be grasped from
code in motion (e.g., distributed-locking theory, IAM trust-policy structure). When in
doubt, fold it into the demo. For those exception cases, use the classic arrangement:
a short lean-theory block (20–30 min) preceding the demo that needs it.

---

## Block + Demo Styles

Two named styles govern how content blocks and demos are combined. **Declare the style
per demo in the outline** and apply it consistently through demo scripts and deck generation.

---

### Style 1 — Live-coding companion (default)

Slides advance in sync with the terminal. No separate theory block precedes the demo.
Each slide guides one step of the demo — but it is a **teaching guide, not a code mirror**.
The terminal holds the code; the slide holds the context the instructor speaks out loud.

**Use when:** students are ready to follow along in real time (Session 3+), the session
covers multiple parallel primitives of the same shape (e.g., four module types), and
watching the instructor type is itself the tutorial.

**Slide sequence per demo — strictly in this order:**

| Slide | Type | Content |
|---|---|---|
| demoSlide | `demoSlide` | Live demo marker — always the first slide of every demo, both styles |
| 1 — Context | `lSlide` | What we're building, why it matters, what the module interface looks like. 3–4 bullets. |
| Per step | `stepSlide` | One action per slide: what to do, why it matters, what to verify. See deck-spec.md. |
| Final — Callout | `calloutSlide` | One key concept from this demo: label pill + two paragraphs max. |

**Hard rules for live-coding companion slides:**
- One terminal action per `stepSlide` — never combine two steps on one slide
- `demoSlide` marker appears at the very start of the demo sequence — required even in companion style
- **Never reproduce HCL on slides.** The terminal is the code; the slide is the guide. Key argument names may appear inline in prose (e.g., "set `sensitive = true`"), but never full resource blocks or command output
- Each `stepSlide` uses exactly three bullets: (1) what to do in the terminal, (2) the concept or decision behind it, (3) what to verify in the output or the common pitfall to call out

**Demo script implication:** DEMO.md steps map 1-to-1 to `stepSlide` slides. Number
the DEMO.md steps to match slide numbers so the instructor can call out "slide 4"
without mental translation.

---

### Style 2 — Classic (exception)

Content slides precede the demo. A `demoSlide` marker separates theory from live coding.
Students read the theory, then watch the demo with no concurrent slides.

```
[Theory slides — prose + diagrams] → [demoSlide marker] → [live demo, terminal only]
```

**Use when (the exception, not the default):** the topic requires conceptual grounding
that genuinely cannot be grasped from code in motion — state management models,
distributed-locking theory, IAM trust-policy structure. For everything else, prefer the
Live-coding companion default and fold the lean theory into the demo's context slide.

**Deck implication:** one or more `cSlide` / `lSlide` theory slides followed by a single
`demoSlide`. No slides during the live coding segment.

---

## Outline Design Principles

Apply these when constructing the outline (Step 1). Check before presenting to the user.

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

### 5.4 — Default to show-n-tell structure
The default session structure is **cold open → demo → exercise → demo → exercise** with no
standalone theory blocks (see "Default flow pattern" above). Standalone content blocks are
the exception, reserved for concepts that cannot be grasped from code in motion. When in
doubt, fold the lean theory into the demo's context slide.
