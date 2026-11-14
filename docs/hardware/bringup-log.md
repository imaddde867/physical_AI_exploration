# Panel bench bring-up log

Status, 2026-11-04: panel choice and bench plan remain on hold; no first light is recorded for this Good Display proposal. This is the historical evidence log for the Good Display proposal, not the current hardware verdict. See the [product brief](../product-brief.md).

## 2026-11-14 Recovery probe and cable pull on the 16 MiB build — measured

Both on the 1.29.0 / 16 MiB build from the entry below, with the benchmark
installed as `main.py` and the blink restored afterwards (sha256 `f3931442...`,
byte-identical to the backup).

**Safe-mode partial-frame recovery: PASS.** A 17-byte partial frame stalled, the
receiver resynchronized, and the next frame completed CRC-valid in 8.3 ms with
76,240 B free (1.22.2: 7.8 ms, 75,776 B). The preceding smoke run passed at
8.33 ms, heap 81,200 B.

**Cable pull: the host fails fast and the board recovers without reflashing.**
400 frames of 134,400 B were requested; the cable came out around frame 334.
The host recorded `status: incomplete`, `expected_frames: 400`,
`attempted_frames: 334`, `completed_frames: 333`, `failures: 1`,
`recovered: False`, `error: '[Errno 6] Device not configured'`, then
`STOP. Do not reuse the port until the receiver state is checked.` and exit 2.
No `BENCH 0 0` was sent, as designed, and the partial numbers were still saved
(114.88 KB/s to that point, heap floor 560 B).

After replugging: `machine.reset_cause()` was 1 (PWRON_RESET, a real power cycle
rather than a soft reset), the port came back as the same
`/dev/cu.usbmodem101`, and recovery took no reflash — smoke PASS at 8.33 ms,
then one 28,800 B frame in 255.95 ms (112.52 KB/s, heap 74,528 B).

**Two method notes.** First, a `/dev/cu.usbmodem*` node can outlive the unplug on
macOS: a once-per-second presence monitor logged no transition at all while the
host was getting Errno 6, so a surviving device node is not evidence the cable
is connected, and the host error plus `PWRON_RESET` are the real evidence.
Second, `mpremote exec` leaves the board at the REPL, so an immediately following
`--smoke` reads its own `SYNC` back as an echo and exits 2 with
`unexpected startup reply`; reset before each invocation. That was a harness
sequencing mistake, not a board fault — the clean rerun passed.

## 2026-11-14 16 MiB build: flashed, storage and throughput re-measured — measured

Follows the flash-space check below, with user approval. Order was: back up,
verify, flash, restore, re-baseline. Board, port and cable unchanged.

**Backup, verified.** All eight device files went to
`.local-archive/device-backup-2026-11-14/` (git-ignored) and were hashed on both
sides — `hashlib.sha256` on the device, `shasum -a 256` on the Mac — with all
eight matching. `main.py` was `f3931442b87e...`, the same hash this log records
for the blink, so the backup is the state that was actually running.

**Flash.** `WAVESHARE_RP2040_PLUS-FLASH_16M-20260824-v1.29.0.uf2`, sha256
`654744919132d80f8095db8a5f5a641a8966d685f818dc66df0e14cdd7d2c1ba`, 676,864 B,
1,322 UF2 blocks, embedded board string `Waveshare RP2040-Plus 16MB with RP2040`,
highest address written `0x10052A00` (the image stays under 2 MB; it is the
*storage layout* that grows). Entered bootloader with `mpremote ... bootloader`.
The volume is `/Volumes/RPI-RP2`; its first `ls` returned `Permission denied`
while the volume was still mounting, then writes succeeded. The board rebooted
and re-enumerated on the same `/dev/cu.usbmodem101`.

**Filesystem.** `os.statvfs('/')` = 3840 x 4096 = **15,728,640 B**, exactly the
variant's `MICROPY_HW_FLASH_STORAGE_BYTES`. Fresh flash: 15,720,448 B free. After
restoring all eight files: 221,184 B used, 15,507,456 B free — room for 115 raw
134,400 B frames against nine before.

**Restored firmware runs.** `blink ready; free heap: 78768 bytes`, eyes drawn
normally. That is 7,632 B less headroom than the 86,400 B recorded on 1.22.2 with
the same driver loaded, so the newer runtime costs memory.

