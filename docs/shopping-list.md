# MacDesk Buddy — concrete Finland shopping basket

**Checked:** 2026-10-26. Prices are advertised, not checked out; stock, regional VAT and delivery charges may change. Project is not hardware-validated.

## Recommended consolidated one-shop order

Supplier: [Otronic, Netherlands](https://www.otronic.nl/en/). Its [shipping table](https://www.otronic.nl/nl/verzending) lists tracked delivery to Finland for **€8**.

| Item (quantity 1 each) | SKU / specification | € | Direct link |
|---|---|---:|---|
| ESP32-S3 N16R8 development board | OT1022; 16 MB flash, 8 MB PSRAM, dual USB-C, seller-provided CH343P USB-UART, pre-soldered header **reported in a buyer review** | 9.95 | https://www.otronic.nl/en/esp32-s3-n16r8-devboard-16mb-flash-en-8mb-psram.html |
| White OLED 0.96-inch 128x64 I2C | OT822-C66; address 0x3C default, 3–5 V advertised, **SSD1306 controller and soldered headers unconfirmed** | 5.99 | https://www.otronic.nl/en/mini-oled-display-white-096-inch-128x64-i2c.html |
| 830-hole solderless breadboard | OT141-B94; bench testing only; will not fit inside final printed enclosure | 2.39 | https://www.otronic.nl/en/breadboard-830-hole-for-prototyping.html |
| Female-female Dupont wires 40x20cm | OT215-B93 | 1.85 | https://www.otronic.nl/en/dupont-jumper-cables-40-pieces-female-female-20cm.html |
| Male-female Dupont wires 40x20cm | OT211-B91 | 1.85 | https://www.otronic.nl/en/dupont-jumper-cables-40-pieces-male-female-20cm-dr.html |
| USB-C to USB-C **data** cable, 1 m | OT5551, omit if already owned | 2.65 | https://www.otronic.nl/en/usb-c-to-usb-c-1m-cable-for-data-and-fast-charging.html |

**Parts: €24.68. Estimated shipping: €8.00. Total: €32.68.** Without the cable: €30.03.

### OLED fallback — guaranteed controller, higher price

[Joy-IT SBC-OLED01V2 from Partco](https://partco.fi/tuote/joy-it-oled-n%C3%A4ytt%C3%B6-0-96-128x64-i2c-spi-v2-2588), **€11.29**, explicitly specifies **SSD1306**, 128x64, 3.3/5 V and I2C-compatible 4-pin header. Requires a separate shipment and adds delivery cost. Check its switch/configuration for I2C mode, rather than assuming all I2C/SPI boards default to I2C.

### Alternative Finnish controller

[ESP32-S3 N16R8 at Piikauppa](https://piikauppa.fi/kauppa/mikrokontrollerit/esp32/esp32-s3-devkitc-1-n16r8/), listed €15.90; verify header population and shipping before buying. Avoid making a second shipment purely to save a few euros on individual pieces.

## Useful *optional* tools

- [Digital multimeter, Otronic OT3201](https://www.otronic.nl/en/digital-multimeter) — €9.95, includes leads and battery; **only recommend for low-voltage electronics**, not mains safety work. Listings show inconsistent stock status, verify at checkout. For long-term use, consider a better branded UNI-T meter when your experiments become more demanding.
- [150 mm caliper, Otronic](https://www.otronic.nl/en/tools) — from €8.79. Useful for measuring PCB/display and reworking the CAD. A more durable metal option is listed at €18.35 but availability is inconsistent.
- [MPU-6050 I2C accelerometer/gyro](https://www.otronic.nl/en/acceleration-accelerometer-and-gyroscope-i2c-mpu.html) — €3.75; worthwhile for V2 motion interaction, **not required now**.

## Final checks before purchasing

1. Confirm the Otronic OLED is **SSD1306**, not SH1106/SSD1315, and that its 4-pin header is **pre-soldered**; otherwise use the explicit Joy-IT alternative.
2. Confirm the ESP32 board's exact manufacturer SKU, 3V3, GND, GPIO8 and GPIO9 pin positions and pre-soldered headers. Product is **compatible-style**, not confirmed to be manufactured by Espressif.
3. Check USB-UART CH343P macOS driver compatibility. The board also has a native USB port; depending on the driver, prefer native USB CDC as configured in `firmware/platformio.ini`. Test serial communication before building the enclosure.
4. Do **not** connect motor/servo loads to the board's 3V3 pin.
5. Confirm Bambu printer model and **measure your actual electronics** before slicing `cad/desk-buddy.scad`.
6. Do not purchase microphone, camera, actuator, LiPo battery, amplifier or separate power supply for the first build. Add them only after validating v0 and their electrical requirements.

**Technical references:** [project README](../README.md), [assembly](first-build.md), [BOM specification](bom.md), [firmware pinout](../firmware/README.md).
