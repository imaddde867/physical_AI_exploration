# Nine saved Instagram Reels — technical notes for future projects

> Earlier inspiration research. Use the [2026-10-27 purchase audit](../reports/MacDesk%20Buddy%20purchase%20audit.md) for the current face-first recommendation and verification limits; original Reel files were unavailable during that audit.


**Research checkpoint: 2026-10-26.** Nine MP4s, **eight distinct projects**: videos **02 and 06 are successive updates of the same Mac AI Buddy**. No original videos or creator images are distributed in this repository. The original study inspected video frames, legible captions and publicly linked project/manufacturer sources. **Complete verbatim audio transcription was not performed.** The table below separates **project-documented facts** from **proposed experiments**.

## Evidence notation

- **Source:** linked creator's current public repository, product documentation or project page.
- **Video:** detail visibly identifiable in the saved Reel's imagery/captions.
- **Proposal:** independent extension, not claimed to have been built by the creator.
- **Unresolved:** original source, connector revision, electrical tests or other supporting evidence missing.

## Reel/file mapping

| # | Saved filename | Project |
|---:|---|---|
| 01 | `20261025_164350000_iOS.MP4` | Atticus macOS desktop agent |
| 02 | `20261025_164610000_iOS.MP4` | Mac AI Buddy Day 2 |
| 03 | `20261025_164620000_iOS.MP4` | Rocky |
| 04 | `20261025_164935000_iOS.MP4` | Neo Deskimon |
| 05 | `20261025_165244000_iOS.MP4` | Physical Taby |
| 06 | `20261025_165416000_iOS.MP4` | Mac AI Buddy Day 1 |
| 07 | `20261025_165443000_iOS.MP4` | M5Stack StackChan |
| 08 | `20261025_165745000_iOS.MP4` | OOMWOO |
| 09 | `20261025_173551000_iOS.MP4` | Minimal motion-reactive desk buddy; source unknown |

---

## 01. Atticus — macOS assistant, not robotics hardware

**Source:** https://github.com/SaarthurR/atticus-mac

**Video:** macOS assistant controlled through natural voice and desktop context. **Source:** a macOS-native tool/agent frontend; verify its current supported model providers, permissions and macOS release compatibility before installation.

**No hardware purchase** is needed. The main thing to learn is the boundary between a probabilistic assistant and real-world actions. **Proposal:** implement an allowlisted `set_expression(face)`, `read_motion()`, and `sleep_device()` interface. Never let an LLM's shell command directly write arbitrary GPIO or servo instructions. Experiment first with simulator-only actions and an audit log.

**Next action:** inspect README, dependency installers and macOS Accessibility permissions; test in an isolated/scratch environment before giving access to personal files.

## 02 + 06. Mac AI Buddy — both Reels are one project

**Source:** https://github.com/AyhanSh/Mac-AI-Buddy

**Video 06 (Day 1):** a small classic Macintosh-inspired companion evolves from face/UI and a printed shell into conversation. **Video 02 (Day 2):** head movement, a printed pan/tilt mechanism and camera face tracking are introduced.

**Source-documented architecture:** ESP32-CAM **or** ESP32 + OV2640, SSD1306 OLED face, **two SG90 servos**, laptop-hosted Python, local MLX-Whisper speech recognition, a model/tool backend such as Ollama, memory in SQLite and optional hosted ElevenLabs voice output. Device exposes HTTP endpoints for facial expressions, look direction, capture, audio and status.

**Reproduction order (proposal):**
1. Establish the exact board variant and GPIO wiring; never assume our N16R8 + GC9A01 firmware can run it.
2. Test the firmware/device API without AI or servos first, then add one servo on a properly rated **separate** supply with common ground and safe angle limits.
3. Test camera acquisition; move from image coordinates to pan/tilt targets with deadband and smoothing; measure tracking stability and delay.
4. Validate typed text → model/tool → simulated device response before starting microphone capture. The M4 laptop can host smaller local models; benchmark memory/swap, don't assume larger creator defaults are suitable.
5. Add audio output last, with microphone echo control.

