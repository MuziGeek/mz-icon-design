#!/usr/bin/env python3
"""Compose a deterministic 3x3 contact sheet from nine accepted RGBA PNG icons."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("icons_dir"); parser.add_argument("output"); parser.add_argument("--cell", type=int, default=512); args = parser.parse_args()
    files = sorted(Path(args.icons_dir).glob("*.png"))
    if len(files) != 9: parser.error("exactly nine PNG icons are required")
    canvas = Image.new("RGBA", (args.cell * 3, args.cell * 3), (0, 0, 0, 0))
    for index, file in enumerate(files):
        icon = Image.open(file).convert("RGBA")
        if icon.size != (args.cell, args.cell): parser.error(f"unexpected icon size: {file}")
        canvas.alpha_composite(icon, ((index % 3) * args.cell, (index // 3) * args.cell))
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True); canvas.save(output)
    print(output)


if __name__ == "__main__": main()
