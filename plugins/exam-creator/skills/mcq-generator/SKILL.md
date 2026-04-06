---
name: mcq-generator
description: >
  Generates multiple-choice question (MCQ) exams from course content and outputs
  a structured JSON file ready for import into any exam delivery system. Use this
  skill whenever the user wants to CREATE or GENERATE a multiple-choice exam, quiz,
  test, or practice questions from course materials — lecture notes, slides, readings,
  syllabi, textbook chapters, or any academic content. Trigger on phrases like:
  "create an exam", "make a quiz", "generate multiple choice questions", "create a
  test from my notes", "build an MCQ exam", "make practice questions", "generate exam
  questions", "create a multiple-choice quiz", or similar. Applies to any subject and
  education level. Do NOT trigger for open-ended or essay questions.
---

# MCQ Generator

Generates a multiple-choice exam JSON file from course content.

## Step 1 — Read Content and Detect Language

Accept course material in any format the user provides: PDF, docx, md, txt, or pasted text. Read everything before proceeding.

Auto-detect the language from the content (Spanish or English) — do not ask.

## Step 2 — Propose Topics and Question Count

Before generating any questions, present two proposals to the user and wait for confirmation:

**Topics:** Extract the key topics covered in the content. List them clearly. Ask the user to confirm, remove, add, or reorder topics. The final topic list drives question distribution.

**Question count:** Suggest a number based on content depth and topic count — a reasonable baseline is 2–3 questions per topic, but adjust up or down based on how much material each topic covers. State your reasoning briefly (e.g., "5 topics × 2–3 questions = 10–15 questions; I suggest 12"). Ask the user to confirm or adjust.

Wait for the user's response before continuing.

## Step 3 — Generate Questions

Generate the confirmed number of questions distributed across the confirmed topics. For each question, follow these rules without exception:

### Question design rules

**Invert the definition:** The question body must contain the definition, description, or characteristic. The answers must be the concepts, terms, or labels — not the other way around.

- Wrong: "What is prompt engineering?" → [4 definitions as answers]
- Right: "What discipline focuses on designing and optimizing inputs to get better outputs from AI systems?" → [Prompt engineering / Fine tuning / Model training / Context design]

This matters because it forces the student to understand the concept deeply rather than recognize a memorized definition.

**Answers must be short.** Prefer single words, short phrases, or proper nouns as answers. Avoid full sentences. Aim for answers that feel like labels or titles, not explanations.

**First answer is always the correct one.** The exam delivery system randomizes answer order — you must place the correct answer first so the teacher can use position as a reference key. Never shuffle or vary this.

**Design distractors from the same conceptual family.** Wrong answers should come from the same topic area — terms, modules, or concepts that a student could realistically confuse with the correct answer. Avoid obviously wrong answers. Prioritize:
1. Concepts from the same course that share similar definitions or scope
2. Common student misconceptions about the topic
3. Plausible-sounding alternatives that require genuine understanding to distinguish

**Example of good distractor design (CRM modules):** If the correct answer is "Accounts" (the module that maintains enterprise records), the wrong answers should be other CRM modules like "Contacts", "Leads", "Opportunities" — not unrelated concepts like "Dashboard" or "Reports".

**Distribute questions across topics** proportionally to content depth. Each confirmed topic should appear at least once.

## Step 4 — Build and Save the JSON

Construct the JSON using this structure:

```json
{
  "language": "es",
  "course": "Course or subject name",
  "topics": ["Topic A", "Topic B", "Topic C"],
  "questions": [
    {
      "number": 1,
      "topic": "Topic A",
      "question": "What is the definition or characteristic that describes...?",
      "answers": [
        "Correct concept",
        "Wrong concept 1",
        "Wrong concept 2",
        "Wrong concept 3"
      ]
    }
  ]
}
```

Rules:
- `language`: `"es"` or `"en"`, auto-detected from content; when mixed languages, always ask
- `course`: infer from context (filename, title, or content heading); ask the user only if genuinely unclear
- `topics`: the confirmed topic list from Step 2
- Each question's `topic` field must match one of the entries in the top-level `topics` array
- `answers[0]` is always the correct answer

Determine the output directory:
- If the user specified a destination folder, use that folder.
- Otherwise, default to `/mnt/user-data/outputs/`.

Save the file as `exam_<slug>.json` where `<slug>` is a short lowercase identifier derived from the course name (e.g., `exam_crm_basics.json`).

## Step 5 — Deliver

Present the file with `present_files`.

Report only: number of questions generated and topics covered. Nothing else.

If the user edits the JSON and asks to re-present it, use `present_files` again without regenerating.
