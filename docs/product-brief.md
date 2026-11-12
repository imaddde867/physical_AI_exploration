# MacDesk Buddy: current product brief

Updated 2026-11-04. This is the starting point for current product scope. CAD numbers live in `cad/slab/src/params.py`; historical research is evidence to revisit, not a purchasing decision.

## Approved direction

A small animated companion beside the right edge of a 14" MacBook Pro screen. Preserve the appearance approved from the front, close-up, and rear renders on 2026-11-04: black front glass, slim silver framing, and a rear mount mostly hidden from the front.

The current concept is about 59 × 49.65 mm, with a 0.6 mm gap from the lid. These proportions are the visual baseline; exact dimensions and materials may change to fit real hardware. The silver/aluminum appearance does not mean the final frame is already manufacturable or directly printable.

The display is intended to detach magnetically. The adhesive-mounted plate and USB cable stay on the laptop. Contact geometry exists, but the spring contacts, retention, electrical connection, and safe attachment/detachment are not yet engineered or tested.

## First working version

The user selected **animated companion only initially**, with other features added gradually. This is also a first hardware/IoT/physical-AI learning project: target **about €30 all-in**, with slight flexibility; stretch toward **€50 only for worthwhile future reuse**, not appearance alone.

- Show a character with idle animation and blinking; its visual style and personality remain open. The two round eyes in `experiments/hello_buddy.py` are a placeholder.
- Use the simulator to settle the face and animation before porting to a real display.
- Start with ordinary USB data/power from the Mac and an optional simple desk holder. Thin packaging, magnetic attachment and electrical contacts are deferred until after a working prototype; the approved long-term appearance remains the goal. Sleep, wake, and disconnect behavior need device validation.
- Success means the selected physical display runs the chosen character reliably, followed by a mount/fit prototype that works on the real laptop.

Claude/Codex usage meters, a focus timer, lyrics, and chat are later candidates, not first-version requirements or commitments to a delivery order. Other ideas from the old notes (cursor following, music reactions, nudge-to-wake, notifications, and home automation) remain optional. Touch, microphones, speakers, cloud APIs, wireless connectivity, and batteries are not required by this first-version brief. Revisit them only for a chosen behavior.

## Current evidence and limits

| Area | What exists | What is not settled |
|---|---|---|
| CAD | Display exterior, magnets, rear plate, contact pads, cable, plug, simplified laptop | Electronics cavity, closures, real contact assembly, manufacturing tolerances, and cable fastening |
| Simulator | 240×280 portrait RGB565 drawing for the ordered prototype, native macOS physical sizing, animation examples | Real refresh rate, brightness, and final face |
| Host/device software | Draft messages, validation, watchdog helper, and [local blink prototype](../firmware/rp2040/README.md) | Running Mac service, serial transport, and hardware validation |
| Hardware | Delivered: Waveshare RP2040-Touch-LCD-1.69 (BerryBase order 1097674) | Bench measurements, frame rate, sleep/wake behaviour; final power circuit and connectors |
| Printing | Concept meshes can be exported | Printable enclosure, printer/profile/material details recorded in this repo, tolerances, and fit tests |

The previous Good Display GDOJ0269C01 / ESP32-P4 proposal is **on hold**. Its dimensions still drive the CAD concept, while the simulator now follows the ordered prototype. The [hardware log](hardware/bringup-log.md) records the earlier panel-selection pause; no first-light results or final enclosure fit are recorded.

**Ordered prototype hardware (ordered 2026-11-04, delivered 2026-11-12):** Waveshare RP2040-Touch-LCD-1.69 (BerryBase WS-28161, order 1097674): [1.69" 240×280 capacitive touch display](https://www.waveshare.com/product/rp2040-touch-lcd-1.69.htm) with an integrated RP2040 (133 MHz, 264 KB SRAM, 16 MB flash). €19.90 + €9.90 DHL shipping = **€29.80** delivered to Finland, on the €30 target. This replaces the Pico WH + Pico-LCD-1.8 + CU0240 basket in the [budget report](../reports/Budget%20companion%20learning%20hardware.md#final-basket-2026-11-04), which was never ordered. No cable was bought: use the existing 50 cm Apple USB-C to USB-C cable (power + data) and find a shorter one later. Pinout, driver setup and the firmware path still need bring-up checks; read Waveshare's wiki for this board first. The [display shortlist report](../reports/Companion%20display%20hardware%20shortlist.md) remains background evidence.

## Device renderer plan

Render the face locally from small commands; do not stream desktop frames. Start with one packed RGB565 framebuffer: 240 × 280 × 2 = 134,400 bytes. Two buffers need 268,800 bytes, leaving only 1,536 bytes of the RP2040's 264 KiB SRAM for everything else, so double buffering is not a practical baseline. Keep room for runtime, stack and driver state; use a smaller working region if bring-up shows the chosen runtime needs it. The simulator uses a nominal 27.972 × 32.634 mm visible area (about 218 pixels/inch) from the [vendor panel specifications](https://www.waveshare.com/wiki/1.69inch_Touch_LCD_Module), not PCB dimensions. The native macOS viewer preserves all 240×280 source pixels and detects logical points/inch from display metadata; verify the black area with a ruler and use `--ppi` to calibrate if needed. RGB565 uses 65,536 colors versus the panel's advertised 262K (18-bit); resolution stays the same. Color, brightness and corner clipping still need hardware validation. See the [preview instructions](../README.md#live-desktop-simulator). Its Python lists of hex strings are desktop-only, not the device memory layout. A [local blink prototype](../firmware/rp2040/README.md) is prepared for the board. A host line-transport helper exists in `daemon/link.py`; device commands and end-to-end USB integration are not implemented.

## Next decisions, in order

1. Board delivered and flashed 2026-11-12. Record that session (free heap, orientation, colour, flicker) in the [bring-up log](hardware/bringup-log.md).
2. Run Waveshare's demo, then a blink, then one Mac serial command over the 50 cm USB-C cable. Do not freeze final CAD from board width and height alone.
3. Prove the display works on the bench. In parallel, collect the [real Mac measurements](hardware/measure-mac.md), [printer filament/profile](hardware/printer.md) (model recorded), and a physical cable-route test.
4. Adapt the enclosure and mount around actual hardware, then print a fit prototype. Check lid movement, magnet retention, contacts, assembly access, and strain relief before final print files.

The current cable route has a documented slack shortfall; do not treat the rendered bend as validated. The current body is an exterior concept, not a hollow, ready-to-print electronics enclosure. See [CAD decisions](../cad/slab/DECISIONS.md).

## Where to work

- `cad/slab/src/placement.py`: current assembly; `mount.py`: geometry; `params.py`: dimensions and assumptions.
- `sim/` and `experiments/`: active face/animation exploration. Keep the motion and quality demos as diagnostic examples.
- `daemon/protocol.py` and [protocol draft](protocol.md): candidate software boundary; tests do not imply an implemented device.
- `docs/superpowers/`, [old slab decisions](archive/2026-11-01-slab-decisions.md), and `scale_compare.py`: historical or paused work; use their status notices before following them.

The reset preserves existing uncommitted work and historical files. The prototype board was delivered and flashed on 2026-11-12. No history is deleted, and no commit is implied by this brief.
