# Measure the real Mac (10 minutes, free)

Values in `cad/slab/src/params.py` marked ASSUMED depend on these. Tools: calipers, a USB-C power meter (inline tester), a piece of string or thin wire.

| # | Measure | How | Assumed in CAD | Measured |
|---|---|---|---|---|
| 1 | Lid thickness (at the right edge) | calipers, lid closed or open | 4.5 mm | |
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
