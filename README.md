# Teaching Claude Plugin Marketplace

A curated collection of Claude plugins — skills, slash commands, and MCP servers — for teaching and academic workflows.

## Structure

```
plugins/
└── <plugin-id>/
    ├── plugin.yaml          # Plugin metadata
    ├── skills/
    │   └── <skill-id>/
    │       ├── SKILL.md     # Skill definition (triggers, steps, behavior)
    │       ├── scripts/     # Helper scripts invoked by the skill
    │       └── references/  # Reference docs read by Claude at runtime
    ├── commands/            # Slash commands (optional)
    └── mcp/                 # MCP server definitions (optional)
index.yaml                   # Top-level registry of all plugins
```

## Plugins

| Plugin | Description | Skills | Commands | MCP Servers |
|--------|-------------|--------|----------|-------------|
| [course-factory](plugins/course-factory) | Course-agnostic harness: bootstrap a per-course harness and produce session plans, examples, exercises, slides, labs, exams, homework, readings, project deliveries, presentation guides, Miro boards, and Google Doc publications | 18 | — | — |
| [evaluation-rubrics](plugins/evaluation-rubrics) | Create grading rubrics, evaluate student submissions, and rebuild cumulative grade files | 3 | — | — |
| [exam-creator](plugins/exam-creator) | Generate multiple-choice exams from course content, shuffle N versions with answer keys, and export to Google Docs | 3 | — | — |
| [google-drive-creation](plugins/google-drive-creation) | General-purpose Google Doc and Google Slides creation with named styles, code blocks, and inline formatting | 2 | — | — |

## Plugin Concepts

| Concept | What it is |
|---------|-----------|
| **Skill** | A `SKILL.md` file that instructs Claude to follow a specific multi-step workflow when triggered by certain user phrases. Can include helper scripts and reference documents. |
| **Command** | A slash command (e.g. `/grade`) that invokes a skill or workflow directly. |
| **MCP Server** | A Model Context Protocol server that exposes tools, resources, or prompts to Claude. |

## Bumping a Plugin Version

Five places must be updated in sync — the CLI reads each one for a different purpose:

| File | Why it must be updated |
|------|------------------------|
| `plugins/<plugin-id>/.claude-plugin/plugin.json` | Version authority for `claude plugin update` — **this is what the CLI checks** |
| `plugins/<plugin-id>/plugin.yaml` | Canonical plugin definition |
| `.claude-plugin/marketplace.json` (plugin entry) | Repo registry used by `claude plugin install` |
| `.claude-plugin/marketplace.json` (top-level `version`) | Controls whether `claude plugin marketplace update` fetches fresh data at all |
| `index.yaml` | Top-level registry entry for the plugin |

## Updating the plugin locally

When the plugin is updated remotely, the marketplace and plugin must be updated locally to reflect the new version. Run:

```bash
claude plugin marketplace update <marketplace-id>
claude plugin update <plugin-id>@<marketplace-id>
```

The marketplace must be refreshed first — otherwise the CLI reads a stale registry and reports the old version as latest.

## Adding a New Plugin

1. Create a directory under `plugins/<your-plugin-id>/`.
2. Add a `plugin.yaml` with `name`, `display_name`, `description`, `version`, and lists of `skills`, `commands`, and `mcp_servers`.
3. Add a `plugins/<your-plugin-id>/.claude-plugin/plugin.json` with `name`, `description`, and `version` (the minimal manifest the CLI uses for update detection).
4. Add each skill under `skills/<skill-id>/SKILL.md`. Follow the existing skills as a template.
5. Register the plugin in `index.yaml` and in `.claude-plugin/marketplace.json`.

### plugin.yaml schema

```yaml
name: my-plugin
display_name: My Plugin
description: What this plugin does.
version: 1.0.0
skills:
  - id: my-skill
    path: skills/my-skill
commands: []
mcp_servers: []
```

### SKILL.md frontmatter

```yaml
---
name: skill-name
description: >
  One or two sentences describing when Claude should activate this skill.
  Include trigger phrases.
---
```
