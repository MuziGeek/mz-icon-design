#!/usr/bin/env python3
"""Remove neutral-grey background fringe from an MZ Isometric PNG without redrawing it."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


BACKGROUND = (128, 128, 128)


def unblend(channel: int, alpha: int) -> int:
    """Recover a foreground channel composited over the fixed grey source sheet."""
    if alpha <= 0:
        return 0
    value = round((channel * 255 - BACKGROUND[0] * (255 - alpha)) / alpha)
    return max(0, min(255, value))


def is_neutral_shadow(red: int, green: int, blue: int) -> bool:
    average = (red + green + blue) / 3
    return max(red, green, blue) - min(red, green, blue) <= 16 and 80 <= average <= 180


def is_warm_shadow(red: int, green: int, blue: int) -> bool:
    average = (red + green + blue) / 3
    return max(red, green, blue) - min(red, green, blue) <= 28 and 95 <= average <= 220


def small_components(image: Image.Image, minimum_size: int = 16) -> set[tuple[int, int]]:
    alpha = image.getchannel("A")
    width, height = image.size
    seen: set[tuple[int, int]] = set()
    remove: set[tuple[int, int]] = set()
    for y in range(height):
        for x in range(width):
            if alpha.getpixel((x, y)) < 32 or (x, y) in seen:
                continue
            component, stack = [], [(x, y)]
            seen.add((x, y))
            while stack:
                px, py = stack.pop()
                component.append((px, py))
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and alpha.getpixel((nx, ny)) >= 32:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            if len(component) < minimum_size:
                remove.update(component)
    return remove


def exterior_pixels(image: Image.Image) -> set[tuple[int, int]]:
    alpha = image.getchannel("A")
    width, height = image.size
    seen, stack = set(), []
    for x in range(width):
        stack.extend(((x, 0), (x, height - 1)))
    for y in range(height):
        stack.extend(((0, y), (width - 1, y)))
    while stack:
        x, y = stack.pop()
        if not (0 <= x < width and 0 <= y < height) or (x, y) in seen or alpha.getpixel((x, y)) >= 32:
            continue
        seen.add((x, y))
        stack.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
    return seen


def normalize(image: Image.Image) -> Image.Image:
    source = image.convert("RGBA")
    target = Image.new("RGBA", source.size, (0, 0, 0, 0))
    source_pixels, target_pixels = source.load(), target.load()
    for y in range(source.height):
        for x in range(source.width):
            red, green, blue, alpha = source_pixels[x, y]
            if alpha < 16:
                continue
            # High-confidence subject pixels remain byte-for-byte untouched.
            # Only neutral grey can be source-sheet fringe; warm-white is a
            # legitimate Isometric structural surface and must be preserved.
            if alpha >= 224 and not is_neutral_shadow(red, green, blue):
                target_pixels[x, y] = (red, green, blue, alpha)
                continue
            foreground = (unblend(red, alpha), unblend(green, alpha), unblend(blue, alpha))
            # This removes only semi-transparent low-saturation source-sheet residue;
            # coloured anti-aliasing is retained with its recovered foreground colour.
            if is_neutral_shadow(*foreground):
                continue
            target_pixels[x, y] = (*foreground, alpha)
    # Remove only the remaining neutral-grey outer contour that touches the
    # transparent exterior. Internal and warm-white facets stay intact.
    alpha = target.getchannel("A")
    exterior = exterior_pixels(target)
    for y in range(1, target.height - 1):
        for x in range(1, target.width - 1):
            red, green, blue, opacity = target_pixels[x, y]
            if not (16 <= opacity <= 255 and is_neutral_shadow(red, green, blue)):
                continue
            neighbours = [(x + dx, y + dy) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))]
            if any(point in exterior for point in neighbours):
                target_pixels[x, y] = (0, 0, 0, 0)
    for x, y in small_components(target):
        target_pixels[x, y] = (0, 0, 0, 0)
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    with Image.open(args.input) as raw:
        result = normalize(raw)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    print(f"normalized {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
