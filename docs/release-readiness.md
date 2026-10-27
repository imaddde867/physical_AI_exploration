# Build readiness

**As of the 2026-10-27 audit: software prototype; no physical hardware validation.** The [rectangular engineering study](../reports/Rectangular%20buddy%20engineering%20study.md) and [build plan](rectangular-build-plan.md) are the current direction records. The [initial OLED audit](archive/2026-10-26-initial-audit.md) is historical.

## Evidence and boundaries

| Evidence | Established | Still unverified |
|---|---|---|
| Local Python suite and repository checker | 21 tests passed; protocol, simulator, asset encoding, manifest arithmetic and links checked | Physical USB reliability, display output and sensor behavior |
| PlatformIO workflows | Native USB and UART build jobs are configured with pinned dependencies | Not rerun in this audit; live CI status not checked |
| CAD workflow | OpenSCAD render/mesh checks are configured | Not rerun in this audit; physical fit, slicer settings, installed nozzle/profile and mounting |
| Face asset | One checked-in 240×240 image used by GC9A01 firmware | Appearance, brightness and colors on a real panel |

The simulator's shake event is synthetic. Build success cannot prove that a write-only SPI panel illuminates. No unit has been assembled, flashed or physically tested in this project.

## Hardware tracks

**Leading documented purchase candidate:** Waveshare ESP32-S3-Touch-AMOLED-1.64 SKU 31197, listed V2. Purchase remains gated on mapping the delivered revision to the drawing/schematic and verifying USB data; its 33.12 × 48 × 13 mm concept scale does not establish fit. It needs separate firmware/UI and Mac USB work. No AMOLED implementation is claimed here. Taby 1.64 V1 support is separate.

**Implemented learning prototype:** separate ESP32-S3 N16R8 + GC9A01 1.28-inch SPI display, with optional MPU-6050 on I²C. The dated €40.03 basket is an estimate, not a current checkout quote. LCD headers/BLK, board labels, 3.3 V logic, screen output, USB recovery and printed fit need physical checks. Alternative boards cannot use this firmware unchanged.

## Feature readiness

Implemented: six facial mood commands, local blink, synthetic host simulation and optional experimental shake response. Not implemented: text, timers, Mac app events, notifications, coding-agent status/tokens, music, lyrics, screen capture or model inference.

The Mac target is a base M4 with **16 GB shared unified memory**, not a separate GPU memory pool. No model or cloud service is required for the current demo or a deterministic timer/event bridge.

Follow the [first-build milestones](first-build.md). Existing [physical bring-up issue #1](https://github.com/imaddde867/physical_AI_exploration/issues/1) and [optional Mac AI issue #2](https://github.com/imaddde867/physical_AI_exploration/issues/2) are background tracking; this cleanup does not update their scope or status.
