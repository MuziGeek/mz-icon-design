# QA Checklist

## SVG

- Static validator passes with no errors.
- Preview reads at 16px, 24px, and 32px on light and dark backgrounds.
- One concept is recognisable without extra decoration.
- Stroke, corners, optical size, and whitespace match the set.

## PNG

- Output is 512x512 RGBA with transparent corners.
- Subject is not clipped, grey edge residue is below the validator threshold, and no neighbour fragment remains.
- Magenta, black, and cream composites reveal no halo or missing edge.
- 48px and 96px previews remain legible and visually balanced.
- Every concept follows the frozen style's palette, camera, detail budget, and motif rules.

## Status

Write `READY_FOR_REVIEW` only after the relevant checks and visual inspection pass. Write `VALIDATION_FAILED` after two failed targeted regenerations. User approval alone may change a reviewed artifact to `ACCEPTED` outside this Skill's automatic workflow.
