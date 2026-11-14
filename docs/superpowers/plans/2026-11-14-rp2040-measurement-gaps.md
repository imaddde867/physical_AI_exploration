# RP2040 Measurement Gaps Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans. Spot **five** subagents, one per task below, and enforce the device lock in "Harness dispatch". Tasks are independent in content but share one physical board, so they must not run concurrently on hardware.

**Goal:** close the five measurement gaps that stand between us and the slice-0 architecture decision — flash read cost, fast-mode stall recovery, host-death recovery, partial-region refresh, and long-run/endurance behaviour — without changing firmware behaviour, the wire protocol, or any already-recorded evidence.

**Architecture:** Every task is a measurement, not a feature. Three tasks add a small device-side script under `firmware/rp2040/` and run it with `mpremote run` alongside the installed `main.py`, so `main.py` is never replaced. Two tasks deploy the existing `firmware/rp2040/bench_usb.py` over `:main.py` (its own documented pattern, needed because it owns stdin) and restore the backup afterwards. No host-tool logic changes, no protocol changes, no reflash. All artifacts land in per-agent directories under `.local-archive/`; exactly one coordinator step appends to the bring-up log, so no two agents ever edit the same file.

**Tech Stack:** MicroPython 1.29.0 on RP2040, `mpremote`, Python 3 standard library host tooling already in `tools/`, POSIX `mkdir` locking.

**Spec:** `docs/hardware/usb-benchmark.md` (flash/backup/benchmark/restore protocol), `docs/hardware/bringup-log.md` (all prior evidence), `docs/hardware/display-frame-rate.md` (frame size, 20% headroom rule), `docs/superpowers/specs/2026-11-12-buddy-os-design.md` (the `<150 KB/s` branch this work feeds).

---

## Where we stand

Board: Waveshare RP2040-Touch-LCD-1.69 (16 MB), MicroPython **v1.29.0 on 2026-08-24**, flashed 2026-11-14 from `WAVESHARE_RP2040_PLUS-FLASH_16M-20260824-v1.29.0.uf2`. Filesystem **15,728,640 B** total, 15,507,456 B free with the eight restored files. Device state is the pre-flash blink, `main.py` sha256 `f3931442…`, all eight files byte-identical to `.local-archive/device-backup-2026-11-14/`.

Measured and settled:

| Item | Value | Verdict |
|---|---|---|
| USB receive, 28,800 B, `show=0` | 112.31 KB/s, 256.4 ms | unchanged from 1.22.2 (112.2) |
| USB receive, 134,400 B, `show=0` | 114.87 KB/s, 1170.0 ms | unchanged (114.5) |
| `show()` whole screen | 55.44 ms mean, 56.3 p95, 18.04 fps | **regressed** from 23.2 ms |
| SPI as instantiated | `SPI(1, baudrate=24000000)` | driver asks 100 MHz, gets 24 MHz |
| Heap, blink with driver | 78,768 B | 7,632 B below 1.22.2 |
| Heap floor, 400 frames | 64–1,408 B (`heap_min` per configuration) | thin, unexplained |
| Safe-mode recovery probe | PASS; 8.3 ms recovery frame, 7.9 ms follow-up frame | holds on 1.29.0 |
| Cable pull mid-run | `Errno 6`, exit 2, 333/400 kept | recovers with no reflash |

Decided: USB receive is not the bottleneck, so the `<150 KB/s` branch in the design spec stands. The display, not USB, is now the binding constraint.

Not decided: how to recover the 24 MHz SPI cap (custom build raising `clk_peri`, a PIO SPI path, or accept 18 fps). **Not in this plan** — it needs the user, and Tasks 1 and 4 decide whether it is worth doing at all.

The five gaps this plan closes:

