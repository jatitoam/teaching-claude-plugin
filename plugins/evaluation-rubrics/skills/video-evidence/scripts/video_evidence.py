#!/usr/bin/env python3
"""Decompose a video submission into an auditable on-disk "evidence pack".

Claude cannot watch video, so this script turns one into files a model can
read and cite against a rubric. The pack CAPTURES, INDEXES and helps SELECT evidence;
it issues no verdicts (a separate judge does). Output contract (``video-evidence/2``)::

    OUT_DIR/<id>/
        metadata.json        source, probe, params, download/transcript status, flags
        frames/tSSSS.mmm.jpg timestamped frames (interval + scene-change passes)
        frames.json          near-duplicate-pruned frames; each says "static from t to static_until"
        contact-sheet[-NN].jpg   thumbnail grid(s) of the frames
        contact-sheet.json   cell (row,col) -> timestamp for each sheet
        transcript.json      {"engine","model","language","segments":[{start,end,mmss,text}]}
        transcript.srt
        evidence-map.json    (with --rubric) selection skeleton, status PENDING_SELECTION;
                             filled by a selector model, checked by finalize_pack.py
        video.<ext>          (with --keep-video, URL inputs only)

A JSON summary is printed to stdout; progress goes to stderr.
Exit codes: 0 ok, 2 preflight failed, 3 download failed, 4 probe/frame failure.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preflight  # noqa: E402
from pack_common import mmss, write_json  # noqa: E402

CONTRACT = "video-evidence/2"
COLS = 6
THUMB_W = 320
MAX_PER_SHEET = 60
DEDUPE_THRESHOLD = 1.5
DEDUPE_TILE_THRESHOLD = 3.0
DEFAULT_MODELS = {
    "mlx_whisper": "mlx-community/whisper-large-v3-turbo",
    "whisper": "turbo",
    "faster_whisper": "small",
}
EPILOG = """\
examples:
  video_evidence.py https://youtu.be/XXXXXXXXXXX --out ./packs --rubric rubric.json
  video_evidence.py ./student.mp4 --out ./packs --id s042 --no-transcribe
