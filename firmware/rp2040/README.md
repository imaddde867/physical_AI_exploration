# RP2040 local blink prototype

For **Waveshare RP2040-Touch-LCD-1.69 (SKU 28161)** only. Prepared before
delivery; not flashed or validated on a board. USB power from the Mac is enough
for this prototype. Run the vendor demo first, then this blink.

`main.py` draws the simulator's placeholder eye geometry in white on black:
one 140 ms blink every four seconds. It uses the vendor driver's single packed
RGB565 framebuffer (134,400 bytes), prints the remaining MicroPython heap after
initialization, and redraws only when blink state changes. Ctrl-C stops the loop
and turns off the backlight. No touch, batteries, or host commands are needed.

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
The blink uses only black/white; vendor color constants and RGB byte order still
need a separate physical color test. Requested SPI speed is inherited from the
vendor example, not a measured stable rate on this board.

## On arrival

1. Connect the existing USB-C data cable. Check the factory demo if present.
2. Follow the board wiki's MicroPython setup. The example archive above already contains
   `Python/RPI_PICO-20240222-v1.22.2.uf2` (MicroPython 1.22.2, sha256
   `e92c2a25...bba9`): hold BOOT while plugging in, then copy it to the `RPI2-RP2` drive.
   Run the original vendor example from Thonny to establish a working baseline.
   Record the installed MicroPython version; no version has been board-tested here.
3. In Thonny, copy `waveshare_lcd.py` and our `main.py` to the board's root.
   Both files must be on the board. Saving as `main.py` makes the blink start on boot.
4. Run `main.py`. Expect two centered eyes and a short blink every four seconds.
   Record the reported free heap, screen orientation, cropping, flicker, and any errors.
5. Stop with Ctrl-C. Restart to confirm recovery. Test unplug/replug and Mac sleep/wake
   after a stable blink; those behaviors remain unverified.

If allocation fails or the screen is blank, stop and record the error plus the
firmware version; return to the vendor demo before changing display registers.

## Checks without hardware

```sh
python3 -m unittest discover -s tests -p test_device_blink.py -v
```

Checks compare open/blink/open geometry with the desktop face, verify the SPI
window commands, reject invalid bounds, and exercise tick wraparound and stopping.
They do not emulate the controller, measure available device memory, or establish
electrical/display performance. MicroPython APIs: [framebuf](https://docs.micropython.org/en/latest/library/framebuf.html)
and [time](https://docs.micropython.org/en/latest/library/time.html); the prototype
uses basic fill/rectangle operations rather than newer drawing features.
