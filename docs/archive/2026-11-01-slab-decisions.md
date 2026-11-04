> Historical design and research record, preserved during the 2026-11-04 reset.
> Superseded for current scope by [the product brief](../product-brief.md) and
> [current CAD decisions](../../cad/slab/DECISIONS.md). Prices, stock, electrical
> claims, and dimensions below were not re-verified during the reset.
> `src/` and `tools/` paths below refer to `cad/slab/`.

# Slab buddy: decisions (2026-11-01)

Replaces the 48 mm chunky pod on the 1.64" AMOLED. Reason: thick bezels and body around a 36x22 mm
active area looked cheap next to a 312.6 mm MacBook Pro lid. Targets: AMOLED-like edge-to-edge glass,
silver aluminium, readable size.

- **Use cases:** always-on face with idle animations, nudge-to-wake, awareness of the Mac (cursor-following
  eyes, video, music-reactive), Claude Code / Codex usage %, lyrics, AI chat view.
- **Panel:** Good Display GDOJ0269C01 AMOLED (a -T01 touch variant exists; touch not needed, non-touch variant to be checked).
  RM69700, 2-lane MIPI-DSI, 800x600, 30-pin 0.35 mm FPC, rails 1.8/3.0/+4.6/-2.0/+6.8 V. Glass 56.6 x 47.25 mm, visible
  54.6 x 40.95 mm. Chosen by the user after viewing a 1:1 render.
- **Size:** outer 59.0 x 49.65 mm at an assumed 1.2 mm frame wall (slab is allowed to grow; user confirmed), 4.9 mm thick.
- **Compute:** the Mac daemon does the thinking (usage stats, lyrics, chat, animation logic). A thin custom board inside the
  screen part (ESP32-P4 module + panel power) renders the face from small commands and drives the panel over MIPI-DSI. It
  cannot live in the plate or cable end: the pogo link carries only VBUS/GND/D+/D- (USB 2.0) and DSI cannot cross it.
- **Host link:** the Mac (14" M4 base, Nov 2024) has three Thunderbolt 4 USB-C ports (Apple tech specs; TB5 is M4 Pro/Max only) and accepts USB 2.0 devices, so the USB 2.0 pogo link is fine.
  The plug still needs a 5.1 kOhm pull-down on CC or the Mac may not supply 5 V.
- **Power/sleep:** the buddy sleeps with the Mac and blanks when VBUS drops or the daemon disconnects. With the lid closed,
  if the tilt makes the slab touch the surface, the user detaches it.
- **Placement:** flush side-car on the lid's right edge. Gap 0.6 mm, back and display plane flush with the lid,
  top edge 1/4 of the lid height (about 53 mm) below the lid top. Assumed reading of "1/4 of the screen
  height"; adjust `placement.py` if the buddy centre was meant instead. Not re-rendered after this change.
- **Mount (decided 2026-11-01, modeled in `src/mount.py`, numbers in `src/params.py`):** a permanent 30 mm tall
  stainless plate (1.2 mm) is stuck to the lid back with 0.4 mm tape on a 24 mm strip at the right edge and cantilevers
  under the screen part. The screen part's back sits on the plate (4 magnets 5x1 mm in its back, 4 gold pads for
  VBUS/GND/D+/D-, so the snap interface is USB 2.0 + 5 V, enough for a small display). Pull it off and only the plate stays.
  Screen part is 4.9 mm thick (glass flush with the lid front); screen + plate is 6.1 mm behind the front plane.
- **Connectivity and power:** one fixed USB-C cable (3 mm, 12 mm minimum bend radius on every bend) leaves the plate's
  bottom edge, runs down the lid back, leaves the lid sideways at z = 19.75 mm above the hinge so the last bend can drop
  onto a right-angle plug in the right-side Thunderbolt port. About 183 mm. No battery, no Wi-Fi.
- **Look:** black edge-to-edge glass, hairline aluminium frame, rear arm + clip hidden behind the lid.

## Round-3 research (ChatGPT, 2026-11-01): verdict PARTLY, no public GDOJ bring-up exists
- **Init:** only a related RM69700 800x600 Linux driver (i.MX8MN) is public: 7 vendor GEN writes (FE 40/24 50/47 13/FE 50/C0 20/FE 60/95 CE),
  FE 00, soft reset, C2 0B (video mode), 35 00, 3A 77, 11, 53 20, 55 00, 36 82, 29. Not verified for GDOJ. Its short reset-to-sleep-out delay
  conflicts with the RM69700 datasheet (RESX rising to Sleep-Out > 120 ms; T4 OTP reload >= 10 ms, T9/T10 >= 2 frames, T13 >= 2 ms off). Use the datasheet.
