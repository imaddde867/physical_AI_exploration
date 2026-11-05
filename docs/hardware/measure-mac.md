# Measure the real Mac (10 minutes, free)

Values in `cad/slab/src/params.py` marked ASSUMED depend on these. Tools: calipers, a USB-C power meter (inline tester), a piece of string or thin wire.

| # | Measure | How | Assumed in CAD | Measured |
|---|---|---|---|---|
| 1 | Lid thickness (at the right edge) | calipers, lid closed or open | 4.5 mm | 4.0 (drawing) |
| 2 | Lid height (hinge to top edge) | ruler, lid open | 214 mm | |
| 3 | Right-side port: distance from the base's rear edge to port centre | ruler | 45 mm | |
| 4 | Port centre height above the desk | calipers | half of base height | |
| 5 | Hinge axis position (how far behind the lid front) | look at the hinge from the side | lid mid-thickness | |
| 6 | Lid opening angle you actually use | protractor app | 135 deg max | |
| 7 | Do the lid's own magnets pull on a steel plate at the right edge? | hold a small steel piece there | unknown | |

Power and sleep (needs the USB-C meter and any 5 V USB-C load):

| # | Question | How | Result |
|---|---|---|---|
| 8 | Does the port supply 5 V to a plain sink with a 5.1 kOhm CC pull-down? | meter in line | |
| 9 | Current the port allows | meter reading with a known load | |
| 10 | Does VBUS stay on when the Mac sleeps with the lid open? | sleep the Mac, watch the meter | |
| 11 | Does VBUS stay on with the lid closed? | close the lid | |
| 12 | When the lid is closed, does a slab beside the right edge touch the desk? | hold a card of the slab's size against the edge and close the lid | |

Cable slack test: lay a string along the planned cable route on the lid back (see `cad/slab/DECISIONS.md`), swing the lid through your normal range and mark how much the route length changes.

## Values taken from Apple's dimensions drawing (2026-11-05)

Source: Apple's drawing for the 14.2-inch MacBook Pro (screenshot, treated as 1:1). Pixel positions were measured against the 312.6 mm width (about 2.74 px/mm); the drawing's USB-C slot measures 8.7 mm, as expected. Resolution is about ±0.4 mm. The screenshot and a source link were not saved, so the scale and reference edges cannot be rechecked. Treat rows 1-4 as provisional drawing values and keep the caliper checks open until the drawing is saved to the repo with its URL and marked measurement points.

| Row | Item | Value used | Was |
|---|---|---|---|
| 1 | Lid thickness | 4.0 mm | 4.5 ASSUMED |
| 2 | Lid height | 221.2 mm (lid outline equals the base footprint) | 214 ASSUMED |
| 3 | Right USB-C centre from rear edge | 46.1 mm (rear to front: HDMI, USB-C, SD) | 45 ASSUMED |
| 4 | Right USB-C centre height | 7.75 mm, half of the 15.5 mm body (base is 11.5 mm) | half of base height |

Not in the drawing, still assumed: hinge axis (rows 5), opening angle (6), magnet pull (7), power and sleep behaviour (8-11), lid-closed clearance (12), cable slack.
