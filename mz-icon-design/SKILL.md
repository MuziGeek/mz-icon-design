---
name: mz-icon-design
description: Create, extend, restyle, or audit MZ Icon Design System assets. Use when the user explicitly asks for Muzi or MZ icons, a 16-32px MZ UI SVG icon, or a coherent MZ crayon or isometric block spot-icon set for sections, features, categories, marketing, or empty states.
---

# MZ Icon Design System

Create original, review-first icons in one of two isolated tracks. Do not use this Skill for generic icons that are not meant to use MZ visual language.

## Route the request

Extract `concepts`, `usage`, `display_size`, `mode`, `style`, `output_dir`, and optional user-provided references. Run `scripts/route_request.py` when the request is ambiguous.

| Request | Mode and style |
| --- | --- |
| One functional UI icon, navigation, button, or 16-32px target | `svg`, `mz-line-v1` |
| Section, feature, category, marketing, empty state, or 48-256px set | `spot`, `mz-crayon-v2` |
| Explicitly asks for voxel, isometric, or block-like space | `spot`, `mz-block-v1` |

An explicit user mode or style always wins. Default a single unspecified icon to SVG. Default an unspecified set to crayon spot icons.

## SVG workflow

1. Read [SVG rules](references/svg-track.md) and [shared design DNA](references/design-dna.md).
2. Write each icon as an original 24x24 SVG in the requested output directory. Use category `core`, `system`, `life`, or `brand` only to set semantic detail; never change the base geometry.
3. Run `python scripts/validate_svg.py <file-or-directory>`.
4. Create a 16/24/32px light-and-dark preview using the host browser or an equivalent local preview. Static validation alone never produces `READY_FOR_REVIEW`.
5. Record all files and results in `manifest.json` using [the batch contract](references/batch-schema.json), then run `python scripts/validate_manifest.py manifest.json`.

## Spot-icon workflow

1. Read [spot workflow](references/spot-track.md), [QA checklist](references/qa.md), and the selected style spec under `references/styles/`.
2. Freeze the selected style and write a sheet prompt. Use one clear metaphor per concept. Do not copy an upstream icon, path, composition, palette preset, or asset.
3. Generate a 1254px 4x4 sheet on a flat `#808080` background. Use nine populated cells by default; leave all later cells blank. If image generation is unavailable, save the prompt and manifest with `GENERATION_BLOCKED`; do not substitute an external paid API.
4. Slice with `python scripts/slice_sheet.py <sheet> <icons-dir> --count <n>` and validate with `python scripts/validate_png.py <icons-dir>`.
5. Build magenta, black, cream, 48px, and 96px QA previews with `python scripts/build_png_qa.py <icons-dir> <qa-dir>`; inspect them before marking the manifest `READY_FOR_REVIEW`.
6. Regenerate at most twice for a failed style, composition, bleed, or edge check. Then stop as `VALIDATION_FAILED` rather than claiming acceptance.

## Audit and restyle

Read the matching track reference, inspect the input, and report every rule breach. Write a corrected sibling copy only; never overwrite the original unless the user explicitly asks. Treat user references as semantic or style context, never as material to trace.

## Preserve

- Keep generated output outside this Skill directory.
- Use `DRAFT`, `VALIDATION_FAILED`, `GENERATION_BLOCKED`, or `READY_FOR_REVIEW` in manifests. Never claim `ACCEPTED` without user confirmation.
- Keep the crayon baseline assets intact. They are reference material, not templates to trace.
- Do not publish, upload, install plugins, create automations, or use a paid external image API.

## Resources

- [Design DNA](references/design-dna.md): shared MZ identity, categories, and originality limits.
- [SVG track](references/svg-track.md): vector rules and review criteria.
- [Spot track](references/spot-track.md): sheet, slicing, and style selection instructions.
- [QA checklist](references/qa.md): visual and mechanical release criteria.
- [Batch contract](references/batch-schema.json): `mz.icon-batch/1` manifest fields.
- [Crayon spec](references/styles/mz-crayon-v2.json) and [block spec](references/styles/mz-block-v1.json): frozen production specifications.
