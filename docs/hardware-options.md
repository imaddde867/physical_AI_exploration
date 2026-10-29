# Hardware decisions: Reel originals vs independently sourced alternatives

> Current purchase decision: [one Waveshare 1.64 V2 and a USB data cable](build-decision.md). Earlier comparisons and the GC9A01 basket below remain reference material. Check the delivered revision before flashing or finalizing a case.

**Historical comparison recorded 2026-10-27:** subtle rounded-rectangle face, one discreet USB power-and-data cable.** The **Waveshare ESP32-S3-Touch-AMOLED-1.64 SKU 31197, listed V2**, is the leading documented purchase candidate behind revision/drawing/schematic and USB verification gates. The **GC9A01** remains the implemented prototype. See the [engineering study](../reports/Rectangular%20buddy%20engineering%20study.md) and [build plan](rectangular-build-plan.md).

This catalog preserves alternatives without implying electrical or firmware compatibility. Prices below were recorded on 2026-10-26; the audit did not recheck every listing, accessory or checkout total.

## Decision in one minute

| Path | Based on | Screen / capabilities | Price evidence | Best reason to choose | Main limitation |
|---|---|---|---|---|---|
| **A — Implemented prototype** | Reel 09 concept, **original implementation** | ESP32-S3 N16R8 + 1.28″ **GC9A01 IPS**, 240×240; optional MPU-6050 | **€40.03** reference basket with estimated Finland shipping | **Hands-on electronics** and learning SPI/I²C, wiring, CAD | Bare module pins/BLK need confirmation; small 31.4 mm visible aperture |
| **A2 — Better documented connector** | Online alternative | Waveshare 1.28″ GC9A01 240×240 with supplied 8-pin cable; still needs separate MCU | **$14.99** display alone before shipping | Same driver family, documented cable/pinout | Not necessarily drop-in **mechanically**; MCU end of cable still needs wiring |
| **B — Round Taby alternative** | **Reel 05**, creator-supported | Waveshare **ESP32-S3-Touch-AMOLED-1.32**; 466×466 AMOLED, touch, mic/audio interface | **$21.99** board alone, excluding shipping/VAT | Integrated round display, creator-supported animations | Different firmware; Mac bridge needed; official round case pending |
| **B2 — Leading custom rectangular candidate** | Waveshare SKU 31197, listed V2 | ESP32-S3-Touch-AMOLED-1.64; 280×456 AMOLED, touch | **$23.99** board listing, before checkout | Integrated rectangular display/MCU; single USB connection | Drawing-to-PCB revision map and USB data path unverified; custom firmware/CAD required |
| **C — Taby 1.64 V1** | **Reel 05**, creator-supported | 1.64″ rectangular 280×456 AMOLED, touch, onboard IMU | **$23.99** board alone | Official Taby animations **and downloadable STL/3MF case** | **V1 only** supported; V2 incompatible; not a round face |
| **D — Creator-independent premium devboard** | Online alternative | Waveshare 1.43″ round **AMOLED 466×466**, ESP32-S3, touch, IMU/RTC | **$26.99–31.99** by case option | OLED black levels and **onboard sensor**; case SKU unverified | Not Taby-compatible by default; separate firmware/CAD; confirm exact case option |
| **E — Fully embodied robot** | **Reel 07**, StackChan K151 | 2″ touchscreen, camera, dual mic, speaker, sensors, 2 servos, battery | **$99** ready-made K151 robot | Fastest route to an actual moving/seeing/talking reference | More expensive, less foundational wiring, service/backend may matter |
| **F — Advanced DIY mechatronics** | **Reel 03**, Rocky V1/V2 | XIAO ESP32S3 Sense camera/mic, OLED, 2 servos, speaker | Creator estimates V2 **~$100 in parts** + tools/print bundle | Best deeper robotics hardware learning once comfortable | Soldering and servo power; paid 3D build bundle; old monochrome face |

**Important:** **A/A2** use *this repository's* GC9A01 hardware-SPI firmware (A2 still needs pin/BLK/fit verification). **B/B2/C/D/E/F use different boards, controllers, pinouts and software**. Do not flash this repository's `platformio.ini` firmware onto them. The first phase is **not** an AI model on a microcontroller; the Mac is the future AI host.

## Recommended order of operations

1. **Without buying anything:** clone and run the Python simulator, inspect the face art, and make a paper mockup of the subtle rounded-rectangle direction. The Ø31.4 mm front view below documents only the legacy GC9A01 build.
2. **For the current direction:** evaluate **B2**, Waveshare 1.64 SKU 31197. Before purchase, resolve delivered board revision against drawing/schematic and verify native USB data. Taby’s 1.64 V1 support is a separate option, not support for the custom V2 candidate.
3. **For wiring practice:** retain **A** as the implemented GC9A01 route and use its [reference basket](shopping-list.md) only after confirming headers/backlight. Defer the optional IMU.
4. **Keep C–F as later alternatives.** They have different software and mechanical requirements; a 1.64 Taby build requires **V1**, not V2. No camera, microphone, motors or battery is needed for the first Mac-connected face.
5. Test the chosen display on the desk before designing a mount. The existing SCAD is a desktop prototype and the new rear-lid CAD is provisional; keep the device and cable clear of the lid and display glass.

