"""
generate_xlsx.py — AGEVP Phase 2

Reads a JSON spec file (xlsx_recap shape) and produces an .xlsx workbook
with one worksheet per sheet entry, bold header row, and auto-fitted
column widths. Output filename is derived from the input spec filename stem.

Usage:
    python scripts/generate_xlsx.py <json-spec-path>
"""

import sys
import json
import argparse
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import Font
except ImportError:
    print("Missing dependency. Run: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)


def auto_fit_columns(ws: openpyxl.worksheet.worksheet.Worksheet) -> None:
    """Set column widths based on the maximum cell content length."""
    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                cell_len = len(str(cell.value)) if cell.value is not None else 0
                if cell_len > max_len:
                    max_len = cell_len
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max_len + 4, 60)


def generate_xlsx(spec_path: Path, output_dir: Path) -> Path:
    """
    Build an .xlsx workbook from an xlsx_recap JSON spec.

    Args:
        spec_path:  Path to the JSON spec file.
        output_dir: Directory where the .xlsx file will be written.

    Returns:
        Absolute path of the created .xlsx file.

    Raises:
        SystemExit: on any I/O or validation error.
    """
    try:
        raw = spec_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read {spec_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {spec_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if spec.get("type") != "xlsx_recap":
        print(
            f"ERROR: expected type 'xlsx_recap', got '{spec.get('type')}'",
            file=sys.stderr,
        )
        sys.exit(1)

    sheets: list = spec.get("sheets", [])

    if not sheets:
        print("ERROR: spec contains no sheets", file=sys.stderr)
        sys.exit(1)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # remove default empty sheet

    bold_font = Font(bold=True)

    for sheet_spec in sheets:
        sheet_name: str = sheet_spec.get("name", "Sheet")
        headers: list = sheet_spec.get("headers", [])
        rows: list = sheet_spec.get("rows", [])

        ws = wb.create_sheet(title=sheet_name)

        if headers:
            ws.append(headers)
            for cell in ws[1]:
                cell.font = bold_font

        for row in rows:
            ws.append(row)

        auto_fit_columns(ws)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{spec_path.stem}.xlsx"

    try:
        wb.save(out_path)
    except OSError as exc:
        print(f"ERROR: cannot write {out_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    return out_path.resolve()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate an .xlsx workbook from an xlsx_recap JSON spec."
    )
    parser.add_argument("spec", help="Path to the JSON spec file")
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory (default: output/)",
    )
    args = parser.parse_args()

    result = generate_xlsx(
        spec_path=Path(args.spec),
        output_dir=Path(args.output),
    )
    print(result)
    sys.exit(0)
