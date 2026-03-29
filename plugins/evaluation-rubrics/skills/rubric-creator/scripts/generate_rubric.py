"""
generate_rubric.py — Rubric Creator output script
Usage: python generate_rubric.py <input_json> <output_path>

input_json: path to a JSON file with the following structure:
{
  "language": "es" | "en",
  "criteria": [
    {
      "name": "...",
      "cumple": "...",
      "parcial": "...",
      "no_cumple": "...",
      "pts": <int>
    },
    ...
  ]
}
"""

import json
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

HEADERS = {
    "es": ["Criterio", "Cumple (100%)", "Cumple Parcialmente (60%)", "No Cumple (0%)", "Puntos"],
    "en": ["Criterion", "Meets Expectations (100%)", "Partially Meets (60%)", "Does Not Meet (0%)", "Points"],
}

SHEET_NAMES = {"es": "Rubrica", "en": "Rubric"}

COL_WIDTHS = [28, 52, 52, 52, 10]


def generate(input_json_path, output_path):
    with open(input_json_path) as f:
        data = json.load(f)

    lang = data.get("language", "es")
    criteria = data["criteria"]

    assert sum(c["pts"] for c in criteria) == 100, \
        f"Points must sum to 100, got {sum(c['pts'] for c in criteria)}"

    wb = Workbook()
    ws = wb.active
    ws.title = SHEET_NAMES[lang]

    headers = HEADERS[lang]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical='top')

    for col_letter, width in zip("ABCDE", COL_WIDTHS):
        ws.column_dimensions[col_letter].width = width
    ws.freeze_panes = "A2"

    for c in criteria:
        ws.append([c["name"], c["cumple"], c["parcial"], c["no_cumple"], c["pts"]])
        row = ws.max_row
        ws.cell(row, 1).font = Font(bold=True)
        ws.cell(row, 5).font = Font(bold=True)
        for col in range(1, 6):
            kwargs = dict(wrap_text=True, vertical='top')
            if col == 5:
                kwargs['horizontal'] = 'center'
            ws.cell(row, col).alignment = Alignment(**kwargs)

    wb.save(output_path)
    print(f"Saved: {output_path} ({len(criteria)} criteria, {sum(c['pts'] for c in criteria)} pts)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_rubric.py <input_json> <output_path>")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
