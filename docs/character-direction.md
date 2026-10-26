# A character, not a status indicator

**Status: design exploration (26 October 2026). Awaiting user selection.** The original `assets/face-preview.svg` showed almost identical pairs of symmetrical cyan eyes with swapped mouth symbols. It was rejected because the characters looked generic and lacked a recognizable personality.

![Nine character sketches; these are concept explorations, NOT firmware output or real product photos](../assets/face-preview.svg)

## Distinct directions

| Candidate | Character identity | The personality is in the behaviour | Signature shape |
|---|---|---|---|
| **NIM** | Odd, curious, slightly mischievous forest gremlin | Curious sideways gaze; skeptical one-eye squint; unusually big delight response | Asymmetrical cream eyes, little pointed leaf tufts and **one crooked fang** |
| **LUNE** | Bashful nocturnal dream-spirit | Slow sleepy lid; tiny hesitations; sparkles only as reactions | Soft lilac eyes, moon/star ornament, tear-shaped anxious response |
| **KIP** | Cheeky night-shift robot | Dry side-eye, squint, lopsided smirk, short digital reaction | One big cyan lens, one thin pink display-eye, antenna, status-chip accent |

The aim is **emotionally readable, small-scale character animation** rather than more colors or more decorative stickers.

## Hard display/design constraints

- **Screen:** GC9A01 **240×240** 16-bit RGB565, round **Ø32.4 mm** active area; current printed front bezel exposes **Ø31.4 mm**. Hardware is unchanged by this concept-only branch.
- Each concept displays full-size round-screen coordinates (enlarged in the gallery for inspection). **The gallery is not a rendering of the current firmware.**
- At physical size, most sub-2-pixel details will be lost. The chosen direction must survive **240×240, downscaled preview ~80 pixels, and the real approximately 31 mm screen**.
- A static SVG should be treated as a **character/art direction guide**, never a firmware-compatibility or speed claim. Avoid unsupported effects: no heavy transparency, shader-like glow, unsupported fonts or oversized sprite memory without benchmarking.
- **Do not automatically replace working C++ code** until the owner chooses the personality and verifies actual art at screen scale.
- Prior art from the Instagram Reels (e.g. Taby's restricted face assets) is inspiration only. No third-party animation asset is copied.

## What will create actual "soul" in the implemented firmware?

1. **Persistent shape language:** unique eye proportions, blink shape, cheek asymmetry, one signature imperfection. Emotion isn't a recolor.
2. **Timing and anticipation:** gentle spontaneous glances, half-blinks, micro-squint before waking, eyes widening **before** the surprised mouth; no repetitive clockwork 4.3-second blink.
3. **Context and memory:** a resting personality, tiredness after inactivity, a distinct hello after USB reconnect, reactions to the optional MPU-6050 motion event.
4. **Legible expressions:** at least idle, delighted, skeptical, worried, sleepy, curious; distinguish by eye shapes and head/gaze, not just mouth.
5. **Hardware-level verification:** produce an honest `240x240` rendered framebuffer per state from **the exact drawing logic**, compare against the approved illustrations, measure device SPI redraw time, visual flicker and responsiveness. CI compiling is not a visual acceptance test.
6. **Emotional restraint:** no scrolling labels, dashboard rectangles or rainbow UI elements on the character's face. Give the character room to feel alive.

## Design-review gates

- [x] Old generic art rejected; branch contains 3 alternatives × 3 states.
- [ ] **Owner chooses one direction or requests another**. No unreviewed `main` merge for aesthetic work.
- [ ] Refine selected character sheet to all six protocol expressions; include neutral, happy, sad, sleepy, surprised, thinking.
- [ ] Create a sprite/font-free **original** embedded renderer, or a documented pre-rendered sprite asset pipeline that fits ESP32-S3 resources.
- [ ] Add deterministic preview rendering test to CI so the published SVG and actual firmware do not drift.
- [ ] Add interactions: variable blink interval, gaze, curiosity, touch/IMU (if supported), smooth changes with bounded frame budget.
- [ ] Test on real GC9A01, photograph at normal desk distance, benchmark redraw latency and verify black-level/contrast.
- [ ] Verify case art geometry stays truthful (current 31.4 mm aperture vs 72 mm body).

**For more visual detail without firmware porting compromises:** compare the [Taby 1.32-inch round AMOLED](hardware-options.md) separately. It offers more pixels and creator-developed animation but uses **different firmware, hardware and likely its own asset license**.

Current firmware protocol and physical build instructions remain unchanged until a direction is selected.
