# Nine original inspiration Reels — source index

Research date **2026-10-26**. All nine uploaded Reels were inspected visually, but full verbatim audio transcription has **not** been completed. **02 and 06 are the same Mac AI Buddy project**. Technical specifics below are from creator/manufacturer docs, not guaranteed audible statements in the clips. For practical hardware comparisons and costs, see [Hardware choices](hardware-options.md).

| Video | Project / source | Exact current status and practical takeaway |
|---|---|---|
| **01** | [Atticus macOS agent](https://github.com/SaarthurR/atticus-mac) | Software agent/voice frontend. No electronics to purchase. Future Mac control-plane reference, with permission-gated robot tools. |
| **02** | [Mac AI Buddy Day 2](https://github.com/AyhanSh/Mac-AI-Buddy) | ESP32 camera plus two SG90 servos for tracking/head movement; laptop hosts reasoning. Public repo **does not specify a license**. |
| **03** | [Rocky](https://github.com/cgro00/desk-robot) | V1 footage matches [v1.0](https://github.com/cgro00/desk-robot/releases/tag/v1.0), **not** V2 main. Seeed XIAO ESP32-S3 Sense, speaker/amp, 2 servos and OLED. Code MIT; printed V2 build bundle separate. |
| **04** | [Neo Deskimon](https://creative-chance.com/pages/world-of-deskimon) | Paid 3D character + firmware/build-kit files; creator-supplied product rather than open firmware code to copy. Good industrial/character design reference. |
| **05** | [Physical Taby](https://github.com/TRIIIS-LABS/firmware-taby) | As of Oct 26, supports **Waveshare 1.64-inch AMOLED V1** (not V2) **and Waveshare round 1.32-inch AMOLED**. 1.64 STL/3MF available; round official case **coming soon**. Code/3D Apache-2.0; Taby animations/art **separately restricted**. |
| **06** | [Mac AI Buddy Day 1](https://github.com/AyhanSh/Mac-AI-Buddy) | Same repo as 02: early face/audio/host integration. Don't count twice or assume V2 motors were present from Day 1. |
| **07** | [M5Stack StackChan K151](https://github.com/m5stack/StackChan) | Fully assembled option (CoreS3, touch LCD, camera, mics, speaker, battery, two servo axes), **$99 base** before shipping. Software is in manufacturer ecosystem. |
| **08** | [OOMWOO ROS 2 vacuum](https://github.com/makerspet/oomwoo) | [Simulation available now](https://github.com/makerspet/oomwoo/blob/main/README.md); **physical vacuum not buildable/validated**. Useful ROS 2/Gazebo/Nav2 study, **not** a parts shopping list today. |
| **09** | Original DIY sensor-reactive desk buddy | No credible exact original repo established. Our independently authored **GC9A01 + ESP32-S3 + optional MPU-6050** build recreates the engineering concepts, **not the creator's display/model exactly**. |

## Good next investigations

- **Fundamentals:** Build 09-inspired MacDesk Buddy, learn I²C, SPI, serial protocol, power, 3D printing, physical tests.
- **Higher-fidelity display:** Reproduce 05 Taby **on its exact supported Waveshare board**, without trying to flash our GC9A01 build. For 1.64 **verify V1 PCB marking**. Avoid rebranding restricted Taby art.
- **Physical motion and perception:** Build 03 Rocky V1 or study 02/06 Mac AI Buddy, including servo power, camera, microphone and Mac model pipeline.
- **Integrated robotics reference:** Compare 07 StackChan K151 before buying separate motors/cameras.
- **Robot autonomy:** Run 08 OOMWOO in simulation; investigate ROS 2 topics, odometry, TF and navigation before purchasing mechanical hardware.

No Reel MP4s or third-party proprietary 3D/CAD art are included in this repository. Only source links and original work are checked in.
