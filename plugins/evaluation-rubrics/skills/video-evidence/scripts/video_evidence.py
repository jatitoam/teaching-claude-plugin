#!/usr/bin/env python3
"""Decompose a video submission into an auditable on-disk "evidence pack".

Claude cannot watch video, so this script turns one into files a model can
read and cite against a rubric. Output contract (``video-evidence/1``)::

    OUT_DIR/<id>/
        metadata.json        source, probe, params, download/transcript status, flags
        frames/tSSSS.mmm.jpg timestamped frames (interval + scene-change passes)
        frames.json          [{"file","t","mmss","reasons"}], plus max_gap_s
        contact-sheet[-NN].jpg   thumbnail grid(s) of the frames
        contact-sheet.json   cell (row,col) -> timestamp for each sheet
        transcript.json      {"engine","model","language","segments":[{start,end,mmss,text}]}
        transcript.srt
        evidence.json        (with --rubric) grading skeleton, status PENDING_GRADING
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

CONTRACT = "video-evidence/1"
COLS = 6
THUMB_W = 320
MAX_PER_SHEET = 60
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


def mmss(t):
    t = int(round(t))
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


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


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")


# --------------------------------------------------------------------- rubric

def parse_rubric(path):
    """Return (criteria, penalties) as lists of dicts for evidence.json."""
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


def evidence_skeleton(sid, rubric_path):
    def shape(c, amount_key="weight"):
        out = {"criterion": c["criterion"], amount_key: c["weight"]}
        if c["levels"]:
            out["levels"] = c["levels"]
        out.update({"verdict": "PENDING", "evidence": [], "review_required": [],
                    "note": ""})
        return out
    criteria, penalties = parse_rubric(rubric_path)
    doc = {"contract": CONTRACT, "submission_id": sid,
           "rubric_source": str(rubric_path), "status": "PENDING_GRADING",
           "criteria": [shape(c) for c in criteria]}
    if penalties:
        doc["penalties"] = [shape(c, "penalty") for c in penalties]
    return doc


# ------------------------------------------------------------------- download

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
        lines.append(f"file '{sources[-1]}'")
        lst.write_text("\n".join(lines) + "\n")
        run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
             "-safe", "0", "-i", lst, "-vf",
             f"scale={THUMB_W}:-2,tile={COLS}x{rows}:padding=4:color=black",
             "-frames:v", "1", "-q:v", "3", pack / name])
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

def transcribe(video, pack, work, engine, model, lang):
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
    segments = [s for s in segments if s["text"]]  # whisper emits empty tail segments
    (pack / "transcript.srt").write_text(_srt(segments), encoding="utf-8")
    write_json(pack / "transcript.json", {"engine": engine, "model": model,
                                           "language": language, "segments": segments})
    return {"status": "ok", "engine": engine, "model": model, "language": language,
            "segments": len(segments), "error": None}


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
    ap.add_argument("--max-height", type=int, default=1080)
    ap.add_argument("--frame-width", type=int, default=1920)
    ap.add_argument("--lang")
    ap.add_argument("--max-duration", type=float, metavar="SECONDS")
    ap.add_argument("--whisper-model", metavar="MODEL")
    ap.add_argument("--work-dir", metavar="DIR")
    ap.add_argument("--keep-video", action="store_true")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--cookies-from-browser", metavar="BROWSER")
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
            "download": {"status": "skipped", "error": None}, "probe": None,
            "params": {"interval": a.interval, "scene": a.scene,
                       "max_height": a.max_height, "frame_width": a.frame_width,
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
            meta["youtube"] = {k: info.get(k) for k in (
                "id", "title", "description", "uploader", "channel", "upload_date",
                "availability")}
            meta["youtube"]["webpage_url"] = info.get("webpage_url")
        else:
            video = Path(a.source).resolve()

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
            max_gap = round(max(gaps), 3)
            write_json(pack / "frames.json", {"count": len(frames), "max_gap_s": max_gap,
                                              "frames": frames})
            meta["frames"] = {"count": len(frames), "max_gap_s": max_gap}
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
                                                    a.whisper_model, a.lang)
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
                write_json(pack / "evidence.json", evidence_skeleton(sid, a.rubric))
            except Exception as exc:
                warnings.append(f"rubric parse failed: {exc}")

        write_json(pack / "metadata.json", meta)
        summary = {"pack": str(pack), "submission_id": sid,
                   "duration": meta["probe"]["duration_mmss"],
                   "duration_s": meta["probe"]["duration_s"],
                   "frames": meta["frames"], "contact_sheets": [s["sheet"] for s in sheets],
                   "transcript": meta["transcript"]["status"],
                   "evidence_skeleton": (pack / "evidence.json").exists(),
                   "flags": meta["flags"], "warnings": warnings}
        print(json.dumps(summary, indent=2))
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


FFMPEG = "ffmpeg"

if __name__ == "__main__":
    sys.exit(main())
