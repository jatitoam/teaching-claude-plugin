#!/usr/bin/env python3
"""Validate the judge's verdicts.json for a video-evidence/2 pack and render review.md.

    render_review.py <pack_dir> <verdicts.json> [--out review.md]

verdicts.json::
  {"submission_id":..,"items":[{"id","criterion","kind":"criterion|penalty",
     "verdict":"Meets Expectations|Partially Meets|Does Not Meet|REVIEW_REQUIRED|met|partial|not_met",
     "note", "cites":[{"t","frame"|null,"quote"|null,"metadata_field"|null}],
     "review_required":[{"from","to","reason"}]}],
   "key_moments":[{"t","frame","label"}]}

Validation: cited frames exist; REVIEW_REQUIRED items have >=1 window; every other verdict
has >=1 cite. Adds `watch` to every cite / window / key moment and writes the enriched JSON
back (only when valid), then writes review.md (default <pack>/review.md): "Needs your
review" first, then Verdicts, then Key moments. Image paths are relative to the pack dir.
Exit 1 on validation errors (nothing written).
"""
import argparse
import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pack_common import mmss, read_json, watch_ref, write_json  # noqa: E402

VERDICTS = {"Meets Expectations", "Partially Meets", "Does Not Meet", "REVIEW_REQUIRED",
            "met", "partial", "not_met"}
THUMB_W = 320


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate(pack, v):
    errs = []
    items = v.get("items")
    if not isinstance(items, list) or not items:
        return ["items missing or empty"]
    for it in items:
        iid = it.get("id", "?")
        verdict = it.get("verdict")
        if verdict not in VERDICTS:
            errs.append(f"{iid}: invalid verdict {verdict!r}")
        cites = it.get("cites") or []
        wins = it.get("review_required") or []
        if verdict == "REVIEW_REQUIRED":
            if not wins:
                errs.append(f"{iid}: REVIEW_REQUIRED needs >=1 review_required window")
        elif not cites:
            errs.append(f"{iid}: verdict {verdict!r} needs >=1 cite")
        for i, c in enumerate(cites, 1):
            if not is_num(c.get("t")):
                errs.append(f"{iid}/cite {i}: numeric t required")
            if not (c.get("frame") or c.get("quote") or c.get("metadata_field")):
                errs.append(f"{iid}/cite {i}: needs frame, quote or metadata_field")
            if c.get("frame") and not (pack / c["frame"]).is_file():
                errs.append(f"{iid}/cite {i}: frame not found: {c['frame']}")
        for i, w in enumerate(wins, 1):
            if not (is_num(w.get("from")) and is_num(w.get("to"))):
                errs.append(f"{iid}/window {i}: numeric from/to required")
            elif w["from"] > w["to"]:
                errs.append(f"{iid}/window {i}: from > to")
            if not str(w.get("reason") or "").strip():
                errs.append(f"{iid}/window {i}: reason required")
    for i, k in enumerate(v.get("key_moments") or [], 1):
        if not is_num(k.get("t")):
            errs.append(f"key_moment {i}: numeric t required")
        if k.get("frame") and not (pack / k["frame"]).is_file():
            errs.append(f"key_moment {i}: frame not found: {k['frame']}")
    return errs


def enrich(meta, v):
    for it in v["items"]:
        for c in it.get("cites") or []:
            c["watch"] = watch_ref(meta, c["t"])
            c["mmss"] = mmss(c["t"])
        for w in it.get("review_required") or []:
            w["watch"] = watch_ref(meta, w["from"])
            w["from_mmss"], w["to_mmss"] = mmss(w["from"]), mmss(w["to"])
    for k in v.get("key_moments") or []:
        k["watch"] = watch_ref(meta, k["t"])
        k["mmss"] = mmss(k["t"])


def link(label, w):
    return f"[{label}]({w})" if w.startswith("http") else f"`{w}`"


def img(path):
    return f'<img src="{escape(path, quote=True)}" width="{THUMB_W}">' if path else ""


def nearest_frame(frames, lo, hi):
    """Kept frame whose [t, static_until] span is closest to the window midpoint."""
    if not frames:
        return None
    mid = (lo + hi) / 2

    def dist(f):
        a, b = f["t"], f.get("static_until", f["t"])
        return 0 if a <= mid <= b else min(abs(mid - a), abs(mid - b))
    return min(frames, key=dist)["file"]


