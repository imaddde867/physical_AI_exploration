# First 20 minutes after cloning — MacBook M4

**You can complete every software step in this section with no ESP32, display, 3D printer, cloud credentials or GPU workstation.** This is a quick **smoke test**, not a claim that the hardware is already operational.

## 1. Clone and inspect

```sh
git clone https://github.com/imaddde867/physical_AI_exploration.git
cd physical_AI_exploration
git status --short
python3 --version
```

Use an existing Python **3.11 or newer**. (The code is ordinary Python; Python 3.12 was used in CI.)

## 2. Tests and software-only demonstration

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_repository.py
python3 -m macdesk.demo --simulate --face happy --watch
```

The last command shows a simulated JSON ACK and a deliberately **synthetic** shake event. **No microcontroller, sensors or local LLM were involved.**

## 3. Compile firmware on the Mac

Install the documented [PlatformIO CLI](https://docs.platformio.org/en/latest/core/installation/) with Homebrew (the verified formula is `platformio`; avoid modifying the system Python):

```sh
brew install platformio
pio --version
pio run -d firmware -e esp32s3_n16r8_usb
pio run -d firmware -e esp32s3_n16r8_uart
```

Both configurations must compile. The USB environment assumes **native ESP32-S3 USB/OTG**; the UART environment is for the board's separate USB-to-serial CH343P connector. **Neither build command flashes a board.**

If you don't have Homebrew, use the official PlatformIO VS Code extension instead.

## 4. Look at the design and screen sizes before buying

- [Stylized concept, not to scale](../assets/face-preview.svg)
- [Dimensioned face/body ratio](../assets/actual-scale-front.svg)
- [Hardware comparisons and Reel matches](hardware-options.md)
- [Exact starter basket](shopping-list.md)

The available Bambu printer model still needs direct identification. Do not slice with a guessed profile.

**OpenSCAD on current Apple Silicon macOS:** Homebrew's 2021.01 `openscad` cask is listed as disabled/Intel-only; use the manufacturer's installer or the maintained [`openscad@snapshot` cask](https://formulae.brew.sh/cask/openscad%40snapshot) if its requirements match your Mac. Check the installation details first.

## 5. When electronics arrive (not before)

1. Photograph the exact board labels, display backside, connectors and screen dimensions.
2. Confirm **pre-soldered header** and **BLK** behavior on the Otronic GC9A01. Verify the chosen board variant is the same one the firmware targets.
3. Follow [the SPI wiring table and USB instructions](../firmware/README.md). Disconnect USB before each rewiring step.
4. With data-capable USB cable attached to the **correct** connector, identify the board with `pio device list`. Check the selected port carefully, then (only after verifying it) flash:

```sh
pio run -d firmware -e esp32s3_n16r8_usb -t upload
```

5. Start with one expression, inspect screen illumination and backlight **visually**, then check all six face commands. Example (replace placeholder with the actual device):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m macdesk.demo --port /dev/cu.usbmodemXXXX --face happy --watch
```

**Important**: `"display":"init_sent_unverified"` reports only that the SPI initialization was sent. It does **not** prove the panel illuminated correctly.

## 6. What to record

[Build Issue #1](https://github.com/imaddde867/physical_AI_exploration/issues/1) is your physical validation log. Include board revision, actual GPIO labels, solder status, serial port, firmware versions, photograph of each face, actual backlight wiring, Bambu model, fit-coupon measurements, case slicing and any failures.

The next step is [Phase #2](https://github.com/imaddde867/physical_AI_exploration/issues/2): Mac-local inference, permissions, response-time benchmarks and later servo motion. It is **not** necessary for the first build.
