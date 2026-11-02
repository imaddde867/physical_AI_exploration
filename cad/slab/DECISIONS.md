# Slab buddy: mounting and electrical geometry (2026-11-02)

The 60 × 38.4 mm detachable side display and single fixed USB-C cable are still the intended design. The magnetic mount is a **conceptual, unverified prototype**, not a production-safe USB connector. See PR #12 for the original design decisions and reason for replacing the 48 mm pod.

## Static CAD arrangement (mm)

- MacBook 14-inch enclosure: Apple-published width 312.6 and depth 221.2. **Not measured:** lid height 214, lid thickness 4.5, hinge axis (`y=-2.25, z=11`), right-side USB-C port at 45 mm from rear, and 135° lid sweep. The simplified lid/deck boxes are only placement aids; do not use them as a manufacturing fit reference.
- Display: 60 wide × 38.4 tall, 0.6 gap from lid. Aluminum shell's front is `y=-4.5` and back `y=0.4`; 0.3 glass is seated *inside* the shell with its outer surface flush at `y=-4.5`. Nominal detachable thickness **4.9**. Front glass seat is conceptual; panel and driver PCB still unselected.
- Permanent mount: 30-high, 1.2-thick magnetic stainless plate bonded on a 24-wide lid strip with 0.4 tape, cantilevered beneath the detachable screen. Four 5 × 1 magnets in the screen back; magnetic strength, steel grade, retention under shock and interaction with MacBook magnets **not verified**.
- **Isolated connector:** one full-thickness rectangular window in steel contains a dielectric polymer insert. A 0.35-thick rear lip retains it against screen-side removal. An additional 0.15 gap to the steel surrounds its core; the four individually separated metal pad-and-via envelopes have >=1.0 polymer margin on the core and >=0.64 polymer web between pad wells. Counterpart pogo contact envelopes sit in separate shell bores and touch the pad faces only at the nominal assembly plane. Steel never intersects contacts in CAD. A real pogo part, dielectric material, positioning features, adhesive, lead routing and mating spring force are **not yet specified**. The via ends on the carrier rear would connect to an insulated flex circuit; the flex circuit is **not modeled**.
- **Cable exit:** nominal 3-mm cable goes through a 4.5-mm-wide **bottom-open through-notch** in the plate, with a separately modeled insulating elastomer sleeve (4.0 outer diameter, 3.16 bore, 1.5 projection below the plate). Cable centerline `y=3.0` keeps the nominal route behind the lid and out of steel; no tape/lid/steel collision in nominal geometry is the design requirement. The 12-mm nominal bend radius is a *static* routing assumption, not a cable manufacturer's fatigue or dynamic bend rating. Sleeve adhesion/retention, strain relief and four-core termination remain to be designed.
- Stack from the screen front to the dielectric rear retention lip is **6.45 mm**, under the nominal 6.5-mm envelope; this does **not** include localized cable protrusion, tolerances or internal electronics. This is not proof of a buildable 4.9-mm device.
- Electrical: four mechanical contacts carry nominal **USB 2.0 VBUS/GND/D+/D-**, not USB 3 or Thunderbolt. The USB-C plug still needs a correct CC configuration, power-budget compliance, D+/D- impedance control, shield/ground strategy, ESD protection, rated contacts, verified insulation resistance and appropriate disconnect sequencing. **No power should be applied based on CAD alone.** These are contact *envelopes*, not a completed schematic.

## Open: hinge cable movement (high-priority blocker)

`cable_report()` prints **geometric free-span excess over endpoint chord**, NOT verified usable slack. `params.slack_needed()` is an **arc-length proxy** based on an unverified hinge and rotation angle, NOT a measured demand. Both are insufficient to ensure the cable remains untensioned, avoids pinch points or survives repeated opening/closing.

Illustrative sensitivity with the nominal model: at 90° and 150° nominal hinge sweep, the proxy demand changes substantially; moving assumed hinge Y also changes the estimate (see `test_slack_estimate_is_sensitive_to_unmeasured_hinge`). The original PR estimated ~7.9 mm chord excess vs ~22 mm at a guessed 135°; changing the cable plane alters the proxy again, but **does not close the deficit or establish a safe range**. A specific flexible cable and a controlled service loop/strain relief should be selected **after** measuring actual MacBook hinge location, USB-C receptacle position, maximum lid angle and swept envelope. Validate the prototype at closed, intermediate and maximum angles before supplying power. Do not use elastic cable stretch as a design requirement.

## CAD validation / limitations

From the repository root:

```sh
python -m unittest discover -s tests -v
python -m pip install build123d==0.13.0
python -m unittest discover -s tests -p 'test_mount_geometry.py' -v
(cd cad/slab/src && python mount.py && python export_parts.py)
```

The independent pure-Python clearance tests run without a CAD installation; the solid-level tests run with `build123d` (also in the CAD CI job). The exporter deletes **only generated STLs** from `cad/slab/tmp/parts/` before regenerating them, preventing stale assembly parts from contaminating renders. `tools/render.py` produces a static nominal layout, not a hinge-motion simulation: the cable cannot deform if lid and deck are rotated as rigid solids. Treat renders as illustrations only, not clearance evidence. An actual toleranced assembly, visual/fit check, multimeter continuity/insulation tests and repeated hinge cycling are still required.
