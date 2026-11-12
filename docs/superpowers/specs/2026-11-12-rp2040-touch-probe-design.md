# RP2040 touch and frame-time probe (design)

Status: 2026-11-12. Bring-up only; the face is a temporary stand-in for the 3D model.

## Goal
Learn, on the real board, (1) whether the CST816D touch controller works and how its
coordinates map to the panel, and (2) what a blink redraw actually costs. Decide any
touch protocol or smoothing work from these numbers.

## Scope
- `firmware/rp2040/touch_probe.py`: one script run from Thonny. It uses the vendor
  `Touch_CST816D` class and prints, for 10 s each, point-mode `x, y` and gesture-mode codes,
  then times `show()` (existing `benchmark_display.measure_show`) and a full
  `main.draw()` for open and closed eyes.
- README: record the results in the status section.

## Out of scope
Touch events over USB (needs a new device-to-host message), partial redraws, easing,
gaze, any change to `main.py` or the protocol.

## Verification
No host unit test fits a hardware probe. Host check: `python3 -m py_compile` and the
existing suite stays green. Hardware check: user runs it with the board, quits Thonny
afterwards, and pastes the output; README is updated from it.

## Risks
- The vendor class attaches the IRQ handler that does I2C reads inside the interrupt; if
  that misbehaves, the probe will show it and the fix is a polled read, decided then.
- The class returns early from `__init__` when the chip is not detected; the probe checks
  for that instead of crashing.
