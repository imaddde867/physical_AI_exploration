# First print: a small clearance coupon

The selected appearance is the [landscape rear-lid buddy](build-decision.md). **Print only the fit coupon at this stage.** The selected placement model is solid reference geometry with placeholder electronics and dock; it is not a functional shell or mount STL.

## What the printer photos establish

The supplied photos identify a **Bambu Lab H2S** and an **AMS 2 Pro** filament feeder. The separate tool kit contains hotends marked 0.4, but this does not establish which nozzle is installed. Black, gray and blue describe color; the photos do not identify PLA/PETG, brand or the material profile. Read the spool label or the printer's loaded-material information before slicing.

You can use one loaded spool. There is no need to change colors, unload the feeder or buy three filaments. Prefer an available PLA spool for the first fit gauge. If black is another material, use the identified PLA color instead. For the later load-bearing arm, PETG is a candidate requiring its own fit and retention tests; do not treat a PLA coupon as proof of PETG fit.

The shared printer's local booking and personal-project rules still apply. Confirm permission locally before starting a print. The photos and local notices remain outside the public repository.

## File to bring

Download [fit_coupon.stl](../cad/peeking-concepts/STL/fit_coupon.stl) onto a USB stick, or copy it from the repository. This is a clearance gauge with **two separate objects**, not the old round display aperture coupon:

- A strip with three holes, left to right: 4.2 x 8.2, 4.4 x 8.4 and 4.6 x 8.6 mm.
- A 4 x 8 mm peg on a foot.

The overall mesh envelope is **45 x 27.5 x 8 mm**. The hole sizes provide 0.2, 0.4 and 0.6 mm total dimensional clearance relative to the peg. Mesh inspection found two closed components. That establishes file geometry, not printed accuracy or latch strength.

## In Bambu Studio

1. Import the STL in millimetres at **100% scale**. Keep both objects; do not merge them or place one on top of the other. Keep their flat bases on the build plate.
2. Select **Bambu Lab H2S** and the installed nozzle diameter. If it is 0.4 mm, start with **0.20 mm Standard**, 3 walls and 15% infill. These are proposed first-print settings, not a validated slicer preset.
3. Select the actual installed plate and the identified spool's material profile. Map both objects to **one filament slot**. Use the profile's temperatures and calibration defaults; avoid manual nozzle/bed guesses.
4. Slice and inspect the preview. Both pieces should begin on the plate, their holes should remain open, and no support should fill the holes. The gauge was designed for a flat print without supports; if the slicer proposes supports, recheck placement before proceeding.
5. Record estimated time and filament mass, then follow local booking and print procedures. Watch the first layer. Ask the printer custodian for help with a material mismatch or failed start.
6. Let the plate cool before removing the parts. Check each hole gently with the peg, without forcing it. Record material, nozzle, profile, measured dimensions and which fit feels right. Do not enlarge or rescale the whole model as a fit correction.

For later documentation, record results in this form:

```text
Date / printer / nozzle / plate:
Material and spool profile:
Layer height / walls / infill:
Slice time and grams:
Peg measured X/Y:
Hole 0.2 / 0.4 / 0.6: loose, sliding, tight, or will not enter:
Warping or first-layer issues:
```

## Before a fitted enclosure

Measure the received board, display position, USB plug body and cable bend, buttons, holes, headers and mass. Measure the Mac's actual lid geometry and cable route. The current 48 x 33.12 x 13 mm landscape housing is an appearance envelope. It lacks board retention, serviceable fastening, verified button/antenna clearance, strain relief and a tested detachable dock. Adhesion to bare laptop finish and lid closure are unverified.

Print a measured board-fit piece before a full enclosure. Keep electronics out until it fits without glass pressure or exposed-contact shorts. A working latch, repeated detach cycles and lid/cable clearance must be checked before mounting or transport.

## Earlier GC9A01 stand

[cad/desk-buddy.scad](../cad/desk-buddy.scad) is the earlier desktop round-screen shell. Its `fit_coupon` setting produces a **different**, circular aperture gauge for the GC9A01. Neither that shell nor its aperture belongs to the selected AMOLED order. Keep it as a historical learning prototype.

The [CAD README](../cad/peeking-concepts/README.md) lists the current placement source, historical rebuild toolchains and coupon checks. No slicer session or physical print was performed during this audit.
