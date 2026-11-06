# Display frame-rate decision — 2026-11-06

12 FPS was a preview choice, not a measured hardware ceiling. **30 FPS is the
new offline preview target**, with 24/25 FPS alternatives. The actual device rate
is undecided until the board is measured. Keep the approved 12 FPS exports as
comparison material.

## What the sources establish

The ordered board uses a 240 × 280 ST7789V2 SPI display. The inspected vendor
Python driver requests 100 MHz SPI and writes register C6h with 13h. Sitronix's
normal-mode table labels 13h approximately 53 Hz; the table assumes porch values
0Ch/0Ch while the example uses 0Bh/0Bh. Treat this as a nominal scan setting, not
an exact measured refresh or guaranteed animation FPS. Changing the scan setting
is not part of this change.

Primary references:

- [Waveshare board wiki](https://www.waveshare.net/wiki/RP2040-Touch-LCD-1.69)
- [Vendor demo archive](https://www.waveshare.net/w/upload/0/0c/RP2040-Touch-LCD-1.69-Code.zip), checksum and setup in the firmware README.
- [ST7789V2 datasheet](https://files.waveshare.com/wiki/common/ST7789V2.pdf): p44, four-wire serial timing; p134–137, TE synchronization; p287, FRCTRL2.
- [Board product specification](https://www.waveshare.com/product/raspberry-pi/boards-kits/raspberry-pi-pico-cat/rp2040-touch-lcd-1.69.htm): advertised 16 MB flash; confirm accessible filesystem space after installing firmware.
- [MicroPython SPI documentation](https://docs.micropython.org/en/latest/library/machine.SPI.html): actual baudrate can be lower than requested; print the SPI object.

The datasheet's minimum write-clock period is 16 ns (62.5 Mbit/s). That gives a
**transfer-only theoretical ceiling of 58.13 full RGB565 frames/s**, before
commands, flash reads, decoding or software overhead. It is not a measured board
rate. 60 full RGB565 frames/s would require 64.512 Mbit/s of pixel payload alone.
The controller's register table is not proof that the complete module supports
its highest listed scan setting.

## Full-frame cost

A frame is exactly 240 × 280 × 2 = **134,400 bytes** in RGB565.

| Animation rate | Pixel payload / second | Pixel bus bandwidth | Frame budget |
| --- | --- | --- | --- |
| 12 FPS | 1.6128 MB | 12.9024 Mbit/s | 83.33 ms |
| 24 FPS | 3.2256 MB | 25.8048 Mbit/s | 41.67 ms |
| 25 FPS | 3.3600 MB | 26.8800 Mbit/s | 40.00 ms |
| 30 FPS | 4.0320 MB | 32.2560 Mbit/s | 33.33 ms |
| 60 FPS | 8.0640 MB | 64.5120 Mbit/s | 16.67 ms |

These are decimal MB and exclude overhead. An eight-second 30 FPS clip is
32.256 MB uncompressed, exceeding the advertised 16 MB flash before firmware.
Compression, changed-region updates, or compressed streaming will be needed for
the library. Raw 30 FPS also exceeds full-speed USB bandwidth, so a Mac connection
does not remove the need for compression.
Two complete framebuffers consume 268,800 bytes, leaving only 1,536 bytes of the
RP2040's 264 KiB SRAM; full double buffering is not practical with MicroPython.

Matching a nominal FPS number does not synchronize scanning. The existing driver
does not use TE feedback. Tear-free playback requires checking TE wiring and
scheduling, not just asking an encoder for 30 or 60 FPS. If a stable 60 Hz scan is
validated, 30 FPS gives simple 2:1 cadence; a validated 50 Hz / 25 FPS pairing is
another option. Neither setting is adopted before a board test.

## On-arrival measurement

Run the factory/vendor demo first. Stop the blink, copy `benchmark_display.py`
alongside `main.py` and `waveshare_lcd.py`, and run it from Thonny. It keeps a dark
static image and prints SPI configuration, mean/p95/worst full-transfer time,
transfer-only FPS and heap. No display refresh registers are changed.

Then measure the real pipeline (flash read + decode + transfer + other work).
Choose a fixed cadence whose p95 frame cost leaves about 20% headroom. Record
missed deadlines, tearing, corruption, heap and long-run stability. A fast SPI-only
result is not a promise of equally fast animated playback.

Offline exports now evaluate actual Blender subframes at the requested output
rate, keeping the eight-second state duration unchanged and excluding its repeated endpoint.
There is no AI frame interpolation. The monitor previews are not a hardware test.

Use MP4 for cadence comparisons. GIF timing uses centiseconds and cannot represent
every 30 FPS frame duration exactly; it also reduces colors. The desktop FPS
comparison uses a shared 60 FPS container, preserving the 12/24/30 source cadences.
