# Panel bench bring-up log

Status, 2026-11-04: panel choice and bench plan remain on hold; no first light is recorded for this Good Display proposal. This is the historical evidence log for the Good Display proposal, not the current hardware verdict. See the [product brief](../product-brief.md).

## 2026-11-13 USB CDC throughput (slice 0) — incomplete

Status: **not measured**. The first physical attempt used the PR #31 benchmark
at Git commit `071c14c`, on an M4 MacBook Pro connected to the Waveshare
RP2040-Touch-LCD-1.69 running MicroPython 1.22.2. Serial port observed:
`/dev/cu.usbmodem101` (not guaranteed stable across reconnects).

- Verified pre-test: 16-byte payload, `show=0`, device replied
  `OK 345230767 87024`; host CRC32 check passed; free heap reported: **87,024 B**.
- Full four-configuration test started but terminated by the host's external
  **480-second timeout**. **Zero usable full-configuration result lines** were
  recorded; throughput, display overhead and p95 are **not measured**.
- Additional 28,800-byte transfer: host wrote 28,814 bytes including header,
  but received repeated `U` characters from the REPL rather than a valid `OK`;
  CRC verification failed. No 28,800-byte throughput figure is established.
- Diagnostic REPL reboot showed `bench ready; free heap: 87424` followed by
  `ValueError: need more than 0 values to unpack` at `main.py` line 35; a
  later Ctrl+C produced `KeyboardInterrupt`.
- Restored the previously backed-up device-side `main.py`; `cmp` verified the
  restored copy byte-for-byte; board reset and blink resumed normally.

**Not tested / not passed:** sustained 28,800-byte and 134,400-byte transfers,
`show=1` performance, four-by-100-frame run, fast-mode stall recovery, safe-mode
recovery, USB cable pull while sending, physical partial-region refresh, and
Buddy OS streaming/leased-frame operation. **No architecture decision** follows
from this attempt. Corrected benchmark proposed on draft PR #32; hardware run
pending separate approval and observation.

## 2026-11-12 Waveshare board: first load (current hardware)

MicroPython 1.22.2 installed; the vendor driver and `firmware/rp2040/main.py` were loaded. Session results (free heap, orientation, colour, flicker, tearing, SPI rate) are not recorded yet. This is the ordered bench prototype, separate from the paused Good Display proposal below.

## 2026-11-01 Good Display proposal

Paused [bench plan](../superpowers/plans/2026-11-01-panel-bench-bringup.md). Later entries supersede earlier proposals in this log; prices and stock below are dated observations, not current quotes.

## 2026-11-01 Task 1: datasheet re-read (no hardware)

