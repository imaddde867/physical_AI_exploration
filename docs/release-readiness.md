# Release-readiness / first-build boundary

**Status: clone-ready software and CAD prototype; physical hardware not validated.** This is the current summary for MacDesk Buddy. The initial OLED-era technical review is preserved [in the historical archive](archive/2026-10-26-initial-audit.md); **do not use that document for current purchasing or wiring**.

## Implemented and checked

| Evidence | What it supports | What it does not support |
|---|---|---|
| Python / repository CI | JSONL protocol tests, simulator, artwork checksum/encoding, hardware catalog and BOM arithmetic, local links/SVG | Physical display or serial reliability |
| PlatformIO CI (native USB and UART) | ESP32-S3 N16R8 firmware compiles with pinned dependencies and generated face header | Actual board wiring, BLK, pixel colors or I²C health |
| OpenSCAD + mesh CI | Prototype shell and circular aperture coupon render to watertight, single-component meshes | Slicer supports, printer profile or PCB fit |
| One checked-in face image | Deterministic 240×240 source with SHA256-checked generated RGB565 payload | Backlight/black level, visual quality at 31.4 mm |

CI badge status is live in the [README](../README.md). **No physical unit was assembled, flashed or tested. No hardware has been bought.** The mock simulator event is synthetic, not a recorded sensor measurement.

## One supported starter build

- **Controller:** ESP32-S3 N16R8, with the correct **native USB/OTG vs CH343P UART** environment.
- **Screen:** Otronic GC9A01 1.28-inch 240×240 SPI IPS, showing **one approved face** only.
- **Optional sensor:** MPU-6050, independent I²C GPIO8/9; reaction threshold remains experimental.
- **Estimated single-store basket:** **€40.03 to Finland** including listed shipping, **not** an actual checkout.
- **Mac host:** base M4, 10-core CPU, 10-core GPU and **16 GB shared memory**. No local model runs in V0.

The independent Taby/AMOLED, Rocky and StackChan alternatives in [hardware-options.md](hardware-options.md) **require different software, parts and/or CAD**. Do not buy them as substitutes for the supported GC9A01 wiring guide.

## Unresolved physical gates

1. Supplier confirmation of **pre-soldered LCD headers** and exact **BLK backlight** wiring.
2. Physical ESP32 board pinout/USB labeling and 3.3 V logic verification.
3. Visual inspection of the real 240×240 screen (rotation, color order, brightness, blink and mood changes).
4. Sensor false positives, USB disconnect/reconnect tests and observed command latency.
5. Exact Bambu printer model, fit-coupon measurement, slicer supports and enclosure retention.

These are [Build Issue #1](https://github.com/imaddde867/physical_AI_exploration/issues/1), not software CI pass conditions. After hands-on evidence exists, investigate [Issue #2 — Mac-local AI](https://github.com/imaddde867/physical_AI_exploration/issues/2).

## Starting point

Follow the [Mac clone-and-run guide](clone-and-run.md). It deliberately performs no package downloads beyond ordinary Python/PlatformIO setup, no cloud AI and no external GPU connections. Record the actual macOS/Python versions because the owner's specification document does **not** establish them.
