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
