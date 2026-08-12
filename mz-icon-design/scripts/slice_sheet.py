#!/usr/bin/env python3
"""Slice a 4x4 neutral-grey icon sheet and remove edge-connected background."""
import argparse
from collections import deque
from pathlib import Path
from PIL import Image

def parse_hex(value):
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))

def close(pixel, backgrounds, threshold, preserve_neutral_materials=False):
    if not preserve_neutral_materials and max(pixel[:3]) - min(pixel[:3]) <= 10 and 90 <= sum(pixel[:3]) / 3 <= 180:
        return True
    return any(sum((pixel[index] - background[index]) ** 2 for index in range(3)) <= threshold ** 2 for background in backgrounds)

def clear_background(image, background, threshold, preserve_neutral_materials=False):
    image = image.convert("RGBA")
    pixels, width, height = image.load(), image.width, image.height
    queue, seen = deque(), set()
    for x in range(width): queue.extend(((x, 0), (x, height - 1)))
    for y in range(height): queue.extend(((0, y), (width - 1, y)))
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen or not (0 <= x < width and 0 <= y < height): continue
        seen.add((x, y))
        if not close(pixels[x, y], background, threshold, preserve_neutral_materials): continue
        pixels[x, y] = (pixels[x, y][0], pixels[x, y][1], pixels[x, y][2], 0)
        queue.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
    return image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet"); parser.add_argument("output_dir")
    parser.add_argument("--count", type=int, default=9); parser.add_argument("--grid", type=int, default=4); parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--row-cuts", default="", help="comma-separated source row edges for a nonconforming calibration sheet")
    parser.add_argument("--column-cuts", default="", help="comma-separated source column edges for a nonconforming calibration sheet")
    parser.add_argument("--size", type=int, default=512); parser.add_argument("--background", default="auto")
    parser.add_argument("--threshold", type=int, default=44)
    parser.add_argument("--preserve-neutral-materials", action="store_true", help="only remove edge-connected pixels close to the sampled background; use for Realistic objects with grey materials")
    args = parser.parse_args()
    if not 1 <= args.count <= args.grid * args.rows: parser.error("count must fit the sheet grid")
    sheet = Image.open(args.sheet).convert("RGBA")
    if sheet.width != sheet.height: parser.error("sheet must be square")
    output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=True)
    row_cuts = [int(value) for value in args.row_cuts.split(",") if value] if args.row_cuts else []
    column_cuts = [int(value) for value in args.column_cuts.split(",") if value] if args.column_cuts else []
    if row_cuts and (len(row_cuts) != args.rows + 1 or row_cuts[0] != 0 or row_cuts[-1] != sheet.height): parser.error("row-cuts must start at 0, end at sheet height, and define --rows rows")
    if column_cuts and (len(column_cuts) != args.grid + 1 or column_cuts[0] != 0 or column_cuts[-1] != sheet.width): parser.error("column-cuts must start at 0, end at sheet width, and define --grid columns")
    for index in range(args.count):
        row, col = divmod(index, args.grid)
        left, right = (column_cuts[col], column_cuts[col + 1]) if column_cuts else (round(col * sheet.width / args.grid), round((col + 1) * sheet.width / args.grid))
        top, bottom = (row_cuts[row], row_cuts[row + 1]) if row_cuts else (round(row * sheet.height / args.rows), round((row + 1) * sheet.height / args.rows))
        raw_cell = sheet.crop((left, top, right, bottom))
        if args.background == "auto":
            backgrounds = [raw_cell.getpixel(point)[:3] for point in ((0, 0), (raw_cell.width - 1, 0), (0, raw_cell.height - 1), (raw_cell.width - 1, raw_cell.height - 1))]
        else:
            backgrounds = [parse_hex(args.background)]
        cell = clear_background(raw_cell, backgrounds, args.threshold, args.preserve_neutral_materials)
        cell.resize((args.size, args.size), Image.Resampling.LANCZOS).save(output / f"icon-{index + 1:02d}.png")
    print(f"Sliced {args.count} icon(s) to {output}")
if __name__ == "__main__": main()
