# Spot Track

Use this track for coherent MZ sets displayed at 48-256px. Select one style before generating and keep it frozen for the complete set.

## Sheet contract

- Generate a square 1254x1254 sheet on exactly flat `#808080`.
- Use a 4x4 grid with generous equal gutters and row-major placement.
- Generate nine concepts by default. For fewer concepts, leave remaining cells perfectly blank. Never exceed sixteen concepts.
- Keep every icon isolated, optically equal, and fully within its own cell. Use no text, badge, tile, grid line, shadow, watermark, or decorative detached mark.

## Output contract

Slice each accepted cell into 512x512 RGBA PNG files. Run the supplied slicer, PNG validator, and QA builder. The slicer only clears edge-connected neutral-grey background; inspect all output for residual grey and neighbour bleed.

## Style selection

- `mz-crayon-v2`: default MZ brand spot style. Use the bundled baseline only as a style authority.
- `mz-block-v1`: use when the request needs isometric, block-like spatial structure. Keep its MZ palette, matte crayon treatment, and low-density block budget.
- `mz-soft-3d-v1`: use only for explicit soft-3D or matte-clay requests. Keep one compact original object, the shared three-quarter camera and broad soft light; prohibit glass, chrome, ground shadows, labels, and logos.
- `mz-colorblock-v1`: use only for explicit Colorblock or contrasting-colour-block requests. Keep one original two-dimensional metaphor, no outline, at most three MZ chromatic blocks, and only 8-12% shallow tonal modelling; prohibit shadows, material texture, and 3D extrusion.
- `mz-isometric-v1`: use only for an explicit soft-isometric-miniature request. Keep one original floating object, the shared three-quarter camera, clean flat-facet shading, and a restrained five-facet budget; prohibit ground shadows, grey fringe, glossy plastic, crayon outlines, labels, and logos.
- `mz-voxel-macro-v1`: use only for explicit Macro Voxel or polished-acrylic-voxel requests. Keep one original low-density silhouette on the shared coarse grid, an orthographic three-quarter camera, opaque planar faces, semantic colours, and two or three identity cues. Prohibit internal alpha holes, detached alpha islands, chroma residue, ground shadows, Oreo-derived palettes, labels, logos, and third-party motifs. Bare `voxel`, `block`, and `isometric` requests remain on `mz-block-v1`.
- `mz-sticker-v1`: use only for explicit Sticker or die-cut-sticker requests. Keep one original flat symbol, a continuous warm-white border at approximately 8-12% of subject scale, transparent exterior, and only restrained local tonal modelling. Prohibit character faces, cards, cast shadows, material texture, 3D extrusion, labels, logos, and third-party motifs.
- `mz-cartoon-v1`: use only for explicit Cartoon-icon requests. Keep one original rounded two-dimensional silhouette, a consistent soft deep-navy outline, no more than three chromatic blocks, and only restrained local tonal modelling. Prohibit fixed mascots, character likeness, childish doodling, strong gradients, cast shadows, material texture, 3D extrusion, labels, logos, and third-party motifs.
- `mz-animal-badge-v1`: use only for explicit Animal Badge requests. Use a different generic one-off animal metaphor for every concept inside a simple circular badge, with one semantic prop at most and restrained local tonal modelling. Prohibit recurring mascots, Muzi, the existing cat identity, game-achievement styling, cast shadows, material texture, 3D extrusion, labels, logos, and third-party motifs.
- `mz-realistic-v1`: use only for explicit Realistic-object requests. Keep one original generic object, a restrained three-quarter product view, opaque natural matte material, soft studio light, and no more than three material cues. Prohibit people, brands, product replicas, photographic scenery, cast shadows, text, logos, watermarks, and third-party industrial design. Validate every final PNG with `python scripts/validate_png.py <icons-dir> --style mz-realistic-v1` so material-erasure holes, detached fragments, and translucent halos fail closed.
