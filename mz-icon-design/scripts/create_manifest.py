#!/usr/bin/env python3
"""Create a portable mz.icon-batch/1 manifest for an already-generated output directory."""
import argparse, hashlib, json
from pathlib import Path

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("output_dir")
    parser.add_argument("--mode", choices=("svg", "spot"), required=True)
    parser.add_argument("--style", choices=("mz-line-v1", "mz-crayon-v2", "mz-block-v1"), required=True)
    parser.add_argument("--status", choices=("DRAFT", "VALIDATION_FAILED", "GENERATION_BLOCKED", "READY_FOR_REVIEW"), default="DRAFT")
    parser.add_argument("--concept", action="append", required=True); parser.add_argument("--files-dir", default=".")
    args = parser.parse_args(); output = Path(args.output_dir).resolve(); files_root = (output / args.files_dir).resolve()
    suffix = ".svg" if args.mode == "svg" else ".png"; files = sorted(files_root.rglob(f"*{suffix}"))
    if not files: parser.error(f"no {suffix} files in {files_root}")
    payload = {"schema": "mz.icon-batch/1", "status": args.status, "mode": args.mode, "style": args.style, "concepts": args.concept, "output": {"directory": str(output), "files": [{"path": str(path.relative_to(output)).replace('\\\\', '/'), "sha256": digest(path)} for path in files]}, "validation": {"manifest": "generated locally; run validate_manifest.py after any change"}}
    target = output / "manifest.json"; target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)
if __name__ == "__main__": main()
