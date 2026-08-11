#!/usr/bin/env python3
"""Choose the deterministic default MZ icon track from explicit request metadata."""
import argparse
import json

SPOT_WORDS = ("section", "feature", "category", "marketing", "empty state", "spot", "栏目", "营销", "分类", "空状态")
BLOCK_WORDS = ("voxel", "isometric", "block", "体素", "等距", "立体块面")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usage", default="")
    parser.add_argument("--size", type=int, default=0)
    parser.add_argument("--concept-count", type=int, default=1)
    parser.add_argument("--mode", choices=("auto", "svg", "spot"), default="auto")
    parser.add_argument("--style", choices=("", "mz-line-v1", "mz-crayon-v2", "mz-block-v1"), default="")
    args = parser.parse_args()
    text = args.usage.lower()
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
    elif mode == "svg":
        style = "mz-line-v1"
    elif any(word in text for word in BLOCK_WORDS):
        style = "mz-block-v1"
    else:
        style = "mz-crayon-v2"
    if style == "mz-line-v1": mode = "svg"
    if style in ("mz-crayon-v2", "mz-block-v1"): mode = "spot"
    print(json.dumps({"mode": mode, "style": style}, ensure_ascii=False))

if __name__ == "__main__": main()
