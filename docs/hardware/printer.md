# Printer

Recorded 2026-11-05 from photos taken at the machine.

| Item | Value | Source |
|---|---|---|
| Printer | Bambu Lab H2S, asset label "FIT Printer 2" (shared lab machine) | front label |
| Build volume | 340 × 320 × 340 mm | printed on the build plate |
| Plate | Bambu plate marked PLA/ABS/PETG | plate label |
| Nozzle | 0.4 mm (two spare 0.4 hotends in the toolbox) | hotend labels |
| Filament system | AMS 2 Pro on top, 4 spools, dry packs inside | photo |

The concept assembly (372.2 × 221.2 × 232.7 mm) exceeds the build volume, so it must be printed as separate parts. The expected part sizes (slab shell about 59 × 49.65 mm, plate, desk holder) are well within the bed, but none is a print-ready part yet: the mount uses a steel plate, the shell is still a solid exterior concept, and the desk holder is not modeled.

## Still unknown

- Filament material and brand: which spools are loaded, and whether any are PLA, PETG or ABS.
- Slicer profile: layer height, walls, infill, and supports used for the first print.
- Measured tolerance: print a fit coupon (slot, pin, and USB-C plug cavity) before freezing enclosure dimensions. Use it to set clearances in `cad/slab/src/params.py`, not manufacturer numbers.
- Access: shared machine, so booking and queue time are unrecorded.
