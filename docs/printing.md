# Printing the enclosure

`cad/desk-buddy.scad` is an **original parametric desk stand**, not a creator-provided STL. It contains a vented enclosure with an open service back and separate face bezel. The display and board are initially mounted with removable adhesive/foam or small printed spacers: final standoffs/holes require measured board dimensions.

1. Check the exact **Bambu printer model** at the machine. The shared Academy link is not proof of the printer model.
2. Measure your actual OLED PCB, module visible area, ESP32 development board, USB port/cable clearance and available headers. Do not rely on internet nominal dimensions.
3. Install OpenSCAD; open the SCAD and adjust `body_w`, `body_h`, `body_d`, `screen_w`, and `screen_h`.
4. Render with F6 and export STL. Check fit and layer orientation in Bambu Studio.
5. Default prototype: PLA, 0.2 mm layers, 3 perimeters, ~15% infill; print the hollow shell open-back down where practical, verify bridges/support preview.
6. Print a low-cost fit-check bezel or small draft first. Keep ventilation and USB cable strain relief. Never enclose a LiPo battery in this initial design.

The CAD does **not** yet guarantee a snap-fit or safe retention of a specific OLED or ESP32-S3 SKU. Measure and revise before final assembly.
