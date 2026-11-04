# Separate reusable microcontroller and display — checked 2026-11-04

## Which coherent starter BOM fits the budget?

### Takeaway
The strongest separate-parts option found is **Raspberry Pi Pico WH + Waveshare Pico-LCD-1.8**, because both arrive with their mating headers already installed. Its published-price sum is €27.40 delivered before a €2 home-printed holder; allow **€31–33 total** because the Finnish destination VAT amount was not verified in checkout. This is a near-€30 learning option, not a verified €30 delivered offer.

### Cited Findings
- BOM: **Pico WH, RPI-PICO-WH, €7.20**, over 100 available; choose WH specifically, not the unheaded W. The retailer specifies RP2040 + WLAN and fitted headers. — [Board](https://www.berrybase.de/raspberry-pi-pico-wh-rp2040-wlan-mikrocontroller-board-mit-headern)
- **Waveshare Pico-LCD-1.8, WS-19579, €8.80**, 7 available, ST7735S 160×128 TFT, active area 35.04×28.03mm, board 52×34.5mm; retailer lists Pico C/C++ and MicroPython examples. — [Display](https://www.berrybase.de/1-8-zoll-lcd-anzeigemodul-fuer-raspberry-pi-pico-65k-farben-160x128-spi)
- **USB-C male to Micro-B data cable, S-Impuls 77145-10, 1m, €1.50**, 24 available; described for connecting devices to PC/Mac, not merely charging. This avoids a separate USB-A adapter for a USB-C MacBook. — [Cable](https://www.berrybase.de/usb-2.0-adapterkabel-usb-c-stecker-micro-b-stecker-schwarz)
- BerryBase publishes **€9.90 DHL shipping to EU countries** below €200. Germany's 1–3-day product labels should not be interpreted as Finland delivery guarantees. Prices are marked VAT-inclusive, but the pages do not establish the final Finnish destination rate. — [Shipping](https://www.berrybase.de/versand-und-zahlungsbedingungen)
- Display has onboard female headers for direct attachment to Pico, so no breadboard, Dupont wires, soldering iron, solder or external programmer is necessary for this starter build. — [Manufacturer](https://www.waveshare.com/Pico-LCD-1.8.htm)

### Inferences
- Published arithmetic: €7.20 + €8.80 + €1.50 + €9.90 = **€27.40**; adding the coordinator's **€2 estimated print material** gives €29.40. If every published amount were adjusted from 19% to 25.5% VAT, the result including print would be €30.90. This is a planning calculation, not a tax-verified quote.
- Print a simple desk cradle around the assembled 52×34.5mm display board with cable clearance; measure stack height first. No battery, contacts or slim case yet.
- An optional €1.60 400-contact breadboard and €4.90 mixed jumper set are listed alongside the Pico; they are unnecessary for the companion and can wait until sensor experiments. Adding them now pushes the provisional total to roughly €36–38. — [Accessories shown on board page](https://www.berrybase.de/raspberry-pi-pico-wh-rp2040-wlan-mikrocontroller-board-mit-headern)

### Gaps
- No checkout, account, address or purchase was used. Therefore **no BOM here has a verified Finnish delivered total**. Header fit and display firmware have not been tested on physical hardware.

## What does the beginner learn, and what remains to verify?

### Takeaway
The plug-on Pico display minimizes initial wiring while retaining a detachable, reusable controller. It teaches firmware, USB communication, graphics and Wi-Fi first; a free-form ESP32 + SPI display teaches wiring sooner but introduces more opportunities for wrong connections.

### Cited Findings
- Raspberry Pi documents installing MicroPython by holding BOOTSEL, connecting USB, and copying a UF2 firmware file; Thonny offers native installers for both Intel and Apple Silicon Macs. — [Pico MicroPython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html), [Thonny](https://thonny.org/)
- Waveshare provides Pico/Pico2 orientation guidance, pin definitions and downloadable example resources on its wiki. Match the USB-end silkscreen before plugging the stack together. — [Manufacturer wiki](https://www.waveshare.com/wiki/Pico-LCD-1.8)
- Exact fixed connections: VCC→VSYS, GND→GND, DIN→GP11, CLK→GP10, CS→GP9, DC→GP8, RST→GP12, BL→GP13. Supply range 2.6–5.5V; the direct plug-on assembly handles power and Pico logic without a separate level shifter. — [Manufacturer pin table](https://www.waveshare.com/wiki/Pico-LCD-1.8)
- A generic modular alternative was investigated: **BerryBase NodeMCU ESP32 €6.80 + Waveshare 1.3-inch SPI IPS ST7789 €7.90**. Direct product pages currently say unavailable despite cached category/search results claiming stock. Do not present this as an immediately orderable BOM. The display is 240×240, board 31×45mm, with PH2.0 eight-wire lead included. — [ESP32](https://www.berrybase.de/esp32-nodemcu-development-board), [1.3-inch display](https://www.berrybase.de/1.3-240x240-ips-hd-lcd-display-modul-spi-interface)
- That ESP32 has CP2102 USB serial, Micro-B, 3.3V logic, GPIO/ADC/PWM/SPI/I2C/UART, but no additional PSRAM; an unsoldered variant is explicitly offered. Recheck exact header variant rather than assuming the photo means ready to connect. — [Board specifications](https://www.berrybase.de/esp32-nodemcu-development-board)

### Inferences
- Start with the vendor display demo, then animate simple eyes by redrawing shapes. A polished companion still needs its own animation/state code and Mac-to-device protocol; **no exact ready-to-flash animated-companion firmware was verified** for this Pico display.
- Unplugging the LCD frees the Pico for later breadboard sensors and actuators. The plug-on arrangement physically covers GPIO, so simultaneous experimentation may require an expansion board or wiring later.
- For an ESP32 wiring build, expect power/ground plus clock, data, select, command/data, reset and backlight connections. Use 3.3V logic; a display accepting 5V supply does not establish 5V-safe GPIO.

### Gaps
- Waveshare full pages returned 403 during direct fetch; targeted search retrieved the manufacturer pin table and demo instructions. The full schematic was not inspected. No animation speed benchmark, Mac serial trial, or print-fit validation was performed. Use current Pico W firmware from Raspberry Pi, rather than blindly copying the wiki's old non-W firmware filename.
