#!/usr/bin/env python3
"""Validate MZ spot-icon PNG geometry, alpha, and neutral-grey residue."""
import argparse, json, sys
from pathlib import Path
from PIL import Image

COLORBLOCK_PALETTE = {
    "ink": (6, 36, 70),
    "mustard": (251, 188, 14),
    "rust": (213, 73, 2),
}
STICKER_PAPER = (248, 246, 241)

def _colour_distance(pixel, base):
    return sum((pixel[index] - base[index]) ** 2 for index in range(3)) ** 0.5

def _luma(pixel):
    return 0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]

def _components(mask, width, height):
    seen, sizes = set(), []
    for y in range(height):
        for x in range(width):
            if not mask[y][x] or (x, y) in seen:
                continue
            stack, size = [(x, y)], 0
            seen.add((x, y))
            while stack:
                px, py = stack.pop(); size += 1
                for nx in range(px - 1, px + 2):
                    for ny in range(py - 1, py + 2):
                        if nx == px and ny == py:
                            continue
                        if 0 <= nx < width and 0 <= ny < height and mask[ny][nx] and (nx, ny) not in seen:
                            seen.add((nx, ny)); stack.append((nx, ny))
            sizes.append(size)
    return sizes

def colorblock_errors(image):
    width, height = image.size
    opaque_by_family = {name: [] for name in COLORBLOCK_PALETTE}
    alpha = image.getchannel("A")
    semi_interior = 0
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            red, green, blue, opacity = image.getpixel((x, y))
            if opacity >= 224:
                family, distance = min(((name, _colour_distance((red, green, blue), value)) for name, value in COLORBLOCK_PALETTE.items()), key=lambda item: item[1])
                if distance > 96:
                    return [f"colorblock contains a non-MZ colour family at {x},{y}"]
                opaque_by_family[family].append((red, green, blue))
            elif 48 <= opacity < 224:
                neighbours = [alpha.getpixel((x + dx, y + dy)) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))]
                if all(value >= 224 for value in neighbours):
                    semi_interior += 1
    errors = []
    if semi_interior:
        errors.append(f"colorblock contains {semi_interior} interior semi-transparent pixels")
    for family, pixels in opaque_by_family.items():
        if not pixels:
            continue
        base = COLORBLOCK_PALETTE[family]
        maximum_deviation = max(abs(_luma(pixel) - _luma(base)) / max(1, _luma(base)) * 100 for pixel in pixels)
        if maximum_deviation > 12.25:
            errors.append(f"{family} tonal variation exceeds the 12% Colorblock limit")
    mask = [[alpha.getpixel((x, y)) >= 128 for x in range(width)] for y in range(height)]
    fragments = [size for size in _components(mask, width, height) if size < 16]
    if fragments:
        errors.append(f"colorblock contains detached alpha fragments: {len(fragments)}")
    return errors

def voxel_errors(image):
    width, height = image.size
    alpha = image.getchannel("A")
    mask = [[alpha.getpixel((x, y)) >= 128 for x in range(width)] for y in range(height)]
    points = [(x, y) for y in range(height) for x in range(width) if mask[y][x]]
    if not points: return ["no opaque voxel subject"]
    seen, components = set(), []
    for point in points:
        if point in seen: continue
        stack, size = [point], 0; seen.add(point)
        while stack:
            x, y = stack.pop(); size += 1
            for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0 <= nx < width and 0 <= ny < height and mask[ny][nx] and (nx,ny) not in seen:
                    seen.add((nx,ny)); stack.append((nx,ny))
        components.append(size)
    errors = []
    if sum(size >= 24 for size in components) != 1: errors.append("voxel subject must have one major opaque component")
    bbox = alpha.getbbox()
    if bbox:
        left, top, right, bottom = bbox
        exterior, stack = set(), []
        for x in range(left, right): stack.extend([(x, top), (x, bottom-1)])
        for y in range(top, bottom): stack.extend([(left, y), (right-1, y)])
        while stack:
            x, y = stack.pop()
            if not (left <= x < right and top <= y < bottom) or (x, y) in exterior or mask[y][x]: continue
            exterior.add((x, y)); stack.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
        holes = sum(1 for y in range(top, bottom) for x in range(left, right) if not mask[y][x] and (x, y) not in exterior)
        if holes >= 16: errors.append(f"voxel subject has internal transparent holes: {holes} pixels")
    magenta = sum(1 for red, green, blue, value in image.getdata() if value >= 32 and red >= 180 and blue >= 180 and green <= 100)
    if magenta >= 16: errors.append(f"voxel subject has chroma-key residue: {magenta} pixels")
    return errors

def isometric_errors(image):
    alpha = image.getchannel("A")
    width, height = image.size
    exterior, stack = set(), []
    for x in range(width): stack.extend(((x, 0), (x, height - 1)))
    for y in range(height): stack.extend(((0, y), (width - 1, y)))
    while stack:
        x, y = stack.pop()
        if not (0 <= x < width and 0 <= y < height) or (x, y) in exterior or alpha.getpixel((x, y)) >= 32: continue
        exterior.add((x, y)); stack.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
    neutral_fringe = 0
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            red, green, blue, opacity = image.getpixel((x, y))
            average = (red + green + blue) / 3
            neighbours = [(x + dx, y + dy) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))]
            neutral = max(red, green, blue) - min(red, green, blue) <= 16 and 80 <= average <= 180
            if 32 <= opacity and any(point in exterior for point in neighbours) and neutral:
                neutral_fringe += 1
    mask = [[alpha.getpixel((x, y)) >= 32 for x in range(width)] for y in range(height)]
    fragments = [size for size in _components(mask, width, height) if size < 16]
    errors = []
    if neutral_fringe > 48:
        errors.append(f"isometric contains external neutral-grey fringe or pseudo-shadow: {neutral_fringe} pixels")
    if fragments:
        errors.append(f"isometric contains detached alpha fragments: {len(fragments)}")
    return errors