**Throughput re-measured**, 400 frames, 0 failures, host exit 0, JSON
`complete: true` and `device_stopped: true` (KB = 1000 bytes):

| payload | show | KB/s | ms mean | ms p95 | heap_min |
|---|---|---|---|---|---|
| 28,800 | 0 | 112.31 | 256.4 | 264.4 | 768 |
| 28,800 | 1 | 92.53 | 311.2 | 320.1 | 1,408 |
| 134,400 | 0 | 114.87 | 1170.0 | 1177.4 | 64 |
| 134,400 | 1 | 109.73 | 1224.8 | 1232.0 | 448 |

Pre-suite single 28,800 B fast frame: 255.9 ms, 112.56 KB/s, heap 74,528. Smoke:
8.32 ms, heap 81,200 (1.22.2: 7.8 ms, 80,768). JSON and transcript in
`.local-archive/usb-benchmark-16m-v1.29.0.{json,log}`.

**The USB receive path is unchanged.** 112.3 and 114.9 KB/s against 112.2 and
114.5, so the < 150 KB/s branch and its decision still stand. The heap floor is
also unchanged in character: 768 / 1,408 / 64 / 448 B, still thin and still
unexplained.

**Display refresh regressed, and the peripheral clock is the cause.** `show()`
alone now measures **55.44 ms mean, 56.3 p95, 66.8 max, 18.04 fps** (1.22.2:
23.2 ms mean, 43 fps). `benchmark_display.py` reports the bus as
`SPI(1, baudrate=24000000, ...)` although the driver requests 100 MHz; 134,400 B
at 24 MHz is 44.8 ms on its own, which accounts for the difference.
`machine.freq()` is 125 MHz and raising it to 133 MHz did not change the SPI
object; `machine` exposes only `freq` and `rp2` exposes no clock setter. The old
23.2 ms implies about 62.5 MHz on 1.22.2, but the SPI object was not printed
then, so that rate is inferred rather than measured.

Consequence: `show=1` minus `show=0` is 54.8 ms at both payload sizes, matching
the standalone figure. At 12 FPS an 83.3 ms frame budget leaves about 28 ms for
flash read plus decode, and 18 fps is the hard ceiling without a faster SPI path.

**Not measured here, but measured next** in the entry above: the safe-mode
recovery probe and a mid-frame cable pull, both run after this suite. Still
unmeasured: anything beyond 400 frames, and the 24 MHz SPI cause is diagnosed
but not fixed. Options for the SPI rate — a custom build raising clk_peri, a PIO
SPI path, or accepting 24 MHz — are considered and **not chosen** here.

## 2026-11-14 Flash space: filesystem measured, 16 MiB build available — checked

Prompted by the storage question in the character-frame entry below. The board
is advertised with 16 MB flash, yet MicroPython reported 1.40 MB free. Measured
read-only over `mpremote` on `/dev/cu.usbmodem101`, no firmware change:

- Build is the stock Pico target: `v1.22.2 on 2024-02-22`, `machine`
  `Raspberry Pi Pico with RP2040`. That target maps 2 MB of flash, so 14 MB of
  the chip is unused.
- `os.statvfs('/')` = `(4096, 4096, 352, 298, ...)`: **1,441,792 B total**
  (352 x 4096), **1,220,608 B free** (298 blocks), 221,184 B used.
- Free heap at a bare REPL was 228,688 B; the 72-87 KB figures elsewhere in this
  log were measured with the LCD driver loaded, so they are not comparable.

**Correction:** this log's earlier "reported 1.40 MB free flash" is the *total*
filesystem size, not free space. Usable headroom is 1.16 MiB, which holds nine
raw 134,400 B frames.

