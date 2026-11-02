#!/usr/bin/env python3
"""Word fingerprint of a source .md, comparable with doc-report.js `fingerprint` (same n and sha
means the Doc's words are exactly the source's, in order). Markup (#, **, |, ☐) is ignored; the
words "http"/"https" are dropped on both sides so removing the URL scheme does not count as a change.
Usage: python3 text-fingerprint.py <source.md>
Note: a Markdown link [text](url) counts both text and url here but only text in the Doc — sources
for print should carry bare URLs on their own line."""
import hashlib
import re
import sys
import unicodedata

text = unicodedata.normalize("NFC", open(sys.argv[1], encoding="utf-8").read())
words = [w for w in re.findall(r"[^\W_]+", text) if w.lower() not in ("http", "https")]
print({"n": len(words), "sha": hashlib.sha256(" ".join(words).encode()).hexdigest()[:16]})
