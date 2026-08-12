#!/usr/bin/env python3
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
PYTHON = sys.executable

def run(script, *args):
    return subprocess.run([PYTHON, str(ROOT / script), *map(str, args)], text=True, capture_output=True)

VALID_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M4 12h16"/></svg>'
FILLED_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" stroke="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 4h14v16H5z"/></svg>'

class MzIconDesignTests(unittest.TestCase):
    def test_router(self):
        result = run("route_request.py", "--usage", "navigation", "--size", "24")
        self.assertEqual(json.loads(result.stdout), {"mode": "svg", "style": "mz-line-v1"})
        result = run("route_request.py", "--usage", "solid glyph for mobile navigation", "--size", "24")
        self.assertEqual(json.loads(result.stdout), {"mode": "svg", "style": "mz-filled-v1"})
        result = run("route_request.py", "--usage", "isometric product feature", "--concept-count", "9")
        self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-block-v1"})
        result = run("route_request.py", "--usage", "matte clay icon for a product feature")
        self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-soft-3d-v1"})
        result = run("route_request.py", "--usage", "contrasting colour blocks for product sections", "--concept-count", "9")
        self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-colorblock-v1"})
        result = run("route_request.py", "--usage", "soft isometric miniature for product feature icons", "--concept-count", "9")
        self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-isometric-v1"})
        macro = run("route_request.py", "--usage", "macro voxel icons with transparent background", "--concept-count", "9")
        self.assertEqual(json.loads(macro.stdout), {"mode": "spot", "style": "mz-voxel-macro-v1"})
        sticker = run("route_request.py", "--usage", "die-cut sticker icon")
        self.assertEqual(json.loads(sticker.stdout), {"mode": "spot", "style": "mz-sticker-v1"})
        explicit_sticker = run("route_request.py", "--style", "mz-sticker-v1")
        self.assertEqual(json.loads(explicit_sticker.stdout), {"mode": "spot", "style": "mz-sticker-v1"})
        cartoon = run("route_request.py", "--usage", "cartoon icon")
        self.assertEqual(json.loads(cartoon.stdout), {"mode": "spot", "style": "mz-cartoon-v1"})
        explicit_cartoon = run("route_request.py", "--style", "mz-cartoon-v1")
        self.assertEqual(json.loads(explicit_cartoon.stdout), {"mode": "spot", "style": "mz-cartoon-v1"})
        animal_badge = run("route_request.py", "--usage", "animal badge icon")
        self.assertEqual(json.loads(animal_badge.stdout), {"mode": "spot", "style": "mz-animal-badge-v1"})
        explicit_animal_badge = run("route_request.py", "--style", "mz-animal-badge-v1")
        self.assertEqual(json.loads(explicit_animal_badge.stdout), {"mode": "spot", "style": "mz-animal-badge-v1"})
        realistic = run("route_request.py", "--usage", "realistic object icon")
        self.assertEqual(json.loads(realistic.stdout), {"mode": "spot", "style": "mz-realistic-v1"})
        explicit_realistic = run("route_request.py", "--style", "mz-realistic-v1")
        self.assertEqual(json.loads(explicit_realistic.stdout), {"mode": "spot", "style": "mz-realistic-v1"})
        default_spot = run("route_request.py", "--usage", "product categories", "--concept-count", "9")
        self.assertEqual(json.loads(default_spot.stdout), {"mode": "spot", "style": "mz-crayon-v2"})
        bare_voxel = run("route_request.py", "--usage", "voxel feature icons", "--concept-count", "9")
        self.assertEqual(json.loads(bare_voxel.stdout), {"mode": "spot", "style": "mz-block-v1"})
        oreo = run("route_request.py", "--usage", "Oreo directed voxel icon", "--concept-count", "9")
        self.assertNotEqual(oreo.returncode, 0)
        self.assertIn("third-party voxel palette", oreo.stderr)
        with tempfile.TemporaryDirectory() as temp:
            brief = Path(temp) / "brief.json"
            brief.write_text(json.dumps({
                "format": "mz.visual-brief/1", "engineVersion": "1.2.0", "status": "RESOLVED",
                "request": {"summary": "search"}, "intent": {}, "asset": {"profile": "icon-ui"},
                "style": {"preset": {"id": "mz-filled-v1"}}, "target": {"skill": "mz-icon-design", "mode": "svg"},
                "generation": {}, "provenance": {}
            }), encoding="utf-8")
            result = run("route_request.py", "--brief", brief)
            self.assertEqual(json.loads(result.stdout), {"mode": "svg", "style": "mz-filled-v1"})
            self.assertEqual(run("validate_visual_brief.py", brief).returncode, 0)
            brief.write_text(json.dumps({
                "format": "mz.visual-brief/1", "engineVersion": "1.2.0", "status": "RESOLVED",
                "request": {"summary": "soft isometric miniature"}, "intent": {}, "asset": {"profile": "icon-spot"},
                "style": {"preset": {"id": "mz-isometric-v1"}}, "target": {"skill": "mz-icon-design", "mode": "spot"},
                "generation": {}, "provenance": {}
            }), encoding="utf-8")
            result = run("route_request.py", "--brief", brief)
            self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-isometric-v1"})
            self.assertEqual(run("validate_visual_brief.py", brief).returncode, 0)
            brief.write_text(json.dumps({
                "format": "mz.visual-brief/1", "engineVersion": "1.2.0", "status": "RESOLVED",
                "request": {"summary": "colour blocks"}, "intent": {}, "asset": {"profile": "icon-spot"},
                "style": {"preset": {"id": "mz-colorblock-v1"}}, "target": {"skill": "mz-icon-design", "mode": "spot"},
                "generation": {}, "provenance": {}
            }), encoding="utf-8")
            result = run("route_request.py", "--brief", brief)
            self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-colorblock-v1"})
            self.assertEqual(run("validate_visual_brief.py", brief).returncode, 0)
            brief.write_text(json.dumps({
                "format": "mz.visual-brief/1", "engineVersion": "1.2.0", "status": "RESOLVED",
                "request": {"summary": "die-cut sticker icon"}, "intent": {}, "asset": {"profile": "icon-spot"},
                "style": {"preset": {"id": "mz-sticker-v1"}}, "target": {"skill": "mz-icon-design", "mode": "spot"},
                "generation": {}, "provenance": {}
            }), encoding="utf-8")
            result = run("route_request.py", "--brief", brief)
            self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-sticker-v1"})
            self.assertEqual(run("validate_visual_brief.py", brief).returncode, 0)
            brief.write_text(json.dumps({
                "format": "mz.visual-brief/1", "engineVersion": "1.2.0", "status": "RESOLVED",
                "request": {"summary": "cartoon icon"}, "intent": {}, "asset": {"profile": "icon-spot"},
                "style": {"preset": {"id": "mz-cartoon-v1"}}, "target": {"skill": "mz-icon-design", "mode": "spot"},
                "generation": {}, "provenance": {}
            }), encoding="utf-8")
            result = run("route_request.py", "--brief", brief)
            self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-cartoon-v1"})
            self.assertEqual(run("validate_visual_brief.py", brief).returncode, 0)
            brief.write_text(json.dumps({
                "format": "mz.visual-brief/1", "engineVersion": "1.2.0", "status": "RESOLVED",
                "request": {"summary": "animal badge icon"}, "intent": {}, "asset": {"profile": "icon-spot"},
                "style": {"preset": {"id": "mz-animal-badge-v1"}}, "target": {"skill": "mz-icon-design", "mode": "spot"},
                "generation": {}, "provenance": {}
            }), encoding="utf-8")
            result = run("route_request.py", "--brief", brief)
            self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-animal-badge-v1"})
            self.assertEqual(run("validate_visual_brief.py", brief).returncode, 0)
            brief.write_text(json.dumps({
                "format": "mz.visual-brief/1", "engineVersion": "1.2.0", "status": "RESOLVED",
                "request": {"summary": "realistic object icon"}, "intent": {}, "asset": {"profile": "icon-spot"},
                "style": {"preset": {"id": "mz-realistic-v1"}}, "target": {"skill": "mz-icon-design", "mode": "spot"},
                "generation": {}, "provenance": {}
            }), encoding="utf-8")
            result = run("route_request.py", "--brief", brief)
            self.assertEqual(json.loads(result.stdout), {"mode": "spot", "style": "mz-realistic-v1"})
            self.assertEqual(run("validate_visual_brief.py", brief).returncode, 0)

    def test_engine_snapshot(self):
        snapshot = ROOT.parent / "references" / "visual-engine"
        result = subprocess.run([PYTHON, str(snapshot / "scripts" / "verify_snapshot.py"), str(snapshot)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_svg_validator(self):
        with tempfile.TemporaryDirectory() as temp:
            valid = Path(temp) / "valid.svg"; valid.write_text(VALID_SVG, encoding="utf-8")
            self.assertEqual(run("validate_svg.py", valid).returncode, 0)
            invalid = Path(temp) / "invalid.svg"; invalid.write_text(VALID_SVG.replace('fill="none"', 'fill="red"'), encoding="utf-8")
            self.assertNotEqual(run("validate_svg.py", invalid).returncode, 0)
            forbidden = Path(temp) / "forbidden.svg"; forbidden.write_text(VALID_SVG.replace('</svg>', '<script>bad()</script></svg>'), encoding="utf-8")
            self.assertNotEqual(run("validate_svg.py", forbidden).returncode, 0)
            filled = Path(temp) / "filled.svg"; filled.write_text(FILLED_SVG, encoding="utf-8")
            self.assertEqual(run("validate_svg.py", filled, "--style", "mz-filled-v1").returncode, 0)
            self.assertNotEqual(run("validate_svg.py", filled).returncode, 0)
            self.assertNotEqual(run("validate_svg.py", valid, "--style", "mz-filled-v1").returncode, 0)

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

    def test_voxel_png_validator_rejects_holes_islands_and_chroma(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            clean = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); ImageDraw.Draw(clean).rectangle((120, 120, 390, 390), fill=(45, 90, 170, 255)); clean.save(folder / "clean.png")
            self.assertEqual(run("validate_png.py", folder / "clean.png", "--style", "mz-voxel-macro-v1").returncode, 0)
            donut = clean.copy(); ImageDraw.Draw(donut).rectangle((220, 220, 290, 290), fill=(0, 0, 0, 0)); donut.save(folder / "donut.png")
            self.assertNotEqual(run("validate_png.py", folder / "donut.png", "--style", "mz-voxel-macro-v1").returncode, 0)
            island = clean.copy(); ImageDraw.Draw(island).rectangle((20, 20, 60, 60), fill=(45, 90, 170, 255)); island.save(folder / "island.png")
            self.assertNotEqual(run("validate_png.py", folder / "island.png", "--style", "mz-voxel-macro-v1").returncode, 0)
            magenta = clean.copy(); ImageDraw.Draw(magenta).rectangle((200, 200, 250, 250), fill=(255, 0, 255, 255)); magenta.save(folder / "magenta.png")
            self.assertNotEqual(run("validate_png.py", folder / "magenta.png", "--style", "mz-voxel-macro-v1").returncode, 0)

    def test_colorblock_png_validator_accepts_mz_palette_and_rejects_fourth_colour(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            valid = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); ImageDraw.Draw(valid).rounded_rectangle((100, 100, 412, 412), radius=36, fill=(6, 36, 70, 255)); valid.save(folder / "valid.png")
            self.assertEqual(run("validate_png.py", folder / "valid.png", "--style", "mz-colorblock-v1").returncode, 0)
            fourth = valid.copy(); ImageDraw.Draw(fourth).rectangle((220, 220, 300, 300), fill=(30, 220, 90, 255)); fourth.save(folder / "fourth.png")
            self.assertNotEqual(run("validate_png.py", folder / "fourth.png", "--style", "mz-colorblock-v1").returncode, 0)
            tones = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); draw = ImageDraw.Draw(tones)
            for y in range(100, 412):
                value = round(1.04 * 70 - 0.08 * 70 * (y - 100) / 311)
                draw.line((100, y, 411, y), fill=(round(value * 6 / 70), round(value * 36 / 70), value, 255))
            tones.save(folder / "tones.png")
            self.assertEqual(run("validate_png.py", folder / "tones.png", "--style", "mz-colorblock-v1").returncode, 0)

    def test_isometric_png_validator_rejects_neutral_shadow_and_fragments(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            valid = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); ImageDraw.Draw(valid).rounded_rectangle((120, 100, 390, 370), radius=28, fill=(6, 36, 70, 255)); valid.save(folder / "valid.png")
            self.assertEqual(run("validate_png.py", folder / "valid.png", "--style", "mz-isometric-v1").returncode, 0)
            shadow = valid.copy(); ImageDraw.Draw(shadow).ellipse((150, 385, 360, 410), fill=(128, 128, 128, 128)); shadow.save(folder / "shadow.png")
            self.assertNotEqual(run("validate_png.py", folder / "shadow.png", "--style", "mz-isometric-v1").returncode, 0)
            fragment = valid.copy(); ImageDraw.Draw(fragment).rectangle((30, 30, 32, 32), fill=(6, 36, 70, 80)); fragment.save(folder / "fragment.png")
            self.assertNotEqual(run("validate_png.py", folder / "fragment.png", "--style", "mz-isometric-v1").returncode, 0)

    def test_sticker_png_validator_requires_a_continuous_die_cut_border(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            valid = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); draw = ImageDraw.Draw(valid)
            draw.rounded_rectangle((90, 90, 422, 422), radius=70, fill=(248, 246, 241, 255))
            draw.rounded_rectangle((125, 125, 387, 387), radius=48, fill=(6, 36, 70, 255))
            valid.save(folder / "valid.png")
            self.assertEqual(run("validate_png.py", folder / "valid.png", "--style", "mz-sticker-v1").returncode, 0)
            exposed = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); ImageDraw.Draw(exposed).rounded_rectangle((90, 90, 422, 422), radius=70, fill=(6, 36, 70, 255)); exposed.save(folder / "exposed.png")
            self.assertNotEqual(run("validate_png.py", folder / "exposed.png", "--style", "mz-sticker-v1").returncode, 0)
            shadow = valid.copy(); ImageDraw.Draw(shadow).ellipse((120, 440, 392, 462), fill=(80, 80, 80, 96)); shadow.save(folder / "shadow.png")
            self.assertNotEqual(run("validate_png.py", folder / "shadow.png", "--style", "mz-sticker-v1").returncode, 0)

    def test_realistic_png_validator_rejects_material_holes_fragments_and_halo(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            valid = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); ImageDraw.Draw(valid).rounded_rectangle((120, 90, 392, 422), radius=52, fill=(82, 96, 108, 255)); valid.save(folder / "valid.png")
            self.assertEqual(run("validate_png.py", folder / "valid.png", "--style", "mz-realistic-v1").returncode, 0)
            hole = valid.copy(); ImageDraw.Draw(hole).ellipse((220, 210, 290, 280), fill=(0, 0, 0, 0)); hole.save(folder / "hole.png")
            self.assertNotEqual(run("validate_png.py", folder / "hole.png", "--style", "mz-realistic-v1").returncode, 0)
            fragment = valid.copy(); ImageDraw.Draw(fragment).rectangle((30, 30, 32, 32), fill=(82, 96, 108, 255)); fragment.save(folder / "fragment.png")
            self.assertNotEqual(run("validate_png.py", folder / "fragment.png", "--style", "mz-realistic-v1").returncode, 0)
            halo = valid.copy(); ImageDraw.Draw(halo).ellipse((140, 440, 372, 458), fill=(80, 80, 80, 96)); halo.save(folder / "halo.png")
            self.assertNotEqual(run("validate_png.py", folder / "halo.png", "--style", "mz-realistic-v1").returncode, 0)

    def test_nonconforming_sheet_cuts(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "sheet.png"; output = Path(temp) / "icons"
            image = Image.new("RGB", (400, 400), (128, 128, 128)); draw = ImageDraw.Draw(image)
            columns, rows = [0, 110, 220, 330, 400], [0, 150, 280, 400]
            for index in range(9):
                row, column = divmod(index, 4)
                left, top = columns[column] + 18, rows[row] + 18
                draw.rectangle((left, top, left + 42, top + 42), fill=(251, 188, 14))
            image.save(source)
            result = run("slice_sheet.py", source, output, "--count", "9", "--grid", "4", "--rows", "3", "--row-cuts", "0,150,280,400", "--column-cuts", "0,110,220,330,400", "--background", "#808080")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(run("validate_png.py", output).returncode, 0)

    def test_realistic_sheet_cut_preserves_neutral_subject_material(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "sheet.png"; output = Path(temp) / "icons"
            image = Image.new("RGB", (300, 300), (128, 128, 128)); ImageDraw.Draw(image).rounded_rectangle((80, 70, 220, 230), radius=30, fill=(72, 72, 72)); image.save(source)
            result = run("slice_sheet.py", source, output, "--count", "1", "--grid", "1", "--rows", "1", "--threshold", "14", "--preserve-neutral-materials")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            alpha = Image.open(output / "icon-01.png").convert("RGBA").getchannel("A")
            self.assertGreater(sum(value >= 224 for value in alpha.getdata()), 40000)

    def test_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp); icons = output / "icons"; icons.mkdir()
            (icons / "search.svg").write_text(VALID_SVG, encoding="utf-8")
            create = run("create_manifest.py", output, "--mode", "svg", "--style", "mz-line-v1", "--status", "READY_FOR_REVIEW", "--concept", "search", "--files-dir", "icons")
            self.assertEqual(create.returncode, 0, create.stderr)
            self.assertEqual(run("validate_manifest.py", output / "manifest.json").returncode, 0)

if __name__ == "__main__": unittest.main()