exit codes: 0 ok, 2 preflight failed, 3 download failed, 4 probe/frame failure.
Progress on stderr, JSON summary on stdout. Videos are downloaded to the OS
temp dir (outside synced folders) and deleted unless --keep-video.
"""


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def slug(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-._")[:80] or "video"


def run(cmd, check=True, timeout=None):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                       timeout=timeout)
    if check and p.returncode != 0:
        raise RuntimeError(f"{Path(str(cmd[0])).name} failed ({p.returncode}): "
                           f"{p.stderr.strip()[-600:]}")
    return p


def youtube_id(url):
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None


# --------------------------------------------------------------------- rubric

def parse_rubric(path):
    """Return (criteria, penalties) as lists of dicts for evidence-map.json."""
    path = Path(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))

        def item(c, weight_keys):
            weight = next((c[k] for k in weight_keys if k in c), None)
            levels = {k: c[k] for k in ("cumple", "parcial", "no_cumple",
                                        "meets", "partial", "not_met") if k in c}
            return {"criterion": c.get("name", ""), "weight": weight,
                    "levels": levels}
        return ([item(c, ("pts", "weight", "points")) for c in data.get("criteria", [])],
                [item(c, ("penalty", "penalizacion", "pts"))
                 for c in data.get("penalties", [])])

    from openpyxl import load_workbook  # only needed for xlsx
    ws = load_workbook(path, data_only=True).active
    criteria, penalties, in_pen = [], [], False
    for row in ws.iter_rows(min_row=2, values_only=True):
        name = row[0]
        if name is None or not str(name).strip():
            continue
        name = str(name).strip()
        low = name.lower()
        if low.startswith("penal"):
            in_pen = True
            continue
        if low in ("criterio", "criterion"):
            continue
        pts = row[4] if len(row) >= 5 else None
        levels = {k: str(v) for k, v in zip(("cumple", "parcial", "no_cumple"),
                                            row[1:4]) if v}
        entry = {"criterion": name, "levels": levels}
        if in_pen:
            entry["weight"] = None if pts is None else str(pts).strip()
            penalties.append(entry)
            continue
        if pts is None:
            continue
        try:
            entry["weight"] = float(pts)
        except (TypeError, ValueError):
            in_pen = True
            entry["weight"] = str(pts).strip()
            penalties.append(entry)
            continue
        criteria.append(entry)
    return criteria, penalties


def evidence_map_skeleton(sid, rubric_path):
    """Selection skeleton: one item per criterion/penalty, candidates filled later."""
    criteria, penalties = parse_rubric(rubric_path)
    items = []
    for i, c in enumerate(criteria, 1):
        items.append({"id": f"C{i}", "kind": "criterion", "criterion": c["criterion"],
                      "weight": c["weight"], "levels": c["levels"],
                      "candidates": [], "coverage": ""})
    for i, c in enumerate(penalties, 1):
        items.append({"id": f"P{i}", "kind": "penalty", "criterion": c["criterion"],
                      "penalty": c["weight"], "levels": c["levels"],
                      "candidates": [], "coverage": ""})
    return {"contract": CONTRACT, "submission_id": sid,
            "rubric_source": str(rubric_path), "status": "PENDING_SELECTION",
            "items": items}


# ------------------------------------------------------------------- download

def watch_meta(source, is_url):
    if not is_url:
        return {"kind": "file", "path": str(Path(source).resolve())}
    yid = youtube_id(source)
    if yid:
        return {"kind": "youtube", "id": yid, "template": f"https://youtu.be/{yid}?t={{s}}"}
    return {"kind": "url", "url": source}


def fetch_info(url, cookies_browser):
    """Metadata only (title/description) for a manually downloaded file. Non-fatal."""
    cmd = [preflight.find_tool("yt-dlp") or "yt-dlp", "--skip-download", "--dump-single-json",
           "--no-playlist"]
    if cookies_browser:
        cmd += ["--cookies-from-browser", cookies_browser]
    out = run(cmd + [url]).stdout
    return json.loads(out)


YT_FIELDS = ("id", "title", "description", "uploader", "channel", "upload_date",
             "availability", "webpage_url")


def download(url, work, max_height, cookies_browser):
    cmd = ["yt-dlp", "-f",
           f"bv*[height<={max_height}]+ba/b[height<={max_height}]",
           "--merge-output-format", "mp4", "--write-info-json", "--no-playlist",
           "--no-progress", "-o", str(work / "video.%(ext)s")]
    if cookies_browser:
        cmd += ["--cookies-from-browser", cookies_browser]
    cmd.append(url)
    cmd[0] = preflight.find_tool("yt-dlp") or "yt-dlp"
    run(cmd)
    vids = [p for p in work.glob("video.*")
            if p.suffix not in (".json", ".part", ".ytdl")]
    if not vids:
        raise RuntimeError("yt-dlp produced no video file")
    info = {}
    ij = work / "video.info.json"
    if ij.exists():
        info = json.loads(ij.read_text(encoding="utf-8"))
    return vids[0], info


# ---------------------------------------------------------------------- probe

def probe(video):
    p = run([preflight.find_tool("ffprobe") or "ffprobe", "-v", "error",
             "-show_format", "-show_streams", "-of", "json", video])
    data = json.loads(p.stdout)
    vs = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    if vs is None:
        raise RuntimeError("no video stream")
    num, _, den = vs.get("avg_frame_rate", "0/1").partition("/")
    fps = round(float(num) / float(den or 1), 3) if float(den or 1) else None
    dur = float(data["format"].get("duration") or vs.get("duration") or 0)
    return {"duration_s": dur, "duration_mmss": mmss(dur),
            "width": int(vs["width"]), "height": int(vs["height"]), "fps": fps,
            "has_audio": any(s["codec_type"] == "audio" for s in data["streams"]),
            "codec": vs.get("codec_name")}


# --------------------------------------------------------------------- frames

def scene_times(video, threshold):
    p = run([FFMPEG, "-hide_banner", "-nostats", "-i", video, "-an", "-vf",
             f"select='gt(scene,{threshold})',showinfo", "-fps_mode", "passthrough",
             "-f", "null", "-"], check=False)
    if p.returncode != 0:
        raise RuntimeError(f"scene detection failed: {p.stderr.strip()[-400:]}")
    return [float(m) for m in re.findall(r"pts_time:\s*([0-9.]+)", p.stderr)]


def plan_frames(duration, interval, scenes):
    """Merge interval/last/scene timestamps into [{t, reasons}] sorted by t."""
    last = max(0.0, duration - 0.5)
    times, t = [], 0.0
    while t < duration - 1e-6:
        times.append(round(t, 3))
        t += interval
    plan = [{"t": x, "reasons": ["interval"]} for x in times]
    if not any(abs(e["t"] - last) < 0.25 for e in plan):
        plan.append({"t": round(last, 3), "reasons": ["last"]})
    for s in sorted(scenes):
        s = round(min(max(s, 0.0), max(0.0, duration - 0.05)), 3)
        near = next((e for e in plan if abs(e["t"] - s) <= 0.5), None)
        if near is None:
            plan.append({"t": s, "reasons": ["scene"]})
        elif "scene" not in near["reasons"]:
            near["reasons"].append("scene")
    plan.sort(key=lambda e: e["t"])
    return plan


def frame_name(t):
    ms = int(round(t * 1000))
    return f"t{ms // 1000:04d}.{ms % 1000:03d}.jpg"


def extract_frames(video, plan, frames_dir, width, workers=6):
    frames_dir.mkdir(parents=True, exist_ok=True)
    vf = f"scale='min(iw,{width})':-2"

    def one(e):
        name = frame_name(e["t"])
        run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss",
             f"{e['t']:.3f}", "-i", video, "-frames:v", "1", "-vf", vf,
             "-q:v", "2", frames_dir / name])
        return {"file": f"frames/{name}", "t": e["t"], "mmss": mmss(e["t"]),
                "reasons": e["reasons"]}
    with ThreadPoolExecutor(workers) as ex:
        out = list(ex.map(one, plan))
    return [f for f in out if (frames_dir.parent / f["file"]).exists()]


# ---------------------------------------------------------------- near-duplicates

THUMB_GRID = (160, 90)   # raw grayscale thumbnail used only for comparison
TILES = (8, 6)           # local-change check grid (columns x rows)


def thumb_gray(path, ffmpeg):
    w, h = THUMB_GRID
    p = subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(path),
                        "-vf", f"scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True)
    if p.returncode != 0 or len(p.stdout) != w * h:
        return None
    return p.stdout


def tile_diffs(a, b):
    """Mean abs diff (0-255) per tile of the TILES grid, row-major (index = row*cols+col)."""
    w, h = THUMB_GRID
    cols, rows = TILES
    tw, th = w // cols, h // rows
    d = [abs(x - y) for x, y in zip(a, b)]
    out = []
    for ty in range(rows):
        for tx in range(cols):
            tot = 0
            for r in range(ty * th, (ty + 1) * th):
                o = r * w + tx * tw
                tot += sum(d[o:o + tw])
            out.append(tot / (tw * th))
    return out


def live_tiles(thumbs, tile_threshold, min_pairs=6, min_share=0.40, min_quiet=8):
    """Tiles that change in >= min_share of consecutive extracted pairs (webcam/animation).

    Returns the set of tile indexes to mask, or an empty set when there are too few pairs
    or fewer than min_quiet tiles would remain unmasked (a genuinely busy video: no masking).
    (Tuned on a webcam + animated-gradient tutorial: 0.70 left webcam-edge and gradient tiles
    unmasked; 0.40 masks them while static content tiles sit near 0; 0.30 over-masks (too few quiet tiles).)
    """
    pairs = [(x, y) for x, y in zip(thumbs, thumbs[1:]) if x is not None and y is not None]
    n = TILES[0] * TILES[1]
    if len(pairs) < min_pairs:
        return set()
    hits = [0] * n
    for x, y in pairs:
        for i, v in enumerate(tile_diffs(x, y)):
            if v >= tile_threshold:
                hits[i] += 1
    live = {i for i in range(n) if hits[i] >= min_share * len(pairs)}
    return live if n - len(live) >= min_quiet else set()


def dedupe_frames(frames, pack, ffmpeg, threshold, tile_threshold, mask_live=False, workers=8):
    """Drop frames near-identical to the previous KEPT frame (first/last always kept).

    A frame is dropped only if BOTH the mean difference < threshold AND no single tile
    differs by >= tile_threshold (so a small localized change such as an edited cell
    survives). Live tiles (changing in most consecutive pairs) are always DETECTED and
    reported, but only masked out of the comparison with mask_live=True: a formula bar being
    typed into looks exactly like a webcam bubble to this test, and masking it silently drops
    evidence (verified on a real DAX screen recording). Returns (kept, n_dropped, info).
    Kept frames gain static_until/absorbed.
    """
    with ThreadPoolExecutor(workers) as ex:
        thumbs = list(ex.map(lambda f: thumb_gray(pack / f["file"], ffmpeg), frames))
    live = live_tiles(thumbs, tile_threshold)
    use = [i for i in range(TILES[0] * TILES[1]) if not (mask_live and i in live)]
    kept, ref = [], None
    for i, (f, th) in enumerate(zip(frames, thumbs)):
        f = dict(f, static_until=f["t"], absorbed=0)
        last = i == len(frames) - 1
        if ref is not None and th is not None and not last:
            td = tile_diffs(ref, th)
            vals = [td[j] for j in use]
            if sum(vals) / len(vals) < threshold and max(vals) < tile_threshold:
                kept[-1]["static_until"] = f["t"]
                kept[-1]["absorbed"] += 1
                (pack / f["file"]).unlink(missing_ok=True)
                continue
        kept.append(f)
        ref = th
    for f in kept:
        f["static_until_mmss"] = mmss(f["static_until"])
    info = {"threshold": threshold, "tile_threshold": tile_threshold,
            "grid": f"{TILES[0]}x{TILES[1]}",
            "live_tiles": [[j % TILES[0], j // TILES[0]] for j in sorted(live)],
            "masked": bool(mask_live and live)}
    return kept, len(frames) - len(kept), info


# ---------------------------------------------------------------- contact sheet

def make_contact_sheets(pack, frames, work, has_drawtext):
    sheets = []
    chunks = [frames[i:i + MAX_PER_SHEET] for i in range(0, len(frames), MAX_PER_SHEET)]
    for n, chunk in enumerate(chunks, 1):
        name = "contact-sheet.jpg" if len(chunks) == 1 else f"contact-sheet-{n:02d}.jpg"
        rows = -(-len(chunk) // COLS)
        sources = [pack / f["file"] for f in chunk]
        labelled = False
        if has_drawtext:
            try:
                sources = _label_thumbs(chunk, pack, work, n)
                labelled = True
            except RuntimeError as exc:
                log(f"drawtext failed, sheet {n} unlabeled: {exc}")
                sources = [pack / f["file"] for f in chunk]
        lst = work / f"concat-{n}.txt"
        lines = []
        for s in sources:
            lines += [f"file '{s}'", "duration 1"]
        lst.write_text("\n".join(lines) + "\n")
        run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
             "-safe", "0", "-i", lst, "-vf",
             f"scale={THUMB_W}:-2,tile={COLS}x{rows}:padding=4:color=black",
             "-fps_mode", "passthrough", "-frames:v", "1", "-q:v", "3", pack / name])
        cells = [{"row": i // COLS, "col": i % COLS, "file": f["file"],
                  "t": f["t"], "mmss": f["mmss"]} for i, f in enumerate(chunk)]
        sheets.append({"sheet": name, "columns": COLS, "rows": rows,
                       "labels_drawn": labelled, "cells": cells})
    return sheets


def _label_thumbs(chunk, pack, work, n):
    tdir = work / f"thumbs-{n}"
    tdir.mkdir(exist_ok=True)
    outs = []
    for i, f in enumerate(chunk):
        o = tdir / f"{i:03d}.jpg"
        run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", pack / f["file"],
             "-vf", f"scale={THUMB_W}:-2,drawtext=text='{f['mmss'].replace(':', chr(92) + ':')}'"
                    ":x=6:y=6:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6",
             "-frames:v", "1", "-q:v", "3", o])
        outs.append(o)
    return outs


# ------------------------------------------------------------------ transcript

def clean_segments(segments, duration):
    """Drop Whisper artefacts: empty segments, segments starting past the end of the video,
    and hallucination loops (the same text repeated 3+ times in a row → keep the first).
    Returns (segments, dropped) — dropped is a list of {start, text, reason} for audit."""
    out, dropped, run_text, run_len = [], [], None, 0
    for seg in segments:
        if not seg["text"]:
            continue  # empty: not worth recording
        if duration and seg["start"] >= duration:
            dropped.append({"start": seg["start"], "text": seg["text"], "reason": "past_end"})
            continue
        norm = seg["text"].strip().lower()
        run_len = run_len + 1 if norm == run_text else 1
        run_text = norm
        if run_len >= 3:
            dropped.append({"start": seg["start"], "text": seg["text"], "reason": "repeat_loop"})
            continue
        out.append(seg)
    return out, dropped


def transcribe(video, pack, work, engine, model, lang, duration=None):
    audio = work / "audio.wav"
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", video, "-vn",
         "-ac", "1", "-ar", "16000", audio])
    model = model or DEFAULT_MODELS[engine]
    segments, language = [], lang
    if engine == "faster_whisper":
        from faster_whisper import WhisperModel
        segs, i = WhisperModel(model).transcribe(str(audio), language=lang)
        language = i.language
        segments = [{"start": s.start, "end": s.end, "text": s.text.strip()}
                    for s in segs]
    else:
        out = work / "tr"
        out.mkdir(exist_ok=True)
        if engine == "mlx_whisper":
            cmd = [preflight.find_tool("mlx_whisper"), audio, "--model", model,
                   "--output-format", "all", "--output-dir", out,
                   "--word-timestamps", "False", "--verbose", "False"]
        else:
            cmd = [preflight.find_tool("whisper"), audio, "--model", model,
                   "--output_format", "all", "--output_dir", out, "--fp16", "False"]
        if lang:
            cmd += ["--language", lang]
        run(cmd)
        data = json.loads((out / "audio.json").read_text(encoding="utf-8"))
        language = data.get("language", lang)
        segments = [{"start": s["start"], "end": s["end"], "text": s["text"].strip()}
                    for s in data.get("segments", [])]
    for s in segments:
        s["start"], s["end"] = round(s["start"], 2), round(s["end"], 2)
        s["mmss"] = mmss(s["start"])
    segments, dropped = clean_segments(segments, duration)
    (pack / "transcript.srt").write_text(_srt(segments), encoding="utf-8")
    write_json(pack / "transcript.json", {"engine": engine, "model": model,
                                           "language": language, "segments": segments})
    return {"status": "ok", "engine": engine, "model": model, "language": language,
            "segments": len(segments), "dropped_artifacts": len(dropped),
            "dropped_samples": dropped[:20], "error": None}


def _srt(segments):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text']}\n"
                     for i, s in enumerate(segments, 1))


# ------------------------------------------------------------------------ main

def build_parser():
    ap = argparse.ArgumentParser(
        description="Build an evidence pack (frames, transcript, metadata) from a video.",
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", metavar="SOURCE", help="http(s) URL or local video file")
    ap.add_argument("--out", required=True, metavar="OUT_DIR")
    ap.add_argument("--id", dest="sid", metavar="SUBMISSION_ID")
    ap.add_argument("--rubric", metavar="RUBRIC.json|.xlsx")
    ap.add_argument("--interval", type=float, default=5.0)
    ap.add_argument("--scene", type=float, default=0.30)
    ap.add_argument("--dedupe-threshold", type=float, default=DEDUPE_THRESHOLD,
                    metavar="MAD", help="drop a frame when its mean abs pixel difference "
                    f"(0-255) vs the previous kept frame is below this (default {DEDUPE_THRESHOLD})")
    ap.add_argument("--dedupe-tile-threshold", type=float, default=DEDUPE_TILE_THRESHOLD,
                    metavar="MAD", help="...and no 1/48 screen tile differs by this much "
                    f"(default {DEDUPE_TILE_THRESHOLD})")
    ap.add_argument("--mask-live", action="store_true",
                    help="ignore always-changing regions (webcam bubble, animated background) "
                         "when deduping. Off by default: it also hides typing in a formula bar")
    ap.add_argument("--no-dedupe", action="store_true",
                    help="keep every extracted frame")
    ap.add_argument("--max-height", type=int, default=1080)
    ap.add_argument("--frame-width", type=int, default=1920)
    ap.add_argument("--lang")
    ap.add_argument("--max-duration", type=float, metavar="SECONDS")
    ap.add_argument("--whisper-model", metavar="MODEL")
    ap.add_argument("--work-dir", metavar="DIR")
    ap.add_argument("--keep-video", action="store_true")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--cookies-from-browser", metavar="BROWSER")
    ap.add_argument("--source-url", metavar="URL",
                    help="with a local SOURCE: the video's original URL (manual-download "
                         "fallback) — keeps youtu.be watch links and fetches metadata if reachable")
    ap.add_argument("--force", action="store_true",
                    help="overwrite a non-empty pack directory")
    return ap


def main(argv=None):
    global FFMPEG
    a = build_parser().parse_args(argv)
    is_url = re.match(r"https?://", a.source) is not None
    if not is_url and not Path(a.source).is_file():
        log(f"error: file not found: {a.source}")
        return 4

    pf = preflight.run_checks(need_download=is_url, need_transcribe=not a.no_transcribe)
    if not pf["ok"]:
        log("Preflight failed; missing: " + ", ".join(pf["missing"]))
        log("Install with:\n" + pf["install_hint"])
        return 2
    FFMPEG = pf["tools"]["ffmpeg"]["path"]

    if a.sid:
        sid = slug(a.sid)
    elif is_url:
        sid = slug(youtube_id(a.source) or "url-" + hashlib.sha1(a.source.encode()).hexdigest()[:10])
    else:
        sid = slug(Path(a.source).stem)
    pack = Path(a.out).expanduser().resolve() / sid
    if pack.exists() and any(pack.iterdir()):
        if not a.force:
            log(f"error: pack dir not empty: {pack} (use --force to overwrite)")
            return 4
        shutil.rmtree(pack)
    pack.mkdir(parents=True, exist_ok=True)

    # Always a fresh private subdir (inside --work-dir when given) so cleanup never touches
    # anything the caller owns.
    if a.work_dir:
        Path(a.work_dir).expanduser().mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="video-evidence-",
                                 dir=str(Path(a.work_dir).expanduser()) if a.work_dir else None))
    warnings = []
    meta = {"contract": CONTRACT,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": {"kind": "url", "url": a.source} if is_url
            else {"kind": "file", "path": str(Path(a.source).resolve())},
            "submission_id": sid, "youtube": None,
            "watch": watch_meta(a.source_url, True) if (a.source_url and not is_url)
            else watch_meta(a.source, is_url),
            "download": {"status": "skipped", "error": None}, "probe": None,
            "params": {"interval": a.interval, "scene": a.scene,
                       "max_height": a.max_height, "frame_width": a.frame_width,
                       "dedupe": None if a.no_dedupe else {
                           "mask_live": a.mask_live,
                           "threshold": a.dedupe_threshold,
                           "tile_threshold": a.dedupe_tile_threshold},
                       "lang": a.lang, "max_duration": a.max_duration},
            "frames": None,
            "transcript": {"status": "skipped", "engine": None, "model": None,
                           "language": None, "error": None},
            "flags": {"over_max_duration": None}, "video_kept": None,
            "tool_versions": {k: v["version"] for k, v in pf["tools"].items()}}
    video = None
    created_video = False
    try:
        if is_url:
            log(f"downloading {a.source}")
            try:
                video, info = download(a.source, work, a.max_height, a.cookies_from_browser)
                created_video = True
            except (RuntimeError, OSError) as exc:
                meta["download"] = {"status": "failed", "error": str(exc)[-800:]}
                write_json(pack / "metadata.json", meta)
                log("Download failed. Download the video manually (e.g. with a GUI "
                    "downloader, or re-run with --cookies-from-browser chrome) and "
                    "re-run with the local file path as SOURCE.")
                log(str(exc)[-400:])
                return 3
            meta["download"] = {"status": "ok", "error": None}
            meta["youtube"] = {k: info.get(k) for k in YT_FIELDS}
        else:
            video = Path(a.source).resolve()
            if a.source_url:
                meta["source"]["url"] = a.source_url
                try:
                    info = fetch_info(a.source_url, a.cookies_from_browser)
                    meta["youtube"] = {k: info.get(k) for k in YT_FIELDS}
                except Exception as exc:  # bot-blocked etc.: links still work, text doesn't
                    meta["download"]["error"] = "metadata fetch failed: " + str(exc)[-300:]
                    warnings.append("--source-url metadata unavailable (title/description "
                                    "not fetched); description criteria need human review")

        try:
            meta["probe"] = probe(video)
            dur = meta["probe"]["duration_s"]
            if dur <= 0:
                raise RuntimeError("zero duration")
            if a.max_duration is not None:
                meta["flags"]["over_max_duration"] = dur > a.max_duration
                if dur > a.max_duration:
                    warnings.append(f"duration {mmss(dur)} exceeds max {mmss(a.max_duration)}")
            log(f"probe: {meta['probe']['duration_mmss']} "
                f"{meta['probe']['width']}x{meta['probe']['height']}")
            scenes = scene_times(video, a.scene)
            plan = plan_frames(dur, a.interval, scenes)
            log(f"extracting {len(plan)} frames ({len(scenes)} scene changes)")
            frames = extract_frames(video, plan, pack / "frames",
                                    min(meta["probe"]["width"], a.frame_width))
            if not frames:
                raise RuntimeError("no frames extracted")
            gaps = [b["t"] - a_["t"] for a_, b in zip(frames, frames[1:])]
            gaps.append(max(0.0, dur - frames[-1]["t"]))
            max_gap = round(max(gaps), 3)   # sampling gap between EXTRACTED frames
            extracted = len(frames)
            if a.no_dedupe:
                for f in frames:
                    f.update(static_until=f["t"], static_until_mmss=f["mmss"], absorbed=0)
                dropped, dd_info = 0, None
            else:
                frames, dropped, dd_info = dedupe_frames(frames, pack, FFMPEG,
                                                a.dedupe_threshold, a.dedupe_tile_threshold,
                                                a.mask_live)
                log(f"dedupe: kept {len(frames)} of {extracted} ({dropped} near-duplicates dropped)")
                if dd_info["live_tiles"] and not a.mask_live:
                    warnings.append(
                        f"{len(dd_info['live_tiles'])} always-changing screen tiles detected; "
                        "if that is a webcam bubble or animated background (check the contact "
                        "sheet), re-run with --mask-live to dedupe through it. Not masked by "
                        "default: typing in a formula bar looks the same")
            write_json(pack / "frames.json", {
                "count": len(frames), "extracted": extracted, "dropped_duplicates": dropped,
                "dedupe_threshold": None if a.no_dedupe else a.dedupe_threshold,
                "dedupe": dd_info,
                "max_gap_s": max_gap, "frames": frames})
            meta["frames"] = {"count": len(frames), "extracted": extracted,
                              "dropped_duplicates": dropped, "max_gap_s": max_gap,
                              "live_tiles": dd_info and dd_info["live_tiles"],
                              "masked": bool(dd_info and dd_info["masked"])}
            sheets = make_contact_sheets(pack, frames, work,
                                         pf["tools"]["ffmpeg"].get("drawtext", False))
            write_json(pack / "contact-sheet.json", {"sheets": sheets})
        except (RuntimeError, OSError, KeyError, ValueError) as exc:
            log(f"error: {exc}")
            meta["probe_error"] = str(exc)[-800:]
            write_json(pack / "metadata.json", meta)
            return 4

        if not a.no_transcribe:
            if not meta["probe"]["has_audio"]:
                meta["transcript"] = {"status": "no_audio", "engine": None, "model": None,
                                      "language": None, "error": None}
                warnings.append("video has no audio stream")
            else:
                log(f"transcribing with {pf['transcriber']}")
                try:
                    meta["transcript"] = transcribe(video, pack, work, pf["transcriber"],
                                                    a.whisper_model, a.lang, dur)
                except Exception as exc:  # non-fatal by design
                    meta["transcript"] = {"status": "failed", "engine": pf["transcriber"],
                                          "model": a.whisper_model, "language": None,
                                          "error": str(exc)[-800:]}
                    warnings.append("transcription failed: " + str(exc)[-200:])
                else:
                    # Whisper hallucinates short stock phrases ("Thank you.") over music or
                    # silence. Flag transcripts too sparse to count as narration.
                    segs = json.loads((pack / "transcript.json").read_text())["segments"]
                    words = sum(len(x["text"].split()) for x in segs)
                    wpm = words / max(dur / 60, 1e-6)
                    meta["transcript"]["words_per_min"] = round(wpm, 1)
                    meta["transcript"]["sparse"] = wpm < 30
                    if wpm < 30:
                        warnings.append(f"transcript sparse ({wpm:.0f} words/min): likely music "
                                        "or no narration; whisper may have hallucinated text")

        if a.keep_video:
            if created_video:
                dest = pack / f"video{video.suffix}"
                shutil.move(str(video), dest)
                meta["video_kept"] = str(dest)
            else:
                meta["video_kept"] = str(video)

        if a.rubric:
            try:
                write_json(pack / "evidence-map.json", evidence_map_skeleton(sid, a.rubric))
            except Exception as exc:
                warnings.append(f"rubric parse failed: {exc}")

        write_json(pack / "metadata.json", meta)
        summary = {"pack": str(pack), "submission_id": sid,
                   "duration": meta["probe"]["duration_mmss"],
                   "duration_s": meta["probe"]["duration_s"],
                   "frames": meta["frames"], "contact_sheets": [s["sheet"] for s in sheets],
                   "transcript": meta["transcript"]["status"],
                   "evidence_map": (pack / "evidence-map.json").exists(),
                   "flags": meta["flags"], "warnings": warnings}
        print(json.dumps(summary, indent=2))
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


FFMPEG = "ffmpeg"

if __name__ == "__main__":
    sys.exit(main())
