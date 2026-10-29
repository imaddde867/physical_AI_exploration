# GC9A01 prototype — reference bill of materials

> Current purchase decision: [one Waveshare 1.64 V2 and a USB data cable](build-decision.md). Earlier comparisons and the GC9A01 basket below remain reference material. Check the delivered revision before flashing or finalizing a case.

This is the dated basket for the **implemented GC9A01 learning prototype**, not the current purchase recommendation. The selected purchase is one Waveshare 1.64 V2; its custom renderer and fitted enclosure remain work to complete. Use the decision linked above for the order.

## Reference basket (Otronic; advertised prices recorded 2026-10-26)

| Part | Specification | € |
|---|---|---:|
| ESP32-S3 N16R8 | 16 MB flash, 8 MB PSRAM, dual USB-C | 9.95 |
| **Round IPS LCD** | **OT8724, GC9A01, 1.28 inch, 240×240, SPI, 3.3 V** | **8.99** |
| MPU-6050 sensor | Optional motion input; defer for the face-first build | 3.75 |
| Breadboard | Reusable 830-contact prototype board | 2.99 |
| Female-female jumper wires | 40 × 20 cm | 1.85 |
| Male-female jumper wires | 40 × 20 cm | 1.85 |
| USB-C data cable | 1 m (omit if owned) | 2.65 |
| Estimated Finland delivery | Tracked Otronic shipment | 8.00 |
| **Total** | | **40.03** |

Without a new USB cable: **€37.38**. These totals retain the optional sensor for reproducible BOM arithmetic. Accessory prices were not individually rechecked in the audit; final VAT, stock and Finland checkout total are unverified. No purchase was made.

**Stop before ordering:** the screen has 8 positions at 2.54 mm pitch, but the seller does **not explicitly confirm the pins are pre-soldered**. Confirm header population or ask for a preassembled alternative. Confirm **BLK backlight behavior**, power at 2.8–3.3 V and the exact screen dimensions. All GPIO signals must be 3.3 V. See [shopping links](shopping-list.md) and [display research](display-choice.md).

**Long-term accessories:** a dependable low-voltage multimeter (e.g. UNI-T), a 150 mm caliper and eventually basic soldering tools. **Do not buy motors, batteries, cameras or a separate GPU machine for V0.** The Bambu Lab H2S is confirmed; identify the installed nozzle before printing.
