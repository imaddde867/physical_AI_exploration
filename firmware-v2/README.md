# MacDesk Buddy · Waveshare AMOLED V2 bench renderer

Target: **ESP32-S3-Touch-AMOLED-1.64 V2, SKU 31197**. Experimental software;
no hardware bought, flashed or physically tested as of 2026-10-29.
The GC9A01 project in `../firmware` is unchanged and has a different binary.

## Inspect on a Mac without hardware

From the repository root (Python 3.11+):

```sh
python3 -m tools.amoled_face
open assets/amoled-preview.html
python3 -m unittest discover -s tests -v
python3 tools/check_repository.py
```

There is also a **live simulator** (`sim/`, purely additive): a mini-app is one
Python file defining `update(screen, t_ms)`, drawn each frame into the same
quantized 456×280 view at a configurable fps cap (default 30):

```sh
sim/run.sh experiments/hello_buddy.py      # populates a tkinter window
sim/run.sh experiments/hello_buddy.py --fps 30 --scale 1 --frames 0
```

On this Mac use `sim/run.sh`: the system Python's bundled Tk 8.6.8 opens windows
that stay blank, so the launcher points the uv Python's Tcl/Tk at its own
libraries. Install that interpreter first with
`brew install uv && uv python install 3.12`. Browser pixels and sim pixels still
prove nothing about panel color, brightness or timing.

You can also open the checked-in HTML directly. It is self-contained, uses no
network, and starts paused at neutral. Select a mood, hold blink, scrub time or
play its fixed 12-second loop. Blink intervals are `[4000,4135)` and
`[9000,9135)` ms. The canvas expands the **same RGB565 colors** sent by firmware.
The native-resolution [PNG](../assets/face-idle-456.png) is the neutral asset;
its source palette retains the original RGB colors before RGB565 quantization.
Browser pixels are not a physical scale or color calibration.

## Character composition and preset study

The source remains the SHA-pinned [approved character](../assets/face-idle-240.png).
The landscape adaptation is authored here: uniform 1.5× sampling, positioned at
`(48,-40)` on a 456×280 black canvas. It removes the almost-black round-head arc
and preserves the heavy lids, textured cool eyes, warm highlights, asymmetry and
small mouth. It does not stretch the eyes or replace them with geometric emoji.
At this source resolution, some pixel texture remains visible when enlarged.
Six existing protocol moods retain their small mouth cues; sleepy and local
blink close the eyes. These cues are intentionally modest, not six new faces.

[FluxGarage RoboEyes](https://github.com/FluxGarage/RoboEyes) was reviewed as a
premade reference for separating mood, eye closure and idle timing. Its configurable
monochrome shapes are unsuitable for preserving this raster identity. No RoboEyes
code/artwork or GPL dependency is incorporated. The vendor's LVGL preset informed
the panel setup and rotation approach; its widgets/demo artwork is not bundled.
Our composition, RLE format, preview and strip renderer are independently authored.

## Build, do not infer a working screen

```sh
python3 -m pip install 'platformio==6.2.0'
python3 -m platformio run -d firmware-v2 -e waveshare_amoled_v2
```

This is a separate **ESP-IDF** project, not an Arduino alias for the round board.
PlatformIO `espressif32@6.12.0` selects ESP-IDF 5.5.0 and pins its framework/toolchains.
The vendor ESP-IDF reference records 5.5.2; this keeps the same 5.5 API family
without upgrading the unmodified driver to ESP-IDF 6. The reference config
uses 8 MB flash. This renderer does not need PSRAM, touch, Wi-Fi, LVGL or sensors.
The USB Serial/JTAG console is selected on ESP32-S3 native USB; actual Mac port
enumeration and command delivery still need the board. No upload runs here.

| Setting | Exact V2 reference / implementation |
|---|---|
| QSPI | SPI2, mode 0, 40 MHz; CS 46, CLK 10, D0–D3 11–14; reset 21 |
| Native panel | 280×456, RGB565, RGB element order |
| Address window | Native X + `0x14`, applied exactly once |
| Landscape | Software map `(x,y) → (279-y,x)`; no unsupported `swap_xy` |
| Wire bytes | RGB565 MSB first, matching vendor `LV_COLOR_16_SWAP=1` |
| Draw alignment | Full 280-pixel native width; two-row strips, even starts/exclusive ends |
| Buffer ownership | 1120-byte internal DMA strip; completion semaphore before reuse |
| Init | Entire eight-command V2 override, reset/init/display-on in vendor order |
| Brightness | Vendor `0x51` via `0x02` QSPI opcode; 64 on start/valid command, 16 after 60 s, 0 after 5 min |

Brightness values are register values, not nits. Blanking uses brightness zero;
it is not tested deep sleep or a guarantee against image retention. Valid face
commands wake/reset idle timing; malformed/unsupported requests do not.

USB JSONL retains `{"cmd":"face","value":"neutral"}` and the six existing names.
Lines are capped at 255 bytes, overflow is dropped through newline, invalid JSON,
NUL bytes and unknown values are rejected. Startup reports `init_sent_unverified`.
There is no touch, text command, battery/music adapter or motion event in this build.

See [vendor provenance](src/vendor/README.md) for the pinned driver and limits.

## What software checks establish

The stdlib Python tests regenerate all assets and decode all twelve states (six
moods × open/blink). A host C compiler runs **the actual firmware RLE/strip core**;
all 127,680 pixels per state are compared byte-for-byte with the expected rotated
RGB565 output. Tests cover fixed blink boundaries, margins, invalid frame index,
HTML parity, approved-source identity and unmodified vendor-driver hashes.
Compilation establishes ESP-IDF API compatibility and linking, not illumination.

## Board-arrival checks still required

Run the pinned official V2 example first and photograph board/revision markings.
Then bench-test this separate binary: color bars/red/blue ordering, offset edges,
landscape direction and cable orientation, all six moods/blinks, tearing/flicker,
USB reconnect/overflow/recovery, actual DMA latency, modest brightness and
idle dim/blank/wake. Compare with the preview; reverse the software quarter turn
only if the physical mounting demands it. Record measurements before automatic
Mac events or an enclosure. Physical colors, panel identity, power sequencing,
brightness, fit and sustained operation remain unknown until then.
