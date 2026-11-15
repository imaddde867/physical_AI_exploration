# Clip playback plan: Blender-baked, delta-encoded, played from flash

Date 2026-11-15. Status: **approved direction, nothing built yet.** Supersedes the "layered sprites + custom MicroPython build" idea floated on 2026-11-14.

## Goal

A companion that looks high quality: rich colour, dark blacks, smooth motion, alive. It must also be a platform for modules (music, usage, CI, AirPods, breaks, lyrics, touch) on a roughly EUR 30 board, with a hardware upgrade acceptable later if the board hits a stated ceiling.

## Decision

Bake every motion in Blender. Play back delta-encoded clips from flash, with the delta apply in `@micropython.viper`. Draw module UI (badges, text, bars) procedurally in a reserved strip. Modules send state, never pixels. Drop the sprite compositor, the custom MicroPython build and the custom USB receive path **for now**.

Why (from an independent Opus review, 2026-11-15; labels: **F** measured on the board, **M** measured offline from preview videos, **I** inference, **U** uncertain):

- The character is an 8-limb IK rig with planted contacts. 2D layers cannot reproduce its occlusion and shading, so blended layers ghost (I). Blender already gives the correct motion.
- Clip install speed is bound by flash write at 72 KB/s (F), slower than USB at 115 KB/s (F). A faster USB path would not help.
- `look-around` changes 8.9% of pixels per frame on average, 33% peak (M, from H.264 previews, **re-run on the real PNGs**). About 12 KB per frame, about 1.2 MB per 8 s clip at 12 fps (I). Eight clips fit in 15.5 MB at 12 fps, borderline at 24 fps.
- Per-frame budget at 24 fps (41.7 ms): `show()` 22 ms (F) + peak read about 6 ms (I) + viper apply 3 to 6 ms (U).

## Measured baselines this plan relies on

| Item | Value |
|---|---|
| `show()` full screen | 22.0 ms mean, p95 22.2 (F, after clk_peri fix) |
| Flash read, 134,400 B | 19.0 ms (F); about 7 MB/s |
| Flash write | 72 KB/s (F) |
| USB receive | about 115 KB/s (F) |
| Heap with LCD driver | about 74 to 78 KB (F); about 29 KB with touch loaded (spec estimate) |
| Filesystem | 15.5 MB free (F) |

## Not reachable on this board

60 fps. Double buffering. Tear-free output (driver ignores TE; wiring unverified). Real-time pose blending. Mac-streamed animation (a full frame takes over 1 s). True black (IPS LCD; needs OLED). Interrupting a clip at an arbitrary frame: switch states at the shared idle boundary pose (`animation/README.md`).

## Stages

Each stage has a go/no-go number. Do them in order; stop and report if a stage fails.

### Stage 0: Mac-only exporter

Blender PNG sequence -> RGB565 with ordered dither -> keyframe plus per-frame delta runs `(offset, length, pixels)`. Runs on the Mac only; does not touch the board.

- Render the real PNGs (not the H.264 previews) for `watch` and `look-around` first.
- Bake dithering here; it costs nothing on the device. Keep backgrounds at exact `0x0000`. Avoid large dark gradients (RGB565 bands).
- Report per clip: size, mean and peak delta bytes per frame, at 12 and 24 fps.
- **Go (amended 2026-11-15):** all 8 clips fit in flash with room, and the exporter has a host-side decode test that reproduces the dithered source frames exactly. The original "each clip at most 2 MB at 24 fps" was not met and 24 fps is unmeasured.
- **No-go action:** lower the frame rate to 12 to 15 fps, shrink the rendered area, or trim states.
- **Result (done, `animation/clip_export.py`, 7 tests pass):** 12 fps, hold threshold 6, luma threshold 14. All 8 states total 11.2 MB vs 15.5 MB free. Per clip MB: watch 0.44, scratch 0.59, lean_in 0.80, lean_back 0.92, look_right 1.93, look_left 2.02, shift 2.17, look_around 2.36. Peak delta 13 to 65 KB per frame (look_* 56 to 65 KB), not the ~12 KB assumed above.
- **Findings:** about 29% of pixels flicker by 1 to 2/255 per frame (render noise; the hold threshold removes it). A shading gradient drifting 7 to 20/255 across the body while it moves is the real cost (the luma threshold). The character spans rows 21 to 279, not 238 rows. Pinning key light and AO to world space in the .blend might cut sizes further (not tried).

### Stage 1: Player prototype on the board

`look-around` from flash, viper apply into the one framebuffer, `show()`. Time read, apply and show separately over 1000 frames. Do not replace `main.py`; use `mpremote run`.

- **Go:** 12 fps (target after Stage 0): p95 total under ~70 ms, heap at least 20 KB free. Peak deltas of 56 to 65 KB mean about 9 ms read + 22 ms show before apply, so 24 fps (p95 under 38 ms) is doubtful; try it only to record the number.
- **If apply time is the miss:** go to Stage 4.
- Needs a look at the panel: no tearing artefacts, no stale pixels after loop wrap.

### Stage 2: Eight-state machine and badge strip

All eight states, switching at the shared idle boundary pose. Badge strip drawn procedurally in the rows the character does not use (about 20 px free: the character spans rows 21 to 279).

- **Go:** no visible glitch at state switches; a 30-minute run with no heap drift (record `gc.mem_free()` at start and end); flash holds all clips.

### Stage 3: Touch and daemon state end to end

Wire touch, the Buddy OS reconciler and a first module (`idle` / `break_reminder`) to the device over the existing line protocol. Add `play {state}` and `badge` messages, gated on `caps`.

- **Go:** tap to visible reaction under 150 ms; Mac sleep, cable pull and host death still recover (reuse the 2026-11-14 recovery tests).

### Stage 4: Native `.mpy` module (only if Stage 1 misses on apply time)

A native module compiled for armv6m that loads on stock firmware. No custom firmware build unless this also fails.

## Hardware upgrade triggers

Move to better hardware only if one of these happens:

1. 24 fps p95 is still above 41.7 ms after Stage 4.
2. Heap is under 15 KB with touch, player and protocol loaded.
3. Tearing is visible and TE is not usable.
4. The blacks are unacceptable at your real desk lighting.

Candidate (cost **U**): an ESP32-S3 board with an AMOLED and PSRAM, roughly EUR 25 to 40 plus shipping; MicroPython AMOLED drivers are third-party, and a static badge strip risks burn-in. An RP2350 fixes RAM (520 KB, allows double buffering) but not blacks; pick it only if RAM is the trigger.

## Task list (use these as issue titles)

1. Exporter: PNG sequence to dithered RGB565 delta clips, with host decode test (Stage 0)
2. Render `watch` and `look-around` PNG sequences and record clip sizes (Stage 0)
3. Player prototype: timing of read, apply and show over 1000 frames (Stage 1)
4. Eight-state machine, boundary switching, 30-minute heap run (Stage 2)
5. Badge strip in reserved rows (Stage 2)
6. Protocol: `play` and `badge` messages gated on `caps` (Stage 3)
7. Touch to daemon to reaction path, under 150 ms (Stage 3)
8. First module end to end: `idle` and `break_reminder` (Stage 3)
9. Re-run recovery tests with the player active (Stage 3)
10. Decide: native `.mpy` or hardware upgrade, from Stage 1 numbers (Stage 4)

## Open questions

- Is TE wired on this board? Needs a schematic check before any tear-free claim.
- ST7789 gamma registers E0/E1 can deepen near-black slightly; worth one experiment, a small gain at best.
- Brightness control: set from the Mac; no light sensor is documented for this board.
