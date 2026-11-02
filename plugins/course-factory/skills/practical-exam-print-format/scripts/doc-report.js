// course-factory · practical-exam-print-format · doc-report.js
// Paste into `javascript_tool` in the tab of a Google Doc — the BASE (expected values) or the TARGET
// (actual values); both give the same JSON shape, so compare them field by field. Safe to run several
// times in the same tab (`var`, no top-level `const`).
// The tool truncates long results: read the rest from the global `report` with a second short call.
// Verified live 2026-11-02 (base: header rgb(24, 54, 178); a formatted Doc: fingerprint = its source).
// Read-only: fetches the Doc's own export (txt + html) and renders the html in an off-screen iframe
// via a Blob URL (the Docs page enforces TrustedHTML, so innerHTML is refused). px → pt = × 0.75.
// Paragraph spacing is exported as PADDING (margins are always 0): `spacing` = "top/bottom" padding.
// LIMITS: the export does NOT show the space after the Title (reads 0px even when the editor has it)
// nor a blank last page — check both visually (SKILL.md §Orchestrator verification).
var base = location.pathname.replace(/\/edit.*/, '');
var txt = await (await fetch(base + '/export?format=txt')).text();
var words = (txt.normalize('NFC').match(/[\p{L}\p{N}]+/gu) || [])
  .filter(w => !['http', 'https'].includes(w.toLowerCase()));
var dig = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(words.join(' ')));
var fingerprint = { n: words.length,
  sha: [...new Uint8Array(dig)].map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 16) };
var html = await (await fetch(base + '/export?format=html')).text();
var f = document.createElement('iframe');
f.style.cssText = 'position:fixed;left:-9999px;width:900px;height:900px';
f.src = URL.createObjectURL(new Blob([html], { type: 'text/html' }));
document.body.appendChild(f);
await new Promise(r => (f.onload = r));
var d = f.contentDocument, cs = e => f.contentWindow.getComputedStyle(e), sp = e => e.querySelector('span') || e;
var pt = px => Math.round(parseFloat(px) * 0.75 * 10) / 10;
var spacing = p => cs(p).paddingTop + '/' + cs(p).paddingBottom;
// Compare pt, font, weight, color, band, align between BASE and TARGET; `text` differs by design.
var style = p => p && { text: p.innerText.trim().slice(0, 40), pt: pt(cs(sp(p)).fontSize),
  font: cs(sp(p)).fontFamily, weight: cs(sp(p)).fontWeight, color: cs(sp(p)).color,
  band: cs(p).backgroundColor, align: cs(p).textAlign, spacing: spacing(p) };
// Address = host[/path]. With a path (or a scheme, or www.), any host.tld counts — github.com/a/x.py too.
// A bare host (no path) counts only with a TLD of 2–4 letters that is not a file extension, so
// main.py / data.json / app.config are not addresses. Known gap: a bare host on a long TLD (x.studio).
var FILE_EXT = /^(py|js|ts|json|html?|md|txt|csv|xlsx?|docx?|pdf|png|jpe?g|gif|svg|zip|yaml|yml|sql|sh|css)$/i;
var isUrl = s => { var m = s.match(/^(https?:\/\/)?((?:[\w-]+\.)+([a-z]{2,}))(\/\S*)?$/i); if (!m) return false;
  if (m[1] || m[4] || /^www\./i.test(m[2])) return true; return m[3].length <= 4 && !FILE_EXT.test(m[3]); };
var sig = s => [pt(cs(s).fontSize), cs(s).fontWeight, cs(s).color, cs(s).textDecorationLine].join('|');
// Lines 1 and 2 are the title and subtitle whether or not their styles were applied yet.
var nonEmpty = [...d.body.querySelectorAll('p, h1, h2, h3, li')].filter(p => !p.closest('table') && p.innerText.trim());
var report = {
  fingerprint,
  schemes: (txt.match(/https?:\/\//g) || []).length,
  comments: (html.match(/cmnt_ref/gi) || []).length,
  links: [...d.querySelectorAll('a[href]')].map(a => ({ text: a.innerText.trim().slice(0, 40), inTable: !!a.closest('table') })),
  title: style(nonEmpty[0]),
  subtitle: style(nonEmpty[1]),
  h1: style(d.querySelector('h1')),
  body: style(nonEmpty.slice(2).find(p => p.tagName === 'P' && !isUrl(p.innerText.trim()))),
  // Every body paragraph (outside tables, not title/subtitle/headings/addresses): distinct "pt|spacing".
  bodyStyles: [...new Set(nonEmpty.slice(2).filter(p => p.tagName === 'P' && !isUrl(p.innerText.trim()))
    .map(p => pt(cs(sp(p)).fontSize) + '|' + spacing(p)))],
  urls: nonEmpty.filter(p => isUrl(p.innerText.trim())).map(p => ({
    text: p.innerText.trim(), tag: p.tagName, align: cs(p).textAlign, pt: pt(cs(sp(p)).fontSize),
    weight: cs(sp(p)).fontWeight, color: cs(sp(p)).color, deco: cs(sp(p)).textDecorationLine,
    spanStyles: new Set([...p.querySelectorAll('span')].map(sig)).size })),
  tables: [...d.querySelectorAll('table')].map((t, i) => { var r0 = t.rows[0], c = r0.cells[0]; return {
    index: i, header: [...r0.cells].map(x => x.innerText.trim().slice(0, 20)), rows: t.rows.length,
    headerBg: [...new Set([...r0.cells].map(x => cs(x).backgroundColor))],
    headerText: cs(sp(c)).color, headerWeight: cs(sp(c)).fontWeight,
    pt: [...new Set([...t.querySelectorAll('span')].map(s => pt(cs(s).fontSize)))],
    spacing: [...new Set([...t.querySelectorAll('p')].map(spacing))],
    widthsPx: [...r0.cells].map(x => Math.round(parseFloat(cs(x).width))) }; }),
};
f.remove();
JSON.stringify(report);
// EXPECTED on a formatted TARGET: links [] · schemes 0 · comments 0 · fingerprint = text-fingerprint.py
// of SOURCE_MD · title/subtitle/h1 = BASE's on pt, font, weight, color, band, align · every url: align
// center, pt = url_pt, weight 700, color rgb(0, 0, 0), deco none, spanStyles 1 · every table: headerBg
// = [BASE rubric headerBg], headerText rgb(255, 255, 255), headerWeight 700, spacing ["0px/0px"], pt
// [rubric_table_pt] for rubric/penalty tables and [table_pt] for the others · body and bodyStyles =
// BEFORE's (same set: table formatting did not leak into any body paragraph).
