# Google Doc Style Spec

Reference for `scripts/create-gdoc.py`. Describes every supported element type,
the style each maps to, and the code block formatting applied by the script.

---

## Named paragraph styles

Named styles (Title, Subtitle, Heading 1–4, Normal text) are applied by name only.
The script does NOT override font, size, or color for these — the Google account's
default theme provides all that. Whatever the account owner has customized for those
named styles is exactly what the document will use.

| JSON `type`      | Google Docs named style |
|------------------|------------------------|
| `title`          | TITLE                  |
| `subtitle`       | SUBTITLE               |
| `heading1`       | HEADING_1              |
| `heading2`       | HEADING_2              |
| `heading3`       | HEADING_3              |
| `heading4`       | HEADING_4              |
| `paragraph`      | NORMAL_TEXT (default)  |

---

## Code block style (explicit — not from account defaults)

Applied to `type: "code"` elements and to tables (which are rendered as code).

| Property         | Value                        |
|------------------|------------------------------|
| Font             | Courier New                  |
| Size             | 9.5 pt                       |
| Background       | #272822 (Monokai dark)       |
| Default text     | #F8F8F2 (Monokai light gray) |
| Line spacing     | 100 % (no extra gaps)        |
| Space above/below| 0 pt                         |

When `"language"` is provided, Pygments tokenizes the code and applies Monokai
syntax colors per token via individual `foregroundColor` requests. Without
`"language"`, the block renders in the default `#F8F8F2` text on dark background.

**Monokai token colors:**

| Token category          | Color   | Hex       |
|-------------------------|---------|-----------|
| Default text            | white   | `#F8F8F2` |
| Comments                | gray    | `#75715E` |
| Keywords                | pink    | `#F92672` |
| Strings                 | yellow  | `#E6DB74` |
| Numbers                 | purple  | `#AE81FF` |
| Functions / classes     | green   | `#A6E22E` |
| Builtins / types        | cyan    | `#66D9EF` |
| Operators               | pink    | `#F92672` |
| Docstrings              | gray    | `#75715E` |

Inline code spans (`"style": "code"` inside a `spans` array) get only the font
and size — they appear in normal paragraphs (light background) so no foreground
color override is needed.

**Dependencies:** `pip install pygments` — if not installed, code blocks render
in default text color without syntax highlighting (no error).

---

## Header block

`header` is an array of `{label, value}` pairs rendered as bold-label lines
before the body. Any number of pairs, in the order given.

```json
"header": [
  { "label": "Course",       "value": "Introduction to Cloud Automation" },
  { "label": "Session",      "value": "3 — May 7, 2026" },
  { "label": "Time allowed", "value": "30 minutes" }
]
```

---

## Script invocation

```
python plugins/google-drive-creation/skills/gdoc-creator/scripts/create-gdoc.py \
  <json_file> <folder_url_or_id> "<doc_title>"
```

| Argument | Required | Description |
|---|---|---|
| `json_file` | Yes | Path to the JSON body spec |
| `folder_url_or_id` | Yes | Drive folder URL or bare folder ID — the script extracts the ID from the URL automatically |
| `doc_title` | Yes | Title used for both the Drive filename and the `TITLE`-styled first paragraph |

The script prints the Google Doc URL to stdout. The doc is moved into the specified
folder immediately after creation.

---

## Full JSON schema

The JSON file contains only `header` and `body` — title and folder come from CLI args.

```json
{
  "header": [
    { "label": "Label", "value": "Value" }
  ],
  "body": [ ]
}
```

### Body element types

**Headings and plain paragraphs**

```json
{ "type": "heading1", "text": "Section" }
{ "type": "heading2", "text": "Sub-section" }
{ "type": "heading3", "text": "Detail" }
{ "type": "heading4", "text": "Sub-detail" }
{ "type": "paragraph", "text": "Plain body text." }
```

**Paragraph or heading with inline formatting** — use `spans` instead of `text`:

```json
{
  "type": "paragraph",
  "spans": [
    { "text": "Run ", "style": "normal" },
    { "text": "terraform apply", "style": "code" },
    { "text": " to provision resources.", "style": "normal" }
  ]
}
```

Allowed `style` values: `normal`, `bold`, `italic`, `bold_italic`, `code`.
Headings support `spans` too.

**Code block** — for file contents, CLI commands, directory trees, shell output:

```json
{ "type": "code", "language": "ruby", "text": "require 'socket'\nrequire 'json'\n\nPORT = 8080" }
```

`language` is optional. When present, Pygments tokenizes the code and applies
Monokai syntax colors. Omit for shell output, directory trees, or any content
that should not be syntax-highlighted (plain Monokai text on dark background).

Common language identifiers: `python`, `ruby`, `javascript`, `typescript`,
`terraform`, `yaml`, `bash`, `dockerfile`, `json`, `hcl`, `go`, `java`.

**Lists**

```json
{ "type": "bullet_list",   "items": ["First item", "Second item"] }
{ "type": "numbered_list", "items": ["Step one", "Step two"] }
```

List items may be span arrays for inline formatting:

```json
{
  "type": "bullet_list",
  "items": [
    {
      "spans": [
        { "text": "environment", "style": "code" },
        { "text": " — string, no default", "style": "normal" }
      ]
    }
  ]
}
```

**Table** — rendered as a fixed-width monospace code block:

```json
{
  "type": "table",
  "headers": ["Option", "Instance type", "AMI", "Best for"],
  "rows": [
    ["arm64", "t4g.nano", "ami-0ddb64e71e68cf624", "macOS M-series"],
    ["x86_64", "t3.micro", "ami-0d43f0bb92e485897", "Windows, Intel Mac"]
  ]
}
```

---

## Credentials and setup

- OAuth credentials: `~/.config/teaching-claude-plugin/credentials.json`
- Token cache: `~/.config/teaching-claude-plugin/token.json` (auto-created on first run)
- First run opens a browser tab for Google authorization; subsequent runs are silent.

Required Python packages:
```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib pygments
```
