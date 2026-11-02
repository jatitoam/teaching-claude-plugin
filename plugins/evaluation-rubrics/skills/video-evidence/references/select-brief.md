# Select brief — Sonnet, one agent per video

Dispatch with `model: sonnet`, description `[Sonnet] Select evidence <submission-id>`. One per
video, all in one message. Fill `<…>`; paste the rest verbatim.

---

Model tier: Sonnet. You SELECT evidence for a judge; you do NOT decide verdicts or scores.
Write only `<pack>/evidence-map.json`.

- Pack: `<pack>` (contract `video-evidence/2`, see `<plugin>/skills/video-evidence/references/output-contract.md`)
- Rubric: `<rubric path>` · Assignment context: `<brief path or one paragraph>`

1. Read `metadata.json` (youtube title/description, `probe.duration_s`, `frames.max_gap_s`,
   `transcript.sparse`, flags), `frames-index.json` (Haiku descriptions of every kept frame;
   a frame covers the screen until `static_until_mmss`), `transcript.json`, and `evidence-map.json`.
   If there is no `frames-index.json` (`metadata.index.recommended` was "skip" — a very short
   video), open every frame in `frames.json` yourself instead; there are only a few.
2. For each item (criterion or penalty), find where in the video it can be judged. Use the index
   and transcript to locate candidates, then **open the candidate frames at full resolution**
   yourself — index descriptions are leads, not facts (Haiku may misread small text).
3. Fill `candidates`: `{from, to, frames, quotes:[{t, text}], on_screen:[{t, text, frame}],
   metadata_fields, why}` — `from/to` in seconds, `why` one line saying what the judge should look
   at. `quotes` = spoken words from `transcript.json` only; `on_screen` = text read on a frame
   (slides, text boxes, captions, overlays), verbatim, with the frame you read it on. Never put
   on-screen text in `why`. Prefer 1–3 strong candidates
   over many weak ones. Include contrary evidence too (a frame that might show the requirement
   NOT met) — the judge needs both sides.
4. Metadata items (duration, title, description, first frame = cover) cite `metadata_fields`
   (e.g. `probe.duration_s`, `youtube.description`) and/or `frames/t0000.000.jpg`.
5. If nothing relevant exists, leave `candidates` empty and write `coverage`: what you searched,
   and the largest stretch where it could have appeared unseen (between sampled frames, a fast
   scroll, unreadable text) with mm:ss — e.g. "not found in frames/transcript; 03:40–03:50 is a
   fast scroll that could hide it". If `transcript.sparse`, say transcript quotes are unreliable.
6. Do not write verdicts, scores, or words like "meets"/"fails". Then run
   `python3 <plugin>/skills/video-evidence/scripts/finalize_pack.py <pack>` and fix any errors it
   reports until it exits 0 (it also fills the `watch` links).

Reply in ≤ 12 lines: per item id → number of candidates (or "coverage only") and the mm:ss
ranges; then anything in the pack that looked broken.