1. **Flash read cost is unknown.** About 115 raw frames fit (15,507,456 ÷ 134,400 ≈ 115.4, before filesystem block overhead), but nobody has timed reading one back into the framebuffer. With the repo's 20%-headroom rule at 12 fps, a frame budget of 83.3 ms allows 66.7 ms of work, so a full-screen refresh (`show()` = 55.4 ms) leaves **≈11 ms** for the read. Without that headroom the read may take 28 ms. If it takes 80 ms, 12 fps is out of reach even with no display refresh at all.
2. **Fast-mode stall recovery is untested.** The probe covered mode `S` only; the log records a device-side timeout inside a fast-mode slice as "not measured".
3. **Host death mid-frame is untested.** A dead host is not a pulled cable: the board keeps its session and never sees a disconnect.
4. **Partial refresh is untested.** Only whole-screen `show()` has ever been timed, and `Windows_show` has quirks (it clamps the start coordinate to 10 and then shifts both edges outward by 10, it issues one `spi.write` per row, and its expanded window escapes the panel bounds near the edges) that a sprite engine must know about.
5. **Endurance is untested.** Nothing has run past 400 frames or written near filesystem capacity.

---

## Global Constraints

- **One board.** All five tasks need exclusive access to the single USB CDC device. The harness must serialize them with the lock in the next section. Never run two agents against `/dev/cu.usb*` at once.
- **No reflash, no firmware behaviour change.** Do not touch the UF2, the partition layout, `machine.freq`, or `waveshare_lcd.py`. Do not edit `firmware/rp2040/bench_usb.py`, `tools/bench_usb.py`, or the wire protocol. The only permitted repo additions are the three new device scripts named in Tasks 1, 4 and 5.
- **Board state contract.** `main.py` must be the blink, `sha256(:main.py) == f3931442b87ed0680df1fb06f764d0a07b63eb716864888813004ffb2073415f`, and the board must end with the blink running again (it re-owns the backlight on boot). Verify with `hashlib` readback (`binascii.hexlify(h.digest())`), then `reset`. Tasks 1, 4 and 5 never replace `main.py`; Tasks 2 and 3 restore it from the backup.
- **A wedged receiver blocks the lock.** `bench_usb.py` disables `kbd_intr` while receiving a payload, so a device blocked inside `readinto` ignores Ctrl-C and a soft reset. If `mpremote connect "$PORT" exec "print(1)"` fails, stop the task, release nothing further, and report that a physical replug is required. Do not start another task on an unresponsive board.
- **Reset before every host invocation.** `mpremote connect "$PORT" reset` then `sleep 2`. `mpremote exec` and `mpremote run` leave the board at the REPL; a following `--smoke` then echoes its own `SYNC` and exits 2.
- **Port discovery.** `set -- /dev/cu.usbmodem*`. Require exactly one match; if two appear, record both and stop. Record the name; do not assume `101`. The macOS node survives an unplug, so a present node is not proof of a live link.
- **Measured vs inferred.** Numbers get units and the command that produced them. Anything not directly printed by the device or the host tool is labelled *inferred*. Never present a timing implication as a measurement.
- **Evidence is additive.** Write only inside `.local-archive/agent-<n>-<slug>/`. On the host, do not edit `docs/`, do not delete or overwrite any existing file in `.local-archive/`, do not amend prior entries.
- **Failure is a result.** An `ENOSPC`, `MemoryError`, `ValueError`, timeout or missing port is recorded with its exact text, not worked around, retried away, or hidden. If a task cannot run, it reports why and stops.
- **Timeouts.** 25 minutes per agent, enforced by the harness. Default `timeout 120` per `mpremote` or host-tool call; two documented exceptions — Task 1's read loop gets `timeout 480` and Task 5's 600-frame run gets `timeout 1100`. A hung call is killed and reported, never left running.
- **No commits.** Leave the tree for review.

## Review Focus

The failure modes this plan's tasks can introduce or leave open.

