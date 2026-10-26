# MacDesk Buddy — color-display shopping basket

**Updated 2026-10-26:** The old monochrome calculator-looking OLED is NOT in the basket. Prices are seller listings, not final checkout totals; VAT, stock and delivery may change.

## Buy from a single EU store: Otronic

| Quantity | Part | List € | Product link |
|---:|---|---:|---|
| 1 | ESP32-S3 N16R8 16 MB flash / 8 MB PSRAM | 9.95 | [Controller](https://www.otronic.nl/en/esp32-s3-n16r8-devboard-16mb-flash-en-8mb-psram.html) |
| **1** | **OT8724 1.28 inch round GC9A01 240×240 IPS color LCD** | **8.99** | **[Round IPS screen](https://www.otronic.nl/en/1-28-round-tft-lcd-240-240-gc9a01-spi-for-arduino)** |
| 1 | MPU-6050 I²C motion sensor | 3.75 | [Sensor](https://www.otronic.nl/en/acceleration-accelerometer-and-gyroscope-i2c-mpu.html) |
| 1 | 830-hole solderless breadboard | 2.39 | [Breadboard](https://www.otronic.nl/en/breadboard-830-hole-for-prototyping.html) |
| 1 | Female-female Dupont wires, 40 × 20 cm | 1.85 | [Female-female cables](https://www.otronic.nl/en/dupont-jumper-cables-40-pieces-female-female-20cm.html) |
| 1 | Male-female Dupont wires, 40 × 20 cm | 1.85 | [Male-female cables](https://www.otronic.nl/en/dupont-jumper-cables-40-pieces-male-female-20cm-dr.html) |
| 1 | USB-C-to-USB-C DATA cable 1 m | 2.65 | [USB data cable](https://www.otronic.nl/en/usb-c-to-usb-c-1m-cable-for-data-and-fast-charging.html) |
| — | [Estimated tracked Finland delivery](https://www.otronic.nl/nl/verzending) | 8.00 | Same seller |
| | **Total estimated delivered** | **39.43** | |

**Without buying another data cable: €36.78.** This is only €3.00 more than the €36.43 previous monochrome-OLED basket.

## Display alternatives (not drop-in compatible with current firmware)

- **[Otronic 1.3 inch square ST7789 IPS 240×240](https://www.otronic.nl/en/1-3-inch-spi-tft-lcd-display-rgb-st7789-3-3v) — €6.25.** Good colors but square shape and different firmware/CAD; cheaper if a rectangular face is preferred.
- **[Waveshare 1.28 inch round GC9A01](https://www.waveshare.com/product/1.28inch-lcd-module.htm) — $14.99 list.** Offers official documentation and an included 8-pin cable; check shipping if Otronic's header cannot be used without soldering.
- **[Electrokit Waveshare module](https://www.electrokit.com/en/lcd-module-round-1.28240x240px-spi) — 199 SEK list.** Stock and Finland shipping require a live checkout check.

## Required checks before payment

1. The Otronic OT8724 spec confirms GC9A01, 240×240 IPS, 2.8–3.3 V, 8 pins and a 44×36×5 mm board. **It does NOT confirm its header is soldered or how BLK is electrically controlled.** Ask the vendor; the first-build plan assumes no soldering.
2. The LCD uses **SPI**, even though its SCL and SDA pads resemble I²C labels. They map to ESP32-S3 GPIO12 SCK and GPIO11 MOSI, with GPIO10 CS, GPIO13 DC and GPIO14 RES. MPU-6050 alone uses GPIO8 and GPIO9 for I²C.
3. Check the ESP32 board header labels, 3V3 and native USB/OTG socket. Do not apply 5 V to ESP32 GPIO.
4. The optional BLK pin is intentionally left unconnected in the default design until the exact module's backlight operation is verified. If the display stays dark, check vendor documentation before changing this wire.
5. The MPU-6050 breakout should keep its I²C pullups at 3.3 V. Measure actual parts before designing final board mounts.
6. The printer must be identified from its label/display; the Academy URL is not confirmation of a particular Bambu printer.

**No products were purchased on your behalf.** 
