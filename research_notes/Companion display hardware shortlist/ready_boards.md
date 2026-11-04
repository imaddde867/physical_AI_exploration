# Ready-to-drive display and MCU boards

Research checked 2026-11-04 (Europe/Helsinki). Scope: wired animated face; approved concept exterior 59 × 49.65 mm, 4.9 mm body + 0.3 mm glass supplied by coordinator. No hardware, purchases, or CAD changes.

## Which complete boards are credible?

### Takeaway
Waveshare 2.41 AMOLED is the stronger face prototype, provided the enclosure grows. The square 1.54 LCD is a cheaper, simpler display/software fallback, but its supplied enclosure is much thicker and its electronics include unnecessary audio hardware.

### Cited Findings
- **Preferred exact model:** ESP32-S3-Touch-AMOLED-2.41, bare SKU **30563**; **-B SKU30589** adds a case. ESP32-S3R8 240 MHz, 512 KB SRAM, 8 MB PSRAM, 16 MB flash; 600 × 450 AMOLED, RM690B0 QSPI controller, FT6336 I2C touch. [Manufacturer documentation](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41)
- **Revision matters:** V2 bare board is marked Rev2.0; cased V2 has a V2 QC label. V1/V2 firmware is not interchangeable. V2 improves external USB routing. This is a revision requirement, not a separate published SKU. [Manufacturer documentation](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41)
- **Fallback exact model:** ESP32-S3-LCD-1.54-EN **SKU33866**, without touch; docs also list SKU33867 without -EN, touch -EN33868, touch33869. Same S3R8/8 MB PSRAM/16 MB flash; 240 × 240 IPS, ST7789 four-wire SPI. Select **without touch / battery not included** on store; confirm numeric order SKU because docs and store distinguish language/battery options differently. [Manufacturer docs](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.54), [store options](https://www.waveshare.com/esp32-s3-lcd-1.54.htm)
- Store pages observed $49.99–53.99 for 2.41 and $14.99–18.99 for 1.54 before shipping/taxes; these are option ranges, not quotes for selected variants. [AMOLED store](https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm), [LCD store](https://www.waveshare.com/esp32-s3-lcd-1.54.htm)

### Inferences
- Both have far more memory than a simple locally rendered blinking face needs. Lower LCD pixel count reduces rendering/data work, but does not make the 1.54 board physically simpler: it also carries audio codecs, amplifier, microphones and speaker. [LCD hardware](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.54)

### Gaps
- No ordering promise that SKU30563 will arrive V2; obtain revision confirmation before final enclosure design.

## What geometry actually fits?

### Takeaway
Neither assembled product fits the approved 5.2 mm overall thickness. Even bare 2.41 glass is wider than the 59 mm concept when landscape.

### Cited Findings
| Item | Visible area | Glass / front outline | Complete supplied assembly | PCB-only outline |
|---|---|---|---|---|
| 2.41 bare | 49.65 × 37.22 mm landscape | 61.56 × 44.72 mm landscape, R1 corners; lens thickness0.70 mm | **11.50 mm** maximum populated thickness including rear header; bare means no case, not a bare display | Not separately dimensioned in reviewed drawing; mounting pitch36.50 ×51.00 mm is NOT PCB size |
| 2.41 -B case | same | — | **64.00 ×47.20 ×11.80 mm** landscape | — |
| 1.54 LCD supplied case | **27.72 ×27.72 mm** active | Drawing front black cover40.15 ×40.15 mm; window28.12 ×28.12 mm | **46.00 ×46.00 ×22.50 mm** | Not established |

2.41 values transcribed from [manufacturer bare drawing](https://docs.waveshare.com/assets/images/ESP32-S3-AMOLED-2.41-Ar-demo-16-8e2b120a4ebee07033a3b5e92cb59240.webp), [case drawing](https://docs.waveshare.com/assets/images/ESP32-S3-AMOLED-2.41-Ar-demo-17-9b14b978fc984e2b38ab82b52254d7ec.webp), and [downloadable dimension PDFs](https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-2.41/Dimension_Appearance_Diagram.zip). LCD values from [manufacturer case drawing](https://docs.waveshare.com/assets/images/ESP32-S3-LCD-1.54-details-size-bc50407d2c63d720a0351e843954a84b.webp) and [active-area specification](https://www.waveshare.com/esp32-s3-lcd-1.54.htm).

- **Cable orientation:** 2.41 drawing shows a right-angle USB-C socket opening off a long PCB edge (left in rear portrait view), with cable approximately parallel to display plane. Rotate to landscape and it exits a long upper/lower edge. LCD1.54 case drawing places USB-C centered on the bottom edge, also parallel to display plane. [AMOLED drawing](https://docs.waveshare.com/assets/images/ESP32-S3-AMOLED-2.41-Ar-demo-16-8e2b120a4ebee07033a3b5e92cb59240.webp), [LCD drawing](https://docs.waveshare.com/assets/images/ESP32-S3-LCD-1.54-details-size-bc50407d2c63d720a0351e843954a84b.webp)

### Inferences
- 2.41 requires at least2.56 mm added concept width just for glass, plus enclosure clearance/walls. Its active landscape area ratio1.333 differs from concept exterior1.188; black bezel can preserve the desired outer proportions.
- Removing headers/case/battery may reduce thickness, but the resulting stack is unverified; no thin-fit claim should be made.

### Gaps
- Crucial: downloadable 2.41 PDFs have 2024 dates and appear to describe original hardware. Current documentation does not label mechanical drawings V2. Confirm V2 envelope, connector placement and tallest part before CAD lock.
- No verified bare LCD1.54 PCB/glass stack height, glass thickness, or complete unpopulated PCB dimensions. No cable plug protrusion/bend allowance specified for either board. Neither is proven compatible with0.3 mm concept glass.

## Is USB power/data and animation supported end to end?

### Takeaway
One USB data cable can provide power and native USB serial. Manufacturer code is a credible starting point for an embedded face; neither device is documented as a plug-and-play Mac external monitor.

### Cited Findings
- **2.41 V2 electrical path (schematic interpretation):** Mac USB-C → board Type-C J2; CC1/CC2 have5.1 kΩ pulldowns; USB_5V → Q2 AO3401 power path → VCC → U5 MP1605GTF-Z buck →3V3 for MCU/display. USB_5V also feeds ETA6098 battery charger; battery branch is separate. D+/D− route through22 Ω resistors to native S3 GPIO20/19. No external USB-UART bridge is needed. [Manufacturer V2 schematic](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-2.41-V2/blob/main/04_schematic/ESP32-S3-Touch-AMOLED-2.41%20V2.0.pdf)
- **LCD1.54 electrical path (schematic interpretation):** Type-C VBUS → D4 Schottky → VSYS → TMI3112H buck →3V3, including LCD and MCU; ETA6098 charges optional battery separately. Two5.1 kΩ CC pulldowns; D+/D− →22 Ω/ESD network →GPIO20/19 native USB. [Manufacturer schematic](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.54/ESP32-S3-LCD-1.54-Schematic.pdf)
- Both guides explicitly say native USB, with USB CDC On Boot/HWCDC configuration for Arduino Serial. [2.41 Arduino guide](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41/Arduino), [1.54 Arduino guide](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.54/Arduino)
- 2.41 official **V2** source includes Arduino09_LVGL_Test and ESP-IDF09_LVGL_V9_Test, QSPI setup, landscape600 ×450, LVGL timer/flush handling and touch. Source uses an sh8601 driver filename despite RM690B0 product specification: start from exact vendor initialization rather than choosing by filename. [V2 examples](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-2.41-V2/tree/main/02_Example), [actual Arduino source](https://raw.githubusercontent.com/waveshareteam/ESP32-S3-Touch-AMOLED-2.41-V2/main/02_Example/Arduino/09_LVGL_Test/09_LVGL_Test.ino)
- LCD factory firmware includes video playback; manufacturer provides GFX HelloWorld and LVGL8/9 examples plus [full source](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-1.54). Its copied Arduino LVGL example instantiates Arduino_GC9107 despite the ST7789 hardware specification: verify current source/display driver rather than treating documentation snippets as tested. [Store firmware description](https://www.waveshare.com/esp32-s3-lcd-1.54.htm), [Arduino examples](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.54/Arduino)

### Inferences
- Minimal system: Mac → USB data-capable cable → display board; firmware renders eyes locally and accepts small serial commands from a Mac app. No battery, separate display controller, Wi-Fi, or cloud is needed. This is a proposed architecture, not shipped companion firmware.
- Electrical schematics provide an independent USB supply path with battery absent. Standard5 V operation is sufficient; USB-PD negotiation is not shown. A USB-C Mac needs a data-capable C-to-C cable; a USB-A host/hub needs A-to-C.

### Gaps
- No measured power/current, validated USB sleep/wake behavior, Mac app integration, animation frame rate, USB frame-stream throughput, or hardware test. No evidence of an included USB cable on either store package list.
- No manufacturer animated-face demo found in scoped search. LVGL/video evidence establishes graphics capability, not guaranteed target performance.
