# Panel Bench Bring-up Plan

**PAUSED — status 2026-11-04.** Panel/controller selection is reopened. This candidate-specific plan is not authorization to buy, wire, flash, or resume bring-up. Read the [current product brief](../../product-brief.md) and [later corrections/open gates](../../hardware/bringup-log.md) first. The reset did not re-verify electrical specifications or complete any hardware gate.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox syntax. Hardware steps are done by the user; the agent prepares files and checks results.

**Goal:** First light of the Good Display GDOJ0269C01-T01 (RM69700, 800x600, 2-lane DSI) driven by an ESP32-P4, with no panel damage.

**Architecture:** Stage gates. Prove each rail on a current-limited bench supply with NO panel attached, then attach the panel, then DSI. A failed gate stops the plan. Firmware is a throwaway bring-up app, not the product firmware. Production board design waits until this finishes.

**Tech Stack:** M5Stack Stamp-P4 (ESP32-P4, 2-lane DSI), ESP-IDF (>= 5.4), SGM3838 PMIC breakout (candidate), Molex 30-pin 0.35 mm board-to-board, bench supply with current limit, multimeter, optional scope.

## Global Constraints

- Source of facts: `cad/slab/DECISIONS.md` "Round-3 research". Everything from the related i.MX RM69700 driver is UNVERIFIED for this panel.
- Panel rails (typical, corrected from the later bring-up log): VDDIO 1.8 V, VCI 3.0 V, ELVDD +4.6 V, ELVSS -2.0 V, AVDD +6.8 V. The old AVEE/ELVDD/VCI naming was wrong. Re-read the panel specification before any hardware work; do not rely on this plan's copy.
- RM69700 timing (datasheet pp. 117-119): RESX rising to Sleep-Out > 120 ms, T4 OTP reload >= 10 ms, T9/T10 >= 2 frames, T13 >= 2 ms off-interval.
- Start at 800x600 RGB888, 50 Hz, ~33.16 MHz pixel clock, porches HSA/HBP/HFP 128/88/40, VSA/VBP/VFP 4/8/16. Do not raise refresh rate or invent register values to fix a blank panel.
- Data boundary: nothing here is CoRe/TUAS data.
- Commits: conventional, no attribution lines, branch `feat/good-display-slab`, commit only when the user asks.

## Stop conditions (apply to every gate)

Unexpected rail voltage or current, wrong rail polarity, SWIRE signalling mismatch, persistent DSI packet errors, or an inability to confirm the power sequence from the datasheet. On stop: power off, write the finding into `docs/hardware/bringup-log.md`, do not continue.

## File Structure

- Create: `docs/hardware/bringup-log.md` (dated readings per gate; the evidence trail)
- Create: `firmware/bringup/` (ESP-IDF project: `main/main.c`, `main/rm69700_init.h`, `CMakeLists.txt`)
- Create: `tests/test_rm69700_init.py` (checks the init table in `rm69700_init.h` against the documented sequence)

---

### Task 1: Re-read the datasheets and freeze the pin map (no hardware)

**Files:**
- Create: `docs/hardware/bringup-log.md`

- [ ] **Step 1:** Download the Good Display GDOJ0269C01 spec and the RM69700 datasheet; read spec pp. 5-6 and 18-19 (rails, power diagram Figure 8.1) and RM69700 pp. 13, 117-119. Record in the log: each rail's min/typ/max, sequence order and delays, the 30 pin names with pin numbers, and which pins are SWIRE, OLED_EN, RESX, TE.
- [ ] **Step 2:** Compare the pin table with Molex 5052743012 vs 5052743040 (Molex drawings). Record the mating match or mismatch. If it mismatches, stop and pick a mating part before buying.
- [ ] **Step 3:** Decide the power source for each rail: SGM3838 for AVDD/AVEE/ELVDD, a 1.8 V and 3.0 V LDO or the bench supply for the logic rails. Record the SGM3838 SWIRE pulse-count settings needed to hit -2.0 V and +6.8 V (SGM3838 datasheet) in the log.
- [ ] **Gate 1:** every rail, the power sequence order, the connector match and the SWIRE settings are written down with page references. If the Figure 8.1 timing values can't be read, ask the user to photograph that page. Do not proceed on a guess.

### Task 2: Power breakout, panel NOT attached

**Files:**
- Modify: `docs/hardware/bringup-log.md`

- [ ] **Step 1:** Build or buy the PMIC breakout (SGM3838 EVKIT layout is the starting point). Set the bench supply to 3.3 V with a 100 mA limit.
- [ ] **Step 2:** Power up with the panel connector unloaded. Measure each rail at the connector pins with the multimeter. Log voltage and supply current.
- [ ] **Step 3:** Drive SWIRE per the SGM3838 datasheet, re-measure. AVEE must be negative and near -2.0 V; ELVDD near +6.8 V.
- [ ] **Step 4:** Add a dummy load (about 1 kOhm per rail) and re-measure to check regulation.
- [ ] **Gate 2:** all five rails within the panel's min/max, correct polarity, supply current within the PMIC idle spec. Power off.

### Task 3: Init-table test and firmware skeleton

**Files:**
- Create: `firmware/bringup/main/rm69700_init.h`
- Create: `tests/test_rm69700_init.py`

- [ ] **Step 1: Write the failing test** `tests/test_rm69700_init.py`:

