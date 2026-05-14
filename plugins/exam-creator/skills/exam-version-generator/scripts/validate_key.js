#!/usr/bin/env node
/**
 * validate_key.js
 * Validates answer_key.json: ensures no entry has letter "?" or missing
 * correct_text, and prints a per-version summary.
 *
 * Usage:
 *   node validate_key.js --input answer_key.json
 *
 * Exit code 0 = all good. Exit code 1 = errors found.
 */

const fs = require('fs');

const args = process.argv.slice(2);
function getArg(flag) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : null;
}

const inputFile = getArg('--input') || 'answer_key.json';
const key = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

let total   = 0;
let missing = 0;

for (const [version, questions] of Object.entries(key)) {
  let vMissing = 0;
  for (const q of questions) {
    total++;
    if (!q.letter || q.letter === '?' || !q.correct_text || q.correct_text === '?') {
      console.error(`  [Exam ${version}] Q${q.n}: UNRESOLVED — "${q.question_snippet}"`);
      vMissing++;
      missing++;
    }
  }
  if (vMissing === 0) {
    console.log(`Exam ${version}: ${questions.length}/${questions.length} answers OK`);
  } else {
    console.error(`Exam ${version}: ${vMissing} MISSING answer(s)`);
  }
}

console.log(`\nTotal: ${total} | Missing: ${missing}`);

if (missing > 0) {
  console.error('\nValidation FAILED. Fix missing answers before exporting.');
  process.exit(1);
} else {
  console.log('Validation PASSED. Safe to export.');
  process.exit(0);
}
