# MacDesk Buddy: 60 mm slab mount (engineering status, 2026-11-02)

**Status: unpowered conceptual CAD only. NOT READY FOR FABRICATION OR POWER.**
This branch corrects the insulation, retention and registration *shapes* from PRs #12/#13. It does not establish physical strength, USB compliance, electrical isolation under wet/dirty conditions, lid fit, hinge endurance, or an assembled screen PCB. It must never be treated as a finished connector.

## Nominal envelope, coordinates and honesty about fit

All distances are mm. X points right, Y toward the back of the lid, Z up. Simplified lid front = Y -4.5, lid rear = Y 0; these lid dimensions are *assumptions*. Published overall MacBook enclosure W=312.6, depth=221.2, closed H=15.5 are not an accessory interface drawing.

| Item | Static front-to-back envelope |
| --- | ---: |
| Detachable aluminum + flush glass body (60 × 38.4) | **4.90** |
| Front to back of tape + stainless plate | **6.10** |
| Front to far rear of contact-carrier capture flange | **6.45** |
| Front to cable outside surface (local, not continuous) | **9.00** |
| Front to protective grommet outside surface (local maximum) | **9.50** |

These are ideal geometry extents, **not maximum as-built thicknesses**. No manufacturing tolerance stack, real glass adhesive, bare display panel, controller PCB, connector PCB, solder, cable strain relief or wiring volume has been packaged. The screen shell is still a *solid mass envelope with glass/mount cutouts*, not a manufacturable hollow enclosure. The proposed 4.9-mm body may be impossible with the eventual panel, electronics, thermal clearances and fasteners; select/measure those parts before revising the target. The 0.6-mm lid-edge gap is only nominal.

## Mechanically registered detachable interface

- Four magnets remain at X = screen center ±18 and Z = center ±10, with nominal 5.0 × 1.0-mm magnets. Their 5.2-mm diameter pockets now include a nominal 0.10-mm adhesive ring and floor, leaving the magnetic face 0.10 mm behind the shell. **Adhesive formulation, surface preparation, pull-off/shear force, corrosion and temperature cycling are unverified.** A magnet may pull out before the screen detaches unless tested.
- **Two asymmetric integral aluminum locating dowels**, 1.60 mm diameter, project 1.0 mm from the back of the screen. Primary 1.90-mm round through-hole and secondary 1.90-mm-wide elongated through-slot are cut in the steel plate. Their 36-mm-class spacing constrains rotation; asymmetric Z offset prevents a nominal 180° mate. At the ideal hole sizes the primary radial allowance is 0.15 mm, *not an achievable finished-product tolerance promise*. Lead-in/chamfers, hole-edge strength, insertion wear and real stack tolerances need a physical build. Pogo pins begin contacting only after the longer dowels have entered the holes.
- The insulating carrier is now **captured by opposite front and rear shoulders** across the 1.2-mm steel thickness, with a 0.15-mm clearance to the through-window core. This is a **steel-insert overmold** concept; a single-piece, double-flanged carrier cannot be pressed through a closed hole afterward. Alternatively, redesign it as a two-piece screw/clip assembly *before fabrication*. The front flange has explicit relief in the screen shell. Polymer creep, adhesion, tooling and repeated pogo loading have not been evaluated.
- The 3-mm fixed cable passes down a bottom notch behind the bonded lid strip inside a 4.0-mm-OD insulating sleeve. Unlike the previous loose sleeve, the modeled grommet uses **two closed steel mounting holes**, 1.50-mm elastomeric snap stems and 2.20-mm front mushroom heads (through 1.90-mm bores), now opposed by 2.40-mm rear retaining collars adjacent to the steel. The tape is relieved around the heads. Their nominal axial float is 0.09 mm (formerly 1.09 mm), with an ideal worst-position head-to-lid gap of 0.15 mm. These are **untoleranced ideal CAD margins**, not evidence of compression, snap assembly, retention strength or real MacBook clearance. **A real elastomer grade and snap-deflection/fatigue design have not been chosen**. This is an outline of a captive molding, not a pull-tested clamp or strain relief. A separate cable-grip/strain-relief feature is mandatory.
- The stainless grade, its magnetic response, plate bending stress, plate-to-lid adhesive, and interaction with the MacBook's own magnets/sensors are **not verified**.

## USB contact geometry and explicit electronics blocker

The steel has a full-depth isolated opening. The 1.8-mm-wide, 3.00-mm-pitch mounting pads are now recessed **0.20 mm** in separate dielectric wells. The carrier outline includes each 0.05-mm well clearance **before** adding the remaining 1.0-mm outer polymer wall. Nominal 1.10-mm internal web between wells; nominal 0.15-mm carrier-to-steel window gap. Four pad/via metal envelopes remain independently isolated from the stainless in the static model. Physical polymer dielectric strength and leakage under contamination/ESD are unverified.

Physical pad order is **GND / D- / D+ / VBUS**, deliberately separating power and ground by signal contacts. Recesses and alignment reduce accidental contact but **do not make exposed VBUS safe**. With the permanent USB-C plug connected and the screen removed, its VBUS pad must be **normally de-energized**. A future cable-side or plug-contained PCB must provide:

