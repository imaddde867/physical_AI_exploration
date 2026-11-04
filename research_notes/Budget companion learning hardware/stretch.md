# Stretching the companion budget toward €50

Research checked 2026-11-04. Public pages only; no cart, checkout, supplier contact, or hardware testing.

## Does stretching buy useful learning rather than a larger screen?

### Takeaway
**Conditional yes: M5StickS3 is the strongest learning-oriented stretch, around €45 planned all-in.** It adds usable onboard motion, audio, IR and buttons in a finished enclosure. Its tiny rectangular screen is a compromise for the actual companion; do not stretch solely for the display.

### Cited Findings
- StickS3: ESP32-S3, 8MB flash + 8MB PSRAM, BMI270 IMU, microphone, speaker, IR transmit/receive, programmable buttons, HY2.0-4P and Hat2 16-pin expansion; enclosure **48×24×15mm**, **1.14in 135×240** screen, USB-C DC5V, internal250mAh battery. Box lists only one StickS3, not a cable. [M5Stack specification](https://docs.m5stack.com/en/core/StickS3)
- Screen **active area14.864×24.912mm**, separate from case or screen-module outline. [M5Stack replacement-screen specification](https://docs.m5stack.com/en/accessory/display/Display_1.14_For_StickS3)
- AtomS3R: **24×24×12.9mm**, **0.85in128×128**, BMI270 IMU plus BMM150 magnetometer, one programmable screen button, IR transmit, six bottom GPIO and HY2.0-4P. USB-C supplies power and downloads firmware; no battery listed, box contains only device. Arduino/UIFlow2 tutorials and factory demo available. [M5Stack](https://docs.m5stack.com/en/core/AtomS3R)
- StickC Plus2 has IMU, microphone, RTC, buzzer, three buttons and135×2401.14in screen, **48×24×13.5mm**; manufacturer shop now labels it **EOL**. [Specification](https://docs.m5stack.com/en/core/StickC-Plus2), [manufacturer shop](https://shop.m5stack.com/products/m5stickc-plus2-esp32-mini-iot-development-kit)

### Inferences
- StickS3 supports meaningful reuse: shake/tilt input, sound-reactive face, button interaction and later wired sensor experiments. No separate sensors, breadboard or soldering tools needed for these onboard exercises; USB cable is mandatory. Its onboard250mAh cell is included, not an extra purchase; desktop USB power is explicitly specified, so battery runtime need not determine this prototype.
- AtomS3R's square active side is approximately **15.3mm**, calculated from0.85in diagonal assuming square pixels. Suitable for simple eyes nearby, weak for readable status text. StickS3 landscape gives eyes roughly25mm width but only15mm height. Readability is judgment, not a physical test.
- Plus2 offers no convincing reason to choose older/EOL stock at similar price. AtomS3R is compact and reusable, but choose it only if size is more valuable than expressive face area.

### Gaps
- Bare PCB dimensions inside cases were not verified; case dimensions govern first prototype. USB operation is documented, but continuous unattended charging/always-on thermal behavior was not tested. No claim of permanent-installation suitability.

## Can either actually fit €50 delivered to Finland?

### Takeaway
Both fit a cautious planning allowance via BerryBase's published EU rate; these are **estimates, not verified Finnish checkout quotes**.

### Cited Findings
- StickS3 **€24.90 incl.VAT**,86pieces/available displayed;1–3days is seller processing/delivery wording, not a Finland arrival promise. [Product](https://www.berrybase.de/en/m5stack-m5sticks3-esp32s3-mini-iot-dev-kit-8mb-flash-8mb-psram-1-14-zoll-lcd-wifi-2-4-ghz-5v)
- AtomS3R **€20.50 incl.VAT**, available; locale/category copies show different counts42/88, so stock counts are unstable. [Seller](https://www.berrybase.de/en/development-boards/m5stack/atom)
- Published **EU DHL€9.90** below€199.99; no Finland exclusion stated. Named exceptions are Switzerland/Liechtenstein/Norway/Iceland. Finland eligibility inferred from EU category; no address entered. [Shipping policy](https://www.berrybase.de/en/footer/information/payment-dispatch)
- Finnish general VAT25.5%. [Tax authority](https://vero.fi/en/businesses-and-corporations/taxes-and-charges/vat/rates-of-vat)

### Inferences
| Plan | Board + shipping displayed | Cable + printed stand allowance | Conservative VAT-adjusted plan |
|---|---:|---:|---:|
| StickS3 |€34.80|€5 +€2|**€43.97**|
| AtomS3R |€30.40|€5 +€2|**€39.33**|

Calculation: (board +€9.90 +€5)×1.255/1.19 +€2; assumes displayed German19% VAT changes to Finnish25.5%, including delivery/cable. This is a budgeting assumption, not tax advice. Cable€5 and print€2 are estimates; stand optional because device already enclosed. No added tools or battery. Stop if actual delivered total exceeds€50.

### Gaps
- Exact cable SKU/price, Finland VAT recalculation and address eligibility remain unverified. Require **USB-C-to-C data cable** for USB-C-only MacBook; do not substitute a charge-only cable or assume an existing USB-A adapter.

## Is getting started documented for Mac and a first-time builder?

### Takeaway
Yes for local Arduino development and onboard demos; no verified drop-in MacBook-companion firmware.

### Cited Findings
- Official StickS3 sequence: Arduino IDE, M5Stack board manager, M5StickS3 selection, M5Unified/M5GFX libraries, USB programming mode and port selection, then ScrollGraph example. Related examples cover buttons/display/IMU/IR/mic/speaker. [Quick start](https://docs.m5stack.com/en/arduino/m5sticks3/program)
- Arduino IDE2 provides macOS installation instructions. [Arduino](https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-downloading-and-installing)
- StickS3 IR reception requires RMT and speaker amplifier disabled; external5V input/output configuration has constraints. [Manufacturer notes](https://docs.m5stack.com/en/core/StickS3)

### Inferences
- Small first session: upload display demo, animate eyes, map button/tilt to expression, then add a Mac serial message. This teaches reusable embedded work while keeping optional modules out of the purchase.

### Gaps
- No physical Mac/USB validation or custom companion code tested. Built-in demos establish access, not finished Mac integration. Skipped extra accessories and enclosure design; main risks are small-screen disappointment and final delivered-price changes.

