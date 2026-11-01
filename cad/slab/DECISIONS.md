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
- **Look:** black edge-to-edge glass, hairline aluminium frame, rear arm + clip hidden behind the lid.

## Open
- No panel chosen. Waveshare's largest ESP32-S3 AMOLED board is 2.41" (600x450, 4:3), too small for 60 mm
  wide without visible border. Likely a bare ~3" panel plus a small controller board.
- Rear mount (arm/clip) is a placeholder, not designed or tested for the lid.
- MacBook model is a simplified slab (lid height 214 mm, bezels assumed). Only width/depth are published.
- Face art (456x280) is the old one; new faces still to design.

## Files
- `src/placement.py`, `src/scale_compare.py` (60/70/80 vs lid), `src/export_parts.py` (STL per part)
- Renders: Blender script `tools/render.py` (regenerate with `cadgen run src/export_parts.py`
  then `Blender -b -P tools/render.py`). Run cadgen via `~/.local/bin/cadgen +0.8.4 run`.
