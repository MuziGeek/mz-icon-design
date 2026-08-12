#!/usr/bin/env python3
"""Deterministic contracts for MZ Visual Engine v1."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
ENGINE_VERSION = "1.2.0"
VALID_BRIEF_STATUSES = {
    "RESOLVED",
    "STYLE_CONFLICT",
    "UNSUPPORTED_ASSET",
    "UNSUPPORTED_COMBINATION",
    "INVALID_INPUT",
}
CORE_RULES = [
    "one-primary-concept",
    "restraint-and-legible-hierarchy",
    "controlled-human-imperfection",
    "traceable-dimensions-names-versions-and-evidence",
    "original-geometry-prompts-composition-and-assets",
    "user-acceptance-required",
]
PRESET_STATUSES = {"REGISTERED", "READY_FOR_REVIEW", "APPROVED_FOR_SKILL_OPERATION", "RETIRED"}
ADAPTER_STATUSES = {"MAPPED_TO_EXISTING", "CANDIDATE", "REGISTERED"}


class ContractError(ValueError):
    """Raised when an engine contract is structurally invalid."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {path}")
    return value


def normalized_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def digest(path: Path) -> str:
    return hashlib.sha256(normalized_bytes(path)).hexdigest()


def tree_hash(root: Path, files: list[Path]) -> str:
    rows = []
    for file in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        rows.append(f"{file.relative_to(root).as_posix()}\t{digest(file)}\n")
    return hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()


def _load_directory(path: Path) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for file in sorted(path.glob("*.json")):
        item = read_json(file)
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise ContractError(f"missing id: {file}")
        if item_id in values:
            raise ContractError(f"duplicate id {item_id}")
        item["_file"] = file
        values[item_id] = item
    return values


def _load_optional_directory(path: Path) -> dict[str, dict[str, Any]]:
    return _load_directory(path) if path.is_dir() else {}


def load_catalog(root: Path = PACKAGE_ROOT) -> dict[str, Any]:
    catalog = {
        "root": root,
        "schema": read_json(root / "schemas" / "mz-contracts-v1.json"),
        "presets": _load_directory(root / "styles" / "presets"),
        "sources": _load_optional_directory(root / "sources"),
        "adapters": _load_optional_directory(root / "styles" / "adapters"),
        "modifiers": _load_directory(root / "styles" / "modifiers"),
        "profiles": _load_directory(root / "profiles"),
    }
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict[str, Any]) -> None:
    partial_snapshot = (catalog["root"] / "engine-snapshot.json").is_file()
    required = catalog["schema"].get("contracts", {})
    mappings = {
        "mz.style-source/1": catalog["sources"].values(),
        "mz.style-adapter/1": catalog["adapters"].values(),
        "mz.style-preset/1": catalog["presets"].values(),
        "mz.style-modifier/1": catalog["modifiers"].values(),
        "mz.asset-profile/1": catalog["profiles"].values(),
    }
    for contract, entries in mappings.items():
        for entry in entries:
            if entry.get("format") != contract:
                raise ContractError(f"{entry.get('_file')}: expected {contract}")
            for key in required[contract]["required"]:
                if key not in entry:
                    raise ContractError(f"{entry.get('_file')}: missing {key}")
    for preset in catalog["presets"].values():
        if preset.get("status") not in PRESET_STATUSES:
            raise ContractError(f"{preset['id']}: invalid preset status")
        for profile_id in preset["profiles"]:
            if profile_id not in catalog["profiles"] and not partial_snapshot:
                raise ContractError(f"{preset['id']}: unknown profile {profile_id}")
        for modifier_id in preset["allowedModifiers"]:
            if modifier_id not in catalog["modifiers"]:
                raise ContractError(f"{preset['id']}: unknown modifier {modifier_id}")
        lineage = preset.get("lineage")
        if lineage is not None:
            if not isinstance(lineage, dict) or lineage.get("method") != "method-derived-original-rules":
                raise ContractError(f"{preset['id']}: invalid lineage method")
            for source_id in lineage.get("sources", []):
                if source_id not in catalog["sources"]:
                    raise ContractError(f"{preset['id']}: unknown lineage source {source_id}")
    targets: set[str] = set()
    for source in catalog["sources"].values():
        if not re.fullmatch(r"[0-9a-f]{40}", str(source.get("commit", ""))):
            raise ContractError(f"{source['id']}: commit must be a full SHA-1")
        if source.get("license") != "MIT":
            raise ContractError(f"{source['id']}: unsupported source license")
        if not isinstance(source.get("allowed"), list) or not isinstance(source.get("prohibited"), list) or not source.get("notice"):
            raise ContractError(f"{source['id']}: incomplete source boundary")
        for item in source.get("auditedFiles", []):
            if not isinstance(item, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))):
                raise ContractError(f"{source['id']}: invalid audited file hash")
    for adapter in catalog["adapters"].values():
        if adapter.get("sourceId") not in catalog["sources"]:
            raise ContractError(f"{adapter['id']}: unknown source")
        if adapter.get("status") not in ADAPTER_STATUSES:
            raise ContractError(f"{adapter['id']}: invalid adapter status")
        target = adapter.get("targetPreset")
        if not isinstance(target, str) or target in targets:
            raise ContractError(f"{adapter['id']}: adapter target must be unique")
        targets.add(target)
        if adapter["status"] in {"MAPPED_TO_EXISTING", "CANDIDATE"} and target not in catalog["presets"]:
            raise ContractError(f"{adapter['id']}: missing target preset")


