#!/usr/bin/env python3
"""Validate the judge's verdicts.json for a video-evidence/2 pack and render review.md.

    render_review.py <pack_dir> <verdicts.json> [--out review.md]

verdicts.json::
  {"submission_id":..,"items":[{"id","criterion","kind":"criterion|penalty",
     "verdict":"Meets Expectations|Partially Meets|Does Not Meet|REVIEW_REQUIRED|met|partial|not_met",
     "note", "cites":[{"t","frame"|null,"quote"|null,"on_screen"|null,"metadata_field"|null}],
     "review_required":[{"from","to","reason","outside_video"?}], "code"?, "outside_video"?,
     "confirmation"?:{"by","via":"direct|relayed","relayed_by","at","note"}}],
   "key_moments":[{"t","frame","label"}],
   "extra_sections":[{"title","markdown"}]}   # optional, rendered after Key moments

Also "not_applicable" / "N/A" verdicts (criteria and penalties): valid without cites. Items
that cannot be judged from the video (REVIEW_REQUIRED with only 0-0 windows, or
`outside_video: true`) render in "Needs your review" without window/watch/thumbnail.

Validation: cited frames exist; REVIEW_REQUIRED items have >=1 window; every other verdict
has >=1 cite. Adds `watch` to every cite / window / key moment and writes the enriched JSON
back (only when valid), then writes review.md (default <pack>/review.md): "Needs your
review" first, then Verdicts, then Key moments. Image paths are relative to the pack dir.
Options: --preamble FILE (inserted verbatim after the header block; it lives in the inputs,
so pass it on every re-render). Integrity: verdicts.submission_id must equal
metadata.submission_id; a stamped evidence-map (finalize_pack.py) must still match frames.json.
Piece rubrics (evidence-map `scoring: "piezas"`) get an informative "## Puntos" section.
Exit 1 on validation errors (nothing written).
"""
import argparse
import json
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pack_common import (frames_sha256, mmss, read_json, watch_ref, watch_start,  # noqa: E402
                         write_json)

VERDICTS = {"Meets Expectations", "Partially Meets", "Does Not Meet", "REVIEW_REQUIRED",
            "met", "partial", "not_met", "not_applicable", "N/A"}
NA_VERDICTS = {"not_applicable", "N/A"}
NA_DEFAULT = "not in this submission's plan"
THUMB_W = 320


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_na(it):
    return it.get("verdict") in NA_VERDICTS


def win_outside(w):
    return bool(w.get("outside_video")) or (w.get("from") == 0 and w.get("to") == 0)


def item_outside(it):
    """Cannot be judged from the video: flagged, or REVIEW_REQUIRED whose windows are all 0-0."""
    if it.get("outside_video"):
        return True
    wins = it.get("review_required") or []
    return it.get("verdict") == "REVIEW_REQUIRED" and bool(wins) \
        and all(win_outside(w) for w in wins)


def validate(pack, v):
    errs = []
    items = v.get("items")
    if not isinstance(items, list) or not items:
        return ["items missing or empty"]
    for sec in v.get("extra_sections") or []:
        if not (isinstance(sec, dict) and str(sec.get("title") or "").strip()
                and isinstance(sec.get("markdown"), str)):
            errs.append("extra_sections entries need a title and a markdown string")
    for it in items:
        iid = it.get("id", "?")
        verdict = it.get("verdict")
        if verdict not in VERDICTS:
            errs.append(f"{iid}: invalid verdict {verdict!r}")
        cites = it.get("cites") or []
        wins = it.get("review_required") or []
        conf = it.get("confirmation")
        if conf is not None:
            if not isinstance(conf, dict) or not str(conf.get("by") or "").strip():
                errs.append(f"{iid}: confirmation needs an object with `by`")
            elif conf.get("via") not in ("direct", "relayed"):
                errs.append(f"{iid}: confirmation.via must be direct|relayed")
        if verdict in NA_VERDICTS:
            pass
        elif verdict == "REVIEW_REQUIRED":
            if not wins and not it.get("outside_video"):
                errs.append(f"{iid}: REVIEW_REQUIRED needs >=1 review_required window")
        elif not cites:
            errs.append(f"{iid}: verdict {verdict!r} needs >=1 cite")
        for i, c in enumerate(cites, 1):
            if not is_num(c.get("t")):
                errs.append(f"{iid}/cite {i}: numeric t required")
            if not (c.get("frame") or c.get("quote") or c.get("metadata_field")
                    or c.get("on_screen")):
                errs.append(f"{iid}/cite {i}: needs frame, quote, on_screen or metadata_field")
            if "on_screen" in c and c["on_screen"] is not None \
                    and not str(c["on_screen"]).strip():
                errs.append(f"{iid}/cite {i}: on_screen text is empty")
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
            if not win_outside(w):
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