- **Reading the wrong bytes fast.** Task 1 verifies the framebuffer CRC against the host file before reporting any timing; a read that returns stale or partial data is not a result.
- **Mistaking a block for a stall.** `recv_into` documents that 1.22.2's `readinto` waits for the whole 256-byte chunk, so a mid-chunk stall cannot time out. That is unverified on 1.29.0, which is why Tasks 2 and 3 branch on the observed behaviour instead of asserting one.
- **Calling a reset a recovery.** "No replug needed" is only true if the 16-byte frame passes afterwards with no `reset`; Tasks 2 and 3 state which step was actually required.
- **Reporting `heap_min` as a trend.** `tools/bench_usb.py` records only `heap_min`/`heap_max` per configuration; there is no per-frame series, so no drift claim may be made from it.
- **Timing measured on a different boot.** Each task records `show()` as a control on its own boot so a 55 ms figure taken from another boot cannot silently stand in.
- **Documented line references drifting.** Every file:line cited below was checked against the current tree; a reviewer should re-check any that moved.

---

## Harness dispatch

Five subagents, one per task, **dispatched sequentially in the order below**. The lock still applies as a safety net for retries and manual runs, but the order is real: a wedged board from Task 2 or 3 must be cleared before the next task starts.

Task order: 1 → 4 → 2 → 3 → 5. Cheapest and most decision-relevant first; the 12-minute endurance run last.

Dispatch prompt, verbatim, plus the task block:

> You are agent N of 5 in `docs/superpowers/plans/2026-11-14-rp2040-measurement-gaps.md`. Read that file first and obey "Global Constraints". Your task is measurement only. Report **exactly**: the question, the method actually run, raw command lines, raw output, numbers with units, pass/fail against the stated criteria, what the result does **not** prove, artifact paths, and final board state. Do not summarise away numbers, do not interpret beyond the criteria, and do not edit anything under `docs/`.

**Serialization.** `flock` is not installed on this machine; use an atomic `mkdir` lock with stale-PID recovery:

```bash
LOCK=.local-archive/.device.lock
acquire() {
  until mkdir "$LOCK" 2>/dev/null; do
    if [ -r "$LOCK/pid" ] && ! kill -0 "$(cat "$LOCK/pid")" 2>/dev/null; then
      rm -rf "$LOCK"; continue
    fi
    sleep 2
  done
  echo $$ > "$LOCK/pid"
}
release() { rm -rf "$LOCK"; }
trap release EXIT
```

**Pre-flight inside the lock**, before any measurement — abort the task, release, and report if any check fails:

```bash
mpremote connect "$PORT" exec "import os,machine;u=os.uname();print(u.release,u.machine,machine.reset_cause())"
# expect: 1.29.0 Waveshare RP2040-Plus 16MB with RP2040
mpremote connect "$PORT" exec "import os;v=os.statvfs('/');print(v[2]*v[0],v[3]*v[0])"
# expect: 15728640 total, and >= 15000000 free
mpremote connect "$PORT" exec "import hashlib,binascii;print(binascii.hexlify(hashlib.sha256(open('main.py','rb').read()).digest()))"
# expect: f3931442b87ed0680df1fb06f764d0a07b63eb716864888813004ffb2073415f
```

**Watchdog.** Wrap each agent in `timeout 1500`. On timeout the harness kills the agent, then tries to restore state: copy `.local-archive/device-backup-2026-11-14/main.py` to `:main.py`, `reset`, re-verify the hash. If the board does not answer `mpremote`, it is wedged inside `readinto`; the harness cannot clear that in software — record the condition, stop the queue, and tell the operator to replug. Never leave the board benchmarked between agents.

**Post-task exit check**, before releasing the lock: `mpremote connect "$PORT" exec "print(1)"` must print `1`, the hash must match, `statvfs` free space must be back to ≥15,000,000 B, and `reset` must leave the blink running.

**Collection.** The harness concatenates each agent's `findings.md` into `.local-archive/measurement-gaps-2026-11-14.md` and hands it to the coordinator step. It does not merge prose itself.

---

### Task 1: Flash read throughput into a framebuffer

**Question:** how long does reading a stored frame from LittleFS into the 134,400-byte framebuffer take, and what frame rate does that allow alongside a 55.4 ms full refresh?

**Files:**
- Create: `firmware/rp2040/bench_flash_read.py`
- Read: `.local-archive/device-backup-2026-11-14/watch-final.rgb565` (134,400 B) and `watch-frame.rgb565` (33,600 B); `firmware/rp2040/benchmark_display.py` (the `Display` subclass pattern); `firmware/rp2040/main.py:101-110` (`set_window`)
- Artifacts: `.local-archive/agent-1-flash-read/`

