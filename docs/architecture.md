# Architecture, protocol and test levels

~~~text
MacBook M4 (Python CLI; optional later model)
    | USB serial (native USB/OTG, newline JSON, 115200 baud)
    v
ESP32-S3 N16R8
    +-- I²C at GPIO8 SDA, GPIO9 SCL -- SSD1306 OLED (0x3C)
    +-- same I²C bus ------------- optional MPU-6050 (0x68)
~~~

**Mac host:** validates command choice; no arbitrary model-generated shell execution; future model tools must use an action allowlist.

**Firmware:** physical display driver, deterministic blinking and optional threshold-based shake detector. **No LLM or ML model** runs on the microcontroller.

## Wire protocol v1

~~~json
{"cmd":"face","value":"happy"}
{"type":"ack","face":"happy"}
{"type":"ready","display":"ok","imu":"ok","protocol":1}
{"type":"event","name":"shake"}
{"type":"error","reason":"invalid_face"}
~~~

Transport is UTF-8 line-delimited JSON. The six allowed facial values are neutral, happy, sad, sleepy, surprised and thinking. Overlong lines are discarded until newline; unsupported commands/values return errors. An absent IMU does not prevent OLED function. The sensor detector uses two consecutive 40 ms samples with large acceleration change and a 1.5 s cooldown; **thresholds are heuristic and require on-device calibration**.

## Evidence ladder

1. **Unit tests** establish Python JSON generation/parsing and simulator behavior (synthetic events are clearly labeled).
2. **Firmware CI build** establishes compilation/linking for selected platform/library versions and USB modes—not GPIO correctness or actual electronics.
3. **OpenSCAD watertight check** establishes printable *geometry*, not practical print orientation or dimensional fit.
4. **Physical device tests** establish serial, I²C, voltage, motion accuracy, materials/assembly and real latency. **Not done yet.**
5. **AI integration tests** later establish latency, reliability, security and model suitability on 16GB M4 without workstation dependency.

Measurements required later: ≥100 real command-to-ACK roundtrips, p50/p95/p99, sensor-event false positive rate and response latency, USB reconnect/recovery, Mac CPU/RAM/swap, board brownout checks. ACK is not itself a measured display-refresh timestamp.