**16 MiB build exists prebuilt.** MicroPython publishes a
`WAVESHARE_RP2040_PLUS-FLASH_16M-<date>-<version>.uf2` alongside that board's
normal build (https://micropython.org/download/WAVESHARE_RP2040_PLUS/). Its
`mpconfigvariant_FLASH_16M.cmake` sets `MICROPY_HW_FLASH_STORAGE_BYTES` =
15,728,640 B (15 MiB, one 1 MiB block reserved). On the download page the 16 MiB
variant starts at v1.28.0; there is no 1.22.2 build of it. There is no
MicroPython board target for the RP2040-Touch-LCD-1.69 itself, and none is
needed: `firmware/rp2040/main.py` imports no `machine` symbol, and the vendor LCD
driver takes explicit pins, so any RP2040 build runs the same code.

**Done later the same day** — the backup, flash and re-measurement are in the
entry above. Two caveats still govern the older numbers in this log: the 112 KB/s
baselines were measured on 1.22.2, and the chip's 16 MB capacity rests on the
Waveshare specification rather than on a JEDEC ID read from this board.

**What this changes:** at 12 FPS, an eight-second raw clip is 96 x 134,400 B =
12,902,400 B and fits in 15 MiB with room to spare; at 30 FPS it does not. Clip
*size* stops being the binding constraint at 12 FPS, and flash-read plus decode
throughput becomes the one to measure.

## 2026-11-14 Character frame: first full-resolution display — passed

Rendered the saved `ANCHORED | watch` character in Blender and displayed one
frame on the Waveshare RP2040-Touch-LCD-1.69. The user approved the closer
`CAM | Window close-up` framing at 65 mm and the `Standard` view transform;
these scene settings were saved in `animation/crying-head-2-anchored.blend`.

- Blender rendered 240 × 280 PNG to `/tmp/watch-final.png`; converted it to
  big-endian RGB565 at `/tmp/watch-final.rgb565` (134,400 bytes).
- The frame displayed correctly using Thonny and the existing LCD driver. The
  test streams one 480-byte row at a time into the driver's existing full-screen
  framebuffer, avoiding a second 134,400-byte allocation.
- A red/green/blue/white bar check displayed the four colors in the right order.
  Backlight duty 8192 (12.5%) preserves the preferred dark background;
  increasing it to 32768 made little visible difference and lifted the blacks.
- An earlier 120 × 140 attempt failed when it allocated an extra 33,600-byte
  image buffer. Reuse the LCD framebuffer and stream rows instead.

**Status:** one static frame is verified on hardware. Animation playback,
compressed clip size, sustained timing, and a Mac command selecting a clip are
still open. The 134,400-byte frame demonstrates that full-resolution raw frame
sequences cannot fit in the board's 1.40 MB filesystem (1.16 MB free, measured —
see the flash-space entry above) for an eight-second 30 FPS animation. Next:
prototype compact encoding and on-device decode/playback, then measure frame
cadence and stability before implementing clip commands.

## 2026-11-14 Fast-mode stall completion (host-side fix) — measured

Host: merged `main` (`861f82f`), MicroPython 1.22.2, same board, port and cable.
Firmware: `firmware/rp2040/bench_usb.py` copied temporarily to `:main.py`; the
blink firmware was restored afterwards and compared byte-identical to the backup
(`f3931442...`). Baseline in the same session, before the probe: one 28,800 B
fast frame at 112.5 KB/s, free heap 72,288 B.

Probe (`stall-recovery-2026-11-14.py`): `SYNC`, `BENCH 0 28800 0 F`, write 300 of
28,800 bytes, wait 1 s. The device produced **no output for that second**, i.e. it
was blocked inside `readinto()`, which is the pre-fix failure mode. The host then
wrote 28,500 filler bytes plus a newline; the frame is discarded, not counted:

- `complete_stalled_frame` returned true after **257 ms**, including the `OK` for
  the padded frame and a fresh `SYNC` / `SYNCED`.
- A fresh 16 B safe-mode frame passed in 7.9 ms (CRC matched).
- A fresh 28,800 B fast frame passed at **112.6 KB/s** (CRC matched), within the
  recorded baseline range of 112.2-112.6 KB/s.
- `BENCH 0 0` teardown was acknowledged with `STOPPED`.

**Not measured:** a device-side 200 ms timeout *inside* a fast-mode slice (the
device cannot author one while blocked in `readinto()`), and recovery after the
host process itself dies mid-frame. Both still need a nonblocking native receive
path or a verified watchdog, which is the slice 0 architecture decision.

Evidence: `~/Desktop/macdesk-buddy-usb-2026-11-13/stall-recovery-2026-11-14.{py,log}`,
`stall-baseline-28800.log`, `stall-smoke.{json,log}`.

