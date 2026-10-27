# MacDesk Buddy hardware purchase audit

Research scope: purchasing-relevant specs, price evidence, compatibility, readability, and mounting safety in `README.md`, `docs/hardware-options.md`, `docs/shopping-list.md`, `docs/display-choice.md`, `docs/bom.md`, `docs/printing.md`, and `hardware/{bom,options}.json`. Sources checked 2026-10-27; live stock and prices are volatile. Status labels below mean **verified** (primary source supports it), **false/outdated** (source contradicts the repo), or **unverified** (not established by source or physical test).

## Which screen and platform best fits the stated first-build goal?

### Takeaway
For an expressive, glanceable character beside the MacBook, keep the supported GC9A01 path only if the goal is electronics learning and the ~32 mm circle is acceptable. For a more polished turnkey character, the Waveshare/Taby 1.32-inch round AMOLED is the strongest display-first candidate; for small text, a rectangular external HDMI monitor has more usable area and can act as a true Mac display, but it changes this from a portable ESP32 character into a separately powered desktop monitor. No option has verified delivery totals or a tested laptop-side mounting solution.

### Cited Findings
- **Verified:** Otronic OT8724 seller page lists €8.99, 240×240, GC9A01, 4-wire SPI, 2.8–3.3 V, 8 pins at 2.54 mm pitch, 32.4 mm round display area, PCB 44×36×5 mm. It does not state header population or BLK drive behavior. [Otronic OT8724](https://www.otronic.nl/en/128-rond-tft-lcd-240240-gc9a01-spi-voor-arduino.html)
- **Verified:** Waveshare round AMOLED 1.32 board has 466×466, 500 cd/m², CO5300/QSPI display, CST820 touch, ESP32-S3 with 8 MB flash and 8 MB PSRAM, mic/audio codec, USB-C, and battery/speaker/peripheral headers. [Waveshare product spec](https://www.waveshare.com/product/esp32-s3-touch-amoled-1.32.htm); [Waveshare docs](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-1.32)
- **Verified:** Taby installation supports the Waveshare 1.32 round board target and its 466×466 screen. The current Taby project page says the round case is “coming soon,” and lists 27 animations. [Taby install matrix](https://github.com/TRIIIS-LABS/firmware-taby/blob/main/INSTALL.md); [Taby project](https://github.com/TRIIIS-LABS/firmware-taby)
- **Verified:** Waveshare 1.64 board is 280×456 AMOLED, 350 cd/m², CO5300/QSPI, touch, IMU, TF slot, ESP32-S3R8 with 16 MB flash/8 MB PSRAM. Taby explicitly supports **V1 only**, and sells case STL/3MF files for this board. [Waveshare 1.64 product](https://www.waveshare.com/ESP32-S3-Touch-AMOLED-1.64.htm); [Taby install matrix](https://github.com/TRIIIS-LABS/firmware-taby/blob/main/INSTALL.md); [Taby project/case status](https://github.com/TRIIIS-LABS/firmware-taby)
- **Verified:** The Taby 1.64 case’s documented assembly uses a strong 20×10×2 mm magnet and rubber grip tape; the official print pack specifies G-code for Bambu P1S and a 3MF A1 mini profile, so a different printer needs its own slicing. [Taby project/case notes](https://github.com/TRIIIS-LABS/firmware-taby)
- **Verified:** A Waveshare round 1.28 GC9A01 module is $14.99, 240×240, 32.4 mm active diameter, PCB 40.4×37.5 mm, and includes a 20 cm PH2.0 8-pin cable; pin table documents BL. It remains a separate display plus MCU. [Waveshare module](https://www.waveshare.com/product/1.28inch-lcd-module.htm); [Waveshare wiki pinout](https://www.waveshare.com/wiki/1.28inch_LCD_Module)
- **Verified:** The Otronic 1.3-inch ST7789 alternative is €6.25 including VAT, 240×240, IPS, 4-wire SPI; this is another small square module, not a meaningful text-area upgrade over the round module. [Otronic ST7789](https://www.otronic.nl/en/1-3-inch-spi-tft-lcd-display-rgb-st7789-3-3v)
- **Verified:** A modest 4-inch HDMI monitor source supports 800×480 IPS and direct computer-monitor operation over HDMI (touch unavailable in monitor use). This pixel grid and square-rectangular area are much better suited to readable text than the 240×240 circle; exact contemporary price, weight, thickness, power needs and Finland landed cost were not established in this audit. [Waveshare 4-inch HDMI manual](https://files.waveshare.com/upload/4/46/4inch_HDMI_LCD_User_Manual_EN.pdf)
- **Verified:** The target MacBook Pro is 14.2-inch, 3024×1964, 254 ppi; body 312.6×221.2 mm, 15.5 mm thick, 1.55 kg. [Apple 2024 14-inch M4 specs](https://support.apple.com/en-gb/121552)

### Inferences
- 1.32-inch AMOLED offers ~3.8× as many pixels as 240×240 and 500-nit stated brightness (versus no brightness figure for OT8724), while preserving the attractive round character form. This is a defensible display-first choice, but it is a different firmware/code path from this repository.
- For glanceable short labels, icons, timers and face animations, the round AMOLED is a better compromise than the 1.64 rectangular panel. For actual lyrics, notification snippets, token counts and persistent status text, a small HDMI panel is easier to read and directly mirrors/renders macOS content; the small ESP32 panels need a custom host bridge and UI anyway.
- The Taby round product is lower integration friction than assembling ESP32 + separate screen, but the round-case absence means some enclosure work remains. Taby's board runs Taby firmware, not this project's current firmware.
- No product spec proves sunlight/room-glare legibility at the chosen viewing angle; vendor brightness is not a physical readability test.

### Gaps
- Live prices for Taby/Waveshare options on 2026-10-27, exact checkout VAT/shipping, stock, return cost to Finland, and product weight/thickness for integrated boards.
- A specific HDMI screen's current local availability, total landed price, exact enclosure dimensions/weight, USB power draw and cable requirements; only the display-class tradeoff is established.
- Actual viewing comfort for this user's desk distance, font size, eyesight and ambient light.

## Are the selected BOM, prices and electrical/mechanical claims reliable?

### Takeaway
The repo’s listed component prices and arithmetic match current Otronic page evidence for the core parts, and the Finland tracked-shipping amount still appears on its live table. The €40.03 figure is a current list-price estimate rather than a verified cart; the crucial no-solder assumption for OT8724 is not verified. Parts will require exposed wiring and a breadboard, so the proposed assembly is not yet a finished desk-safe enclosure.

### Cited Findings
- **Verified:** Otronic currently lists OT8724 €8.99 and an ESP32-S3 N16R8 board €9.95. [OT8724 seller page](https://www.otronic.nl/en/128-rond-tft-lcd-240240-gc9a01-spi-voor-arduino.html); [N16R8 listing](https://www.otronic.nl/en/microcontrollers/esp32/)
- **Verified:** Otronic shipping table lists Finland among “other countries” for tracked parcel at €8.00. [Otronic shipping](https://www.otronic.nl/nl/verzending)
- **Verified:** Those lines plus BOM-listed MPU-6050 €3.75, breadboard €2.99, F-F wires €1.85, M-F wires €1.85 and USB-C data cable €2.65 add to €40.03; without cable they add to €37.38. The live Otronic listing corroborates N16R8 and LCD prices, but the other item pages/prices were not individually rechecked here. [Repository BOM](../../docs/bom.md)
- **Verified:** Waveshare's cabled GC9A01 listing documents a 3.3V/5V supply input and BL pin; its cable is useful if OT8724 headers are bare, but does not remove the need to connect the cable's other end to an MCU. [Waveshare module/pinout](https://www.waveshare.com/product/1.28inch-lcd-module.htm); [wiki](https://www.waveshare.com/wiki/1.28inch_LCD_Module)
- **Unverified:** Otronic OT8724 pre-soldered headers, exact BLK electrical behavior/current, board photo/revision, and whether the stated 5 mm board depth includes pins or components. Seller page only says 8 pins/2.54 mm pitch and dimensions. [Otronic OT8724](https://www.otronic.nl/en/128-rond-tft-lcd-240240-gc9a01-spi-voor-arduino.html)
- **False / contradictory:** Repo says GC9A01 has “4-Pin SPI,” which can be misread as four physical module pins. Otronic specifies **8 module pins** and 4-wire SPI (clock/data/control protocol); Waveshare’s 8-pin pinout separately shows power, ground, DIN, CLK, CS, DS, RST and BL. Clarify wording as four-wire SPI bus / eight-pin module. [Otronic OT8724](https://www.otronic.nl/en/128-rond-tft-lcd-240240-gc9a01-spi-voor-arduino.html); [Waveshare pinout](https://www.waveshare.com/wiki/1.28inch_LCD_Module)
- **Unverified:** `hardware/options.json` calls the Waveshare 1.43 case option an “optional CNC case” and gives a $26.99–31.99 range, but this audit did not verify current listing price/configuration or identify whether a displayed case is included in that price. Treat both as unverified until SKU selection on manufacturer checkout. [Waveshare 1.43 listing](https://www.waveshare.com/product/esp32-s3-touch-amoled-1.43.htm)
- **Unverified purchase alternatives in the existing comparison:** Waveshare 1.32 ($21.99), 1.64 ($23.99), and 1.43 ($26.99–31.99) list prices; StackChan K151 ($99); Rocky creator estimate (~$100 parts) and any peripherals/print bundle. Existing source links are [Waveshare 1.32](https://www.waveshare.com/esp32-s3-touch-amoled-1.32.htm), [Waveshare 1.64](https://www.waveshare.com/ESP32-S3-Touch-AMOLED-1.64.htm), [Waveshare 1.43](https://www.waveshare.com/product/esp32-s3-touch-amoled-1.43.htm), [M5Stack K151](https://shop.m5stack.com/products/stackchan-kawaii-co-created-open-source-ai-desktop-robot), and [Rocky creator BOM](https://github.com/cgro00/desk-robot); no current total or exact variant/cart was verified. The comparison’s core description of K151 as a prebuilt robot and Rocky as a soldering/servo build is not re-audited here and should not be used to make this first purchase decision.
- **Unverified accessory lines:** MPU-6050 €3.75, breadboards €2.99, jumper wire packs €1.85 each, USB-C data cable €2.65, and their stock/accessory/header state were not individually checked against current listing pages in this bounded audit; their figures are arithmetic inputs from the repo BOM, not freshly verified prices. [Otronic MPU listing](https://www.otronic.nl/en/acceleration-accelerometer-and-gyroscope-i2c-mpu.html); [breadboard](https://www.otronic.nl/en/breadboard-830-hole-for-prototyping.html); [F-F wires](https://www.otronic.nl/en/dupont-jumper-cables-40-pieces-female-female-20cm.html); [M-F wires](https://www.otronic.nl/en/dupont-jumper-cables-40-pieces-male-female-20cm-dr.html); [USB-C data cable](https://www.otronic.nl/en/usb-c-to-usb-c-1m-cable-for-data-and-fast-charging.html)
- **Verified:** Waveshare lists GC9A01 panel area 32.4 mm diameter but module PCB 40.4×37.5 mm; the repository’s 44×36×5 mm dimensions apply to the Otronic module and are not transferable to the Waveshare module. [Otronic dimensions](https://www.otronic.nl/en/128-rond-tft-lcd-240240-gc9a01-spi-voor-arduino.html); [Waveshare dimensions](https://www.waveshare.com/product/1.28inch-lcd-module.htm)

### Inferences
- Keep the €40.03 number only with a clear “estimated advertised basket, not cart quote” label, and the stated optional cable distinction. Do not present it as Finland checkout total without a fresh cart.
- Before any no-solder shopping recommendation, obtain vendor confirmation or substitute a documented cable-equipped module. Even if header pins are included in the box, that is not proof they are fitted.
- The firmware pin mapping could be electrically reasonable for an SPI display, but pin labels alone do not settle the backlight circuit; do not wire BLK by assumption. Verify exact module schematic/vendor answer or use a documented breakout.

### Gaps
- Direct current evidence for every non-display BOM item, exact shipping/cart combination, inventory/dispatch date, and confirmation of the final VAT-inclusive checkout.
- Whether MPU-6050 module pullups are tied to 3.3 V, its header status, and actual board dimensions; repo appropriately flags this for inspection.
- OT8724 schematic, component-side photograph, supplied accessories, header population and BLK drive circuit.

## What mounting approach avoids damaging the laptop or blocking its lid?

### Takeaway
Mount it on its own weighted/weighted-footprint desk stand beside the laptop display, with a flexible USB lead and strain relief. Do not attach it to the display glass/bezel, place its body or cable in the hinge/lid sweep, or trap any component between keyboard and display; close the laptop only after moving the accessory clear. The repository CAD is explicitly a prototype and has not established a stable or protective mount.

### Cited Findings
- **Verified:** Repo CAD describes an open-back enclosure, 72 mm shell width and 31.4 mm aperture; CAD/mesh checks confirm geometry only, and the print instructions explicitly say fit is not verified and recommend measuring board, glass, headers and cable bend radius first. [Printing notes](../../docs/printing.md); [display decision](../../docs/display-choice.md)
- **Verified:** OT8724 seller gives 44×36×5 mm board and 32.4 mm active circle; this is a small screen mounted in a much wider shell. [Otronic OT8724](https://www.otronic.nl/en/128-rond-tft-lcd-240240-gc9a01-spi-voor-arduino.html)
- **Verified:** Apple's MacBook is 15.5 mm thick and weighs 1.55 kg. [Apple specs](https://support.apple.com/en-gb/121552)
- **Verified:** Taby's available 1.64 case is desktop-oriented and uses magnet plus non-slip rubber; no official round case exists yet. [Taby case notes](https://github.com/TRIIIS-LABS/firmware-taby)

### Inferences
- A stand whose load rests on the desk avoids concentrated load on the laptop display glass/bezel and lets its footing resist USB cable tug. A small clip-on arm hung from a display edge concentrates load and can interfere with lid travel; no such mount should be assumed safe from vendor screen specs.
- Use rounded/covered edges and a smooth, broad desk-contact foot. Keep stand, protruding pins and cable clear of the hinge line and the full lid swing. The MacBook's 15.5 mm closed thickness is a practical reminder that a 5 mm PCB, headers and wires must never be left over the keyboard/deck when closing.
- Avoid an adhesive or magnetic attachment on the Mac itself; leave no accessory attached to screen/lid during closure. The Taby magnet case is for its own desk base, not evidence that a laptop mount is safe.
- Breadboard and loose jumpers belong in a bench prototype; final desk use needs an enclosure that retains the board and insulates contacts, plus cable strain relief. There is not yet validated CAD for that use.

### Gaps
- No static/tipping test, weight/center-of-gravity measure, cable-force test, desk vibration test, hinge-clearance study, or physical print fit exists.
- Exact Waveshare/Taby board thickness, weight, connector projection and cable bend radii were not extracted from dimension drawings; check their technical drawings and physical units before designing a compact case.
- No recognized laptop-mount safety specification or Apple endorsement for a third-party screen-edge attachment was found. This audit makes a conservative engineering recommendation based on the stated no-glass-pressure/no-trapped-object constraint.
