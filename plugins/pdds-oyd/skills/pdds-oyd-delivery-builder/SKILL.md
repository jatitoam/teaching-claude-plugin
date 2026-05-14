---
name: pdds-oyd-delivery-builder
description: >
  Use this skill ONLY when building a graded project delivery document for the OyD
  (Optimizaciones y Desempeño / Cloud Deployment Automation) course in the PDDS program
  at FISICC, Universidad Galileo, taught by Tito Alvarez, with TA Abner Pérez, graders
  jatitoam and abner-perez. Triggers on explicit phrases like "prepare delivery N",
  "build delivery N", "create delivery N", or "let's do delivery N" where N is a
  delivery number (1–5) in the context of this specific course. Each delivery
  produces exactly two files: a DOCX assignment document and an XLSX grading rubric.
  Do NOT trigger for other courses, generic rubric creation, or generic Word documents.
---

# OyD (Optimizaciones y Desempeño) — Project Delivery Builder

Produces the two graded-delivery artefacts for the 5-delivery course project:
a **DOCX** assignment document and an **XLSX** grading rubric.

---

## 1. Trigger Conditions (read carefully — very specific)

This skill applies when ALL of the following are true:

- The conversation is about the OyD course in the PDDS program at FISICC / Universidad Galileo
- The user says "prepare", "build", "create", or "let's do" + "delivery N" (N = 1–5)
- No prior deliverable of the same number has been produced in this conversation

Do NOT use this skill for:
- Generic rubric creation (use the `rubric-creator` skill instead)
- Exercise specs or session decks (covered by the session-build workflow in CLAUDE.md)
- Grading or evaluating student work
- Any course other than this one

---

## 2. Approval-Gated Sequence — mandatory, always in this order

1. **Outline** — present the full proposed document structure in chat (sections, rubric
   criteria with proposed point values). Wait for explicit approval before proceeding.
2. **Address questions** — apply any corrections to criteria, point values, optional tracks,
   or AWS/GCP equivalences before generating any file.
3. **Generate DOCX** — run the Node.js build script (docx npm), validate with
   `/mnt/skills/public/docx/scripts/office/validate.py`.
4. **Generate XLSX (via rubric-creator skill)** — see Section 5. The rubric-creator skill
   must be present in `available_skills`. If it is not, **stop immediately and alert the
   user** before doing anything else.
5. **Present both files** — use `present_files` with DOCX first, XLSX second.

Never skip the outline step, even if the user says "just build it."

---

## 3. Course Constants (hardcoded — never ask the user for these)

```
Instructor:        Tito Alvarez  (augusto.alvarez@galileo.edu)
TA:                Abner Pérez   (abner.perez@galileo.edu)
Graders:           jatitoam     → github.com/jatitoam
                   abner-perez  → github.com/abner-perez
Program:           PDDS — FISICC — Universidad Galileo
Course name:       Optimizaciones y Desempeño / Cloud Deployment Automation
Schedule:          Thursdays 6–9 PM, GMT-6
Stack:             Terraform, GitHub Actions, optional Kubernetes/EKS
Repo format:       Same GitHub repo as Infraestructura en la Nube
Tag format:        oyd-delivery-N  (e.g. oyd-delivery-3)
Summary path:      infra/docs/delivery-N-summary.md
Infra root:        infra/   (ALL paths in the document must use this prefix)
```

### Delivery schedule

| # | Due Date | Topic |
|---|----------|-------|
| 1 | May 10, 2026 | Terraform workspace bootstrap & CI pipeline |
| 2 | May 21, 2026 | Compute, storage, database & remote state |
| 3 | Jun 7, 2026  | Networking layer |
| 4 | Jun 21, 2026 | Async infrastructure & full CD pipeline |
| 5 | Jun 25, 2026 | IAM as code, security, observability, one-click deployment |

---

## 4. DOCX Structure — required sections, every delivery

Read `/mnt/skills/public/docx/SKILL.md` before writing any generation code.

### Document hierarchy

The document has two levels above the body:

