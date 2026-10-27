# Project evidence and inspiration audit

Access date: **2026-10-27**. Workspace reviewed: source, Python tests, firmware, CAD, three GitHub workflow files, README, architecture, hardware options, reel index/technical notes, release readiness and the historical initial audit. No source or manifest files were changed. No original Reel MP4s were present in the workspace file inventory, so no visual claims were independently rechecked against footage.

## Does the checked-in software support the intended MacBook desk companion features?

### Takeaway

The repository supports a software-only simulator and a narrow prototype path: Python sends one of six face names over USB JSONL, firmware draws one approved face with minor mood/blink overlays, and an optional MPU-6050 can emit a shake event. It does **not** implement timers, OS notifications, Codex/Claude session or token status, music playback/lyrics, screen awareness, voice, or AI. This is far short of the stated reactive desk-screen goal; those features should be described as desired future integrations, not current capabilities.

### Cited Findings

- The host protocol can serialize only `{cmd: face, value: <allowlisted face>}`; simulator mode prints synthetic acknowledgement and shake output; device mode sends this single command and reads responses. [`macdesk/protocol.py:4-14`](../../macdesk/protocol.py), [`macdesk/demo.py:8-15`](../../macdesk/demo.py), [`macdesk/demo.py:17-46`](../../macdesk/demo.py)
- Firmware accepts only `cmd == "face"` plus a valid face value and replies with ack/error; current outgoing event is `shake` or `imu_disconnected`, and ready reports `display=init_sent_unverified`. [`firmware/src/main.cpp:165-185`](../../firmware/src/main.cpp), [`firmware/src/main.cpp:142-163`](../../firmware/src/main.cpp), [`firmware/src/main.cpp:187-204`](../../firmware/src/main.cpp)
- The screen is one checked-in 240×240 PNG; six names apply small overlays to one identity. Blink is local and periodic. No text, lyrics, timer, notification, agent-status, token-count, audio, camera, or screen-context protocol is present. [`firmware/src/main.cpp:27-30`](../../firmware/src/main.cpp), [`firmware/src/main.cpp:84-122`](../../firmware/src/main.cpp), [`firmware/src/main.cpp:206-240`](../../firmware/src/main.cpp), [`docs/architecture.md:13-29`](../../docs/architecture.md)
- Project docs expressly describe V0 as offline deterministic logic, with no model on ESP32 and later Mac-local inference only as a future milestone; camera, networking, voice and models are out of scope. [`README.md:58-70`](../../README.md), [`docs/architecture.md:15`](../../docs/architecture.md), [`docs/release-readiness.md:34-38`](../../docs/release-readiness.md)
- The goal comparison is an inference from the implemented command surface and source tree: expected features would require new Mac host integrations, event sources, data models and a display/text rendering protocol. None can be supplied by the current simulator or firmware command handler.

### Inferences

- “Reactive face demo” is an accurate description of implemented behavior; “Mac companion” is currently an aspiration except for USB face control.
- The user's features split into distinct future capabilities: host-side integrations for OS timers/notifications, Codex/Claude and token data, and music state/lyrics; screen awareness would additionally require a permissioned screen-capture/context path. The round panel firmware currently exposes no text UI.
- The current hardware decision is a learning/electronics prototype rather than the most feature-complete route to the goal. The documented ready-made StackChan has camera/audio/touch/motion and servos, while Taby is a higher-density screen alternative; both need their own software and do not run this firmware unchanged. [`docs/hardware-options.md:11-17`](../../docs/hardware-options.md)

### Gaps

- The original Reel videos were absent; visual appearance, behavior, captions and exact demonstrated hardware were not independently verified in this audit. The repository itself says audio transcription was incomplete and the Reel-09 original source is unknown. [`docs/reel-index.md:3,15,25`](../../docs/reel-index.md)
- No hardware was assembled, bought, flashed or visually tested; repository docs say so explicitly. [`docs/release-readiness.md:14,26-34`](../../docs/release-readiness.md)

## Are build evidence, hardware assumptions, CI statements and external inspiration facts reliable?

### Takeaway

The software-level evidence is reproducible locally: **21 Python tests pass**, and `python3 tools/check_repository.py` passes. The configured PlatformIO and OpenSCAD jobs were not rerun because `pio` and `openscad` are unavailable; their workflow definitions prove intended checks, not current live CI status. Physical claims remain properly caveated in most docs. The main concrete purchase/build risks are unverified LCD header/backlight and pinout details, uncalibrated IMU threshold, and unvalidated CAD fit. External source checks broadly support the documented project distinctions; Mac-AI-Buddy’s current public GitHub page has no visible license declaration, so treat reuse rights as unverified.

### Cited Findings

