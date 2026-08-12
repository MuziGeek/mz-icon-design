#!/usr/bin/env python3
"""Compose transparent spot-icon candidates into an exact 4x4 neutral-grey sheet."""
import argparse
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("icons_dir")
    parser.add_argument("output")
    parser.add_argument("--size", type=int, default=1254)
    parser.add_argument("--background", default="#808080")
    args = parser.parse_args()
    files = sorted(Path(args.icons_dir).glob("*.png"))
    if len(files) != 9:
        parser.error("exactly nine PNG icons are required")
    colour = tuple(int(args.background.lstrip("#")[index:index + 2], 16) for index in (0, 2, 4))
    canvas = Image.new("RGBA", (args.size, args.size), (*colour, 255))
    for index, file in enumerate(files):
        left, right = round((index % 4) * args.size / 4), round(((index % 4) + 1) * args.size / 4)
        top, bottom = round((index // 4) * args.size / 4), round(((index // 4) + 1) * args.size / 4)
        cell = Image.open(file).convert("RGBA").resize((right - left, bottom - top), Image.Resampling.LANCZOS)
        canvas.alpha_composite(cell, (left, top))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output)
    print(output)


if __name__ == "__main__":
    main()
