# Index brief — Haiku, one agent per batch of up to 16 frames

Dispatch with `model: haiku`, description `[Haiku] Index frames <submission-id> b<NN>`. All
batches of all videos go in ONE message (parallel, ≤ 8 agents per message). Batches:
consecutive slices of `frames.json → frames[]`, **up to 16 per batch** (split evenly), numbered
`01, 02, …`.

Why 16 (measured): each agent costs ~62k tokens of fixed overhead + ~1.5–5k per frame
(1280 px → 1080p). Bigger batches are cheaper, but at 35 frames per agent Haiku's descriptions
drifted one frame out of alignment over a stretch (frame N described with N+1's content);
12-frame batches stayed aligned. 16 keeps alignment with less overhead than 12. Fill `<…>`; paste the rest verbatim.

---

Model tier: Haiku. You DESCRIBE video frames. You do not grade, judge, or compare against any
rubric — you have none.

Pack: `<pack>`. Your frames (open each with the Read tool; paths relative to the pack):
<list of frames/tSSSS.mmm.jpg, one per line>

Work strictly one frame at a time, in the order listed: open a frame, write its object (with
`file` = the exact path you just opened), then open the next. Never describe a frame you have
not just opened.

For each frame write one JSON object:
```json
{"file": "frames/t0065.000.jpg",
 "app": "Power BI Desktop",
 "screen": "report view with a bar chart",
 "headings": ["Country wise sales"],
 "key_text": ["Canada", "France", "Total 12,79,31,601"],
 "summary": "bar chart of sales by country"}
```
- `app`: application or page type (browser + site, IDE, slide, terminal, n8n editor, …).
- `headings`: titles, tab names, dialog titles, slide titles — verbatim.
- `key_text`: up to ~8 short verbatim strings that identify what is on screen (column headers,
  labels, button/menu names, values). Copy exactly; if you cannot read a string clearly,
  do not guess it — write `"[small text unreadable]"` once.
- `summary`: ≤ 8 words.
Write the JSON array (in frame order) to `<pack>/frames-index/batch-<NN>.json` (create the
folder if needed). Reply with only: `batch <NN>: <n> frames written`.
