#!/usr/bin/env python3
"""Validate MZ spot-icon PNG geometry, alpha, and neutral-grey residue."""
import argparse, json, sys
from pathlib import Path
from PIL import Image

def inspect(path, expected=512):
    errors, warnings = [], []
    with Image.open(path) as raw:
        image = raw.convert("RGBA")
    if image.size != (expected, expected): errors.append(f"expected {expected}x{expected}, got {image.width}x{image.height}")
    corners = [image.getpixel(point)[3] for point in ((0,0), (image.width-1,0), (0,image.height-1), (image.width-1,image.height-1))]
    if any(alpha != 0 for alpha in corners): errors.append("corners must be transparent")
    alpha = image.getchannel("A"); bbox = alpha.getbbox()
    if not bbox: errors.append("no visible subject")
    else:
        if min(bbox[0], bbox[1], image.width - bbox[2], image.height - bbox[3]) < 2: errors.append(f"subject too close to edge: {bbox}")
        pixels = list(image.getdata()); visible = [pixel for pixel in pixels if pixel[3] >= 32]
        coverage = len(visible) / (image.width * image.height)
        if not .03 <= coverage <= .75: warnings.append(f"unusual visible coverage: {coverage:.3f}")
        near_grey = sum(1 for red, green, blue, alpha_value in visible if max(abs(red-128), abs(green-128), abs(blue-128)) <= 10)
        if visible and near_grey / len(visible) > .08: warnings.append("high neutral-grey residue; inspect QA composites")
    return {"file": str(path), "errors": errors, "warnings": warnings, "bbox": bbox}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("path"); parser.add_argument("--size", type=int, default=512); parser.add_argument("--json", action="store_true"); args = parser.parse_args()
    target = Path(args.path); files = [target] if target.is_file() else sorted(target.glob("*.png"))
    if not files: print("No PNG files found.", file=sys.stderr); raise SystemExit(1)
    reports = [inspect(file, args.size) for file in files]
    if args.json: print(json.dumps(reports, indent=2, default=str))
    else:
        for report in reports:
            print(f"{'OK' if not report['errors'] else 'FAIL'}\t{report['file']}")
            for message in report['errors']: print(f"  error: {message}")
            for message in report['warnings']: print(f"  warning: {message}")
    raise SystemExit(1 if any(report['errors'] for report in reports) else 0)
if __name__ == "__main__": main()
