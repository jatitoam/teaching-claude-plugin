#!/usr/bin/env node
/**
 * build_guide_html.js
 * Produces a Google Docs-compatible HTML scoring guide from answer_key.json.
 *
 * Usage:
 *   node build_guide_html.js \
 *     --input answer_key.json \
 *     --output scoring_guide.html \
 *     --section-header "PART I — Closed-Ended Questions" \
 *     --pts-per-question 4 \
 *     --total-pts 60 \
 *     --exam-title "Midterm Exam — Sessions 1-4"
 */

'use strict';
const fs = require('fs');

const args = process.argv.slice(2);
function getArg(flag) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : null;
}

const inputFile     = getArg('--input') || 'answer_key.json';
const outputFile    = getArg('--output') || 'scoring_guide.html';
const sectionHeader = getArg('--section-header') || 'PART I — Closed-Ended Questions';
const ptsPerQ       = parseInt(getArg('--pts-per-question') || '4', 10);
const totalPts      = parseInt(getArg('--total-pts') || '0', 10);
const examTitle     = getArg('--exam-title') || 'Exam';

const key       = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
const versions  = Object.keys(key).sort();
const nQ        = key[versions[0]]?.length || 0;
const computedTotal = totalPts || (ptsPerQ * nQ);

// ── HTML Escape ───────────────────────────────────────────────────────────────
function esc(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ── Styles ────────────────────────────────────────────────────────────────────
const FONTS_URL = 'https://themes.googleusercontent.com/fonts/css?kit=rfSAlb2JfKqknMZbyNv1qbd1z-QJxci6pgsJEDD--sK5C-2JrCr1ABsZF5AjRv96T';

const H2_STYLE = [
  'padding-top:0pt', 'margin:0', 'color:#1836b2',
  'border-bottom-color:#1836b2', 'padding-left:0',
  'font-size:16pt', 'padding-bottom:2pt', 'line-height:1.15',
  'page-break-after:avoid', 'border-bottom-width:1pt',
  'font-family:&quot;League Spartan&quot;', 'border-bottom-style:solid',
  'orphans:2', 'widows:2', 'text-align:left', 'padding-right:0'
].join(';');

const H2_SPAN = [
  'color:#1836b2', 'font-weight:400', 'text-decoration:none',
  'vertical-align:baseline', 'font-size:16pt',
  'font-family:&quot;League Spartan&quot;', 'font-style:normal'
].join(';');

const P_STYLE = [
  'padding-top:0pt', 'margin:0', 'color:#000000', 'padding-left:0',
  'font-size:11pt', 'padding-bottom:10pt',
  'font-family:&quot;Inter&quot;', 'line-height:1.15',
  'orphans:2', 'widows:2', 'text-align:left', 'padding-right:0'
].join(';');

const BODY_SPAN = [
  'color:#000000', 'font-weight:400', 'text-decoration:none',
  'vertical-align:baseline', 'font-size:10pt',
  'font-family:&quot;Inter&quot;', 'font-style:normal'
].join(';');

// ── Table builders ────────────────────────────────────────────────────────────
const TH_BASE  = `border:1pt solid #1836b2;padding:6pt 8pt;font-size:10pt;font-family:&quot;Inter&quot;;color:#ffffff;background-color:#1836b2;font-weight:700`;
const TD_N     = `border:1pt solid #cccccc;padding:6pt 8pt;font-size:10pt;font-family:&quot;Inter&quot;;color:#000000;text-align:center;width:28pt`;
const TD_LTR   = `border:1pt solid #cccccc;padding:6pt 8pt;font-size:11pt;font-family:&quot;Inter&quot;;color:#1836b2;font-weight:700;text-align:center;width:40pt`;
const TD_TEXT  = `border:1pt solid #cccccc;padding:6pt 8pt;font-size:10pt;font-family:&quot;Inter&quot;;color:#000000`;

function buildTable(letter) {
  const rows = key[letter].map(item =>
    `<tr>
      <td style="${TD_N}">${item.n}</td>
      <td style="${TD_LTR}">${item.letter}</td>
      <td style="${TD_TEXT}">${esc(item.correct_text)}</td>
    </tr>`
  ).join('\n');

  return `<table style="border-collapse:collapse;width:100%;margin-bottom:8pt">
  <tr>
    <th style="${TH_BASE};width:28pt">#</th>
    <th style="${TH_BASE};width:40pt">Answer</th>
    <th style="${TH_BASE}">Correct answer text</th>
  </tr>
  ${rows}
</table>`;
}

// ── Assemble sections ─────────────────────────────────────────────────────────
const versionSections = versions.map(v =>
  `<h2 style="${H2_STYLE}"><span style="${H2_SPAN}">Version ${v} — Answer Key</span></h2>\n` +
  buildTable(v)
).join('\n\n');

// ── Full document ─────────────────────────────────────────────────────────────
const html = `<html><head><meta content="text/html; charset=UTF-8" http-equiv="content-type">
<style type="text/css">
 @import url(${FONTS_URL});
</style></head>
<body class="doc-content" style="background-color:#ffffff;max-width:468pt;padding:72pt 72pt 72pt 72pt">

<h2 style="${H2_STYLE}"><span style="${H2_SPAN}">Scoring Guide — ${esc(examTitle)}</span></h2>

<p style="${P_STYLE}"><span style="${BODY_SPAN}">This document contains the answer keys for all ${versions.length} version(s) of the exam. The <strong>Answer</strong> column shows the letter (A–D) as it appears on the student's printed exam. The <strong>Correct answer text</strong> column shows the full text of the correct option for verification.</span></p>

<h2 style="${H2_STYLE}"><span style="${H2_SPAN}">Scoring Criteria</span></h2>

<p style="${P_STYLE}"><span style="${BODY_SPAN}"><strong>Points per correct answer:</strong> ${ptsPerQ} point${ptsPerQ !== 1 ? 's' : ''}. Maximum score: ${computedTotal}/${computedTotal}.<br>
<strong>Minimum passing score:</strong> at instructor's discretion.<br>
<strong>Blank or multiple marks:</strong> scored as incorrect.<br>
<strong>Partial credit:</strong> not awarded on multiple-choice questions.</span></p>

<h2 style="${H2_STYLE}"><span style="${H2_SPAN}">Notes for Graders</span></h2>

<p style="${P_STYLE}"><span style="${BODY_SPAN}">Mark answers as correct only when the student's mark exactly matches the option shown in this key. For inverted-definition questions (the question describes a concept; the student selects the term), the exact term is required — no credit for approximate answers. For questions with long answer options, the full text is shown in the <em>Correct answer text</em> column; options that begin similarly but differ in meaning are incorrect.</span></p>

${versionSections}

</body></html>`;

fs.writeFileSync(outputFile, html, 'utf8');
console.log(`Written: ${outputFile} (${versions.length} version(s), ${nQ} questions each)`);
