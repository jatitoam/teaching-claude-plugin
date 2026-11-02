"""
append_grade.py — Assignment Evaluator output script
Appends one evaluated row to the grades xlsx, creating the file if it doesn't exist.

Usage:
    python append_grade.py <rubric_xlsx|rubric_json> <grades_xlsx> <row_json>

Arguments:
    rubric_xlsx   Path to the rubric .xlsx produced by rubric-creator (or a piezas rubric .json)
    grades_xlsx   Path to the grades output file (created if missing)
    row_json      Path to a JSON file with the evaluated row:

Row JSON structure:
{
  "name": "Group 1",
  "scores": {
    "Criterion Name 1": "Meets Expectations",
    "Criterion Name 2": "Partially Meets",
    "Criterion Name 3": "Does Not Meet"
  },
  "observations": {
    "Criterion Name 1": "",
    "Criterion Name 2": "only 2 out of 10 elements completed.",
    "Criterion Name 3": "missing price and link."
  },
  "penalties": {
    "Presentation": "met",
    "Attached file": {"level": "not_met", "note": "submitted a cloud link, not a file"}
  }
}

observations may also be a plain string (legacy format) — both are accepted.
When a dict is provided, non-empty values are compiled into a single string:
"Criterion Name 2: only 2 out of 10 elements completed. Criterion Name 3: missing price and link."

penalties is OPTIONAL (omit it for the original additive-only behaviour). When present, each key
is the name of a penalty row in the rubric's penalties block; the value is either a bare level
string or an object {"level": ..., "note": ...}. Accepted levels (case-insensitive, ES/EN):
    met       | cumple      -> no deduction
    partial   | parcial     -> 40% of the penalty magnitude (mirror of the 60% partial credit)
    not_met   | no_cumple   -> full penalty
Penalty magnitudes are read from the rubric (column E of the penalties block): a plain number
(e.g. "-15") deducts points; a percentage (e.g. "-100%") removes that share of the running total,
so "-100%" not-met zeroes the grade (invalid work). Point penalties apply first, then percentages.
The amount is extracted as the first signed number (plus an optional trailing "%"), so a decorated
cell like "**−100 %** · invalid if not met" is read the same as a clean "-100%".

Score labels must be exactly one of:
    "Meets Expectations" | "Partially Meets" | "Does Not Meet"
PIECE MODE ("piezas"): if <rubric> is a .json file with top-level "scoring": "piezas", scores are
per-piece points instead of levels x weights (see the PIECE MODE block below for the formulas and
the penalty/cap order). Row JSON additions: scores accept "not_applicable"/"N/A" (and pieces absent
from scores are not_applicable); keys may be the piece code, name, or "code · name"; optional
"piece_points": {code: number} is REQUIRED for open range pieces (e.g. "10–25") scored Meets/Partially.
Grades sheet: Name / Group | "<code> · <name>" per piece | Puntos | Nota | Observations.
A .json rubric WITHOUT scoring=piezas runs level mode (criteria 'pts' as weights). .xlsx = level mode, unchanged.
"""

import json
import re
import sys
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment

MULTIPLIERS = {
    "Meets Expectations": 1.0,
    "Partially Meets": 0.6,
    "Does Not Meet": 0.0,
}

VALID_LABELS = set(MULTIPLIERS.keys())

# Fraction of a penalty applied at each level (mirrors the additive 0.6 partial-credit rule).
PENALTY_LEVEL_FACTOR = {
    "met": 0.0, "cumple": 0.0,
    "partial": 0.4, "parcial": 0.4,
    "not_met": 1.0, "no_cumple": 1.0, "not met": 1.0,
}

# First signed number in a penalty amount, e.g. the "-15" in "**−15** · scored negatively".
_PENALTY_AMOUNT_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")


def _fmt(n):
    """Format a number without trailing '.0' for tidy observation notes."""
    n = round(n, 2)
    return str(int(n)) if n == int(n) else str(n)