- **Title** — a document-title styled element (large, bold). Not a heading. Not numbered.
  Example: "Delivery 2 — Compute, Storage, Database & Remote State"
  In docx-js: a Paragraph with a large bold TextRun (e.g. size 48, bold), not `HeadingLevel`.

- **H1 sections** — numbered `1.` through `10.`, rendered with `HeadingLevel.HEADING_1`.
  Numbers are written explicitly in the heading text ("1. Delivery Information", etc.).

- **H2 sub-sections** — numbered within their parent (e.g. "2.1 Deliverable A"), used
  inside Assignment Specification.

- **H3** — used for named sub-sub-topics within a deliverable (e.g. "Requirements — RDS").

### Section order

| H1 # | Section name | Notes |
|------|-------------|-------|
| 1 | Delivery Information | 2-column table. No prose. |
| 2 | What This Delivery Builds | Goal statement + bullet list of outcomes. No recap of prior deliveries. |
| 3 | Assignment Specification | H2 per deliverable (A, B, C…). Each: equivalence caption → equivalence table → requirements → evidence. |
| 4 | MD Written Summary | Exactly 5 numbered points. Fresh `reference` key per list. |
| 5 | Common Pitfalls | Bulleted. Bold label + explanation per item. |
| 6 | Submission Instructions | 2-column table. Always verbatim (see spec below). |
| 7 | Reference Commands | Verbatim CLI in Courier New. H2 per topic. |
| 8 | Reference Documentation | 2-column table: Resource \| URL. Delivery-specific (see Section 6). |
| 9 | Academic Integrity Reminder | Standard boilerplate. Page break before this section. |
| 10 | Grading Rubric | Summary table only — detailed rubric lives in the XLSX. Page break before this section. |

---

### Section 1 — Delivery Information table

2-column table (~2400 / ~6960 DXA). Labels in bold. Adapt values per delivery.

| Label | Value pattern |
|-------|---------------|
| Delivery | "Delivery N of 5 — \<topic subtitle\>" |
| Due Date | "Sunday, \<date\>, 2026 - EoD" |
| Weight | "8 points (20% of full project grade)" |
| Format | "GitHub repository (shared with instructors or public) including brief MD summary. Same repository used for Infraestructura en la Nube." |
| Team Size | "3 students — same team as Infraestructura en la Nube" |

---

### Section 6 — Submission Instructions table (always verbatim)

2-column table (~2400 / ~6960 DXA). Adapt [N], [N-1], and [date] only.

| Label | Verbatim content |
|-------|-----------------|
| Share repository | "Same repository as Infraestructura en la Nube and Delivery [N-1]. Make sure your **repository is public**. If you prefer to keep it private, make sure of adding ***jatitoam*** and ***abner-perez*** as repository collaborators with Read access. This must be done before submission time." |
| Tag the delivery | "Create a Git tag named **oyd-delivery-[N]** pointing to the commit that represents your Delivery [N] submission. Push the tag: git push origin oyd-delivery-[N]. **Grading is performed against this tag** and not necessarily to the latest commit." |
| Upload MD summary | "Commit the summary to **infra/docs/delivery-[N]-summary.md** in the same commit that receives the **oyd-delivery-[N]** tag." |
| Evidence files | "All evidence files (**infra/evidence/\*.png** or **infra/evidence/\*.txt**) must be committed to the repository and rendered inline in **infra/README.md** under a **## Evidence** section." |
| Deadline | "Sunday, [due date]. The timestamp of the **oyd-delivery-[N]** tag determines whether the submission is on time. Late penalty is based on how long after the deadline the tag is pushed." |
| Questions | "Post course-related questions in the WhatsApp group or via email to instructors. **Do not send private messages via WhatsApp to instructors about assignment content, we encourage open discussions concerning these topics.**" |

Grader names are rendered **bold + italic** (`***text***`) and hyperlinked:
- `jatitoam` → `https://github.com/jatitoam`
- `abner-perez` → `https://github.com/abner-perez`