def label(it, emap_items):
    code = it.get("code") or (emap_items.get(it.get("id")) or {}).get("code")
    return f"{code} \u00b7 {it['criterion']}" if code else f"{it['id']} {it['criterion']}"


def num(x):
    return float(x) if is_num(x) else None


def fmt(x):
    return f"{x:g}" if isinstance(x, float) else str(x)


def parse_conversion(conv):
    """-> callable(points) -> grade, or None. number = multiplier; {"divide_by","multiply_by"};
    string 'MIN(puntos;CAP)/A*B' (the cap is applied separately)."""
    if is_num(conv):
        return lambda p: p * conv
    if isinstance(conv, dict):
        d, m = num(conv.get("divide_by")) or 1.0, num(conv.get("multiply_by")) or 1.0
        return lambda p: p / d * m
    if isinstance(conv, str):
        # Same pattern as append_grade.py's _CONV_RE (tolerates a "nota =" prefix, spaces and
        # decimal commas) so the review's grade always matches the grades xlsx.
        m = re.search(r"MIN\(\s*[^;()]+?\s*;\s*(\d+(?:[.,]\d+)?)\s*\)\s*/\s*(\d+(?:[.,]\d+)?)"
                      r"\s*\*\s*(\d+(?:[.,]\d+)?)", conv, re.IGNORECASE)
        if m:
            d, mu = (float(g.replace(",", ".")) for g in m.groups()[1:])
            if d:
                return lambda p: p / d * mu
    return None


