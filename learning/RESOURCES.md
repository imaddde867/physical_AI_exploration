# Waveshare RP2040-Touch-LCD-1.69 Resources

## Knowledge

- [Waveshare wiki (Chinese mirror)](https://www.waveshare.net/wiki/RP2040-Touch-LCD-1.69)
  Chip list, specs, pinout image, C/MicroPython/Arduino/LVGL demos. English wiki may return 403. Use for: board facts, demo setup.
- [Waveshare product page](https://www.waveshare.com/rp2040-touch-lcd-1.69.htm)
  Official listing. Use for: confirming specs.
- [RP2040 datasheet, Raspberry Pi](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
  Primary source for the chip: memory, SPI, I2C, PIO. Use for: any claim about RP2040 limits.
- [MicroPython docs, RP2 quick reference](https://docs.micropython.org/en/latest/rp2/quickref.html)
  Pins, SPI, I2C, timers in MicroPython. Use for: writing and reading firmware.
- Local: `firmware/rp2040/README.md`, `docs/hardware/bringup-log.md`
  Our own board notes and bring-up plan.

## Wisdom (Communities)

- [Raspberry Pi forums, RP2040 / MicroPython](https://forums.raspberrypi.com/)
  Moderated, staffed by Pi engineers. Use for: stuck bring-up questions.
- [MicroPython forum](https://github.com/orgs/micropython/discussions)
  Use for: runtime and driver questions.

## Gaps
- Flash size: Waveshare's product specification lists 16 MB; the wiki page's 4 MB figure is older. `os.statvfs('/')` reports the filesystem, not the chip, so verify the installed chip separately if needed.
- Pinout image is not machine-readable; transcribe from the board silkscreen/vendor code.

## Added (primary sources read in full or in part)
- [ST7789V2 datasheet (Sitronix, via Waveshare)](https://files.waveshare.com/wiki/common/ST7789V2.pdf)
  Read: features, 4-line serial protocol, CASET, COLMOD, MADCTL, SLPOUT. Use for: any display command or timing.
- [RP2040 datasheet: SPI section and memory](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
  Read: SPI bit-rate formula, SRAM, XIP flash. Not yet read: I2C, PIO, USB.
- [MicroPython machine.SPI](https://docs.micropython.org/en/latest/library/machine.SPI.html), [RP2 quick reference](https://docs.micropython.org/en/latest/rp2/quickref.html), [Reset and boot](https://docs.micropython.org/en/latest/reference/reset_boot.html)
  Use for: API behaviour, machine.freq, boot order.
## Not read yet
- Touch controller (CST816) and QMI8658 datasheets; Waveshare wiki battery and IMU sections.

## Images
- Board photo with pins: `https://www.waveshare.net/w/upload/6/63/RP2040-Touch-LCD-1.69-details-9.jpg`; size drawing: `.../3/38/RP2040-Touch-LCD-1.69-details-size.jpg`. Copyright Waveshare, all rights reserved (wiki footer), so hotlinked in lesson 1, not stored in the repo. Use for: locating parts. Open: IMU and touch chip positions.
