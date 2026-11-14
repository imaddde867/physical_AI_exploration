# RP2040 USB CDC benchmark: safe experiment protocol

Status: **measured on hardware, 2026-11-14; two repeat runs agree within 0.1%**.
Source: PR #31 created the first version. This revision fixes header crashes, adds
frame synchronization and bounded host writes, and adds a separate recovery probe.
The original spec's `BENCH 0 0` ends each successful invocation with a `STOPPED` acknowledgment after board cleanup.
MicroPython version on the user's board: **1.22.2**. Board:
**Waveshare RP2040-Touch-LCD-1.69**. Mac: **M4 MacBook Pro**. Results, decision and
what remains unmeasured: [bring-up log](bringup-log.md), section 2026-11-14.

## Why two receive modes?

MicroPython 1.22.2 implements `sys.stdin.buffer.readinto(n)` by waiting for
*all* `n` bytes. Calling `select.poll()` first only guarantees that **some**
data is ready. This is visible in MicroPython's
`shared/runtime/sys_stdio_mphal.c` (`stdio_buffer_read`). The original
`readinto(framebuffer[:n])` could block forever if the sender stopped mid-frame.

- **F (fast)**: 256-byte `readinto()` slices, with a single 200 ms poll between
  slices. Measures a practical Python/C USB receive path. **Does not guarantee
  recovery if the host stops halfway through a slice.** On a fast-mode timeout
  or unplug, stop, power-cycle if needed, and restore/restart deliberately.
- **S (safe)**: polls before every 1-byte read, ensuring the read itself cannot
  wait for more than one already-available byte. On a 200 ms gap, reports
  `ERR <session> <seq> stall <count>` and requires a fresh `SYNC`. Its per-byte
  overhead is intentionally **not comparable to the fast throughput mode**.

Neither mode implements Buddy OS leased-frame expiry or local-face fallback.
This is **benchmark code only**, not production display firmware.

## Prepare and preserve working firmware

Run from the repo root on macOS. Close Thonny and all other serial clients.
Use the **currently detected** port (do not assume it stays `101`).

```sh
export PORT=/dev/cu.usbmodem101
export BACKUP="$HOME/Desktop/macdesk-buddy-usb-2026-11-13"
mkdir -p "$BACKUP"
mpremote connect "$PORT" fs cp :main.py "$BACKUP/main.py"
mpremote connect "$PORT" fs cp :protocol.py "$BACKUP/protocol.py"
mpremote connect "$PORT" fs cp :waveshare_lcd.py "$BACKUP/waveshare_lcd.py"
shasum -a 256 "$BACKUP/main.py"
```

Each successful invocation now shuts down the temporary benchmark by sending
`BENCH 0 0`, and waits for `STOPPED` after the backlight and interrupt settings
are cleaned up. **Reset the board before the next command**, for example with
`mpremote connect "$PORT" reset`; this intentionally reruns benchmark `main.py`.
The benchmark returns to MicroPython's REPL after a successful run.

**Never overwrite the backup with the temporary benchmark.** The backups made
on 2026-11-13 are already verified; reuse them if still present and intact.

After inspecting and approving this branch's changes, install the benchmark:

```sh
mpremote connect "$PORT" fs cp firmware/rp2040/bench_usb.py :main.py
mpremote connect "$PORT" reset
ls /dev/cu.usbmodem*
```

This replaces the board's `main.py` temporarily. A white/static display is
normal until a test refreshes it. The framebuffer bytes are arbitrary patterns.

## Run in stages, do not skip straight to 400 frames

Without a positional port, `python3 tools/bench_usb.py` discovers a single
`/dev/cu.usbmodem*` port or fails rather than guessing between multiple devices.
Prefer passing `"$PORT"` explicitly.

Each command runs the host's verified nonblocking writes with deadlines and
strict `SYNC` / `READY` / CRC-checked `OK` replies. It exits nonzero on failure
rather than continuing after a desynchronization. `F` and `S` are mutually
exclusive per frame; the board enters `F` only after sending `READY`.

```sh
# Initial 16-byte proof. Includes Ctrl+C (0x03) in the binary payload.
python3 tools/bench_usb.py "$PORT" --smoke
mpremote connect "$PORT" reset

# Only after smoke passes: one optimized large frame, no display refresh.
python3 tools/bench_usb.py "$PORT" --frames 1 --size 28800 --show 0
mpremote connect "$PORT" reset

# Only after both succeed: the original four 100-frame configurations.
python3 -u tools/bench_usb.py "$PORT" \
  --json-out "$BACKUP/usb-benchmark-results.json" \
  2>&1 | tee "$BACKUP/usb-benchmark-full-fixed.log"
```

