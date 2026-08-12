#!/usr/bin/env python3
"""Normalize a Colorblock candidate to MZ palette families and bounded 2D tonal modelling."""
import argparse
from pathlib import Path

from PIL import Image


PALETTE = ((6, 36, 70), (251, 188, 14), (213, 73, 2))


def distance(pixel, base):
    return sum((pixel[index] - base[index]) ** 2 for index in range(3))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--variation", type=float, default=0.08)
    args = parser.parse_args()
    if not 0 <= args.variation <= 0.12:
        parser.error("variation must be between 0 and 0.12")
    with Image.open(args.input) as raw:
        image = raw.convert("RGBA")
    pixels = image.load()
    denominator = max(1, image.width + image.height - 2)
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0:
                continue
            base = min(PALETTE, key=lambda item: distance((red, green, blue), item))
            progress = (x + y) / denominator
            factor = 1 + args.variation / 2 - args.variation * progress
            pixels[x, y] = tuple(round(channel * factor) for channel in base) + (alpha,)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(output)


if __name__ == "__main__":
    main()