def read_rubric(rubric_path):
    """Parse the rubric xlsx into (criteria, penalties).

    criteria  -> list of (name, weight) for the additive block.
    penalties -> list of {"name", "text"} for the optional penalties block.

    The additive block is the leading rows whose Points column (E) is numeric. The penalties
    block, if present, starts at the bold heading row (column A begins with "Penal…") that
    rubric-creator emits, followed by a header row and one row per penalty whose column E holds
    free-text amounts like "-15" or "-100%". Rubrics with no penalties block just return [].
    """
    wb = load_workbook(rubric_path, data_only=True)
    ws = wb.active
    criteria, penalties = [], []
    in_penalties = False
    for row in ws.iter_rows(min_row=2, values_only=True):
        name = row[0]
        pts = row[4] if len(row) >= 5 else None
        if name is None or str(name).strip() == "":
            continue  # blank separator row
        name = str(name).strip()
        low = name.lower()
        if low.startswith("penal"):          # penalties block heading -> everything below is penalties
            in_penalties = True
            continue
        if low in ("criterio", "criterion"):  # header row of either block
            continue
        if in_penalties:
            penalties.append({"name": name, "text": "" if pts is None else str(pts).strip()})
            continue
        if pts is None:
            continue
        try:
            weight = float(pts)
        except (TypeError, ValueError):
            # Non-numeric where a weight was expected: we've reached the penalties block without a
            # recognised heading. Treat this and the rest of the sheet as penalties.
            in_penalties = True
            penalties.append({"name": name, "text": str(pts).strip()})
            continue
        criteria.append((name, weight))
    return criteria, penalties


def parse_penalty_amount(text):
    """Parse a penalty amount into (kind, magnitude), or None if no number is present.

    Extracts the first signed number (and an optional trailing '%') from the text, so a clean
    magnitude ("-15", "-100%") and a decorated cell copied straight from grading-penalties.md
    ("**−100 %** · invalid if not met") parse identically. The unicode minus is normalised first.

    kind == "percent" -> magnitude is a fraction (0..1+), e.g. "-100%" -> ("percent", 1.0)
    kind == "points"  -> magnitude is a point amount,   e.g. "-15"    -> ("points", 15.0)
    """
    if text is None:
        return None
    s = str(text).replace("−", "-")  # normalise unicode minus (U+2212)
    m = _PENALTY_AMOUNT_RE.search(s)
    if m is None:
        return None
    magnitude = abs(float(m.group()))
    is_pct = s[m.end():].lstrip().startswith("%")  # a '%' after the number -> percentage
    return ("percent", magnitude / 100.0) if is_pct else ("points", magnitude)


def apply_penalties(base_total, rubric_penalties, row_penalties):
    """Apply the row's penalty assessments to base_total. Returns (final_total, notes).

    Point penalties are subtracted first, then percentage penalties are applied multiplicatively,
    then the total is clamped at 0. notes is a list of human-readable strings for the
    observations cell, one per penalty that actually deducted points.
    """
    if not rubric_penalties or not row_penalties:
        return base_total, []

    point_deduction = 0.0
    pct_fractions = []
    notes = []
    for pen in rubric_penalties:
        entry = row_penalties.get(pen["name"])
        if entry is None:
            continue
        if isinstance(entry, dict):
            level = str(entry.get("level", "")).strip().lower()
            note = str(entry.get("note", "")).strip()
        else:
            level, note = str(entry).strip().lower(), ""
        factor = PENALTY_LEVEL_FACTOR.get(level, 0.0)
        if factor == 0.0:  # met / cumple / unknown-benign -> no deduction
            continue
        parsed = parse_penalty_amount(pen["text"])
        if parsed is None:
            continue
        kind, magnitude = parsed
        suffix = f" ({note})" if note else ""
        if kind == "points":
            ded = magnitude * factor
            point_deduction += ded
            notes.append(f"PENALTY — {pen['name']}: -{_fmt(ded)} pts [{level}]{suffix}")
        else:
            frac = min(1.0, magnitude * factor)
            pct_fractions.append(frac)
            notes.append(f"PENALTY — {pen['name']}: -{_fmt(frac * 100)}% [{level}]{suffix}")

    total = base_total - point_deduction
    for frac in pct_fractions:
        total *= (1.0 - frac)
    return max(0.0, total), notes