**Method:**
- [ ] `mpremote run firmware/rp2040/bench_flash_read.py` — do **not** copy over `:main.py`. mpremote's Ctrl-C stops the blink, and the script imports `set_window` from the installed `main` module exactly as `benchmark_display.py` does.
- [ ] Construct `Display(LCD_1inch69)` with `setWindows` overridden to `set_window(self, …)`, `gc.collect()` first, and keep a single `lcd.buffer` — two 134,400 B buffers do not fit in RP2040's 264 KiB SRAM.
- [ ] For each of the two files: open once, then 100 iterations of `seek(0)` + `readinto(memoryview(lcd.buffer))`, timed with `ticks_us`. Report mean/p95/max in ms and MB/s.
- [ ] Time `seek(0)` alone, 100 iterations, to price repositioning separately. Do **not** attempt a second sequential read: the files are exactly n bytes, so a read without `seek(0)` returns 0.
- [ ] Time `open()` + `close()` alone, 100 iterations, to price per-frame reopening.
- [ ] Verify the buffer: `binascii.crc32(memoryview(lcd.buffer)[:n])` must equal the host's `crc32` of the same backup file. Record both.
- [ ] Control: 20 `lcd.show()` calls after the reads, on the same boot. Record mean; flag if it falls outside 45–65 ms, because that means this boot is not comparable to the 55.44 ms baseline.
- [ ] Print one JSON line per measurement: `{"file", "bytes", "samples", "mean_ms", "p95_ms", "max_ms", "mb_s", "crc32", "heap_free"}`.
- [ ] Finish with `mpremote connect "$PORT" reset` so the blink comes back.

**Pass:** 100 valid samples per case, CRC match on both files, control `show()` recorded.
**Report:** read ms for 134,400 B and 33,600 B; the `read + show` total; the implied maximum fps at 80% headroom (`0.8 * 1000 / (read + show)`); and whether 12 fps with a full refresh is reachable (read ≤ ~11 ms), reachable without headroom (≤ ~28 ms), or not reachable.
**Does not prove:** decode cost (none exists yet), read behaviour after filesystem fragmentation, or sustained mixed read/write.
**Artifacts:** `findings.md`, `bench_flash_read.py` as run, raw console log, `read-results.json`.

---

### Task 2: Fast-mode in-place stall recovery

**Question:** when a fast-mode (`F`) frame stalls mid-chunk, does the receiver detect it at all, and can a fresh session be established without a replug?

**Files:**
- Modify: none. Deploy `firmware/rp2040/bench_usb.py` over `:main.py` and restore the backup afterwards.
- Read: `firmware/rp2040/bench_usb.py:69-96` (`recv_into`), `:12` (`STALL_MS = 200`), `:15` (`FAST_CHUNK = 256`), `:99-140` (`run`); `docs/hardware/bringup-log.md` "Not measured / not passed" clause
- Artifacts: `.local-archive/agent-2-fast-stall/`

