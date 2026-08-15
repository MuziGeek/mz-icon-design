#!/usr/bin/env python3
"""Build a deterministic release archive for an MZ public Skill repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "PUBLIC_MANIFEST.json"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}
EXCLUDED_NAMES = {".DS_Store"}


def normalized_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def payload_files(payload: Path) -> list[Path]:
    files: list[Path] = []
    for path in payload.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(payload)
        if path.name in EXCLUDED_NAMES or EXCLUDED_PARTS.intersection(relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"release payload cannot contain symlinks: {relative.as_posix()}")
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(payload).as_posix())


def write_archive(archive: Path, payload: Path, skill_id: str) -> None:
    temporary = archive.with_suffix(archive.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    with zipfile.ZipFile(
        temporary,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as bundle:
        for path in payload_files(payload):
            relative = path.relative_to(payload).as_posix()
            info = zipfile.ZipInfo(f"{skill_id}/{relative}", ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.flag_bits |= 0x800
            bundle.writestr(info, normalized_bytes(path), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    os.replace(temporary, archive)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "release")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    skill = manifest.get("skill", {})
    release = manifest.get("release", {})
    skill_id = skill.get("id")
    directory = skill.get("directory")
    version = manifest.get("version")
    tag = release.get("tag")
    if not all(isinstance(value, str) and value for value in (skill_id, directory, version, tag)):
        print("PUBLIC_MANIFEST.json lacks release identity fields", file=sys.stderr)
        return 1
    if tag != f"v{version}":
        print(f"release tag {tag!r} does not match version {version!r}", file=sys.stderr)
        return 1

    payload = ROOT / directory
    if not (payload / "SKILL.md").is_file():
        print(f"missing Skill payload: {payload}", file=sys.stderr)
        return 1

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"{skill_id}-v{version}.zip"
    checksum = output_dir / f"CHECKSUMS-v{version}.txt"
    write_archive(archive, payload, skill_id)
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum.write_text(f"{archive_hash}  {archive.name}\n", encoding="utf-8", newline="\n")
    print(archive)
    print(checksum)
    print(archive_hash)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
