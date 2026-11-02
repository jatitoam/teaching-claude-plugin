#!/usr/bin/env python3
"""Preflight for the video-evidence skill.

Checks the external tools needed to build an evidence pack and prints a JSON
report to stdout:

    {"ok": bool,
     "tools": {name: {"path": str, "version": str}},
     "transcriber": "mlx_whisper" | "whisper" | "faster_whisper" | null,
     "missing": [str, ...],
     "install_hint": "<exact command(s)>"}

Exit code 0 when everything required is present, 1 otherwise.
Python 3 stdlib only.
"""
import argparse
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_FILTERS = ("select", "scale", "tile")
SETUP_SCRIPT = Path(__file__).resolve().parent / "setup-video-deps.sh"

# Extra places where pipx / brew put binaries that may not be on a minimal PATH.
EXTRA_BIN_DIRS = ("/opt/homebrew/bin", "/usr/local/bin", str(Path.home() / ".local/bin"))


def find_tool(name):
    path = shutil.which(name)
    if path:
        return path
    for d in EXTRA_BIN_DIRS:
        cand = Path(d) / name
        if cand.is_file():
            return str(cand)
    return None


def _run(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def tool_version(path, args=("--version",)):
    rc, out = _run([path, *args])
    line = out.strip().splitlines()[0] if out.strip() else ""
    return line if rc == 0 and line else "unknown"


def ffmpeg_filters(ffmpeg):
    """Return the set of filter names ffmpeg exposes."""
    _, out = _run([ffmpeg, "-hide_banner", "-filters"])
    names = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and len(parts[0]) <= 3 and parts[0][0] in ".T":
            names.add(parts[1])
    return names


def install_hint():
    system = platform.system()
    setup = f'bash "{SETUP_SCRIPT}"'
    if system == "Darwin":
        raw = ("brew install ffmpeg yt-dlp pipx && "
               + ("pipx install mlx-whisper" if platform.machine() == "arm64"
                  else "pipx install openai-whisper"))
        return f"{setup}\n# or manually:\n{raw}"
    raw = ("sudo apt-get install -y ffmpeg pipx && pipx install yt-dlp "
           "&& pipx install openai-whisper")
    return f"{setup}   # prints the commands on Linux\n# or manually:\n{raw}"


def run_checks(need_download=False, need_transcribe=True):
    tools, missing = {}, []
    ffmpeg = find_tool("ffmpeg")
    for name in ("ffmpeg", "ffprobe"):
        path = find_tool(name)
        if path:
            tools[name] = {"path": path,
                           "version": tool_version(path, ("-version",))}
        else:
            missing.append(name)
    if ffmpeg:
        have = ffmpeg_filters(ffmpeg)
        for f in REQUIRED_FILTERS:
            if f not in have:
                missing.append(f"ffmpeg filter '{f}'")
        tools["ffmpeg"]["drawtext"] = "drawtext" in have

    ytdlp = find_tool("yt-dlp")
    if ytdlp:
        tools["yt-dlp"] = {"path": ytdlp, "version": tool_version(ytdlp)}
    elif need_download:
        missing.append("yt-dlp")

    transcriber = None
    if need_transcribe:
        for name, exe in (("mlx_whisper", "mlx_whisper"), ("whisper", "whisper")):
            path = find_tool(exe)
            if path:
                transcriber = name
                tools[name] = {"path": path, "version": tool_version(path)}
                break
        if transcriber is None and importlib.util.find_spec("faster_whisper"):
            transcriber = "faster_whisper"
            tools["faster_whisper"] = {"path": sys.executable, "version": "module"}
        if transcriber is None:
            missing.append("transcriber (mlx_whisper | whisper | faster_whisper)")

    return {"ok": not missing, "tools": tools, "transcriber": transcriber,
            "missing": missing, "install_hint": install_hint()}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check video-evidence dependencies.")
    ap.add_argument("--need-download", action="store_true",
                    help="require yt-dlp (input is a URL)")
    ap.add_argument("--no-transcribe", action="store_true",
                    help="skip the transcriber check")
    args = ap.parse_args(argv)
    report = run_checks(args.need_download, not args.no_transcribe)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