def build_header(criteria):
    headers = ["Name / Group"] + [c[0] for c in criteria] + ["Total", "Observations"]
    return headers


def create_grades_file(grades_path, criteria):
    wb = Workbook()
    ws = wb.active
    ws.title = "Grades"

    headers = build_header(criteria)
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical='top')

    # Column widths
    ws.column_dimensions['A'].width = 28
    for i in range(len(criteria)):
        col_letter = ws.cell(1, i + 2).column_letter
        ws.column_dimensions[col_letter].width = 22
    # Total
    total_col = ws.cell(1, len(criteria) + 2).column_letter
    ws.column_dimensions[total_col].width = 10
    # Observations
    obs_col = ws.cell(1, len(criteria) + 3).column_letter
    ws.column_dimensions[obs_col].width = 80

    ws.freeze_panes = "A2"
    wb.save(grades_path)


def append_row(grades_path, criteria, penalties, row_data):
    wb = load_workbook(grades_path)
    ws = wb.active

    name = row_data["name"]
    scores = row_data["scores"]
    raw_obs = row_data.get("observations", "")
    if isinstance(raw_obs, dict):
        observations = " ".join(
            f"{k}: {v}" for k, v in raw_obs.items() if v
        )
    else:
        observations = raw_obs

    # Validate labels
    for cname, label in scores.items():
        if label not in VALID_LABELS:
            raise ValueError(f"Invalid score label '{label}' for criterion '{cname}'. Must be one of: {VALID_LABELS}")

    # Additive total, then apply the optional penalties block.
    base_total = sum(
        weight * MULTIPLIERS[scores.get(cname, "Does Not Meet")]
        for cname, weight in criteria
    )
    total, penalty_notes = apply_penalties(base_total, penalties, row_data.get("penalties", {}))
    if penalty_notes:
        observations = (observations + " " if observations else "") + " ".join(penalty_notes)

    row = [name] + [scores.get(cname, "Does Not Meet") for cname, _ in criteria] + [round(total, 1), observations]
    ws.append(row)

    data_row = ws.max_row
    num_cols = len(row)

    for col in range(1, num_cols + 1):
        cell = ws.cell(data_row, col)
        is_total = col == num_cols - 1
        kwargs = dict(wrap_text=True, vertical='top')
        if is_total:
            kwargs['horizontal'] = 'center'
            cell.font = Font(bold=True)
        cell.alignment = Alignment(**kwargs)

    wb.save(grades_path)
    print(f"Appended row for '{name}' → total: {round(total, 1)}")


# ---------------------------------------------------------------------------------------------
# PIECE MODE ("piezas") — triggered by a rubric .json whose top level has "scoring": "piezas".
# Level mode above is untouched. Kept in sync, verbatim, with the sibling script in the other
# skill folder (append_grade.py <-> build_grades.py) so both score identically.
#
#   points_raw  = sum of piece points (Meets -> pts, Partially -> pts_parcial, else 0;
#                 not_applicable pieces contribute 0 and are excluded)
#   points      = max(0, points_raw - point_penalties)      (kind "points" penalties, partial = 40%)
#   capped      = min(points, cap)
#   grade       = capped * factor, then percentage penalties applied multiplicatively to the grade
#
# ORDER (single place to flip): piece_points_total() — point penalties are subtracted BEFORE the
# cap, per the rubric text "-15 puntos de la suma de piezas" + conversion "MIN(puntos;CAP)/A*B".
# To apply the cap first instead, swap the two marked lines inside piece_points_total().
# ---------------------------------------------------------------------------------------------

