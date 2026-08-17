#!/usr/bin/env python3
"""Validate one public MZ Skill repository and its release manifest."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ID = ROOT.name
PAYLOAD = ROOT / SKILL_ID
MANIFEST = ROOT / "PUBLIC_MANIFEST.json"
ALLOWED_ROOTS = {
    ".gitattributes",
    ".github",
    ".gitignore",
    "ASSET_LICENSE.md",
    "LICENSE",
    "NOTICE.md",
    "PUBLIC_MANIFEST.json",
    "README.md",
    "README.zh-CN.md",
    "docs",
    SKILL_ID,
    "tools",
}
FORBIDDEN_PARTS = {"raw", "rejected", "evaluation", "__pycache__", ".pytest_cache"}
BINARY_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
TEXT_NAMES = {"LICENSE", ".gitignore", ".gitattributes"}
TEXT_EXTENSIONS = {
    ".css", ".html", ".js", ".json", ".md", ".mjs", ".ps1", ".py",
    ".svg", ".toml", ".txt", ".yaml", ".yml",
}
FORBIDDEN_TEXT = (
    (re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[a-z0-9_\-]{16,}"), "possible secret"),
    (re.compile(r"(?i)[a-z]:\\(?:users|gitproject|muzi)\\", re.ASCII), "Windows absolute path"),
    (re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"), "email address"),
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "Chinese mobile number"),
)


def repository_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.relative_to(ROOT).parts
        and "release" not in path.relative_to(ROOT).parts
        and not FORBIDDEN_PARTS.intersection(part.lower() for part in path.relative_to(ROOT).parts)
    )


def normalized_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def tree_hash() -> str:
    rows: list[str] = []
    paths = (item for item in repository_files() if PAYLOAD in item.parents)
    for path in sorted(paths, key=lambda item: item.relative_to(PAYLOAD).as_posix()):
        relative = path.relative_to(PAYLOAD).as_posix()
        digest = hashlib.sha256(normalized_bytes(path)).hexdigest()
        rows.append(f"{relative}\t{digest}\n")
    return hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()


def validate_markdown_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        clean = target.split("#", 1)[0]
        if not clean or "://" in clean or clean.startswith("mailto:"):
            continue
        if not (path.parent / clean).resolve().exists():
            errors.append(f"{path.relative_to(ROOT)}: broken local link {target}")


def main() -> int:
    errors: list[str] = []
    if not PAYLOAD.is_dir() or not (PAYLOAD / "SKILL.md").is_file():
        errors.append(f"Missing payload: {SKILL_ID}/SKILL.md")

    files = repository_files()
    for path in files:
        relative = path.relative_to(ROOT)
        if relative.parts[0] not in ALLOWED_ROOTS:
            errors.append(f"Unexpected root path: {relative.as_posix()}")
        lowered = {part.lower() for part in relative.parts}
        if FORBIDDEN_PARTS.intersection(lowered):
            errors.append(f"Forbidden path: {relative.as_posix()}")
        suffix = path.suffix.lower()
        if suffix in BINARY_EXTENSIONS:
            if "assets" not in lowered and "images" not in lowered:
                errors.append(f"Binary outside assets/images: {relative.as_posix()}")
            continue
        if path.name not in TEXT_NAMES and suffix not in TEXT_EXTENSIONS:
            errors.append(f"Undeclared file type: {relative.as_posix()}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern, label in FORBIDDEN_TEXT:
            scan_text = re.sub(r"(?i)\b[0-9a-f]{64}\b", "<sha256>", text) if label == "Chinese mobile number" else text
            if pattern.search(scan_text):
                errors.append(f"{relative.as_posix()}: {label}")
        if suffix == ".md":
            validate_markdown_links(path, errors)

    skill_text = (PAYLOAD / "SKILL.md").read_text(encoding="utf-8")
    if not skill_text.startswith("---\n"):
        errors.append("SKILL.md lacks YAML frontmatter")
    else:
        _, frontmatter, _ = skill_text.split("---\n", 2)
        keys = [line.split(":", 1)[0] for line in frontmatter.splitlines() if ":" in line]
        if keys != ["name", "description"]:
            errors.append("SKILL.md frontmatter keys must be exactly name and description")
        if f"name: {SKILL_ID}" not in frontmatter:
            errors.append("SKILL.md name does not match repository payload")

    agent_text = (PAYLOAD / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for key in ("display_name:", "short_description:", "default_prompt:"):
        if key not in agent_text:
            errors.append(f"agents/openai.yaml lacks {key}")
    if f"Use ${SKILL_ID}" not in agent_text:
        errors.append("agents/openai.yaml default prompt does not invoke this Skill")

    if not (PAYLOAD / "LICENSE").is_file():
        errors.append("Payload lacks bundled LICENSE")

    snapshot = PAYLOAD / "references" / "visual-engine"
    verifier = snapshot / "scripts" / "verify_snapshot.py"
    if not verifier.is_file():
        errors.append("MZ Visual Engine snapshot is missing")
    else:
        result = subprocess.run([sys.executable, str(verifier), str(snapshot)], text=True, capture_output=True)
        if result.returncode:
            errors.append(f"MZ Visual Engine snapshot is invalid: {result.stdout}{result.stderr}".strip())

    for asset_manifest in PAYLOAD.rglob("*.json"):
        try:
            payload = json.loads(asset_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{asset_manifest.relative_to(ROOT)}: invalid JSON: {exc}")
            continue
        distribution = payload.get("distribution") if isinstance(payload, dict) else None
        if distribution is not None:
            if distribution.get("status") != "APPROVED_FOR_SKILL_OPERATION":
                errors.append(f"{asset_manifest.relative_to(ROOT)}: unapproved distribution status")
            if distribution.get("license") != "MZ Reference Asset License 1.0":
                errors.append(f"{asset_manifest.relative_to(ROOT)}: invalid asset license")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("format") != "mz.public-skill/1" or manifest.get("version") != "2.0.0":
        errors.append("PUBLIC_MANIFEST.json has an unexpected format or version")
    if manifest.get("repository") != f"MuziGeek/{SKILL_ID}":
        errors.append("PUBLIC_MANIFEST.json repository mismatch")
    skill = manifest.get("skill", {})
    if skill.get("id") != SKILL_ID or skill.get("directory") != SKILL_ID:
        errors.append("PUBLIC_MANIFEST.json Skill identity mismatch")
    actual_hash = tree_hash()
    if skill.get("treeHash") != actual_hash:
        errors.append(f"Skill tree hash mismatch: expected {actual_hash}")
    release = manifest.get("release", {})
    if release.get("tag") != "v2.0.0" or release.get("artifactChecksumAlgorithm") != "sha256":
        errors.append("PUBLIC_MANIFEST.json release declaration mismatch")
    engine = manifest.get("visualEngine", {})
    if (
        engine.get("version") != "2.0.0"
        or engine.get("snapshotHash") != "222511da454932f546ae71141325edaab91fc3585e65c183f62968a7d2a9ae57"
        or engine.get("sourceCatalogHash") != "2f74eaa8d55b4037b702c200ace510b9b9a7680c861070be0c04ee04e9824ed0"
    ):
        errors.append("PUBLIC_MANIFEST.json Visual Engine declaration mismatch")

    if errors:
        print("PUBLIC VALIDATION FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Public release validation passed: {SKILL_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
