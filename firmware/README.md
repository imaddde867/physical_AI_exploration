# ESP32 firmware

Targets **ESP32-S3 DevKitC-1 style** hardware, SSD1306 128x64 OLED at I2C address 0x3C, SDA GPIO8, SCL GPIO9. These are *project-selected pins*, **not universal ESP32-S3 pins**.

1. Install PlatformIO (VS Code extension, or `brew install platformio`).
2. Verify board variant, USB CDC setting, GPIO labels and 3.3 V-safe SSD1306 pinout against the purchased part.
3. Connect GND -> GND, VCC -> **3V3**, SDA -> GPIO8, SCL -> GPIO9. **Do not connect a 5 V-only OLED to 3V3.**
4. From `firmware/`, run `pio run`, then `pio run -t upload`.
5. On macOS, find the serial device with `ls /dev/cu.usb*`; run `pio device monitor -b 115200`.
6. The board emits a JSON `ready` message. `display:not_found` means check power, 0x3C address, wiring, and display controller.

PlatformIO and Arduino dependencies are version-ranged, not yet locked to an exact reproducibility snapshot. Pin mapping, display compatibility, and USB CDC behavior **require a physical test**. OLEDs sold as SH1106 are **not** drop-in SSD1306 replacements.
