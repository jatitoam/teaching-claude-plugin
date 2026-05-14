#!/usr/bin/env node
/**
 * build_answer_key.js
 * Reads N shuffled exam JSON files and produces answer_key.json.
 *
 * Input (exam_A.json, exam_B.json, ...):
 *   { "version": "A", "questions": [{ "n": 1, "question": "...",
 *     "options": [...], "correct_index": 2 }] }
 *
 * Output (answer_key.json):
 *   {
 *     "A": [{ "n": 1, "letter": "C", "correct_text": "..." }, ...],
 *     "B": [...],
 *     ...
 *   }
 *
 * Usage:
 *   node build_answer_key.js --input-dir ./out --output answer_key.json
 *
 * The script auto-discovers all exam_*.json files in input-dir unless
 * --versions is specified (e.g. --versions A,B,C).
 */

const fs   = require('fs');
const path = require('path');

const args = process.argv.slice(2);
function getArg(flag) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : null;
}

const inputDir   = getArg('--input-dir') || '.';
const outputFile = getArg('--output') || 'answer_key.json';
const versionsArg = getArg('--versions'); // optional "A,B,C"

const LETTERS = ['A','B','C','D','E','F','G','H'];

// Discover version files
let versionFiles;
if (versionsArg) {
  versionFiles = versionsArg.split(',').map(v => ({
    letter: v.trim(),
    file:   path.join(inputDir, `exam_${v.trim()}.json`)
  }));
} else {
  versionFiles = fs.readdirSync(inputDir)
    .filter(f => /^exam_[A-Z]\.json$/.test(f))
    .sort()
    .map(f => ({
      letter: f.replace('exam_', '').replace('.json', ''),
      file:   path.join(inputDir, f)
    }));
}

if (versionFiles.length === 0) {
  console.error('No exam_*.json files found in', inputDir);
  process.exit(1);
}

const answerKey = {};

for (const { letter, file } of versionFiles) {
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  const questions = data.questions || [];

  answerKey[letter] = questions.map(q => {
    const idx = q.correct_index;
    if (idx === undefined || idx === null) {
      console.error(`[Exam ${letter}] Q${q.n}: missing correct_index`);
      process.exit(1);
    }
    const letter_answer = LETTERS[idx] || '?';
    const correct_text  = q.options[idx] || '?';
    if (letter_answer === '?') {
      console.error(`[Exam ${letter}] Q${q.n}: correct_index ${idx} out of range`);
      process.exit(1);
    }
    return {
      n:            q.n,
      letter:       letter_answer,
      correct_text: correct_text,
      question_snippet: q.question.slice(0, 80)
    };
  });

  console.log(`Exam ${letter}: ${answerKey[letter].length} answers resolved`);
}

fs.writeFileSync(outputFile, JSON.stringify(answerKey, null, 2));
console.log(`\nAnswer key written to: ${outputFile}`);
