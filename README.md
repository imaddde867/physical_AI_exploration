# MacDesk Buddy

A slim display companion beside a 14" MacBook Pro lid, with silver framing and black front glass. The first version is an animated companion; useful widgets can follow gradually.

Start with the [current product brief](docs/product-brief.md): approved direction, first-version scope, open decisions, and next steps. The physical appearance was approved on 2026-11-04; electronics fit and print readiness remain unresolved. The ordered bench prototype is the Waveshare RP2040-Touch-LCD-1.69; final enclosure hardware is not frozen.

Current character: [planted 3D character and animation handoff](animation/README.md).
Hardware next step: [ordered prototype bring-up](docs/hardware/shortlist-handoff.md).

| Area | Current entry point | Status |
|---|---|---|
| Physical design | [CAD decisions and commands](cad/slab/DECISIONS.md) | Approved appearance; concept geometry |
| Character | [Blender library](animation/README.md) | Eight validated states, planted claw contacts, 30 FPS exports |
| Earlier face experiments | `sim/` and `experiments/occupant_idle.py` | Approved 2D checkpoint retained |
| Hardware | [Bring-up log](docs/hardware/bringup-log.md), [Mac measurements](docs/hardware/measure-mac.md) | Waveshare RP2040-Touch-LCD-1.69 ordered; no recorded first light |
| Device prototype | [Local blink setup](firmware/rp2040/README.md) | Prepared MicroPython blink; hardware validation awaits delivery |
| Communication | [Draft protocol](docs/protocol.md), `daemon/protocol.py` | Codec, watchdog, and host line-transport helper tested; no running service or device command handler |

Older simulator plans in `docs/superpowers/`, the [November 1 slab record](docs/archive/2026-11-01-slab-decisions.md), and `cad/slab/src/scale_compare.py` are historical references. The removed 1.64" pod work remains in git history.

## Live desktop simulator

A mini-app is a Python file defining `update(screen, t_ms)`. The preview preserves the ordered prototype's full 240×280 portrait source and RGB565 color quantization. On macOS it uses a native AppKit viewer, Python 3 and Swift from Apple's Command Line Tools (`xcode-select --install` if missing); uv and Tk are not needed. The first launch can spend about a minute compiling Swift.

```sh
sim/run.sh experiments/hello_buddy.py
```

The black display area targets **27.972 × 32.634 mm**, not the PCB or enclosure dimensions. This is about 218 pixels/inch. The [vendor panel specification](https://www.waveshare.com/wiki/1.69inch_Touch_LCD_Module) lists 262K (18-bit) colors; our RGB565 renderer uses 65,536 colors at the same 240×280 resolution. The preview does not establish actual panel color, brightness, or corner clipping.

macOS derives logical points/inch from `NSScreen` width and `CGDisplayScreenSize` physical width, and recalculates when the window moves between screens or the display mode changes. Apple's [14-inch MacBook Pro specification](https://support.apple.com/en-gb/121552) gives a 14.2-inch, 3024×1964 physical panel at 254 pixels/inch. Logical points and backing pixels depend on the selected display mode: this Mac reports 1800×1169 logical points and 3600×2338 backing pixels, giving about 151.5 logical points/inch and a 166.841×194.648-point preview.

Verify the **black area only**, excluding the title bar and status strip, with a ruler; display metadata can be rounded. `--ppi` overrides detected logical points/inch: use `new_ppi = detected_ppi × target_width / measured_width`, with both widths in the same units. `--width-mm` changes the target width. `--scale 1` overrides physical sizing with one logical point per source pixel; it is not one native display pixel per source pixel.

Other platforms use the approximate Tk fallback. Run `python3 -m sim.runner experiments/hello_buddy.py` with Python and Tk installed, and calibrate `--ppi` with a ruler.

## CAD

`cad/slab/src/placement.py` is the current assembly (build123d via cadgen); it uses `mount.py` and `params.py`. Rebuild/export/render commands are in the [CAD decisions](cad/slab/DECISIONS.md). Files under `cad/slab/tmp/` are generated previews, not manufacturing deliverables.

## Tests

```sh
python3 -m unittest discover -s tests -v
```
