# Start the companion on documented boards

**Recommend Waveshare ESP32-S3-Touch-AMOLED-2.41, no-case SKU 30563, confirmed V2/Rev2.0, for the first bench prototype.** Its integrated controller, USB and graphics examples remove the largest first-light risks. Keep ESP32-S3-LCD-1.54 without touch or battery as the lower-cost fallback. Neither establishes a thin final enclosure, and no bare panel clears the documentation gate. Preserve the approved black glass, silver framing and adaptable 59 × 49.65 mm proportions from the [product brief](../docs/product-brief.md); grow the enclosure around verified hardware. This is a **recommendation, not selected hardware or purchasing authorization**. Research observed 2026-11-04; no purchase, fabrication or powered testing occurred.

## Complete boards make first light practical

Figures below are **manufacturer claims/drawings**, not measurements; geometry calculations are labeled derivations. “Bare” 30563 means a complete populated board without a case, not a bare OLED. V1 and V2 firmware are incompatible; identify V2 by Rev2.0 on the bare PCB or a V2 QC label on the cased unit. SKU alone does not guarantee revision. ([Manufacturer](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41))

| Route | Display and active area | Documented assembly and access | Controller/software evidence |
|---|---|---|---|
| Preferred: 30563 V2 | 600 × 450 AMOLED; 49.65 × 37.22 mm landscape; RM690B0 QSPI, FT6336 touch | Glass 61.56 × 44.72 mm, 0.70 mm lens; populated assembly maximum 11.50 mm including header. PCB outline not separately established. USB exits an upper/lower long edge in landscape. | ESP32-S3R8, 512 KB SRAM, 8 MB PSRAM, 16 MB flash; official V2 LVGL examples. |
| Same board, cased: 30589 / -B | Same display | 64.00 × 47.20 × 11.80 mm landscape; different mechanical variant | Confirm V2 label; case is unnecessary for a custom enclosure. |
| Fallback: LCD1.54, no touch/no battery | 240 × 240 IPS; 27.72 × 27.72 mm active; ST7789 SPI | Supplied case 46 × 46 × 22.50 mm; front cover 40.15 mm square, window 28.12 mm square. Bottom USB exit. Bare stack unknown. | Same quoted S3R8 memory; GFX/LVGL examples and factory video playback. |

