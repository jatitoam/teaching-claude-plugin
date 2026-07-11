#!/usr/bin/env python3
"""Generate index.html + presenter.html for a slide build folder.

Usage: python3 build-presenter.py <build-dir> <session-label> ["<deck title>"]
  e.g.: python3 build-presenter.py slides/S01-build S01 "S01 — AI Foundations and the New Builder Mindset"

Ported from the TIC harness (D44) presenter pattern. Key gotchas baked in:
- file:// windows can be DISTINCT origins: all index<->presenter sync uses postMessage
  (never window.opener variable/DOM reads), and speaker notes are baked into
  presenter.html as a static JS NOTES array extracted from each slide's hidden
  <div class="speaker-notes"> at build time (never read via iframe.contentDocument).
- iframes carry pointer-events:none (a stray click steals keyboard focus and
  breaks arrow navigation).
- The presenter current-slide iframe needs flex:0 0 auto — as a flex child its
  1280px width otherwise gets flex-shrunk, clipping the slide before the
  transform scale is applied.
- Fullscreen hides the index bottom bar (body.is-fullscreen class on
  fullscreenchange) and the stage rescale stops subtracting the bar height.
- The 🎤 Presenter view button opens the popup AND auto-triggers fullscreen.
- The popup window name is unique per deck (presenter-<label>) so two decks
  open at once don't collide.
- The clock is real system time (HH:MM:SS), not an elapsed timer, so it compares
  directly against the time ranges stamped in the speaker-note headers.

Rerun this script whenever any slide's speaker notes change (NOTES are baked).
"""
import re, sys, json, html as htmlmod
from pathlib import Path

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:100%; height:100%; background:#000; overflow:hidden;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
  #stage { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; }
  #frame-wrap { width:1280px; height:720px; transform-origin:center center; overflow:hidden; background:#0D0D0D; }
  iframe { width:1280px; height:720px; border:0; display:block; pointer-events:none; }
  #bar {
    position:absolute; bottom:0; left:0; right:0; height:56px;
    display:flex; align-items:center; justify-content:center; gap:18px;
    background:rgba(13,13,13,0.92); border-top:1px solid #2a2a2a;
    color:#bbb; font-size:15px; z-index:10; user-select:none;
  }
  body.is-fullscreen #bar { display:none; }
  button {
    background:#E76A28; color:#fff; border:none; border-radius:6px;
    padding:8px 16px; font-size:15px; cursor:pointer; font-weight:600;
  }
  button:disabled { opacity:0.35; cursor:default; }
  button.ghost { background:rgba(255,255,255,0.14); }
  #counter { min-width:80px; text-align:center; letter-spacing:0.5px; }
</style>
</head>
<body>
<div id="stage"><div id="frame-wrap"><iframe id="slide-frame" src="slide-01.html"></iframe></div></div>
<div id="bar">
  <button id="prev">◀ Prev</button>
  <span id="counter">1 / __TOTAL__</span>
  <button id="next">Next ▶</button>
  <button id="fs" class="ghost">⛶ Fullscreen</button>
  <button id="presenter-view" class="ghost">🎤 Presenter view</button>
</div>
<script>
  var TOTAL = __TOTAL__;
  var current = 1;
  var frame = document.getElementById('slide-frame');
  var counter = document.getElementById('counter');
  var prevBtn = document.getElementById('prev');
  var nextBtn = document.getElementById('next');
  var presenterWin = null;

  function pad(n) { return n < 10 ? '0' + n : '' + n; }

  function broadcastState() {
    if (presenterWin && !presenterWin.closed) {
      presenterWin.postMessage({ source: 'et-slides', type: 'state', current: current, total: TOTAL }, '*');
    }
  }

  function render() {
    frame.src = 'slide-' + pad(current) + '.html';
    counter.textContent = current + ' / ' + TOTAL;
    prevBtn.disabled = current <= 1;
    nextBtn.disabled = current >= TOTAL;
    fitStage();
    broadcastState();
  }

  function goTo(n) {
    if (n < 1 || n > TOTAL) return;
    current = n;
    render();
  }

  function fitStage() {
    var wrap = document.getElementById('frame-wrap');
    var barH = document.body.classList.contains('is-fullscreen') ? 0 : 56;
    var scale = Math.min(window.innerWidth / 1280, (window.innerHeight - barH) / 720);
    wrap.style.transform = 'scale(' + scale + ')';
  }

  prevBtn.addEventListener('click', function () { goTo(current - 1); });
  nextBtn.addEventListener('click', function () { goTo(current + 1); });

  function enterFullscreen() {
    var el = document.documentElement;
    if (!document.fullscreenElement && el.requestFullscreen) { el.requestFullscreen(); }
  }

  document.getElementById('fs').addEventListener('click', function () {
    if (document.fullscreenElement) { document.exitFullscreen(); }
    else { enterFullscreen(); }
  });
  document.addEventListener('fullscreenchange', function () {
    document.body.classList.toggle('is-fullscreen', !!document.fullscreenElement);
    fitStage();
  });
  window.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); goTo(current + 1); }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); goTo(current - 1); }
    if (e.key === 'Home') { goTo(1); }
    if (e.key === 'End') { goTo(TOTAL); }
    if (e.key === 'f' || e.key === 'F') { document.getElementById('fs').click(); }
  });
  window.addEventListener('resize', fitStage);

  window.addEventListener('message', function (e) {
    if (!e.data || e.data.source !== 'et-slides') return;
    if (e.data.type === 'nav') {
      if (e.data.direction === 'next') { goTo(current + 1); }
      if (e.data.direction === 'prev') { goTo(current - 1); }
    }
    if (e.data.type === 'request-state') { broadcastState(); }
  });

  document.getElementById('presenter-view').addEventListener('click', function () {
    presenterWin = window.open('presenter.html', 'presenter-__LABEL__', 'width=1200,height=750,resizable=yes');
    enterFullscreen();
  });

  render();
