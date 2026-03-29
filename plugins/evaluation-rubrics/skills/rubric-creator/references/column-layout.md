# Column Layout Reference

## Spreadsheet Columns

| Col | Header (ES) | Header (EN) | Width (chars) | Formatting |
|-----|------------|-------------|--------------|------------|
| A | Criterio | Criterion | 28 | Bold, wrap, top-align |
| B | Cumple (100%) | Meets Expectations (100%) | 52 | Wrap, top-align |
| C | Cumple Parcialmente (60%) | Partially Meets (60%) | 52 | Wrap, top-align |
| D | No Cumple (0%) | Does Not Meet (0%) | 52 | Wrap, top-align |
| E | Puntos | Points | 10 | Bold, center, top-align |

## Formatting Rules

- Table starts at **A1** — no titles, subtitles, or blank rows above.
- **No background colors, cell fills, or color formatting** of any kind.
- **No total row** at the bottom.
- Bold applied only to: header row (row 1), column A values, column E values.
- No italic, no font color, no font size changes from default.
- Freeze header row at A2.
- Sheet tab: `Rubrica` (ES) or `Rubric` (EN).
- Do not hardcode row heights — let `wrap_text=True` handle it naturally.
