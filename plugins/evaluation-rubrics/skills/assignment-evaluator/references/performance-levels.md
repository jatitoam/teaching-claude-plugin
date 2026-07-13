# Performance Levels Reference

## How Levels Work

Each rubric criterion defines three performance levels with explicit descriptions. Your job is to match the student's work to the level whose description best fits — not to invent thresholds or reinterpret what each level means.

| Level | Multiplier |
|-------|------------|
| Meets Expectations / Cumple | 1.0 × criterion weight |
| Partially Meets / Cumple Parcialmente | 0.6 × criterion weight |
| Does Not Meet / No Cumple | 0.0 × criterion weight |

The multipliers are fixed. The level boundaries are defined entirely by the rubric.

## Matching Student Work to a Level

1. Read the rubric's description for each level of the criterion.
2. Compare the student's submission against those descriptions.
3. Assign the level whose description the submission most closely satisfies.

Do not apply judgment that goes beyond what the rubric describes. If the rubric says "Partially Meets requires 6–9 of the 10 items," use that. If the rubric gives a qualitative description instead, use that. Never substitute your own threshold rules for the rubric's language.

## Score Calculation

For each criterion:
- `criterion_score = criterion_weight × level_multiplier`

Additive subtotal = sum of all criterion scores.

## Penalties (optional block)

If the rubric has a penalties block, each penalty is assessed at one of three levels, and a
fraction of its magnitude is deducted:

| Level | Factor |
|-------|--------|
| Met / Cumple | 0.0 (no deduction) |
| Partial / Parcial | 0.4 × penalty magnitude |
| Not Met / No Cumple | 1.0 × penalty magnitude |

The partial factor (0.4) mirrors the 60% partial credit on the additive side. Magnitudes come
from the rubric's penalty column:
- A **point** amount (`-15`) subtracts points from the subtotal.
- A **percentage** (`-100%`) removes that share of the running total — so a `-100%` penalty at
  Not Met zeroes the grade (invalid work).

**Row total** = additive subtotal − point penalties, then × (1 − each percentage penalty),
clamped at 0.