PIECE_LABELS = {
    "Meets Expectations": "meets",
    "Partially Meets": "partial",
    "Does Not Meet": "not_met",
}
_PIECE_NA = {"not_applicable", "n/a", "na", "not applicable"}
_RANGE_RE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*[-–—]\s*(\d+(?:[.,]\d+)?)\s*$")
_PCT_RE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*%\s*$")
_CONV_RE = re.compile(
    r"MIN\(\s*[^;()]+?\s*;\s*(\d+(?:[.,]\d+)?)\s*\)\s*/\s*(\d+(?:[.,]\d+)?)\s*\*\s*(\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)


def _num(s, field):
    try:
        return float(str(s).strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"Rubric field '{field}': cannot parse number from {s!r}")


def _parse_piece_pts(value, code):
    """-> (lo, hi) ; lo == hi for fixed pieces. Accepts number, numeric string, 'a–b' range."""
    if isinstance(value, bool):
        raise ValueError(f"Piece {code}: invalid 'pts' {value!r}")
    if isinstance(value, (int, float)):
        return float(value), float(value)
    m = _RANGE_RE.match(str(value))
    if m:
        lo, hi = _num(m.group(1), f"{code}.pts"), _num(m.group(2), f"{code}.pts")
        if lo > hi:
            raise ValueError(f"Piece {code}: range 'pts' {value!r} has min > max")
        return lo, hi
    return (_num(value, f"{code}.pts"),) * 2


def _parse_conversion(conv, cap):
    """-> (factor, cap_from_conversion_or_None). Accepts number, dict, or 'MIN(puntos;300)/100*3'."""
    if isinstance(conv, bool) or conv is None:
        raise ValueError("Rubric field 'conversion' is missing or invalid")
    if isinstance(conv, (int, float)):
        return float(conv), None
    if isinstance(conv, dict):
        try:
            div, mul = float(conv["divide_by"]), float(conv["multiply_by"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("Rubric field 'conversion': object needs numeric 'divide_by' and 'multiply_by'")
        if div == 0:
            raise ValueError("Rubric field 'conversion': divide_by cannot be 0")
        return mul / div, None
    s = str(conv)
    m = _CONV_RE.search(s)
    if not m:
        raise ValueError(
            f"Rubric field 'conversion': cannot parse {s!r}; expected a number, "
            "{'divide_by':A,'multiply_by':B} or 'MIN(puntos;CAP)/A*B'"
        )
    c, a, b = (_num(g, "conversion") for g in m.groups())
    if a == 0:
        raise ValueError("Rubric field 'conversion': divisor is 0")
    return b / a, c


def load_piece_rubric(rubric_path):
    """Load a piezas rubric JSON -> dict(pieces, penalties, cap, factor). Raises ValueError."""
    with open(rubric_path, encoding="utf-8") as f:
        data = json.load(f)
    crit = data.get("criteria")
    if not isinstance(crit, list) or not crit:
        raise ValueError("Rubric field 'criteria' must be a non-empty list")
    pieces, seen = [], set()
    for c in crit:
        code = str(c.get("code", "")).strip()
        name = str(c.get("name", "")).strip()
        if not code or not name:
            raise ValueError(f"Every piece needs 'code' and 'name': {c!r}")
        if code.lower() in seen:
            raise ValueError(f"Duplicate piece code '{code}'")
        seen.add(code.lower())
        lo, hi = _parse_piece_pts(c.get("pts"), code)
        pp = c.get("pts_parcial")
        if isinstance(pp, bool) or pp is None:
            raise ValueError(f"Piece {code}: missing 'pts_parcial'")
        if isinstance(pp, (int, float)):
            partial = ("abs", float(pp))
        else:
            m = _PCT_RE.match(str(pp))
            partial = ("pct", _num(m.group(1), f"{code}.pts_parcial") / 100.0) if m \
                else ("abs", _num(pp, f"{code}.pts_parcial"))
        pieces.append({"code": code, "name": name, "lo": lo, "hi": hi,
                       "is_range": lo != hi, "partial": partial,
                       "label": f"{code} · {name}"})
    factor, conv_cap = _parse_conversion(data.get("conversion"), data.get("cap"))
    cap = data.get("cap")
    if cap is not None:
        if isinstance(cap, bool):
            raise ValueError("Rubric field 'cap' is invalid")
        cap = _num(cap, "cap")
        if conv_cap is not None and abs(conv_cap - cap) > 1e-9:
            raise ValueError(f"Rubric fields disagree: cap={cap} but conversion caps at {conv_cap}")
    else:
        cap = conv_cap
    penalties = [{"name": str(p["name"]).strip(), "text": str(p.get("penalty", p.get("penalizacion", ""))).strip()}
                 for p in data.get("penalties", [])]
    return {"pieces": pieces, "penalties": penalties, "cap": cap, "factor": factor}


def load_rubric_any(rubric_path):
    """Dispatch on rubric type. Returns ("piezas", rubric_dict) or ("levels", (criteria, penalties)).

    .xlsx -> level mode exactly as before. .json with scoring == "piezas" -> piece mode.
    .json without it -> level mode using criteria 'pts' as weights and each penalty's 'penalty' text.
    """
    if str(rubric_path).lower().endswith(".json"):
        with open(rubric_path, encoding="utf-8") as f:
            data = json.load(f)
        if str(data.get("scoring", "")).strip().lower() == "piezas":
            return "piezas", load_piece_rubric(rubric_path)
        criteria = [(str(c["name"]).strip(), float(c["pts"])) for c in data["criteria"]]
        penalties = [{"name": str(p["name"]).strip(), "text": str(p.get("penalty", p.get("penalizacion", ""))).strip()}
                     for p in data.get("penalties", [])]
        return "levels", (criteria, penalties)
    return "levels", read_rubric(rubric_path)


def piece_header(rubric):
    return (["Name / Group"] + [p["label"] for p in rubric["pieces"]]
            + ["Puntos", "Nota", "Observations"])


def create_piece_grades_file(grades_path, rubric):
    wb = Workbook()
    ws = wb.active
    ws.title = "Grades"
    ws.append(piece_header(rubric))
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical='top')
    n = len(rubric["pieces"])
    ws.column_dimensions['A'].width = 28
    for i in range(n):
        ws.column_dimensions[ws.cell(1, i + 2).column_letter].width = 22
    ws.column_dimensions[ws.cell(1, n + 2).column_letter].width = 10
    ws.column_dimensions[ws.cell(1, n + 3).column_letter].width = 10
    ws.column_dimensions[ws.cell(1, n + 4).column_letter].width = 80
    ws.freeze_panes = "A2"
    wb.save(grades_path)


def check_piece_header(grades_path, rubric):
    """Refuse to append into a sheet whose header does not match piece mode for this rubric."""
    ws = load_workbook(grades_path).active
    have = [c.value for c in ws[1]]
    want = piece_header(rubric)
    if have != want:
        raise ValueError(
            f"Grades file {grades_path} header does not match piece-mode rubric "
            f"(different mode or different rubric). Expected {want}, found {have}."
        )


def _resolve_piece(key, pieces):
    """Map a row key ('D8', full name, or 'D8 · name') to a piece dict, else None."""
    k = str(key).strip()
    low = k.casefold()
    for p in pieces:
        if low in (p["code"].casefold(), p["name"].casefold(), p["label"].casefold()):
            return p
    head = re.split(r"\s*[·:]\s*|\s+", k, maxsplit=1)[0].casefold()
    for p in pieces:
        if head == p["code"].casefold():
            return p
    return None


def _resolve_map(mapping, pieces, what):
    out = {}
    for key, val in (mapping or {}).items():
        p = _resolve_piece(key, pieces)
        if p is None:
            raise ValueError(f"Unknown piece '{key}' in {what}")
        if p["code"] in out:
            raise ValueError(f"Piece {p['code']} appears twice in {what}")
        out[p["code"]] = val
    return out


def _round_half_up(x, places=2):
    """Round like a spreadsheet's ROUND (1.125 -> 1.13), not Python's banker's rounding.
    Piece mode only; level mode keeps its original round(total, 1) for byte compatibility."""
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(1).scaleb(-places)
    v = float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))
    return int(v) if v == int(v) else v