**Method:** one stdlib script driving the port directly (no `pyserial`), timestamping every line.
- [ ] `SYNC <16 hex>` → `SYNCED <nonce>`.
- [ ] `BENCH 1 28800 0 F` → `READY <nonce> 1`; send **100 B** (a partial 256-byte chunk); wait 1.2 s; record reply R1 or its absence.
- [ ] **Branch A — R1 empty** (receiver blocked in `readinto`, the documented 1.22.2 behaviour, unverified on 1.29.0): send the remaining 156 B so the chunk completes, then wait 1.0 s. Expect `ERR <nonce> 1 stall 256`.
- [ ] **Branch B — R1 is `ERR <nonce> 1 stall 100`**: 1.29.0 returns short reads. Record it and do not send the 156 B.
- [ ] With no new `SYNC`, send `BENCH 2 16 0 F` → expect `ERR need_sync` (the session was invalidated in both branches).
- [ ] Fresh `SYNC` → `SYNCED`; `BENCH 3 16 0 F` → `READY`; 16 B → `OK` with a host-verified CRC.
- [ ] **Wedge probe:** `BENCH 4 28800 0 F` → `READY`; send 100 B; wait 2.0 s; then send a fresh `SYNC` line and wait 1.5 s. Record which arrives: `SYNCED` (not wedged), `ERR … stall 100` (short-read path), or silence (wedged — the `SYNC` was absorbed as payload).
- [ ] **Recovery if wedged:** send 28,800 filler bytes. That is always at least the frame remainder, so even a blocked `readinto` completes the frame; wait 1.0 s for `OK`, then wait a further 0.5 s so the receiver's 200 ms poll can discard the leftover partial line, then `SYNC` → `SYNCED`. Without that pause the `SYNC` is swallowed as part of the garbage line and the test would wrongly conclude the receiver never resynchronises. Record that recovery needed a whole frame's worth of bytes, not a reset.
- [ ] `BENCH 0 0` → `STOPPED`; `reset`; restore `main.py` from the backup; verify the hash and that `mpremote` still answers.

**Pass:** the branch is identified unambiguously, every `ERR` carries the expected `got` value, the session is invalidated after each truncation, and the 16 B frame sent after the fresh `SYNC` is CRC-valid. A wedged receiver is a valid recorded outcome, not a failure of the test.
**Report:** R1 for each branch, ms from last byte to `ERR`, whether detection only occurs at chunk boundaries, whether the `SYNC` survived a wedge, and the exact cost of recovery.
**Does not prove:** behaviour when the host never resumes; that is Task 3's scenario.
**Artifacts:** `findings.md`, the driver script, raw transcript with per-step timestamps.

---

### Task 3: Host process death mid-frame

**Question:** if the host process is `kill -9`'d mid-frame, does the board free its session on its own, and what does a fresh host have to do to take over?

**Files:**
- Modify: none. Deploy `firmware/rp2040/bench_usb.py` over `:main.py` and restore afterwards.
- Read: `tools/bench_usb.py` (`send_frame` writes the header then the payload in chunks); `firmware/rp2040/bench_usb.py:99-140`
- Artifacts: `.local-archive/agent-3-host-death/`

**Method:**
- [ ] Run `python3 tools/bench_usb.py "$PORT" --frames 1 --size 134400 --show 0` as a child; one frame takes ~1.17 s.
- [ ] Sleep 200 ms, `kill -9` that child only, and record an epoch timestamp.
- [ ] Read the port for 1.5 s and record whatever the device emits. A `stall` line means the kill landed on a chunk boundary and the 200 ms poll fired; silence means `readinto` is blocked mid-chunk.
- [ ] Send 134,400 filler bytes followed by `\n`. That is always at least the frame remainder, so a blocked receiver finishes its frame; the trailing newline lets any header reader discard the leftovers.
- [ ] Read for 1.5 s; record `OK …` (frame completed, garbage accepted — the device has no host-side frame CRC), `ERR … stall` (the kill landed on a chunk boundary), `ERR header` (leftovers were parsed as a line), or nothing.
- [ ] `SYNC` → record whether `SYNCED` arrives, and how many attempts. Do not report `ERR need_sync` as a possible reply to `SYNC`: `parse_header` handles `SYNC` before the session check, so the only alternatives are `SYNCED` or silence.
- [ ] 16 B fast frame → expect CRC-valid `OK`; then `BENCH 0 0` → `STOPPED`.
- [ ] Record whether anything needed a `reset`. If `mpremote` cannot connect at any point, record "wedged, replug required" and stop — do not claim a software recovery.
- [ ] Restore `main.py`, verify the hash, confirm `mpremote` answers.

**Pass:** a valid frame is delivered afterwards, and the report states exactly which recovery was required (none / finishing the frame / reset / replug).
**Report:** epoch of the kill, first device line and its delay, whether the session was released without help, whether `STOPPED` was reachable, the serial port name before and after, and the elapsed time from kill to a valid frame.
**Does not prove:** recovery if the host never resumes and no filler is sent, or behaviour under repeated host crashes.
**Artifacts:** `findings.md`, killer script, raw transcript, timings.

