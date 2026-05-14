#!/usr/bin/env node
/**
 * build_exam_html.js
 * Produces a Google Docs-compatible HTML file for one shuffled exam version.
 *
 * Input:  exam_A.json (from shuffle_exam.js)
 * Output: exam_A.html (ready to upload via Google Drive:create_file)
 *
 * Usage:
 *   node build_exam_html.js \
 *     --input exam_A.json \
 *     --output exam_A.html \
 *     --section-header "PART I — Closed-Ended Questions" \
 *     --pts-per-question 4 \
 *     --total-pts 60
 */

'use strict';
const fs   = require('fs');
const path = require('path');

const args = process.argv.slice(2);
function getArg(flag) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : null;
}

const inputFile     = getArg('--input');
const outputFile    = getArg('--output');
const sectionHeader = getArg('--section-header') || 'PART I — Closed-Ended Questions';
const ptsPerQ       = parseInt(getArg('--pts-per-question') || '4', 10);
const totalPts      = parseInt(getArg('--total-pts') || '0', 10);

if (!inputFile || !outputFile) {
  console.error('Usage: node build_exam_html.js --input <file> --output <file> [options]');
  process.exit(1);
}

const data      = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
const questions = data.questions || [];

// ── HTML Escape ──────────────────────────────────────────────────────────────
function esc(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ── Styles ───────────────────────────────────────────────────────────────────
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

const INSTR_SPAN = [
  'color:#000000', 'font-weight:400', 'text-decoration:none',
  'vertical-align:baseline', 'font-size:10pt',
  'font-family:&quot;Inter&quot;', 'font-style:normal'
].join(';');

const Q_SPAN = [
  'color:#000000', 'font-weight:700', 'text-decoration:none',
  'vertical-align:baseline', 'font-size:10pt',
  'font-family:&quot;Inter&quot;', 'font-style:normal'
].join(';');

const OPT_SPAN = [
  'color:#000000', 'font-weight:400', 'text-decoration:none',
  'vertical-align:baseline', 'font-size:10pt',
  'font-family:&quot;Inter&quot;', 'font-style:normal'
].join(';');

// Checkbox: 3 non-breaking spaces + 1 regular space before ]
const CB = '[&nbsp;&nbsp;&nbsp; ]';

// ── Section header text ───────────────────────────────────────────────────────
const nQ        = questions.length;
const computedTotal = totalPts || (ptsPerQ * nQ);
const headerText = `${sectionHeader} - ${ptsPerQ} pts each (${computedTotal} total)`;

// ── Build question blocks ─────────────────────────────────────────────────────
const blocks = questions.map(q => {
  const optLines = q.options.map(o => `${CB} ${esc(o)}`).join('<br>');
  const qPara = `<p style="${P_STYLE}"><span style="${Q_SPAN}">${esc(q.n + '. ' + q.question)}</span></p>`;
  const oPara = `<p style="${P_STYLE}"><span style="${OPT_SPAN}">${optLines}</span></p>`;
  return qPara + '\n' + oPara;
}).join('\n');

// ── Assemble HTML ─────────────────────────────────────────────────────────────
const html = `<html><head><meta content="text/html; charset=UTF-8" http-equiv="content-type">
<style type="text/css">
 @import url(${FONTS_URL});
</style></head>
<body class="doc-content" style="background-color:#ffffff;max-width:468pt;padding:72pt 72pt 72pt 72pt">
<h2 style="${H2_STYLE}"><span style="${H2_SPAN}">${esc(headerText)}</span></h2>
<p style="${P_STYLE}"><span style="${INSTR_SPAN}">Read each question carefully and mark your answer by placing an X inside the brackets [ ] next to the correct option. Only one answer is correct per question.</span></p>
${blocks}
</body></html>`;

fs.writeFileSync(outputFile, html, 'utf8');
console.log(`Written: ${outputFile} (${questions.length} questions, version ${data.version})`);
