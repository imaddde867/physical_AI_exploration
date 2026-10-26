# MacDesk Buddy ESP32-S3 firmware

**Target:** ESP32-S3 DevKitC-1 *style* N16R8 board (16 MB QD flash, 8 MB OPI PSRAM), 0.96-inch **SSD1306** 128×64 I²C OLED, optional **MPU-6050** I²C motion sensor.

This code has automated compile checks, but **has not been flashed or electrically tested on the actual purchased modules**.

## Pin wiring (power disconnected while wiring)

| ESP32-S3 | OLED | Optional MPU-6050 |
|---|---|---|
| 3V3 | VCC (only if display is 3.3 V safe) | VCC (only if breakout operates at 3.3 V) |
| GND | GND | GND |
| GPIO8 / SDA | SDA | SDA |
| GPIO9 / SCL | SCL | SCL |

Both devices share SDA and SCL. OLED default address **0x3C**, MPU-6050 address **0x68**. Inspect actual PCB silkscreen and headers; no ESP32 GPIO pin is safe to connect to 5 V. **Do not power motors from 3V3.**

[Wiring diagram](../assets/wiring.svg)

## The two USB-C ports matter

The Otronic N16R8 board has two USB-C ports:

- **Native ESP32-S3 USB/OTG:** default firmware environment <code>esp32s3_n16r8_usb</code> enables USB CDC on boot. Choose this port for Mac serial communication without depending on CH343P UART driver support.
- **CH343P USB-to-UART:** use alternative environment <code>esp32s3_n16r8_uart</code>, which disables USB CDC on boot. Using the opposite USB port from the chosen firmware may give **no Serial output**.

The seller board is not verified as a genuine Espressif PCB, so confirm its actual pin labels and which connector goes to which interface.

## Flash and test

Install the [PlatformIO IDE extension](https://platformio.org/install/ide?install=vscode) or PlatformIO Core 6.2.0 (for example with pipx). From the repository root:

~~~sh
cd firmware
pio run -e esp32s3_n16r8_usb
pio run -e esp32s3_n16r8_usb -t upload
pio device list
pio device monitor -b 115200
~~~

Choose the **native USB/OTG connector**; monitor the matching new serial port. Native USB first flash may require holding BOOT and tapping RESET before upload, followed by a reset after first flashing. If using CH343P UART, replace the environment name with <code>esp32s3_n16r8_uart</code> in both build/upload commands and select its serial device instead.

For a Mac host (run from repository root):

~~~sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m macdesk.demo --simulate --face happy --watch
# Replace /dev/cu.usbmodemXXXX with the actual native USB port:
.venv/bin/python -m macdesk.demo --port /dev/cu.usbmodemXXXX --face happy --watch
~~~

**Expected:** an initial ready JSON event (display ok; imu ok/not_found), ACKs for valid expressions, and optional shake events from the MPU. A powered USB port may not show the initial ready message if the host connected late; valid face commands still ACK.

## Troubleshooting

- No serial output: wrong USB port for chosen firmware env, charging-only cable, permissions, missing manual BOOT/RESET on first flash.
- Ready says display not_found: check 3V3/GND, pin mapping, I²C address 0x3C, actual SSD1306 model.
- Ready says imu not_found: sensor optional; check 0x68 address, compatible breakout and SDA/SCL.
- Excess false shake: threshold is experimental (|‖accel‖−1g| > 0.55g twice at 40ms sample spacing, 1.5s cooldown). Calibrate on your assembled enclosure; not a production gesture detector.
- Invalid JSON / unsupported face / overlong line: firmware sends error; overlong input is ignored until the next newline.
- No wireless operation, audio or LLM in this firmware by design.

PlatformIO Core 6.2.0 / Espressif32 7.1.3 and library versions are explicitly fixed in the build configuration and CI. This is stronger than a floating dependency setup, but a physical verification log is still required.
