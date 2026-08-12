#!/usr/bin/env python3
"""Validate an Engine brief against the bundled Icon snapshot."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_visual_brief.py <brief.json>")
        return 2
    snapshot = Path(__file__).resolve().parents[1] / "references" / "visual-engine"
    sys.path.insert(0, str(snapshot / "scripts"))
    from engine_lib import ContractError, load_catalog, validate_brief
    try:
        brief = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        validate_brief(brief, load_catalog(snapshot))
        if brief.get("status") != "RESOLVED" or brief["target"].get("skill") != "mz-icon-design":
            raise ContractError("brief is not a resolved Icon handoff")
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"INVALID: {exc}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
