# Architecture and verification

~~~text
MacBook Pro M4
  | Python controller; USB serial, JSONL at 115200
ESP32-S3 N16R8
  |-- SPI MOSI GPIO11, SCK GPIO12, CS GPIO10, DC GPIO13, RES GPIO14
  |      \-- 1.28-inch GC9A01 240x240 round IPS LCD, powered by 3V3
  |-- I2C SDA GPIO8, SCL GPIO9
         \-- optional MPU-6050 motion sensor at 0x68
~~~

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
2. ESP32 PlatformIO CI establishes compile/link for native USB and UART profiles only.
3. OpenSCAD mesh checks establish closed geometry, not FDM slicer success or PCB fit.
4. Physical GPIO, voltage, backlight, color ordering, screen appearance, IMU and serial behavior require real components.
5. Future AI work must separately benchmark memory, responsiveness, action accuracy, p50/p95/p99 command latency and safety limits on a 16 GB M4.

No performance claims until results are measured under repeatable physical conditions.