In docx-js, use `ExternalHyperlink` wrapping a `TextRun` with `{ bold: true, italics: true }`.

---

### Section 8 — Reference Documentation table

2-column table: Resource | URL. Always delivery-specific — see Section 6 of this skill
for how to populate it. This section always sits between Reference Commands and
Academic Integrity.

---

### Formatting rules (non-negotiable)

- **Font:** Calibri 12pt body; Courier New for all code blocks
- **Emphasis:** Bold and font size only — no colors anywhere in the document
- **Lists:** `LevelFormat.BULLET` with numbering config — never unicode bullets
- **Numbered lists:** Unique `reference` string per independent list — reuse causes count carry-over
- **Tables:** `WidthType.DXA` always; dual widths (`columnWidths` + per-cell `width`); `ShadingType.CLEAR` not SOLID; never `WidthType.PERCENTAGE`
- **Page size:** US Letter (12240 × 15840 DXA), 1-inch margins, content width = 9360 DXA
- **Code blocks:** Courier New 20pt, no background box
- **Page breaks:** `new Paragraph({ children: [new PageBreak()] })` — always in a Paragraph
- **No `\n`:** Use separate `Paragraph` elements

---

### Equivalence tables

Every deliverable sub-section must include this caption (exact text, bold paragraph,
no colon, immediately above the table):

> **Allowed service equivalences (choose at least one depending on your chosen provider)**

Then a 3-column table: Provider | AWS | GCP.

**Always verify against the current Infraestructura en la Nube project document
before writing any equivalence table.** If the document is not in context, ask
the user before proceeding.

Current known equivalences (confirm each delivery):

| Category | AWS | GCP |
|----------|-----|-----|
| Compute | EC2 / Lambda / ECS Fargate | Compute Engine / Cloud Functions / Cloud Run |
| Storage | Amazon S3 | Google Cloud Storage |
| Database | RDS / DynamoDB | Cloud SQL / Firestore |
| Networking | VPC, ALB, API Gateway | VPC, Cloud Load Balancing, API Gateway |
| Async | SQS + DLQ, SNS, EventBridge | Pub/Sub, Cloud Tasks, Cloud Scheduler |
| Container registry | Amazon ECR | Google Artifact Registry |
| Secrets | AWS Secrets Manager | Google Secret Manager |
| Encryption | AWS KMS (CMK) | Google Cloud KMS (CMEK) |
| IAM | IAM roles + policies | Service accounts + IAM bindings |
| Observability | CloudWatch | Cloud Monitoring + Cloud Logging |
| CI auth | GitHub Actions OIDC → AWS | GitHub Actions OIDC → GCP |

---

### Path conventions — infra/ boundary (non-negotiable)

Every file path in the document must be prefixed with `infra/`.
Exception: `.github/workflows/` stays at the repo root.

| ✗ Wrong | ✓ Correct |
|---------|-----------|
| `README.md` | `infra/README.md` |
| `evidence/compute.png` | `infra/evidence/compute.png` |
| `docs/delivery-2-summary.md` | `infra/docs/delivery-2-summary.md` |
| `modules/compute/` | `infra/modules/compute/` |
| `envs/dev/` | `infra/envs/dev/` |

Before running the build script, grep for bare paths and fix all occurrences.

---

## 5. Rubric — Generated via rubric-creator skill

**Do not write ad-hoc openpyxl rubric scripts.** The XLSX is always produced by
the `rubric-creator` skill using the completed DOCX as input.

### Pre-flight check

Before triggering rubric generation, verify `rubric-creator` appears in
`available_skills`. If it does not: **stop, alert the user, and do not proceed.**

```
⚠️  The rubric-creator skill is required but not loaded.
    Please install it and restart the conversation before continuing.
```

### How to invoke rubric-creator for this course

Pass the following as context when triggering the skill:

1. **Input:** The completed DOCX assignment document for this delivery.
2. **Total points:** 150 — broken down as:
   - 100 pts base criteria (rubric-creator decides the distribution)
   - 40 pts Optional EKS track (always present, Score defaults to 0%)
   - 10 pts Optional External CI Provider (always present, Score defaults to 0%)
