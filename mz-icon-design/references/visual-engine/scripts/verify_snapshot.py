#!/usr/bin/env python3
"""Verify an exported Engine snapshot without accessing its source repository."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine_lib import ContractError, digest, tree_hash


def verify(snapshot: Path) -> dict:
    manifest_file = snapshot / "engine-snapshot.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest.get("format") != "mz.engine-snapshot/1":
        raise ContractError("invalid snapshot format")
    files = []
    for entry in manifest.get("files", []):
        file = snapshot / entry["path"]
        if not file.is_file() or digest(file) != entry.get("sha256"):
            raise ContractError(f"snapshot file hash mismatch: {entry.get('path')}")
        files.append(file)
    if manifest.get("snapshotHash") != tree_hash(snapshot, files):
        raise ContractError("snapshot aggregate hash mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot")
    args = parser.parse_args()
    try:
        manifest = verify(Path(args.snapshot))
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"INVALID: {exc}")
        return 1
    print(f"VALID {manifest['target']} snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