The final command uses a pipe: if you need its exit status in zsh, use
`echo ${pipestatus[1]}` immediately afterward. **Do not treat a partial log as
success.** Do not unplug during the full benchmark.

Timing interpretation:

- `ms_mean`, `ms_p95`, `kb_s_mean`, `kb_s_p95_worst` measure from **after
  `READY`** to receipt of the CRC-checked `OK`: USB transmission, device read,
  optional full-screen `lcd.show()`, CRC calculation and acknowledgement.
- `cycle_ms_mean`, `cycle_ms_p95` additionally include the per-frame BENCH
  header and READY round-trip. Real Buddy OS framing may differ.
- `heap_min`, `heap_max` are the device's observed free heap during acknowledged
  frames, not necessarily the lowest instantaneous peak during receipt.
- A 28,800-byte payload modifies a prefix of the existing full framebuffer;
  `lcd.show()` still refreshes all 134,400 bytes. **Dirty-rectangle refresh has
  not been measured.** `show=1` minus `show=0` is an approximation affected by
  host/device scheduling and CRC costs.
- The design's 150/500 KB/s thresholds are provisional **candidacy screens**.
  Consider p95 frame latency, zero failures, refresh costs, and recovery as
  independent requirements. A reported decision is not approval to deploy
  streamed frames in Buddy OS.

## Separate controlled recovery probe (without unplugging)

**Run only after the normal smoke test passes.** This exercises mode `S`, not
mode `F`, and deliberately transmits only 17 bytes of a declared 1,024-byte
frame. It expects an error after 200 ms, sends a fresh `SYNC`, then validates a
new 16-byte CRC-protected frame:

```sh
mpremote connect "$PORT" reset  # if the previous benchmark completed
python3 tools/bench_usb.py "$PORT" --recovery-test
```

`SAFE recovery PASS` establishes only the bounded-read path on that physical
connection. It **does not** prove optimized fast-mode stall recovery. The latter
requires a nonblocking native CDC receive implementation or a separately
verified watchdog/reboot strategy.

**The original specification's unplug-mid-frame test is still OPEN and NOT PASSED.**
The safe-mode partial-frame probe does not replace it. Before any unplug during
an active transfer, implement and review a separate, bounded host test with a
power-cycle recovery procedure and explicit evidence recording. No result from
this PR is evidence of fast-mode recovery after a physical USB cable pull.

**Unplug test is separate:** unplugging the current USB-powered board also cuts
its power. Only after safe results should you deliberately unplug it between
runs, replug, confirm the new port with `ls /dev/cu.usbmodem*`, and rerun the
16-byte smoke test. That validates reboot/re-enumeration, not recovery of a
partially transmitted frame without a reset.

## Failure handling

If the host prints `INCOMPLETE`, `FAIL`, an unexpected acknowledgement, or a
CRC mismatch, stop. **Do not repeatedly send frames against an unknown
receiver state.** The fast path may be blocked inside a partial 256-byte read:
reconnecting USB power resets it. After that, confirm the port and begin with
`--smoke`. Preserve logs as evidence; no failed run counts toward a throughput
threshold. Use Thonny or `mpremote repl` to inspect a traceback if available.

## Restore verified working firmware

Exit all serial clients. If a fast-mode transfer is blocked, safely unplug and
reconnect the board first. Confirm the actual port again, then:

```sh
mpremote connect "$PORT" fs cp "$BACKUP/main.py" :main.py
mpremote connect "$PORT" fs cp :main.py "$BACKUP/restored-check.py"
cmp "$BACKUP/main.py" "$BACKUP/restored-check.py"
mpremote connect "$PORT" reset
```

Verify the eyes are blinking. The board backup is the source of truth; avoid
substituting the repository's `main.py` because the actual board may have been
running an older commit.

## Reporting (not yet measured)

The existing failed first attempt is documented in `docs/hardware/bringup-log.md`; append only newly observed values there: the repository
commit, board and MicroPython version, cable/port, four benchmark lines, JSON
log, host exit status, free heap, display behavior, any failures, safe-mode
recovery outcome, unplug-reconnect outcome if tested, and whether the backup
was restored and blinking. Mark anything not tested as **not tested**.