3. **Performance levels:** Meets (100%) / Partially Meets (60%) / Does Not Meet (0%)
4. **Language:** English
5. **Output directory:** `/home/claude/delivery<N>/`

The rubric-creator skill handles criterion design, the markdown preview/approval
loop, JSON generation, and XLSX output via its own `generate_rubric.py` script.
Do not bypass its Step 3 (review in chat) — the user must approve the rubric table
before the file is generated.

### Mandatory criteria to inject regardless of rubric-creator's output

After the skill proposes its criteria but before the user approves, verify that
the following criteria are present with at least the minimum points shown. If any
are missing or underweighted, add or adjust them and re-present the table:

| Criterion | Min pts | Notes |
|-----------|---------|-------|
| Code Quality | 8 | File separation, all vars/outputs described, no hardcoded env values |
| MD Written Summary | 10 | 5 required points with specificity |
| [Optional] EKS Cluster | 40 | Score defaults to 0%; added to base score |
| [Optional] External CI Provider | 10 | Score defaults to 0%; added to base score |

### Standard language for mandatory criteria

Use this wording verbatim for the four criteria above:

**Code Quality:**
- Meets: Separate `main.tf`, `variables.tf`, `outputs.tf` per module. All variables and outputs have `description` fields. No environment-specific values hardcoded where variables should be used. Consistent naming and navigable repository structure.
- Partially Meets: File separation present but incomplete in ≥1 module, or a few description fields missing.
- Does Not Meet: ≥2 modules use a single monolithic `.tf` file, or descriptions absent from the majority of variables and outputs.

**MD Written Summary:**
- Meets: `infra/docs/delivery-N-summary.md` addresses all 5 required points with specificity tied to the team's actual configuration and decisions — not generic descriptions.
- Partially Meets: ≥3 of 5 points addressed with adequate detail; 1–2 points superficial or missing a required artifact (e.g., plan output excerpt, init output).
- Does Not Meet: File absent, fewer than 3 points addressed, or content is generic with no reference to the team's actual infrastructure.

**Optional EKS Cluster (40 pts — Score defaults to 0%):**
- Meets: EKS cluster provisioned via `terraform-aws-modules/eks`. ≥1 managed node group with min/max/desired/instance_type as input variables. Cluster endpoint, CA certificate, and cluster name exposed as Terraform outputs. `kubectl get nodes` output showing ≥1 Ready node saved as `infra/evidence/eks-nodes.png` and rendered in `infra/README.md`.
- Partially Meets: ≥3 of the above requirements met. Node group present but ≥1 variable hardcoded, or kubectl evidence is missing or shows nodes in NotReady state.
- Does Not Meet: EKS cluster absent, fewer than 3 requirements met, or the cluster is provisioned but not reachable via kubectl.

**Optional External CI Provider (10 pts — Score defaults to 0%):**
- Meets: Written pre-approval from instructors committed to the repository. All required pipeline behaviors implemented with functional equivalence to the GitHub Actions specification for this delivery. Pipeline definitions live in the repository. Credentials injected via the tool's native secrets mechanism — none hardcoded in any committed file.
- Partially Meets: Pre-approval documented and the pipeline executes, but 1 required step is missing or functionally incomplete. Credential hygiene is maintained.
- Does Not Meet: Pre-approval not documented in the repository, fewer than 3 required pipeline steps implemented, pipeline definitions stored outside the repository, or credentials hardcoded anywhere.

---

## 6. Reference Documentation — how to populate Section 8

Section 8 is not a static catalogue — it is assembled fresh for each delivery
based on the tools, providers, and modules actually used.

### Always include at the top (every delivery)

| Resource | URL |
|----------|-----|
| Terraform documentation | developer.hashicorp.com/terraform/docs |
| AWS Provider for Terraform | registry.terraform.io/providers/hashicorp/aws |
| Google Provider for Terraform | registry.terraform.io/providers/hashicorp/google |

### Delivery-specific links — how to find them

