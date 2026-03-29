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
| [evaluation-rubrics](plugins/evaluation-rubrics) | Create grading rubrics and evaluate student submissions | 2 | — | — |

## Plugin Concepts

| Concept | What it is |
|---------|-----------|
| **Skill** | A `SKILL.md` file that instructs Claude to follow a specific multi-step workflow when triggered by certain user phrases. Can include helper scripts and reference documents. |
| **Command** | A slash command (e.g. `/grade`) that invokes a skill or workflow directly. |
| **MCP Server** | A Model Context Protocol server that exposes tools, resources, or prompts to Claude. |

## Adding a New Plugin

1. Create a directory under `plugins/<your-plugin-id>/`.
2. Add a `plugin.yaml` with `name`, `display_name`, `description`, `version`, and lists of `skills`, `commands`, and `mcp_servers`.
3. Add each skill under `skills/<skill-id>/SKILL.md`. Follow the existing skills as a template.
4. Register the plugin in `index.yaml`.

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
