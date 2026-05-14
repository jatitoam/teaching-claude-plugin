#!/usr/bin/env node
/**
 * shuffle_exam.js
 * Creates N shuffled versions of an MCQ exam from a source JSON file.
 *
 * Source JSON format (mcq-generator output):
 *   { "questions": [{ "number": N, "question": "...", "answers": ["correct", "wrong1", ...] }] }
 *
 * Output per version (exam_A.json, exam_B.json, ...):
 *   {
 *     "version": "A",
 *     "questions": [{
 *       "n": 1,
 *       "question": "...",
 *       "options": ["...", "...", "...", "..."],   // shuffled
 *       "correct_index": 2                          // 0=A,1=B,2=C,3=D
 *     }]
 *   }
 *
 * Usage:
 *   node shuffle_exam.js --input questions.json --versions 3 --output-dir ./out
 */

const fs   = require('fs');
const path = require('path');

// ── CLI args ────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
function getArg(flag) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : null;
}

const inputFile  = getArg('--input');
const nVersions  = parseInt(getArg('--versions') || '3', 10);
const outputDir  = getArg('--output-dir') || '.';

if (!inputFile) {
  console.error('Usage: node shuffle_exam.js --input <file> --versions <n> --output-dir <dir>');
  process.exit(1);
}

// ── Fisher-Yates shuffle ────────────────────────────────────────────────────
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// ── Load source ─────────────────────────────────────────────────────────────
const raw  = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

// Support both { questions: [...] } and a bare array
const sourceQuestions = Array.isArray(raw) ? raw : (raw.questions || raw);

if (!Array.isArray(sourceQuestions) || sourceQuestions.length === 0) {
  console.error('Source JSON must contain a non-empty "questions" array (or be a bare array).');
  process.exit(1);
}

// Normalise: each item must have .question and .answers where answers[0]=correct
const normalised = sourceQuestions.map((q, idx) => {
  const question = q.question || q.q || q.text || '';
  const answers  = q.answers  || q.options || [];
  if (!question) { console.error(`Q${idx + 1}: missing question text`); process.exit(1); }
  if (answers.length < 2) { console.error(`Q${idx + 1}: need at least 2 answers`); process.exit(1); }
  return { question, answers };
});

// ── Generate N versions ──────────────────────────────────────────────────────
fs.mkdirSync(outputDir, { recursive: true });

const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

for (let v = 0; v < nVersions; v++) {
  const letter = letters[v];

  // 1. Shuffle question order
  const shuffledQs = shuffle(normalised).map((q, i) => {
    // 2. Shuffle options, track correct answer position
    const correct    = q.answers[0];
    const shuffled   = shuffle(q.answers);
    const correctIdx = shuffled.indexOf(correct);

    return {
      n:             i + 1,
      question:      q.question,
      options:       shuffled,
      correct_index: correctIdx   // 0=A, 1=B, 2=C, 3=D
    };
  });

  const output = { version: letter, questions: shuffledQs };
  const outPath = path.join(outputDir, `exam_${letter}.json`);
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log(`Written: ${outPath} (${shuffledQs.length} questions)`);
}

console.log(`\nDone. ${nVersions} version(s) created in ${outputDir}/`);
