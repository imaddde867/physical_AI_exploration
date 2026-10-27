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

**Status — software prototype; hardware untested.** The existing firmware controls a GC9A01 face over USB. Timers, notifications, music, coding-agent status and screen awareness are planned, not implemented. The 2026-10-27 audit passed 21 Python tests and the repository checker; firmware/CAD builds and live CI were not rechecked. [Readiness](docs/release-readiness.md).

## Current direction

**Current direction: a subtle rounded-rectangle face**, with one discreet USB cable for power and data. The leading documented board candidate is Waveshare ESP32-S3-Touch-AMOLED-1.64, SKU 31197, listed as V2; purchase remains gated on matching the delivered PCB revision to the drawing and schematic and verifying USB data. The existing GC9A01 firmware stays implemented; the new board needs its own display/UI path and Mac USB bridge. See the [engineering study](reports/Rectangular%20buddy%20engineering%20study.md) and [build plan](docs/rectangular-build-plan.md). The 33.12 × 48 × 13 mm concept is provisional packaging scale, not proof of board fit.

Start with one board, a data cable and a temporary desk stand. Confirm exact board variant, Finland checkout total and enclosure plan first. No camera, microphone, IMU, motors or battery is needed for the first companion. The existing SCAD is a desktop stand prototype; the new rear-lid CAD studies are provisional, not validated mounts.

[**Rectangular engineering study**](reports/Rectangular%20buddy%20engineering%20study.md) · [Rectangular build plan](docs/rectangular-build-plan.md) · [Display choice](docs/display-choice.md) · [First-build milestones](docs/first-build.md)

![Portrait, landscape and square form studies](assets/rectangular-placement-study.png)

*Provisional scale studies; the MacBook lid geometry and physical fit remain unverified. [CAD sources, coupon and rebuild guide](cad/peeking-concepts/README.md).*

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
