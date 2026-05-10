#!/usr/bin/env python3
"""
create-gdoc.py — Creates a styled Google Doc from a JSON spec.

Usage:
    python create-gdoc.py <json_file> <folder_url_or_id> <doc_title>

Arguments:
    json_file        Path to the JSON body spec (see references/gdoc-style-spec.md)
    folder_url_or_id Google Drive folder URL or bare folder ID
    doc_title        Title for the Google Doc (used as both the Drive filename
                     and the TITLE-styled first paragraph)

Prints the Google Doc URL to stdout.
"""
import json
import os
import re
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

try:
    from pygments import lex
    from pygments.lexers import get_lexer_by_name
    from pygments.token import Token, Comment, Keyword, Name, Literal, Operator, Punctuation, Generic
    PYGMENTS = True
except ImportError:
    PYGMENTS = False

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]
CREDS_PATH = os.path.expanduser("~/.config/teaching-claude-plugin/credentials.json")
TOKEN_PATH = os.path.expanduser("~/.config/teaching-claude-plugin/token.json")

CODE_FONT = "Courier New"
CODE_SIZE_PT = 9.5

# ── Monokai palette ──────────────────────────────────────────────────────────

def _rgb(h):
    h = h.lstrip("#")
    return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}

CODE_BG  = _rgb("272822")  # Monokai background
CODE_FG  = _rgb("F8F8F2")  # Monokai default text

# Maps Pygments token types → Monokai RGB dicts (traversed bottom-up at runtime)
MONOKAI = {}
if PYGMENTS:
    MONOKAI = {
        Token:                   _rgb("F8F8F2"),  # default
        Comment:                 _rgb("75715E"),  # gray
        Keyword:                 _rgb("F92672"),  # pink
        Keyword.Type:            _rgb("66D9EF"),  # cyan
        Name.Function:           _rgb("A6E22E"),  # green
        Name.Class:              _rgb("A6E22E"),
        Name.Decorator:          _rgb("A6E22E"),
        Name.Namespace:          _rgb("A6E22E"),
        Name.Attribute:          _rgb("A6E22E"),
        Name.Tag:                _rgb("F92672"),  # HTML/XML tags
        Name.Builtin:            _rgb("66D9EF"),  # cyan
        Name.Builtin.Pseudo:     _rgb("F8F8F2"),  # self, cls
        Literal.String:          _rgb("E6DB74"),  # yellow
        Literal.String.Doc:      _rgb("75715E"),  # docstrings → comment color
        Literal.Number:          _rgb("AE81FF"),  # purple
        Operator:                _rgb("F92672"),  # pink
        Operator.Word:           _rgb("F92672"),
        Punctuation:             _rgb("F8F8F2"),
        Generic.Output:          _rgb("75715E"),
        Generic.Prompt:          _rgb("F92672"),
    }

def _monokai_color(token_type):
    """Walk the Pygments token hierarchy to find the closest Monokai match."""
    t = token_type
    while t is not None:
        if t in MONOKAI:
            return MONOKAI[t]
        t = t.parent if hasattr(t, "parent") else None
    return CODE_FG

# ── Docs API helpers ─────────────────────────────────────────────────────────

NAMED_STYLES = {
    "title": "TITLE",
    "subtitle": "SUBTITLE",
    "heading1": "HEADING_1",
    "heading2": "HEADING_2",
    "heading3": "HEADING_3",
    "heading4": "HEADING_4",
}


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as fh:
            fh.write(creds.to_json())
    return creds


def pt(n):
    return {"magnitude": n, "unit": "PT"}


def fg(color_dict):
    return {"color": {"rgbColor": color_dict}}


def bg(color_dict):
    return {"color": {"rgbColor": color_dict}}


# ── Builder ──────────────────────────────────────────────────────────────────

