# Output File Column Layout

## Structure

| Col | Content | Width (chars) | Formatting |
|-----|---------|--------------|------------|
| A | Name / Group | 28 | Bold header, wrap, top-align |
| B…N | One column per criterion (name from rubric) | 22 each | Wrap, top-align |
| N+1 | Total | 10 | Bold header, bold values, center |
| N+2 | Observations | 80 | Wrap, top-align |

Criterion column count is dynamic — determined by reading the rubric file at runtime.

## Formatting Rules

- Table starts at **A1** — no titles, blank rows, or extra content above.
- **No background colors, fills, or color formatting** of any kind.
- Bold applied only to: header row (row 1), Total column values.
- No italic, no font color, no font size changes from default.
- Freeze header row at A2.
- Sheet tab: `Grades`.
- Do not hardcode row heights — let `wrap_text=True` handle it.

## Header Row (row 1)

```
Name / Group | <Criterion 1 name> | <Criterion 2 name> | ... | Total | Observations
```

Criterion headers are read directly from column A of the rubric xlsx (rows 2+).

## Data Rows

One row per student/group submission. Fields:

- **Name / Group**: extracted from submission cover page, or provided by user.
- **Criterion columns**: one of `Meets Expectations`, `Partially Meets`, or `Does Not Meet`.
- **Total**: integer or float — sum of `criterion_weight × multiplier` across all criteria.
- **Observations**: single string, no line breaks. Format:
  `Criterion Name: <reason>. Criterion Name: <reason>.`
  Only include criteria scored as Partially Meets or Does Not Meet.
  If all criteria meet expectations, leave blank.