def piece_points_total(points_raw, point_deduction, cap):
    """THE ORDER OF OPERATIONS (flip here if the instructor rules otherwise).

    Returns (points_after_penalties, capped_points). Current order: point penalties first,
    then cap. Floor at 0.
    """
    points = max(0.0, points_raw - point_deduction)      # step 1: point penalties
    capped = min(points, cap) if cap is not None else points  # step 2: cap
    return points, capped


def score_piece_row(rubric, row_data):
    """Score one row. Returns dict(name, cells, points, grade, observations)."""
    pieces = rubric["pieces"]
    name = row_data["name"]
    scores = _resolve_map(row_data.get("scores"), pieces, "scores")
    extra = _resolve_map(row_data.get("piece_points"), pieces, "piece_points")

    cells, points_raw = [], 0.0
    for p in pieces:
        label = scores.get(p["code"], "not_applicable")
        if str(label).strip().casefold() in _PIECE_NA:
            cells.append("N/A")
            continue
        if label not in PIECE_LABELS:
            raise ValueError(
                f"Invalid score label '{label}' for piece '{p['code']}'. "
                f"Must be one of: {sorted(VALID_LABELS)} or 'not_applicable'"
            )
        cells.append(label)
        level = PIECE_LABELS[label]
        if level == "not_met":
            continue
        if p["is_range"]:
            pp = extra.get(p["code"])
            if pp is None or isinstance(pp, bool):
                raise ValueError(
                    f"Piece {p['code']} is an open piece ({_fmt(p['lo'])}–{_fmt(p['hi'])} pts): "
                    f"'piece_points' with a value for {p['code']} is required when scored '{label}'"
                )
            try:
                full = float(pp)
            except (TypeError, ValueError):
                raise ValueError(f"piece_points for {p['code']} must be a number, got {pp!r}")
            if not (p["lo"] <= full <= p["hi"]):
                raise ValueError(
                    f"piece_points for {p['code']} = {_fmt(full)} is outside the range "
                    f"{_fmt(p['lo'])}–{_fmt(p['hi'])}"
                )
        else:
            full = p["lo"]
        if level == "meets":
            points_raw += full
        else:
            kind, v = p["partial"]
            points_raw += v * full if kind == "pct" else v

    # Penalties: split into point deductions and percentage fractions.
    row_pen = row_data.get("penalties") or {}
    known = {pen["name"].casefold(): pen for pen in rubric["penalties"]}
    for k in row_pen:
        if str(k).strip().casefold() not in known:
            raise ValueError(f"Unknown penalty '{k}' (rubric penalties: {[x['name'] for x in rubric['penalties']]})")
    point_deduction, pct_fractions, notes = 0.0, [], []
    for pen in rubric["penalties"]:
        entry = next((v for k, v in row_pen.items() if str(k).strip().casefold() == pen["name"].casefold()), None)
        if entry is None:
            continue
        if isinstance(entry, dict):
            level, note = str(entry.get("level", "")).strip().lower(), str(entry.get("note", "")).strip()
        else:
            level, note = str(entry).strip().lower(), ""
        if level not in PENALTY_LEVEL_FACTOR:
            raise ValueError(f"Invalid level '{level}' for penalty '{pen['name']}'")
        factor = PENALTY_LEVEL_FACTOR[level]
        if factor == 0.0:
            continue
        parsed = parse_penalty_amount(pen["text"])
        if parsed is None:
            raise ValueError(f"Penalty '{pen['name']}' has no parseable amount: {pen['text']!r}")
        kind, magnitude = parsed
        suffix = f" ({note})" if note else ""
        if kind == "points":
            ded = magnitude * factor
            point_deduction += ded
            notes.append(f"PENALTY — {pen['name']}: -{_fmt(ded)} pts [{level}]{suffix}")
        else:
            frac = min(1.0, magnitude * factor)
            pct_fractions.append(frac)
            notes.append(f"PENALTY — {pen['name']}: -{_fmt(frac * 100)}% [{level}]{suffix}")

    points, capped = piece_points_total(points_raw, point_deduction, rubric["cap"])
    if capped < points:
        notes.append(f"CAP — puntos {_fmt(points)} → {_fmt(capped)}")
    grade = capped * rubric["factor"]
    for frac in pct_fractions:
        grade *= (1.0 - frac)
    grade = max(0.0, grade)

    observations = compile_observations_any(row_data.get("observations", ""))
    if notes:
        observations = (observations + " " if observations else "") + " ".join(notes)
    return {"name": name, "cells": cells, "points": _round_half_up(capped),
            "grade": _round_half_up(grade), "observations": observations}


