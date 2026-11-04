# Bare-panel display and controller route

## Is there a purchase-ready thin RM690B0 route?

### Takeaway
Research date: 2026-11-04. **No complete bare-panel route meets the evidence threshold yet.** Purchasable RM690B0 panels exist, but the documented MCU/MIPI bare panel is not established as the same QSPI assembly used by Waveshare. Do not buy one on the assumption that the driver IC name establishes compatibility. [OLEDCORE product](https://oledcore.com/products/2-4-inch-ltps-amoled-display-450x600-mcu-mipi); [its specification](https://oledcore.com/cdn/shop/files/ID-024EGOIN152-01_SPEC_V0.pdf?v=12462889038985755321); [Waveshare documentation](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41)

### Cited Findings
- OLEDCORE lists **ID-024EGOIN152-01**, no touch, RM690B0, 450×600, active area 36.72×48.96 mm, overall 38.72×51.56×1.00 mm, **$45.99**, “In Stock” and direct purchase. These are seller claims observed today, not an inventory reservation or delivered quote. Its interface is explicitly **MCU/MIPI**, not QSPI. [Product](https://oledcore.com/products/2-4-inch-ltps-amoled-display-450x600-mcu-mipi)
- Its PDF identifies IM[1:0]=00 as MIPI and 11 as MCU; it supplies separate MCU/MIPI initial command lists, including sleep-out, 120 ms wait and display-on. It lists a **45-pin** connection and Molex **502598-4591** as matching connector; FPC ships unfolded. [Specification, physical pages 6, 13–14, 21](https://oledcore.com/cdn/shop/files/ID-024EGOIN152-01_SPEC_V0.pdf?v=12462889038985755321)
- Hicenda lists a 2.4-inch 450×600 RM690B0 product at **$36.95**, with separate bare-display and display+HDMI-board packaging choices. The reviewed listing does not establish an exact purchasable QSPI FPC SKU with a public complete reference circuit. [Seller listing](https://www.hicendadisplay.com/products/2-4-inch-450x600-amoled-display-rm690b0-driver-800nits-60hz?variant=44310164766798)
- Good Display publicly identifies **GDOJ024C45**, RM690B0, SPI/MCU/MIPI, active 36.72×48.96 mm and 60 Hz; stock/retail fields are blank. A specification and RM690B0 datasheet are linked. This establishes an alternative model, not confirmed availability or electrical interchangeability. [Manufacturer](https://www.e-paper-display.com/products_detail/productId=334.html)
- **BOE240-450600** appears in the OLED marketplace catalog at 38.72×51.56 mm with thickness explicitly absent. This is a catalog identifier, not a proven orderable Waveshare replacement. [Catalog](https://marketplace.oled-info.com/browse/amoled-displays)

### Inferences
- The OLEDCORE outline rotated to landscape is 51.56×38.72 mm. Against the requested 59×49.65 mm exterior, that leaves 7.44 mm and 10.93 mm total respectively **before** walls, flex clearance, adhesive and connector routing. This is outline arithmetic, not verified enclosure fit. [Dimension source](https://oledcore.com/products/2-4-inch-ltps-amoled-display-450x600-mcu-mipi)
- “RM690B0” does not select a pinout, factory configuration, power assembly or initialization. A bare 45-pin MCU/MIPI purchase cannot currently be substituted for the Waveshare QSPI module. [OLEDCORE specification](https://oledcore.com/cdn/shop/files/ID-024EGOIN152-01_SPEC_V0.pdf?v=12462889038985755321); [Waveshare V1 schematic](https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-2.41/ESP32-S3-Touch-AMOLED-2.41-sch.pdf)

### Gaps
- **Purchase blocker:** exact orderable QSPI panel/FPC assembly corresponding to the Waveshare board, plus its approved schematic and sample code, remains unidentified.
- OLEDCORE's public documentation supports MCU/MIPI. QSPI compatibility must not be inferred. The listing's 1.00 mm overall thickness and the PDF's 0.5 mm panel-glass figure measure different things; do not report 0.5 mm as complete module thickness.
- No transaction, supplier message, physical measurement, firmware build or first-light test was performed.

## What do the bare-panel mechanical and power documents actually establish?

### Takeaway
The public Panox **B024JMV-N50-6DP0** specification supplies useful rails, pin roles and a named mating connector, but only a block diagram for the external power conversion. This is a conditional thin research lead, not a complete documented design. [Panox specification](https://www.panoxdisplay.com/uploadfile/datasheet/B024JMV-N50-6DP0_1.pdf)

### Cited Findings
- Panox documents RM690B0, SPI/MCU/MIPI, 450×600, outline 38.72×51.56 mm, active 36.72×48.96 mm, 60 Hz and “1/3RAM.” It gives glass panel thickness 0.5 mm, polarizer 0.147 mm and SCF 0.13 mm separately; these are **not a verified assembled stack height**. Its drawing names Molex 502598-4591. [PDF physical pages 4–6](https://www.panoxdisplay.com/uploadfile/datasheet/B024JMV-N50-6DP0_1.pdf)
- Nominal rails are **VCI 3.3 V, VDDIO 1.8 V, ELVDD +3.6 V, ELVSS −3.6 V**. Pin 14 SWIRE is explicitly **output**, for controlling the power IC; pin 16 reset is active-low. External DC-DC conversion is a block, not a component reference circuit. Power/current fields are mostly TBD. [PDF physical pages 14–16, 22–23](https://www.panoxdisplay.com/uploadfile/datasheet/B024JMV-N50-6DP0_1.pdf)
- Startek's **KD024EGOIN144** listing claims 1.00 mm overall, 45 pins, “0.6 mm” pitch and 3.3 V input. These broad marketing fields do not eliminate multi-rail requirements; its pitch must not be transferred to another SKU. [Manufacturer listing](https://www.startek-lcd.com/product/1424-KD024OLEDN144-2.4-inch-450x600-resolution-LTPS-AMOLED-display-with-SPI-MCU-MIPI-interface.html)

### Inferences
- This panel family has a plausible glass-size advantage, but a new controller board needs a validated positive/negative OLED supply, logic supply, sequencing, interface configuration and flex connection. A generic 3.3 V ESP32 breakout is not a complete bare-panel solution. [Panox PDF](https://www.panoxdisplay.com/uploadfile/datasheet/B024JMV-N50-6DP0_1.pdf)
- The old GDOJ0269C01/RM69700/DSI plan should remain paused. Nothing found here resolves that panel's missing connector/init/sequencing evidence; these RM690B0 results concern different products.

### Gaps
- **Power blocker:** no reviewed bare SKU provides a complete, matched public OLED PMIC circuit with component values and validated sequence. Do not transplant the old panel's rail values or MCU-driven SWIRE assumptions.
- **Mechanical blocker:** flex exit direction, folded component envelope, minimum bend radius, shipped contact orientation and total folded thickness have not been visually verified. PDF screenshot attempts returned no inspectable image through the research tool; local download was unavailable. No invented bend allowance or stack depth is used.
- **Connector blocker:** panel specification names 502598-4591, but the Molex primary drawing could not be retrieved. Exact pitch/contact mechanics, availability and any replacement mating part are unverified from primary documentation. Distributor search results suggest 0.3 mm and obsolete status; excluded from a confirmed design until checked against Molex drawings. Do not use Startek's 0.6 mm field to design the Panox/OLEDCORE connector.

## What documented controller route is useful now, and what development remains?

### Takeaway
The **complete Waveshare ESP32-S3-Touch-AMOLED-2.41 board** is the documented QSPI/USB first-light route. It can guide a later custom board only after the exact display assembly is sourced; no 4.9 mm finished-body fit is established. [Waveshare](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41); [resources](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41/Resources-And-Documents)

### Cited Findings
- Waveshare identifies SKU **30563** board and **30589** cased version, ESP32-S3R8 at 240 MHz, **512 KB SRAM, 8 MB PSRAM, 16 MB flash**, RM690B0 **QSPI**, 600×450 display and FT6336 I²C touch. Native USB data is GPIO19/20. **V1/V2 firmware is not interchangeable**; OLED reset changes from GPIO21 to EXIO0, among other differences. [Official documentation](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41)
- Resources explicitly provide V1 examples, official V2 GitHub examples, both schematics, dimension drawing ZIP and RM690B0 datasheet. [Official resources](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41/Resources-And-Documents)
- Official ESP-IDF demos include **09_LVGL_Test / 10_FactoryProgram** for V1; V2 repository contains **09_LVGL_V9_Test / 10_FactoryProgram**. V1 requires IDF≥5.1.4; V2 documentation recommends 5.5.x. [Development guide](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41/ESP-IDF); [official V2 example tree](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-2.41-V2/tree/main/02_Example/ESP-IDF)
- V1 schematic exposes a **34-pin LCD connection**, QSPI data/clock/select, reset/TE, touch and display supply nets. It includes USB-C 5 V, power path/charger ETA6098 and onboard regulation. This is not the bare-panel 45-pin interface above. [V1 schematic](https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-2.41/ESP32-S3-Touch-AMOLED-2.41-sch.pdf)

### Inferences
- At RGB565, a full 450×600 image is **540,000 bytes**, two buffers **1,080,000 bytes** (calculated). Use PSRAM/partial buffers rather than assume the quoted internal SRAM holds a full frame plus the application. Local sprite animation with Mac USB commands is a credible architecture; sustained Mac framebuffer streaming needs separate throughput testing. [Resolution/memory basis](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41)
- Remaining software work: version-match the vendor demo; demonstrate reliable battery-free USB boot; render companion assets; implement a USB command protocol and Mac sender; measure frame rate, USB disconnect/suspend behavior and peak current. Vendor demos are not an existing Mac companion application.

### Gaps
- Exact panel/module SKU, complete module power circuitry, 34-pin connector part/pitch and flex contact orientation are not provided by the examined board-level text. The schematic stops at the LCD connector; it does not establish the panel's internal rail design.
- Dimension ZIP exists but could not be inspected here. No complete board/module measured Z envelope, independent cover-glass thickness, folded flex clearance or 4.9 mm-body feasibility is established.
- V1 schematic labels the MCU differently from the current product memory description; use actual purchased PCB revision and fitted part, not a mixed-version BOM.
- USB power/data wiring is documented, but no Mac companion, peak-current budget, battery-free reliability or animation benchmark was tested. **Thin-route evidence threshold remains unmet; first-light board evidence must not be presented as proof of final thin hardware.**
