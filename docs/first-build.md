# First build: beginner checklist

## Stage A — free, no hardware

- [ ] Read `README.md` and inspect the architecture drawing.
- [ ] `python3 -m unittest discover -s tests -v` passes.
- [ ] `python3 -m macdesk.demo --simulate --face happy` prints an acknowledgement.
- [ ] Open `cad/desk-buddy.scad` in OpenSCAD; adjust dimensions for your board, screen and cable.
- [ ] Print only the fit-check cradle initially.

## Stage B — minimal physical build

- [ ] Buy one ESP32-S3 DevKitC-1-style USB-C board, one **SSD1306 I2C** OLED at 3.3 V, female-female jumper wires, and a small solderless breadboard if the board and display are header-equipped.
- [ ] Check that the parts **actually have usable headers**, or arrange help with soldering.
- [ ] Before wiring, disconnect USB. Verify display VCC and the ESP32 3V3 pin; never place servo loads on the 3V3 pin.
- [ ] Install firmware dependencies; compile and flash with the correct board settings.
- [ ] Check that the board says `{"type":"ready","display":"ok"}` and draws eyes.
- [ ] Use a **data** USB-C cable; test every face via `macdesk.demo`.
- [ ] Measure board and display; adjust the CAD and print a fit test, then full stand.

## Stage C — report results

Record: exact board SKU, display PCB revision/controller, operating system, PlatformIO package versions, USB port, CAD dimensions, print time/material, wiring photo, actual response latency, power issues and failures. Don't claim performance or power use without measuring.

## Electrical and privacy guardrails

Use USB only for V0; no LiPo battery or mains modifications. Never power motors from MCU 3V3; use separately rated 5 V with shared ground and proper motor protection when upgrading. Do not enable public access or auto-executing arbitrary model-generated shell commands. For Mac automation, use a human-approved allowlist and local authentication.
