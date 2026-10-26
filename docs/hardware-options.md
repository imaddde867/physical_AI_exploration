# Hardware decisions: Reel originals vs independently sourced alternatives

**Verified:** 2026-10-26. **Goal:** a good-looking, practical MacBook M4 companion with a credible path into IoT and robotics. This catalog preserves alternatives without suggesting they are electrically or firmware compatible.

## Decision in one minute

| Path | Based on | Screen / capabilities | Price evidence | Best reason to choose | Main limitation |
|---|---|---|---|---|---|
| **A — Supported first build** | Reel 09 concept, **original implementation** | ESP32-S3 N16R8 + 1.28″ **GC9A01 IPS**, 240×240; optional MPU-6050 | **€40.03** estimated full one-store basket delivered to Finland | Cheapest well-scoped **hands-on electronics** and learning SPI/I²C, wiring, CAD | Bare module pins/BLK need confirmation; small 31.4 mm visible aperture |
| **A2 — Better documented connector** | Online alternative | Waveshare 1.28″ GC9A01 240×240 with supplied 8-pin cable; still needs separate MCU | **$14.99** display alone before shipping | Same driver family, documented cable/pinout | Not necessarily drop-in **mechanically**; MCU end of cable still needs wiring |
| **B — Taby Round** | **Reel 05**, creator-supported | Waveshare **ESP32-S3-Touch-AMOLED-1.32**; 466×466 AMOLED, touch, mic/audio interface | **$21.99** board alone, excluding shipping/VAT | Best compact premium-looking **creator-supported** face/animations | Separate firmware/toolchain, official round case **not yet available** |
| **C — Taby 1.64 V1** | **Reel 05**, creator-supported | 1.64″ rectangular 280×456 AMOLED, touch, onboard IMU | **$23.99** board alone | Official Taby animations **and downloadable STL/3MF case** | **V1 only** supported; V2 incompatible; not a round face |
| **D — Creator-independent premium devboard** | Online alternative | Waveshare 1.43″ round **AMOLED 466×466**, ESP32-S3, touch, IMU/RTC | **$26.99–31.99** by case option | OLED black levels, **onboard sensor**, optional CNC case | Not Taby-compatible by default; separate firmware & CAD required |
| **E — Fully embodied robot** | **Reel 07**, StackChan K151 | 2″ touchscreen, camera, dual mic, speaker, sensors, 2 servos, battery | **$99** ready-made K151 robot | Fastest route to an actual moving/seeing/talking reference | More expensive, less foundational wiring, service/backend may matter |
| **F — Advanced DIY mechatronics** | **Reel 03**, Rocky V1/V2 | XIAO ESP32S3 Sense camera/mic, OLED, 2 servos, speaker | Creator estimates V2 **~$100 in parts** + tools/print bundle | Best deeper robotics hardware learning once comfortable | Soldering and servo power; paid 3D build bundle; old monochrome face |

**Important:** **A/A2** use *this repository's* GC9A01 hardware-SPI firmware (A2 still needs pin/BLK/fit verification). **B/C/D/E/F use different boards, controllers, pinouts and software**. Do not flash this repository's `platformio.ini` firmware onto them. The first phase is **not** an AI model on a microcontroller; the Mac is the future AI host.

## My recommended order of operations

1. **Without buying anything:** clone and run the Python simulator, inspect face art **and the physically scaled front view** ([visual guide](../assets/actual-scale-front.svg)), then decide whether a Ø31.4 mm visible display is big enough.
2. **Want to learn electronics at the lowest cost?** Choose **A** and [buy the €40.03 basket](shopping-list.md) **after confirming headers/backlight**.
3. **Want the most attractive, ready animated character with little wiring?** Consider **B** (round AMOLED Taby), accepting a different codebase and no official round enclosure yet.
4. **Want a creator-matched printable project now?** Choose **C**, but obtain an explicitly identified **1.64 V1**. The 1.64 V2 does not run the current Taby image.
5. **Want a longer-lived general-purpose standalone devboard with bigger round display and built-in IMU?** Choose **D**, but budget time to port firmware.
6. **Want actual movement/camera immediately?** Choose **E**; **F** is a richer DIY challenge to do later.

## Why the face preview can mislead

[Concept SVG](../assets/face-preview.svg) is an artistic illustration, **not drawn to the actual component/case scale**. The real budget LCD has **Ø32.4 mm active area** and current CAD opens **Ø31.4 mm** in a **72 mm-wide shell** — the exposed window is **~44% of the face body's width**. It will look more like a small round badge on a larger body, unless we shrink the housing or select a larger display. The [actual-scale view](../assets/actual-scale-front.svg) shows the dimension relationship. **Do not purchase based solely on the concept art.**

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

**Freshness check:** On 2026-10-26, the 830-hole Otronic breadboard listed **€2.99** (previously €2.39); this is why the complete basket is now €40.03 rather than €39.43. The quote is not a completed checkout.

**Price comparison limitation:** The €40.03 baseline **includes** estimated Finland shipping and a full basket. USD amounts apply to products or bare boards **only** and exclude postage, VAT/import costs, peripherals and optional enclosures. Cross-currency comparisons should not be treated as delivered-price rankings. Stock can change; no item was ordered. 
