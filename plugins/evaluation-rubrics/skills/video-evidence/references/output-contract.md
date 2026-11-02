# Output contract — `video-evidence/1`

Every file carrying a `contract` field declares `"video-evidence/1"`. A breaking change to any
shape below bumps it to `/2` (and the plugin's MAJOR version).

```
<out>/<submission-id>/
├── metadata.json          # always
├── frames/                # always (unless probe failed)
│   ├── t0000.000.jpg      # t<seconds:4>.<ms:3>.jpg — first frame is always t0000.000
│   └── …
├── frames.json            # always
├── contact-sheet.jpg      # or contact-sheet-01.jpg, -02.jpg … when frames > 60
├── contact-sheet.json     # always: grid cell (row, col) → frame file + timestamp
├── transcript.json        # unless --no-transcribe, no audio, or transcription failed
├── transcript.srt         # same
├── evidence.json          # only with --rubric; skeleton from the script, filled by the grader
└── video.mp4              # only with --keep-video
```

## metadata.json

| Field | Meaning |
|---|---|
| `contract`, `generated_at`, `submission_id` | identity |
| `source.kind` / `source.url` / `source.path` | `url` or `file` |
| `youtube` | `{id, title, description, uploader, channel, upload_date, availability}` or `null` (local file / download failed) |
| `download.status` | `ok` \| `failed` \| `skipped` (local file); `download.error` = stderr tail |
| `probe` | `{duration_s, duration_mmss, width, height, fps, has_audio, codec}` — `duration_s` is ffprobe's exact value |
| `params` | the tunables used (`interval`, `scene`, `max_height`, `frame_width`, `lang`, `max_duration`) |
| `frames` | `{count, max_gap_s}` — `max_gap_s` bounds what sampling could have missed |
| `transcript` | `{status, engine, model, language, segments, error, words_per_min, sparse}` — `status` ∈ `ok` \| `failed` \| `skipped` \| `no_audio`; `sparse: true` (< 30 words/min) means music/no narration and possibly hallucinated text |
| `flags.over_max_duration` | `true`/`false`, or `null` when no `--max-duration` |
| `video_kept`, `tool_versions` | hygiene / reproducibility |

## frames.json

`{count, max_gap_s, frames: [{file, t, mmss, reasons}]}` sorted by `t`; `reasons` ⊆
`["interval", "scene", "last"]` (a scene cut within 0.5 s of an interval tick is merged into one
entry). The last frame (`duration − 0.5 s`, reason `last`) is always included; `max_gap_s`
includes the tail to the end of the video.

## transcript.json

`{engine, model, language, segments: [{start, end, mmss, text}]}` — seconds as floats; empty
segments are dropped. `transcript.srt` is generated from the same segments.

## evidence.json

Script writes the skeleton (`status: "PENDING_GRADING"`, every `verdict: "PENDING"`, rubric level
texts copied into each entry's `levels`); the grader fills it and sets `status: "GRADED"`.
Criteria carry `weight` (number); penalties carry `penalty` (the rubric's free-text amount).

```json
{
  "contract": "video-evidence/1",
  "submission_id": "grupo3",
  "rubric_source": "/path/rubrica_entrega2.json",
  "status": "GRADED",
  "criteria": [
    {
      "criterion": "Gráfico con nombres de producto",
      "weight": 20,
      "verdict": "Meets Expectations",
      "evidence": [
        {"source": "frame", "mmss": "01:05", "t": 65.25, "frame": "frames/t0065.250.jpg",
         "observation": "Bar chart axis shows product names (Laptop, Mouse…), no codes."}
      ],
      "review_required": [],
      "note": ""
    },
    {
      "criterion": "Declaración de uso de IA",
      "weight": 10,
      "verdict": "REVIEW_REQUIRED",
      "evidence": [],
      "review_required": [
        {"from": "03:40", "to": "03:50", "reason": "fast scroll between frames; text unreadable"}
      ],
      "note": "Not in YouTube description; may appear on screen during the scroll."
    }
  ],
  "penalties": [
    {"criterion": "Duración ≤ 5 min", "penalty": "-10", "verdict": "not_met",
     "evidence": [{"source": "metadata", "observation": "duration_s = 412.3 (06:52)"}],
     "review_required": [], "note": "06:52 > 05:00"}
  ]
}
```

- Criterion `verdict` ∈ `Meets Expectations` | `Partially Meets` | `Does Not Meet` |
  `REVIEW_REQUIRED` (exactly the assignment-evaluator labels, plus the review flag).
- Penalty `verdict` ∈ `met` | `partial` | `not_met` | `REVIEW_REQUIRED`.
- `evidence[].source` ∈ `frame` | `transcript` | `metadata`; transcript items carry `quote`.
- A `REVIEW_REQUIRED` verdict must carry at least one `review_required` window.