def compile_observations_any(raw_obs):
    if isinstance(raw_obs, dict):
        return " ".join(f"{k}: {v}" for k, v in raw_obs.items() if v)
    return raw_obs or ""


def append_piece_row(grades_path, rubric, row_data):
    res = score_piece_row(rubric, row_data)
    wb = load_workbook(grades_path)
    ws = wb.active
    row = [res["name"]] + res["cells"] + [res["points"], res["grade"], res["observations"]]
    ws.append(row)
    data_row = ws.max_row
    n = len(row)
    for col in range(1, n + 1):
        cell = ws.cell(data_row, col)
        kwargs = dict(wrap_text=True, vertical='top')
        if col in (n - 2, n - 1):  # Puntos, Nota
            kwargs['horizontal'] = 'center'
        if col == n - 1:
            cell.font = Font(bold=True)
        cell.alignment = Alignment(**kwargs)
    wb.save(grades_path)
    return res


def main():
    if len(sys.argv) != 4:
        print("Usage: python append_grade.py <rubric_xlsx|rubric_json> <grades_xlsx> <row_json>")
        sys.exit(1)

    rubric_path, grades_path, row_json_path = sys.argv[1], sys.argv[2], sys.argv[3]

    mode, rubric = load_rubric_any(rubric_path)

    if mode == "piezas":
        try:
            with open(row_json_path) as f:
                row_data = json.load(f)
            if Path(grades_path).exists():
                check_piece_header(grades_path, rubric)
            res = score_piece_row(rubric, row_data)  # validate fully before touching the file
            if not Path(grades_path).exists():
                create_piece_grades_file(grades_path, rubric)
                print(f"Created grades file: {grades_path}")
            append_piece_row(grades_path, rubric, row_data)
        except ValueError as e:
            print(f"ERROR: {e}")
            sys.exit(2)
        print(f"Appended row for '{res['name']}' → puntos: {res['points']}, nota: {res['grade']}")
        return

    criteria, penalties = rubric

    if Path(grades_path).exists():
        # Refuse to append level-mode rows into a piece-mode sheet (header ends Puntos | Nota | Observations).
        hdr = [c.value for c in load_workbook(grades_path).active[1]]
        if hdr[-3:] == ["Puntos", "Nota", "Observations"]:
            print(f"ERROR: {grades_path} is a piece-mode grades sheet; use the piezas rubric .json with it.")
            sys.exit(2)

    if not Path(grades_path).exists():
        create_grades_file(grades_path, criteria)
        print(f"Created grades file: {grades_path}")

    with open(row_json_path) as f:
        row_data = json.load(f)

    append_row(grades_path, criteria, penalties, row_data)


if __name__ == "__main__":
    main()
