# Index brief — Haiku, one agent per batch of up to 36 frames

Dispatch with `model: haiku`, description `[Haiku] Index frames <submission-id> b<NN>`. All
batches of all videos go in ONE message (parallel, ≤ 8 agents per message). Batches:
consecutive slices of `frames.json → frames[]`, **up to 36 per batch** (split evenly, e.g. 66
frames → 2 × 33), numbered `01, 02, …`.

Why 36: measured cost is ~62k tokens of fixed per-agent overhead + ~1.5k per frame (1 frame →
64k, 12 → 80k). 12-frame batches spend ~75 % on overhead; 36 cuts total indexing cost by more
than half while each agent still finishes in about a minute. Fill `<…>`; paste the rest verbatim.

---

Model tier: Haiku. You DESCRIBE video frames. You do not grade, judge, or compare against any
rubric — you have none.

Pack: `<pack>`. Your frames (open each with the Read tool; paths relative to the pack):
<list of frames/tSSSS.mmm.jpg, one per line>

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
