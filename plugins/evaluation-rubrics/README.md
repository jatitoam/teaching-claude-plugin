# evaluation-rubrics

| Skill | Purpose |
|---|---|
| `rubric-creator` | Build an analytic rubric (JSON → xlsx), with an optional penalties block |
| `assignment-evaluator` | Score one submission (document or video) against a rubric; append a row to the grades file |
| `build-grades` | Rebuild the grades xlsx from the saved row JSONs |
| `video-evidence` | Turn a video (YouTube URL or local file) into an auditable evidence pack — frames, transcript, index, and a per-criterion evidence map with watch links. Captures and selects evidence; never grades |

| Command | Purpose |
|---|---|
| `/evaluation-rubrics:install-video-deps` | Preview (`--dry-run`), confirm, install, and verify the video dependencies |

## Video grading pipeline

| Stage | Who | Output |
|---|---|---|
| Capture | script (no model) | metadata, de-duplicated frames, contact sheets, transcript |
| Index | Haiku, ≤ 24 frames per agent (1280-px copies; skipped below the break-even) | `frames-index.json` (describes, never judges) |
| Select | Sonnet, one per video | `evidence-map.json` (candidate windows per criterion, no verdicts) |
| Judge | `assignment-evaluator` (lead / delegated Sonnet) | `verdicts.json`, `review.md` (REVIEW_REQUIRED first, `youtu.be/…?t=` links), grades row |

Python scripts need `openpyxl` (`pip install openpyxl`).

## Video dependencies

`video-evidence` shells out to free CLI tools:

| Tool | Used for |
|---|---|
| `yt-dlp` | download (≤ 1080p) + YouTube title/description metadata |
| `ffmpeg` / `ffprobe` | exact duration, frame extraction (scene changes + interval), contact sheet |
| `mlx_whisper` (Apple Silicon) · `whisper` (openai-whisper) · `faster-whisper` | timestamped transcript |

Install / verify — in Claude Code:

```
/evaluation-rubrics:install-video-deps            # dry-run preview → asks → installs → verifies
/evaluation-rubrics:install-video-deps --dry-run  # preview only
```

The command wraps `skills/video-evidence/scripts/setup-video-deps.sh` (`--dry-run` prints the
exact `WOULD RUN:` commands and changes nothing). It never uses sudo or edits shell rc files; on
Linux it only prints the commands for you to run.

Equivalent manual install:

- macOS arm64: `brew install ffmpeg yt-dlp pipx && pipx install --python python3.14 mlx-whisper`
- macOS x86_64: `brew install ffmpeg yt-dlp pipx && pipx install openai-whisper`
- Debian/Ubuntu: `sudo apt-get install -y ffmpeg pipx && pipx install yt-dlp && pipx install openai-whisper`

**How missing dependencies are flagged** (mirrors code-general's install pattern):

- **SessionStart hook** (`hooks/video-deps-notice.sh`): `command -v` lookups only (~4 ms, no
  Python, no brew). **Silent** when everything is present. When something is missing it prints one
  line pointing at `/evaluation-rubrics:install-video-deps`, **at most once per plugin version**
  (stamp in `~/.cache/evaluation-rubrics/video-deps-notified-<version>`). It never installs and
  never fails the session. This keeps the per-session cost at effectively zero — the reason v1.4.0
  shipped without a hook — while still telling new installs what they need.
- **Preflight at point of use** (`scripts/preflight.py`) remains the backstop: every video job
  checks binaries first and stops with the exact install command, so a half-built pack never
  happens.

Privacy: downloaded videos go to the OS temp dir (outside synced folders) and are deleted once
the pack is built, unless `--keep-video`. Evidence packs (frames, transcript) go where the caller
says — they contain student content, so keep them out of public folders.
