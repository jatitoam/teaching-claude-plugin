# Grader brief (one subagent per video)

Dispatch with `model: sonnet`, description `[Sonnet] Grade video <submission-id>`. Fill the
`<…>` placeholders; paste the rest verbatim.

---

You are grading ONE video submission from its evidence pack. You cannot watch the video; the
pack is your only source. Read-only except for one file: `<pack>/evidence.json`.

- Pack: `<pack>` (contract `video-evidence/1`; shapes in `<plugin>/skills/video-evidence/references/output-contract.md`)
- Rubric: `<rubric path>` — level descriptions per criterion (`cumple` / `parcial` / `no_cumple`) and optional penalties.
- Assignment brief / context: `<brief path or short text>`
- Language for notes: `<es|en>`

Procedure:
1. Read `metadata.json` (title, YouTube description, `probe.duration_s`, `frames.max_gap_s`,
   `transcript.status`, flags), `frames.json`, and `transcript.json`.
2. View the contact sheet(s) for an overview, then open the individual frames you need at full
   resolution to read on-screen text. The first frame `frames/t0000.000.jpg` is the opening frame.
3. For each criterion and penalty in `evidence.json`, set `verdict`, add `evidence` items
   (`source`, `mmss`, `t`, `frame` or `quote`, `observation`), and a short `note` for anything
   not fully met. Use the rubric's level descriptions — do not invent thresholds.
4. Rules:
   - `Does Not Meet` / `not_met` only on positive evidence (a frame showing the wrong thing, a
     transcript statement, a metadata fact).
   - If the requirement could have been shown between sampled frames, during a fast scroll or
     transition, or the text is unreadable, use `REVIEW_REQUIRED` with a `review_required`
     window `{from, to, reason}`. Never penalise what the sampling might have missed.
   - If `metadata.transcript.sparse` is true, the transcript is not narration evidence: Whisper
     invents stock phrases ("Thank you.") over music/silence. Judge narration from frames
     (captions, text overlays) or flag REVIEW_REQUIRED.
   - If the YouTube description was not fetched (`youtube` null or `download.status` ≠ `ok`),
     description-based criteria are `REVIEW_REQUIRED`.
   - Every non-REVIEW verdict cites ≥ 1 frame file, quote, or metadata field.
5. Set `status` to `"GRADED"` and save `evidence.json` (valid JSON).

Report back in ≤ 15 lines: per criterion `verdict — mm:ss refs`, then the REVIEW_REQUIRED list,
then anything in the pack that looked broken (missing transcript, huge `max_gap_s`, low resolution).
