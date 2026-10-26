# Hardware basket: purchase only the essentials

**Goal:** €35–60 planning allowance, not a verified checkout total. Prices, local stock, taxes and shipping vary. The printer is already available. No LLM-capable embedded device is needed because the M4 Mac hosts higher-level logic.

| Priority | Part | Specification / reason | Planning allowance |
|---|---|---|---|
| Essential | ESP32-S3 DevKitC-1-compatible USB-C development board | ESP32-S3 with accessible GPIO8/9 and 3V3; avoid tiny boards without headers unless you plan to solder | €10–20 |
| Essential | 0.96-inch I2C OLED | 128x64 **SSD1306**, 3.3 V-compatible, 4 pins (GND/VCC/SCL/SDA), ideally pre-soldered | €4–9 |
| Essential | Jumper wires + breadboard | Female-to-female wires for pre-soldered modules, breadboard if required | €5–10 |
| Essential | USB data cable | Compatible with actual board port | €3–8 |
| Optional | Filament, small screws, adhesive feet | Use available printer materials first | €0–10 |
| Later | BME280 or MPU-6050 | Adds real sensing and I2C device management | €4–15 |
| Later | MG90S servo, 5 V regulated supply | Adds physical motion **after** power engineering | €10–25 |

**Check before ordering:** exact board's programming interface/pin labels, OLED driver (SSD1306 not SH1106), dimensions, headers, USB data cable, Finnish shipping/VAT. Search product pages rather than relying on assumed availability.

Supplier discovery: [Partco](https://www.partco.fi/), [Robomaa](https://www.robomaa.fi/), [Opencircuit](https://opencircuit.fi/), [DigiKey Finland](https://www.digikey.fi/), [Mouser Finland](https://www.mouser.fi/). These are research starting points, **not confirmed cart links or stock**.

**Printer identity not verified:** the supplied Bambu Academy URL is not itself sufficient evidence of the exact printer model. Verify the model on the printer's own display before choosing printable volume/profile.
