# First session on the MacBook Pro M4

**Target:** MacBook Pro 14-inch (2024), **base M4 10-core CPU / 10-core GPU / 16 GB unified RAM**. See [development-host specifications](development-host.md). This guide starts with **no new hardware, no models and no cloud accounts**.

## 1. Clone

~~~sh
git clone https://github.com/imaddde867/physical_AI_exploration.git
cd physical_AI_exploration
git status --short
uname -m                           # Expected: arm64 on your Mac
python3 --version
~~~

Use **Python 3.11+**. For a reproducible fresh installation, if you use Homebrew, the following commands install **Python 3.12** and PlatformIO Core (the verified macOS formulae):

~~~sh
brew install python@3.12 platformio
python3.12 --version
pio --version
~~~

If Homebrew is not available, use a compatible Python 3.11+ installation and the [PlatformIO VS Code IDE extension](https://platformio.org/install/ide?install=vscode). Do not run a downloaded installer as root. The repository does not require Docker or Xcode-specific Python packages.

## 2. Create an isolated environment and test

~~~sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/check_repository.py
.venv/bin/python -m macdesk.demo --simulate --face neutral --watch
~~~

**Expected:** unit-test pass, a repository-check pass, and a simulated serial ACK / **explicitly synthetic** motion event. No physical ESP32 is accessed. If Python 3.12 is not installed but another supported Python is, substitute its actual executable when creating the venv.

## 3. Compile both ESP32-S3 firmwares

~~~sh
pio run -d firmware -e esp32s3_n16r8_usb
pio run -d firmware -e esp32s3_n16r8_uart
git status --short
~~~

The first build downloads the **pinned PlatformIO dependencies** and may take longer. Both build environments use the same approved artwork. A pre-build hook converts [the one 240×240 screen PNG](../assets/face-idle-240.png) into a gitignored RGB565 asset header with **standard-library Python**; do not manually modify the generated file.

**The build does not flash anything.** The USB profile is for **native ESP32-S3 USB/OTG**; the UART profile uses the board's **separate CH343P USB-to-UART** port. The actual board may need first-flash BOOT/RESET steps. Full [firmware instructions and wiring](../firmware/README.md).

## 4. Review your choices before purchasing

- [One approved screen-only face, exactly 240×240 source pixels](../assets/face-idle-240.png).
- [Physical screen aperture versus body width](../assets/actual-scale-front.svg): Ø31.4 mm visible opening in a 72 mm-wide body.
- [Part compatibility and price comparison](hardware-options.md) and [single-store basket](shopping-list.md).
- [Development milestones](first-build.md).

**The existing Bambu Academy URL does not identify the printer model.** Verify the physical printer label before slicing. On Apple Silicon, the current [Homebrew OpenSCAD snapshot cask](https://formulae.brew.sh/cask/openscad%40snapshot) can be installed optionally:

~~~sh
brew install --cask openscad@snapshot
~~~

Check its OS requirements first. The legacy `openscad` cask is disabled and Intel-only; do not add Rosetta just for an outdated CAD build.

## 5. When electronics arrive

1. Check module revisions and **pre-soldered headers**, **LCD BLK pin** behavior, 3.3 V-safe sensor pull-ups and the ESP32 board's native USB/OTG labeling.
2. Disconnect USB when wiring. Wire the GC9A01 on **SPI**, and the optional MPU-6050 on **separate I²C** pins.
3. Find the correct serial device with `pio device list`, then flash the matching board profile. For native USB/OTG only:

~~~sh
pio run -d firmware -e esp32s3_n16r8_usb -t upload
~~~

4. Inspect the LCD **with your eyes**: `display=init_sent_unverified` is a transmit-only event, not proof of illumination. Then test the one face and all six *moods*:

~~~sh
.venv/bin/python -m macdesk.demo --port /dev/cu.usbmodemXXXX --face neutral --watch
~~~

Replace the port placeholder with the actual macOS device. Record color order, clarity, timing, motion false positives and USB recovery in [Issue #1](https://github.com/imaddde867/physical_AI_exploration/issues/1).

## Scope

V0/V1 uses **no local LLM or extra GPU memory**. Later Mac inference is optional and should stay within the machine's **shared 16 GB unified-memory budget**, using measurements rather than guessed model-fit assumptions. See [Mac profile](development-host.md) and [readiness gates](release-readiness.md).