def _result(status: str, request: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "format": "mz.visual-brief/1",
        "engineVersion": ENGINE_VERSION,
        "status": status,
        "request": {"summary": request},
        "reason": reason,
        **extra,
    }


def _prompt_value(value: Any) -> str:
    if isinstance(value, dict):
        return "; ".join(f"{key}={item}" for key, item in value.items())
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def resolve_intent(intent: dict[str, Any], catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    catalog = catalog or load_catalog()
    if intent.get("format") != "mz.intent/1":
        return _result("INVALID_INPUT", "", "format must be mz.intent/1")
    request = intent.get("request")
    asset = intent.get("asset")
    style = intent.get("style")
    if not isinstance(request, str) or not request.strip() or not isinstance(asset, dict) or not isinstance(style, dict):
        return _result("INVALID_INPUT", request if isinstance(request, str) else "", "request, asset, and style are required")
    profile_id = asset.get("profile")
    preset_id = style.get("preset")
    modifiers = style.get("modifiers", [])
    if not isinstance(profile_id, str) or not isinstance(preset_id, str) or not isinstance(modifiers, list):
        return _result("INVALID_INPUT", request, "asset.profile, style.preset, and style.modifiers are required")
    profile = catalog["profiles"].get(profile_id)
    if not profile:
        return _result("UNSUPPORTED_ASSET", request, f"unknown asset profile: {profile_id}", asset=asset)
    preset = catalog["presets"].get(preset_id)
    if not preset:
        if any(adapter["targetPreset"] == preset_id for adapter in catalog["adapters"].values()):
            return _result("STYLE_CONFLICT", request, f"preset is registered but has no executable rules: {preset_id}", asset=asset, style=style)
        return _result("STYLE_CONFLICT", request, f"unknown preset: {preset_id}", asset=asset)
    if preset.get("status") != "APPROVED_FOR_SKILL_OPERATION":
        return _result("STYLE_CONFLICT", request, f"preset is registered but not enabled: {preset_id}", asset=asset, style=style)
    if preset_id not in profile["supportedPresets"]:
        return _result("UNSUPPORTED_COMBINATION", request, f"{preset_id} is not supported by {profile_id}", asset=asset, style=style, target=profile["target"])
    size = asset.get("size")
    bounds = profile["hardConstraints"].get("size")
    if size is not None and (not isinstance(size, int) or not bounds or not bounds["minimum"] <= size <= bounds["maximum"]):
        return _result("UNSUPPORTED_COMBINATION", request, f"size is outside {profile_id} constraints", asset=asset, style=style, target=profile["target"])
    axes: set[str] = set()
    modifier_items = []
    for modifier_id in modifiers:
        if not isinstance(modifier_id, str):
            return _result("INVALID_INPUT", request, "modifier ids must be strings")
        modifier = catalog["modifiers"].get(modifier_id)
        if not modifier:
            return _result("STYLE_CONFLICT", request, f"unknown modifier: {modifier_id}", asset=asset, style=style)
        if modifier["axis"] in axes:
            return _result("STYLE_CONFLICT", request, f"duplicate modifier axis: {modifier['axis']}", asset=asset, style=style)
        axes.add(modifier["axis"])
        if modifier_id not in preset["allowedModifiers"]:
            return _result("STYLE_CONFLICT", request, f"{modifier_id} is not allowed by {preset_id}", asset=asset, style=style)
        if preset_id not in modifier["allowedPresets"] or profile_id not in modifier["allowedProfiles"]:
            return _result("STYLE_CONFLICT", request, f"{modifier_id} conflicts with {preset_id} or {profile_id}", asset=asset, style=style)
        modifier_items.append(modifier)
    rules = copy.deepcopy(preset["rules"])
    rule_sources = {key: f"preset:{preset_id}" for key in rules}
    for modifier in modifier_items:
        for key, value in modifier["patch"].items():
            rules[key] = value
            rule_sources[key] = f"modifier:{modifier['id']}"
    resolved_style = {
        "preset": {"id": preset_id, "family": preset["family"], "version": preset["version"]},
        "modifiers": [{"id": item["id"], "axis": item["axis"], "version": item["version"]} for item in modifier_items],
        "rules": rules,
        "ruleSources": rule_sources,
    }
    generation = {
        "requirements": [*CORE_RULES, *[f"{key}: {_prompt_value(value)}" for key, value in rules.items() if key != "avoid"]],
        "avoid": sorted(set(profile["hardConstraints"].get("prohibited", []) + rules.get("avoid", []))),
        "promptBlocks": ["MZ Core", f"Asset profile: {profile_id}", f"Base preset: {preset_id}", *[f"Modifier: {item['id']}" for item in modifier_items]],
    }
    return {
        "format": "mz.visual-brief/1",
        "engineVersion": ENGINE_VERSION,
        "status": "RESOLVED",
        "request": {"summary": request},
        "intent": intent.get("intent", {}),
        "asset": {**asset, "profile": profile_id, "hardConstraints": profile["hardConstraints"]},
        "style": resolved_style,
        "content": intent.get("content", {}),
        "target": profile["target"],
        "generation": generation,
        "provenance": {
            "core": "references/core.md", "preset": preset_id, "profile": profile_id, "catalogHash": catalog_hash(catalog),
            "sources": [
                {"id": source_id, "repository": catalog["sources"][source_id]["repository"], "commit": catalog["sources"][source_id]["commit"]}
                for source_id in preset.get("lineage", {}).get("sources", [])
            ],
        },
    }


def catalog_files(catalog: dict[str, Any]) -> list[Path]:
    root = catalog["root"]
    folders = [root / "schemas", root / "styles", root / "profiles", root / "references", root / "sources"]
    return [file for folder in folders if folder.is_dir() for file in folder.rglob("*") if file.is_file()]


def catalog_hash(catalog: dict[str, Any]) -> str:
    return tree_hash(catalog["root"], catalog_files(catalog))


def validate_brief(brief: dict[str, Any], catalog: dict[str, Any] | None = None) -> None:
    catalog = catalog or load_catalog()
    if brief.get("format") != "mz.visual-brief/1":
        raise ContractError("brief format must be mz.visual-brief/1")
    if brief.get("engineVersion") != ENGINE_VERSION:
        raise ContractError(f"brief engine version must be {ENGINE_VERSION}")
    if brief.get("status") not in VALID_BRIEF_STATUSES:
        raise ContractError("invalid brief status")
    if brief["status"] != "RESOLVED":
        return
    for key in catalog["schema"]["contracts"]["mz.visual-brief/1"]["required"]:
        if key not in brief:
            raise ContractError(f"brief missing {key}")
    profile_id = brief["asset"].get("profile")
    preset_id = brief["style"].get("preset", {}).get("id")
    if profile_id not in catalog["profiles"] or preset_id not in catalog["profiles"][profile_id]["supportedPresets"]:
        raise ContractError("brief has an unsupported profile/preset combination")
    if brief["target"] != catalog["profiles"][profile_id]["target"]:
        raise ContractError("brief target does not match profile")
