# V2 software validation · 2026-10-29

No board has been purchased, connected, flashed or physically tested.

| Check | Result | Meaning |
|---|---|---|
| Approved source | Original 240×240 PNG and GC9A01 implementation unchanged | Existing identity/prototype preserved |
| Generated assets | PNG/HTML regenerate identically from pinned source | Reproducible software artifact |
| C renderer | All twelve states match expected native RGB565 output byte-for-byte | Decoder, strip traversal, software rotation and wire byte ordering agree offline |
| HTML script | All twelve RGBA canvas buffers match RGB565 expansion; controls/boundaries exercised using Node's VM and a minimal DOM | Script behavior checked without a browser; not browser-layout verification |
| Python suite/repository | 37 checks and repository checker passed locally; GitHub Python/repository job passed | No electronics involved |
| Firmware compilation | PASS: V2 ESP-IDF 5.5.0 compile/link and both unchanged GC9A01 USB/UART profiles; GitHub firmware workflow also passed | Not a physical panel test |
| Browser smoke test | Chromium unavailable; browser download returned truncated archives | PNG visually inspected; page layout still needs inspection on the user's Mac |

The original driver files remain byte-identical to the pinned V2 vendor source.
The separate renderer compiles against the ESP-IDF APIs rather than stubbing the
vendor driver. Host C checks exercise the real portable rendering core; they do
not execute ESP32 GPIO, QSPI, interrupts, USB or brightness commands.

Physical board-arrival checks and exact reproduction commands are in [README](README.md).

## Completed software checks

Validated implementation tree: PR commit `7f9dddc5774c309bc7d6da1ef1fb1d5bb089cf50`.
The subsequent validation-record update changes documentation only.

```sh
python3 -m unittest discover -s tests -q
python3 tools/check_repository.py
python3 -m platformio run -d firmware -e esp32s3_n16r8_usb
python3 -m platformio run -d firmware -e esp32s3_n16r8_uart
IDF_COMPONENT_MANAGER=0 python3 -m platformio run -d firmware-v2 -e waveshare_amoled_v2
```

All passed. The local V2 invocation disables ESP-IDF's optional component manager
because its process lookup failed inside the execution environment. All required
components are bundled; the project and vendor driver were not stubbed or changed
to get the build through. The standard V2 command also passed on GitHub Actions.
V2 linked static RAM: 13,288 bytes; flash: 465,509 bytes. Static RAM excludes
runtime heap/stack allocation; these are build sizes, not measured device usage.

GitHub runs for that implementation commit: [Python/repository](https://github.com/imaddde867/physical_AI_exploration/actions/runs/40829185918),
[all three firmware profiles](https://github.com/imaddde867/physical_AI_exploration/actions/runs/40829185919),
[CAD regression](https://github.com/imaddde867/physical_AI_exploration/actions/runs/40829185915).
All concluded successfully. No software result establishes physical screen behavior.

## Greptile review follow-up

Command handling now updates state only; the main loop owns redraws and updates
its cached frame after drawing. Rejected commands do not invalidate the cache.
The preview check now advances queued animation callbacks with a fake clock,
covering blink boundaries, the 12-second wrap, paused time, resume and rapid
pause/resume. Pending callbacks are cancelled on pause or scrub to avoid
duplicate animation chains.

All 37 checks and the repository checker pass after these changes. The V2
firmware recompiles and links: 13,288 bytes static RAM and 465,493 bytes flash.
The unchanged GC9A01 profiles retain the passing validation above. Final CI
results are attached to the PR head. Physical validation remains outstanding.
