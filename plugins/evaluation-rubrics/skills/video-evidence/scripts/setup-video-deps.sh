#!/usr/bin/env bash
# Install/verify video-evidence dependencies (ffmpeg, yt-dlp, a whisper transcriber).
#   macOS: installs missing pieces via Homebrew + pipx. Linux/other: prints commands only.
#   --dry-run: change nothing. Prints `ok <tool> <version>` for present tools and one
#              `WOULD RUN: <command>` line per install step, then `SUMMARY: ...`. Exit 0
#              (exit 1 only if Homebrew itself is missing on macOS).
#   --check:   alias of --dry-run (identical output and semantics).
#   -h|--help: this text.   Never uses sudo. A real install ends by running preflight.py.
#   Env (testing): VIDEO_DEPS_NO_PATH_PREPEND=1 skips prepending brew/local bin dirs to PATH,
#                  so a restricted PATH can simulate missing tools.
set -u

DRY=0
for a in "$@"; do
  case "$a" in
    --dry-run|--check) DRY=1 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown arg: $a (try --dry-run, --check, -h)" >&2; exit 64 ;;
  esac
done

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OS="$(uname -s)"; ARCH="$(uname -m)"
# Do not let `brew install` run its automatic cleanup of unrelated caches as a side effect.
export HOMEBREW_NO_INSTALL_CLEANUP=1
ORIG_PATH="$PATH"
if [ "${VIDEO_DEPS_NO_PATH_PREPEND:-0}" != 1 ]; then
  export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"
fi
echo "platform: $OS $ARCH"

have() { command -v "$1" >/dev/null 2>&1; }
report() {  # report <tool> [version-args...]
  local t="$1"; shift
  local v; v="$("$t" "${@:---version}" 2>&1 | head -1)"
  echo "ok $t $v"
}
have_transcriber() { have mlx_whisper || have whisper; }

STEPS=0
plan() {  # plan <command line>: dry-run prints it, real mode executes it (returns its status)
  if [ "$DRY" = 1 ]; then
    echo "WOULD RUN: $*"; STEPS=$((STEPS + 1)); return 0
  fi
  "$@"
}
summary() {
  if [ "$STEPS" = 0 ]; then echo "SUMMARY: nothing to install"
  else echo "SUMMARY: $STEPS step(s) would run"; fi
}

run_preflight() {
  python3 "$DIR/preflight.py" --need-download
  exit $?
}

if [ "$OS" = "Darwin" ]; then
  if ! have brew; then
    echo "Homebrew is required but not installed. Install it yourself with:" >&2
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"' >&2
    exit 1
  fi
  for pkg in ffmpeg yt-dlp pipx; do
    if have "$pkg"; then
      report "$pkg" "$([ "$pkg" = ffmpeg ] && echo -version || echo --version)"
    else
      plan brew install "$pkg" || echo "warning: brew install $pkg failed" >&2
    fi
  done
  if have_transcriber; then
    for t in mlx_whisper whisper; do have "$t" && echo "ok $t $(command -v "$t")"; done
  elif [ "$ARCH" = "arm64" ]; then
    PY=""
    for v in 3.14 3.13 3.12 3.11 3.10; do   # prefer newest supported (mlx wheels: 3.10-3.14)
      if have "python$v"; then PY="$(command -v "python$v")"; break; fi
    done
    if [ -z "$PY" ]; then
      plan brew install python@3.12 || echo "warning: brew install python@3.12 failed" >&2
      PY="$(brew --prefix python@3.12)/bin/python3.12"
    fi
    plan pipx install --python "$PY" mlx-whisper || echo "warning: mlx-whisper install failed" >&2
  else
    plan pipx install openai-whisper || echo "warning: openai-whisper install failed" >&2
  fi
  case ":$ORIG_PATH:" in *":$HOME/.local/bin:"*) ;; *)
    echo "note: pipx installs CLIs into ~/.local/bin, which is not on your PATH." >&2
    echo "      The skill finds it anyway; for your shell, run: pipx ensurepath" >&2 ;;
  esac
  if [ "$DRY" = 1 ]; then summary; exit 0; fi
  run_preflight
fi

# Linux / other: report, print commands, never install.
for t in ffmpeg yt-dlp pipx; do
  if have "$t"; then report "$t" "$([ "$t" = ffmpeg ] && echo -version || echo --version)"; fi
done
have_transcriber && echo "ok transcriber $(command -v mlx_whisper || command -v whisper)"
cat <<MSG

Automatic install is only supported on macOS. On this system ($OS $ARCH), run these yourself
(Debian/Ubuntu shown; adapt for your package manager):

  sudo apt-get install -y ffmpeg pipx
  pipx ensurepath
  pipx install yt-dlp
  pipx install openai-whisper    # provides the 'whisper' CLI (faster-whisper has no CLI of its own)

Then re-run: bash "$DIR/setup-video-deps.sh" --dry-run
MSG
if [ "$DRY" = 1 ]; then exit 0; fi
python3 "$DIR/preflight.py" --need-download
exit $?