**Rights:** Public source repository did not specify an explicit license in the reviewed revision. **Do not vendor its code/3D assets** without permission. It is still useful to learn and reference.

## 03. Rocky — camera, motion, voice and a small body

**Creator source:** https://github.com/cgro00/desk-robot

**Version discipline:** The older Reel matches the creator's [**v1.0 release**](https://github.com/cgro00/desk-robot/releases/tag/v1.0), not necessarily current `main` (V2). V1 used a camera/mic-equipped **Seeed XIAO ESP32S3 Sense**, OLED display and an off-the-shelf two-servo pan/tilt bracket. The newer V2 README specifies a **2.42-inch SSD1309 I²C OLED**, **MG90S metal-gear servos**, MAX98357A amplifier and small speaker, with custom printed gears/head. The creator estimates approximately **$100 in V2 parts**, plus tools and a separately sold build bundle.

**Physical lesson:** Large-model inference lives on the Mac/PC; deterministic face/motor/camera I/O lives on the embedded board. In V2, **5 V servo/amp power, a common ground, the 470 µF supply capacitor and protective diode** are explicitly described; **never power servos from XIAO 3V3**. Follow the correct version's actual wiring, not these summary words.

**Next experiment:** record `camera_frame → face_detection → pan_request → actual_head_motion` and distinguish model latency from servo settling. Compare V1's simpler no-printed-neck build against V2's better mechanics. Code is MIT; paid CAD/build plans are separate.

## 04. Neo Deskimon — product design and 3D-printed character

**Creator:** https://creative-chance.com/pages/world-of-deskimon

**Video:** decorative, visually expressive desk character built around an embedded screen and printable body. **Creator product model:** a purchased **digital kit** includes printable files, software, assembly guide and part links; **electronics are purchased separately**. Do not assume raw software source or an unrestricted CAD license is included.

**What to learn:** printable tolerances, enclosure aesthetics, surface finish, display masking, wire routing and modular accessory design. **Proposal:** borrow only general mechanical *principles*, not proprietary artwork/firmware. Our [open-back CAD](../cad/desk-buddy.scad) is an independent prototype, **not a Neo Deskimon reproduction**.

**Next action:** inspect kit license, exact module SKU, dimensions, battery requirements and 3D print settings before deciding whether the paid bundle is worth buying.

## 05. Physical Taby — two excellent AMOLED targets

**Official firmware/repository:** https://github.com/TRIIIS-LABS/firmware-taby  
**Specific board verification:** https://github.com/TRIIIS-LABS/firmware-taby/blob/main/INSTALL.md

**Source (2026-10-26):** Taby currently supports (a) **Waveshare ESP32-S3-Touch-AMOLED-1.64 V1**, 280×456 AMOLED, touchscreen, 84 animations, **downloadable STL/3MF housing** and onboard motion sensor; and (b) **Waveshare ESP32-S3-Touch-AMOLED-1.32**, **round 466×466 AMOLED**, touchscreen, 27 animations, with **official round case not yet released**. The 1.64 **V2 is unsupported**. Do not infer board revision from USB VID/PID; check PCB marking or actual purchase variant.

**Key engineering distinction:** Both integrated displays use **QSPI AMOLED controllers**, not the generic GC9A01 4-wire SPI LCD. They are **not compatible** with our PlatformIO profile or our 31.4 mm circular CAD aperture. The round 1.32 includes ESP32-S3/mic/audio circuitry on the board; there is no reason to purchase a separate N16R8 merely to use that display.

**Reproduction:** confirm exact supported board → follow Taby's release-specific **signed/checksummed bundle** instructions → visually validate expression → connect the desktop app if desired → print matching design (1.64 V1 available; round needs a custom, measured housing) → test documented device commands. Verify Mac app/integration features for the specific installed version.

**Rights:** Original code/3D assets have Apache-2.0 terms; **Taby artwork and animations are restricted separately**. Study/modify according to license; don't rebrand artwork as our own.

**Why it matters:** Best short route to a beautiful, high-density display for an AI companion. Evaluate against the separate-parts learning benefits in [the hardware matrix](hardware-options.md).

