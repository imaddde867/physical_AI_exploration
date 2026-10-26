# MacDesk Buddy · Physical AI Exploration

**First build:** a compact, original, Mac-first desk companion with a **1.28-inch circular GC9A01 full-color IPS face**, an ESP32-S3, optional motion sensing and a printable case. Inspired by the saved robotics Reels without copying creators' assets.

![Illustrative original round-color face concepts; not physical prototype photos](assets/face-preview.svg)

> **Status:** Mac-side tests and both USB firmware builds are automated. The round CAD was rendered and mesh-checked, but **real LCD illumination, physical fit, Bambu slicing and assembly are not validated**. See [audit and evidence](docs/audit-2026-10-26.md).

## Why this build?

A USB-powered **ESP32-S3** renders full-color expressions over **SPI**, while the **MacBook M4** hosts commands and future optional local AI. The optional **MPU-6050** uses a **separate I²C bus** for motion-triggered reactions. The starter avoids cloud accounts, microphones, cameras and motors. Start with the electronics you can understand and validate, then expand.

```text
 MacBook Pro (Python host, optional local LLM)
           | USB serial / newline JSON
           v
 ESP32-S3 MCU --> SPI GC9A01 round IPS (color animated face)
           |
       \--> I2C MPU-6050 (optional motion sensor)
       later expansion: servo, voice, Wi-Fi
```

## Start here

1. Read [docs/first-build.md](docs/first-build.md) and [docs/bom.md](docs/bom.md).
2. Without hardware: `python3 -m unittest discover -s tests -v` and `python3 -m macdesk.demo --simulate --face happy`.
3. With hardware: follow [firmware/README.md](firmware/README.md) and flash the ESP32-S3.
4. Connect a **data-capable USB cable to the board's native ESP32-S3 USB/OTG port (not its CH343P UART port for the default firmware)**, find the port, then run `python3 -m pip install -r requirements.txt` and `python3 -m macdesk.demo --port /dev/cu.usbmodemXXXX --face happy`.
5. Print the small **screen fit coupon** first, then render `cad/desk-buddy.scad` with **OpenSCAD** after measuring actual components. See [docs/printing.md](docs/printing.md).

## Project map

| Area | What you'll find |
|---|---|
| [docs/first-build.md](docs/first-build.md) | Steps, safety, acceptance tests |
| [docs/bom.md](docs/bom.md) | One small starter basket and expansion options |
| [docs/reel-index.md](docs/reel-index.md) | All nine inspirations, upstream links, licensing cautions |
| [docs/printing.md](docs/printing.md) | Printable enclosure and fit test |
| [docs/architecture.md](docs/architecture.md) | JSON protocol, responsibility boundaries |
| [firmware/](firmware/) | Original PlatformIO Arduino ESP32-S3 implementation |
| [macdesk/](macdesk/) | macOS-friendly Python controller + simulator |
| [cad/](cad/) | Source-controlled, adjustable OpenSCAD enclosure |
| [assets/architecture.svg](assets/architecture.svg) | Original vector architecture visual |

## Roadmap

- **V0 (now):** simulator, original JSONL protocol, **GC9A01 round color faces**, periodic blinking, optional MPU-6050 shake reaction, printable circular enclosure and fit coupon.
- **V1 (hardware):** verify wiring + fit; measure time-to-expression and reconnect behavior.
- **V2:** optional Mac-local LLM/voice and a constrained face-action interface; additional physical sensors only as needed.
- **V3:** measure model-to-action reliability, latency and memory; introduce bounded movement with a separately rated motor power supply.
- **V4:** camera or richer perception experiments and independent hardware sensing.
- **V5:** optional standalone Wi-Fi mode; compare Mac-hosted vs edge-only behavior.

**No language model runs in V0**. Mac-local model/tool integration is V2/V3 work, and ESP32 keeps deterministic sensor behavior. The M4 laptop should remain responsive; GPU machines are **optional for training**, not required at runtime. No cloud dependency is required for V0/V1. No third-party images, firmware or CAD assets have been copied.

## Attributions and licensing

See [docs/reel-index.md](docs/reel-index.md). Original repository material is MIT licensed under [LICENSE](LICENSE). Linked projects retain their authors' licenses and restrictions. This is an independently designed learning project.

## Latest review

- [Technical audit (26 October 2026)](docs/audit-2026-10-26.md)
- [Verified vendor part list](docs/shopping-list.md)
- [Original pin-level wiring diagram](assets/wiring.svg)
- [Round color display choice and sourcing](docs/display-choice.md)
- [Original concept face gallery](assets/face-preview.svg)
- [Issue #1: actual hardware bring-up](https://github.com/imaddde867/physical_AI_exploration/issues/1)
