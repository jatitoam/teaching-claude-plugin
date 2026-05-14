#!/usr/bin/env node
/**
 * build_exam_html.js
 * Produces a Google Docs-compatible HTML file for one shuffled exam version.
 * Supports Part I (MCQ) and optional Part II (open-ended questions).
 *
 * Input JSON shape:
 *   data.questions  — shuffled MCQ array (from shuffle_exam.js)
 *   data.open_ended — optional array: [{ n, session, question }]
 *
 * Usage:
 *   node build_exam_html.js \
 *     --input exam_A.json --output exam_A.html \
 *     --section-header "PART I — Closed-Ended Questions" \
 *     --pts-per-question 4 --total-pts 60
 */
'use strict';
const fs = require('fs');

const args = process.argv.slice(2);
function getArg(f) { const i = args.indexOf(f); return i >= 0 ? args[i + 1] : null; }

const inputFile     = getArg('--input');
const outputFile    = getArg('--output');
const sectionHeader = getArg('--section-header') || 'PART I — Closed-Ended Questions';
const ptsPerQ       = parseInt(getArg('--pts-per-question') || '4', 10);
const totalPts      = parseInt(getArg('--total-pts') || '0', 10);

if (!inputFile || !outputFile) {
  console.error('Usage: node build_exam_html.js --input <f> --output <f> [opts]');
  process.exit(1);
}

const data      = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
const questions = data.questions  || [];
const openEnded = data.open_ended || [];

function esc(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

const FONTS = 'https://themes.googleusercontent.com/fonts/css?kit=rfSAlb2JfKqknMZbyNv1qbd1z-QJxci6pgsJEDD--sK5C-2JrCr1ABsZF5AjRv96T';

// ── Shared paragraph base ─────────────────────────────────────────────────────
const P = [
  'padding-top:0pt','margin:0','color:#000000','padding-left:0',
  'font-size:11pt','padding-bottom:10pt','font-family:&quot;Inter&quot;',
  'line-height:1.15','orphans:2','widows:2','text-align:left','padding-right:0'
].join(';');

// ── Part I styles ─────────────────────────────────────────────────────────────
const P1_H2   = 'padding-top:0pt;margin:0;color:#1836b2;border-bottom-color:#1836b2;padding-left:0;font-size:16pt;padding-bottom:2pt;line-height:1.15;page-break-after:avoid;border-bottom-width:1pt;font-family:&quot;League Spartan&quot;;border-bottom-style:solid;orphans:2;widows:2;text-align:left;padding-right:0';
const H2_SPAN = 'color:#1836b2;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:16pt;font-family:&quot;League Spartan&quot;;font-style:normal';
const INSTR   = 'color:#000000;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:10pt;font-family:&quot;Inter&quot;;font-style:normal';
const Q_BOLD  = 'color:#000000;font-weight:700;text-decoration:none;vertical-align:baseline;font-size:10pt;font-family:&quot;Inter&quot;;font-style:normal';
const OPT     = 'color:#000000;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:10pt;font-family:&quot;Inter&quot;;font-style:normal';
const CB      = '[&nbsp;&nbsp;&nbsp; ]'; // 3 nbsp + 1 regular space

// ── Part II styles ────────────────────────────────────────────────────────────
// Part II H2 differs: padding-top:10pt, line-height:1.0 (not 0pt/1.15 like Part I)
const P2_H2_BASE   = 'padding-top:10pt;margin:0;color:#1836b2;border-bottom-color:#1836b2;padding-left:0;font-size:16pt;padding-bottom:2pt;line-height:1.0;page-break-after:avoid;border-bottom-width:1pt;font-family:&quot;League Spartan&quot;;border-bottom-style:solid;orphans:2;widows:2;text-align:left;padding-right:0';
const P2_H2_SPACER = P2_H2_BASE + ';height:16pt'; // empty spacer H2 before the header
const P2_INSTR     = 'color:#000000;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:11pt;font-family:&quot;Inter&quot;;font-style:normal'; // 11pt (Part I uses 10pt)
const BLANK_P      = `<p style="${P};height:11pt"><span style="${P2_INSTR}"></span></p>`;

// ── Part I: section header ────────────────────────────────────────────────────
const nQ  = questions.length;
const tot = totalPts || (ptsPerQ * nQ);
const hdr = `${sectionHeader} - ${ptsPerQ} pts each (${tot} total)`;

// ── Part I: MCQ blocks ────────────────────────────────────────────────────────
const p1Blocks = questions.map(q => {
  const opts = q.options.map(o => `${CB} ${esc(o)}`).join('<br>');
  return `<p style="${P}"><span style="${Q_BOLD}">${esc(q.n + '. ' + q.question)}</span></p>\n`
       + `<p style="${P}"><span style="${OPT}">${opts}</span></p>`;
}).join('\n');

// ── Part II: open-ended blocks ────────────────────────────────────────────────
let p2Html = '';

if (openEnded.length > 0) {
  const p2Pts = openEnded.length * 10;
  const p2Hdr = `PART II \u2014 Open-Ended Questions - 10 pts each (${p2Pts} total)`;

  // Each question on its own page (page break before each)
  const qPages = openEnded.map(oq => {
    const answerLines = Array(18).fill(BLANK_P).join('\n');
    return `<hr style="page-break-before:always;display:none;">\n`
         + `<p style="${P}"><span style="${Q_BOLD}">${esc(oq.n + '. ' + oq.question)}</span></p>\n`
         + answerLines;
  }).join('\n');

  p2Html = [
    `\n<hr style="page-break-before:always;display:none;">`,
    `<h2 style="${P2_H2_SPACER}"><span style="${H2_SPAN}"></span></h2>`,
    `<h2 style="${P2_H2_BASE}"><span style="${H2_SPAN}">${esc(p2Hdr)}</span></h2>`,
    `<p style="${P}"><span style="${P2_INSTR}">Answer the following questions in the space provided. Responses should be thorough and well-structured, demonstrating understanding of course concepts.</span></p>`,
    BLANK_P,
    BLANK_P,
    qPages
  ].join('\n');
}

// ── Assemble final document ───────────────────────────────────────────────────
const html = `<html><head><meta content="text/html; charset=UTF-8" http-equiv="content-type">
<style type="text/css">
 @import url(${FONTS});
</style></head>
<body class="doc-content" style="background-color:#ffffff;max-width:468pt;padding:72pt 72pt 72pt 72pt">
<h2 style="${P1_H2}"><span style="${H2_SPAN}">${esc(hdr)}</span></h2>
<p style="${P}"><span style="${INSTR}">Read each question carefully and mark your answer by placing an X inside the brackets [ ] next to the correct option. Only one answer is correct per question.</span></p>
${p1Blocks}${p2Html}
</body></html>`;

fs.writeFileSync(outputFile, html, 'utf8');
console.log(`Written: ${outputFile} (${questions.length} MCQ + ${openEnded.length} open-ended, version ${data.version})`);
