# First physical build: stage gates

The intended experience is **MacBook + small nearby companion**, not a home-workstation service. Firmware provides local OLED control and optional motion response; LLM/voice integration comes later.

## A. Free validation, no board required

- [ ] Read [audit](audit-2026-10-26.md), [architecture](architecture.md), and [wiring diagram](../assets/wiring.svg).
- [ ] Run <code>python3 -m unittest discover -s tests -v</code> and <code>python3 -m macdesk.demo --simulate --face happy --watch</code>.
- [ ] Confirm firmware CI compiles both USB variants.
- [ ] Render [OpenSCAD enclosure](../cad/desk-buddy.scad), first using <code>part="fit_coupon"</code>.
- [ ] Check printer model **at the machine**; the Academy URL has not established it.

## B. Confirm parts before purchasing

- [ ] ESP32-S3 **N16R8** with USB/OTG, CH343P USB-UART and usable GPIO8/GPIO9, 3V3 and GND.
- [ ] OLED **SSD1306** (not just 128×64), 3.3 V supply/I²C, populated 4-pin header.
- [ ] Recommended additional sensor: **MPU-6050** 3.3 V-compatible breakout, populated headers.
- [ ] Jumper wires, breadboard, USB **data** cable, available filament; basic multimeter useful.
- [ ] Confirm prices + Finland shipping at checkout. See [shopping list](shopping-list.md).

## C. Breadboard bring-up (disconnect USB while wiring)

Wire OLED (and optionally MPU-6050) **3V3 / GND / GPIO8 SDA / GPIO9 SCL**; see diagram. Do not connect servo/battery/mains to this prototype.

- [ ] Compile and flash [firmware](../firmware/README.md) using **native USB/OTG** port for default profile.
- [ ] Confirm expected ready message and all six faces on the real SSD1306 screen.
- [ ] Test invalid face command, cable unplug/replug, boot with display disconnected.
- [ ] Add MPU-6050, confirm <code>"imu":"ok"</code> and <code>event:shake</code> when intentionally shaken; check false triggering.
- [ ] Record board/PCBs and their actual dimensions, wiring photos, pin labels and firmware package versions.

## D. Print

- [ ] Print a small window-fit coupon and measure its true hole dimensions.
- [ ] Adjust CAD dimensions against real PCB, headers, connector and display active area.
- [ ] Inspect Bambu Studio slicing preview carefully for bridging, overhangs and supports.
- [ ] Print the shell; retain board/display safely without stressing glass or shorting components.

## E. Evidence and next milestone

Capture short before/after video and first measured timings, plus any errors. Only then close [Issue #1](https://github.com/imaddde867/physical_AI_exploration/issues/1) and proceed to [Issue #2](https://github.com/imaddde867/physical_AI_exploration/issues/2). AI-controlled motion and voice should not be added without separate safety and privacy review.