- Local check output on 2026-10-27: `python3 -m unittest discover -s tests -v` — 21 tests, `OK`; `python3 tools/check_repository.py` — `OK: BOM €40.03, 7 hardware choices, Markdown/HTML image links, SVG and firmware contract.` [`tests/`](../../tests), [`tools/check_repository.py`](../../tools/check_repository.py)
- CI config runs Python tests/checker on Ubuntu/Python 3.12; firmware job installs PlatformIO 6.2.0 and builds both USB/UART profiles; CAD job installs OpenSCAD/trimesh dependencies, renders shell/coupon, and checks watertightness/connectivity/dimensions. These workflow files specify jobs and do not by themselves prove the latest run passed. [Python workflow](../../.github/workflows/python-tests.yml), [firmware workflow](../../.github/workflows/firmware-build.yml), [CAD workflow](../../.github/workflows/cad-check.yml)
- This audit could not establish a current GitHub Actions run result; README badges are live links but were not treated as status evidence. Thus README’s statement that tests/build/CAD “pass in CI” is a project assertion, while the local Python tests/checker are directly verified here. [`README.md:13-18`](../../README.md)
- Firmware explicitly states GPIO assignments must be checked against the actual board, TFT SCL/SDA labels mean SPI signals, BLK is intentionally left unconnected pending electrical verification, and the LCD’s write-only SPI path cannot confirm lit pixels. [`firmware/src/main.cpp:12-25`](../../firmware/src/main.cpp), [`firmware/README.md:14-38,65-81`](../../firmware/README.md)
- MPU-6050 motion uses a fixed 40 ms sample interval, magnitude deviation >0.55 g for two consecutive samples and a 1500 ms cooldown; code comments label threshold experimental/calibration-required. This is not measured or calibrated hardware behavior. [`firmware/src/main.cpp:23-25,128-163`](../../firmware/src/main.cpp)
- CAD is explicitly a parametric prototype, asks for physical board measurement, has no verified board mount, and provides a cheap fit coupon. CI’s watertight mesh result would not establish printer success or part fit. [`cad/desk-buddy.scad:1-4,43-53`](../../cad/desk-buddy.scad), [`docs/release-readiness.md:9-14,26-34`](../../docs/release-readiness.md)
- The €40.03 basket is listed as an estimate to Finland, not a checkout quote; the vendor does not confirm header population or BLK behavior, and the exact printer model is not established. No purchases were made. [`docs/shopping-list.md:3-19,31-42`](../../docs/shopping-list.md), [`README.md:45`](../../README.md)
- Atticus’s current README describes a macOS agent with screen reading, app/music actions, notifications/watch behavior and permission gates; it requires macOS 26+ and an AI client. This is a separate software reference, not part of this repository’s implementation. [Atticus README](https://github.com/SaarthurR/atticus-mac/blob/main/README.md)
- Mac-AI-Buddy’s repository README describes ESP32-CAM or ESP32+OV2640, SSD1306, two SG90 servos, HTTP endpoints, local Ollama/MLX Whisper options and optional hosted voice. Its public page has no displayed license text; current explicit license status is therefore unverified, and copying should be avoided without permission. [Mac-AI-Buddy repository](https://github.com/AyhanSh/Mac-AI-Buddy)
- Rocky’s v1.0 release describes the V1 video configuration (XIAO ESP32S3 Sense, OLED, SG90 pan/tilt, camera/mic, amp/speaker, Python brain). Current README describes V2 parts, including MG90S and a printed neck; V1 footage must not be conflated with V2. Current repo states MIT code, while the printed hardware bundle is distributed separately. [Rocky v1.0 release](https://github.com/cgro00/desk-robot/releases/tag/v1.0), [Rocky repository](https://github.com/cgro00/desk-robot)
- Neo Deskimon’s creator page sells a digital kit containing print files, software, guide and parts list, with electronics bought separately. That page does not establish raw source availability or an unrestricted redistribution license; do not infer either. [World of Deskimon](https://creative-chance.com/pages/world-of-deskimon)
- Current Taby INSTALL board table supports Waveshare ESP32-S3-Touch-AMOLED-1.64 V1 and round ESP32-S3-Touch-AMOLED-1.32; it explicitly says 1.64 V2 unsupported. Repository README lists the 1.64 case as downloadable and round case as coming soon. License file applies Apache-2.0 to code/docs/original mechanical designs but separate terms to Taby art, requiring Taby attribution/identity and forbidding rebranding as a different original character/product. [Taby installation guide](https://github.com/TRIIIS-LABS/firmware-taby/blob/main/INSTALL.md), [Taby repository](https://github.com/TRIIIS-LABS/firmware-taby), [Taby license](https://github.com/TRIIIS-LABS/firmware-taby/blob/main/LICENSE)
- M5Stack’s K151 product page lists $99 and CoreS3-based unit with 2-inch touchscreen, camera, microphones, speaker, IMU, NFC, LEDs, two servo axes and 550 mAh battery. This is an as-accessed seller listing, not a landed price quote. [M5Stack K151 product page](https://shop.m5stack.com/products/stackchan-kawaii-co-created-open-source-ai-desktop-robot)
- OOMWOO README says physical robot is “not buildable yet” while simulation is runnable; it describes a future ROS 2/Gazebo project and identifies BOM/hardware validation as pending. It is a software/simulation study now, not a presently validated shopping list. [OOMWOO README](https://github.com/makerspet/oomwoo)

### Inferences

- CI claims should be phrased by evidence level: workflow configured; local Python checks passed in this audit; firmware/CAD builds configured but not rerun; live CI result not verified; no physical verification.
- On the current evidence the only purchase-ready confidence is an estimate conditional on seller confirmation and measuring parts. It is not a validated complete build kit.
- The archive is clearly marked obsolete OLED review and current-purchase guidance is redirected away from it; it should remain historical only. [`docs/release-readiness.md:3`](../../docs/release-readiness.md)

### Gaps

- `pio` and `openscad` are not installed; neither firmware configuration nor CAD job was locally rebuilt. No installs were made, as requested.
- No firmware was flashed, no serial-device interaction occurred, and no LCD, IMU, wiring, brightness/color/orientation, threshold or print-fit observation exists.
- Live GitHub Actions statuses were not verified, so do not state that the current remote runs are green based only on workflow YAML or README badges.
- Mac-AI-Buddy has no visible license declaration on its public repository page; this verifies absence of a displayed declaration there, not the creator’s private intent or legal status under every jurisdiction.
