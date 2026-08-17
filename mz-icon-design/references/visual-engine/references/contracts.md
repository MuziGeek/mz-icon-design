# MZ Visual Contracts

All v1 machine contracts are JSON and use a `format` field. The canonical required fields and allowed values are stored in `schemas/mz-contracts-v1.json` and enforced by `scripts/engine_lib.py`.

- `mz.intent/1`: structured request interpretation.
- `mz.design-tokens/1`: semantic visual roles shared across media.
- `mz.character-profile/1`: explicit character identity and medium defaults; the public Engine bundles no private character.
- `mz.visual-extension/1`: an explicit, hash-bound namespaced extension that may add Tokens, Character Profiles, and Presets without overriding public Core IDs.
- `mz.engine-compat/1`: Engine version, resolver Snapshot identity, and shared source-catalog hash. Executors compare `sourceCatalogHash` with their own managed Snapshot instead of requiring different Snapshot targets to have the same aggregate hash.
- `mz.style-source/1`: fixed upstream provenance, license, audited hashes, and exclusion boundary.
- `mz.style-adapter/1`: source-to-MZ capability mapping that never contains upstream assets.
- `mz.style-preset/1`: a full visual preset.
- `mz.style-modifier/1`: an allowed partial rule patch.
- `mz.asset-profile/1`: hard asset constraints and target Skill.
- `mz.visual-brief/1`: resolved handoff document.
- `mz.evaluation/1`: evidence-based review result.
- `mz.engine-snapshot/1`: self-contained downstream subset.

The resolver accepts structured input only. Agent reasoning fills the intent fields; deterministic scripts validate and merge the result.

Load an Extension only through the resolver's explicit `--extension` argument. Never scan local Skill directories for identities or brands. Extension IDs must use their declared namespace and cannot replace public catalog entries.
