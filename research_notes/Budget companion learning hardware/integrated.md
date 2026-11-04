# Budget integrated display + MCU boards

## Which exact board best serves an animated desktop companion?

### Takeaway
Waveshare ESP32-S3-LCD-1.54, **without touch, without battery**, is the strongest inexpensive integrated choice: square face, supplied case, substantial memory and reusable sensors/audio. Its €16.49 RobotShop offer is **on-demand**, so it is a conditional recommendation, not a verified purchasable-under-€30 basket. Research date: 2026-11-04.

### Cited Findings
- **S3 LCD1.54:** ESP32-S3R8 MCU and screen already integrated; 240×240 square IPS/ST7789, active area27.72×27.72mm, 8MB PSRAM/16MB flash; speaker, dual microphones, IMU, buttons and microSD. Case included; battery optional; package lists host and insulating sheet, **no cable**. Direct manufacturer range$14.99–18.99 spans touch/battery choices. — [Manufacturer](https://www.waveshare.com/esp32-s3-lcd-1.54.htm)
- Exact no-touch/no-battery seller variant RB-Wav-1876: **€16.49 tax included**, shipping calculated at checkout, on-demand/not normally stocked, ETA unavailable. — [RobotShop EU](https://eu.robotshop.com/de/products/waveshare-esp32-s3-154-lcd-display-development-board-240240-dual-microphones-wi-fi-bluetooth-5-kein-touch-keine-batterie)
- Shared 1.54 chassis46×46×22.5mm; display window28.12mm square. A different touch/battery variant is the dimensional source; manufacturer says all other hardware features match. — [Seller dimensions](https://www.robotshop.com/products/waveshare-esp32-s3-154-lcd-display-development-board-240240-dual-microphones-wi-fi-bluetooth-5-no-touch-w-battery), [Manufacturer variant distinction](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.54)
- **C6 LCD1.47 standard, SKU28563:** $11.99–12.99 range; -M SKU30381 has pre-soldered headers. Integrated C6/4MB flash, 172×320 tall TFT/ST7789, microSD, RGB LED, GPIO, USB-C. — [Manufacturer](https://www.waveshare.com/ESP32-C6-LCD-1.47.htm)
- Manufacturer outline: board20.32×36.37mm, max illustrated depth7.60mm; active17.39×32.35mm rounded rectangle. — [Dimension drawing inspected](https://docs.waveshare.com/assets/images/ESP32-C6-LCD-1.47-Dimensions-36ec12d1102e68ba047fc4530c24df3a.webp)
- **S3 LCD1.69 non-touch, SKU27932:** manufacturer catalog$15.31–15.99; 240×280 rounded-corner LCD, 8MB PSRAM/16MB flash, RTC/IMU/buzzer, USB-C programming/logging, 12-pin expansion connector. — [Price](https://www.waveshare.com/product/index.htm?dir=desc&limit=50&order=name&p=29), [Hardware](https://docs.waveshare.com/ESP32-S3-LCD-1.69)
- 1.69 board30×37.12mm, active27.972×32.634mm; connector/button protrusions and thickness require checking before CAD. — [Inspected manufacturer drawing](https://docs.waveshare.com/assets/images/ESP32-S3-LCD-1.69-details-size-15ed68e1d045a9474bad27533c1aa320.webp)

### Inferences
- 1.54's square face is a more natural expressive-eyes canvas than C6's narrow portrait; rotate C6 for wide eyes. 1.69 provides a larger, nearly square face but lacks supplied case and costs more locally.
- All three contain the MCU: **do not buy an extra ESP32**. For first blinking/animated face, mandatory hardware is board + USB data cable connected to Mac; no battery, breadboard, soldering iron, sensor or SD card needed. Draw assets from onboard flash. This follows integrated peripherals/USB programming; hardware operation was not tested.
- Existing thin59×49.65mm CAD is not a buying constraint. 1.54's22.5mm case is considerably thicker.

### Gaps
- Precise 1.54 bare-PCB dimensions versus complete case not independently checked.
- 1.69 USB-only battery-free operation is inferred from USB programming; explicit manufacturer battery-absent run statement not located.

## Is any delivered basket verified within €30?

### Takeaway
No delivered Finland total was verifiable without checkout. Do not present a board-only price as total.

### Cited Findings
- Electrokit C6 SKU41023184 **189SEK incl25% Swedish VAT, 136pcs in stock on opened page**; search cache earlier showed92. USB-C explicitly powers and programs. Headers are unsoldered;13 GPIOs available. — [Electrokit](https://www.electrokit.com/en/utvecklingskort-med-esp32-c6-och-microlcd-172x320px)
- Electrokit ships to Finland and applies local VAT; in-stock goods normally dispatched same day. Finland freight amount/transit not quoted here. — [Seller FAQ](https://www.electrokit.com/en/faq2)
- BerryBase C6€12.90 but unavailable; Electrokit S3 LCD1.69 279SEK but out of stock. — [BerryBase](https://www.berrybase.de/dev.-boards/esp8266-esp32-d1-mini/module), [Electrokit1.69](https://www.electrokit.com/utvecklingskort-med-esp32-s3-och-microlcd-240x280px)

### Inferences
- Provisional budget allowances supplied by coordinator: **€5 USB-C data cable +€2 home-print material**, estimates, not quotes. 1.54 = **€23.49 + unquoted shipping/tax adjustment**; ≤€30 only if those extras ≤€6.51. Reuse cable saves€5; supplied case makes print optional.
- C6 Electrokit =189SEK adjusted to Finland VAT + freight + estimated€7; no current currency conversion performed. Direct-China costs additionally need exchange rate, freight and confirmed tax treatment.

### Gaps
- None of RobotShop/direct China Finland availability, postage, arrival date, VAT settlement verified; no checkout/purchase/contact performed. Cannot promise €30 delivery.

## Is setup appropriate for a first project and reusable?

### Takeaway
Use Arduino and manufacturer display examples first, then send simple behavior commands from Mac. These are programmable development boards, not finished desktop-companion software.

### Cited Findings
- 1.54 exposes I2C/UART/USB **pads**; Arduino/ESP-IDF tutorials and resources are provided. Pad expansion can require soldering; onboard face/sensors do not. — [Docs](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.54)
- 1.69 older wiki provides simple graphics examples plus LVGL; pinned library/config setup is required (Arduino ESP32≥3.0.5, GFX1.4.9, LVGL8.4). — [Manufacturer examples](https://www.waveshare.com/wiki/ESP32-S3-LCD-1.69)
- C6 has Arduino/LVGL and image demos; manufacturer specifically warns **keep brightness≤50%**, otherwise heat can cause display shadows. — [Docs](https://docs.waveshare.com/ESP32-C6-LCD-1.47), [Examples](https://www.waveshare.com/wiki/ESP32-C6-LCD-1.47)

### Inferences
- Best progression: USB power/programming → autonomous blink → USB serial/Wi-Fi commands from Mac. AI behavior can remain on Mac; the boards render animation.

### Gaps
- No hands-on Mac compilation/USB-C-to-C verification, measured animation frame rate or beginner walkthrough quality test. Manufacturer tutorials include Windows-style port screenshots; expect adaptation to Mac port names. No claim of turnkey firmware.
