# evaluation-rubrics

| Skill | Purpose |
|---|---|
| `rubric-creator` | Build an analytic rubric (JSON → xlsx), with an optional penalties block |
| `assignment-evaluator` | Score one submission (document or video) against a rubric; append a row to the grades file |
| `build-grades` | Rebuild the grades xlsx from the saved row JSONs |
| `video-evidence` | Turn a video (YouTube URL or local file) into an auditable evidence pack and grade it against the rubric |

Python scripts need `openpyxl` (`pip install openpyxl`).

## Video dependencies

`video-evidence` shells out to free CLI tools:

| Tool | Used for |
|---|---|
| `yt-dlp` | download (≤ 1080p) + YouTube title/description metadata |
| `ffmpeg` / `ffprobe` | exact duration, frame extraction (scene changes + interval), contact sheet |
| `mlx_whisper` (Apple Silicon) · `whisper` (openai-whisper) · `faster-whisper` | timestamped transcript |

Install / verify (idempotent; never uses sudo — on Linux it prints the commands for you to run):

```bash
# locate the installed copy (config dir may be ~/.claude or $CLAUDE_CONFIG_DIR)
SETUP=$(find "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins" -path '*evaluation-rubrics*/video-evidence/scripts/setup-video-deps.sh' | sort | tail -1)
bash "$SETUP"            # install what's missing
bash "$SETUP" --check    # report only
```

Or just ask Claude to grade a video: the preflight prints the absolute path of the setup script.

Equivalent manual install:

- macOS arm64: `brew install ffmpeg yt-dlp pipx && pipx install --python python3.14 mlx-whisper`
- macOS x86_64: `brew install ffmpeg yt-dlp pipx && pipx install openai-whisper`
- Debian/Ubuntu: `sudo apt-get install -y ffmpeg pipx && pipx install yt-dlp && pipx install openai-whisper`

The skill runs `scripts/preflight.py` before every job and stops with the exact install command
if anything is missing, so a half-built evidence pack never happens.

**Why no SessionStart hook:** a hook would run on every session for every user of this plugin,
including the many who never grade video, adding latency and a recurring warning for a
dependency they may never need. The preflight gives the same guarantee at the only point it
matters — right before a video job — with zero ambient cost.

Privacy: downloaded videos go to the OS temp dir (outside synced folders) and are deleted once
the pack is built, unless `--keep-video`. Evidence packs (frames, transcript) go where the caller
says — they contain student content, so keep them out of public folders.