</script>
</body>
</html>
"""

PRESENTER_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Presenter view — __LABEL__</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:100%; height:100%; background:#111; color:#fff;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; overflow:hidden; }
  #top { position:absolute; top:0; left:0; right:0; bottom:56px; display:flex; }
  #current { flex:3; background:#000; position:relative; overflow:hidden; display:flex; align-items:center; justify-content:center; }
  #current iframe { width:1280px; height:720px; border:0; transform-origin:center center; pointer-events:none; flex:0 0 auto; }
  #side { flex:2; min-width:320px; max-width:480px; display:flex; flex-direction:column; border-left:2px solid #262626; }
  #next-wrap { padding:10px; border-bottom:2px solid #262626; }
  #next-label { font-size:12px; color:#999; margin-bottom:6px; text-transform:uppercase; letter-spacing:1px; }
  #next-frame-wrap { width:100%; aspect-ratio:16/9; background:#000; overflow:hidden; position:relative; border-radius:4px; }
  #next-frame-wrap iframe { width:1280px; height:720px; border:0; transform-origin:top left; pointer-events:none; }
  #notes { flex:1; padding:16px; overflow-y:auto; font-size:19px; line-height:1.5; white-space:pre-wrap; }
  #bottom {
    position:absolute; bottom:0; left:0; right:0; height:56px;
    display:flex; align-items:center; justify-content:space-between; gap:18px; padding:0 16px;
    background:rgba(13,13,13,0.95); border-top:2px solid #262626; font-size:16px;
  }
  #bottom .group { display:flex; align-items:center; gap:12px; }
  button { background:#E76A28; color:#fff; border:none; border-radius:6px;
    padding:8px 16px; font-size:15px; cursor:pointer; font-weight:600; }
  #clock { font-variant-numeric:tabular-nums; min-width:100px; text-align:center; font-size:20px; font-weight:600; }
  #counter { min-width:80px; text-align:center; letter-spacing:0.5px; }
  #warn { padding:40px; font-size:20px; }
  #status { font-size:12px; color:#f66; margin-left:8px; }
</style>
</head>
<body>
<div id="warn" style="display:none">Open this window from the "🎤 Presenter view" button in the main presentation (it does not work opened on its own).</div>
<div id="app">
  <div id="top">
    <div id="current"><iframe id="cur-frame"></iframe></div>
    <div id="side">
      <div id="next-wrap">
        <div id="next-label">Next</div>
        <div id="next-frame-wrap"><iframe id="next-frame"></iframe></div>
      </div>
      <div id="notes">Waiting for the main presentation…</div>
    </div>
  </div>
  <div id="bottom">
    <div class="group">
      <button id="prev">◀ Prev</button>
      <span id="counter">– / __TOTAL__</span>
      <button id="next">Next ▶</button>
      <span id="status"></span>
    </div>
    <div id="clock">--:--:--</div>
  </div>
</div>
<script>
  var NOTES = __NOTES__;
  var TOTAL = __TOTAL__;
  var opener_ = window.opener;

  if (!opener_ || opener_.closed) {
    document.getElementById('warn').style.display = 'block';
    document.getElementById('app').style.display = 'none';
  } else {
    var curFrame = document.getElementById('cur-frame');
    var nextFrame = document.getElementById('next-frame');
    var notesEl = document.getElementById('notes');
    var counterEl = document.getElementById('counter');
    var statusEl = document.getElementById('status');
    var lastShown = -1;
    var gotState = false;

    function pad(n) { return n < 10 ? '0' + n : '' + n; }

    function fitCur() {
      var wrap = document.getElementById('current');
      var scale = Math.min(wrap.clientWidth / 1280, wrap.clientHeight / 720);
      curFrame.style.transform = 'scale(' + scale + ')';
    }
    function fitNext() {
      var wrap = document.getElementById('next-frame-wrap');
      var scale = wrap.clientWidth / 1280;
      nextFrame.style.transform = 'scale(' + scale + ')';
    }

    function showSlide(cur) {
      if (cur === lastShown) return;
      lastShown = cur;
      curFrame.src = 'slide-' + pad(cur) + '.html';
      nextFrame.src = (cur < TOTAL) ? ('slide-' + pad(cur + 1) + '.html') : 'about:blank';
      counterEl.textContent = cur + ' / ' + TOTAL;
      notesEl.textContent = NOTES[cur - 1] || '(no notes for this slide)';
      fitCur(); fitNext();
    }

    // The opener pushes state via postMessage (works even though each
    // file:// document can be a distinct origin — unlike reading the
    // other window's variables/DOM directly).
    window.addEventListener('message', function (e) {
      if (!e.data || e.data.source !== 'et-slides') return;
      if (e.data.type === 'state') {
        gotState = true;
        statusEl.textContent = '';
        showSlide(e.data.current);
      }
    });

    function requestState() {
      if (!opener_ || opener_.closed) return;
      opener_.postMessage({ source: 'et-slides', type: 'request-state' }, '*');
    }

    document.getElementById('prev').addEventListener('click', function () {
      if (opener_ && !opener_.closed) opener_.postMessage({ source: 'et-slides', type: 'nav', direction: 'prev' }, '*');
    });
    document.getElementById('next').addEventListener('click', function () {
      if (opener_ && !opener_.closed) opener_.postMessage({ source: 'et-slides', type: 'nav', direction: 'next' }, '*');
    });
    window.addEventListener('keydown', function (e) {
      if (!opener_ || opener_.closed) return;
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { opener_.postMessage({ source: 'et-slides', type: 'nav', direction: 'next' }, '*'); }
      if (e.key === 'ArrowLeft' || e.key === 'PageUp') { opener_.postMessage({ source: 'et-slides', type: 'nav', direction: 'prev' }, '*'); }
    });
    window.addEventListener('resize', function () { fitCur(); fitNext(); });

    requestState();

    function updateClock() {
      var now = new Date();
      document.getElementById('clock').textContent =
        pad(now.getHours()) + ':' + pad(now.getMinutes()) + ':' + pad(now.getSeconds());
    }

    setInterval(function () {
      updateClock();
      if (!opener_ || opener_.closed) return;
      if (!gotState) { statusEl.textContent = 'syncing…'; requestState(); }
    }, 400);
    updateClock();

    fitCur(); fitNext();
  }
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    build_dir = Path(sys.argv[1])
    label = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else label

    slides = sorted(build_dir.glob("slide-*.html"))
    total = len(slides)
    if total == 0:
        sys.exit(f"no slide-*.html files in {build_dir}")

    notes = []
    for f in slides:
        h = f.read_text()
        m = re.search(r'<div class="speaker-notes"[^>]*>(.*?)</div>', h, re.S)
        txt = m.group(1) if m else ""
        txt = re.sub(r"<[^>]+>", "", txt)
        txt = htmlmod.unescape(txt).strip()
        notes.append(txt)
    missing = [i + 1 for i, n in enumerate(notes) if not n]
    if missing:
        print(f"WARNING: empty speaker notes on slides {missing}")

    index = (INDEX_TEMPLATE.replace("__TOTAL__", str(total))
             .replace("__LABEL__", label).replace("__TITLE__", title))
    presenter = (PRESENTER_TEMPLATE.replace("__TOTAL__", str(total))
                 .replace("__LABEL__", label)
                 .replace("__NOTES__", json.dumps(notes, ensure_ascii=False)))

    (build_dir / "index.html").write_text(index)
    (build_dir / "presenter.html").write_text(presenter)
    print(f"wrote {build_dir}/index.html + presenter.html ({total} slides, {len([n for n in notes if n])} notes)")


if __name__ == "__main__":
    main()
