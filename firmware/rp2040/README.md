# RP2040 local blink prototype

For **Waveshare RP2040-Touch-LCD-1.69 (SKU 28161)** only. Prepared before
delivery; first loaded on the board on 2026-11-12 with MicroPython 1.22.2. USB power from the Mac is enough
for this prototype. Run the vendor demo first, then this blink.

`main.py` draws the placeholder eyes in soft white on black, with a one-pixel
antialiased circle edge and 12.5% backlight duty to reduce the black-level glow:
one 140 ms blink every four seconds. It uses the vendor driver's single packed
RGB565 framebuffer (134,400 bytes), prints the remaining MicroPython heap after
initialization, and redraws only when blink state changes. Ctrl-C stops the loop
and turns off the backlight. No touch or battery is needed, and the USB serial
command channel is optional: without a host it blinks on its own.

## Status, 2026-11-12

- Done on the board: MicroPython 1.22.2 installed; vendor driver and this blink loaded.
- Free heap after initialization: 86,400 bytes (printed by `main.py`).
- Power: the board and screen ran from Mac USB-C, iPhone USB-C, and a USB wall charger. No battery or power bank was tested.
- Display: portrait orientation, eye alignment, smooth edges and clipping visually checked and passed. Soft-white eyes visually confirmed (colour accuracy not measured). No flicker or tearing observed; 12.5% backlight duty dims the glow as designed.
- Stability: about 1-2 hours of operation without observed problems, with successful reconnects. Individual run durations and internal resets were not instrumented.
- Mac sleep: the device kept blinking while the MacBook slept; wake-transition behaviour was not separately measured.
- Not measured: real SPI rate, delivered frame rate, brightness.
- Not yet exercised: vendor demo baseline, on-device transfer benchmark.

## Prepare the vendor driver on the Mac

Use the [board wiki](https://www.waveshare.net/wiki/RP2040-Touch-LCD-1.69)
and its [example archive](https://www.waveshare.net/w/upload/0/0c/RP2040-Touch-LCD-1.69-Code.zip).
The English wiki may return HTTP 403; the linked Chinese wiki has the same board's resources.
The driver is kept as an ignored local dependency rather than copied into the
repository's MIT-licensed source. From the repository root:

```sh
python3 - <<'PY'
import hashlib
import io
from pathlib import Path
import urllib.request
import zipfile

url = 'https://www.waveshare.net/w/upload/0/0c/RP2040-Touch-LCD-1.69-Code.zip'
data = urllib.request.urlopen(url, timeout=30).read()
expected = 'daccb95c93170ecce939d75af60a5fdc43c038b5f7bf06de7666dff91b113953'
if hashlib.sha256(data).hexdigest() != expected:
    raise SystemExit('Vendor archive changed; inspect it before updating the checksum.')
with zipfile.ZipFile(io.BytesIO(data)) as archive:
    driver = archive.read('RP2040-Touch-LCD-1.69-Code/Python/RP2040_Touch_LCD_1.69.py')
Path('firmware/rp2040/waveshare_lcd.py').write_bytes(driver)
PY
```

Archive inspected 2026-11-04. Its driver defines `LCD_1inch69`, SPI1 (100 MHz
requested), DC=8, CS=9, SCK=10, MOSI=11, RST=13, BL=25. It allocates one
framebuffer. Its touch/demo loop is guarded by `if __name__ == '__main__'`, so
importing it does not run that demo.

The vendor `setWindows()` calculates the row end from `Ystart`, ignoring `Yend`.
Our subclass corrects that method, including the 20-row panel offset and splitting
coordinates into high/low bytes. The vendor initialization sequence is unchanged.
Gray shades are packed as RGB565 and byte-swapped for the driver's direct buffer
transfer. Vendor color constants still need a separate physical color test.
Requested SPI speed is inherited from the
vendor example, not a measured stable rate on this board.

## Bring-up steps

1. Connect the existing USB-C data cable. Check the factory demo if present.
2. Follow the board wiki's MicroPython setup. The example archive above already contains
   `Python/RPI_PICO-20240222-v1.22.2.uf2` (MicroPython 1.22.2, sha256
   `e92c2a253d2d4830d56cd6aebae1bbc6c913f413122dabba3cc2de74b984bba9`): hold BOOT while plugging in, then copy it to the `RPI-RP2` drive.
   Run the original vendor example from Thonny to establish a working baseline.
3. In Thonny, copy `waveshare_lcd.py`, `daemon/protocol.py` (as `protocol.py`) and our
   `main.py` to the board's root. All three files must be on the board. Saving as
   `main.py` makes the blink start on boot. The board has no `daemon` package, so
   `protocol.py` sits beside `main.py` and the shared codec is not duplicated in git.
4. Run `main.py`. Expect two centered eyes and a short blink every four seconds.
   Record the reported free heap, screen orientation, cropping, flicker, and any errors.
5. Stop with Ctrl-C. Restart to confirm recovery. Unplug/replug and Mac sleep were
   exercised on 2026-11-12; repeat them if the wiring or firmware changes.

If allocation fails or the screen is blank, stop and record the error plus the
firmware version; return to the vendor demo before changing display registers.

## Host commands

The blink also listens on the same USB serial port, without blocking the
animation. From the repository root:

```sh
python3 tools/send_blink.py /dev/cu.usbmodem1101
```

With no argument it uses `/dev/cu.usbmodem1101`, which changes when the board is
plugged into a different port. The sender writes the two `face.blink` messages
from [protocol.md](../../docs/protocol.md), prints the device's reply, and exits
non-zero unless both messages were answered `ok`; extra serial output never counts
as an acknowledgement. Standard library only, no `pyserial`.

The device answers `ping` and `face.blink` today and replies `err`/`unsupported`
to the other documented commands. It holds the eyes closed for at most 2000 ms
per `blink:true`, so a sender that dies mid-blink cannot leave them shut.
Ctrl-C still stops the loop and turns the backlight off.

## Checks without hardware

```sh
python3 -m unittest discover -s tests -p test_device_blink.py -v
```

Checks verify smooth edges and open/blink/open restoration, verify the SPI
window commands, reject invalid bounds, and exercise tick wraparound and stopping.
They do not emulate the controller, measure available device memory, or establish
electrical/display performance. MicroPython APIs: [framebuf](https://docs.micropython.org/en/latest/library/framebuf.html)
and [time](https://docs.micropython.org/en/latest/library/time.html); the prototype
uses basic fill/rectangle operations rather than newer drawing features.
