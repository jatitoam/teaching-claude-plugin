# Index brief — Haiku, one agent per batch of up to 22 frames

Dispatch with `model: haiku`, description `[Haiku] Index frames <submission-id> b<NN>`. All
batches of all videos go in ONE message (parallel, ≤ 8 agents per message). Batches:
consecutive slices of `frames.json → frames[]`, **up to 22 per batch** (split evenly), numbered
`01, 02, …`. List the **`index-frames/<name>`** paths (1280-px copies), not `frames/`.

Why 22 at 1280 px (measured): ~62k tokens fixed per agent + ~1.45k per 1280-px frame. Batches
must satisfy F + n·h < 100k with margin — Haiku's price tier is 5× above 100k, and 24-frame
batches measured 98–101.6k. Alignment held at 24 when frames are read strictly one at a time; it
drifted at 35. See SKILL.md Step 2. Fill `<…>`; paste the rest verbatim.

---

Model tier: Haiku. You DESCRIBE video frames. You do not grade, judge, or compare against any
rubric — you have none.

Pack: `<pack>`. Your frames (open each with the Read tool; paths relative to the pack):
<list of frames/tSSSS.mmm.jpg, one per line>

Work strictly one frame at a time, in the order listed: open a frame, write its object (with
`file` = the exact path you just opened), then open the next. Never describe a frame you have
not just opened. Never open two frames in one step.

For each frame write one JSON object:
```json
{"file": "index-frames/t0065.000.jpg",
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
