---
name: video-evidence
description: >
  Turns a video submission (YouTube URL — public or unlisted — or a local video file) into an
  on-disk, auditable evidence pack — metadata incl. the YouTube title/description, exact
  duration, de-duplicated timestamped frames (scene changes + fixed interval), contact sheets,
  a timestamped transcript, a per-frame index, and (with a rubric) an evidence-map.json that
  points each criterion to the windows, frames, quotes and metadata where it can be judged,
  with watch links. Captures, indexes and selects evidence only — it does NOT grade. Use when
  assignment-evaluator meets a video submission, or when asked to "build the evidence pack" /
  "index this video for grading". Do NOT trigger for editing, producing, or summarizing videos
  for non-evaluation purposes.
---

# Video Evidence

Claude cannot watch video; it reads images and text. This skill decomposes a video into an
evidence pack on disk and points the judge at the right moments. **It never issues verdicts** —
`assignment-evaluator` does (see its "Video submissions" section).

Contract: **`video-evidence/2`** — `references/output-contract.md`.
Scripts: `${CLAUDE_PLUGIN_ROOT}/skills/video-evidence/scripts/` (below: `$S`).

| Stage | Who | Output |
|---|---|---|
| 1. Capture | script, no model | metadata, frames (deduped), contact sheets, transcript, evidence-map skeleton |
| 2. Index | **Haiku**, one per ≤ 16 frames | `frames-index.json` — describes frames, never judges |
| 3. Select | **Sonnet**, one per video | `evidence-map.json` — candidate windows per criterion, no verdicts |
| 4. Judge | assignment-evaluator (lead, or a delegated Sonnet) | `verdicts.json`, `review.md`, row JSON |

## Step 0 — Preflight (always)

```bash
python3 "$S/preflight.py" [--need-download] [--no-transcribe]
```

`--need-download` when any input is a URL. Non-zero exit → **stop** and point the user at
`/evaluation-rubrics:install-video-deps` (it previews with `--dry-run` and asks before
installing). Never install on your own initiative.

## Step 1 — Capture (script)

```bash
python3 "$S/video_evidence.py" <url-or-path> --out <out_dir> --id <slug> \
  [--rubric <rubric.json|xlsx>] [--lang es] [--max-duration 300] [--interval 5]
```

- Inputs: source; output dir (assignment-evaluator passes `<output_dir>/evidence/`); submission
  id (student/group slug); optional rubric (rubric-creator JSON preferred — carries level texts).
- Tunables only when the brief implies them: `--interval` (default 5 s; 2–3 for fast-scrolling
  recordings), `--scene` (0.30), `--max-height` (1080), `--lang`, `--max-duration` (flags, never
  fails), `--dedupe-threshold` / `--no-dedupe`, `--mask-live` (only after checking the contact
  sheet: the warning fires, and the always-changing region really is a webcam/animation).
- Downloads go to an OS temp subdir and are deleted afterwards unless `--keep-video`.
- Several videos: capture **sequentially** — YouTube rate-limits download bursts, and
  transcription is heavy. Index/select stages parallelize instead.
- **Exit 3 (download failed):** retry once with `--cookies-from-browser chrome` (ask first — it
  reads browser cookies), else ask for a manual download and re-run on the local path **with
  `--source-url <the YouTube URL>`** — the pack keeps `youtu.be/…?t=` watch links and fetches the
  title/description if YouTube answers. If it can't, the warning says so and the judge must treat
  description criteria as REVIEW_REQUIRED. Bursts of downloads trigger YouTube's bot check
  (HTTP 429); capture sequentially when grading a whole class.
- Read the printed summary: `warnings`, `frames.extracted → count` (dedupe), `max_gap_s`,
  transcript status / `sparse`.

## Step 2 — Index (Haiku)

Split each pack's `frames.json → frames[]` into even batches of ≤ 16 and dispatch one Haiku agent
per batch with `references/index-brief.md` (`model: haiku`, description
`[Haiku] Index frames <id> b<NN>`) — every batch of every video in one message. Then:

```bash
python3 "$S/merge_index.py" <pack>
```

Exit 1 lists frames no batch described → re-dispatch just those. Haiku describes; it never
decides small-text questions (name vs code etc.) — the selector and judge open the frames.

## Step 3 — Select (Sonnet) — only with a rubric

One Sonnet agent per video, all in one message, with `references/select-brief.md`
(`model: sonnet`, description `[Sonnet] Select evidence <id>`). It fills `evidence-map.json` and
runs `finalize_pack.py`, which validates the map and fills every `watch` link
(`https://youtu.be/<id>?t=<s−3>` for YouTube, `mm:ss <path>` for local files).

Lead check: `python3 "$S/finalize_pack.py" <pack>` exits 0 for every pack.

## Step 4 — Hand off

Return the pack path(s) to assignment-evaluator, which judges from `evidence-map.json` + the cited
frames and renders `review.md` with `$S/render_review.py`. Standalone use (no evaluator): report
pack paths and stop — do not grade.

Packs contain student data: keep them local, never publish them.

## Known limits

- Sampling can miss sub-second events; `coverage` notes and REVIEW_REQUIRED exist for that.
- Small text depends on the uploaded resolution; a 480p upload cannot be made legible.
- Dedupe compares low-res thumbnails; a tiny change (one digit) on an otherwise static screen can
  be absorbed into the previous frame — `static_until` shows the span to re-check.
- Dedupe saves little on busy recordings at 5 s sampling (measured: 18→17, 104→104, 13→13);
  it pays off on static-heavy ones (19→5) and, with `--mask-live`, on webcam videos (102→66).
- `--mask-live` (off by default) ignores always-changing regions — a webcam bubble, an animated
  background. It is opt-in because a formula bar being typed into looks identical to that test:
  on a real DAX recording it silently dropped the frames showing the formula being written. The
  script warns when it detects such regions; check the contact sheet before re-running with it.
- Whisper hallucinates filler over music/silence (`transcript.sparse`) and loops phrases past the
  end of the audio; segments past the video's end and 3+ identical repeats are dropped
  (`transcript.dropped_artifacts`).
- Homebrew's ffmpeg lacks `drawtext`, so sheets carry no burned-in timestamps;
  `contact-sheet.json` maps cells to times.
- No speaker attribution in the transcript.
