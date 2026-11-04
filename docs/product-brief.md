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
| Simulator | 800×600 RGB565 drawing, approximate physical scale, animation examples | Final panel resolution, real refresh rate, brightness, and final face |
| Host/device software | Draft messages, validation, and watchdog helper | Running Mac service, serial transport, firmware, and hardware integration |
| Hardware | Ordered: Waveshare RP2040-Touch-LCD-1.69 (BerryBase order 1097674) | Delivery, first light, frame rate, sleep/wake behaviour; final power circuit and connectors |
| Printing | Concept meshes can be exported | Printable enclosure, printer/profile/material details recorded in this repo, tolerances, and fit tests |

The previous Good Display GDOJ0269C01 / ESP32-P4 proposal is **on hold**. Its dimensions still drive the concept and simulator defaults; that does not lock the product to this hardware. The last [hardware log](hardware/bringup-log.md) reopens panel selection. No procurement or hardware build is established by the records reviewed here.

**Ordered prototype hardware (2026-11-04):** Waveshare RP2040-Touch-LCD-1.69 (BerryBase WS-28161, order 1097674): 1.69" capacitive touch display with an integrated RP2040 (133 MHz, 264 KB SRAM, 16 MB flash). €19.90 + €9.90 DHL shipping = **€29.80** delivered to Finland, on the €30 target. This replaces the Pico WH + Pico-LCD-1.8 + CU0240 basket in the [budget report](../reports/Budget%20companion%20learning%20hardware.md#final-basket-2026-11-04), which was never ordered. No cable was bought: use the existing 50 cm Apple USB-C to USB-C cable (power + data) and find a shorter one later. Resolution, pinout and the firmware path are not yet checked; read Waveshare's wiki for this board first. The [display shortlist report](../reports/Companion%20display%20hardware%20shortlist.md) remains background evidence.

## Next decisions, in order

1. Wait for delivery. Meanwhile read the Waveshare wiki for the RP2040-Touch-LCD-1.69 (panel resolution, driver, MicroPython/C demos).
2. Run Waveshare's demo, then a blink, then one Mac serial command over the 50 cm USB-C cable. Do not freeze final CAD from board width and height alone.
3. Prove the display works on the bench. In parallel, collect the [real Mac measurements](hardware/measure-mac.md), printer model/profile/material, and a physical cable-route test. The user says the printer is known; its details were not found in the reviewed repository.
4. Adapt the enclosure and mount around actual hardware, then print a fit prototype. Check lid movement, magnet retention, contacts, assembly access, and strain relief before final print files.

The current cable route has a documented slack shortfall; do not treat the rendered bend as validated. The current body is an exterior concept, not a hollow, ready-to-print electronics enclosure. See [CAD decisions](../cad/slab/DECISIONS.md).

## Where to work

- `cad/slab/src/placement.py`: current assembly; `mount.py`: geometry; `params.py`: dimensions and assumptions.
- `sim/` and `experiments/`: active face/animation exploration. Keep the motion and quality demos as diagnostic examples.
- `daemon/protocol.py` and [protocol draft](protocol.md): candidate software boundary; tests do not imply an implemented device.
- `docs/superpowers/`, [old slab decisions](archive/2026-11-01-slab-decisions.md), and `scale_compare.py`: historical or paused work; use their status notices before following them.

The reset preserves existing uncommitted work and historical files. The prototype board is ordered (not yet delivered). No history is deleted, and no commit is implied by this brief.