## 2026-11-14 USB CDC throughput (slice 0) — measured

Benchmark commit `6355c0d`, MicroPython 1.22.2, Waveshare RP2040-Touch-LCD-1.69,
M4 MacBook Pro, `/dev/cu.usbmodem101`. Two full runs of four configurations, 100
frames each, 800 frames total, **0 failures**. Each run ended with a confirmed
`STOPPED` acknowledgement, so `BENCH 0 0` teardown works on hardware.

Fast mode (`F`), KB = 1000 bytes, second column is the repeat run:

| payload | show | KB/s run 1 / run 2 | avg KB/s | ms mean run 1 / run 2 | ms p95 |
|---|---|---|---|---|---|
| 28,800 | 0 | 112.2 / 112.2 | 112.2 | 256.7 / 256.6 | 266.6 |
| 28,800 | 1 | 103.3 / 103.2 | 103.2 | 278.9 / 279.1 | 288.6 |
| 134,400 | 0 | 114.5 / 114.5 | 114.5 | 1174.3 / 1173.8 | 1181.8 |
| 134,400 | 1 | 112.3 / 112.3 | 112.3 | 1197.0 / 1196.4 | 1203.6 |

Run-to-run spread is at most 0.1% on throughput and at most 0.6 ms on mean
latency; `ms p95` was recorded once per configuration, so it carries no
run-to-run comparison. The numbers are repeatable, not a lucky pass.

**Decision: all four configurations land below 150 KB/s — "MicroPython CDC receive
path bottleneck".** Throughput is flat across payload size (112.2 / 103.2 / 114.5 /
112.3 KB/s), so the cost is per byte, not per frame: chunk tuning cannot reach the
500 KB/s full-region threshold. Ceiling at this rate: about 3.8 fps for a 120x120
region (28,800 B) and about 0.85 fps for a full 134,400 B frame. The spec's `< 150`
branch applies: add a C/viper receive path, or stay device-side with clips in flash.

Two side readings:

- `lcd.show()` costs a flat ~22 ms per frame regardless of payload (256.7 -> 278.9
  ms, 1174.3 -> 1197.0 ms). Display refresh is not the bottleneck.
- Free heap started near 85 KB and bottomed out at **176-1104 B** within each
  100-frame run (`heap_min`: 320/336, 1056/176, 448/848, 272/1104). The runs
  completed, so GC kept up, but that floor is thin and unexplained; measure it
  before running anything longer than 100 frames per configuration.

Smoke: 16-byte CRC frame passed with a confirmed `STOPPED` (`complete: true`,
`device_stopped: true`), free heap 80,768 B. Safe-mode recovery probe
(`--recovery-test`) passed on hardware: 17-byte partial frame stalled,
resynchronized, then a CRC-valid 16-byte frame at 7.8 ms, 75,776 B free.

**Cable pull, measured (2026-11-14).** Unplugged during a 200-frame, 134,400-byte
fast-mode run, at frame 5. The host failed fast with `[Errno 6] Device not
configured` and kept the four completed frames plus `failures: 1` in
`cablepull-6355c0d.json` with `complete: false`, `device_stopped: false`. Before
fix `039843e` it also printed a `termios.error` traceback and exited 1 instead of
2; that is fixed and pinned by `test_close_survives_a_cable_pull`. After replug
(same port name, no reflash, no second replug) a 16-byte smoke passed with
`STOPPED`, then one 28,800-byte fast-mode frame passed at 112.6 KB/s - within
0.4% of the pre-pull average. Each later invocation needs the documented
`mpremote connect "$PORT" reset`, because `STOPPED` leaves the board at the REPL.

**Not measured / not passed:** fast-mode stall recovery on a truncated 256-byte
read (the pull proved power-cycle recovery, not in-place stall recovery), real
partial-region refresh (only whole-screen `lcd.show()` was exercised), and
sustained runs longer than 100 frames per configuration.

Artifacts kept outside the repo, in the 2026-11-13 backup folder:
`full-6355c0d.json`, `full-6355c0d-run2.json`, `smoke-6355c0d.json`,
`cablepull-6355c0d.json`, `cablepull-recovery-6355c0d.json`,
`cablepull-recovery-28800.json`.

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
