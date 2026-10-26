# Round color face — printing and mechanical fit

The source [desk-buddy.scad](../cad/desk-buddy.scad) now models a **circular face opening**, a subtle front bezel, a rounded enclosure and an open-back service cavity. There is also a separate **fit_coupon** part to print before the full housing.

For visual realism, inspect the [dimensional front-view illustration](../assets/actual-scale-front.svg) before deciding whether the screen is big enough: **31.4 mm aperture / 72 mm body width = 43.6%**. The approved PNG represents **screen pixels**, not the relative size of the finished enclosure. Smaller body dimensions would require verifying internal board and cable clearances.

**Manufacturer/seller nominal dimensions:** active round LCD diameter 32.4 mm; external display board about 44×36×5 mm. The default visible aperture diameter is **31.4 mm** to hide the extreme screen edge and the display PCB. The LCD must sit behind the front wall, with its active area centered on the opening.

**Local geometrical checks (2026-10-26):** OpenSCAD compiled both configurations. Watertight meshes with one connected component: shell outer bounds **82×54×78.5 mm**; coupon **47×47×2.8 mm**. This is **not a verified part fit**, and not a tested Bambu Studio slicing profile.

## Steps

1. Identify the exact Bambu Lab printer from the physical machine label or display. The Academy URL does not establish the model.
2. Obtain the actual LCD module and measure PCB, viewing-glass location, header protrusion and wire bend radius with a caliper.
3. Open the SCAD in OpenSCAD; set **part = "fit_coupon"**, render F6 and export STL. Print this small circular-window sample first.
4. Revise **opening_d**, **face_height**, body dimensions and tolerances if needed. Set **part = "shell"**, render F6 and export STL.
5. Import the exported model into Bambu Studio with the correct printer profile, inspect the enclosed top bridge and circular front face overhang for supports; choose the lowest-risk orientation.
6. Use PLA, ~0.2 mm layers, 3 walls and ~15% infill as **initial slicing suggestions**, not validated settings.
7. Print, photograph the assembly, and test actual LCD and connector clearances. Avoid touching or trapping LCD glass. For a durable version, design proper mounts/standoffs after measuring the real PCB.

The [actual approved 240×240 sprite](../assets/face-idle-240.png) is firmware's idle screen source; it is enlarged by browsers and is not a photograph of the real LCD. The [dimensioned aperture diagram](../assets/actual-scale-front.svg) describes geometry, **not** a second character design. Final aesthetics depend on actual filament finish, screen black-level, backlight, fit and print quality.