Sources: [AMOLED drawings](https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-2.41/Dimension_Appearance_Diagram.zip), [LCD dimensions](https://docs.waveshare.com/assets/images/ESP32-S3-LCD-1.54-details-size-bc50407d2c63d720a0351e843954a84b.webp), [LCD specifications](https://www.waveshare.com/esp32-s3-lcd-1.54.htm), [V2 source](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-2.41-V2/tree/main/02_Example).

The AMOLED dimensional PDFs date from 2024 and are **not explicitly V2**: confirm the received revision's envelope before CAD. Its glass already exceeds concept width by **2.56 mm** (derived), before walls or clearance. Both supplied assemblies exceed the 4.9 mm body plus 0.3 mm concept glass. Removing headers or cases has no verified thin-stack result. The AMOLED schematic shows a 34-pin LCD connection, distinct from the 45-pin bare panels below; exact mating part, pitch, FPC contacts and fold envelope remain unknown. Neither board has a documented cable-plug protrusion or bend allowance. ([Drawings](https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-2.41/Dimension_Appearance_Diagram.zip), [schematic](https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-2.41/ESP32-S3-Touch-AMOLED-2.41-sch.pdf))

## USB supplies the bench; local rendering limits work

**Schematic interpretation:** on AMOLED V2, Mac USB-C → J2 USB_5V → AO3401 Q2 → VCC → MP1605 buck → 3V3 supplies the MCU/display assembly; ETA6098 serves the separate optional battery branch. LCD1.54 uses VBUS → D4 Schottky → VSYS → TMI3112H buck → 3V3, likewise with separate battery charging. Both show 5.1 kΩ CC pulldowns and native USB D+/D− through 22 Ω resistors to GPIO20/19; standard 5 V, without documented PD negotiation. This supports battery-free USB operation electrically, but boot reliability and current have not been tested. Internal OLED rail generation beyond the board's LCD connector is not fully established. ([V2 circuit](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-2.41-V2/blob/main/04_schematic/ESP32-S3-Touch-AMOLED-2.41%20V2.0.pdf), [LCD circuit](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.54/ESP32-S3-LCD-1.54-Schematic.pdf))

Use a data-capable C-to-C cable from the Mac, render the face locally, and send small USB serial commands. Native CDC configuration is documented; a Mac sender and companion firmware still need implementation. At RGB565, an AMOLED frame requires **540,000 bytes**, two require 1,080,000; LCD requires 115,200 per frame (derived). Use PSRAM or partial buffers. No measured FPS or host-streaming rate exists. AMOLED examples use an sh8601 driver filename despite the RM690B0 specification; LCD's copied example uses GC9107 despite ST7789 specifications. Start with revision-matched vendor code and verify initialization. ([AMOLED Arduino](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41/Arduino), [LCD Arduino](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.54/Arduino))

## EU listings do not establish Finland delivered prices

These are public seller observations, potentially cached, **not reserved stock or checkout quotes**. No candidate has a verified quantity-one Finland delivered total, destination tax basis, freight and guaranteed lead time together.

| Seller / exact variant | Observed item price and availability | Finland delivery evidence |
|---|---|---|
| RobotShop RB-Wav-1904, no-case 2.41 | €54.99 “tax included”; On Demand, ETA unavailable; revision unspecified | Ships from Netherlands to EU; freight at checkout. Generic 1–6-day transit excludes uncertain replenishment. |
| OpenELAB Waveshare-30589 | €59.69 incl. VAT observed; other fetches €62.54/€65.38; title says V2, SKU means cased | Stock unconfirmed; €7.95 / 3–5-day service is conditional on destination. Finland eligibility and final VAT require checkout. |
| RobotShop RB-Wav-1876, LCD no touch/no battery | €16.49 “tax included”; On Demand, ETA unavailable | Same freight/replenishment uncertainty; exact language suffix unconfirmed. |
| ELTY 30589 cased | €57.44 incl. Polish 23% tax; unavailable | Not a Finland quote or immediate supply route. |

Sources: [RobotShop AMOLED](https://eu.robotshop.com/products/waveshare-esp32-s3-241-amoled-touch-display-development-board-600450-accelerometer-gyroscope-no-case?variant=53788178055504), [OpenELAB](https://openelab.io/fi/products/waveshare-esp32-s3-amoled-2-41-touch), [RobotShop LCD](https://eu.robotshop.com/nl/products/waveshare-esp32-s3-154-lcd-scherm-ontwikkelingsbord-240240-dubbele-microfoons-wi-fi-bluetooth-5-geen-aanraak-geen-batterij), [ELTY](https://elty.pl/en_US/p/Display-2.41-AMOLED-600450-Touch-Panel-ESP32-S3-WiFi-and-BT-RTC-IMU/3923), [shipping policy](https://eu.robotshop.com/policies/shipping-policy).

Manufacturer $49.99–53.99 AMOLED and $14.99–18.99 LCD ranges span variants, excluding verified Finland charges. LCD documentation maps non-touch -EN to **33866**, but store/seller options do not establish that exact suffix: reconcile the order SKU. Before buying, obtain revision/variant confirmation, physical stock and dispatch date, and a Finland quantity-one quote including destination VAT, freight, any import handling and a USB data cable. Do not add OpenELAB's generic freight to its location-sensitive item price. ([AMOLED store](https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm), [LCD docs](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.54))

## Bare panels still fail the thin-route gate

OLEDCORE **ID-024EGOIN152-01** claims $45.99, stock, 38.72 × 51.56 × 1.00 mm overall and 36.72 × 48.96 mm active, but specifies **MCU/MIPI**, not the board's QSPI assembly. Its 45-pin specification names Molex 502598-4591; mating mechanics and flex fold remain unverified. Claimed dispatch is 2–3 business days, generic delivery 7–12 days; neither is a Finland delivered quote. BOE240-450600 remains inquiry-only, without verified price or availability. ([OLEDCORE](https://oledcore.com/products/2-4-inch-ltps-amoled-display-450x600-mcu-mipi), [specification](https://oledcore.com/cdn/shop/files/ID-024EGOIN152-01_SPEC_V0.pdf?v=12462889038985755321), [BOE catalog](https://marketplace.oled-info.com/browse/amoled-displays))

Panox B024JMV-N50-6DP0 documents VCI 3.3 V, VDDIO 1.8 V, ELVDD +3.6 V, ELVSS −3.6 V and SWIRE as an **output**, but only a converter block diagram. Its glass/polarizer figures are not assembled thickness. No exact purchasable panel has a complete matched PMIC circuit, validated sequencing, connector and folded envelope in the reviewed evidence. RM690B0 alone establishes none of these. Keep both this thin route and the old GDOJ0269C01/P4 plan paused. ([Panox specification](https://www.panoxdisplay.com/uploadfile/datasheet/B024JMV-N50-6DP0_1.pdf))

## Conclusion

First-light acceptance checklist: confirm PCB revision and firmware; boot repeatedly from Mac USB with **no battery**; verify orientation and full active area; run idle/blink animation and record actual frame timing; exchange host commands; test disconnect/reconnect and sleep/wake recovery; measure startup/peak current, brightness and temperature; measure the complete stack, FPC and cable clearance. Only then adapt the enclosure and mount. The [CAD baseline](../cad/slab/DECISIONS.md) remains conceptual; separate open PR #13 dock geometry is excluded. The next useful result is reproducible battery-free animation and measured fit, not a thinner render.
