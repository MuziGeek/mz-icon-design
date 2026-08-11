#!/usr/bin/env python3
"""Compose final transparent spot icons into a strict 4x4 neutral-grey reference sheet."""
import argparse
from pathlib import Path
from PIL import Image

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("icons_dir"); parser.add_argument("output")
    parser.add_argument("--size", type=int, default=1254); parser.add_argument("--background", default="#808080"); args = parser.parse_args()
    icons = [Image.open(path).convert("RGBA") for path in sorted(Path(args.icons_dir).glob("*.png"))]
    if not 1 <= len(icons) <= 16: parser.error("expected 1-16 PNG icons")
    sheet = Image.new("RGBA", (args.size, args.size), args.background)
    cell = args.size / 4
    target = round(cell * .72)
    for index, icon in enumerate(icons):
        row, col = divmod(index, 4)
        scaled = icon.copy(); scaled.thumbnail((target, target), Image.Resampling.LANCZOS)
        x = round((col + .5) * cell - scaled.width / 2); y = round((row + .5) * cell - scaled.height / 2)
        sheet.alpha_composite(scaled, (x, y))
    sheet.convert("RGB").save(args.output)
    print(f"Created strict 4x4 sheet: {args.output}")
if __name__ == "__main__": main()