def sticker_errors(image):
    width, height = image.size
    alpha = image.getchannel("A")
    visible = [(x, y) for y in range(height) for x in range(width) if alpha.getpixel((x, y)) >= 128]
    if not visible:
        return ["no visible Sticker subject"]
    paper = set()
    coloured = []
    for x, y in visible:
        red, green, blue, opacity = image.getpixel((x, y))
        if opacity >= 224 and _colour_distance((red, green, blue), STICKER_PAPER) <= 48:
            paper.add((x, y))
        elif opacity >= 224 and max(red, green, blue) - min(red, green, blue) >= 32:
            coloured.append((x, y))
    errors = []
    paper_ratio = len(paper) / len(visible)
    if not .06 <= paper_ratio <= .75:
        errors.append(f"Sticker warm-white border coverage is outside the expected range: {paper_ratio:.3f}")
    exposed = 0
    for x, y in coloured:
        if any(alpha.getpixel((nx, ny)) < 32 for nx in range(max(0, x - 2), min(width, x + 3)) for ny in range(max(0, y - 2), min(height, y + 3))):
            exposed += 1
    if exposed:
        errors.append(f"Sticker colour reaches the transparent exterior without a die-cut border: {exposed} pixels")
    mask = [[alpha.getpixel((x, y)) >= 128 for x in range(width)] for y in range(height)]
    components = _components(mask, width, height)
    if sum(size >= 24 for size in components) != 1:
        errors.append("Sticker must have one major connected alpha component")
    if any(size < 16 for size in components):
        errors.append("Sticker contains detached alpha fragments")
    remote_semi = 0
    for y in range(height):
        for x in range(width):
            opacity = alpha.getpixel((x, y))
            if not 32 <= opacity < 224:
                continue
            near_opaque = any(alpha.getpixel((nx, ny)) >= 224 for nx in range(max(0, x - 2), min(width, x + 3)) for ny in range(max(0, y - 2), min(height, y + 3)))
            if not near_opaque:
                remote_semi += 1
    if remote_semi > 24:
        errors.append(f"Sticker contains a detached translucent halo or pseudo-shadow: {remote_semi} pixels")
    return errors

def realistic_errors(image):
    width, height = image.size
    alpha = image.getchannel("A")
    mask = [[alpha.getpixel((x, y)) >= 128 for x in range(width)] for y in range(height)]
    components = _components(mask, width, height)
    errors = []
    if not 1 <= sum(size >= 24 for size in components) <= 3:
        errors.append("Realistic subject must use one to three intentional opaque components")
    fragments = [size for size in components if size < 16]
    if fragments:
        errors.append(f"Realistic subject contains detached alpha fragments: {len(fragments)}")
    bbox = alpha.getbbox()
    if bbox:
        left, top, right, bottom = bbox
        exterior, stack = set(), []
        for x in range(left, right): stack.extend(((x, top), (x, bottom - 1)))
        for y in range(top, bottom): stack.extend(((left, y), (right - 1, y)))
        while stack:
            x, y = stack.pop()
            if not (left <= x < right and top <= y < bottom) or (x, y) in exterior or mask[y][x]: continue
            exterior.add((x, y)); stack.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
        holes = sum(1 for y in range(top, bottom) for x in range(left, right) if not mask[y][x] and (x, y) not in exterior)
        if holes >= 16:
            errors.append(f"Realistic subject has material-erasure holes: {holes} pixels")
    remote_semi = 0
    for y in range(height):
        for x in range(width):
            opacity = alpha.getpixel((x, y))
            if not 32 <= opacity < 224:
                continue
            near_opaque = any(alpha.getpixel((nx, ny)) >= 224 for nx in range(max(0, x - 2), min(width, x + 3)) for ny in range(max(0, y - 2), min(height, y + 3)))
            if not near_opaque:
                remote_semi += 1
    if remote_semi > 24:
        errors.append(f"Realistic subject contains a detached translucent halo or pseudo-shadow: {remote_semi} pixels")
    return errors

def inspect(path, expected=512, style="generic"):
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
    if style == "mz-voxel-macro-v1": errors.extend(voxel_errors(image))
    if style == "mz-colorblock-v1": errors.extend(colorblock_errors(image))
    if style == "mz-isometric-v1": errors.extend(isometric_errors(image))
    if style == "mz-sticker-v1": errors.extend(sticker_errors(image))
    if style == "mz-realistic-v1": errors.extend(realistic_errors(image))
    return {"file": str(path), "errors": errors, "warnings": warnings, "bbox": bbox}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("path"); parser.add_argument("--size", type=int, default=512); parser.add_argument("--style", choices=("generic", "mz-colorblock-v1", "mz-isometric-v1", "mz-voxel-macro-v1", "mz-sticker-v1", "mz-realistic-v1"), default="generic"); parser.add_argument("--json", action="store_true"); args = parser.parse_args()
    target = Path(args.path); files = [target] if target.is_file() else sorted(target.glob("*.png"))
    if not files: print("No PNG files found.", file=sys.stderr); raise SystemExit(1)
    reports = [inspect(file, args.size, args.style) for file in files]
    if args.json: print(json.dumps(reports, indent=2, default=str))
    else:
        for report in reports:
            print(f"{'OK' if not report['errors'] else 'FAIL'}\t{report['file']}")
            for message in report['errors']: print(f"  error: {message}")
            for message in report['warnings']: print(f"  warning: {message}")
    raise SystemExit(1 if any(report['errors'] for report in reports) else 0)
if __name__ == "__main__": main()
