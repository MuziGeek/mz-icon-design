#!/usr/bin/env python3
"""Build contrasting-background and site-size contact sheets for accepted PNG icons."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

BACKGROUNDS = {"magenta": "#FF00FF", "black": "#000000", "cream": "#FDF6E9"}

def load_icons(folder): return [Image.open(path).convert("RGBA") for path in sorted(Path(folder).glob("*.png"))]
def contact(icons, background, scale=1, grid=4):
    cell = 512 * scale; rows = (len(icons) + grid - 1) // grid
    canvas = Image.new("RGBA", (cell * grid, cell * rows), background)
    for index, icon in enumerate(icons):
        item = icon.resize((cell, cell), Image.Resampling.LANCZOS) if scale != 1 else icon
        canvas.alpha_composite(item, ((index % grid) * cell, (index // grid) * cell))
    return canvas
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("icons_dir"); parser.add_argument("output_dir"); args = parser.parse_args()
    icons = load_icons(args.icons_dir)
    if not icons: parser.error("no PNG icons found")
    output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=True)
    for name, background in BACKGROUNDS.items(): contact(icons, background).convert("RGB").save(output / f"{name}.png")
    small = Image.new("RGB", (4 * 96, ((len(icons) + 3) // 4) * (96 + 48)), "#FDF6E9")
    draw = ImageDraw.Draw(small)
    for index, icon in enumerate(icons):
        x, y = (index % 4) * 96, (index // 4) * 144
        small.paste(icon.resize((96, 96), Image.Resampling.LANCZOS), (x, y), icon.resize((96, 96), Image.Resampling.LANCZOS))
        reduced = icon.resize((48, 48), Image.Resampling.LANCZOS)
        small.paste(reduced, (x + 24, y + 96), reduced)
    small.save(output / "site-size.png")
    print(f"Created QA previews in {output}")
if __name__ == "__main__": main()
