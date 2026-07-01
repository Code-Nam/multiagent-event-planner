"""
generate_docx.py — AGEVP Phase 2

Reads a JSON spec file (docx_report shape) and produces a .docx document
with a Heading 1 title, Heading 2 section headings, and Normal paragraphs
for body content. Output filename is derived from the input spec filename stem.

If templates/report.docx exists it is loaded as a style base (branding,
fonts, colors). Pass --template to override the template path explicitly.

Usage:
    python scripts/generate_docx.py <json-spec-path> [--template <path>] [--output <dir>]
"""

import sys
import json
import argparse
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("Missing dependency. Run: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
DEFAULT_TEMPLATE = TEMPLATES_DIR / "report.docx"


def _base_document(template: Path | None) -> Document:
    if template and template.exists():
        doc = Document(str(template))
        # Clear any body content carried over from the template
        body = doc.element.body
        for child in list(body):
            body.remove(child)
        return doc
    return Document()


def generate_docx(spec_path: Path, output_dir: Path, template: Path | None = None) -> Path:
    """
    Build a .docx document from a docx_report JSON spec.

    Args:
        spec_path:  Path to the JSON spec file.
        output_dir: Directory where the .docx file will be written.
        template:   Optional path to a .docx template for branding.
                    Defaults to templates/report.docx when present.

    Returns:
        Absolute path of the created .docx file.

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

    if spec.get("type") != "docx_report":
        print(
            f"ERROR: expected type 'docx_report', got '{spec.get('type')}'",
            file=sys.stderr,
        )
        sys.exit(1)

    title: str = spec.get("title", "Document")
    sections: list = spec.get("sections", [])

    resolved_template = template if template is not None else DEFAULT_TEMPLATE
    doc = _base_document(resolved_template)

    doc.add_heading(title, level=1)

    for section in sections:
        heading: str = section.get("heading", "")
        content: str = section.get("content", "")

        if heading:
            doc.add_heading(heading, level=2)
        if content:
            doc.add_paragraph(content)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{spec_path.stem}.docx"

    try:
        doc.save(out_path)
    except OSError as exc:
        print(f"ERROR: cannot write {out_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    return out_path.resolve()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a .docx report from a docx_report JSON spec."
    )
    parser.add_argument("spec", help="Path to the JSON spec file")
    parser.add_argument(
        "--template",
        default=None,
        help=f"Path to a .docx template for branding (default: {DEFAULT_TEMPLATE})",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory (default: output/)",
    )
    args = parser.parse_args()

    result = generate_docx(
        spec_path=Path(args.spec),
        output_dir=Path(args.output),
        template=Path(args.template) if args.template else None,
    )
    print(result)
    sys.exit(0)
