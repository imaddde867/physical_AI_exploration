# MacDesk Buddy · Physical AI Exploration

**First build:** a small, expressive, 3D-printable companion for a MacBook Pro. Original code and parametric enclosure; inspired by the nine saved robotics/IoT Reels, not a clone of their software.

> **Status:** working scaffold and automated protocol tests; **physical build not yet validated**. Buy the hardware only after confirming exact board/display revisions and printer model.

## Why this build?

A USB-powered **ESP32-S3** runs animated eyes and physical I/O; the **MacBook M4** hosts commands, automation and optional local model inference. The starter deliberately omits cloud accounts, microphones, cameras, soldering and servo power. Start with the electronics you can understand and validate, then expand.

```text
 MacBook Pro (Python host, optional local LLM)
           | USB serial / newline JSON
           v
 ESP32-S3 MCU --> I2C SSD1306 OLED (animated face)
           |
       optional expansion: sensor, servo, battery, Wi-Fi
```

## Start here

1. Read [docs/first-build.md](docs/first-build.md) and [docs/bom.md](docs/bom.md).
2. Without hardware: `python3 -m unittest discover -s tests -v` and `python3 -m macdesk.demo --simulate --face happy`.
3. With hardware: follow [firmware/README.md](firmware/README.md) and flash the ESP32-S3.
4. Connect a **data-capable USB cable**, find the port, then run `python3 -m pip install -r requirements.txt` and `python3 -m macdesk.demo --port /dev/cu.usbmodemXXXX --face happy`.
5. Print `cad/desk-buddy.scad` with **OpenSCAD** after measuring your actual components. See [docs/printing.md](docs/printing.md).

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

- **V0 (now):** simulator, original serial protocol, animated OLED face, printable shell.
- **V1 (hardware):** verify wiring + fit; measure time-to-expression and reconnect behavior.
- **V2:** add IMU or ambient sensor for reactive, autonomous expressions.
- **V3:** local Mac voice / local model tools behind an explicit action allowlist; record latency and memory.
- **V4:** pan/tilt movement with separate 5 V power and safe angle limits.
- **V5:** optional standalone Wi-Fi mode; compare Mac-hosted vs edge-only behavior.

The M4 laptop should remain responsive; GPU machines are **optional for training**, not required at runtime. No cloud dependency is required for V0/V1. No third-party images, firmware or CAD assets have been copied.

## Attributions and licensing

See [docs/reel-index.md](docs/reel-index.md). Original repository material is MIT licensed under [LICENSE](LICENSE). Linked projects retain their authors' licenses and restrictions. This is an independently designed learning project.