## 07. StackChan K151 — fully assembled embodied reference

**Manufacturer docs:** https://docs.m5stack.com/en/StackChan  
**Product:** https://shop.m5stack.com/products/stackchan-kawaii-co-created-open-source-ai-desktop-robot  
**Repository:** https://github.com/m5stack/StackChan

**Source:** CoreS3 (ESP32-S3, 16 MB flash, 8 MB PSRAM), **2-inch capacitive screen**, 0.3 MP camera, dual microphone, speaker, **nine-axis IMU**, proximity/ambient light, NFC, LEDs, **two servo axes**, and **550 mAh battery**. Official K151 robot lists **$99** before shipping/tax. Manufacturer ecosystem offers firmware, remote/mobile and server tools; availability and cloud/account requirements depend on installed firmware/app.

**What to learn:** safe servo control, edge sensor events, device-to-host messaging, interactive voice/camera, wake/sleep power management and mobile UI. **Proposal:** build a latency/quality benchmark comparing its ready-made model/voice path with a secure Mac-local agent controlling a minimal allowlisted device interface.

**Don't confuse** a small ESP32-S3 robot with a locally running large LLM; the expensive inference must happen on host/cloud/other hardware.

## 08. OOMWOO — real robotics, currently simulated

**Repository:** https://github.com/makerspet/oomwoo

**Source says explicitly:** **physical robot not buildable yet; simulation can be run now**. Goal: Raspberry Pi/CM hardware, ROS 2, Gazebo, LiDAR, SLAM/navigation, cleaning actuator subsystem and eventually 3D printable hardware. Its current actual BoM and assembly must not be treated as ready to buy.

**Recommended first software task:** follow upstream simulation README and observe actual `/scan`, `/odom`, `/tf` and mapping/navigation topics if present. Run a repeatable route; compare localization and trajectory error, collision count and coverage in simulated scenarios. Keep results and launch configs reproducible.

**Long-term benefit:** introduces control, real-time systems, sensor fusion and uncertainty in ways small animated desk companions do not. Your Windows/WSL and work GPU machines may help **training** but aren't necessary for basic ROS 2 simulation.

## 09. Minimal motion-reactive desk buddy — foundation for our original build

**Original source:** not identified with confidence. The Reel shows tiny cube-like characters, eye screens, a microcontroller and a motion-sensor-style module, with emphasis on simple **two-wire I²C** and expressions responding to movement.

**Our implementation is an adaptation, not an exact parts-level clone:** we intentionally replaced the monochrome I²C display with a visually better **GC9A01 color IPS LCD on SPI**, while the **optional MPU-6050 remains on I²C**. This introduces both buses. Our own firmware, Python JSONL controller and OpenSCAD shell are in this repository.

**Milestones:** no-hardware simulator → PlatformIO compile → power and wire screen safely → verify physical color/animation → connect IMU and measure false positives → print fit coupon → verify mount and document real latency → later add an explicitly bounded Mac-local AI interface.

**Source caution:** don't attribute our GPIO assignments, CAD or higher resolution panel to the unknown original creator.

---

## Career/skills progression from the videos

| Stage | Hands-on new engineering skill | Evidence to capture |
|---|---|---|
| A — First companion | Electronics pinout, 3.3V supply, SPI, I²C, serial, first 3D print | Photos, wiring diagram, first successful physical display, reproducible firmware |
| B — Sense/react | IMU readings, sampling, thresholds, timing, event protocol | Raw samples, motion false-positive rate, p50/p95/p99 response times |
| C — Mac-local intelligence | Speech/model inference, action permission boundaries, host/device separation | End-to-end audio/model/tool latency, memory/swap, false action rate |
| D — Mechanics | Servos, power separation, limits, tracking stability | Current draw, position error, repeatability, safety failure tests |
| E — Robotics | ROS 2, transforms, mapping, navigation, simulation | Reproducible trajectory/coverage comparisons, quantified uncertainty |

Treat videos as inspiration, not scientific evidence of a reproducible design. A GitHub source and assembly footage are starting evidence; **real boards and measured results** determine reproducibility.
