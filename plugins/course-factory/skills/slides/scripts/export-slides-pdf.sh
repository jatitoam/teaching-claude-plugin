#!/usr/bin/env bash
#
# export-slides-pdf.sh — Renders an HTML slide deck to a shareable PDF with no
# speaker notes. FINAL step of the `slides` skill, after the conductor approves
# the HTML (see SKILL.md §"Export to PDF"). Ported from the TIC 2026-II harness
# (its decision D50), adapted to the ET layout.
#
# ── Why PNG and not vector PDF (TIC D50) ──────────────────────────────────────
# The first version used Chrome `--print-to-pdf` (vector PDF). It looked fine in
# poppler, but Chrome encodes `box-shadow`/`filter` as TRANSPARENCY MASKS that
# **Quartz** viewers (Apple Preview, Quick Look, the Google Drive preview, Orca)
# paint as **gray rectangles** behind the elements. Robust, viewer-independent
# fix: rasterize each slide to PNG (identical to the browser) and assemble the
# PNGs into the PDF. Everything is "flattened": any viewer shows EXACTLY what
# was approved. Cost: no selectable text and a heavier file — acceptable for
# slides that are projected/shared.
#
# ── Why render IN-PLACE and not copy to a temp dir ────────────────────────────
# Chrome hangs on `file://` paths containing spaces (the project lives in
# Google Drive: ".../My Drive/..."). The v1 dodged that by copying the deck to a
# space-free temp dir, BUT that broke any asset referenced OUTSIDE the deck
# folder (e.g. `../shared-logo.png`). Here we render from the real location
# with the path percent-encoded (spaces → %20), so ALL relative assets resolve.
# Speaker notes never appear: they are hidden (`display:none`) in each slide.
#
# Usage:
#   export-slides-pdf.sh <deck-dir> <output-pdf-path> [scale]
#   [scale] = resolution factor (default 2 → 2560×1440 px per slide).
#
# Example (ET, one deck per session):
#   export-slides-pdf.sh slides/S02-build \
#     "slides/S02 - From Idea to Spec.pdf"
#
# Requirements (already present on the conductor's Mac):
#   - Google Chrome (headless → one PNG per slide)
#   - Python 3 with Pillow (PIL) to assemble the PNGs into a PDF
#
set -euo pipefail

DECK_DIR="${1:-}"
OUT_PDF="${2:-}"
SCALE="${3:-2}"

if [[ -z "$DECK_DIR" || -z "$OUT_PDF" ]]; then
  echo "Usage: $(basename "$0") <deck-dir> <output-pdf-path> [scale]" >&2
  exit 64
fi

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[[ -x "$CHROME" ]] || { echo "ERROR: Google Chrome not found at '$CHROME'." >&2; exit 69; }
python3 -c "import PIL" 2>/dev/null || { echo "ERROR: Pillow missing (pip3 install --user Pillow)." >&2; exit 69; }
[[ -d "$DECK_DIR" ]] || { echo "ERROR: directory '$DECK_DIR' does not exist." >&2; exit 66; }

DECK_ABS="$(cd "$DECK_DIR" && pwd)"
shopt -s nullglob
SLIDES=("$DECK_ABS"/slide-*.html)   # the glob preserves spaces and sorts lexicographically
shopt -u nullglob
[[ ${#SLIDES[@]} -gt 0 ]] || { echo "ERROR: no 'slide-*.html' in '$DECK_DIR'." >&2; exit 66; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/slides-pdf.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# Render each slide IN PLACE (so relative assets keep working) to a 2× PNG.
# Percent-encode the absolute path (spaces → %20; keep '/' and '@' literal,
# Chrome accepts them) so `file://` doesn't hang on the Google Drive path.
for f in "${SLIDES[@]}"; do
  base="$(basename "$f" .html)"
  url="file://$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe='/@'))" "$f")"
  "$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --force-device-scale-factor="$SCALE" --window-size=1280,720 \
    --screenshot="$WORK/$base.png" "$url" >/dev/null 2>&1
  [[ -s "$WORK/$base.png" ]] || { echo "ERROR: no PNG generated for $base." >&2; exit 70; }
done

mkdir -p "$(dirname "$OUT_PDF")"

# Assemble the PNGs into a single PDF. DPI = 96×scale → every page measures
# 960×540 pt (13.333×7.5 in = exact 16:9), regardless of the scale used.
python3 - "$WORK" "$OUT_PDF" "$SCALE" <<'PY'
import sys, glob, os
from PIL import Image
work, out, scale = sys.argv[1], sys.argv[2], int(sys.argv[3])
files = sorted(glob.glob(os.path.join(work, 'slide-*.png')))
imgs = [Image.open(f).convert('RGB') for f in files]
dpi = 96 * scale
imgs[0].save(out, 'PDF', resolution=dpi, save_all=True, append_images=imgs[1:])
print(f"OK · {len(imgs)} slides → {out}")
PY
