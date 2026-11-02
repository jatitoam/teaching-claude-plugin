# Index brief — Haiku, one agent per batch of up to 18 frames

Dispatch with `model: haiku`, description `[Haiku] Index frames <submission-id> b<NN>`. All
batches of all videos go in ONE message (parallel, ≤ 8 agents per message). The capture script
already split the kept frames into `<pack>/.work/index-batch-NN.txt` (≤ 18 `index-frames/…`
paths each; listed in `metadata.index.batches`) — one agent per file. Point the agent at the
file; don't paste frame lists. Quote every path exactly (folders may contain spaces).

Why 18 (measured): ~62k tokens fixed per agent + ~1.45k per 1280-px frame, bounded by Haiku's 5×
price tier above 100k: F + n·h < 100k with margin. 24 measured 98–101.6k; a 19-frame batch of busy
composite frames hit 105.5k when the agent re-opened frames — so 18, and frames are read once.
Fill `<…>`; paste the rest verbatim.

---

Model tier: Haiku. You DESCRIBE video frames. You do not grade, judge, or compare against any
rubric — you have none.

Pack: `"<pack>"`. Your frame list: `"<pack>/.work/index-batch-<NN>.txt"` — read it first; each
line is an absolute path to one `index-frames/t….jpg`. Open each with the Read tool exactly as
written (paths may contain spaces).

Work strictly one frame at a time, in the order listed: open a frame, write its object (with
`file` = the exact path you just opened), then open the next. Never describe a frame you have
not just opened. Never open two frames in one step. **Open each frame exactly once — never
re-open a frame**, even a busy one; describe what you could read and use
`"[small text unreadable]"` for the rest. Do not write helper scripts.

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
