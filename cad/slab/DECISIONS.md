# Slab buddy: decisions (2026-11-01)

Replaces the 48 mm chunky pod on the 1.64" AMOLED. Reason: thick bezels and body around a 36x22 mm
active area looked cheap next to a 312.6 mm MacBook Pro lid. Targets: AMOLED-like edge-to-edge glass,
silver aluminium, readable size.

- **Use cases:** always-on face with idle animations, nudge-to-wake, awareness of the Mac (cursor-following
  eyes, video, music-reactive), Claude Code / Codex usage %, lyrics, AI chat view.
- **Architecture:** standalone with its own brain (MCU/SBC inside), fed by a Mac daemon over USB/Wi-Fi.
- **Size:** 60 mm wide (smallest of 60/70/80 compared), about 38.4 mm tall (16:10-ish), about 4.25 mm thick.
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

## Open
- No panel chosen. Waveshare's largest ESP32-S3 AMOLED board is 2.41" (600x450, 4:3), too small for 60 mm
  wide without visible border. Likely a bare ~3" panel plus a small controller board.
- **Cable slack vs lid swing:** the route has about 7.9 mm of free-span slack, but a 135 degree lid swing at a 9.4 mm hinge
  lever needs about 22 mm. Options: add a service loop, exit lower (shorter lever), or use a cable that stretches/coils.
  Prototype with string before trusting this.
- ASSUMED, measure on the real Mac: right-side port 45 mm from the rear edge, lid thickness 4.5 mm, hinge axis position,
  and whether the lid's own magnets disturb the plate's magnets or pull on a steel plate.
- Pogo pads limit the detachable link to USB 2.0 (a real USB-C blind-mate would be needed for USB 3/Thunderbolt data).
- Not yet designed: how the cable is held on the lid back (clips/tape), screen-part electronics volume (4.9 mm may not fit a panel + driver).
- MacBook model is a simplified slab (lid height 214 mm, bezels assumed). Only width/depth are published.
- Face art: old designs discarded 2026-11-01; placeholder is two round eyes (`experiments/hello_buddy.py`). Real face still to design.

## Files
- `src/placement.py`, `src/scale_compare.py` (60/70/80 vs lid, historical), `src/export_parts.py` (STL per part)
- Renders and STLs (regenerable, gitignored `tmp/`): Blender script `tools/render.py` (regenerate with `cadgen run src/export_parts.py`
  then `Blender -b -P tools/render.py`). Run cadgen via `~/.local/bin/cadgen +0.8.4 run`.
