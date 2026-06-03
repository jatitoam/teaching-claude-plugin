---
name: gslides-creator
description: >
  General-purpose Google Slides creation skill. Creates a styled Google Slides
  presentation from a JSON spec via the Google Slides API. Supports all PDDS slide
  types (title_slide, agenda, section_divider, content, concept, diagram, demo_marker,
  step, callout, exercise, code). Not triggered directly by the user — invoked by other
  skills (e.g., pdds-session-builder) as the final creation step.
---

# Google Slides Creator

Creates a styled Google Slides presentation from a JSON spec in one pass:
1. Creates an empty presentation via the Slides API
2. Builds all slides and formatting as a single `batchUpdate` request batch
3. Deletes the default empty slide
4. Moves the presentation to the target Drive folder
5. Prints the resulting Google Slides URL

---

## When to use this skill

Use when you have a fully populated JSON spec (matching the schema in
`references/gslides-style-spec.md`) and need to produce a Google Slides presentation.

This skill is **not** triggered by user phrases — it is invoked by other skills
(e.g., `pdds-session-builder`) as the final creation step after content is ready.

---

## Prerequisites

Python packages (install once):
```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

OAuth credentials: `~/.config/teaching-claude-plugin/credentials.json`
Token cache (auto-created on first run): `~/.config/teaching-claude-plugin/token-slides.json`

First run opens a browser tab for Google authorization. Subsequent runs are silent.

---

## Protocol

1. Read `references/gslides-style-spec.md` to confirm the JSON schema before generating.
2. Write the JSON spec to `/mnt/user-data/outputs/<filename>.json`.
3. Run the script:
   ```
   python plugins/google-drive-creation/skills/gslides-creator/scripts/create-gslides.py \
     /mnt/user-data/outputs/<filename>.json \
     "<folder_url_or_id>" \
     "<presentation_title>"
   ```
4. The script prints the Google Slides URL. Present it to the user.

---

## Style reference

Read `references/gslides-style-spec.md` for:
- The full JSON schema with all supported slide types
- Color palette (hex codes and their semantic use)
- Per-slide-type field documentation with example JSON
- Credentials and setup details