---

### Task 4: Partial-region refresh cost

**Question:** what does updating a sub-rectangle cost compared with whole-screen `show()`, given `Windows_show`'s clamp-and-expand window and per-row writes?

**Files:**
- Create: `firmware/rp2040/bench_partial_refresh.py`
- Read: `.local-archive/device-backup-2026-11-14/waveshare_lcd.py:163-224` (`setWindows`, `show`, `Windows_show`), `firmware/rp2040/main.py:101-110` (`set_window`, exclusive end, 20-row offset, bounds check)
- Artifacts: `.local-archive/agent-4-partial-refresh/`

**Method:** `mpremote run firmware/rp2040/bench_partial_refresh.py`; import `set_window` from the installed `main` and subclass `Display` exactly as `benchmark_display.py` does, so `Windows_show`'s `self.setWindows` hits the production override.
- [ ] Time `Windows_show` for three regions, 30 samples each, 3 warm-up calls: 40×40 at (100,120); 120×120 at (60,80); a full-width band at x 10..230, y 120..160.
- [ ] Compute the **effective** window for each. `Windows_show` sets `Xstart = max(Xstart, 10) - 10`, `Xend = Xend + 10`, and the same for Y, so: 40×40 at (100,120) → 90..150 × 110..170, 60×60 px, 7,200 B; 120×120 at (60,80) → 50..190 × 70..210, 140×140 px, 39,200 B; the band → 0..240 × 110..170, 240×60 px, 28,800 B. Report requested vs effective px and bytes.
- [ ] Count `spi.write` calls per update (one per row in the effective window: 60, 140, 60) and report it — per-row writes are the suspected overhead.
- [ ] Edge behaviour: request 40×40 at (200,120) so the +10 expansion would reach x=250, and record the exact result. `set_window` rejects `x1 > 240`, so a `ValueError("display window is outside the panel")` is the expected outcome and must be reported as the production limit — a sprite engine cannot draw within 10 px of a panel edge through this path, and the plan must not fix that here.
- [ ] Control: 20 `show()` calls on the same boot (expect ~55 ms).
- [ ] Time `set_window(...)` alone in a tight loop, 50 iterations, to price command overhead without pixel data.
- [ ] Report bytes/s for each path so it is comparable with the 114 KB/s whole-screen figure, plus an implied update rate.
- [ ] `mpremote connect "$PORT" reset`.

**Pass:** ≥20 valid samples per timed case, the `ValueError` recorded for the edge probe, effective-window arithmetic shown.
**Report:** requested vs effective region, ms mean/p95, per-row write count, bytes/s, and whether a 40×40 update is ≤10 ms — the threshold that makes a sprite layer worthwhile at 12 fps. Note the bus floor: 7,200 B at 24 MHz SPI is 2.4 ms, so anything near 3 ms is already at the wire limit and only fewer bytes or a faster clock can improve it.
**Does not prove:** on-screen correctness of partial updates (no read-back path exists; the panel needs a human look), or flicker/tearing.
**Artifacts:** `findings.md`, script as run, `partial-results.json`, raw console log.

---

### Task 5: Endurance — long run and filesystem capacity

**Question:** does anything degrade past 400 frames, and does the 15.5 MB filesystem actually hold a 12.9 MB 96-frame clip?

**Files:**
- Create: `firmware/rp2040/bench_fill.py` (device-side capacity test)
- Read: `docs/hardware/bringup-log.md:140-141` (96 × 134,400 B = 12,902,400 B), `docs/hardware/display-frame-rate.md:34` (134,400 B/frame), `tools/bench_usb.py:72-81` (`summarize`: `heap_min`/`heap_max` only)
- Artifacts: `.local-archive/agent-5-endurance/`

