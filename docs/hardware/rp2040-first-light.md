# First light: ordered RP2040-Touch-LCD-1.69

Status 2026-11-05: preparation only. The Waveshare board is ordered, not connected. Neither the unmodified manufacturer demo nor our own firmware has been tested on physical hardware. **First run the vendor demo unchanged.**

## Confirm the exact board

This is Waveshare's **integrated RP2040-Touch-LCD-1.69**, SKU 28161: RP2040 (264 KiB SRAM), 16 MB flash, ST7789V2 240 x 280 SPI LCD, CST816T I2C touch, USB-C data/power. The visible LCD measures 27.972 x 32.634 mm. These specifications are for the [integrated board wiki](https://www.waveshare.com/wiki/RP2040-Touch-LCD-1.69), not the standalone 1.69-inch LCD module.

Verified against the [integrated board schematic](https://files.waveshare.com/wiki/RP2040-Touch-LCD-1.69/RP2040-Touch-LCD-1.69-Sch.pdf) and the same-board [hardware-tested ST7789 port](https://github.com/fcjr/gudlet/tree/main/crates/gud-panel):

| Signal | RP2040 GPIO |
| --- | ---: |
| LCD DC, CS | 8, 9 |
| LCD SPI1 SCK, MOSI, MISO | 10, 11, 12 |
| **LCD RESET** | **13** |
| LCD backlight | 25 |
| Touch I2C1 SDA, SCL | 6, 7 |
| Touch INT, RESET | 21, 22 |
| Power button | 14 |

**Important:** GPIO12 is LCD MISO; **GPIO13 is LCD RESET**. Do not copy the Pico wiring table for the standalone 1.69-inch module. The integrated board needs no extra display connections.

## Gate A — original Waveshare demo on Apple Silicon macOS

Download the demo by following the **Demos → Demo** link on the **integrated board's** [official wiki](https://www.waveshare.com/wiki/RP2040-Touch-LCD-1.69#Resources), not an independent LCD-module tutorial.

~~~sh
mkdir -p ~/Downloads/waveshare-rp2040-169
curl -fL 'https://files.waveshare.com/wiki/RP2040-Touch-LCD-1.69/RP2040-Touch-LCD-1.69-Code.zip' \
  -o ~/Downloads/waveshare-rp2040-169.zip
unzip -q ~/Downloads/waveshare-rp2040-169.zip -d ~/Downloads/waveshare-rp2040-169
find ~/Downloads/waveshare-rp2040-169 -type f \
  \( -name '*.uf2' -o -name '*.py' -o -name 'CMakeLists.txt' \) | sort
~~~

The manufacturer archive's **internal paths and included UF2 names were not inspectable in this preparation environment**. Verify the examples match this *integrated* board and keep the original filenames. Do not select a file only because it says "1.69-inch".

1. Install [Thonny (macOS)](https://thonny.org/) for the official MicroPython demo. Do not start by compiling custom code.
2. Connect the existing known data-capable USB-C cable. Hold BOOT, tap RESET while holding BOOT, release BOOT. The ROM boot drive should mount as **/Volumes/RPI-RP2**. Alternatively hold BOOT while plugging in the board.
3. Follow the MicroPython section of the board's wiki: flash the correct Waveshare **RP2040** MicroPython UF2 (the wiki links its RP2040 firmware), not an RP2350 image. Drop the UF2 into **/Volumes/RPI-RP2/**. The drive disappearing after flashing is expected.
4. In Thonny choose **MicroPython (Raspberry Pi Pico)** and the board's USB serial device. Load any vendor demo dependencies, then **run the original integrated-board LCD example without modifications**.
5. Record the exact demo filename and SHA-256, a screen photo, expected/actual color and orientation, and any errors. **Stop if the manufacturer's test fails**; do not flash our experimental firmware until the baseline works.

A "USB mass-storage drive appeared" is *not* evidence that the LCD works.

## Gate B — build custom minimal diagnostic

After Gate A, use the official [Raspberry Pi pico-setup macOS instructions](https://github.com/raspberrypi/pico-setup#macos). Terminal-only development is sufficient; no VS Code extension, Arduino or LVGL needed.

~~~sh
# Install only when missing:
xcode-select --install
brew install cmake ninja
brew install --cask gcc-arm-embedded

# Pin a known Pico SDK version (tag 2.3.1):
mkdir -p ~/dev && cd ~/dev
git clone --depth 1 --recurse-submodules --branch 2.3.1 \
  https://github.com/raspberrypi/pico-sdk.git
export PICO_SDK_PATH="$HOME/dev/pico-sdk"

# From the MacDesk Buddy repository:
cd /path/to/physical_AI_exploration
cmake -S firmware/first_light -B firmware/first_light/build \
  -G Ninja -DPICO_BOARD=pico
cmake --build firmware/first_light/build --parallel
arm-none-eabi-size firmware/first_light/build/buddy_first_light.elf
~~~

The output is **firmware/first_light/build/buddy_first_light.uf2**. Run the repository regression suite with **python3 -m unittest discover -s tests -v**. CI separately cross-compiles the UF2 and exposes it as a workflow artifact; compilation is not display validation.

The conservative **PICO_BOARD=pico** setting targets the same RP2040 and uses a 2 MB flash limit for this small binary despite the board's advertised 16 MB. There is no filesystem or 16 MB-specific support here.

When both Gate A and the build succeed, enter BOOT mode again and copy the UF2 to **/Volumes/RPI-RP2/**:

~~~sh
cp firmware/first_light/build/buddy_first_light.uf2 /Volumes/RPI-RP2/
~~~

**Expected, but not physically verified:** eight vertical RGB565 bars, in order red/green/blue/yellow/magenta/cyan/white/black; top six rows white and bottom six rows black. This tests wiring, init, row offset, SPI and backlight. The pattern stays visible without the Mac service running.

## Gate C — one USB-C serial command

After flashing the custom diagnostic:

~~~sh
ls /dev/cu.usbmodem*
screen /dev/cu.usbmodemXXXX 115200
~~~

Use the **actual** device name printed by the first command in place of the placeholder. A USB CDC connection may print this greeting:

~~~text
{"v":1,"t":"hello","fw":"first-light-0.1","w":240,"h":280}
~~~

Type each exact line followed by Return; CR, LF and CRLF are accepted:

~~~text
{"v":1,"t":"ping"}
{"v":1,"t":"sleep"}
{"v":1,"t":"wake"}
~~~

Each valid command replies with **{"v":1,"t":"ok"}**. Sleep blanks the LCD and disables the backlight; wake displays the pattern again. Exit the macOS screen terminal with Control-A, K and confirmation.

This is an intentionally limited diagnostic subset of the project's [draft v1 codec](../../daemon/protocol.py), whose **canonical compact strings** are accepted. It is **not a general JSON parser**: reordered keys, extra whitespace, unsupported v1 types or malformed messages return an error; a line over the 512-byte protocol cap returns **too_long**. It does not implement the product's watchdog, face, daemon, brightness setting, keepalive, reconnection, touch, animation or state persistence. Successful USB-serial ping is not proof of any of those future functions.

## RAM and software validation

The firmware renders with a single **480-byte RGB565 scanline** and a fixed **513-byte serial line buffer** (993 bytes total before SDK/USB/stack allocations); it streams rows into the ST7789's internal GRAM using the documented **+20 row offset** in its 240 x 320 memory. It does **not** allocate a full 134,400-byte framebuffer or double buffers. The official panel specification advertises 262K colors; this diagnostic explicitly selects RGB565 (65,536 possible colors) for consistency with the existing desktop simulator.

The ST7789 init sequence follows the [independent same-board gud-panel port](https://github.com/fcjr/gudlet/tree/main/crates/gud-panel), which credits Waveshare's example. The port's hardware success does **not** prove this new C implementation works on the purchased board.

**Evidence ledger:** after delivery record: original demo file/hash and visual result → custom UF2 commit/hash and color-bar photo → serial port name and hello/ping/sleep/wake transcript. On a blank screen, reflash the **known-working official demo** first rather than changing hardware connections or the companion design. Keep the first physical results in the hardware log.
