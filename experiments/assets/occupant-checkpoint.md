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
Preview its pronounced breathing and head sway with:

```sh
sim/run.sh experiments/occupant_idle.py --fps 12
```

Animation approved 2026-11-05: breathing amplitude 10 pixels over 4.2 seconds,
head sway 10 pixels over 6.5 seconds, vertical head movement 4 pixels over
7.1 seconds. These are local deformation maxima, not whole-image translations.
This checkpoint retains the original black side margins.

This is a desktop movement study using subpixel image deformation. It adds no
expressions or input reactions. Device playback needs a measured implementation;
the desktop's expanded images and working arrays are not a firmware memory model.

The preview targets approximately 27.972 × 32.634 mm; physical scale needs ruler calibration.
Panel brightness, corner clipping, and hardware animation performance remain unverified.
