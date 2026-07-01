"""
generate_docx.py — AGEVP Phase 2

Reads a JSON spec file (docx_report shape) and produces a .docx document by
duplicating the branded AGEVP template and filling {{TOKEN}} placeholders with
spec content. Slots are located by token text, not positional index, so the
template can be re-laid-out freely as long as the tokens survive.

Tokens (see scripts/tokenize_templates.py):
  {{DOC_TITLE}} {{DOC_SUBTITLE}}   cover
  {{SEC_NUM}} {{SEC_TITLE}}        section heading  (cloned per section)
  {{SEC_BODY}}                     section body     (cloned per section)

Spec shape:
  {"type": "docx_report", "title": str, "event"?: str, "subtitle"?: str,
   "sections": [{"heading": str, "content": str}, ...]}

Usage:
    python scripts/generate_docx.py <json-spec-path> [--template <path>] [--output <dir>]
"""

import sys
import copy
import argparse
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("Missing dependency. Run: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

import token_fill as tf
from token_fill import W, load_spec, para_text, para_has_token, fill_para_tokens

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
DEFAULT_TEMPLATE = TEMPLATES_DIR / "Modele_AGEVP.docx"


def _normalize_style_names(doc: Document) -> None:
    # python-docx 1.2+ BabelFish translates specific UI names (e.g. "Heading 1"
    # -> "heading 1") before XML lookup. Templates saved by Word/LibreOffice may
    # store the capitalised form. Fix only the aliased names so lookup succeeds.
    from docx.styles.styles import BabelFish
    ui_to_internal = dict(BabelFish.style_aliases)
    for style_elem in doc.styles._element:
        name_elem = style_elem.find(f"{{{W}}}name")
        if name_elem is not None:
            val = name_elem.get(f"{{{W}}}val", "")
            if val in ui_to_internal:
                name_elem.set(f"{{{W}}}val", ui_to_internal[val])


def _first_para_with_token(body, name: str):
    for p in body.findall(f"{{{W}}}p"):
        if para_has_token(p, name):
            return p
    return None


def _build_from_template(doc, title, subtitle, sections) -> bool:
    """Fill the tokenized template in place. Returns False if tokens are absent."""
    body = doc.element.body
    orig = list(body)

    sec_title_tmpl = _first_para_with_token(body, "SEC_TITLE")
    sec_body_tmpl = _first_para_with_token(body, "SEC_BODY")
    sect_pr = body.find(f"{{{W}}}sectPr")
    if sec_title_tmpl is None or sec_body_tmpl is None:
        return False

    cut = orig.index(sec_title_tmpl)

    # Cover = every paragraph before the first section block (skip demo tables).
    cover_tokens = {"DOC_TITLE": title, "DOC_SUBTITLE": subtitle}
    cover = []
    for el in orig[:cut]:
        if el.tag == f"{{{W}}}p":
            c = copy.deepcopy(el)
            fill_para_tokens(c, cover_tokens)
            cover.append(c)

    # Footer = last paragraph before sectPr (branding line), kept verbatim.
    paras = [e for e in orig if e.tag == f"{{{W}}}p"]
    footer = copy.deepcopy(paras[-1]) if paras else None

    heading_tmpl = copy.deepcopy(sec_title_tmpl)
    body_tmpl = copy.deepcopy(sec_body_tmpl)

    for child in list(body):
        body.remove(child)

    for el in cover:
        body.append(el)

    for i, section in enumerate(sections, 1):
        h = copy.deepcopy(heading_tmpl)
        fill_para_tokens(h, {"SEC_NUM": f"{i}  ", "SEC_TITLE": section.get("heading", "")})
        body.append(h)
        b = copy.deepcopy(body_tmpl)
        fill_para_tokens(b, {"SEC_BODY": section.get("content", "")})
        body.append(b)

    if footer is not None:
        body.append(footer)
    if sect_pr is not None:
        body.append(sect_pr)
    return True


def _build_plain(title, sections) -> Document:
    """Fallback: unbranded document when no tokenized template is available."""
    doc = Document()
    doc.add_heading(title, level=1)
    for section in sections:
        if section.get("heading"):
            doc.add_heading(section["heading"], level=2)
        if section.get("content"):
            doc.add_paragraph(section["content"])
    return doc


def generate_docx(spec_path: Path, output_dir: Path, template: Path | None = None) -> Path:
    spec = load_spec(spec_path, "docx_report")

    title = spec.get("title", "Document")
    event = spec.get("event", "")
    subtitle = spec.get("subtitle", event)
    sections = spec.get("sections", [])

    resolved_template = template if template is not None else DEFAULT_TEMPLATE

    if resolved_template and resolved_template.exists():
        doc = Document(str(resolved_template))
        _normalize_style_names(doc)
        if not _build_from_template(doc, title, subtitle, sections):
            print(
                f"WARNING: {resolved_template.name} has no {{{{SEC_TITLE}}}} tokens — "
                "run scripts/tokenize_templates.py. Falling back to a plain document.",
                file=sys.stderr,
            )
            doc = _build_plain(title, sections)
    else:
        doc = _build_plain(title, sections)

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
    parser.add_argument("--output", default="output", help="Output directory (default: output/)")
    args = parser.parse_args()

    result = generate_docx(
        spec_path=Path(args.spec),
        output_dir=Path(args.output),
        template=Path(args.template) if args.template else None,
    )
    print(result)
    sys.exit(0)
