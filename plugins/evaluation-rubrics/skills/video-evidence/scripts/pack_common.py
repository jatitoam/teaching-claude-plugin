"""Shared helpers for the video-evidence scripts (stdlib only)."""
import hashlib
import json
from pathlib import Path

WATCH_LEAD_S = 3  # open a few seconds before the cited moment


def mmss(t):
    t = int(round(t))
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")


def frames_sha256(pack):
    """sha256 of the pack's frames.json bytes (integrity stamp), or None if absent."""
    p = Path(pack) / "frames.json"
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def watch_start(meta, t):
    """Second to open at: -WATCH_LEAD_S only for seekable YouTube links; exact otherwise."""
    kind = ((meta or {}).get("watch") or {}).get("kind")
    if kind == "youtube":
        return max(0, int(t) - WATCH_LEAD_S)
    return max(0, t)


def watch_ref(meta, t):
    """Human/agent-usable pointer to second `t` of the source video.

    youtube -> https://youtu.be/<id>?t=<t-3>   (3 s lead: seekable link)
    file -> "<mm:ss> <abs path>"   url (non-YouTube / unknown) -> "<mm:ss> <url>"
    file/url carry the EXACT cited time (no lead): the viewer seeks by hand.
    """
    w = (meta or {}).get("watch") or {}
    kind = w.get("kind")
    start = watch_start(meta, t)
    if kind == "youtube":
        return w["template"].replace("{s}", str(start)) if w.get("template") \
            else f"https://youtu.be/{w['id']}?t={start}"
    if kind == "file":
        return f"{mmss(start)} {w['path']}"
    if kind == "url":
        return f"{mmss(start)} {w['url']}"
    return mmss(start)
