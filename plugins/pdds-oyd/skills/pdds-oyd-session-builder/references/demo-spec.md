# Demo Script Rules

Read this file when building **demo scripts and code example folders** (Step 2).

---

## Structure

Each demo:
- Has a `start/` state (instructor opens this) and `end/` state (target)
- `DEMO.md` contains: numbered steps, verbatim bash commands, pause points with
  talking-point annotations, key conceptual callouts, timing guide
- Delivered as a plain directory — **do not zip**

Demo folders are named `session-<N>-demo-<X>-<topic>` where N is the session number and
X is the demo's position within the session (e.g., `session-6-demo-1-network-foundation/`,
`session-3-demo-2-lambda/`) — never `demo-<N>-<topic>/` and never `example-1/`. The session
prefix makes folders self-identifying when browsing across sessions.

---

## 8.1 — Demos carry the teaching weight
Content blocks preceding a demo should be lean (10–20 min max for complex topics).
The demo is the tutorial; the block is the map. Do not duplicate in slides what the
live demo will show in code.

---

## 8.2 — Multiple parallel primitives → labeled phases or sequential demos
When a session covers multiple resource types that share a concept (e.g., three
compute targets that all expose an HTTP endpoint), structure the session as sequential
demos (Demo A, Demo B, Demo C) each covering one primitive, rather than one large
demo with crowded phases. Each demo has its own content block, its own exercise, and
its own start/end folder.

---

## 8.3 — Bridging resources belong in the block and demo from the start
If a resource has no public interface on its own, identify the required bridging
resource during outline design and include it in the same content block and demo.
Do not add it as a mid-session afterthought.

Examples:
- Lambda has no public URL → API Gateway is a first-class part of the Lambda block
- ECS Fargate has no stable public IP → ALB is a first-class part of the ECS block
- EKS cluster has no app exposure → Service + port-forward or Ingress belongs in the demo

---

## 8.4 — Optional CI/CD workflow in every demo end/ state
Every demo's `end/` directory includes `.github/workflows/terraform-ci.yml`
implementing the standard CI pipeline (fmt check, init -backend=false, validate,
plan with PR comment). Flagged as instructor-paced — shown if time permits, never
required for exercises in the same session.

---

## 8.5 — Demo code is single-cloud (AWS); GCP stays a callout
Write demo `start/`/`end/` code for **one cloud provider only — AWS**. Do not author
parallel GCP demo code, parallel GCP folders, or GCP-specific live-coding slides. Where the
course material references a GCP equivalent, keep it as a verbal note or a small
equivalence table in the context slide — never as runnable demo code. This keeps demos
focused and halves the maintenance surface.

---

## 8.6 — Fork cumulative demos from the prior session's repos
When a session builds on infrastructure students already created in earlier sessions,
each demo's `start/` state should be a **fork of the relevant prior-session repo at its
final state**, with its placeholder values left intact (e.g. hardcoded resource IDs in
`dev.tfvars`). The `end/` state then adds the new layer on top and replaces those
placeholders with real references. This makes the placeholder-to-real-wiring refactor
the central, recognizable teaching moment, and mirrors what the students' own project
repos actually look like at that point in the course.

If the prior-session repos or their locations (GitHub org, local paths) are not provided,
**ask for them before building** — do not invent a `start/` state from scratch when a
forkable predecessor exists.
