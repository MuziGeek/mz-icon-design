# MZ Visual Contracts

All v1 machine contracts are JSON and use a `format` field. The canonical required fields and allowed values are stored in `schemas/mz-contracts-v1.json` and enforced by `scripts/engine_lib.py`.

- `mz.intent/1`: structured request interpretation.
- `mz.style-source/1`: fixed upstream provenance, license, audited hashes, and exclusion boundary.
- `mz.style-adapter/1`: source-to-MZ capability mapping that never contains upstream assets.
- `mz.style-preset/1`: a full visual preset.
- `mz.style-modifier/1`: an allowed partial rule patch.
- `mz.asset-profile/1`: hard asset constraints and target Skill.
- `mz.visual-brief/1`: resolved handoff document.
- `mz.evaluation/1`: evidence-based review result.
- `mz.engine-snapshot/1`: self-contained downstream subset.

The resolver accepts structured input only. Agent reasoning fills the intent fields; deterministic scripts validate and merge the result.
