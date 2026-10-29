# V2 software validation · 2026-10-29

No board has been purchased, connected, flashed or physically tested.

| Check | Result | Meaning |
|---|---|---|
| Approved source | Original 240×240 PNG and GC9A01 implementation unchanged | Existing identity/prototype preserved |
| Generated assets | PNG/HTML regenerate identically from pinned source | Reproducible software artifact |
| C renderer | All twelve states match expected native RGB565 output byte-for-byte | Decoder, strip traversal, software rotation and wire byte ordering agree offline |
| HTML script | All twelve RGBA canvas buffers match RGB565 expansion; controls/boundaries exercised using Node's VM and a minimal DOM | Script behavior checked without a browser; not browser-layout verification |
| Python suite/repository | Final results recorded below after completion | No electronics involved |
| Firmware compilation | In progress; final result will be recorded before review | Not a physical panel test |
| Browser smoke test | Chromium unavailable; browser download returned truncated archives | PNG visually inspected; page layout still needs inspection on the user's Mac |

The original driver files remain byte-identical to the pinned V2 vendor source.
The separate renderer compiles against the ESP-IDF APIs rather than stubbing the
vendor driver. Host C checks exercise the real portable rendering core; they do
not execute ESP32 GPIO, QSPI, interrupts, USB or brightness commands.

Physical board-arrival checks and exact reproduction commands are in [README](README.md).
