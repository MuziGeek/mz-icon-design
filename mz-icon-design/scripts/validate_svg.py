#!/usr/bin/env python3
"""Static safety and style-aware validation for MZ UI SVG icon files."""
import argparse, json, sys
from pathlib import Path
from xml.etree import ElementTree as ET

DRAWING = {"path", "circle", "line", "polyline", "polygon", "rect", "ellipse"}
ALLOWED = DRAWING | {"svg", "g"}
FORBIDDEN = {"image", "text", "script", "style", "animate", "animateTransform", "filter", "mask", "pattern", "linearGradient", "radialGradient", "use", "foreignObject"}
ROOTS = {
    "mz-line-v1": {"viewBox": "0 0 24 24", "fill": "none", "stroke": "currentColor", "stroke-width": "1.5", "stroke-linecap": "round", "stroke-linejoin": "round"},
    "mz-filled-v1": {"viewBox": "0 0 24 24", "fill": "currentColor", "stroke": "none"},
}

def local(tag): return tag.rsplit("}", 1)[-1]
def check(path, style):
    errors, warnings = [], []
    try: root = ET.parse(path).getroot()
    except Exception as exc: return {"file": str(path), "errors": [f"invalid XML: {exc}"], "warnings": []}
    if local(root.tag) != "svg": errors.append("root must be <svg>")
    for key, expected in ROOTS[style].items():
        if root.attrib.get(key) != expected: errors.append(f"root {key} must be {expected!r}")
    drawings = 0
    for element in root.iter():
        tag = local(element.tag)
        if tag in FORBIDDEN: errors.append(f"forbidden element <{tag}>")
        elif tag not in ALLOWED: errors.append(f"unsupported element <{tag}>")
        if tag in DRAWING: drawings += 1
        for key, value in element.attrib.items():
            attr = local(key).lower()
            if attr.startswith("on") or attr in {"href", "xlink:href"}: errors.append(f"forbidden attribute {key}")
            if "url(" in value.lower(): errors.append(f"external or paint-server value in {key}")
            if style == "mz-filled-v1" and attr == "stroke" and value != "none": errors.append("filled icons must not use strokes")
            if style == "mz-filled-v1" and attr == "fill" and element is not root and value != "currentColor": errors.append("filled icons must use inherited currentColor fill")
    if drawings == 0: errors.append("no drawing primitives")
    if drawings > 6: warnings.append(f"{drawings} drawing primitives exceed the review budget of 6")
    warnings.append("path bounds require visual preview QA")
    return {"file": str(path), "errors": errors, "warnings": warnings}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("path"); parser.add_argument("--style", choices=sorted(ROOTS), default="mz-line-v1"); parser.add_argument("--json", action="store_true"); args = parser.parse_args()
    source = Path(args.path); files = [source] if source.is_file() else sorted(source.rglob("*.svg"))
    if not files: print("No SVG files found.", file=sys.stderr); raise SystemExit(1)
    reports = [check(file, args.style) for file in files]
    if args.json: print(json.dumps(reports, indent=2))
    else:
        for report in reports:
            state = "OK" if not report["errors"] else "FAIL"
            print(f"{state}\t{report['file']}")
            for message in report["errors"]: print(f"  error: {message}")
            for message in report["warnings"]: print(f"  warning: {message}")
    raise SystemExit(1 if any(item["errors"] for item in reports) else 0)
if __name__ == "__main__": main()
