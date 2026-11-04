# Budget hardware appearance study

Separate from the approved slab CAD. This is a reproducible, millimetre-based Blender visualization, not a printable enclosure or electrical/mount design.

Run:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -P cad/budget/tools/render_preview.py
```

Outputs in `tmp/`: MacBook overview, close-up, exploded view, editable Blender scene and checked-envelope assumptions JSON.

Documented: [Waveshare Pico-LCD-1.8](https://www.waveshare.com/Pico-LCD-1.8.htm) board 52 × 34.5 mm, active area 35.04 × 28.03 mm; manufacturer drawing puts its left active edge 5.91 mm from the PCB edge. [Pico](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) outline 51 × 21 × 1 mm. Pico WH and display long axes align; USB silkscreen determines orientation. [Apple](https://support.apple.com/en-gb/121552) chassis width/depth 312.6 × 221.2 mm.

Assumed: 59 × 49.65 × **22 mm** enclosure, LCD-module depth, 8.5 mm female socket envelope, component positions/heights, PCB clearance, cover materials, USB cutout and connector overmold dimensions. Pico WH RF package is schematic. Actual supplied headers may need a different depth. The black face conceals unused LCD borders; eyes are illustrative 160 × 128 artwork, not chosen firmware. Silver is a finish concept, not a manufacturing material decision. Lid height/pose/port offsets follow existing provisional CAD, not official Apple measurements. The rear bridge is a visual placeholder; retention and attachment are unvalidated.

The depicted cable is an illustrative connection from Mac USB-C directly to Pico Micro-B. It is **not** constrained to a purchased 300 mm usable length and proves neither 30 cm reach nor safe lid motion. No magnetic electrical contacts are implied. No purchased parts, working hardware, heat, viewing-angle quality, insulation, printable closure, BOOTSEL access or manufacturing fit is validated. Actual parts must be measured before an enclosure is frozen.

The render script checks built board envelopes, active-area size and nominal internal clearance. Images preserve relative geometry, but an image viewed at arbitrary zoom is not physically 1:1 on the user's monitor.
