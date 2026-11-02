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
| 2. Index | **Haiku**, one per ≤ 24 frames (1280-px copies) | `frames-index.json` — describes frames, never judges |
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
- **Sources.** Any URL or local file. The script classifies it (`youtube | gdrive | canva |
  other-url | local`) and tries **yt-dlp for every URL**. This skill never prompts the user and
  contains no Drive/Canva API client.
- **Exit 3 = manual download needed.** stdout carries a JSON object (`source_type`, `url`,
  `reason`, `save_to`, `resume_args`; see the contract). Hand it back to the caller —
  assignment-evaluator turns it into a request to the instructor. Once the file exists, re-run
  with `resume_args` (local path + `--source-url <original> --obtained-via manual`).
- **Connectors (optional, caller's choice).** If the host session has an authenticated connector
  that can export the video (e.g. Canva: get-export-formats → export-design mp4 → download the
  signed URL), the caller may use it and pass `--source-url <original> --obtained-via connector`.
  Never required.
- `watch`: YouTube → `youtu.be/<id>?t=`; Drive/Canva/other → `mm:ss <original view URL>` (Drive
  URL seeking is unverified, so no `&t=`); local → `mm:ss <path>`. Title/description are fetched
  only for YouTube; elsewhere description criteria are REVIEW_REQUIRED.
- YouTube rate-limits download bursts (HTTP 429 / "sign in to confirm") — capture sequentially;
  `--cookies-from-browser chrome` only with the user's OK (it reads browser cookies).
- Read the printed summary: `warnings`, `frames.extracted → count` (dedupe), `max_gap_s`,
  transcript status / `sparse`.

## Step 2 — Index (Haiku)

Check `metadata.index.recommended` (also in the capture summary):

- `"skip"` → no index; the Sonnet selector opens every frame itself (Step 3 handles it).
- `"haiku"` → split `frames.json → frames[]` into even batches of **≤ 24** and dispatch one Haiku
  agent per batch with `references/index-brief.md` (`model: haiku`, description
  `[Haiku] Index frames <id> b<NN>`), ≤ 8 agents per message. Haiku reads the 1280-px copies in
  `index-frames/`; selector and judge keep the full-res `frames/`.

Then `python3 "$S/merge_index.py" <pack>`; exit 1 lists frames no batch described → re-dispatch
just those. Haiku describes; it never decides small-text questions — the selector and judge do.

**When to skip (break-even, `--index-min-frames`, default 2).** Indexing N kept frames costs
`(F + h·N)·pH`; letting the Sonnet selector read them directly costs `s·N·pS`. Skip iff
`N ≤ N* = F·pH / (s·pS − h·pH)`. Measured / current values (2026-11): F = 62k tokens fixed per
Haiku agent, h = 1.45k per 1280-px frame, s = 1.8k per full-res frame for Sonnet, pH = $0.10/MTok
(Haiku 5.5, prompts ≤ 100k), pS = $2.00/MTok (Sonnet 5.5) → **N\* = 6.2 / 3.455 ≈ 1.8 frames**, so
index from 2 kept frames: in practice only a clip of a few seconds (first + last frame) skips.
Re-derive when prices change. Haiku is 20× cheaper per token, so its fixed overhead is repaid
almost immediately; the index also keeps the selector's context small on long videos.

**Why 24 frames at 1280 px.** Haiku 5.5 bills prompts over 100k tokens at 5× ($0.50/MTok). A batch
reaches F + 24·h ≈ 97k — just under the cliff (measured 98–101.6k). At 1080p (h ≈ 3k) the same
cliff caps batches at ~12. Alignment held at 24 one-frame-at-a-time (checked on a 104-frame
video); it drifted at 35 frames per agent.

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