def puntos_section(v, emap, emap_items):
    cap = num(emap.get("cap"))
    out = ["## Puntos", "",
           "_Informative \u2014 the grades xlsx is authoritative._", "",
           "| Piece | Verdict | Points |", "|---|---|---|"]
    total, unresolved, pending = 0.0, [], 0
    pens = []
    for it in v["items"]:
        em = emap_items.get(it.get("id")) or {}
        if it.get("kind") == "penalty":
            pens.append((it, em))
            continue
        w = num(em.get("weight") if em.get("weight") is not None else it.get("weight"))
        vd = it["verdict"]
        if vd in NA_VERDICTS:
            pts = "N/A"
        elif vd == "Meets Expectations":
            pts = w
        elif vd == "Does Not Meet":
            pts = 0.0
        elif vd == "Partially Meets":
            pp = num(em.get("pts_parcial"))
            if pp is None and num(em.get("pct_parcial")) is not None and w is not None:
                pc = num(em["pct_parcial"])
                pp = (pc / 100 if pc > 1 else pc) * w
            pts = pp
        else:  # REVIEW_REQUIRED
            pts, pending = "pending review", pending + 1
        if pts is None:
            unresolved.append(it["id"])
            cell = "?"
        elif isinstance(pts, str):
            cell = pts
        else:
            total += pts
            cell = fmt(pts)
        out.append(f"| {label(it, emap_items)} | {vd} | {cell} |")
    out += ["", f"- \u03a3 points: **{fmt(total)}**"
            + (f" (excludes {pending} pending review)" if pending else "")
            + (f" (unresolved: {', '.join(unresolved)})" if unresolved else "")]
    capped = total
    if cap is not None:
        capped = min(total, cap)
        out.append(f"- Cap: {fmt(cap)} \u2192 {fmt(capped)}")
    conv = parse_conversion(emap.get("conversion"))
    if conv:
        from decimal import Decimal, ROUND_HALF_UP  # half-up, like append_grade.py and a spreadsheet
        g = Decimal(repr(conv(capped))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        out.append(f"- Grade: **{g}** (conversion: `{emap.get('conversion')}`)")
    elif emap.get("conversion") is not None:
        out.append(f"- Grade: not computed (conversion not parseable: `{emap.get('conversion')}`)")
    if pens:
        out += ["", "Penalties (listed, not applied here \u2014 append_grade applies them):", ""]
        for it, em in pens:
            val = em.get("penalty") if em.get("penalty") is not None else it.get("penalty")
            out.append(f"- {label(it, emap_items)}: {it['verdict']}"
                       + (f" (penalty {val})" if val is not None else ""))
    out.append("")
    return out


def render(pack, meta, v, frames, emap=None, preamble=None):
    emap = emap or {}
    emap_items = {i.get("id"): i for i in emap.get("items") or []}
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
    if preamble and preamble.strip():
        out += [preamble.rstrip("\n"), ""]

    out += ["## Needs your review", ""]
    entries = []   # (item, window|None, outside:bool)
    for it in v["items"]:
        if is_na(it):
            continue
        wins = it.get("review_required") or []
        if item_outside(it):
            entries.append((it, wins[0] if wins else None, True))
            continue
        entries += [(it, r, win_outside(r)) for r in wins]
    if not entries:
        out += ["Nothing flagged: every item was decided from the evidence.", ""]
    for it, r, outside in entries:
        out += [f"### {label(it, emap_items)}", ""]
        if outside:
            reason = (r or {}).get("reason") or it.get("note") or "not verifiable in the video"
            out += [f"- Outside the video: {reason}"]
            if it.get("note") and it.get("note") != reason:
                out += [f"- Note: {it['note']}"]
            out.append("")
            continue
        first = next((c["frame"] for c in it.get("cites") or [] if c.get("frame")), None)
        fr = first or nearest_frame(frames, r["from"], r["to"])
        out += [f"- Window: {mmss(r['from'])}-{mmss(r['to'])}",
                f"- Why: {r['reason']}"]
        if it.get("note"):
            out.append(f"- Note: {it['note']}")
        out.append(f"- Watch: {link('open at ' + mmss(watch_start(meta, r['from'])), r['watch'])}")
        if fr:
            out += ["", img(fr)]
        out.append("")

    out += ["## Verdicts", ""]
    for it in v["items"]:
        tag = "penalty" if it.get("kind") == "penalty" else "criterion"
        out += [f"### {label(it, emap_items)} ({tag})", ""]
        if is_na(it):
            out += [f"**N/A \u2014 {it.get('note') or NA_DEFAULT}**", ""]
            conf = it.get("confirmation")
        else:
            out += [f"**{it['verdict']}**", ""]
            if it.get("note"):
                out += [it["note"], ""]
            conf = it.get("confirmation")
        if conf:
            via = conf["via"] + (f" via {conf['relayed_by']}" if conf.get("relayed_by") else "")
            out += [f"Confirmed by {conf['by']} ({via})"
                    + (f" {conf['at']}" if conf.get("at") else "")
                    + (f" \u2014 {conf['note']}" if conf.get("note") else ""), ""]
        cites = it.get("cites") or []
        for c in cites:
            bits = []
            if c.get("quote"):
                bits.append(f'"{c["quote"]}"')
            if c.get("on_screen"):
                bits.append(f"screen: \u201c{c['on_screen']}\u201d")
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

    if emap.get("scoring") == "piezas":
        out += puntos_section(v, emap, emap_items)

    out += ["## Key moments", ""]
    for k in sorted(v.get("key_moments") or [], key=lambda k: k["t"]):
        out.append(f"- {mmss(k['t'])} \u00b7 {k.get('label', '')} \u00b7 {link('watch', k['watch'])}")
        if k.get("frame"):
            out += ["", f"  {img(k['frame'])}", ""]
    if not v.get("key_moments"):
        out += ["None.", ""]
    for sec in v.get("extra_sections") or []:
        out += [f"## {sec['title']}", "", sec["markdown"].rstrip("\n"), ""]
    return "\n".join(out).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pack_dir")
    ap.add_argument("verdicts")
    ap.add_argument("--out", default="review.md", help="default <pack>/review.md")
    ap.add_argument("--preamble", metavar="FILE",
                    help="markdown inserted verbatim after the header block")
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
    warns = []
    msid = meta.get("submission_id")
    if v.get("submission_id") is None:
        warns.append("verdicts.json has no submission_id (not cross-checked)")
    elif v["submission_id"] != msid:
        errs.append(f"verdicts submission_id {v['submission_id']!r} != metadata "
                    f"submission_id {msid!r}: verdicts belong to a different pack")
    emap = None
    epath = pack / "evidence-map.json"
    if epath.is_file():
        try:
            emap = read_json(epath)
        except (OSError, ValueError) as exc:
            warns.append(f"evidence-map.json unreadable ({exc}): codes/points unavailable")
    if emap is not None:
        if emap.get("submission_id") not in (None, msid):
            errs.append(f"evidence-map submission_id {emap.get('submission_id')!r} != "
                        f"metadata submission_id {msid!r}")
        st = emap.get("integrity")
        if isinstance(st, dict):
            if st.get("submission_id") != msid or st.get("frames_sha256") != frames_sha256(pack):
                errs.append("evidence-map was built for a different/changed pack "
                            "(integrity stamp does not match; re-run finalize_pack.py)")
        else:
            warns.append("evidence-map has no integrity stamp (legacy): run finalize_pack.py")
    preamble = None
    if a.preamble:
        try:
            preamble = Path(a.preamble).expanduser().read_text(encoding="utf-8")
        except OSError as exc:
            errs.append(f"cannot read --preamble: {exc}")
    if errs:
        print(json.dumps({"ok": False, "errors": errs, "warnings": warns},
                         indent=2, ensure_ascii=False))
        return 1
    enrich(meta, v)
    write_json(vpath, v)
    out = Path(a.out).expanduser()
    out = out if out.is_absolute() else pack / out
    out.write_text(render(pack, meta, v, frames, emap, preamble), encoding="utf-8")
    print(json.dumps({"ok": True, "review": str(out), "verdicts": str(vpath),
                      "needs_review": sum(len(i.get("review_required") or []) for i in v["items"]),
                      "warnings": warns},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
