#!/usr/bin/env python3
"""Build a deterministic local comparison board for Isometric Golden review."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def panel(image: Image.Image, label: str) -> Image.Image:
    canvas = Image.new("RGB", (528, 570), "#FDF6E9")
    preview = image.convert("RGBA")
    preview.thumbnail((512, 512), Image.Resampling.LANCZOS)
    canvas.paste(preview, ((528 - preview.width) // 2, 48), preview)
    ImageDraw.Draw(canvas).text((16, 16), label, fill="#062446")
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--isometric", required=True)
    parser.add_argument("--block", required=True)
    parser.add_argument("--soft-3d", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    sources = (("MZ Block (existing)", args.block), ("MZ Isometric V1 candidate", args.isometric), ("MZ Soft 3D (existing)", args.soft_3d))
    board = Image.new("RGB", (528 * 3, 570), "#F8F6F1")
    for index, (label, file) in enumerate(sources):
        with Image.open(file) as raw:
            board.paste(panel(raw, label), (528 * index, 0))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    board.save(output)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
