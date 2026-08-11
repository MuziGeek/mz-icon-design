#!/usr/bin/env python3
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
PYTHON = sys.executable

def run(script, *args):
    return subprocess.run([PYTHON, str(ROOT / script), *map(str, args)], text=True, capture_output=True)

VALID_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M4 12h16"/></svg>'

class MzIconDesignTests(unittest.TestCase):
    def test_router(self):
        result = run("route_request.py", "--usage", "navigation", "--size", "24")
        self.assertEqual(json.loads(result.stdout), {"mode": "svg", "style": "mz-line-v1"})
        result = run("route_request.py", "--usage", "isometric product feature", "--concept-count", "9")
        self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-block-v1"})

    def test_svg_validator(self):
        with tempfile.TemporaryDirectory() as temp:
            valid = Path(temp) / "valid.svg"; valid.write_text(VALID_SVG, encoding="utf-8")
            self.assertEqual(run("validate_svg.py", valid).returncode, 0)
            invalid = Path(temp) / "invalid.svg"; invalid.write_text(VALID_SVG.replace('fill="none"', 'fill="red"'), encoding="utf-8")
            self.assertNotEqual(run("validate_svg.py", invalid).returncode, 0)
            forbidden = Path(temp) / "forbidden.svg"; forbidden.write_text(VALID_SVG.replace('</svg>', '<script>bad()</script></svg>'), encoding="utf-8")
            self.assertNotEqual(run("validate_svg.py", forbidden).returncode, 0)

    def test_png_validator_and_qa(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "icons"; folder.mkdir()
            image = Image.new("RGBA", (512, 512), (128, 128, 128, 0))
            for x in range(100, 412):
                for y in range(100, 412): image.putpixel((x, y), (251, 188, 14, 255))
            image.save(folder / "icon-01.png")
            self.assertEqual(run("validate_png.py", folder).returncode, 0)
            qa = Path(temp) / "qa"; self.assertEqual(run("build_png_qa.py", folder, qa).returncode, 0)
            self.assertTrue((qa / "magenta.png").is_file())
            bad = Image.new("RGB", (512, 512), "white"); bad.save(folder / "bad.png")
            self.assertNotEqual(run("validate_png.py", folder).returncode, 0)

    def test_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp); icons = output / "icons"; icons.mkdir()
            (icons / "search.svg").write_text(VALID_SVG, encoding="utf-8")
            create = run("create_manifest.py", output, "--mode", "svg", "--style", "mz-line-v1", "--status", "READY_FOR_REVIEW", "--concept", "search", "--files-dir", "icons")
            self.assertEqual(create.returncode, 0, create.stderr)
            self.assertEqual(run("validate_manifest.py", output / "manifest.json").returncode, 0)

if __name__ == "__main__": unittest.main()
