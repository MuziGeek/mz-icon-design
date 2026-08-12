#!/usr/bin/env python3
"""Choose the deterministic default MZ icon track from explicit request metadata."""
import argparse
import json
import sys
from pathlib import Path

SPOT_WORDS = ("section", "feature", "category", "marketing", "empty state", "spot", "栏目", "营销", "分类", "空状态")
BLOCK_WORDS = ("voxel", "isometric", "block", "体素", "等距", "立体块面")
SOFT_3D_WORDS = ("soft 3d icon", "matte clay icon", "soft-three-quarter icon", "柔和 3d 图标", "哑光黏土图标")
ISOMETRIC_WORDS = ("soft isometric miniature", "soft-isometric miniature", "柔和等距微缩物")
FILLED_WORDS = ("filled ui icon", "solid glyph", "实心 ui 图标", "实心图标")
COLORBLOCK_WORDS = ("colorblock", "contrasting colour blocks", "contrasting color blocks", "撞色块", "色块图标")
VOXEL_MACRO_WORDS = ("macro voxel", "polished acrylic voxel", "宏体素", "抛光亚克力体素")
STICKER_WORDS = ("sticker icon", "die-cut sticker icon", "贴纸图标", "模切贴纸图标")
CARTOON_WORDS = ("cartoon icon", "cartoon icons", "卡通图标")
ANIMAL_BADGE_WORDS = ("animal badge icon", "animal badge icons", "动物徽章图标")
REALISTIC_WORDS = ("realistic object icon", "realistic object icons", "写实物件图标", "写实对象图标")
PROHIBITED_VOXEL_WORDS = ("oreo directed voxel", "oreo palette", "oreo 调色", "oreo 配色")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usage", default="")
    parser.add_argument("--size", type=int, default=0)
    parser.add_argument("--concept-count", type=int, default=1)
    parser.add_argument("--mode", choices=("auto", "svg", "spot"), default="auto")
    parser.add_argument("--style", choices=("", "mz-line-v1", "mz-filled-v1", "mz-crayon-v2", "mz-block-v1", "mz-soft-3d-v1", "mz-colorblock-v1", "mz-isometric-v1", "mz-voxel-macro-v1", "mz-sticker-v1", "mz-cartoon-v1", "mz-animal-badge-v1", "mz-realistic-v1"), default="")
    parser.add_argument("--brief")
    args = parser.parse_args()
    if args.brief:
        snapshot_scripts = Path(__file__).resolve().parents[1] / "references" / "visual-engine" / "scripts"
        sys.path.insert(0, str(snapshot_scripts))
        from engine_lib import ContractError, load_catalog, validate_brief
        try:
            brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
            validate_brief(brief, load_catalog(snapshot_scripts.parent))
        except (OSError, json.JSONDecodeError, ContractError) as exc:
            raise SystemExit(f"invalid MZ visual brief: {exc}") from exc
        if brief.get("status") != "RESOLVED" or brief["target"].get("skill") != "mz-icon-design":
            raise SystemExit("brief does not resolve to mz-icon-design")
        mode = brief["target"].get("mode")
        style = brief["style"]["preset"].get("id")
        if mode not in ("svg", "spot") or style not in ("mz-line-v1", "mz-filled-v1", "mz-crayon-v2", "mz-block-v1", "mz-soft-3d-v1", "mz-colorblock-v1", "mz-isometric-v1", "mz-voxel-macro-v1", "mz-sticker-v1", "mz-cartoon-v1", "mz-animal-badge-v1", "mz-realistic-v1"):
            raise SystemExit("brief contains an unsupported Icon route")
        print(json.dumps({"mode": mode, "style": style}, ensure_ascii=False))
        return
    text = args.usage.lower()
    if any(word in text for word in PROHIBITED_VOXEL_WORDS):
        raise SystemExit("requested third-party voxel palette or visual signature is not supported")
    if args.mode != "auto":
        mode = args.mode
    elif args.size and args.size <= 32:
        mode = "svg"
    elif any(word in text for word in SPOT_WORDS) or args.concept_count > 1:
        mode = "spot"
    else:
        mode = "svg"
    if args.style:
        style = args.style
    elif any(word in text for word in FILLED_WORDS):
        style = "mz-filled-v1"
    elif any(word in text for word in SOFT_3D_WORDS):
        style = "mz-soft-3d-v1"
    elif any(word in text for word in ISOMETRIC_WORDS):
        style = "mz-isometric-v1"
    elif any(word in text for word in COLORBLOCK_WORDS):
        style = "mz-colorblock-v1"
    elif any(word in text for word in VOXEL_MACRO_WORDS):
        style = "mz-voxel-macro-v1"
    elif any(word in text for word in STICKER_WORDS):
        style = "mz-sticker-v1"
    elif any(word in text for word in CARTOON_WORDS):
        style = "mz-cartoon-v1"
    elif any(word in text for word in ANIMAL_BADGE_WORDS):
        style = "mz-animal-badge-v1"
    elif any(word in text for word in REALISTIC_WORDS):
        style = "mz-realistic-v1"
    elif mode == "svg":
        style = "mz-line-v1"
    elif any(word in text for word in BLOCK_WORDS):
        style = "mz-block-v1"
    else:
        style = "mz-crayon-v2"
    if style in ("mz-line-v1", "mz-filled-v1"): mode = "svg"
    if style in ("mz-crayon-v2", "mz-block-v1", "mz-soft-3d-v1", "mz-colorblock-v1", "mz-isometric-v1", "mz-voxel-macro-v1", "mz-sticker-v1", "mz-cartoon-v1", "mz-animal-badge-v1", "mz-realistic-v1"): mode = "spot"
    print(json.dumps({"mode": mode, "style": style}, ensure_ascii=False))

if __name__ == "__main__": main()
