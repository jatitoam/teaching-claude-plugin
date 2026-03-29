"""
append_grade.py — Assignment Evaluator output script
Appends one evaluated row to the grades xlsx, creating the file if it doesn't exist.

Usage:
    python append_grade.py <rubric_xlsx> <grades_xlsx> <row_json>

Arguments:
    rubric_xlsx   Path to the rubric .xlsx produced by rubric-creator
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
  "observations": "Criterion Name 2: only 2 out of 10 elements completed. Criterion Name 3: missing price and link."
}

Score labels must be exactly one of:
    "Meets Expectations" | "Partially Meets" | "Does Not Meet"
"""

import json
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


def read_rubric(rubric_path):
    """Returns list of (criterion_name, weight) tuples from the rubric xlsx."""
    wb = load_workbook(rubric_path, data_only=True)
    ws = wb.active
    criteria = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        name, _, _, _, pts = row[0], row[1], row[2], row[3], row[4]
        if name and pts is not None:
            criteria.append((str(name).strip(), float(pts)))
    return criteria


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


def append_row(grades_path, criteria, row_data):
    wb = load_workbook(grades_path)
    ws = wb.active

    name = row_data["name"]
    scores = row_data["scores"]
    observations = row_data.get("observations", "")

    # Validate labels
    for cname, label in scores.items():
        if label not in VALID_LABELS:
            raise ValueError(f"Invalid score label '{label}' for criterion '{cname}'. Must be one of: {VALID_LABELS}")

    # Calculate total
    total = sum(
        weight * MULTIPLIERS[scores.get(cname, "Does Not Meet")]
        for cname, weight in criteria
    )

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


def main():
    if len(sys.argv) != 4:
        print("Usage: python append_grade.py <rubric_xlsx> <grades_xlsx> <row_json>")
        sys.exit(1)

    rubric_path, grades_path, row_json_path = sys.argv[1], sys.argv[2], sys.argv[3]

    criteria = read_rubric(rubric_path)

    if not Path(grades_path).exists():
        create_grades_file(grades_path, criteria)
        print(f"Created grades file: {grades_path}")

    with open(row_json_path) as f:
        row_data = json.load(f)

    append_row(grades_path, criteria, row_data)


if __name__ == "__main__":
    main()
