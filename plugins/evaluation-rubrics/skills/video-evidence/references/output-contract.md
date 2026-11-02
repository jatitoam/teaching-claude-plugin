# Output contract — `video-evidence/2`

Every JSON file carrying a `contract` field declares `"video-evidence/2"`. A breaking change to
any shape below bumps it (and the plugin's MAJOR version once released to other users).

**v1 → v2:** `evidence.json` (verdicts) is gone. The pack no longer judges; it maps evidence
(`evidence-map.json`). Verdicts live in `verdicts.json`, written by the judge
(assignment-evaluator). Frames are de-duplicated; `frames-index.json` and `watch` links are new.

```
<out>/<submission-id>/
├── metadata.json           # capture (script)
├── frames/t0000.000.jpg …  # capture — kept frames only; t<seconds:4>.<ms:3>.jpg
├── frames.json             # capture
├── contact-sheet.jpg       # capture — contact-sheet-01.jpg, -02.jpg … when > 60 frames
├── contact-sheet.json      # capture — every sheet, cell (row, col) → file, t, mmss
├── transcript.json/.srt    # capture — unless --no-transcribe, no audio, or failure
├── frames-index/batch-NN.json  # index (Haiku), merged by merge_index.py into ↓
├── frames-index.json       # index
├── evidence-map.json       # skeleton (script, with --rubric) → filled by select (Sonnet) → finalize_pack.py
├── verdicts.json           # judge (assignment-evaluator) → enriched by render_review.py
├── review.md               # judge — rendered by render_review.py; local only
└── video.mp4               # only with --keep-video
```

## metadata.json

| Field | Meaning |
|---|---|
| `contract`, `generated_at`, `submission_id` | identity |
| `source.kind` / `.url` / `.path` | `url` or `file` |
| `youtube` | `{id, title, description, uploader, channel, upload_date, availability, webpage_url}` or `null` |
| `download` | `{status: ok\|failed\|skipped, error}` |
| `probe` | `{duration_s (ffprobe exact), duration_mmss, width, height, fps, has_audio, codec}` |
| `params` | tunables used |
| `frames` | `{count (kept), extracted, dropped_duplicates, max_gap_s}` — `max_gap_s` is the sampling gap between extracted frames, incl. the tail |
| `transcript` | `{status: ok\|failed\|skipped\|no_audio, engine, model, language, segments, error, words_per_min, sparse}` — `sparse` (< 30 words/min) = music/no narration, text may be hallucinated |
| `watch` | `{kind: "youtube", id, template: "https://youtu.be/<id>?t={s}"}` (YouTube URL, or local file + `--source-url`) · `{kind: "file", path}` · `{kind: "url", url}` (non-YouTube URL) |
| `flags.over_max_duration` | `true`/`false`, `null` without `--max-duration` |
| `video_kept`, `tool_versions` | hygiene / reproducibility |

## frames.json

```json
{"count": 66, "extracted": 102, "dropped_duplicates": 36, "dedupe_threshold": 1.5, "max_gap_s": 5.0,
 "dedupe": {"threshold": 1.5, "tile_threshold": 3.0, "grid": "8x6",
            "live_tiles": [[4, 0], [5, 1]], "masked": true},
 "frames": [{"file": "frames/t0010.000.jpg", "t": 10.0, "mmss": "00:10",
             "reasons": ["interval", "scene"], "static_until": 35.0,
             "static_until_mmss": "00:35", "absorbed": 5}]}
```

`reasons` ⊆ `interval | scene | last`. A kept frame represents the screen from `t` until
`static_until` (the near-identical frames it absorbed were deleted). First and last frames are
never dropped.

Dedupe compares 160×90 grayscale thumbnails against the previous **kept** frame on an 8×6 tile
grid: drop only if the mean diff < `threshold` AND no tile differs by ≥ `tile_threshold`
(a checkbox tick is a tiny area). **Live tiles** — tiles that change in ≥ 40 % of consecutive
pairs (a webcam bubble, an animated background, *or a formula bar being typed into*) — are
always detected and listed; they are excluded from the comparison only with `--mask-live`
(`masked: true`), and never when fewer than 8 quiet tiles would remain.

## frames-index.json (Haiku — descriptive only)

`{contract, count, frames: [{file, t, mmss, static_until_mmss, app, screen, headings[], key_text[], summary}]}`.
`key_text` is verbatim or `"[small text unreadable]"`. Leads, not facts.

## transcript.json

`{engine, model, language, segments: [{start, end, mmss, text}]}`; empty segments dropped; the SRT
is generated from the same segments.

## evidence-map.json (Sonnet — no verdicts)

```json
{"contract": "video-evidence/2", "submission_id": "grupo3", "rubric_source": "…",
 "status": "SELECTED",
 "items": [
  {"id": "C1", "kind": "criterion", "criterion": "Relationship line visible in Model view",
   "weight": 35, "levels": {"cumple": "…", "parcial": "…", "no_cumple": "…"},
   "candidates": [
     {"from": 95.0, "to": 140.0, "from_mmss": "01:35", "to_mmss": "02:20",
      "frames": ["frames/t0100.000.jpg"], "quotes": [{"t": 98.2, "mmss": "01:38", "text": "…"}],
      "metadata_fields": [], "why": "Model view with a line between Sales and Products",
      "watch": "https://youtu.be/b-NE9crKYYw?t=92"}],
   "coverage": ""},
  {"id": "P1", "kind": "penalty", "criterion": "Duration <= 5 min", "penalty": "-10",
   "levels": {…}, "candidates": [{"from": 0, "to": 490.0, "frames": [], "quotes": [],
   "metadata_fields": ["probe.duration_s"], "why": "duration_s = 490.0", "watch": "…"}],
   "coverage": ""}]}
```

Status: `PENDING_SELECTION` (skeleton) → `SELECTED` (after `finalize_pack.py` passes). Every
item has ≥ 1 candidate **or** a `coverage` note (what was searched, and the stretch where it could
have been missed). Every cited frame exists; every candidate has `why`.

## verdicts.json (judge)

```json
{"submission_id": "grupo3",
 "items": [{"id": "C1", "kind": "criterion", "criterion": "…",
            "verdict": "Meets Expectations",
            "note": "…",
            "cites": [{"t": 100.0, "frame": "frames/t0100.000.jpg", "quote": null,
                       "metadata_field": null, "watch": "https://youtu.be/…?t=97"}],
            "review_required": [{"from": 220.0, "to": 230.0, "reason": "fast scroll",
                                 "watch": "…"}]}],
 "key_moments": [{"t": 0.0, "frame": "frames/t0000.000.jpg", "label": "cover", "watch": "…"}]}
```

- Criterion verdicts: `Meets Expectations` | `Partially Meets` | `Does Not Meet` | `REVIEW_REQUIRED`.
- Penalty verdicts: `met` | `partial` | `not_met` | `REVIEW_REQUIRED`.
- Every non-REVIEW verdict has ≥ 1 cite; every REVIEW_REQUIRED has ≥ 1 window.
- `watch` is filled by `render_review.py` (YouTube: `https://youtu.be/<id>?t=<from − 3 s>`, works
  for unlisted; local file: `"mm:ss <path>"`).

## review.md

Rendered from `verdicts.json`: header (title, source, duration, flags, transcript status) →
**Needs your review** (REVIEW_REQUIRED first: criterion, window, reason, watch link, thumbnail) →
**Verdicts** (criterion → verdict → note → watch links → thumbnail) → **Key moments**
(chronological). Thumbnails are relative `frames/…` links. Local only — student data.