**Method:**
- [ ] Deploy `bench_usb.py` over `:main.py`; `reset`. Create the artifact directory, then long run: `python3 tools/bench_usb.py "$PORT" --frames 600 --size 134400 --show 0 --json-out .local-archive/agent-5-endurance/endurance.json`, `timeout 1100`. Expect ~12 minutes. Record exit code, `heap_min`, `heap_max`, `failures`.
- [ ] Do not claim a heap trend: the host records only the minimum and maximum over the run.
- [ ] Restore `main.py`, verify the hash, `reset`.
- [ ] Capacity: `mpremote run firmware/rp2040/bench_fill.py`. The script must **not** instantiate `LCD_1inch69` — the framebuffer would leave too little heap. At a bare REPL there are ~229 KB free, so one `bytearray(134400)` is safe after a `gc.collect()` (the interrupted blink may not have released its framebuffer yet).
- [ ] Append 134,400-byte synthetic frames to a clip file until either 96 frames are written or the filesystem refuses; time each `write` with `ticks_us`; report MB/s and total.
- [ ] Read back the first, middle and last frame and compare `binascii.crc32` against the generated pattern.
- [ ] Record `statvfs` before, after the fill, and after deleting the file; free space must return to within one block of the starting value.
- [ ] If `ENOSPC` arrives before 96 frames, record the exact exception, the frame index and free space at failure. That passes the test and fails the 12.9 MB claim.
- [ ] Delete the clip, `reset`, verify `main.py` hash, confirm all eight original files are present, and re-check free space ≥15,000,000 B.

**Pass:** 600 frames complete with exit 0 and zero failures; the capacity result is unambiguous either way; the filesystem and file set are back to the pre-task state.
**Report:** `heap_min`/`heap_max`, write MB/s, capacity ceiling in frames, read-back CRC results, and the restored free-space figure.
**Does not prove:** behaviour beyond 600 frames, flash wear, or power-loss durability of a partially written clip.
**Artifacts:** `findings.md`, `bench_fill.py` as run, `endurance.json`, raw logs, `statvfs` samples.

---

## Merge and handoff (coordinator, not a subagent)

- [ ] One new dated entry at the top of `docs/hardware/bringup-log.md`, assembled from the five `findings.md` records, in the established style: measured table, what each result means for 12 fps, then a `Not measured` clause. Cite `.local-archive/agent-*/` paths.
- [ ] Close the three existing "unmeasured" claims this work answers, in place, each pointing at the new entry: `docs/hardware/bringup-log.md:191` (device-side timeout inside a fast-mode slice, recovery after the host process dies), `:251` (fast-mode stall recovery on a truncated 256-byte read, real partial-region refresh, runs longer than 100 frames), and `:101` (anything beyond 400 frames).
- [ ] Fix the stale artifact locations: `docs/hardware/bringup-log.md:196` cites `~/Desktop/macdesk-buddy-usb-2026-11-13/…`, which predates the git-ignored `.local-archive/` convention, and `:253-257` names files "in the 2026-11-13 backup folder" with no path at all. Replace both with the `.local-archive/` equivalents if the files are there; if they are not, say so rather than inventing a path.
- [ ] Correct `docs/hardware/usb-benchmark.md` only where a protocol expectation proved wrong (for example, if Task 2 shows the `ERR … stall` contract does not hold in `F`, or Task 4 shows `Windows_show` cannot reach the panel edge).
- [ ] Final gate: `git diff --check`, `python3 -m unittest discover -s tests` (host-only, no board), device file list and hashes, blink prints `blink ready`.
- [ ] Hand the user one decision list: recover the SPI clock or accept 18 fps; whether clip playback is still in scope given Task 1's read cost; whether the 10 px edge restriction in `Windows_show` is acceptable for sprites.

## Out of scope

- The 24 MHz SPI fix. Needs the user; Tasks 1 and 4 tell us whether to bother.
- Fixing `Windows_show`'s edge clamp or per-row writes — Task 4 measures the current behaviour, nothing more.
- Decode/compression of stored frames, clip format, keyframes.
- Visual correctness of the panel and of partial refresh — needs human eyes.
- Panel/connector work in `docs/hardware/` (Gate 1), unrelated to this board.
