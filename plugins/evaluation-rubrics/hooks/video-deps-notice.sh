#!/usr/bin/env bash
# SessionStart hook: one-line notice when video-evidence dependencies are missing.
# Silent when everything is present. Only `command -v` lookups (milliseconds; no Python,
# no brew). Notifies at most once per plugin version via a stamp file outside the plugin
# dir. Never installs anything; never fails the session.
set -u

# Hooks can run with a minimal PATH; include the usual Homebrew and pipx bin dirs.
# VIDEO_DEPS_NO_PATH_PREPEND=1 skips this (testing: simulate missing tools).
[ -n "${VIDEO_DEPS_NO_PATH_PREPEND:-}" ] \
  || PATH="${PATH:-/usr/bin:/bin}:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin"

missing=""
for t in ffmpeg ffprobe yt-dlp; do
  command -v "$t" >/dev/null 2>&1 || missing="$missing $t"
done
command -v mlx_whisper >/dev/null 2>&1 || command -v whisper >/dev/null 2>&1 \
  || missing="$missing whisper"
[ -z "$missing" ] && exit 0

root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
version="$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
  "$root/.claude-plugin/plugin.json" 2>/dev/null | head -1)"
stamp_dir="${XDG_CACHE_HOME:-$HOME/.cache}/evaluation-rubrics"
stamp="$stamp_dir/video-deps-notified-${version:-unknown}"
[ -e "$stamp" ] && exit 0
mkdir -p "$stamp_dir" 2>/dev/null && : > "$stamp" 2>/dev/null

echo "evaluation-rubrics: video grading deps missing (${missing# }) — run /evaluation-rubrics:install-video-deps when you need to grade videos."
exit 0