- **Timing (experimental start):** 800x600 RGB888, HSA/HBP/HFP 128/88/40, VSA/VBP/VFP 4/8/16, total 1056x628, 2 lanes burst video. 50 Hz (Good Display typical)
  needs ~33.16 MHz pixel clock; 60.32 Hz needs 40 MHz. 60 Hz on this panel NOT verified.
- **ESP-IDF trap:** `esp_lcd_panel_io_tx_param()` on DSI sends DCS writes; the vendor sequence needs generic writes (0x23). Needs a custom low-level path.
- **Power:** PMIC behind SWIRE still unidentified. SGM3838 (WLCSP 2.5x2.5 mm, 3 rails) is a candidate only; defaults 4.6/-3.0/7.3 V differ from the panel's 4.6/-2.0/6.8 V.
  Do not attach the panel until the five rails are verified on a current-limited bench supply.
- **Connector:** 30-contact 0.35 mm Molex SlimStack board-to-board, not FPC/ZIF; Molex 5052743012 is a candidate, verify mating vs 5052743040. Mated height ~0.8-0.9 mm.
- **Controller board:** M5Stack Stamp-P4 (29.8x22.0x4.3 mm, 2-lane DSI, USB 2.0 OTG) for the bench. Bare P4 QFN is 10x10x0.9 mm but needs a custom PCB. The 4.3 mm module does not fit the 4.9 mm
  stack with the panel, so the final board is a custom thin PCB.
- **Panel:** GDOJ0269C01-T01 about $35, 0 in stock. Non-touch variant not found.
- **Decision:** bench first (Stamp-P4 + current-limited power breakout + panel). Buy and print nothing for the final slab before first light.

## Mac measurements from public sources (14" M4, Nov 2024; model of record)
- Published (Apple tech specs): 312.6 x 221.2 x 15.5 mm closed, 1.55 kg, three Thunderbolt 4 ports, MagSafe 3, HDMI, SDXC, headphone jack, 135 degree hinge range per a review site.
- Port order (iFixit, Tom's Hardware, photographed), rear to front: LEFT MagSafe 3, TB4, TB4, headphone; RIGHT HDMI, TB4, SDXC. So the right-side TB4 port is
  the second from the rear, behind the HDMI; the cable plan targets it. Side bezels about 3.4 mm (third-party), 135 degree hinge (review, M4 Pro).
- Lid magnets: the 2021 model has 6 in the display housing (Apple Recycler Guide); M4 count unknown. Lid is aluminium (non-ferromagnetic), so a steel plate is
  attracted only by the lid's own magnets, which must be tested with a steel piece.
- Bare USB-C sink with 5.1 kOhm CC gets 5 V by the standard, USB 2.0 default 500 mA; sleep-state VBUS on this Mac is unverified (measure with the USB-C meter).
- NOT published anywhere found: lid thickness, lid height, hinge axis, port centre offsets and heights, corner radius, closed-lid overhang. The CAD values for these stay ASSUMED until measured with calipers (`docs/hardware/measure-mac.md`).

## Open
- Panel init validation on a bench, the power chip behind the SWIRE pin, frame wall
  thickness (1.2 mm assumed), thin controller board stack height (4.9 mm may not fit it), cable slack (below).
- **Cable slack vs lid swing:** the route has about 7.9 mm of free-span slack, but a 135 degree lid swing at a 9.4 mm hinge
  lever needs about 22 mm. Options: add a service loop, exit lower (shorter lever), or use a cable that stretches/coils.
  Prototype with string before trusting this.
- ASSUMED, measure on the real Mac: right-side port 45 mm from the rear edge, lid thickness 4.5 mm, hinge axis position,
  and whether the lid's own magnets disturb the plate's magnets or pull on a steel plate.
- Pogo pads limit the detachable link to USB 2.0 (a real USB-C blind-mate would be needed for USB 3/Thunderbolt data).
- Not yet designed: how the cable is held on the lid back (clips/tape), screen-part electronics volume.
- MacBook model is a simplified slab (lid height 214 mm, bezels assumed). Only width/depth are published.
- Face art: old designs discarded 2026-11-01; placeholder is two round eyes (`experiments/hello_buddy.py`). Real face still to design.

## Files
- `src/placement.py`, `src/scale_compare.py` (60/70/80 vs lid, historical), `src/export_parts.py` (STL per part)
- Renders and STLs (regenerable, gitignored `tmp/`): Blender script `tools/render.py` (regenerate with `cadgen run src/export_parts.py`
  then `Blender -b -P tools/render.py`). Run cadgen via `~/.local/bin/cadgen +0.8.4 run`.
