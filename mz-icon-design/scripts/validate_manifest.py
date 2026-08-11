#!/usr/bin/env python3
"""Validate the portable subset of the mz.icon-batch/1 manifest contract."""
import argparse, hashlib, json, sys
from pathlib import Path

STATUSES = {"DRAFT", "VALIDATION_FAILED", "GENERATION_BLOCKED", "READY_FOR_REVIEW"}
STYLES = {"mz-line-v1", "mz-crayon-v2", "mz-block-v1"}
def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("manifest"); args = parser.parse_args()
    path = Path(args.manifest); data = json.loads(path.read_text(encoding="utf-8")); errors = []
    if data.get("schema") != "mz.icon-batch/1": errors.append("schema must be mz.icon-batch/1")
    if data.get("status") not in STATUSES: errors.append("invalid status")
    if data.get("mode") not in {"svg", "spot"}: errors.append("invalid mode")
    if data.get("style") not in STYLES: errors.append("invalid style")
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
