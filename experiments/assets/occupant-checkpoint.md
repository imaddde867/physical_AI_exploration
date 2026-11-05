# Approved Occupant checkpoint

Saved 2026-11-05 after the user approved its appearance in the native simulator.

- `occupant-source.png`: original folded creature extracted from the first generated concept sheet. Later human-looking revisions were rejected.
- `occupant.rgb565`: the approved static composition, 240 × 280, little-endian RGB565, exactly 134,400 bytes. The source is fitted without stretching, with black side margins.
- Artwork generated with the built-in image tool on 2026-11-05. No third-party character assets were incorporated.

Reopen the unchanged checkpoint from the repository root:

```sh
sim/run.sh experiments/occupant_still.py --fps 5
```

The animated experiment is separate, so this composition stays available for comparison.
The preview targets approximately 27.972 × 32.634 mm; physical scale needs ruler calibration.
Panel brightness, corner clipping, and hardware animation performance remain unverified.