1. Correct USB-C sink/plug CC/Rd arrangement, power negotiation/budget and cable/plug wiring (do not presume USB-C is just four wires).
2. A **normally disabled, current-limited/latch-off high-side power switch** between Mac VBUS and the exposed mounting VBUS, plus protected power-off/fault handling. TI TPS2553-1 is an *example for feasibility* (adjustable 75mA–1.7A typical current limit, latch-off). It is **not specified into this CAD** and its chosen limit must obey the host/device power budget.
3. **Reliable fully mated detection and break-before-exposure power removal** independent of ordinary four USB data/power contacts, e.g. a verified mechanically actuated interlock or additional staged sense contact. The four-contact design **does not yet implement this**. Do not connect VBUS directly or use D+/D- activity as a safety interlock.
4. USB 2.0 D+/D- continuity and differential integrity across the detachable contacts, EMI/shield/chassis strategy, TVS/ESD positioning, ground sequencing and short/partial-mate tests. No USB 3.x/Thunderbolt passthrough is claimed.
5. A real insulated termination of the four carrier rear vias to the fixed cable, and SMT pogo PCB connections inside the display. Strain relief and cable bend endurance must be qualified.

**Reference pogo candidate, not an approved part:** [Harwin P70-5000045R](https://www.harwin.com/products/P70-5000045R), [Harwin comparison chart](https://cdn.harwin.com/pdfs/Harwin_Pogo_Pin_Comparison_Chart.pdf). Gold-plated SMT pogo; free height 2.40; acceptable manufacturer working height 1.85–2.00 (manufacturer reference 1.90; model targets the midpoint, 1.925); ball head Ø0.60, body Ø1.50; manufacturer normal working force 0.68 ± 0.19 N; max rated current 1 A/contact; specified minimum 10,000 cycles. The contact reference assumes PCB seating face Y = -1.325 and pad mating plane Y = +0.60: **1.925 mm nominal compressed height**, 0.475-mm compression from free and just 0.075-mm ideal axial headroom in either direction. A real PCB, mating-stop and housing tolerance stack is still required. Four contacts imply roughly 2.72 N nominal total spring force *from the datasheet only*, not a measured magnetic retention requirement or tolerance guarantee. The barrel/tip are simplified solids, not manufacturer STEP. 2.40-mm shell bores contain separate 2.10-mm insulating bushings with 1.70-mm bores (nominal 0.20-mm polymer wall, 0.10-mm radial barrel clearance and 0.60-mm aluminum web between shell bores); the eventual PCB needs the actual recommended footprint, solder process and support. No controller PCB/panel assembly is modeled.

**Electrical references:** [TI TPS2553-1](https://www.ti.com/product/TPS2553-1); [ROHM CC/Rd technical guide](https://fscdn.rohm.com/en/products/databook/applinote/ic/interface/usb_pd/bd91n01nux-evk-001-sa_ug-e.pdf). These are candidate design references, not a tested circuit.

## Cable and MacBook movement: still a hard stop

The static centerline is approximately **184.6 mm** with nominal 12-mm radii, but the precise report must be generated by the CAD tool. Prior reference numbers are about 8.0-mm free-span chord excess against ~24.0-mm guessed arc-length demand (~16.1-mm nominal proxy deficit). Both figures depend on assumed hinge/port geometry. **Chord excess is not usable service-loop slack; arc length is not a dynamic hinge simulation**. Neither 12-mm radius nor a nominal zero-intersection with the frozen lid proves fatigue life or cable safety.

Measure on the physical 14-inch M4 MacBook: display-half thickness/profile and heights, hinge pivot/clearance in all relevant axes, true USB-C port XYZ and plug profile, lid max opening angle, cable pinch envelope at closed/intermediate/open angles, and the final cable OD/minimum *dynamic* bend radius from its manufacturer. Trial a restrained service loop and strain relief through the entire lid sweep using a nonconductive mock-up. **Do not stretch the cable to solve the deficit**. A rear plate/plug or routing change may be mandatory. The current model does not validate a full lid movement.

## Reproducible verification (static CAD only)

From the repo root:

```sh
python -m compileall -q cad sim experiments tests
python -m unittest discover -s tests -v
python -m pip install build123d==0.13.0
python -m unittest discover -s tests -v
(cd cad/slab/src && python mount.py && python export_parts.py)
MACDESK_RENDER_SMOKE=1 blender -b -t 2 --python cad/slab/tools/render.py
```

GitHub Actions CAD job **must** install build123d, run the solid checks (not skip), export new STLs while deleting old STLs, render four PNGs headlessly (wide, close, mount contact face, screen rear) and check their signatures/dimensions. The two isolated technical views omit opaque reference parts so the interface can be inspected. Generated CAD STLs and Blender images are uploaded as workflow artifacts. Static CAD regression checks are *not* real tolerance analysis, manufacturing proof, ESD verification, physical clearance metrology or a powered-device approval.
