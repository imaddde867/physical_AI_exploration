# Display decision: round color IPS

The design target is a distinctive, small, high-quality-looking companion for a MacBook, rather than a monochrome diagnostic module.

![The single approved 240×240 face, source used in firmware](../assets/face-idle-240.png)

**Approved character direction:** one mature, restrained, heavy-lidded character on a near-black canvas. No ribbons, cheeks, anime eyes, pastel emoji decorations or multiple character concepts. The previous decorative illustrations have been superseded. This image is exactly what the sprite pipeline reads—not a photo of a tested LCD.

[**Actual front dimensions: Ø31.4 mm face window in 72 mm body**](../assets/actual-scale-front.svg) — about **43.6%** of the shell's width. The visual concept exaggerates the relative screen size. For premium-looking alternatives with different layouts and processors, see [the creator-versus-online hardware matrix](hardware-options.md).

## Decision and comparison (2026-10-26)

| Feature | Previous OLED (retired) | Selected IPS | Alternative IPS |
|---|---|---|---|
| Model | 0.96 inch unspecified SSD1306 | **1.28 inch Otronic OT8724 GC9A01** | 1.3 inch ST7789 |
| Seller list price | €5.99 | **€8.99** | €6.25 |
| Face shape | Rectangular monochrome | **Circular, color** | Square, color |
| Pixels | 128×64, 1-bit | **240×240, RGB565** | 240×240, RGB565 |
| Interface | I²C | **SPI, 3.3 V** | SPI, 3.3 V |
| Code library | Adafruit SSD1306 | **Adafruit GC9A01A 1.2.0** | Separate ST7789 implementation |

The selected LCD has **32.4 mm circular active area**, manufacturer-stated module PCB dimensions 44 × 36 × 5 mm, and costs €8.99 at [Otronic](https://www.otronic.nl/en/1-28-round-tft-lcd-240-240-gc9a01-spi-for-arduino). This improves display design for only **€3.00** above the earlier mono OLED.

[Adafruit's open-source Arduino GC9A01A driver](https://github.com/adafruit/Adafruit_GC9A01A) supports drawing geometric shapes, RGB colors and SPI display updates; the driver is a separately licensed dependency and not copied here. [GC9A01 breakout electrical reference](https://www.lcdwiki.com/index.php?title=1.28inch_IPS_Module) describes common BLK and SPI pins; **the Otronic module itself has not been inspected**, so these are not assumed to guarantee its backlight wiring.

## Screen asset and implementation

- The approved [screen-only PNG](../assets/face-idle-240.png) is **240×240**, indexed to **32 colors** for predictable small-screen appearance.
- The standard-library-only [asset compiler](../tools/face_asset.py) generates a flash-resident RGB565 palette and roughly **10.5 KB** of run-length tokens before every PlatformIO build. The generated header is not checked into git.
- The embedded driver streams pixels row by row to the GC9A01, using just a **480-byte scanline buffer** and no full-frame heap allocation.
- One face identity is shared by all **six retained JSON protocol commands**. Commands only adjust small mouth/lid cues; occasional blinks do not introduce new characters.
- No LLM, image-generation inference, runtime PNG parsing or workstation is required for the display.
- The visual on the real IPS LCD remains unverified until physical hardware is wired and photographed.

## Technical changes

The screen moves from I²C to **SPI** using GPIO11 MOSI, GPIO12 CLK, GPIO10 CS, GPIO13 DC, GPIO14 RES. The motion sensor retains its **separate I²C bus on GPIO8/9**. The LCD is write-only, so a firmware initialization event cannot confirm successful illumination: ready packets deliberately say **init_sent_unverified**, requiring visual confirmation during hardware tests.

The new CAD fits a nominal **31.4 mm round visible aperture** inside an open-backed rounded shell. It is a fit-testable parametric prototype—not a validated mount. Measure the physical PCB, its glass position, headers and cable bend radius before finalizing.

## Remaining uncertainty

Confirm Otronic OT8724 has fitted headers and whether its backlight pin may float or needs 3.3 V. The prototype needs real-screen photographs, color/pin orientation tests and Bambu Studio slice checks before it can be described as finished.
