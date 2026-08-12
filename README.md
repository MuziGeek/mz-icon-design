<p align="right"><a href="README.zh-CN.md">简体中文</a></p>

<p align="center">
  <img src="docs/readme/hero.svg" width="100%" alt="MZ Icon Design routes 16–32 px UI icons to SVG and 48–256 px spot icons to reviewed PNG workflows">
</p>

# MZ Icon Design

One request. The right production track. Reviewable icons.

MZ Icon Design is an independent, review-first agent Skill for creating coherent interface icons and expressive spot-icon systems. It routes by intended use and display size, validates every output, and stops at `READY_FOR_REVIEW`.

## Real output first

![Nine MZ crayon spot icons shown at large and compact sizes](mz-icon-design/assets/mz-crayon-v2/contact-sheet.png)

<details>
<summary><strong>Browse the other nine approved Spot styles</strong></summary>

### MZ Block

![Nine MZ block-style icons](mz-icon-design/assets/mz-block-v1/contact-sheet.png)

### MZ Soft 3D

![Nine matte soft-3D MZ icons](mz-icon-design/assets/mz-soft-3d-v1/contact-sheet.png)

### MZ Colorblock

![Nine MZ Colorblock icons](mz-icon-design/assets/mz-colorblock-v1/contact-sheet.png)

### MZ Isometric

![Nine soft isometric MZ icons](mz-icon-design/assets/mz-isometric-v1/contact-sheet.png)

### MZ Macro Voxel

![Nine polished macro-voxel MZ icons](mz-icon-design/assets/mz-voxel-macro-v1/contact-sheet.png)

### MZ Sticker

![Nine die-cut MZ sticker icons](mz-icon-design/assets/mz-sticker-v1/contact-sheet.png)

### MZ Cartoon

![Nine friendly MZ cartoon icons](mz-icon-design/assets/mz-cartoon-v1/contact-sheet.png)

### MZ Animal Badge

![Nine one-off MZ animal badge icons](mz-icon-design/assets/mz-animal-badge-v1/contact-sheet.png)

### MZ Realistic

![Nine simplified realistic MZ object icons](mz-icon-design/assets/mz-realistic-v1/contact-sheet.png)

</details>

## Choose by job and size

| Track | Best for | Output |
| --- | --- | --- |
| `mz-line-v1` | Navigation, buttons, compact UI at 16–32 px | Original SVG with light/dark previews |
| `mz-filled-v1` | Explicit filled UI icons and solid glyphs at 16–32 px | Original `currentColor` SVG with light/dark previews |
| `mz-crayon-v2` | Sections, features, categories, empty states | Hand-drawn transparent PNG Spot icons |
| `mz-block-v1` | Technical products and spatial concepts | Isometric block-style transparent PNG icons |
| `mz-soft-3d-v1` | Explicit soft-3D or matte-clay concepts | Original transparent PNG Spot icons |
| `mz-colorblock-v1` | Explicit Colorblock or contrasting-colour-block concepts | Original transparent PNG Spot icons |
| `mz-isometric-v1` | Explicit soft isometric miniature concepts | Original transparent PNG Spot icons |
| `mz-voxel-macro-v1` | Explicit Macro Voxel or polished acrylic voxel concepts | Original transparent PNG Spot icons |
| `mz-sticker-v1` | Explicit Sticker or die-cut sticker concepts | Original transparent PNG Spot icons |
| `mz-cartoon-v1` | Explicit friendly Cartoon icon concepts | Original transparent PNG Spot icons |
| `mz-animal-badge-v1` | Explicit one-off Animal Badge concepts | Original transparent PNG Spot icons |
| `mz-realistic-v1` | Explicit simplified Realistic object concepts | Original transparent PNG Spot icons |

An explicit user mode or style always wins. A single unspecified icon defaults to SVG; an unspecified set defaults to `mz-crayon-v2` Spot icons.

## Two tracks, separate QA

### UI SVG · 16–32 px

Create an original 24×24 icon, validate its geometry and style, inspect it at 16/24/32 px on light and dark backgrounds, then validate the batch manifest. Static checks alone never produce `READY_FOR_REVIEW`.

### Spot PNG · 48–256 px

Freeze one approved style, generate a controlled 4×4 sheet, slice the requested icons, validate transparency and clipping, then inspect magenta, black, cream, 48 px, and 96 px QA previews.

## Install

Install the current v1.3.0 code from `main` with Codex:

```text
$skill-installer install https://github.com/MuziGeek/mz-icon-design/tree/main/mz-icon-design
```

The latest published tag is still `v1.0.0`; use `main` for the v1.3.0 routes shown above until a v1.3.0 release is published.

## First use

```text
Use $mz-icon-design to create a 24px search icon for navigation.
Use $mz-icon-design to create nine crayon spot icons for a personal portfolio.
Use $mz-icon-design to audit these SVG icons against the MZ design system.
```

## Review boundary

- UI SVGs receive static validation plus multi-size light/dark visual review.
- PNG sets receive transparent-edge, clipping, size, and QA-sheet checks.
- Manifests distinguish `DRAFT`, `GENERATION_BLOCKED`, `VALIDATION_FAILED`, and `READY_FOR_REVIEW`.
- The Skill never silently publishes assets or claims user acceptance.

## MZ Visual Engine handoff

The Skill can accept an optional validated `mz.visual-brief/1`. A resolved brief selects a compatible existing route; it cannot bypass this Skill's originality, SVG/PNG QA, manifest, or user-review requirements.

## License

Code and documentation are MIT licensed. MZ reference artwork uses the [MZ Reference Asset License 1.0](ASSET_LICENSE.md). See [NOTICE.md](NOTICE.md) for the file-level boundary.
