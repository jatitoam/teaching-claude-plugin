"""Shared helpers for the video-evidence scripts (stdlib only)."""
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


def watch_ref(meta, t):
    """Human/agent-usable pointer to second `t` of the source video.

    youtube -> https://youtu.be/<id>?t=<s>   file -> "<mm:ss> <abs path>"
    url (non-YouTube / unknown) -> "<mm:ss> <url>"
    """
    w = (meta or {}).get("watch") or {}
    start = max(0, int(t) - WATCH_LEAD_S)
    kind = w.get("kind")
    if kind == "youtube":
        return w["template"].replace("{s}", str(start)) if w.get("template") \
            else f"https://youtu.be/{w['id']}?t={start}"
    if kind == "file":
        return f"{mmss(start)} {w['path']}"
    if kind == "url":
        return f"{mmss(start)} {w['url']}"
    return mmss(start)