def render(pack, meta, v, frames):
    yt = meta.get("youtube") or {}
    src = meta.get("source") or {}
    w = meta.get("watch") or {}
    tr = meta.get("transcript") or {}
    over = (meta.get("flags") or {}).get("over_max_duration")
    title = yt.get("title") or v.get("submission_id") or meta.get("submission_id")
    if w.get("kind") == "youtube":
        slink = f"https://youtu.be/{w['id']}"
    else:
        slink = src.get("url") or src.get("path") or ""
    dur = (meta.get("probe") or {}).get("duration_mmss", "?")
    tline = tr.get("status", "unknown")
    if tr.get("sparse"):
        tline += f" (WARNING: sparse, {tr.get('words_per_min')} words/min; likely music or no narration, text may be hallucinated)"
    out = [f"# Review: {title}", "",
           f"- Submission: `{v.get('submission_id') or meta.get('submission_id')}`",
           f"- Source: {slink}",
           f"- Duration: {dur}",
           f"- Over max duration: {'unchecked' if over is None else ('YES' if over else 'no')}",
           f"- Transcript: {tline}", ""]

    review = [(it, r) for it in v["items"] for r in it.get("review_required") or []
             ]
    out += ["## Needs your review", ""]
    if not review:
        out += ["Nothing flagged: every item was decided from the evidence.", ""]
    for it, r in review:
        fr = nearest_frame(frames, r["from"], r["to"])
        out += [f"### {it['id']} {it['criterion']}", "",
                f"- Window: {mmss(r['from'])}-{mmss(r['to'])}",
                f"- Why: {r['reason']}",
                f"- Watch: {link('open at ' + mmss(max(0, r['from'] - 3)), r['watch'])}"]
        if fr:
            out += ["", img(fr)]
        out.append("")

    out += ["## Verdicts", ""]
    for it in v["items"]:
        tag = "penalty" if it.get("kind") == "penalty" else "criterion"
        out += [f"### {it['id']} {it['criterion']} ({tag})", "",
                f"**{it['verdict']}**", ""]
        if it.get("note"):
            out += [it["note"], ""]
        cites = it.get("cites") or []
        for c in cites:
            bits = []
            if c.get("quote"):
                bits.append(f'"{c["quote"]}"')
            if c.get("metadata_field"):
                bits.append(f"metadata: {c['metadata_field']}")
            if c.get("frame"):
                bits.append(f"frame {c['frame']}")
            out.append(f"- {mmss(c['t'])} {link('watch', c['watch'])}"
                       + (" - " + "; ".join(bits) if bits else ""))
        first = next((c["frame"] for c in cites if c.get("frame")), None)
        if first:
            out += ["", img(first)]
        out.append("")

    out += ["## Key moments", ""]
    for k in sorted(v.get("key_moments") or [], key=lambda k: k["t"]):
        out.append(f"- {mmss(k['t'])} · {k.get('label', '')} · {link('watch', k['watch'])}")
        if k.get("frame"):
            out += ["", f"  {img(k['frame'])}", ""]
    if not v.get("key_moments"):
        out += ["None.", ""]
    return "\n".join(out).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pack_dir")
    ap.add_argument("verdicts")
    ap.add_argument("--out", default="review.md", help="default <pack>/review.md")
    a = ap.parse_args(argv)
    pack = Path(a.pack_dir).expanduser().resolve()
    vpath = Path(a.verdicts).expanduser()
    if not vpath.is_absolute() and not vpath.exists():
        vpath = pack / vpath
    try:
        v = read_json(vpath)
        meta = read_json(pack / "metadata.json")
        frames = read_json(pack / "frames.json").get("frames", [])
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "errors": [f"cannot read inputs: {exc}"]}, indent=2))
        return 1
    errs = validate(pack, v)
    if errs:
        print(json.dumps({"ok": False, "errors": errs}, indent=2, ensure_ascii=False))
        return 1
    enrich(meta, v)
    write_json(vpath, v)
    out = Path(a.out).expanduser()
    out = out if out.is_absolute() else pack / out
    out.write_text(render(pack, meta, v, frames), encoding="utf-8")
    print(json.dumps({"ok": True, "review": str(out), "verdicts": str(vpath),
                      "needs_review": sum(len(i.get("review_required") or []) for i in v["items"])},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
