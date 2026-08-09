# Slide archetypes (reference)

> Course-agnostic. Used by the `slides` skill's Build step 1 (mining a template's own archetypes
> into `S<NN>-template-archetypes.md`) and by the spec's per-slide `Archetype:` field. This file
> teaches the generic taxonomy and how to derive the two shapes teaching decks need that business
> templates rarely ship — it does not itself produce or judge any one course's deck.

## Generic archetype taxonomy

Each entry: shape, one-line "right for…".

- **Cover** — right for: the sacred opening/title slide, a section's own title card.
- **Section divider** — right for: marking a new teaching block or topic shift.
- **Big statement** — right for: one idea the room should remember verbatim.
- **Big number** — right for: a single stat that anchors the point (a %, a count, a duration).
- **Two-item compare** — right for: contrasting two options, approaches, or states.
- **Multi-column grid** — right for: three or more parallel items of similar weight.
- **Timeline / step sequence** — right for: an ordered process or a session's own agenda.
- **Data table** — right for: several rows of comparable structured values.
- **Quote / callout** — right for: a definition, a warning, or a memorable line.
- **Full-bleed photo** — right for: a moment, a context, an emotional beat — minimal text.
- **Photo + text split** — right for: an image paired with an explanation of it.
- **Chart + legend** — right for: a trend or distribution the room needs to read at a glance.
- **Device mockup** — right for: showing a UI, app, or webpage inside its real frame.
- **Stacked label list** — right for: a short list of named items with brief tags (not a grid).
- **Agenda / TOC** — right for: previewing the session's shape at the opening.
- **Closing** — right for: wrap-up, thanks, next steps, a due delivery.

## ⚠️ Two shapes business templates almost never ship — and teaching decks constantly need

Business templates are built for pitches and quarterly reviews, not for teaching students to
*do* something. These two shapes are usually missing from the template's own layouts — derive
them; don't skip them.

### 1. The before/after pair

Two states of the same artifact side by side, **equal weight, aligned baselines**, with the
change marked (an arrow, a highlight, a delta callout).

- **Derive it from:** the template's symmetric two-item/two-photo geometry (whatever shape
  already places two blocks side by side at equal size).
- **Common failure:** unequal sizes — it reads as "one of these is more important" instead of
  "these differ." Keep both panes the same dimensions; only the marked change should draw the
  eye.

### 2. The verbatim monospace block

Click paths, instruction lines, code, commands — anything a student copies **character for
character**.

- **Derive it from:** the template's quote or text-plate shape, swapped to a monospace face on a
  tinted plate.
- ⚠️ **It must never wrap or shear.** A sheared command is worse than no slide, because it looks
  correct. *(Observed failure mode: a URL cut mid-string and a presenter's name silently
  truncated — neither visible in the HTML source, only on render.)* Widen the plate, shrink the
  type, or split across two lines at a safe boundary — never let the renderer choose the break.

## How to derive a missing shape without breaking the brand

Reuse the template's own spacing rhythm, type scale, accent color, and unifying visual device
(the plate/mat/rule/corner motif that makes every mined archetype read as one deck). Change the
**arrangement** — how blocks are placed and sized — never the **skin** — the colors, type,
spacing unit, and unifying device stay exactly what the template established.
