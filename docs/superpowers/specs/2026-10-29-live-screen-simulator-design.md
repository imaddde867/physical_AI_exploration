# Live screen simulator — design

**Date:** 2026-10-29 · **Status:** awaiting approval
**Approached as:** small change (short design)

## Intent & why

See, live on the Mac, what would show up on the Waveshare ESP32-S3-Touch-AMOLED-1.64 V2 while experimenting with screen ideas — faces, behaviors, and small desk "mini-apps" — without the hardware. Exploration-first: fastest path from idea to visible pixels.

## Goals

- A `sim/` tool. A mini-app is **one Python file**; run it, a window shows a live animated screen.
- The window is the panel: **456×280 (landscape), 1:1 pixels, RGB565 color quantization** exactly matching what firmware would send (`tools.face_asset.rgb565`, same rounding as `assets/amoled-preview.html`).
- Live loop ≈ 30 fps cap; window close or Ctrl+C stops. Elapsed `t_ms` passed to the app each frame so timing experiments (blink, idle) behave.
- Zero new dependencies: tkinter 8.6 is available on system Python; reuse the repo's stdlib RGB565 helper.
- Fits existing repo patterns: `tools.face_asset.rgb565` reused, unittest suite extended, no firmware-v2 or GC9A01 changes (purely additive).

## Non-goals / anti-goals

- **Not** hardware truth: does not predict real panel color, brightness, tearing, fps, or ESP timing. Hardware checks in `firmware-v2/README.md` remain the gate.
- **Not** interactive input (keyboard/touch/tap) in v1.
- **Not** a porting automation; moving a mini-app into portable C stays manual.
- **Not** a replacement for the byte-exact host C renderer tests.
- No network, no model calls, no text/font primitive until one is asked for.

## Constraints

- Display from Python side: nobody can guarantee what an AMOLED panel shows from pixels alone — quantization formula parity with `amoled-preview.html` is the contract.
- Stream-decoded... no asset pipeline changes: mini-apps draw procedurally or blit the existing approved PNG transcodes (12 baked frames via `tools.check_v2_renderer`-style RLE or `tools.amoled_face` functions where useful).

## Approaches considered

1. **Python live simulator (chosen).** Mini-apps in Python, tkinter window, quantized colors, live loop. Fast small steps; porting is manual later.
2. **Shared-core C simulator (rejected for now).** Bit-exact same code on ESP and Mac, but recompiles per tweak and needs extra viewer plumbing; the repo's byte-exact C tests already cover the render core path, so this buys little during exploration.

## Deferred calls (mine unless flagged)

- Mini-app contract: module-level `update(screen, t_ms)`; `screen` offers `set_pixel`, `fill_rect`, `blit_image`, `clear`.
- Runner: `python3 -m sim.runner <mini_app.py>`; `--fps` and `--scale` before build end.

## What's left to the builder

- Window label showing fps and t_ms (for sanity, not truth).
- One demo mini-app committed (with a small unittest) and listed in the README.
