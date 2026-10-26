# CAD, printer and physical fit

The original [parametric OpenSCAD source](../cad/desk-buddy.scad) produces a small **open-back desktop shell** (not a locked enclosure) and a separate **window-fit test coupon**.

**Local geometric validation (2026-10-26):** OpenSCAD 2021.01 rendered both as one connected, watertight STL each. The shell outer dimensions were **90 × 57 × 81 mm**; coupon **40 × 40 × 2.8 mm**. These facts do **not** establish mechanical fit or support-free FDM printability.

The default OLED window is **21.5 × 11 mm** (visible aperture), whereas the cheap OLED PCB is nominally **26.1 × 26.1 mm**, with exact panel location unknown. Do not confuse active viewing area with circuit-board dimensions. The case intentionally has no unverified screw holes or snap-clips. Start with removable, electrically insulating fixture material **on the PCB perimeter**, avoiding display glass, heat sources, connector contacts and the MacBook.

## Workflow

1. Identify the **actual Bambu printer model** from its display/label. The provided Bambu Academy URL does not establish which printer it is.
2. Measure the purchased OLED PCB, viewing area and header offset, ESP32 board, USB connector and cable bend radius with a caliper.
3. In OpenSCAD, set <code>part = "fit_coupon"</code>; render with F6 and export an STL. Print this tiny test first.
4. Adjust <code>window_w</code>/<code>window_h</code>, enclosure dimensions and tolerances, then set <code>part = "shell"</code> and export STL.
5. Slice using the actual printer profile in Bambu Studio. Start with PLA / 0.2 mm layers / 3 walls / ~15% infill; these are **proposed starting parameters**, not a validated print profile.
6. Inspect preview for the **top cavity roof bridging and the front screen window**. The shell may need an alternate orientation and/or supports: **watertight mesh is not evidence of support-free printing**.
7. Print, measure and physically fit. Revise CAD and document results. Keep ventilation and cable strain relief.

No battery, heat-set inserts or powered servos are included in the initial enclosure. A later release should add actual PCB standoffs, retention features, access cover and measured printer tolerances.
