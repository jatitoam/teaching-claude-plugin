#!/usr/bin/env python3
"""Validate and finalize the selector's evidence-map.json in a video-evidence/2 pack.

    finalize_pack.py <pack_dir> [--strict]

Checks: contract is video-evidence/2; every item has >=1 candidate or a non-empty
`coverage`; every candidate has `why`, from <= to, existing frame files, quotes and
on_screen entries ({t, text, frame}; t within the video) inside the
transcript range, resolvable `metadata_fields`. Fills/overwrites `watch` on every
candidate (from `from`) and fills missing from_mmss/to_mmss/quote mmss. Sets
status SELECTED when there are no errors. --strict promotes warnings to errors.
Prints {"ok", "errors", "warnings"} to stdout; exit 1 on errors.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pack_common import mmss, read_json, watch_ref, write_json  # noqa: E402

CONTRACT = "video-evidence/2"
TOL = 1.0  # seconds of slack past the end of the transcript / video


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def resolve(meta, dotted):
    cur = meta
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return cur is not None


def finalize(pack, strict=False):
    errors, warnings = [], []
    path = pack / "evidence-map.json"
    if not path.is_file():
        return None, ["evidence-map.json not found"], []
    try:
        emap = read_json(path)
        meta = read_json(pack / "metadata.json")
    except (OSError, ValueError) as exc:
        return None, [f"cannot read pack JSON: {exc}"], []

    if emap.get("contract") != CONTRACT:
        errors.append(f"contract is {emap.get('contract')!r}, expected {CONTRACT!r}")

    t_end = None
    tpath = pack / "transcript.json"
    if tpath.is_file():
        segs = read_json(tpath).get("segments", [])
        t_end = max((s.get("end", 0) for s in segs), default=0)
    dur = (meta.get("probe") or {}).get("duration_s")

    items = emap.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items missing or empty")
        items = []
    seen = set()
    for it in items:
        iid = it.get("id", "?")
        if iid in seen:
            errors.append(f"{iid}: duplicate item id")
        seen.add(iid)
        cands = it.get("candidates") or []
        if not cands and not str(it.get("coverage") or "").strip():
            errors.append(f"{iid}: no candidates and empty coverage")
        for n, c in enumerate(cands, 1):
            tag = f"{iid}/candidate {n}"
            for key in ("frames", "quotes", "metadata_fields"):  # normalize to the contract
                c.setdefault(key, [])
            f, t = c.get("from"), c.get("to")
            if not (is_num(f) and is_num(t)):
                errors.append(f"{tag}: from/to must be numbers")
                continue
            if f > t:
                errors.append(f"{tag}: from ({f}) > to ({t})")
            if f < 0:
                errors.append(f"{tag}: negative from")
            if dur and t > dur + TOL:
                warnings.append(f"{tag}: to ({t}) beyond video duration ({dur})")
            if not str(c.get("why") or "").strip():
                errors.append(f"{tag}: missing why")
            if not (c.get("frames") or c.get("quotes") or c.get("metadata_fields")
                    or c.get("on_screen")):
                warnings.append(f"{tag}: cites no frames, quotes, on_screen text or metadata fields")
            for fr in c.get("frames") or []:
                if not (pack / fr).is_file():
                    errors.append(f"{tag}: frame not found: {fr}")
            for q in c.get("quotes") or []:
                qt = q.get("t")
                if not is_num(qt) or not str(q.get("text") or "").strip():
                    errors.append(f"{tag}: quote needs numeric t and text")
                    continue
                if t_end is None:
                    errors.append(f"{tag}: quote cited but pack has no transcript")
                elif qt < 0 or qt > t_end + TOL:
                    errors.append(f"{tag}: quote t={qt} outside transcript range 0-{t_end}")
                q.setdefault("mmss", mmss(qt))
            c.setdefault("frames", [])
            c.setdefault("quotes", [])
            c.setdefault("metadata_fields", [])
            c["on_screen"] = c.get("on_screen") or []
            for k, o in enumerate(c["on_screen"], 1):
                ot = o.get("t")
                if not is_num(ot) or ot < 0 or (dur and ot > dur + TOL):
                    errors.append(f"{tag}: on_screen {k} t={ot!r} outside 0-{dur}")
                else:
                    o.setdefault("mmss", mmss(ot))
                if not str(o.get("text") or "").strip():
                    errors.append(f"{tag}: on_screen {k} has empty text")
                if not o.get("frame") or not (pack / o["frame"]).is_file():
                    errors.append(f"{tag}: on_screen {k} frame not found: {o.get('frame')}")
            for mf in c.get("metadata_fields") or []:
                if not resolve(meta, mf):
                    warnings.append(f"{tag}: metadata field {mf!r} absent or null")
            c["from_mmss"] = c.get("from_mmss") or mmss(f)
            c["to_mmss"] = c.get("to_mmss") or mmss(t)
            c["watch"] = watch_ref(meta, f)

    if strict:
        errors += [f"(strict) {w}" for w in warnings]
        warnings = []
    ok = not errors
    emap["status"] = "SELECTED" if ok else "PENDING_SELECTION"
    write_json(path, emap)
    return ok, errors, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pack_dir")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args(argv)
    ok, errors, warnings = finalize(Path(a.pack_dir).expanduser().resolve(), a.strict)
    if ok is None:
        ok = False
    print(json.dumps({"ok": bool(ok), "errors": errors, "warnings": warnings},
                     indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