After the assignment specification is written, identify every tool, CLI command,
Terraform module, GitHub Action, and cloud service referenced in the document.
For each one, search for the current canonical documentation URL using web_search.

Typical categories to search per delivery:

- **Terraform backends:** S3 backend (D2), GCS backend (D2) — search "terraform s3 backend docs"
- **terraform-aws-modules:** One entry per module used — search "terraform registry \<module-name\>"
- **GitHub Actions:** Only include actions that appear in the delivery's pipeline spec
- **AWS CLI:** Include if the delivery requires manual CLI commands as evidence
- **Cloud SDK (gcloud):** Include for GCP teams if CLI commands appear in the spec
- **Service-specific docs:** e.g., "AWS DynamoDB developer guide", "Amazon RDS user guide"
- **Kubernetes docs:** Include only for deliveries that touch EKS or manifests

Do not include links for services not mentioned in the delivery. Do not include
links already covered by the "always include" set above.

---

## 7. Evidence Requirements

All evidence paths must use the `infra/` prefix.

| Type | Artifact | Rendered in |
|------|----------|-------------|
| CLI output (deployed resource) | `infra/evidence/<n>.txt` | `infra/README.md` → `## Evidence` |
| Screenshot (K8s, running app) | `infra/evidence/<n>.png` | `infra/README.md` → `## Evidence` |
| Pipeline output | PR link + `infra/evidence/<n>.png` | `infra/README.md` → `## Evidence` |

Rule: can a grader verify this without access to the student's machine or account?
If not, strengthen the evidence requirement.

---

## 8. MD Written Summary — 5-point template

Always exactly 5 numbered points. Fresh `reference` key in numbering config.

1. **Delivery-specific decision** — what was built, which service chosen, rationale
2. **Module / architecture design** — structure and interface decisions
3. **Operational / workflow step** — migration, pipeline stages, bootstrap, etc.
4. **Security or credential handling** — how secrets and access are managed
5. **Two architectural trade-offs** — one paragraph each

---

## 9. File Generation Workflow

### DOCX

```bash
mkdir -p /home/claude/delivery<N>
cd /home/claude/delivery<N>
npm install docx
```

Write `build_doc.js`, run `node build_doc.js`.
Validate: `python3 /mnt/skills/public/docx/scripts/office/validate.py Delivery_<N>_Assignment.docx`
Expected: `All validations PASSED!`

### XLSX

Delegate entirely to the `rubric-creator` skill (see Section 5).
Output lands in `/home/claude/delivery<N>/` per the output directory passed to the skill.

### Delivery

```bash
cp /home/claude/delivery<N>/Delivery_<N>_Assignment.docx /mnt/user-data/outputs/
cp /home/claude/delivery<N>/rubrica_*.xlsx               /mnt/user-data/outputs/Delivery_<N>_Rubric.xlsx
```

`present_files`: DOCX first, XLSX second.

---

## 10. Common Generation Bugs — check before presenting

- **Numbered list carry-over:** Unique `reference` string per independent numbered list.
- **Table width mismatch:** `columnWidths` must sum exactly to table `width` (9360 DXA).
- **Wrong infra/ paths:** Grep the build script for bare `README.md`, `evidence/`, `docs/`, `modules/` — all need `infra/` prefix. Exception: `.github/workflows/`.
- **Wrong equivalence caption:** Must read exactly "Allowed service equivalences (choose at least one depending on your chosen provider)".
- **Grader names not hyperlinked:** jatitoam and abner-perez must use `ExternalHyperlink` in docx-js, bold+italic, pointing to their GitHub profiles.
- **Page break not in Paragraph:** Always `new Paragraph({ children: [new PageBreak()] })`.
- **ShadingType.SOLID:** Always `ShadingType.CLEAR`.
- **Title styled as H1:** The document title uses a large bold TextRun, not `HeadingLevel.HEADING_1`. H1 is reserved for the numbered sections 1–10.
- **rubric-creator not checked:** Always verify the skill is in `available_skills` before attempting XLSX generation.
