"""
token_fill.py — AGEVP Phase 2 shared token engine

Placeholder-replacement primitives shared by the document generators.

Templates carry literal ``{{TOKEN}}`` markers (uppercase A-Z, digits, ``_``).
Generators duplicate a branded template, then swap each ``{{TOKEN}}`` for a
value pulled from the JSON spec — located by token text, never by positional
index or shape name. A token whose value is missing/empty is blanked (the
marker is removed) so no raw ``{{...}}`` ever leaks into the output.

Substitution is run-level: only the individual run holding a token is
rewritten, so surrounding runs keep their formatting. Inject one token per run
in the template (see tokenize_templates.py) — tokens must not span runs.
"""

import re
import sys
import json
from pathlib import Path

# OOXML namespaces
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"    # WordprocessingML
A = "http://schemas.openxmlformats.org/drawingml/2006/main"           # DrawingML (pptx)

TOKEN_RE = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")


def load_spec(spec_path: Path, expected_type: str) -> dict:
    """Read + validate a JSON spec, exiting with a clear message on any error."""
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

    if spec.get("type") != expected_type:
        print(
            f"ERROR: expected type '{expected_type}', got '{spec.get('type')}'",
            file=sys.stderr,
        )
        sys.exit(1)

    return spec


def _sub(text: str, tokens: dict) -> str:
    """Replace every {{TOKEN}} in text, blanking unknown/empty tokens."""
    return TOKEN_RE.sub(lambda m: str(tokens.get(m.group(1), "") or ""), text)


# --------------------------------------------------------------------------
# WordprocessingML (docx)
# --------------------------------------------------------------------------

def para_text(p_elem) -> str:
    """Concatenated visible text of a w:p element."""
    return "".join(t.text or "" for t in p_elem.iter(f"{{{W}}}t"))


def para_has_token(p_elem, name: str) -> bool:
    return f"{{{name}}}" in para_text(p_elem)


def fill_para_tokens(p_elem, tokens: dict) -> None:
    """Replace tokens in every run of a w:p element, preserving run formatting."""
    for t in p_elem.iter(f"{{{W}}}t"):
        if t.text and "{{" in t.text:
            t.text = _sub(t.text, tokens)


def set_first_run_text(p_elem, text: str) -> None:
    """Set the first w:r's text and drop the rest — used by the tokenizer."""
    runs = p_elem.findall(f"{{{W}}}r")
    if not runs:
        return
    t = runs[0].find(f"{{{W}}}t")
    if t is not None:
        t.text = text
    for extra in runs[1:]:
        p_elem.remove(extra)


# --------------------------------------------------------------------------
# DrawingML (pptx)
# --------------------------------------------------------------------------

def shape_text(shape) -> str:
    if not shape.has_text_frame:
        return ""
    return shape.text_frame.text


def slide_has_token(slide, name: str) -> bool:
    marker = f"{{{name}}}"
    return any(shape.has_text_frame and marker in shape.text_frame.text
               for shape in slide.shapes)


def fill_slide_tokens(slide, tokens: dict) -> None:
    """Replace tokens in every run of every text shape on a slide."""
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for t in shape.text_frame._txBody.iter(f"{{{A}}}t"):
            if t.text and "{{" in t.text:
                t.text = _sub(t.text, tokens)


def set_shape_first_run(shape, text: str) -> None:
    """Set the shape's first run text, drop trailing runs/paragraphs (tokenizer)."""
    tf = shape.text_frame
    body = tf._txBody
    paras = body.findall(f"{{{A}}}p")
    if not paras:
        tf.text = text
        return
    first_p = paras[0]
    runs = first_p.findall(f"{{{A}}}r")
    if runs:
        t = runs[0].find(f"{{{A}}}t")
        if t is not None:
            t.text = text
        for extra in runs[1:]:
            first_p.remove(extra)
    else:
        tf.text = text
    for extra_p in paras[1:]:
        body.remove(extra_p)
