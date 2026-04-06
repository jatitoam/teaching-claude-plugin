# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A Claude plugin marketplace for teaching and academic workflows. Plugins are collections of **skills**, **commands**, and **MCP servers** installed into Claude Code.

## No Build System

There is no build step, no package manager, and no test suite. Development is editing YAML, Markdown, and Python files directly.

The only runtime dependency is `openpyxl` (used by the Python helper scripts). Install with:

```bash
pip install openpyxl
```

## Plugin Architecture

```
plugins/<plugin-id>/
├── plugin.yaml          # Plugin metadata and skill/command/mcp_server lists
├── skills/<skill-id>/
│   ├── SKILL.md         # Instructs Claude how to behave when the skill is triggered
│   ├── scripts/         # Python scripts Claude invokes during skill execution
│   └── references/      # Markdown docs Claude reads at runtime for context
```

- `index.yaml` — top-level registry; must be updated when adding a plugin
- `.claude-plugin/marketplace.json` — marketplace distribution metadata

## How Skills Work

A skill is activated when Claude recognizes the user's intent matches the skill's `description` in `SKILL.md` frontmatter. Claude then follows the numbered steps in that file, consulting `references/` docs and invoking `scripts/` via shell commands.

**Common pattern:** Claude generates a JSON intermediate file and either passes it to a Python script to produce a formatted output (e.g. `.xlsx`), or writes the JSON directly as the final artifact — depending on the skill's design.

## Adding a New Plugin

1. Create `plugins/<plugin-id>/plugin.yaml` (see schema in README.md)
2. Add skills under `plugins/<plugin-id>/skills/<skill-id>/SKILL.md`
3. Register the plugin in `index.yaml`
4. Update `.claude-plugin/marketplace.json` if publishing to the marketplace

## Versioning

When modifying a plugin, bump its `version` in all three of these files:

1. `plugins/<plugin-id>/.claude-plugin/plugin.json` — version the CLI reads for update detection
2. `plugins/<plugin-id>/plugin.yaml` — canonical plugin definition
3. `.claude-plugin/marketplace.json` — marketplace registry

## Updating the Plugin Locally

When the plugin is updated remotely, run these two commands in order to update the marketplace and plugin locally:

```bash
claude plugin marketplace update <marketplace-id>
claude plugin update <plugin-id>@<marketplace-id>
```

The marketplace refresh must come first — skipping it causes the CLI to report the old version as latest.
