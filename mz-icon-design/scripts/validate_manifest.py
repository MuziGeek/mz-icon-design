#!/usr/bin/env python3
"""Validate the portable subset of the mz.icon-batch/1 manifest contract."""
import argparse, hashlib, json, sys
from pathlib import Path

STATUSES = {"DRAFT", "VALIDATION_FAILED", "GENERATION_BLOCKED", "READY_FOR_REVIEW"}
STYLES = {"mz-line-v1", "mz-filled-v1", "mz-crayon-base-v1", "mz-block-v1", "mz-soft-3d-v1", "mz-colorblock-v1", "mz-isometric-v1", "mz-voxel-macro-v1", "mz-sticker-v1", "mz-cartoon-v1", "mz-animal-badge-v1", "mz-realistic-v1"}
def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("manifest"); args = parser.parse_args()
    path = Path(args.manifest); data = json.loads(path.read_text(encoding="utf-8")); errors = []
    if data.get("schema") != "mz.icon-batch/1": errors.append("schema must be mz.icon-batch/1")
    if data.get("status") not in STATUSES: errors.append("invalid status")
    if data.get("mode") not in {"svg", "spot"}: errors.append("invalid mode")
    style = data.get("style"); extension = data.get("extension")
    extension_style = (
        isinstance(style, str) and isinstance(extension, dict)
        and isinstance(extension.get("namespace"), str)
        and style.startswith(f"{extension['namespace']}-")
        and all(isinstance(extension.get(key), str) and extension.get(key) for key in ("id", "version", "manifestHash"))
        and len(extension.get("manifestHash", "")) == 64
    )
    if style not in STYLES and not extension_style: errors.append("invalid style or missing namespaced Extension provenance")
    concepts = data.get("concepts");
    if not isinstance(concepts, list) or not 1 <= len(concepts) <= 16: errors.append("concepts must contain 1-16 entries")
    files = data.get("output", {}).get("files")
    if not isinstance(files, list) or not files: errors.append("output.files must be non-empty")
    else:
        for file in files:
            target = (path.parent / file.get("path", "")).resolve()
            if not target.is_file(): errors.append(f"missing output file: {file.get('path')}")
            elif file.get("sha256") != sha256(target): errors.append(f"sha256 mismatch: {file.get('path')}")
    if errors:
        for error in errors: print(f"error: {error}")
        raise SystemExit(1)
    print(f"OK\t{path}")
if __name__ == "__main__": main()
