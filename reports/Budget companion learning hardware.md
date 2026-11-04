# Start small and learn reusable hardware

> **Superseded 2026-11-04:** the order actually placed was a Waveshare RP2040-Touch-LCD-1.69 from BerryBase (€29.80 delivered). The Pico WH + Pico-LCD-1.8 basket below was not bought.

**Chosen basket: Raspberry Pi Pico WH + Waveshare Pico-LCD-1.8 from BerryBase, plus a direct 30 cm LogiLink CU0240 cable from Reichelt (Finland storefront). Expected delivered total is €42.74–44.15 (see [Final basket](#final-basket-2026-11-04)).** It combines a useful face area, beginner-friendly MicroPython and a detachable wireless controller for later IoT experiments. The lower-priced integrated Waveshare ESP32-S3-LCD-1.54 remains conditional on supply and a Finland delivery quote; M5StickS3 justifies a roughly €44 stretch only if its onboard sensors and audio will be used. Start on ordinary USB beside the MacBook. Preserve the sleek enclosure as a later design goal. Prices and stock come from public listings checked 2026-11-04; they are not checkout totals, and the build is untested.

## Pico WH balances first success with reuse

The **Pico WH** has WLAN and fitted male headers; Waveshare's **Pico-LCD-1.8** has matching female headers for direct attachment. Choose WH specifically: an unheaded Pico W changes the assembly work. This combination needs **no soldering, breadboard, jumper wires or extra programmer** for the display project. Follow the manufacturer's USB-end orientation marks rather than guessing the stack direction. Its 160×128 display has a 35.04×28.03 mm active area on a 52×34.5 mm board: a useful landscape canvas for eyes, although less detailed than the square ESP32 option. ([Pico WH listing](https://www.berrybase.de/raspberry-pi-pico-wh-rp2040-wlan-mikrocontroller-board-mit-headern), [display listing](https://www.berrybase.de/1-8-zoll-lcd-anzeigemodul-fuer-raspberry-pi-pico-65k-farben-160x128-spi), [manufacturer assembly](https://www.waveshare.com/Pico-LCD-1.8.htm), [orientation guide](https://www.waveshare.com/wiki/Pico-LCD-1.8))

The learning advantage is a staged path: upload firmware, draw shapes, animate expressions, receive Mac commands, then explore Wi-Fi or reuse the detached Pico with sensors. Raspberry Pi documents the BOOTSEL/UF2 MicroPython installation, Thonny supports Intel and Apple Silicon Macs, and Waveshare supplies C/C++ and MicroPython examples. Use current **Pico W firmware**, rather than copying an old non-W filename from an example. The display covers GPIO physically; later simultaneous sensor experiments can require extra wiring or expansion hardware. Those are future purchases, not requirements for blinking eyes. ([MicroPython setup](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html), [Thonny](https://thonny.org/), [display examples and pin map](https://www.waveshare.com/wiki/Pico-LCD-1.8))

## Complete baskets matter more than board prices

The original Pico seller observations showed over 100 Pico WH boards and seven displays available. The originally priced 1 m cable has been replaced; its stock and price do not apply to the revised basket. These are observed listings, not reserved inventory. BerryBase publishes €9.90 EU delivery; its German 1–3-day labels do not establish a Finland arrival date. All three routes below include the MCU: **buy no additional controller**. ([Pico](https://www.berrybase.de/raspberry-pi-pico-wh-rp2040-wlan-mikrocontroller-board-mit-headern), [LCD](https://www.berrybase.de/1-8-zoll-lcd-anzeigemodul-fuer-raspberry-pi-pico-65k-farben-160x128-spi), [replacement data cable](https://www.reichelt.com/fi/en/shop/product/sync_charging_cable_usb-c_micro_b_0_3_m_white-428634), [shipping](https://www.berrybase.de/versand-und-zahlungsbedingungen))

| Route | Mandatory parts and posted charges | Optional holder | Finland planning total |
|---|---|---|---|
| **Pico WH + Pico-LCD-1.8** | €7.20 MCU + €8.80 LCD + posted €9.90 BerryBase EU shipping = **€25.90**, plus CU0240 €1.89 + €14.95 Reichelt Finland shipping = **€16.84** | €2 home-print material estimate | **€42.74–44.15** delivered; the range depends on BerryBase's VAT handling |
| **Waveshare S3 LCD1.54**, no touch/no battery | €16.49 board + €5 USB-C data cable allowance = **€21.49**, plus unknown shipping and tax adjustment | Supplied case; €2 print only if wanted | **Unknown**; under €30 only if added charges fit the remaining €8.51, or €6.51 with print |
| **M5StickS3** | €24.90 device + €9.90 shipping + €5 USB-C data cable allowance = **€39.80** | Supplied case; €2 print only if wanted | About **€42 without holder / €44 with holder**, estimated |

Prices are advertised VAT-inclusive, but Finland checkout VAT was not established. The earlier German-price planning calculation assumed German 19% inclusive amounts become Finnish **25.5%**: multiply posted goods/cable/shipping by 1.255/1.19, then add the €2 print estimate if used. This assumption is not a quote; the €5 cable allowance is also an estimate. A suitable existing data cable reduces cost. No battery, tools, SD card, subscription or extra power supply is required for the proposed Mac-powered first build. ([Finnish VAT](https://vero.fi/en/businesses-and-corporations/taxes-and-charges/vat/rates-of-vat), [Stick price](https://www.berrybase.de/en/m5stack-m5sticks3-esp32s3-mini-iot-dev-kit-8mb-flash-8mb-psram-1-14-zoll-lcd-wifi-2-4-ghz-5v), [EU freight](https://www.berrybase.de/en/footer/information/payment-dispatch))

## Cable update: direct connection near 33 cm

The user estimates the desired cable route at about **33 cm**, rejects adapters, and accepts a separate seller and second shipping fee. Replace the original 1 m cable with **LogiLink CU0240**, EAN **4052792080858**: nominal **30 cm**, white, USB-C male to USB 2.0 Micro-B male. The [manufacturer datasheet](https://www.2direct.de/media/pdf/ae/70/82/cu0240-cu0245.pdf) confirms 480 Mbps data support and 5 V / 2.4 A capability. It is not the wider USB 3.x Micro-B hard-drive connector. No adapter is required.

**Fit decision:** the independent review flagged that 30 cm is 3 cm shorter than the estimated route and leaves little slack for lid movement. It suggested the 0.5 m CU0241 (€2.10, same shipping) or a 1 m bench cable. The user is confident 30 cm works and chose CU0240. When fitting it, point the Pico's USB end toward the laptop, clip the cable near the board so lid movement doesn't pull on the Micro-B socket, and test the full lid swing before fixing anything permanently.

## Final basket (2026-11-04)

| Part | Seller | Link | Price | Stock seen |
|---|---|---|---:|---|
| Raspberry Pi Pico WH, RPI-PICO-WH (header pre-soldered) | BerryBase | [listing](https://www.berrybase.de/raspberry-pi-pico-wh-rp2040-wlan-mikrocontroller-board-mit-headern) | €7.20 | 100+ |
| Waveshare Pico-LCD-1.8, WS-19579 | BerryBase | [listing](https://www.berrybase.de/1-8-zoll-lcd-anzeigemodul-fuer-raspberry-pi-pico-65k-farben-160x128-spi) | €8.80 | 7 |
| BerryBase EU DHL shipping | BerryBase | [terms](https://www.berrybase.de/en/footer/information/payment-dispatch/) | €9.90 | |
| LogiLink CU0240, 0.3 m, EAN 4052792080858 | Reichelt FI | [listing](https://www.reichelt.com/fi/en/shop/product/sync_charging_cable_usb-c_micro_b_0_3_m_white-428634) | €1.89 | in stock, 4–5 business days |
| Reichelt Finland DHL shipping (up to 10 kg) | Reichelt FI | [table](https://www.reichelt.com/fi/en/shop/service/-12_28) | €14.95 | |
| **Total** | | | **€42.74–44.15** | |

Reichelt FI prices already include 25.5% Finnish VAT. BerryBase prices are posted with German VAT. €25.90 assumes BerryBase keeps the posted prices; €27.31 assumes it recalculates to 25.5%. Checkout will show which. The optional €2 printed holder is excluded. This is over the €30 target but within the €50 stretch. The second shipment adds €14.95.

Firmware: use `RPI_PICO_W-20260824-v1.29.0.uf2` from [micropython.org](https://micropython.org/download/RPI_PICO_W/), not the non-W v1.15 file linked from Waveshare's wiki. Waveshare's MicroPython demo (`Pico-LCD-1.8.py`, 10 MHz SPI, full RGB565 framebuffer) was verified by Waveshare on Pico, not Pico W. Expect roughly 15–25 fps for full-frame redraws (estimate). The panel is listed as TFT, not IPS, so check viewing angles in hand.

## Integrated ESP32 boards trade modularity for peripherals

**Waveshare ESP32-S3-LCD-1.54**, RobotShop RB-Wav-1876 without touch or battery, gives a 240×240 IPS face, 27.72 mm square active area, 8 MB PSRAM, 16 MB flash, microphones, speaker and motion sensor. A case is supplied; a cable is not listed. Its €16.49 offer is **on demand**, without an established replenishment date or delivery total. It is attractive if a quote lands within budget, especially for future sound/motion experiments, but unavailable delivery evidence prevents making it the default. Expansion uses pads and can require soldering later. ([Exact seller variant](https://eu.robotshop.com/de/products/waveshare-esp32-s3-154-lcd-display-development-board-240240-dual-microphones-wi-fi-bluetooth-5-kein-touch-keine-batterie), [hardware/package](https://www.waveshare.com/esp32-s3-lcd-1.54.htm), [development documentation](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.54))

**M5StickS3** earns the stretch through its IMU, microphone, speaker, buttons, IR and expansion connectors, with a documented Arduino/M5Unified starting path. The seller showed availability. Its 48×24×15 mm enclosure includes a 250 mAh battery; USB power is documented, so no battery purchase is needed. The compromise is a tiny 1.14-inch 135×240 face, approximately 24.91×14.86 mm active in landscape. Choose it for tilt-controlled expressions and audio learning, not a better-looking display; stop if the actual basket exceeds €50. ([Specification](https://docs.m5stack.com/en/core/StickS3), [screen area](https://docs.m5stack.com/en/accessory/display/Display_1.14_For_StickS3), [quick start](https://docs.m5stack.com/en/arduino/m5sticks3/program), [seller](https://www.berrybase.de/en/m5stack-m5sticks3-esp32s3-mini-iot-dev-kit-8mb-flash-8mb-psram-1-14-zoll-lcd-wifi-2-4-ghz-5v))

A generic ESP32 plus separate 1.3-inch SPI display was investigated, but both direct seller pages said unavailable. Cached stock claims do not make that a buying alternative. ([ESP32](https://www.berrybase.de/esp32-nodemcu-development-board), [LCD](https://www.berrybase.de/1.3-240x240-ips-hd-lcd-display-modul-spi-interface))

## Animation comes before intelligence and enclosure work

ESP32 PSRAM helps graphics and buffers; it does not turn these boards into a practical local conversational LLM. **No on-device LLM is expected.** The Pico is already wireless, and MicroPython offers a direct learning path; ESP32 adds a different ecosystem and more integrated peripherals rather than a prerequisite for “physical AI.” Let the board render the face and let the Mac provide behavior intelligence later. Local rules and USB messages need no subscription. This is the proposed architecture, not implemented integration.

Vendor examples establish a starting point, **not a tested animated Mac companion**. No exact ready-to-flash companion, measured frame rate, Mac serial exchange or physical header fit was validated. First run the matching graphics example, then a simple blink, then one Mac command. Check reconnect and sleep/wake behavior before mounting. The current thin shell and magnetic contacts remain later engineering work; a loose USB cable and optional desk cradle are enough now.

## Conclusion

Spend the first budget on a complete, reusable learning loop. The final basket above is the chosen order; prices and stock were observed 2026-11-04, and no checkout, purchase or hardware validation occurred here. The earlier [display shortlist](Companion%20display%20hardware%20shortlist.md) remains source history, while this budget-first recommendation now sets the prototype priority. Enclosure refinement becomes useful after real animation and measurements establish what must fit.
