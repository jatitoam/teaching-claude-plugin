---
description: Install the video-evidence dependencies (ffmpeg, yt-dlp, a Whisper CLI) after a dry-run preview.
argument-hint: "[--dry-run | --check]"
---

Install what the `video-evidence` skill needs to grade video submissions. Never use sudo.

Do this in order, and do not skip the dry run:

1. Preview, and show the user the full output:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/video-evidence/scripts/setup-video-deps.sh" --dry-run
   ```

2. If it ends with `SUMMARY: nothing to install`, report the versions it listed and stop.

3. If it exits non-zero (e.g. Homebrew missing) or the platform is not macOS, **stop** and relay
   the commands it printed verbatim for the user to run themselves. Do not improvise an
   installer or pick a package manager for them.

4. Otherwise list the `WOULD RUN:` lines in one short block and ask for explicit confirmation —
   this installs software on their machine. Do not proceed without a yes.

5. On yes, run it for real:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/video-evidence/scripts/setup-video-deps.sh"
   ```

6. Verify and report the tool versions from:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/video-evidence/scripts/preflight.py" --need-download
   ```

   If `ok` is false, show `missing` and `install_hint` instead of claiming success.

If the user passes `--dry-run`, `--check`, or any other argument to this command, forward it to
the script verbatim (and with `--dry-run`/`--check`, stop after showing the output).
