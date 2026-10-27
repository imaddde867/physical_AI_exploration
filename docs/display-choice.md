# Display choice: rectangular AMOLED candidate, round IPS prototype

**Current direction (2026-10-27): a subtle rounded-rectangle face, powered and connected by one discreet USB cable.** Leading candidate: Waveshare ESP32-S3-Touch-AMOLED-1.64 SKU 31197, listed as V2, subject to delivered PCB revision mapping to the drawing and schematic and USB data verification. The schematic source is Rev1.1 and its GPIO19/20 routing is not yet confirmed for retail V2. Taby 1.64 V1 support is a separate option and does not imply V2 support. See the [engineering study](../reports/Rectangular%20buddy%20engineering%20study.md) and [build plan](rectangular-build-plan.md).

The existing **GC9A01 IPS** remains the implemented electronics-learning prototype. Its firmware, artwork pipeline and CAD are retained; they do not run unchanged on the AMOLED board. A provisional 33.12 × 48 × 13 mm rectangular concept is a packaging study, not a verified fit.

![The single approved 240×240 face, source used in firmware](../assets/face-idle-240.png)

**Approved character direction:** one mature, restrained, heavy-lidded character on a near-black canvas. No ribbons, cheeks, anime eyes, pastel emoji decorations or multiple character concepts. The previous decorative illustrations have been superseded. This image is exactly what the sprite pipeline reads—not a photo of a tested LCD.

[**Actual front dimensions: Ø31.4 mm face window in 72 mm body**](../assets/actual-scale-front.svg) — about **43.6%** of the shell's width. The on-screen PNG is a native-resolution source image; its appearance on a large monitor does **not** represent its actual 31.4 mm physical opening. For premium-looking alternatives with different layouts and processors, see [the creator-versus-online hardware matrix](hardware-options.md).

## Implemented prototype comparison (prices recorded 2026-10-26)

| Feature | Previous OLED (retired) | Implemented IPS | Alternative IPS |
|---|---|---|---|
| Model | 0.96 inch unspecified SSD1306 | **1.28 inch Otronic OT8724 GC9A01** | 1.3 inch ST7789 |
| Seller list price | €5.99 | **€8.99** | €6.25 |
| Face shape | Rectangular monochrome | **Circular, color** | Square, color |
| Pixels | 128×64, 1-bit | **240×240, RGB565** | 240×240, RGB565 |
| Interface | I²C | **SPI, 3.3 V** | SPI, 3.3 V |
| Code library | Adafruit SSD1306 | **Adafruit GC9A01A 1.2.0** | Separate ST7789 implementation |

The prototype LCD has **32.4 mm circular active area**, manufacturer-stated module PCB dimensions 44 × 36 × 5 mm, and a recorded €8.99 list price at [Otronic](https://www.otronic.nl/en/1-28-round-tft-lcd-240-240-gc9a01-spi-for-arduino). The [reference BOM](bom.md) is a dated estimate, not the current purchase recommendation or a checkout quote.

[Adafruit's open-source Arduino GC9A01A driver](https://github.com/adafruit/Adafruit_GC9A01A) supports drawing geometric shapes, RGB colors and SPI display updates; the driver is a separately licensed dependency and not copied here. [GC9A01 breakout electrical reference](https://www.lcdwiki.com/index.php?title=1.28inch_IPS_Module) describes common BLK and SPI pins; **the Otronic module itself has not been inspected**, so these are not assumed to guarantee its backlight wiring.

## Screen asset and implementation

- The approved [screen-only PNG](../assets/face-idle-240.png) is **240×240**, indexed to **32 colors** for predictable small-screen appearance.
- The standard-library-only [asset compiler](../tools/face_asset.py) generates a flash-resident RGB565 palette and roughly **10.5 KB** of run-length tokens before every PlatformIO build. The generated header is not checked into git.
- The embedded driver streams pixels row by row to the GC9A01, using just a **480-byte scanline buffer** and no full-frame heap allocation.
- One face identity is shared by all **six retained JSON protocol commands**. Commands only adjust small mouth/lid cues; occasional blinks do not introduce new characters.
- No LLM, image-generation inference, runtime PNG parsing or workstation is required for the display.
- The visual on the real IPS LCD remains unverified until physical hardware is wired and photographed.

## Implemented prototype wiring

The prototype uses **SPI** using GPIO11 MOSI, GPIO12 CLK, GPIO10 CS, GPIO13 DC, GPIO14 RES. The motion sensor retains its **separate I²C bus on GPIO8/9**. The LCD is write-only, so a firmware initialization event cannot confirm successful illumination: ready packets deliberately say **init_sent_unverified**, requiring visual confirmation during hardware tests.

The prototype CAD fits a nominal **31.4 mm round visible aperture** inside an open-backed rounded shell. It is a fit-testable parametric prototype—not a validated mount. Measure the physical PCB, its glass position, headers and cable bend radius before finalizing.

## Remaining uncertainty

Confirm Otronic OT8724 has fitted headers and whether its backlight pin may float or needs 3.3 V. The prototype needs real-screen photographs, color/pin orientation tests and Bambu Studio slice checks before it can be described as finished.
