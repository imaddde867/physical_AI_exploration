# Hardware shortlist handoff

Prepared 2026-11-04 after the project reset. Start by reading [the product brief](../product-brief.md) and [current CAD decisions](../../cad/slab/DECISIONS.md).

## Goal and decisions

Find a practical display/controller combination for the first working **animated companion**. The user approved the current black-glass, silver-frame sidecar appearance beside the MacBook lid's right edge. The concept is about 59 × 49.65 mm; preserve its proportions while allowing dimensions to change for real hardware. Usage meters, focus timer, lyrics, and chat can follow gradually.

The display should detach magnetically; the rear plate and fixed USB cable stay on the MacBook. Wired power/data and no battery are the current direction. Final panel, controller, power circuit, contacts, and electronics stack are open. Do not assume a custom PCB is required until comparing simpler working options.

## Evidence and branches

- Good Display GDOJ0269C01 / ESP32-P4 is the previous, paused proposal. See [the bring-up log](bringup-log.md) for connector, power, initialization, and availability gaps. Its old prices/stock are not current evidence.
- Current CAD: `cad/slab/src/placement.py`, `mount.py`, and `params.py`; preview commands in [CAD decisions](../../cad/slab/DECISIONS.md). The shell is a largely solid exterior concept, not a hollow printable electronics enclosure.
- Simulator: 800×600 RGB565, 54.6 mm visible-width default; these preserve the old candidate and do not select it. The two eyes are a placeholder.
- `daemon/protocol.py` is a tested draft codec/watchdog, not a running service or firmware.
- Separate open [PR #13](https://github.com/imaddde867/physical_AI_exploration/pull/13) proposes a different conceptual dock with contact insulation, locating features, and cable-exit changes. It is not part of this reset baseline; review its scope/status before reusing or duplicating that work. Do not silently combine its geometry with the approved preview.

## Research task

Build a small, sourced comparison of credible display + controller options. Include a ready-to-drive prototype option and a thinner bare-panel route only where the driving/power requirements are documented. Compare:

- Visible area, glass/board dimensions, thickness of the entire assembled stack, FPC/connector orientation, and cable access.
- Real driver/demo evidence, animation capability, supported interface, controller RAM, and development effort.
- Complete power requirements and USB data/power path; exposed contacts and live attachment need an engineered solution.
- Current Finland/EU availability, exact part numbers, quantity-one delivered cost including shipping/tax where verifiable, and lead time.
- Compatibility with the approved silhouette; clearly separate known measurements, supplier claims, and unknowns.

Recommend one preferred route and one fallback with the remaining evidence needed to buy a bench prototype. Prove the display works before freezing final enclosure CAD or production parts. No purchases, fabrication, or powered tests are authorized by this handoff.

## Remaining physical checks

Collect [real Mac measurements](measure-mac.md), printer model/material/profile (user says the printer is known, but details are not recorded), and a moving-lid cable-route test. Current cable slack is insufficient under the model's assumptions. Magnetic retention, spring contacts, hot-plug behavior, insulation, strain relief, electronics fit, heat, and enclosure assembly remain unverified.

## Reset and validation

The reset established the product brief, reconciled active and historical docs, and repaired named CAD exports and front/rear renders. It preserved existing simulator/protocol work and did not delete design history or choose hardware. Generated video transcripts and summaries were removed at the user's request before publication; original videos are not part of the repository.

Pre-PR checks: dependency-free tests pass, local documentation links resolve, and the CAD rebuild/export/render succeeds. Assembly bounds (372.2 × 221.2 × 225 mm), volume, and 16 named parts match the approved preview. These checks establish a reproducible concept only. The reset PR's GitHub checks and merge state must be checked separately.
