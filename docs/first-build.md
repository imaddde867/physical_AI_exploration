# First-build milestones — rectangular MacDesk Buddy

**Goal:** a subtle rounded-rectangle face with occasional short text, powered and connected through one discreet USB cable. The Mac supplies events; the peripheral renders locally. See the [engineering study](../reports/Rectangular%20buddy%20engineering%20study.md) and [build plan](rectangular-build-plan.md).

## Leading custom rectangular candidate: work still needed

1. Gate purchase of Waveshare ESP32-S3-Touch-AMOLED-1.64 SKU 31197 (listed V2) on delivered PCB revision mapping to the official mechanical drawing and schematic, native USB data verification and Finland checkout. Rev1.1 schematic routes native USB D+/D− on GPIO19/20, but retail V2 mapping is unconfirmed. Do not treat Taby’s separate 1.64 V1 support as V2 support.
2. Bench the board and cable, measure its envelope and test native USB power/data before implementing the 1.64 display path and Mac USB event interface. Existing GC9A01 firmware and wiring below do not apply.
3. Treat 33.12 × 48 × 13 mm as provisional concept packaging only; verify face, colors, short-label readability, USB reconnect and board/cable dimensions on the desk.
4. Add a Mac timer/manual-event bridge, then supported coding-agent and music events one integration at a time. Screen capture is a later opt-in feature; lyrics and arbitrary notification access remain unresolved.
5. Build a custom rounded-rectangle case and USB-port opening around measured board and plug dimensions; the 33.12 × 48 × 13 mm concept is only a starting scale. Design any stand or removable laptop mount only after measuring weight, clearance and cable routing. The current CAD is a desktop prototype.

Start with one board and a data cable. Defer the IMU, microphone, camera, motors and battery.

## Alternative: assemble the existing GC9A01 learning prototype

The following checks apply only to the **separate ESP32-S3 N16R8 + GC9A01** build. The [approved single-face asset](../assets/face-idle-240.png) is its actual firmware source.

### Before purchasing

- [ ] Confirm [Otronic GC9A01 OT8724](shopping-list.md) has **pre-soldered headers**, or buy a module with a connector cable. Exact BLK pin behavior must be established before use.
- [ ] Confirm ESP32-S3 N16R8 USB/OTG port and GPIO10,11,12,13,14 / GPIO8,9 labels.
- [ ] Use an **optional MPU-6050** sensor only if you buy/have one; check its breakout board uses 3.3 V-safe I²C pull-ups.
- [ ] Use the confirmed Bambu Lab H2S; identify its installed nozzle and matching slicer profile before printing.
- [ ] No soldering, motors, batteries or high-voltage wiring planned for the first experiment.

### Free work before any order

- [ ] Run Python tests: python3 -m unittest discover -s tests -v
- [ ] Run simulator: python3 -m macdesk.demo --simulate --face neutral --watch
- [ ] Confirm ESP32 firmware compile workflow is green for **both** USB profiles.
- [ ] Inspect the [approved 240×240 screen PNG](../assets/face-idle-240.png), the [actual physical size diagram](../assets/actual-scale-front.svg), and the [parametric case](../cad/desk-buddy.scad).

### Breadboard assembly

1. Disconnect USB.
2. Wire the LCD at **3V3, GND, SPI MOSI GPIO11, SPI clock GPIO12, CS GPIO10, DC GPIO13, reset GPIO14**. The LCD pads labeled SCL and SDA are **SPI**, not I²C.
3. Leave BLK as specified in the firmware README pending seller confirmation; do not blindly connect to 5V or GPIO.
4. Optionally attach MPU-6050 at **3V3, GND, GPIO8 SDA, GPIO9 SCL**.
5. Flash the [correct firmware profile](../firmware/README.md) using native ESP32-S3 USB/OTG, then visually inspect the panel.
6. Send each of six expression commands from the Mac controller, test reconnection and invalid JSON, then test the sensor reaction only if a sensor is installed.
7. Record actual board/display model, header labels, color order, power issues, serial port, successful photos/videos and any discrepancies.

### Print and finish

1. Print just the circular 31.4 mm aperture coupon and check actual fit/visibility of the round 32.4 mm display glass.
2. Measure module PCB (seller nominal 44×36×5 mm), wire-header and USB cable clearance.
3. Update and render the OpenSCAD shell, inspect the **actual printer profile and slice supports** in Bambu Studio.
4. Print the shell; hold the module with removable, electrically insulating fixtures at safe PCB areas. Avoid pressure on LCD glass, exposed contacts and power components.
5. Do not close [Issue #1](https://github.com/imaddde867/physical_AI_exploration/issues/1) until real electrical and mechanical fit results exist.

Optional local inference and independently powered motion are separate later projects, after the display and Mac event bridge work.
