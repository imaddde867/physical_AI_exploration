# Architecture and validation

Host Python serial messages are newline-delimited UTF-8 JSON:

```text
Mac -> MCU  {"cmd":"face","value":"happy"}\n
MCU -> Mac  {"type":"ack","face":"happy"}\n
```

Valid faces: neutral, happy, sad, sleepy, surprised, thinking. Every other face is rejected; no general `eval`, shell execution or model-directed actuator API is exposed. The board emits a `ready` event on reset, optionally with `display:not_found`.

**Host:** converts validated app actions into finite device commands, optional future local inference, permission gates. **Firmware:** drives physical display/I2C and validates commands. **Enclosure:** independent, source-controlled geometry.

**Acceptance criteria:** USB-only communication, command->ack for all six expressions, fail-closed bad inputs, display absent recognized, no cloud credentials, all Python unit tests green, reproducible firmware build captured after hardware arrives. No performance claims until measured.

**Next empirical work:** capture >=100 Mac->MCU command round-trips with monotonic timestamps, report p50/p95/p99 including reconnect and board-reset behavior; measure system memory and serial errors; retain raw CSV and methodology. Firmware rendering is not timed by host ACK alone.