## Actual screen size versus the finished body

[The approved 240×240 PNG](../assets/face-idle-240.png) is the **exact embedded source artwork** for the implemented GC9A01 prototype, but a browser's enlarged view is not the physical size of a finished device. The legacy budget LCD has **Ø32.4 mm active area** and current CAD opens **Ø31.4 mm** in a **72 mm-wide shell** — the exposed window is **~44% of the face body's width**. It will look more like a small round badge on a larger body, unless we shrink the housing or select a larger display. The [actual-scale view](../assets/actual-scale-front.svg) shows the dimension relationship. **Decide using the actual millimeter dimensions, not the size of a PNG in a browser.**

## What each of the nine videos contributes

| Video | Creator/project | Role in our roadmap | Action / licensing |
|---|---|---|---|
| 01 | [Atticus macOS agent](https://github.com/SaarthurR/atticus-mac) | Mac-side voice/tool frontend | Software reference; inspect desktop permissions |
| 02 + 06 | [Mac AI Buddy](https://github.com/AyhanSh/Mac-AI-Buddy) | Conversational ESP32 desk buddy, camera and pan/tilt | Two videos of **one** project; no explicit public code license verified; link rather than copy |
| 03 | [Rocky](https://github.com/cgro00/desk-robot) | Camera/audio, ESP32, servo movement | **V1 video matches v1.0 release**, V2 main differs; MIT code, CAD bundle separately distributed |
| 04 | [Neo Deskimon](https://creative-chance.com/pages/world-of-deskimon) | 3D-printed character/product design | Paid digital kit, source availability/rights must be checked |
| 05 | [Physical Taby](https://github.com/TRIIIS-LABS/firmware-taby) | **1.64 V1 and new round 1.32 AMOLED** animated interface | Code and mechanical design Apache-2.0; **Taby art has separate restrictions**; board revisions matter |
| 07 | [StackChan K151](https://github.com/m5stack/StackChan) | Fully assembled mobile-app/robot reference | Manufacturer ecosystem; use documented BSP/SDK |
| 08 | [OOMWOO](https://github.com/makerspet/oomwoo) | ROS 2, LiDAR, navigation | **Simulation ready, physical vacuum not yet buildable**; do not buy unvalidated parts |
| 09 | Independent 3-part sensing/face concept | **Our first implemented learning exercise** | Original source/repo not established; our code/CAD are original |

The [full nine-Reel technical notes](reel-technical-notes.md) are also in this repository, preserving the observed demonstrations, original sources, project-specific build challenges and next engineering steps. The original third-party MP4s remain outside the public repository.

## Sources and fair comparison

Maker documentation, not unsupported marketing claims:

- [Otronic GC9A01 spec, €8.99](https://www.otronic.nl/en/1-28-round-tft-lcd-240-240-gc9a01-spi-for-arduino); [N16R8 €9.95](https://www.otronic.nl/en/esp32-s3-n16r8-devboard-16mb-flash-and-8mb-psram); [Finland shipping €8](https://www.otronic.nl/nl/verzending).
- [Waveshare GC9A01 module with PH2.0 cable ($14.99)](https://www.waveshare.com/product/1.28inch-lcd-module.htm), [round ESP32-S3 1.32 AMOLED ($21.99)](https://www.waveshare.com/esp32-s3-touch-amoled-1.32.htm), [1.64 AMOLED ($23.99)](https://www.waveshare.com/ESP32-S3-Touch-AMOLED-1.64.htm), [1.43 round AMOLED ($26.99–31.99)](https://www.waveshare.com/product/esp32-s3-touch-amoled-1.43.htm).
- [Taby firmware support matrix](https://github.com/TRIIIS-LABS/firmware-taby/blob/main/INSTALL.md): `round-1.32` and `amoled-1.64` **V1 only**; [case availability](https://github.com/TRIIIS-LABS/firmware-taby).
- [Official StackChan K151 ($99)](https://shop.m5stack.com/products/stackchan-kawaii-co-created-open-source-ai-desktop-robot), [Rocky parts/version requirements](https://github.com/cgro00/desk-robot), [OOMWOO simulation status](https://github.com/makerspet/oomwoo).

**Price history:** The reference basket records a **€2.99** breadboard on 2026-10-26 and totals €40.03. Accessory listings were not individually rechecked in the audit; this is not a fresh quote or completed checkout.

**Price comparison limitation:** The €40.03 baseline **includes** estimated Finland shipping and a full basket. USD amounts apply to products or bare boards **only** and exclude postage, VAT/import costs, peripherals and optional enclosures. Cross-currency comparisons should not be treated as delivered-price rankings. Stock can change; no item was ordered. 