class Builder:
    """Accumulates insertText and style requests; flushed in two batchUpdate calls."""

    def __init__(self):
        self.cursor = 1  # Docs body content starts at index 1
        self.inserts = []
        self.styles = []

    # ── primitives ──────────────────────────────────────────────────────────

    def _insert(self, text):
        start = self.cursor
        self.inserts.append(
            {"insertText": {"location": {"index": start}, "text": text}}
        )
        self.cursor += len(text)
        return start, self.cursor

    def _named_style(self, start, end, style_key):
        if style_key in NAMED_STYLES:
            self.styles.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "paragraphStyle": {"namedStyleType": NAMED_STYLES[style_key]},
                    "fields": "namedStyleType",
                }
            })

    def _inline_style(self, start, end, style):
        if style == "bold":
            self.styles.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "textStyle": {"bold": True}, "fields": "bold",
            }})
        elif style == "italic":
            self.styles.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "textStyle": {"italic": True}, "fields": "italic",
            }})
        elif style == "bold_italic":
            self.styles.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "textStyle": {"bold": True, "italic": True}, "fields": "bold,italic",
            }})
        elif style == "code":
            self.styles.append({"updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "textStyle": {
                    "weightedFontFamily": {"fontFamily": CODE_FONT},
                    "fontSize": pt(CODE_SIZE_PT),
                },
                "fields": "weightedFontFamily,fontSize",
            }})

    # ── element builders ────────────────────────────────────────────────────

    def paragraph(self, text, style=None):
        start, end = self._insert(text + "\n")
        self._named_style(start, end, style)
        return start, end

    def spans_paragraph(self, spans, style=None):
        full = "".join(s["text"] for s in spans)
        start, end = self._insert(full + "\n")
        self._named_style(start, end, style)
        cursor = start
        for span in spans:
            span_end = cursor + len(span["text"])
            self._inline_style(cursor, span_end, span.get("style", "normal"))
            cursor = span_end
        return start, end

    def header_line(self, label, value):
        """Bold-label line: 'Label: value'."""
        text = f"{label}: {value}\n"
        start, end = self._insert(text)
        self.styles.append({"updateTextStyle": {
            "range": {"startIndex": start, "endIndex": start + len(label) + 1},
            "textStyle": {"bold": True}, "fields": "bold",
        }})
        return start, end

    def code_block(self, text, language=None):
        lines = text.split("\n")
        while lines and lines[-1] == "":
            lines.pop()
        if not lines:
            return

        full_text = "\n".join(lines) + "\n"
        block_start = self.cursor
        self._insert(full_text)
        block_end = self.cursor

        # Paragraph style: dark background + tight spacing (applies to all lines)
        self.styles.append({"updateParagraphStyle": {
            "range": {"startIndex": block_start, "endIndex": block_end},
            "paragraphStyle": {
                "shading": {"backgroundColor": bg(CODE_BG)},
                "spaceAbove": pt(0),
                "spaceBelow": pt(0),
                "lineSpacing": 100,
            },
            "fields": "shading,spaceAbove,spaceBelow,lineSpacing",
        }})

        # Base text style: monospace font + default Monokai fg for the whole block
        self.styles.append({"updateTextStyle": {
            "range": {"startIndex": block_start, "endIndex": block_end},
            "textStyle": {
                "weightedFontFamily": {"fontFamily": CODE_FONT},
                "fontSize": pt(CODE_SIZE_PT),
                "foregroundColor": fg(CODE_FG),
            },
            "fields": "weightedFontFamily,fontSize,foregroundColor",
        }})

        # Syntax highlighting (token-level color overrides)
        if language and PYGMENTS:
            self._syntax_highlight(block_start, full_text, language)

    def _syntax_highlight(self, block_start, text, language):
        try:
            lexer = get_lexer_by_name(language, stripnl=False, ensurenl=False)
        except Exception:
            return

        default_color = MONOKAI.get(Token, CODE_FG)
        char_pos = 0

        for token_type, token_value in lex(text, lexer):
            if not token_value:
                continue
            color = _monokai_color(token_type)
            # Only emit a request when the color differs from the default
            if color != default_color:
                t_start = block_start + char_pos
                t_end = t_start + len(token_value)
                self.styles.append({"updateTextStyle": {
                    "range": {"startIndex": t_start, "endIndex": t_end},
                    "textStyle": {"foregroundColor": fg(color)},
                    "fields": "foregroundColor",
                }})
            char_pos += len(token_value)

    def list_item(self, text_or_spans, preset):
        if isinstance(text_or_spans, list):
            full = "".join(s["text"] for s in text_or_spans)
            start, end = self._insert(full + "\n")
            cursor = start
            for span in text_or_spans:
                span_end = cursor + len(span["text"])
                self._inline_style(cursor, span_end, span.get("style", "normal"))
                cursor = span_end
        else:
            start, end = self._insert(text_or_spans + "\n")
        self.styles.append({"createParagraphBullets": {
            "range": {"startIndex": start, "endIndex": end},
            "bulletPreset": preset,
        }})

    def table_as_code(self, headers, rows):
        all_rows = [headers] + rows
        widths = [
            max(len(str(r[i])) for r in all_rows if i < len(r))
            for i in range(len(headers))
        ]
        sep = "  ".join("-" * w for w in widths)
        fmt = lambda row: "  ".join(str(row[i]).ljust(widths[i]) for i in range(len(row)))
        lines = [fmt(headers), sep] + [fmt(r) for r in rows]
        self.code_block("\n".join(lines))  # no language — plain Monokai text


