# Demo Script Rules

Read this file when building **demo scripts and code example zips** (Step 2).

---

## Structure

Each demo:
- Has a `start/` state (instructor opens this) and `end/` state (target)
- `DEMO.md` contains: numbered steps, verbatim bash commands, pause points with
  talking-point annotations, key conceptual callouts, timing guide
- Zipped as `demo-<N>-<topic>.zip` for download — never `example-<N>.zip`

Demo names are concrete (e.g., `demo-3-ec2/`) — never `example-1/`.

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
its own start/end zip.

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
