#!/usr/bin/env python3
"""Normalize a transparent single-image candidate onto the MZ 512px spot canvas."""
import argparse
from collections import deque
from pathlib import Path

from PIL import Image


def remove_small_alpha_components(image, minimum):
    alpha = image.getchannel("A")
    width, height = image.size
    opaque = {(x, y) for y in range(height) for x in range(width) if alpha.getpixel((x, y)) >= 128}
    seen, retained = set(), set()
    for point in opaque:
        if point in seen:
            continue
        queue, component = deque([point]), set([point])
        seen.add(point)
        while queue:
            x, y = queue.popleft()
            for nx in range(x - 1, x + 2):
                for ny in range(y - 1, y + 2):
                    neighbour = (nx, ny)
                    if neighbour != (x, y) and neighbour in opaque and neighbour not in seen:
                        seen.add(neighbour); component.add(neighbour); queue.append(neighbour)
        if len(component) >= minimum:
            retained.update(component)
    protected = set()
    for x, y in retained:
        protected.update((nx, ny) for nx in range(max(0, x - 2), min(width, x + 3)) for ny in range(max(0, y - 2), min(height, y + 3)))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            opacity = pixels[x, y][3]
            detached_opaque = opacity >= 128 and (x, y) not in retained
            detached_edge = 0 < opacity < 128 and (x, y) not in protected
            if detached_opaque or detached_edge:
                pixels[x, y] = (pixels[x, y][0], pixels[x, y][1], pixels[x, y][2], 0)
    return image


def decontaminate_opaque_edges(image, radius=3):
    source = image.copy()
    source_pixels, pixels = source.load(), image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            opacity = source_pixels[x, y][3]
            if not 0 < opacity < 224:
                continue
            neighbours = []
            for nx in range(max(0, x - radius), min(width, x + radius + 1)):
                for ny in range(max(0, y - radius), min(height, y + radius + 1)):
                    if source_pixels[nx, ny][3] >= 224:
                        neighbours.append(((nx - x) ** 2 + (ny - y) ** 2, source_pixels[nx, ny]))
            if neighbours:
                _, nearest = min(neighbours, key=lambda item: item[0])
                pixels[x, y] = (nearest[0], nearest[1], nearest[2], opacity)
    return image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--canvas", type=int, default=512)
    parser.add_argument("--max-subject", type=int, default=400)
    parser.add_argument("--min-component", type=int, default=0, help="remove detached alpha components smaller than this many opaque pixels after resizing")
    parser.add_argument("--edge-decontaminate", action="store_true", help="replace RGB contamination on antialiased edges of opaque subjects")
    args = parser.parse_args()

    with Image.open(args.input) as raw:
        image = raw.convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    if not bbox:
        raise SystemExit("input has no visible subject")
    subject = image.crop(bbox)
    subject.thumbnail((args.max_subject, args.max_subject), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (args.canvas, args.canvas), (0, 0, 0, 0))
    left = (args.canvas - subject.width) // 2
    top = (args.canvas - subject.height) // 2
    canvas.alpha_composite(subject, (left, top))
    if args.min_component:
        canvas = remove_small_alpha_components(canvas, args.min_component)
    if args.edge_decontaminate:
        canvas = decontaminate_opaque_edges(canvas)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
    print(f"normalized {output}")


if __name__ == "__main__":
    main()
