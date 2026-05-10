# Exercise Specs

Read this file when building **exercise Google Docs** (Step 3).

Also read `references/exercise-gdoc-spec.md` for the JSON schema, style mapping, and how to run the generation script.

---

## Design rules

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

---

## Copy-paste blocking

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

---

## Evidence requirement

Every exercise must include a verifiable artifact:

- **Running resource**: CLI command output saved as `evidence/<n>.txt`, rendered
  inline in `README.md` under `## Evidence`
- **Visual output** (K8s, running apps): screenshot saved as `evidence/<n>.png`,
  rendered inline in `README.md` under `## Evidence`
- **Pipeline output** (CI/CD, GitHub Actions): link to the PR + screenshot of the
  result, saved as `evidence/<n>.png`

Test: *can a grader verify this passed without access to the student's machine?*

---

## Submission instructions (verbatim in every exercise)

```
Initialize a new repository called oyd-exercise-<session>-<n> and commit/push
everything into it. Submit the repository URL only.
```

---

## Section order

1. **Title** — `Exercise <session>.<n> — <Title>`
2. **Header block** — Course name, Session date, Time allowed, Submission instructions
   (bold labels)
3. **H1 Context** — scenario / starter code; code blocks for any provided file content
4. **H1 Setup** — H2 Prerequisites, H2 Architecture (if choices exist), H2 Repository structure
5. **H1 Tasks** — H2 per task, bullet or numbered lists for sub-requirements
6. **H1 Acceptance Criteria** — bullet list of what a passing submission looks like

See `references/exercise-gdoc-spec.md` for the full JSON schema and formatting rules.