Sources read:
- Good Display spec `GDOJ0269C01-T_Specification.pdf` (30 pp, https://www.e-paper-display.com/GDOJ0269C01-T_Specification.pdf). Pages cited as "spec p.N".
- SG Micro `SGM3838.pdf` (JULY 2022, https://sg-micro.com/rect/assets/d770a6dd-25df-4b57-b99c-845ac608298e/SGM3838.pdf).
- NOT read: RM69700 datasheet. The URL `e-paper-display.com/RM69700_Datasheet.pdf` returns 404. The only public copy found is on archive.org, marked Raydium NDA and for a 1600x2560 part, so it is not used. Plan items citing "RM69700 pp. 13, 117-119" are therefore NOT re-verified; the panel spec p.18-19 gives the same sequence timing (below).

### Rails (spec p.6 Table 4.1)

| Rail | Min | Typ | Max | Panel pins |
|---|---|---|---|---|
| Logic (VDDIO) | 1.62 | 1.8 | 1.98 V | 16 |
| VCI | 2.7 | 3.0 | 3.6 V | 18 |
| ELVDD | 4.6 | 4.6 | 4.6 V | 4, 6 |
| ELVSS | -3.0 | -2.0 | -1.4 V (100 mV step) | 8, 10 |
| AVDD | 6.8 | 6.8 | 7.8 V | 12 |

Logic current 20 / 23 / 26 mA. Abs max (p.6 Table 3.1): VDDIO, VCI 6.6 V; ELVDD min 4.6; ELVSS min -3 V.

**Correction to the plan:** it labels the rails "AVDD +4.6, AVEE -2.0, ELVDD/VCI +6.8". The spec says ELVDD = +4.6, ELVSS = -2.0, AVDD = +6.8, VCI = 3.0. There is no AVEE. Use the spec names.

### Pin map (spec p.9 Table 6.1, 30 pins)

| # | Name | # | Name |
|---|---|---|---|
| 1 | NC | 2 | GND |
| 3 | NC | 4 | ELVDD |
| 5 | NC | 6 | ELVDD |
| 7 | NC | 8 | ELVSS |
| 9 | GND | 10 | ELVSS |
| 11 | D1N | 12 | AVDD |
| 13 | D1P | 14 | GND |
| 15 | GND | 16 | VDDIO |
| 17 | CLKN | 18 | VCI |
| 19 | CLKP | 20 | GND |
| 21 | GND | 22 | SWIRE |
| 23 | D0N | 24 | OLED_EN |
| 25 | D0P | 26 | ERR_FG |
| 27 | GND | 28 | TE |
| 29 | MTP_PWR | 30 | RESX |

SWIRE = 22, OLED_EN = 24, RESX = 30, TE = 28, ERR_FG = 26, MTP_PWR = 29. The spec gives no function text for OLED_EN, ERR_FG, MTP_PWR (OPEN).

### Power sequence (spec p.18 Figure 8.1, p.19 Table 8.1)

On: VDDI up, then VCI up (TON2 >= 2 ms) -> RESX low >= 1 ms (T3) -> RESX high -> OTP reload >= 10 ms (T4) -> command execution / initial code, T6 >= 0 ms from last init code to SLPOUT -> SLPOUT; AVDD_EN rises at SLPOUT -> power-up sequence ~96 ms (T7 typ) -> DISPON after >= 2 frames (T9, VS ~16 ms) -> SWIRE pulse burst after DISPON. MIPI must be LP-11 for >= 1 ms (T2) before reset release.
Off: DISPOFF -> >= 2 VS (T10) -> SLPIN -> >= 1 VS (T11) -> RESX low >= 1 ms (T12) -> VCI off -> >= 2 ms (T13) -> VDDI off.

**Not in the figure:** when ELVDD/ELVSS come up and what OLED_EN does. Plan's "RESX to Sleep-Out > 120 ms" is not on p.18-19; the spec only shows T4 >= 10 ms, so 120 ms stays as the conservative choice (RM69700 datasheet not verified).

### Power source decision (SGM3838, WLCSP 2.5x2.5 mm)

| Panel rail | SGM3838 | Default | Setting |
|---|---|---|---|
| ELVDD 4.6 | VO1 | 4.6 V | none (0 pulses) |
| ELVSS -2.0 | VO2 | -3.0 V | 41 rising edges (Table 2) |
| AVDD 6.8 | VO3 | 7.3 V | 67 edges for 6.8 V, or default 7.3 V is inside 6.8-7.8 V |

Notes:
- VO3 (AVDD) has its own enable pin VO3_EN; SWIRE enables VO1/VO2. Panel's AVDD_EN maps to VO3_EN.
- SWIRE timing: tINIT 350-450 us, tHIGH/tLOW 2-20 us (10 typ), tSTORE 35-80 us, tOFF 35-80 us. Settings are volatile and reset by SWIRE low >= tOFF, so re-send after every power-up.
- Default -3.0 V sits at the panel's absolute limit; always send the 41-edge command before the panel is attached.
- On the panel, SWIRE is pin 22 and Figure 8.1 shows it pulsing after DISPON, so the panel IC likely drives it. On the bench with the panel unplugged the MCU drives it. Whether panel SWIRE is an output is OPEN; confirm before connecting SWIRE to the PMIC.
- Logic rails: 1.8 V and 3.0 V from bench supply (or LDOs) with current limit; no part chosen.

### Connector (OPEN)

- Spec p.9 names Molex 5052743040 as the recommended connector. Third-party listings (Gesight, Allicdata) agree and describe it as a 30-circuit 0.35 mm plug assembly.
- Molex series chart lists 5052743012 as 30-circuit SlimStack SSB RP plug, 0.80/0.90 mm mated height, 2.00 mm mated width.
- Both listed as plugs, so gender/height mating is unproven. molex.com was unreachable from this machine, so the sales drawings (`5052743012_sd.pdf`, `5052743040_sd.pdf`) were not read.

### Gate 1: NOT PASSED

Done: rails, sequence order and delays, pin map, SGM3838 pulse counts, all with page refs.
Open, needs the user:
1. Molex sales drawings for 5052743012 and 5052743040 (mating gender, height). Do not buy until compared.
2. OLED_EN / ERR_FG / MTP_PWR function and ELVDD/ELVSS enable timing: not in the panel spec; ask for the RM69700 datasheet pages or a photo of any pin-description page.
3. Whether panel SWIRE is an input or output.

## 2026-11-01 Panel choice: PAUSED, bring-up plan on hold

Priorities: thin + cheap. Do not buy anything until decided.
- Good Display GDOJ0269C01: 0.505 mm thick (spec p.5), about $35, 0 stock, 2-lane DSI, no public init: hardest to drive.
- 2.4" 450x600 RM690B0 panels (e.g. BOE240-450600): QSPI, much easier; bare-panel vendor, price and thickness NOT found.
- Waveshare ESP32-S3 Touch AMOLED 2.41 board: about $54 (SpotPear), works day one, too thick for the slab, thickness not found.
Next session: find a vendor and thickness for the bare 2.4" RM690B0 panel; then pick a panel; then resume this plan (Task 1 open items above) or drop it.
