#!/usr/bin/env python3
"""leer_lab.py — read-only reader for a lab-submissions section folder.

Used by the attendance skill's lab-attendance mode to determine which
students/groups submitted a given lab, without touching (or requiring) any
attendance JSON. Purely a reader: it never writes anything.

Stdlib only. No network access. Fully deterministic.

CLI
---
    python3 leer_lab.py <lab_section_dir>

    <lab_section_dir>   Path to one lab's section folder, e.g.
                         labs/submissions/lab01/Ad

Behavior
--------
Reads every ``evaluations/row_grupo-*.json`` file in the given directory.
Each such file is expected to look like::

    {
      "name": "Grupo 1",
      "members": ["Fabricio Galvez (24001301)", "Andres Olazábal (23012183)"],
      ...
    }

Each member string is parsed with the regex ``^(?P<name>.*?)\\s*\\((?P<carne>\\d+)\\)\\s*$``
to split it into a name and a carné. If a member string does not match (no
parenthesized carné), it is kept with ``carne: null``.

If the ``evaluations/`` subdirectory is missing or contains no
``row_grupo-*.json`` files, this script does NOT crash: it falls back to
listing group PDFs (``Grupo__*.pdf``) in the directory and emits a result
with empty groups/members plus a ``note`` and a ``pdfs`` list, so the caller
knows submissions exist but membership must be resolved manually.

Output (JSON on stdout)
------------------------
    {
      "lab_dir": "<path>",
      "groups": [
        {"name": "Grupo 1", "members": [{"name": "...", "carne": "..."}]}
      ],
      "present_members": [
        {"name": "...", "carne": "...", "group": "Grupo 1"}
      ],
      "present_carnes": ["24001301", ...],
      "summary": {"groups": N, "members": M, "with_carne": K, "without_carne": J}
    }

Or, in the fallback (no evaluations/ JSONs) case::

    {
      "lab_dir": "<path>",
      "groups": [],
      "present_members": [],
      "present_carnes": [],
      "note": "no evaluations/ JSONs — only <n> group PDFs found; members unknown, resolve manually",
      "pdfs": ["Grupo__1_....pdf", ...]
    }
"""

import argparse
import glob
import json
import os
import re
import sys

MEMBER_RE = re.compile(r"^(?P<name>.*?)\s*\((?P<carne>\d+)\)\s*$")


def parse_member(member_str):
    """Parse one member string into {'name': ..., 'carne': ... or None}."""
    if not isinstance(member_str, str):
        return {"name": member_str, "carne": None}
    match = MEMBER_RE.match(member_str.strip())
    if match:
        return {"name": match.group("name").strip(), "carne": match.group("carne")}
    return {"name": member_str.strip(), "carne": None}


def read_evaluations(lab_dir):
    """Read evaluations/row_grupo-*.json files. Returns list of raw dicts (sorted by filename)."""
    eval_dir = os.path.join(lab_dir, "evaluations")
    if not os.path.isdir(eval_dir):
        return None  # signal: no evaluations dir

    paths = sorted(glob.glob(os.path.join(eval_dir, "row_grupo-*.json")))
    if not paths:
        return None  # signal: dir exists but no matching files

    rows = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                rows.append(json.load(f))
        except (OSError, json.JSONDecodeError):
            continue
    return rows


def build_result(lab_dir, rows):
    """Build the normal-mode result dict from parsed row_grupo-*.json contents."""
    groups = []
    present_members = []
    seen_carnes = set()
    with_carne = 0
    without_carne = 0

    for row in rows:
        group_name = row.get("name", "")
        raw_members = row.get("members") or []
        members = []
        for raw in raw_members:
            parsed = parse_member(raw)
            members.append(parsed)
            present_members.append({
                "name": parsed["name"],
                "carne": parsed["carne"],
                "group": group_name,
            })
            if parsed["carne"]:
                with_carne += 1
                seen_carnes.add(parsed["carne"])
            else:
                without_carne += 1

        groups.append({"name": group_name, "members": members})

    present_carnes = sorted(seen_carnes)

    return {
        "lab_dir": lab_dir,
        "groups": groups,
        "present_members": present_members,
        "present_carnes": present_carnes,
        "summary": {
            "groups": len(groups),
            "members": len(present_members),
            "with_carne": with_carne,
            "without_carne": without_carne,
        },
    }


def build_fallback_result(lab_dir):
    """Build the fallback result when no evaluations/ JSONs are available."""
    pdfs = sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(lab_dir, "Grupo__*.pdf"))
    )
    return {
        "lab_dir": lab_dir,
        "groups": [],
        "present_members": [],
        "present_carnes": [],
        "note": (
            f"no evaluations/ JSONs — only {len(pdfs)} group PDFs found; "
            "members unknown, resolve manually"
        ),
        "pdfs": pdfs,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read-only reader for a lab-submissions section folder (group members + carnés).",
    )
    parser.add_argument("lab_section_dir", help="Path to a lab's section folder, e.g. labs/submissions/lab01/Ad")
    args = parser.parse_args(argv)

    lab_dir = args.lab_section_dir
    rows = read_evaluations(lab_dir)

    if rows is None:
        result = build_fallback_result(lab_dir)
    else:
        result = build_result(lab_dir, rows)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
