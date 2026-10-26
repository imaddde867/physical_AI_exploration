# MacDesk Buddy — minimum repeat-use hardware basket

The goal is to buy **as little as possible without introducing disposable/unsupported parts**. Your MacBook M4 provides the host; the ESP32-S3 runs display/sensor I/O. 3D printer access is already available.

## One recommended Finnish-delivered order (advertised prices, 2026-10-26)

| Item | Model/specification | Listed € | Need |
|---|---|---:|---|
| Controller | Otronic **ESP32-S3 N16R8** (16MB flash, 8MB PSRAM, 2 × USB-C), header installation check | 9.95 | Required |
| Display | Otronic 0.96" 128×64 I²C OLED, **controller SSD1306 not confirmed** | 5.99 | Required; confirm before purchase |
| Motion sensor | MPU-6050 I²C 6-axis breakout | 3.75 | **Recommended** for Reel #9-style reactive behavior |
| Breadboard | 830-hole solderless prototyping board | 2.39 | Required for learning/prototyping |
| 40 female–female wires | 20 cm | 1.85 | Required for two header-equipped modules |
| 40 male–female wires | 20 cm | 1.85 | Useful for breadboard |
| USB-C data cable | 1 m; omit if already owned | 2.65 | Required unless already owned |
| Delivery | Otronic tracked to Finland | 8.00 | Checkout estimate |

**Total including MPU-6050: €36.43.** OLED-only €32.68; both exclude optional tools, extra taxes/currency adjustments or changed checkout conditions. Verify headers on all three electronics boards.

## Useful longer-term tools

- Low-voltage multimeter for continuity, 3V3/5V rail checks and avoiding short circuits; buy a more durable branded model if budget permits.
- Digital or vernier caliper to measure hardware before designing mounts.
- Basic soldering equipment **only if needed** for unpopulated headers or later permanent wiring.

## Alternatives / avoid early purchases

- Explicitly specified **Joy-IT SBC-OLED01V2 SSD1306** from Partco, €11.29 + its separate shipping, is safer than guessing the controller. Check interface jumpers/configuration.
- Defer microphones, amplifiers, cameras, servos, separate 5 V supplies and batteries until the base build works and electrical requirements are documented.
- This full-size N16R8 board is ideal for reusable experiments; a future **XIAO-sized board** may make the finished desk sculpture much smaller, but changing boards means rechecking pinouts and CAD.
- No new LLM workstation, RTX GPU or cloud service is necessary for this phase.

[Exact vendor links and seller-side limitations](shopping-list.md).
