"""
generate_ppt.py — AGEVP Phase 2

Reads a JSON spec file (ppt_presentation shape) and produces a .pptx
presentation by cloning slides from the AGEVP template and filling
named text shapes with spec content.

Template slide map (Modele_AGEVP_Presentation.pptx):
  0 = cover  (Text 3: titre, Text 4: sous-titre, Text 6: date)
  2 = content (Text 1: titre, Text 4/8/12: points, Text 5/9/13: descriptions)

Usage:
    python scripts/generate_ppt.py <json-spec-path> [--template <path>] [--output <dir>]
"""

import sys
import json
import copy
import argparse
from pathlib import Path

try:
    from pptx import Presentation
except ImportError:
    print("Missing dependency. Run: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
DEFAULT_TEMPLATE = TEMPLATES_DIR / "Modele_AGEVP_Presentation.pptx"

_DML = "http://schemas.openxmlformats.org/drawingml/2006/main"
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

_TMPL_COVER = 0
_TMPL_CONTENT = 2  # 3-key-points layout

# Content slide shape name pairs: (point title, point description)
_POINT_SHAPES = [("Text 4", "Text 5"), ("Text 8", "Text 9"), ("Text 12", "Text 13")]


def _replace_shape_text(slide, shape_name: str, text: str) -> bool:
    """Replace text in named shape preserving first run's XML formatting."""
    for shape in slide.shapes:
        if shape.name != shape_name or not shape.has_text_frame:
            continue
        tf = shape.text_frame
        first_p = tf.paragraphs[0]._p
        runs = first_p.findall(f"{{{_DML}}}r")
        if runs:
            t = runs[0].find(f"{{{_DML}}}t")
            if t is not None:
                t.text = text
            for r in runs[1:]:
                first_p.remove(r)
        else:
            tf.text = text
        for extra_p in tf._txBody.findall(f"{{{_DML}}}p")[1:]:
            tf._txBody.remove(extra_p)
        return True
    return False


def _clone_slide(prs: Presentation, src_idx: int):
    """Append a deep-copy of prs.slides[src_idx] to prs and return the new slide."""
    src = prs.slides[src_idx]
    new_slide = prs.slides.add_slide(src.slide_layout)
    dst_tree = new_slide.shapes._spTree
    for elem in list(dst_tree):
        dst_tree.remove(elem)
    for elem in src.shapes._spTree:
        dst_tree.append(copy.deepcopy(elem))
    return new_slide


def _remove_slide(prs: Presentation, idx: int) -> None:
    """Remove prs.slides[idx] and its relationship entry."""
    slide_ids = list(prs.slides._sldIdLst)
    if idx >= len(slide_ids):
        return
    r_id = slide_ids[idx].get(f"{{{_REL}}}id")
    if r_id:
        try:
            prs.part._rels.pop(r_id)
        except (KeyError, Exception):
            pass
    prs.slides._sldIdLst.remove(slide_ids[idx])


def generate_ppt(spec_path: Path, output_dir: Path, template: Path | None = None) -> Path:
    """
    Build a .pptx presentation from a ppt_presentation JSON spec.

    Args:
        spec_path:  Path to the JSON spec file.
        output_dir: Directory where the .pptx file will be written.
        template:   Optional path to a .pptx template for branding.

    Returns:
        Absolute path of the created .pptx file.
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

    if spec.get("type") != "ppt_presentation":
        print(
            f"ERROR: expected type 'ppt_presentation', got '{spec.get('type')}'",
            file=sys.stderr,
        )
        sys.exit(1)

    resolved_template = template if template is not None else DEFAULT_TEMPLATE
    if not (resolved_template and resolved_template.exists()):
        print(f"ERROR: template not found: {resolved_template}", file=sys.stderr)
        sys.exit(1)

    prs = Presentation(str(resolved_template))
    n_original = len(prs.slides)

    title: str = spec.get("title", "Présentation")
    date: str = spec.get("date", "")
    event: str = spec.get("event", "")
    slides_spec: list = spec.get("slides", [])

    # Cover slide
    cover = _clone_slide(prs, _TMPL_COVER)
    _replace_shape_text(cover, "Text 3", title)
    _replace_shape_text(cover, "Text 4", event or title)
    if date:
        _replace_shape_text(cover, "Text 6", date)

    # Content slides — 3 bullets per output slide using the 3-key-points layout
    for slide_spec in slides_spec:
        slide_title: str = slide_spec.get("title", "")
        bullets: list = slide_spec.get("bullets", [])
        chunks = [bullets[i:i + 3] for i in range(0, max(len(bullets), 1), 3)]

        for ci, chunk in enumerate(chunks):
            s = _clone_slide(prs, _TMPL_CONTENT)
            label = slide_title if ci == 0 else f"{slide_title} (suite {ci + 1})"
            _replace_shape_text(s, "Text 1", label)
            for pi, (t_name, d_name) in enumerate(_POINT_SHAPES):
                _replace_shape_text(s, t_name, chunk[pi] if pi < len(chunk) else "")
                _replace_shape_text(s, d_name, "")

    # Remove original template slides (always at indices 0..n_original-1)
    for _ in range(n_original):
        _remove_slide(prs, 0)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{spec_path.stem}.pptx"

    try:
        prs.save(out_path)
    except OSError as exc:
        print(f"ERROR: cannot write {out_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    return out_path.resolve()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a .pptx presentation from a ppt_presentation JSON spec."
    )
    parser.add_argument("spec", help="Path to the JSON spec file")
    parser.add_argument(
        "--template",
        default=None,
        help=f"Path to a .pptx template for branding (default: {DEFAULT_TEMPLATE})",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory (default: output/)",
    )
    args = parser.parse_args()

    result = generate_ppt(
        spec_path=Path(args.spec),
        output_dir=Path(args.output),
        template=Path(args.template) if args.template else None,
    )
    print(result)
    sys.exit(0)
