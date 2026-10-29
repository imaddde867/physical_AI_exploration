# Architecture: implemented and planned

## Implemented GC9A01 prototype

~~~text
MacBook Pro M4
  | Python controller; USB serial, JSONL at 115200
ESP32-S3 N16R8
  |-- SPI MOSI GPIO11, SCK GPIO12, CS GPIO10, DC GPIO13, RES GPIO14
  |      \-- 1.28-inch GC9A01 240x240 round IPS LCD, powered by 3V3
  |-- I2C SDA GPIO8, SCL GPIO9
         \-- optional MPU-6050 motion sensor at 0x68
~~~

**Single-character graphics:** The [approved 240×240 PNG](../assets/face-idle-240.png) is verified by SHA256 in tests and compiled using the Python standard library into a 32-color palette/RLE asset in flash. Firmware writes one RGB565 scanline at a time (480-byte row buffer). Six backward-compatible face command values change small details on the **same identity**, never select other avatar designs.

This is a deterministic, fully offline embedded prototype. No large language model is loaded on the ESP32. Later Mac-local inference may choose from six **allowlisted** facial expressions; the model must never execute arbitrary shell commands or directly select unbounded actuator values.

## JSONL protocol version 1

~~~json
{"cmd":"face","value":"happy"}
{"type":"ack","face":"happy"}
{"type":"ready","display":"init_sent_unverified","driver":"GC9A01","imu":"ok","protocol":1}
{"type":"event","name":"shake"}
{"type":"error","reason":"invalid_face"}
~~~

Valid expressions: neutral, happy, sad, sleepy, surprised, thinking. Invalid JSON and unsupported requests are rejected; overlong lines are dropped. Blink is periodic and local; optional motion response is deterministic with an experimental sensitivity threshold.

**Important:** A GC9A01 on one-way SPI cannot acknowledge that pixels were illuminated. The startup message says **init_sent_unverified**, not false "display ok". The LCD must be inspected visually.

## Testing boundaries

1. Python unit tests and simulator establish host protocol correctness only.
2. The PlatformIO workflow checks compile/link for GC9A01 native USB/UART and the separate V2 profile. The prior GC9A01 baseline d05e934 passed when checked on 2026-10-29; current V2 results are recorded separately. No compile establishes physical display behavior.
3. OpenSCAD mesh checks establish closed geometry, not FDM slicer success or PCB fit.
4. Physical GPIO, voltage, backlight, color ordering, screen appearance, IMU and serial behavior require real components.
5. Future AI work must separately benchmark memory, responsiveness, action accuracy, p50/p95/p99 command latency and safety limits on a 16 GB M4.

No performance claims until results are measured under repeatable physical conditions.

## Planned Mac companion

The Mac gathers explicitly enabled events, decides the reaction, and sends bounded state or short-text messages over USB. The peripheral renders the face and occasional text. The current protocol only supports faces; timers, text and event adapters still need implementation. The selected Waveshare 1.64-inch AMOLED V2 uses the separate bench renderer below and its board-specific pinout, not the wiring above. See the [rectangular engineering study](../reports/Rectangular%20buddy%20engineering%20study.md) and [build plan](rectangular-build-plan.md).

Start with deterministic manual/timer events, then add supported coding-agent hooks, foreground-app identity and authorized music metadata. A local model is optional. Session token counts differ from account quotas; supported Claude Code or Codex workflows do not establish access to every existing desktop chat. macOS has no general documented inbox for other apps' notification bodies.

Screen awareness can later use opt-in screen capture and OCR/vision on the Mac. A camera is unnecessary for reading the Mac's screen. Capture scope, pause controls and any model data destination must be explicit; internal or partner data stays local. Lyrics need a suitable data source and display rights before implementation. No current feature requires motors, a battery or an IMU.

See the [source-backed capability matrix](../reports/MacDesk%20Buddy%20purchase%20audit.md) for platform limits and the [first-build milestones](first-build.md) for the implementation order.

## Separate V2 bench renderer (software only)

The [V2 project](../firmware-v2/README.md) adapts the approved raster to 456×280,
pre-rotates it to the vendor's native 280×456 order and streams RGB565 through
completion-checked, two-row DMA strips. It uses the pinned V2 QSPI initialization
and a single X offset of 20. All twelve rendered states are checked against a
host execution of the actual C decoder. Its standalone HTML preview shares the
same generated pixels and fixed blink schedule. USB JSONL face commands remain
bounded; V2 does not claim the older optional IMU behavior. It dims and blanks
locally on idle. Firmware compile results are recorded in the V2 validation note;
no physical display or USB validation has occurred. The GC9A01 implementation
above remains unchanged. Mac integrations, touch and text rendering remain planned.
