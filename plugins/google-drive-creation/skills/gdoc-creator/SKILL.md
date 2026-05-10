---
name: gdoc-creator
description: >
  General-purpose Google Doc creation skill. Creates a styled Google Doc from a
  JSON spec via the Google Docs API. Supports named paragraph styles (Title,
  Subtitle, Heading 1–4, Normal text), code blocks with monospace font and gray
  background, bullet and numbered lists, inline formatting spans (bold, italic,
  code), and tables rendered as monospace blocks. Named styles inherit the Google
  account's default theme — only code block formatting is applied explicitly.
  Intended to be called by other skills that have already produced a JSON spec;
  not typically triggered directly by the user.
---

# Google Doc Creator

Creates a styled Google Doc from a JSON spec in one pass:
1. Creates an empty document via the Docs API
2. Inserts all content in a single `batchUpdate`
3. Applies all formatting (named styles + code block styling) in a second `batchUpdate`
4. Prints the resulting Google Doc URL

---

## When to use this skill

Use when you have a fully populated JSON spec (matching the schema in
`references/gdoc-style-spec.md`) and need to produce a Google Doc from it.

This skill is **not** triggered by user phrases — it is invoked by other skills
(e.g., `pdds-session-builder`) as the final creation step after content is ready.

---

## Prerequisites

Python packages (install once):
```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

OAuth credentials: `~/.config/teaching-claude-plugin/credentials.json`
Token cache (auto-created on first run): `~/.config/teaching-claude-plugin/token.json`

First run opens a browser tab for Google authorization. Subsequent runs are silent.

---

## Protocol

1. Read `references/gdoc-style-spec.md` to confirm the JSON schema before generating.
2. Write the JSON spec to `/mnt/user-data/outputs/<filename>.json`.
3. Run the script:
   ```
   python plugins/google-drive-creation/skills/gdoc-creator/scripts/create-gdoc.py \
     /mnt/user-data/outputs/<filename>.json \
     "<folder_url_or_id>" \
     "<doc_title>"
   ```
4. The script prints the Google Doc URL. Present it to the user.
5. Validate: open the URL and confirm title style, heading levels, and code block
   background are correct.

---

## Style reference

Read `references/gdoc-style-spec.md` for:
- The full JSON schema with all supported element types
- Named style mapping (which `type` maps to which Google Docs named style)
- Code block formatting spec (font, size, background color, spacing)
- Inline span styles (`bold`, `italic`, `bold_italic`, `code`)
- Header block format (`[{label, value}]` array)
- Table rendering rules
