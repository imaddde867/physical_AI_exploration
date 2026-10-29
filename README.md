# Physical AI Exploration

<p align="center">
  <img src="assets/face-idle-240.png" alt="Approved single digital face: understated, heavy-lidded eyes on a dark 240 × 240 display" width="240" height="240">
</p>

<p align="center">
  <strong>MacDesk Buddy · Face-first prototype</strong><br>
  One expressive character beside a MacBook. Occasional short text. Mac-driven reactions.
</p>

<p align="center">
  <a href="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/python-tests.yml"><img alt="Python and repository checks" src="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/python-tests.yml/badge.svg"></a>
  <a href="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/firmware-build.yml"><img alt="ESP32 firmware build" src="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/firmware-build.yml/badge.svg"></a>
  <a href="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/cad-check.yml"><img alt="OpenSCAD geometry checks" src="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/cad-check.yml/badge.svg"></a>
</p>

**Status: purchase decision settled; physical build and AMOLED software unfinished.** Buy one Waveshare 1.64-inch AMOLED board, SKU 31197 V2, plus a USB data cable if needed. The existing firmware controls the older GC9A01 face. Mac integrations and the V2 renderer remain planned. Start with the [buying decision and build sequence](docs/build-decision.md); see [readiness](docs/release-readiness.md) for verification limits.

## Current direction

The selected design is a matte rounded rectangle in landscape orientation on the upper right side of the lid, about 25 mm below the top, angled inward by 10 degrees. A fixed arm and head detach for transport. The CAD establishes appearance and spacing; the enclosure, cable exit and dock still need physical measurements.

The selected hardware is **Waveshare ESP32-S3-Touch-AMOLED-1.64 V2, SKU 31197**. Use one USB cable for power and data. Its [official V2 examples](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.64-v2/tree/21b952243d306692774f3b5bfeb3eb5cff10f851) are the bring-up starting point. The GC9A01 firmware and Taby V1 images must not be flashed as this board's display firmware.

[Buying decision and feature scope](docs/build-decision.md) · [Shopping list](docs/shopping-list.md) · [Printing](docs/printing.md) · [Detailed build plan](docs/rectangular-build-plan.md)

![Selected landscape placement](assets/selected-placement-iso.png)

*Placement study with placeholder eyes. Physical fit and retention remain unverified. [CAD source and checks](cad/peeking-concepts/README.md).*

## Start on your MacBook

Target: **14-inch MacBook Pro (2024), base M4 (Mac16,1), 10-core CPU, 10-core GPU, 16 GB unified RAM**. The GPU has **no separate 16 GB VRAM**. A local LLM, workstation or cloud account is **not required** for this first build. See [development-host notes](docs/development-host.md).

~~~sh
git clone https://github.com/imaddde867/physical_AI_exploration.git
cd physical_AI_exploration
python3 --version                     # Requires Python >= 3.11; see Mac setup guide
python3 -m unittest discover -s tests -v
python3 tools/check_repository.py
python3 -m macdesk.demo --simulate --face neutral --watch
~~~

This runs **software-only tests and a synthetic simulation**; it does not talk to electronics or run AI. If your default Python is too old, follow the [verified macOS setup guide](docs/clone-and-run.md) to use Python 3.12 in a virtual environment.

## Existing GC9A01 learning prototype

| Part | Implemented target |
|---|---|
| ESP32-S3 **N16R8** | USB-connected microcontroller |
| **1.28-inch GC9A01 IPS** | Round 240×240 display using the face asset above |
| Optional **MPU-6050** | Experimental shake reaction; defer for the face-first build |
| OpenSCAD stand | Open-back desktop shell and fit coupon; physical fit unverified |

The dated [GC9A01 basket](docs/shopping-list.md) is an alternative learning build, not the AMOLED purchase list. Its **€40.03** total is a reference estimate, not a checkout quote. Headers, backlight wiring and physical fit remain unresolved. Do not buy both hardware tracks by default or flash GC9A01 firmware onto an AMOLED board.

~~~text
Implemented: Mac Python host → USB JSONL → ESP32-S3 → GC9A01 face
Planned:     Mac events → companion logic → USB → face / brief text
~~~

Six commands select neutral, happy, sad, sleepy, surprised and thinking cues on the same character. Blink runs locally. The PNG is compiled into a flash-resident RGB565 asset; no model runs on the device. [Protocol and proposed integrations](docs/architecture.md).

## Guides and research

- [Rear-lid peeking concepts](cad/peeking-concepts/README.md): left/right/top scale studies and retractable versus detachable travel concepts; not print-ready mounts.
- [Run the existing prototype on macOS](docs/clone-and-run.md), [GC9A01 wiring/firmware](firmware/README.md), [printing](docs/printing.md).
- [Hardware alternatives](docs/hardware-options.md), [reference BOM](docs/bom.md), [actual GC9A01 front dimensions](assets/actual-scale-front.svg).
- [Reel source index](docs/reel-index.md) and [technical notes](docs/reel-technical-notes.md) preserve earlier research; use the rectangular engineering study and build plan for current recommendations.

## Project boundaries and license

This is an independently authored **learning and research prototype**, not a finished consumer robot, an exact clone of a Reel or a proven physical AI agent. The Mac-first V0 uses only Python/USB and deterministic microcontroller logic; servos, voice, camera, networking and local models are **later, optional milestones**. The repository is [MIT licensed](LICENSE); linked third-party projects retain their own licenses and artwork restrictions.
