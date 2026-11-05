# Ordered prototype bring-up handoff

Prepared 2026-11-04 after the project reset. Start by reading [the product brief](../product-brief.md) and [current CAD decisions](../../cad/slab/DECISIONS.md).

Status: ordered 2026-11-04, BerryBase order 1097674: [Waveshare RP2040-Touch-LCD-1.69](https://www.waveshare.com/product/rp2040-touch-lcd-1.69.htm) (€29.80 delivered, 240×280 portrait, integrated RP2040 with 264 KB SRAM and 16 MB flash, capacitive touch), powered over the existing 50 cm Apple USB-C cable. This supersedes the Pico WH + Pico-LCD-1.8 basket in the [budget report](../../reports/Budget%20companion%20learning%20hardware.md), which was never ordered. The earlier [display shortlist report](../../reports/Companion%20display%20hardware%20shortlist.md) remains source history.

## Goal and decisions

Bring up the ordered board as the first working **animated companion**. The user approved the current black-glass, silver-frame sidecar appearance beside the MacBook lid's right edge. The concept is about 59 × 49.65 mm; preserve its proportions while allowing dimensions to change for real hardware. Usage meters, focus timer, lyrics, and chat can follow gradually.

Begin with ordinary USB power/data and an optional simple desk holder. Thin packaging, magnetic attachment and electrical contacts are deferred until a working prototype; retain the detachable black-glass/silver-frame concept as the long-term appearance. No separate battery purchase is required. Final enclosure hardware and electronics fit remain open; the ordered board already includes its MCU.

## Evidence and branches

- Good Display GDOJ0269C01 / ESP32-P4 is the previous, paused proposal. See [the bring-up log](bringup-log.md) for connector, power, initialization, and availability gaps. Its old prices/stock are not current evidence.
- Current CAD: `cad/slab/src/placement.py`, `mount.py`, and `params.py`; preview commands in [CAD decisions](../../cad/slab/DECISIONS.md). The shell is a largely solid exterior concept, not a hollow printable electronics enclosure.
- Simulator: 240×280 portrait RGB565, 27.972 mm visible-width default from the vendor panel drawing; verify physical scale on arrival. The two eyes are a placeholder.
- `daemon/protocol.py` is a tested draft codec/watchdog, not a running service or firmware.
- Separate [PR #13](https://github.com/imaddde867/physical_AI_exploration/pull/13) proposed a different conceptual dock with contact insulation, locating features, and cable-exit changes. It was closed unmerged (2026-11-04, merge conflicts) and is not part of this reset baseline; reuse its ideas deliberately rather than duplicating them. Do not silently combine its geometry with the approved preview.

## Bring-up and later enclosure research

Run Waveshare's demo on delivery, then a blink, then one Mac serial command over the existing USB cable. Follow the [device renderer plan](../product-brief.md#device-renderer-plan): one packed RGB565 framebuffer, with runtime memory measured on the board. Firmware and transport still need implementation.

The broad display shortlist is paused. Revisit alternatives only if prototype evidence requires them or later enclosure work needs a thinner route. Compare:

- Visible area, glass/board dimensions, thickness of the entire assembled stack, FPC/connector orientation, and cable access.
- Real driver/demo evidence, animation capability, supported interface, controller RAM, and development effort.
- Complete power requirements and USB data/power path; exposed contacts and live attachment need an engineered solution.
- Current Finland/EU availability, exact part numbers, quantity-one delivered cost including shipping/tax where verifiable, and lead time.
- Compatibility with the approved silhouette; clearly separate known measurements, supplier claims, and unknowns.

Prove the ordered display works before freezing final enclosure CAD or production parts.

## Remaining physical checks

Collect [real Mac measurements](measure-mac.md), [printer details](printer.md) (model known; filament material and print profile still open), and a moving-lid cable-route test. Current cable slack is insufficient under the model's assumptions. Magnetic retention, spring contacts, hot-plug behavior, insulation, strain relief, electronics fit, heat, and enclosure assembly remain unverified.

## Reset and validation

The reset established the product brief, reconciled active and historical docs, and repaired named CAD exports and front/rear renders. It preserved existing simulator/protocol work and design history. The later order establishes the bench prototype, not final enclosure hardware. Generated video transcripts and summaries were removed at the user's request before publication; original videos are not part of the repository.

Pre-PR checks: dependency-free tests pass, local documentation links resolve, and the CAD rebuild/export/render succeeds. Assembly bounds (372.2 × 221.2 × 225 mm), volume, and 16 named parts match the approved preview. These checks establish a reproducible concept only. The reset PR's GitHub checks and merge state must be checked separately.
