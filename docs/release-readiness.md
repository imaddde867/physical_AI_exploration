# Build readiness

Audit date: **2026-10-29**. The [purchase decision](build-decision.md) selects Waveshare 1.64 V2 SKU 31197. No board has been purchased, flashed, mounted or physically tested. A separate selected-board bench renderer and deterministic face preview are implemented for software review. Physical firmware validation and the functional mount are unfinished.

## Verification record

| Area | Evidence | Limit |
|---|---|---|
| Host code | 37 Python/C/JavaScript checks and repository checker passed locally | Synthetic/mock USB, no real device |
| V2 face | Twelve generated states; host C decoder output matches every native RGB565 pixel; self-contained Mac preview | Physical orientation, colors, USB, DMA timing and brightness unverified; see [validation](../firmware-v2/VALIDATION.md) |
| Serial framing | Split acknowledgement and watch events survive read timeouts; overlong responses are bounded; incomplete ACK times out | Existing eight-read ACK budget remains; no reconnect service |
| Hardware catalog | Purchase track and implemented firmware track recorded separately, with regression checks | Catalog arithmetic cannot verify a seller cart |
| Existing firmware | Baseline d05e934 live GitHub firmware workflow passed when checked on October 29 | GC9A01 native USB/UART compile only; not selected-board firmware or physical display output |
| Existing OpenSCAD | Baseline d05e934 live CAD workflow passed | Older round desktop shell/coupon only |
| Selected CAD | cadgen 0.8.1 model built with nine valid solids; checks measure 25 mm top offset, 2 mm side gap and 10 degree inward face; no pod/lid solid intersection | Assumed lid and pod envelope; no fitted enclosure, latch, cable or attachment validation |
| Printable gauge | Published STL checked as two closed components, 45 x 27.5 x 8 mm | No Bambu Studio slice or physical print |
| Photos | H2S and AMS 2 Pro identified; spare hotends marked 0.4 | Installed nozzle, material and plate profile not established |

Baseline workflow evidence: [Python](https://github.com/imaddde867/physical_AI_exploration/actions/runs/40456528007), [firmware](https://github.com/imaddde867/physical_AI_exploration/actions/runs/40456527921), [OpenSCAD](https://github.com/imaddde867/physical_AI_exploration/actions/runs/40456527922). These links refer to the prior baseline, not the new changes. Check the runs attached to the final pushed commit separately.

## Remaining work

The official V2 display example uses a vendor QSPI initialization/driver path and software rotation. Our existing Adafruit GC9A01A target cannot drive it. Match the received revision to the [pinned V2 source](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.64-v2/tree/21b952243d306692774f3b5bfeb3eb5cff10f851); bring up that example before bench-testing the [ported character and protocol](../firmware-v2/README.md). Neither a compile nor a ready message proves that the physical panel is lit.

Implemented today: six GC9A01 face commands, local blink, synthetic host demo and optional experimental motion reaction; a separate V2 face renderer with offline pixel parity, deterministic preview and local dim/blank policy. Timers, short text, automatic Mac events, music, lyrics, token integrations, clips, screen awareness and model inference remain planned. The [decision's capability table](build-decision.md#what-the-software-needs) records how each request would be approached.

A Mac-local model is optional and has not been selected or benchmarked. The base M4 has 16 GB shared unified memory. No model, external GPU or cloud subscription is needed to test the current demo or plan deterministic event handling.

Proceed with the [first-build sequence](build-decision.md#what-to-do-next-in-order). A functional enclosure needs the actual board and laptop measurements. Sustained power/heat, display readability, USB reconnect, finish safety, retention, cable routing and transport all need physical checks.