```python
import re
from pathlib import Path

H = Path(__file__).parent.parent / "firmware/bringup/main/rm69700_init.h"

# Vendor sequence from the related i.MX driver (UNVERIFIED for GDOJ), generic writes.
EXPECTED_GEN = [(0xFE, 0x40), (0x24, 0x50), (0x47, 0x13), (0xFE, 0x50),
                (0xC0, 0x20), (0xFE, 0x60), (0x95, 0xCE), (0xFE, 0x00)]


def test_vendor_pairs_present_in_order():
    pairs = re.findall(r"GEN\(0x([0-9A-Fa-f]{2}),\s*0x([0-9A-Fa-f]{2})\)", H.read_text())
    assert [(int(a, 16), int(b, 16)) for a, b in pairs[:8]] == EXPECTED_GEN


def test_sleep_out_delay_is_datasheet_not_driver():
    text = H.read_text()
    assert "#define SLEEP_OUT_AFTER_RESET_MS 120" in text
```

- [ ] **Step 2: Run it, expect FAIL** (`rm69700_init.h` missing): `python -m unittest discover -s tests -q` is the repo runner, but these are pytest-style functions, so run `python -c "import tests.test_rm69700_init as t; t.test_vendor_pairs_present_in_order()"`. Expected: FileNotFoundError.
- [ ] **Step 3: Create `firmware/bringup/main/rm69700_init.h`:**

```c
// Related i.MX Linux driver flow. UNVERIFIED for GDOJ0269C01. GEN = generic DSI write (0x23), DCS = DCS write.
#define SLEEP_OUT_AFTER_RESET_MS 120   // datasheet p.117; the driver's shorter delay conflicts with it
#define GEN(reg, val) { 0, reg, val }
#define DCS(reg, val) { 1, reg, val }
static const struct { int dcs; unsigned char reg, val; } rm69700_init[] = {
    GEN(0xFE, 0x40), GEN(0x24, 0x50), GEN(0x47, 0x13), GEN(0xFE, 0x50),
    GEN(0xC0, 0x20), GEN(0xFE, 0x60), GEN(0x95, 0xCE), GEN(0xFE, 0x00),
    GEN(0xC2, 0x0B),   // video mode
    DCS(0x35, 0x00),   // TE on V-blank
    DCS(0x3A, 0x77),   // RGB888
};
// Then: DCS 0x11 (sleep out), wait, GEN(0x53,0x20), GEN(0x55,0x00), GEN(0x36,0x82), wait >= 2 frames, DCS 0x29 (display on).
```

- [ ] **Step 4:** The second test needs the define above; the first needs the 8 vendor pairs in order. Both are satisfied by Step 3. Run the check from Step 2. Expected: no exception for both functions.
- [ ] **Gate 3:** both checks pass.

### Task 4: DSI host without the panel, then with it

**Files:**
- Create: `firmware/bringup/main/main.c`, `firmware/bringup/CMakeLists.txt`
- Modify: `docs/hardware/bringup-log.md`

- [ ] **Step 1:** Look up the current ESP-IDF API with the `docs` MCP before writing code: `esp_lcd_new_dsi_bus`, `esp_lcd_new_panel_io_dbi`, `esp_lcd_new_panel_dpi` (fields `dpi_clock_freq_mhz`, `pixel_format`, `video_timing`) and the generic-write primitive. Note the known trap: `esp_lcd_panel_io_tx_param()` on DSI issues DCS writes; the vendor `GEN` writes need the lower-level generic-packet path (DSI HAL). If no public generic-write entry exists in the installed IDF version, record that and use the HAL primitive directly.
- [ ] **Step 2:** Write `main.c`: power GPIOs low (panel off) -> start DSI bus (2 lanes, lane bit rate from the Stamp-P4 limits, 1.5 Gbit/s max) -> DPI panel config with the Global Constraints timing -> only then, after user confirmation, the rail enable and reset sequence from Task 1. Fill the framebuffer with a solid red, then green, then blue frame, one second each.
- [ ] **Step 3:** With the panel still unplugged, flash and run. Check on the scope or logic analyser that the clock lane toggles in HS mode and that data lane activity matches the programmed timing. Log it.
- [ ] **Step 4 (user, power off):** Attach the panel connector, supply limit 150 mA at 3.3 V. Power on rails per Task 1's sequence. Log the rail voltages again with the panel attached (rails may droop).
- [ ] **Step 5:** Send reset and the init sequence, sleep out, display on. Expect red/green/blue fills.
- [ ] **Gate 4:** three solid colours at full area, no flicker, no current runaway. If blank: stop and log; check rails, reset timing, TE and lane count in that order, one change at a time. Do not change refresh rate.

### Task 5: Characterise and record

**Files:**
- Modify: `docs/hardware/bringup-log.md`, `cad/slab/DECISIONS.md`

- [ ] **Step 1:** Show a 800x600 test pattern (corner marks, gradient, 1 px grid). Check geometry (visible area 54.6 x 40.95 mm), uniformity and blacks.
- [ ] **Step 2:** Try 60 Hz (40 MHz pixel clock) only after 50 Hz is stable. Record the result either way.
- [ ] **Step 3:** Measure total current for a black screen, a white screen and a typical face. Compare with the USB 2.0 500 mA budget.
- [ ] **Step 4:** Update `DECISIONS.md`: replace "UNVERIFIED" with the confirmed init sequence, timing, rails and power-chip identity, and list what stays open (thin controller stack, connector choice for the production board).
- [ ] **Gate 5:** confirmed init sequence and rail table recorded. Only now plan the production controller board and the screen-part stack.

## Self-review

- Coverage: panel power sequence (Tasks 1-2), init and ESP-IDF generic-write trap (3-4), 50 vs 60 Hz and current (5), stop rules (top). The production board is deliberately out of scope.
- Known gap: the exact ESP-IDF generic-write API is not pinned here; Task 4 Step 1 requires looking it up instead of guessing.