# ── element dispatcher ───────────────────────────────────────────────────────

def process_element(b: Builder, el: dict):
    etype = el.get("type", "paragraph")

    if etype in NAMED_STYLES or etype == "paragraph":
        style = etype if etype != "paragraph" else None
        if "spans" in el:
            b.spans_paragraph(el["spans"], style=style)
        else:
            b.paragraph(el.get("text", ""), style=style)

    elif etype == "code":
        b.code_block(el.get("text", ""), language=el.get("language"))

    elif etype in ("bullet_list", "numbered_list"):
        preset = (
            "BULLET_DISC_CIRCLE_SQUARE"
            if etype == "bullet_list"
            else "NUMBERED_DECIMAL_ALPHA_ROMAN"
        )
        for item in el.get("items", []):
            if isinstance(item, str):
                b.list_item(item, preset)
            elif isinstance(item, dict):
                b.list_item(item.get("spans", item.get("text", "")), preset)

    elif etype == "table":
        b.table_as_code(el.get("headers", []), el.get("rows", []))


# ── main ─────────────────────────────────────────────────────────────────────

def parse_folder_id(value):
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", value)
    return match.group(1) if match else value


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python create-gdoc.py <json_file> <folder_url_or_id> <doc_title>",
            file=sys.stderr,
        )
        sys.exit(1)

    json_file, folder_arg, doc_title = sys.argv[1], sys.argv[2], sys.argv[3]
    folder_id = parse_folder_id(folder_arg)

    with open(json_file) as f:
        spec = json.load(f)

    creds = get_credentials()
    docs_svc = build("docs", "v1", credentials=creds)
    drive_svc = build("drive", "v3", credentials=creds)

    doc = docs_svc.documents().create(body={"title": doc_title}).execute()
    doc_id = doc["documentId"]

    drive_svc.files().update(
        fileId=doc_id,
        addParents=folder_id,
        removeParents="root",
        fields="id,parents",
    ).execute()

    b = Builder()

    b.paragraph(doc_title, style="title")

    for entry in spec.get("header", []):
        b.header_line(entry["label"], entry["value"])

    for el in spec.get("body", []):
        process_element(b, el)

    if b.inserts:
        docs_svc.documents().batchUpdate(
            documentId=doc_id, body={"requests": b.inserts}
        ).execute()
    if b.styles:
        docs_svc.documents().batchUpdate(
            documentId=doc_id, body={"requests": b.styles}
        ).execute()

    print(f"https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    main()
