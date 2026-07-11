<!--
  NEXT-AGENT-PROMPT TEMPLATE — course-factory / course-bootstrap
  ===============================================================
  Copied to <course>/.claude/refs/templates/next-agent-prompt.md. The two blocks below are what
  every orchestrator emits to close its turn. Content-facing labels are localized to
  course.language at bootstrap; skill slugs and the PROTOCOL path stay literal. {{course_label}} =
  "<course_name> <course_code>". DELETE bootstrap comments when generating.
-->
# Closing format for every agent

> Every orchestrator ends its turn by emitting **these two blocks**, in this order.

## 1) Summary for the conductor (human)

```
✅ Artifact: <name>  ·  Session S<NN>  (or Delivery D<n> / Checkpoint / Final)
Produced: <file(s)>
To validate: <2–4 concrete things the human should review>
Decisions I made: <the ones that matter>
Pending / alerts: <blockers, missing MCP/prerequisite, questions>
```

## 2) PROMPT FOR THE NEXT AGENT (ready to copy)

Emit a code block with the **skill invocation** for the next artifact. Example:

```
/<next-slug> — Session <NN>, course {{course_label}}. Start from zero:
follow .claude/refs/PROTOCOL.md §2 (bootstrap) and the session handover.
```

Rules:
- The next prompt points to the **next artifact in the session-type sequence** (`PROTOCOL.md` §10),
  using a slug from `artifacts.enabled`. **Do not hardcode a specific next slug** — read it from the
  sequence for this session's type. If the session finished all its artifacts, the next prompt is
  **`/session-planning` for S<NN+1>**.
- Keep the prompt **short**: `/<slug>` + session (or delivery) + "start from zero" + pointer to
  `.claude/refs/PROTOCOL.md` §2. All the context comes from the documents, not the prompt.
- If the human **must** do something before launching the next agent (validate, drop the `.pptx`,
  set `MIRO_TOKEN`, create a portal assignment, confirm a Sheet converted), say so explicitly
  **before** the prompt.
