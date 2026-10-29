# MacDesk Buddy: ESP32-S3 round color display firmware

**Selected purchase:** [Waveshare 1.64 V2](../docs/build-decision.md) needs its own renderer, based on the revision-matched official V2 examples. Neither environment below targets that board.

**Scope:** this firmware is the GC9A01 learning prototype. It does not support the leading Waveshare AMOLED candidate or Mac app integrations. See [display choice](../docs/display-choice.md).

**Target hardware:** ESP32-S3 N16R8 development board, **GC9A01 1.28 inch circular IPS LCD** (240×240 pixels; SPI; 2.8–3.3 V supply) and optional MPU-6050 I²C motion sensor. The old monochrome OLED firmware is retired.

The firmware uses the documented [Adafruit GC9A01A Arduino driver](https://github.com/adafruit/Adafruit_GC9A01A), pinned at version 1.2.0 in PlatformIO.
**Approved on-screen artwork:** [one actual 240×240 PNG](../assets/face-idle-240.png). It is screen content only (no rendered bezel or robot body).

The PlatformIO hook in `firmware/scripts/embed_face.py` converts this PNG to an RGB565 header before compilation using only Python's standard library. The generated header `firmware/include/face_asset.h` is gitignored. The source file is 32-color indexed, then encoded as **10,514 flash-resident one-byte RLE tokens** with a palette. The display driver streams one 480-byte row buffer instead of allocating a 115 KB framebuffer.

To regenerate manually from the repository root: `python3 tools/face_asset.py`. To validate: `python3 -m unittest discover -s tests -v`. No Pillow or runtime image decoder is required.

**Visual scope:** One mature half-lidded character for all six serial mood names; tiny mouth/lid overlays and infrequent blink are the only changes. These are not six separate faces. Reproduction on the real IPS screen is **not** physically tested.

## Pin connections — verify real module labels first

**Disconnect USB while wiring; never apply 5 V to a 3.3 V GPIO.**

| ESP32-S3 | GC9A01 TFT (SPI) | Notes |
|---|---|---|
| 3V3 | VCC | Otronic product states 2.8–3.3 V supply |
| GND | GND | Shared ground |
| **GPIO11** | **SDA / DIN / MOSI** | **SPI DATA, not I²C SDA** |
| **GPIO12** | **SCL / CLK / SCK** | **SPI CLOCK, not I²C SCL** |
| GPIO10 | CS | SPI chip select |
| GPIO13 | DC | Data/command |
| GPIO14 | RES / RST | Active-low reset |
| — | BLK | **Leave open initially**, confirm actual module backlight spec before connecting |

The eight-pin header and its installed status are **not confirmed** by Otronic. Verify that connection is possible without soldering. Other GC9A01 breakout modules commonly illuminate with BLK floating or HIGH, but do not automatically apply that convention to an unidentified board.

| ESP32-S3 | Optional MPU-6050 (I²C only) |
|---|---|
| 3V3 | VCC (requires 3.3 V-safe breakout and I²C pull-ups) |
| GND | GND |
| GPIO8 | SDA |
| GPIO9 | SCL |

The I²C motion sensor remains completely separate from the LCD's SPI signals. See [color-coded wiring diagram](../assets/wiring.svg). The LCD uses a **write-only** bus; a microcontroller cannot report whether the panel is physically displaying pixels.

## Install, compile and upload

The default profile uses the native ESP32-S3 USB/OTG connector, not the CH343P UART connector. Install PlatformIO IDE in VS Code, or [PlatformIO Core](https://docs.platformio.org/en/latest/core/installation/index.html).

From the firmware directory:

~~~sh
pio run -e esp32s3_n16r8_usb
pio run -e esp32s3_n16r8_usb -t upload
pio device list
pio device monitor -b 115200
~~~

If using the board's **separate CH343P UART** connector, build and upload the **esp32s3_n16r8_uart** environment instead and monitor that port. New firmware may require holding BOOT and pressing RESET to enter USB download mode on the first flash; this depends on the actual board.

For the Mac-side controller, from repository root:

~~~sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m macdesk.demo --simulate --face neutral --watch
# Replace XXXX with the actual serial interface:
.venv/bin/python -m macdesk.demo --port /dev/cu.usbmodemXXXX --face neutral --watch
~~~

Firmware should print a ready event such as:

~~~json
{"type":"ready","display":"init_sent_unverified","driver":"GC9A01","imu":"not_found","protocol":1}
~~~

**This event only proves that initialization commands were sent over SPI, not that the screen works.** Verify colors and face orientation visually. The Mac host accepts six face names and can watch optional shake events.

## Troubleshooting

- No serial output: check the chosen native USB/OTG versus UART port, data cable, permissions and BOOT/RESET.
- Screen black: verify 3V3, GND, MOSI/SCK labels, DC, CS, RES, and **vendor-specific BLK** behavior. Review manufacturer's documentation before changing BLK wiring.
- Blank but backlit: check CS/DC/MOSI/SCK wiring, 240×240 GC9A01 controller and actual pinout; a write-only panel offers no automatic error report.
- Unusual colors or rotation: document it, then test GC9A01 rotation/inversion methods against your module (not yet calibrated).
- Sensor not detected: optional; inspect MPU-6050 I²C GPIO8/9 and address 0x68.
- Slow face updates: ensure hardware SPI wiring, reduce breadboard cable length; benchmark on the physical screen rather than predicting fps.
- Display stays dark while terminal reports init_sent_unverified: this is expected because SPI initialization cannot confirm hardware state.

No voice, LLM, camera, Wi-Fi, servos or battery is required for V0. Firmware compilation in CI is **not proof of electrical operation**.
