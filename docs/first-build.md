# First-build stage gates — round color MacDesk Buddy

The goal is a polished-looking companion beside a MacBook, not a second GPU workstation. The [approved single-face asset](../assets/face-idle-240.png) is now the firmware's actual source image, not a set of decorative concept characters. The selected face is **full-color GC9A01 IPS SPI**; the old SSD1306 monochrome screen is no longer in the bill of materials.

## Before purchasing

- [ ] Confirm [Otronic GC9A01 OT8724](shopping-list.md) has **pre-soldered headers**, or buy a module with a connector cable. Exact BLK pin behavior must be established before use.
- [ ] Confirm ESP32-S3 N16R8 USB/OTG port and GPIO10,11,12,13,14 / GPIO8,9 labels.
- [ ] Use the existing MPU-6050 as an optional sensor, at 3.3 V logic.
- [ ] Verify the actual Bambu printer model on the machine, not from the Academy link.
- [ ] No soldering, motors, batteries or high-voltage wiring planned for the first experiment.

## Free work before any order

- [ ] Run Python tests: python3 -m unittest discover -s tests -v
- [ ] Run simulator: python3 -m macdesk.demo --simulate --face happy --watch
- [ ] Confirm ESP32 firmware compile workflow is green for **both** USB profiles.
- [ ] Inspect the [original face preview](../assets/face-preview.svg) and [parametric case](../cad/desk-buddy.scad).

## Breadboard assembly

1. Disconnect USB.
2. Wire the LCD at **3V3, GND, SPI MOSI GPIO11, SPI clock GPIO12, CS GPIO10, DC GPIO13, reset GPIO14**. The LCD pads labeled SCL and SDA are **SPI**, not I²C.
3. Leave BLK as specified in the firmware README pending seller confirmation; do not blindly connect to 5V or GPIO.
4. Optionally attach MPU-6050 at **3V3, GND, GPIO8 SDA, GPIO9 SCL**.
5. Flash the [correct firmware profile](../firmware/README.md) using native ESP32-S3 USB/OTG, then visually inspect the panel.
6. Send each of six expression commands from the Mac controller, test reconnection and invalid JSON, then deliberately trigger the sensor reaction.
7. Record actual board/display model, header labels, color order, power issues, serial port, successful photos/videos and any discrepancies.

## Print and finish

1. Print just the circular 31.4 mm aperture coupon and check actual fit/visibility of the round 32.4 mm display glass.
2. Measure module PCB (seller nominal 44×36×5 mm), wire-header and USB cable clearance.
3. Update and render the OpenSCAD shell, inspect the **actual printer profile and slice supports** in Bambu Studio.
4. Print the shell; hold the module with removable, electrically insulating fixtures at safe PCB areas. Avoid pressure on LCD glass, exposed contacts and power components.
5. Do not close [Issue #1](https://github.com/imaddde867/physical_AI_exploration/issues/1) until real electrical and mechanical fit results exist.

Next phase: optional local language model and permissioned tools on the Mac, then independently powered motion hardware.
