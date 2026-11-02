---
name: video-evidence
description: >
  Turns a video submission (YouTube URL — public or unlisted — or a local video file) into an
  on-disk, auditable evidence pack — metadata incl. the YouTube title/description, exact
  duration, timestamped frames (scene changes + fixed interval), a contact sheet, and a
  timestamped transcript — and, when a rubric is given, a per-criterion evidence.json with
  verdicts that cite timestamps, frames, and quotes. Use when grading or reviewing a video
  deliverable ("evaluate this video", "grade this YouTube submission", "build the evidence
  pack for these videos"), and whenever assignment-evaluator meets a submission that is or
  contains a video link/file. Do NOT trigger for editing, producing, or summarizing videos
  for non-evaluation purposes.
---

# Video Evidence

Claude cannot watch video; it reads images and text. This skill decomposes a video into an
evidence pack (frames + transcript + metadata) on disk, then grades against the pack. The
deterministic part is a script; the model only judges what the pack shows.

Output contract: **`video-evidence/1`** — see `references/output-contract.md`.

Scripts live in `${CLAUDE_PLUGIN_ROOT}/skills/video-evidence/scripts/` (below: `$S`).

## Step 1 — Preflight (always, before anything else)

```bash
python3 "$S/preflight.py" [--need-download] [--no-transcribe]
```

Pass `--need-download` when any input is a URL. If it exits non-zero, **stop**: show the user
the `install_hint` from its JSON (first option: `bash "$S/setup-video-deps.sh"`) and wait. Do not
start a partial run. Never run the setup script with sudo or on the user's behalf without
asking — it installs software.

## Step 2 — Gather inputs

- **Source(s)** — URL(s) or local path(s). One pack per video.
- **Output dir** — where packs go (`<out>/<submission-id>/`). Ask if not given and there is no
  obvious grading folder (assignment-evaluator passes `<output_dir>/evidence/`).
- **Submission id** — student/group slug if known (`--id`); otherwise the script derives it from
  the YouTube id or file stem.
- **Rubric** (optional) — rubric-creator JSON (preferred) or its xlsx. Enables `evidence.json`.
- **Tunables** — only if the user/brief implies them: `--interval` (s, default 5),
  `--scene` (0–1, default 0.30), `--max-height` (default 1080), `--lang` (e.g. `es`),
  `--max-duration` (s; e.g. 300 for a "≤ 5 min" requirement — flags, doesn't fail).
  Lower `--interval` to 2–3 s for fast screen recordings with lots of scrolling.

## Step 3 — Build the pack (script)

```bash
python3 "$S/video_evidence.py" <url-or-path> --out <out_dir> [--id <slug>] \
  [--rubric <rubric.json|xlsx>] [--lang es] [--max-duration 300] [--interval 5]
```

- Downloads go to an OS temp dir (outside synced folders) and are **deleted** after the pack is
  built. Pass `--keep-video` only if the user asks.
- Several videos: run them sequentially or a few in parallel via Bash background jobs —
  transcription is CPU/GPU-heavy, so cap at ~2 concurrent on a laptop.
- **Exit 3 (download failed)** — YouTube bot-check, private video, etc. Retry once with
  `--cookies-from-browser chrome` (ask first — it reads browser cookies). Otherwise ask the user
  to download the file manually (e.g. a GUI downloader) and re-run with the local path. Record
  that the YouTube description could not be fetched — a criterion about the description then
  becomes `REVIEW_REQUIRED`, never `Does Not Meet`.
- The script prints a JSON summary; check `warnings`, `frames.max_gap_s`, and
  `transcript.status` before grading. A `transcript sparse` warning means music/no narration —
  Whisper may have hallucinated filler text, so the transcript is not narration evidence.

## Step 4 — Grade from the pack (only if a rubric was given)

Delegate one **Sonnet** subagent per video (all in one message, so they run in parallel), using
the brief in `references/grader-brief.md` filled with the pack path and rubric path. Each
subagent reads `metadata.json`, `frames.json`, `transcript.json`, the contact sheet(s), and the
individual frames it needs, and fills `evidence.json`.

The lead then:
1. Validates each `evidence.json`: every criterion has a verdict; every non-`REVIEW_REQUIRED`
   verdict cites at least one frame file or transcript quote; cited frames exist.
2. Spot-checks borderline items itself (open the cited frames). Resolve what it can; leave the
   rest as `REVIEW_REQUIRED` with `mm:ss` for the human.
3. Presents a per-video summary table (criterion → verdict → timestamps) and lists all
   `REVIEW_REQUIRED` items with their `mm:ss` so the instructor can scrub to them.

### Grading rules (non-negotiable)

- **Absence of evidence ≠ evidence of absence.** If the thing could have appeared between two
  sampled frames (gap > a few seconds, fast scroll, transition), or text is too small/blurry to
  read, the verdict is `REVIEW_REQUIRED` with the time window — **never** `Does Not Meet`.
- `Does Not Meet` requires positive evidence: a frame showing the wrong thing, a transcript
  statement, or a metadata fact (e.g. `duration_s` 412 vs a 300 s cap; description present and
  lacking the declaration).
- Cite every verdict: `mm:ss` + frame file and/or a transcript quote with its `mm:ss`.
- Metadata-grounded criteria (duration, title, YouTube description, first frame = cover) are
  graded from `metadata.json` / the `t0000.000` frame, not from impressions.
- Write notes in the language of the assignment brief (fallback: rubric language).

## Step 5 — Hand off

Standalone: report pack path(s), the summary table, and the `REVIEW_REQUIRED` list.
Called from assignment-evaluator: return the `evidence.json` path(s); that skill maps verdicts to
its row JSON (see its "Video submissions" section).

## Known limits

- Frame sampling can miss sub-second events; `REVIEW_REQUIRED` exists for that.
- Small UI text depends on the uploaded resolution; a 480p upload cannot be made legible.
- Whisper hallucinates filler over music/silence; the `sparse` flag catches the common case only.
- No timestamp labels are burned into the contact sheet when ffmpeg lacks `drawtext` (Homebrew's
  default build); `contact-sheet.json` maps each grid cell to its timestamp instead.
- Speaker-to-person attribution (who is talking) is not available — the transcript is unlabelled.
- YouTube may bot-block downloads from some networks; see Step 3 exit 3.
