#!/usr/bin/env python3
"""Merge frames-index/batch-*.json (written by Haiku indexers) into frames-index.json.

Usage: merge_index.py <pack_dir>
Checks every kept frame in frames.json is described exactly once; exits 1 listing gaps.
"""
import json
import sys
from pathlib import Path


def main():
    pack = Path(sys.argv[1])
    frames = json.loads((pack / "frames.json").read_text())["frames"]
    entries = {}
    for batch in sorted((pack / "frames-index").glob("batch-*.json")):
        for e in json.loads(batch.read_text()):
            if e["file"].startswith("index-frames/"):   # indexers read the 1280 px copies
                e = dict(e, file="frames/" + e["file"].split("/", 1)[1])
            entries[e["file"]] = e
    want = [f["file"] for f in frames]
    missing = [f for f in want if f not in entries]
    extra = sorted(set(entries) - set(want))
    index = [dict(entries[f], t=fr["t"], mmss=fr["mmss"],
                  static_until_mmss=fr.get("static_until_mmss", fr["mmss"]))
             for fr in frames for f in [fr["file"]] if f in entries]
    (pack / "frames-index.json").write_text(json.dumps(
        {"contract": "video-evidence/2", "count": len(index), "frames": index},
        indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": not missing, "indexed": len(index), "missing": missing,
                      "unknown_files": extra}))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
