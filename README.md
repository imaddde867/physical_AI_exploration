# Physical AI Exploration

<p align="center">
  <img src="assets/face-idle-240.png" alt="Approved single digital face: understated, heavy-lidded eyes on a dark 240 × 240 display" width="240" height="240">
</p>

<p align="center">
  <strong>MacDesk Buddy · Build 01</strong><br>
  One character. One compact screen. A practical route from software into electronics, sensing and physical AI.
</p>

<p align="center">
  <a href="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/python-tests.yml"><img alt="Python and repository checks" src="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/python-tests.yml/badge.svg"></a>
  <a href="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/firmware-build.yml"><img alt="ESP32 firmware build" src="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/firmware-build.yml/badge.svg"></a>
  <a href="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/cad-check.yml"><img alt="OpenSCAD geometry checks" src="https://github.com/imaddde867/physical_AI_exploration/actions/workflows/cad-check.yml/badge.svg"></a>
</p>

**Status — software prototype.** The single-face PNG is the source used by ESP32 firmware, not a rendered robot or an expression gallery. Python tests, both PlatformIO configurations and CAD mesh validation pass in CI. **Real LCD brightness/colors, PCB wiring, printed fit and motion thresholds are not yet physically verified.** [Current build-readiness report](docs/release-readiness.md).

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

## First physical target

| Part | Purpose |
|---|---|
| ESP32-S3 **N16R8** | USB-connected microcontroller, reusable for later projects |
| **1.28-inch GC9A01 IPS** | Round, full-color 240 × 240 screen showing the **one approved face** |
| Optional **MPU-6050** | I²C motion input / shake reaction |
| Parametric OpenSCAD stand | Printable open-back housing and small fit coupon |
| MacBook Pro M4 | Python host now; optional MLX/local model integration later |

The **estimated complete Otronic basket is €40.03 delivered to Finland**, not a checkout quote. **Confirm pre-soldered headers, the LCD backlight pin, actual module dimensions and the exact Bambu printer model before buying or printing.** [Shopping list](docs/shopping-list.md) · [Reel-matched vs online alternatives](docs/hardware-options.md). Alternative Taby/AMOLED/StackChan boards do **not** run this firmware unchanged.

## How it works

~~~text
MacBook (Python JSONL host, USB serial)
                  |
               ESP32-S3
                /     \
    SPI: GC9A01 LCD   I²C: optional MPU-6050
     single character      motion events
~~~

The **same character** handles neutral, happy, sad, sleepy, surprised and thinking commands via restrained overlays, plus a brief blink. The approved 240 × 240 PNG is reproducibly compiled into a small RGB565 asset in flash; no full-size model runs on the device. See [protocol and architecture](docs/architecture.md).

## Pick your next step

- **No electronics yet:** [clone, simulate and build firmware on macOS](docs/clone-and-run.md).
- **Ready for the first assembly:** [wiring and physical validation checklist](docs/first-build.md), [firmware ports](firmware/README.md), [3D printing](docs/printing.md).
- **Choosing parts:** [priced BOM](docs/bom.md), [hardware options](docs/hardware-options.md), [true physical size diagram](assets/actual-scale-front.svg).
- **Research background:** [nine-Reel technical notes](docs/reel-technical-notes.md), [short Reel index](docs/reel-index.md).
- **After hardware works:** [Issue #1 — reproducible physical bring-up](https://github.com/imaddde867/physical_AI_exploration/issues/1) followed by [Issue #2 — optional Mac-local AI](https://github.com/imaddde867/physical_AI_exploration/issues/2).

## Project boundaries and license

This is an independently authored **learning and research prototype**, not a finished consumer robot, an exact clone of a Reel or a proven physical AI agent. The Mac-first V0 uses only Python/USB and deterministic microcontroller logic; servos, voice, camera, networking and local models are **later, optional milestones**. The repository is [MIT licensed](LICENSE); linked third-party projects retain their own licenses and artwork restrictions.
