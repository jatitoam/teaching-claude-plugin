#!/usr/bin/env bash
# Install/verify video-evidence dependencies (ffmpeg, yt-dlp, a whisper transcriber).
#   macOS: installs missing pieces via Homebrew + pipx. Linux/other: prints commands only.
#   --check: report only, install nothing. Never uses sudo. Ends by running preflight.py.
set -u

CHECK=0
for a in "$@"; do
  case "$a" in
    --check) CHECK=1 ;;
    -h|--help) sed -n '2,4p' "$0"; exit 0 ;;
    *) echo "unknown arg: $a" >&2; exit 64 ;;
  esac
done

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OS="$(uname -s)"; ARCH="$(uname -m)"
ORIG_PATH="$PATH"
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"
echo "platform: $OS $ARCH"

have() { command -v "$1" >/dev/null 2>&1; }
report() {  # report <tool> [version-args...]
  local t="$1"; shift
  local v; v="$("$t" "${@:---version}" 2>&1 | head -1)"
  echo "ok $t $v"
}
have_transcriber() { have mlx_whisper || have whisper; }

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
    elif [ "$CHECK" = 1 ]; then
      echo "missing $pkg (would: brew install $pkg)"
    else
      brew install "$pkg" || echo "warning: brew install $pkg failed" >&2
    fi
  done
  if have_transcriber; then
    for t in mlx_whisper whisper; do have "$t" && echo "ok $t $(command -v "$t")"; done
  elif [ "$ARCH" = "arm64" ]; then
    PY=""
    for v in 3.14 3.13 3.12 3.11 3.10; do   # prefer newest supported (mlx wheels: 3.10-3.14)
      if have "python$v"; then PY="$(command -v "python$v")"; break; fi
    done
    if [ "$CHECK" = 1 ]; then
      echo "missing transcriber (would: pipx install --python ${PY:-<brew python@3.12>} mlx-whisper)"
    else
      if [ -z "$PY" ]; then
        brew install python@3.12 && PY="$(brew --prefix python@3.12)/bin/python3.12"
      fi
      pipx install --python "$PY" mlx-whisper || echo "warning: mlx-whisper install failed" >&2
    fi
  else
    if [ "$CHECK" = 1 ]; then
      echo "missing transcriber (would: pipx install openai-whisper)"
    else
      pipx install openai-whisper || echo "warning: openai-whisper install failed" >&2
    fi
  fi
  case ":$ORIG_PATH:" in *":$HOME/.local/bin:"*) ;; *)
    echo "note: pipx installs CLIs into ~/.local/bin, which is not on your PATH." >&2
    echo "      The skill finds it anyway; for your shell, run: pipx ensurepath" >&2 ;;
  esac
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

Then re-run: bash "$DIR/setup-video-deps.sh" --check
MSG
python3 "$DIR/preflight.py" --need-download
rc=$?
[ "$CHECK" = 1 ] || true
exit $rc
