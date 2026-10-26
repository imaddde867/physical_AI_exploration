# Display decision: round color IPS

The design target is a distinctive, small, high-quality-looking companion for a MacBook, rather than a monochrome diagnostic module.

![Original concept art, not a photo](../assets/face-preview.svg)

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

## Aesthetic implementation

- Black background, oversized cyan/lilac eyes and dark pupils with highlights.
- Pastel expression details, no calculator-style white text at the bottom.
- Six faces and a periodic blink; MPU-6050 shake triggers a surprised face.
- Rounded 3D-printed shell with circular bezel concealing the display PCB.
- SVG above is **illustrative original design**, not measured pixel output or a photo.

## Technical changes

The screen moves from I²C to **SPI** using GPIO11 MOSI, GPIO12 CLK, GPIO10 CS, GPIO13 DC, GPIO14 RES. The motion sensor retains its **separate I²C bus on GPIO8/9**. The LCD is write-only, so a firmware initialization event cannot confirm successful illumination: ready packets deliberately say **init_sent_unverified**, requiring visual confirmation during hardware tests.

The new CAD fits a nominal **31.4 mm round visible aperture** inside an open-backed rounded shell. It is a fit-testable parametric prototype—not a validated mount. Measure the physical PCB, its glass position, headers and cable bend radius before finalizing.

## Remaining uncertainty

Confirm Otronic OT8724 has fitted headers and whether its backlight pin may float or needs 3.3 V. The prototype needs real-screen photographs, color/pin orientation tests and Bambu Studio slice checks before it can be described as finished.
