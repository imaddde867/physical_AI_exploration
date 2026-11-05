# Slab buddy: current CAD baseline

Updated 2026-11-04. Product scope lives in the [product brief](../../docs/product-brief.md). The user approved the current exterior appearance; the hardware, contact mechanism, and manufacturing design are not frozen.

## Current geometry

`src/placement.py` is the assembly entry point. It uses `src/mount.py` for the display, mount, magnets, pads, cable, and plug, and `src/params.py` for dimensions. `src/scale_compare.py` is the historical 60/70/80 mm comparison, not the current design.

| Item | Current CAD value | Meaning |
|---|---|---|
| Display outline | 59 × 49.65 mm | Approved visual proportions; derived from the previous panel candidate |
| Body depth | 4.4 mm | Exterior concept; excludes the additional 0.3 mm front glass |
| Installed front-to-rear extent | 5.9 mm including glass and plate | Geometry target, not verified electronics capacity |
| Lid gap | 0.6 mm | Display on the right edge |
| Vertical placement | Top edge 55.3 mm below lid top | One quarter of the 221.2 mm lid height |
| Rear mount | 30 mm tall, 1.2 mm steel plate; 0.4 mm adhesive on a 24 mm lid strip | Plate and fixed cable stay on the laptop when the display detaches |
| Retention/contact concept | Four 5 × 1 mm magnets and four contact pads | USB power/data intent; spring contacts, wiring, alignment, and live detach behavior are not designed |
| Cable | 3 mm diameter, 12 mm modeled bend radius | Not validated for lid movement or strain relief |

The simplified laptop uses a 312.6 × 221.2 mm base footprint. Lid thickness (4.0 mm), lid height (221.2 mm) and port position/height come from Apple's drawing; hinge axis, opening angle and plug dimensions are still assumptions; record real values in the [measurement sheet](../../docs/hardware/measure-mac.md). The exterior body is solid concept geometry with magnet pockets, not a hollow electronics enclosure.

## Hardware status and open checks

- Waveshare RP2040-Touch-LCD-1.69 (240×280, integrated RP2040) is ordered for bench bring-up with the existing USB cable; electronics fit and final enclosure hardware remain unvalidated.
- Good Display GDOJ0269C01 / ESP32-P4 is a previous proposal, **not selected hardware**. Its dimensions remain in the CAD model to preserve the approved preview; simulator defaults now follow the ordered prototype.
- The recorded cable estimate gives about 7.9 mm free-span slack against about 26 mm estimated need for the assumed lid swing. Both are model estimates; test the route with string before redesigning it.
- Validate the full electronics stack, screen border, mounting retention, spring contacts, cable fastening, strain relief, heat, and lid clearance before final CAD.
- Confirm printer model, material, and print profile from the user before choosing manufacturing tolerances. Their details are not recorded here.
- Preserve the approved silhouette while adapting dimensions to actual hardware. Do not buy final parts or treat exported concept STLs as print-ready enclosure parts.

## Rebuild and preview

Run from the repository root with the installed text-to-CAD skill's pinned runtime (0.8.3 in this session):

```sh
~/.local/bin/cadgen +0.8.3 run cad/slab/src/placement.py
~/.local/bin/cadgen +0.8.3 run cad/slab/src/export_parts.py
/Applications/Blender.app/Contents/MacOS/Blender -b -P cad/slab/tools/render.py
```

`export_parts.py` writes the assembly to `tmp/current-draft.glb` and named concept meshes to `tmp/render-parts/`. The renderer writes `tmp/render_wide.png`, `tmp/render_close.png`, and `tmp/render_rear.png`. It keeps the CAD pose; the blue laptop screen is a presentation reference, not a detailed MacBook model. The buddy screen stays blank because its face is not selected yet.

Everything under `tmp/` is generated and gitignored. `tmp/current_preview.py` and `tmp/render_current.py` from the first review are superseded scratch helpers; use the source commands above. Existing temporary files are retained, not inputs to the current workflow.

The earlier [November 1 decisions/research record](../../docs/archive/2026-11-01-slab-decisions.md) is preserved for context. The [bring-up log](../../docs/hardware/bringup-log.md) contains later corrections and the panel-selection pause; dated prices and availability require fresh research.
