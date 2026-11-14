# Bench USB Review Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the five actionable findings from the review of PR #32 so that a benchmark run cannot lose recorded evidence, a failed teardown cannot be logged as a pass, and the documented repeat-run precision matches the measured table.

**Architecture:** All code changes are in `tools/bench_usb.py`, which is the host side of the benchmark; the device firmware and the wire protocol (`SYNC` / `READY` / `OK` / `ERR` / `STOPPED`) do not change, so no reflash is needed. The changes are: an evidence save point inside the configuration loop, a `KeyboardInterrupt` handler, two prints moved after the teardown ack, `termios.error` added to two exception tuples, and one JSON field plus one printed string. The last task is a documentation correction.

**Tech Stack:** Python 3.12 standard library only (`argparse`, `select`, `termios`, `json`), `unittest` with `unittest.mock`, `pty` for serial transport integration tests.

**Spec:** `docs/hardware/usb-benchmark.md` (protocol and reporting contract), `docs/hardware/bringup-log.md` (the measured table the final task corrects), and the review of PR #32 in the pull request conversation. Slice 0 context: `docs/superpowers/specs/2026-11-12-buddy-os-design.md`.

## Global Constraints

- Standard library only. No new dependencies; `tools/bench_usb.py` imports nothing outside the stdlib plus `tools.send_blink.open_raw`.
- Do not touch `firmware/rp2040/bench_usb.py` and do not change the wire protocol. Host and device must stay compatible with a board already flashed with the PR #32 firmware.
- Do not run anything against the physical board. These fixes are host-side; hardware evidence in the bring-up log stays as recorded.
- Exit codes: `0` success, `2` failure, `130` interrupted. Keep `complete` (measurement finished) and `device_stopped` (teardown acknowledged) as separate, never-inferred flags.
- Never send `BENCH 0 0` when the receiver state is unknown.
- Test command: `python3 -m unittest discover -s tests` (CI runs the same on `ubuntu-latest`, so `pty` tests must stay portable).
- Conventional commits, one commit per task, smallest diff that fully works.

## Review Focus

These are the failure modes this plan's changes introduce or leave open. Each is pinned by a test in the task named.

- **Saving before a port exists.** `port` is assigned inside the `try`; referencing it from an exception handler can raise `NameError` and hide the real failure, and saving an empty `results` would overwrite a previous evidence file. Task 1's save sits inside the configuration loop, after `port` exists, and its regression guard asserts that a failed port open leaves an existing results file byte-identical.
- **Teardown on interrupt.** A Ctrl+C must not send `BENCH 0 0` into a receiver of unknown state. Task 1 asserts `stop_device` is not called.
- **Save ordering.** A per-configuration save must not run after the final `complete=True` write, or a successful file gets downgraded to `complete: false`. Task 1 keeps the new save before the two existing final saves; the existing smoke test asserts both flags are true at the end.
- **Global patch leakage.** `termios` is a shared C module, so `patch.object(host.termios, "tcflush", ...)` breaks every later test that opens a port unless it is scoped to a `with` block. Task 3 scopes it and closes its fds in `finally`.
- **Documented precision drifting again.** The replacement sentence must be recomputed from the table in the same file. Task 5 carries the arithmetic and a grep for the stale figures.

---

### Task 1: Persist each completed configuration and exit cleanly on Ctrl+C

**Files:**
- Modify: `tools/bench_usb.py:296-319`
- Test: `tests/test_bench_usb.py` (class `HostTransport`)

**Interfaces:**
- Consumes: `save_results(path, port, results, complete, device_stopped=False)` and `summarize(...)` from the same module; `host.main(argv)` returns the process exit code.
- Produces: `main` returns `130` on `KeyboardInterrupt`; `--json-out` holds every completed configuration even when the run is interrupted.

- [ ] **Step 1: Write the failing test**

Add to `HostTransport`:

```python
    def test_interrupt_keeps_completed_configurations(self):
        class FakeLink:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "interrupted.json")
            with (patch.object(host, "SerialPort", return_value=FakeLink()),
                  patch.object(host, "synchronize", return_value="0123456789abcdef"),
                  patch.object(host, "send_frame", side_effect=[
                      (0.1, 0.11, 87024), KeyboardInterrupt()]),
                  patch.object(host, "stop_device") as stop):
                exit_code = host.main(["/dev/fake", "--frames", "1", "--show", "0",
                                       "--size", "16", "--size", "1024",
                                       "--json-out", output])
                self.assertEqual(exit_code, 130)
                stop.assert_not_called()  # receiver state is unknown
            with open(output, encoding="utf-8") as result_file:
                result = json.load(result_file)
        self.assertEqual([record["size_bytes"] for record in result["results"]], [16])
        self.assertFalse(result["complete"])
        self.assertFalse(result["device_stopped"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_bench_usb.HostTransport.test_interrupt_keeps_completed_configurations -v`
Expected: ERROR with `KeyboardInterrupt` (the exception escapes `main`), and no JSON file written.

- [ ] **Step 3: Implement the save point and the handler**

In the configuration loop in `main`, immediately after the `if mode == "F": ... else: ...` decision block:

```python
                    # Evidence on disk before the next configuration: an interrupt must not discard it.
                    save_results(args.json_out, port, results, complete=False)
```

After the existing `except (TimeoutError, BenchmarkError, ConnectionError, OSError)` block in `main`:

```python
    except KeyboardInterrupt:
        # No BENCH 0 0: the receiver may be mid-frame. Completed configurations are already saved.
        print("INTERRUPTED: completed configurations saved; the in-progress one is lost",
              file=sys.stderr)
        return 130
```

Do not add a `save_results` call to the other exception handler: it runs when `port` may be unbound, and its job is only to report.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests`
Expected: `OK` with 131 tests.

- [ ] **Step 5: Add the regression guard for the evidence file**

This one passes before and after the change; it exists so a later "fix" that saves from the outer handler cannot silently clobber a previous run. Add to `HostTransport`:

```python
    def test_failed_port_open_keeps_an_existing_results_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "results.json")
            with open(output, "w", encoding="utf-8") as existing:
                existing.write("previous evidence")
            with patch.object(host, "resolve_port", side_effect=host.BenchmarkError("no port")):
                exit_code = host.main(["--json-out", output])
            self.assertEqual(exit_code, 2)
            with open(output, encoding="utf-8") as result_file:
                self.assertEqual(result_file.read(), "previous evidence")
```

Run: `python3 -m unittest tests.test_bench_usb.HostTransport.test_failed_port_open_keeps_an_existing_results_file -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/bench_usb.py tests/test_bench_usb.py
git commit -m "fix(bench): persist each completed configuration and exit on interrupt"
```

---

### Task 2: Print the recovery verdict only after the teardown ack

**Files:**
- Modify: `tools/bench_usb.py:221-235`
- Test: `tests/test_bench_usb.py` (class `HostTransport`)

**Interfaces:**
- Consumes: `recovery_test(link)`, `stop_device(link)`, `send_frame(...)` from the same module.
- Produces: `SAFE recovery PASS` appears on stdout only when `STOPPED` was acknowledged.

- [ ] **Step 1: Write the failing test**

Add to `HostTransport` and extend the imports at the top of the file with `from contextlib import redirect_stdout`:

```python
    def test_recovery_pass_prints_only_after_the_stop_ack(self):
        nonce = "0123456789abcdef"
        crc = binascii.crc32(host.payload(16))
        replies = iter([("READY %s 0" % nonce).encode(),
                        ("ERR %s 0 stall 17" % nonce).encode(),
                        ("READY %s 1" % nonce).encode(),
                        ("OK %s 1 %d 50776" % (nonce, crc)).encode()])

        class FakeLink:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def write_all(self, data, timeout=None):
                pass
            def read_line(self, timeout=None):
                return next(replies)

        buffer = io.StringIO()
        with (patch.object(host, "SerialPort", return_value=FakeLink()),
              patch.object(host, "synchronize", return_value=nonce),
              patch.object(host, "stop_device", side_effect=host.BenchmarkError("no ack")),
              redirect_stdout(buffer)):
            exit_code = host.main(["/dev/fake", "--recovery-test"])
        self.assertEqual(exit_code, 2)
        self.assertNotIn("SAFE recovery PASS", buffer.getvalue())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_bench_usb.HostTransport.test_recovery_pass_prints_only_after_the_stop_ack -v`
Expected: FAIL in `assertNotIn` — the buffer contains `SAFE recovery PASS: 17-byte partial frame stalled, ...`.

- [ ] **Step 3: Move the two prints below the ack**

In `recovery_test`, reorder so `stop_device(link)` is the third statement after `send_frame` and the prints follow it:

```python
    duration, _, heap = send_frame(link, nonce, 1, 16, 0, "S")
    stop_device(link)
    print("SAFE recovery PASS: 17-byte partial frame stalled, resynchronized, then CRC-valid 16-byte frame")
    print("Recovery frame: %.1f ms; free heap: %d B" % (duration * 1000, heap))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests`
Expected: `OK` with 133 tests.

- [ ] **Step 5: Commit**

```bash
git add tools/bench_usb.py tests/test_bench_usb.py
git commit -m "fix(bench): report recovery success only after the stop ack"
```

---

### Task 3: Treat a vanished port at open time as a transport failure

**Files:**
- Modify: `tools/bench_usb.py:276`, `tools/bench_usb.py:317`
- Test: `tests/test_bench_usb.py` (class `HostTransport`)

**Interfaces:**
- Consumes: `SerialPort.__init__` (calls `open_raw` then `termios.tcflush`), `main`.
- Produces: `main` returns `2` and prints `FAIL:` when `termios.error` is raised anywhere in the open or frame path.

`termios.error` is not a subclass of `OSError` in CPython 3.12 (verified on this machine and in the PR #32 review), which is why `SerialPort.close` already catches it explicitly.

- [ ] **Step 1: Write the failing test**

Add to `HostTransport` and extend the imports at the top of the file with `from contextlib import redirect_stderr`:

```python
    def test_termios_error_at_open_is_a_transport_failure(self):
        master, slave = pty.openpty()
        errors = io.StringIO()
        try:
            with (patch.object(host, "open_raw",
                               return_value=(os.dup(slave), termios.tcgetattr(slave))),
                  patch.object(host.termios, "tcflush",
                               side_effect=termios.error(6, "Device not configured")),
                  redirect_stderr(errors)):
                exit_code = host.main(["/dev/fake", "--smoke"])
            self.assertEqual(exit_code, 2)
            self.assertIn("FAIL:", errors.getvalue())
        finally:
            os.close(slave)
            os.close(master)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_bench_usb.HostTransport.test_termios_error_at_open_is_a_transport_failure -v`
Expected: ERROR — `termios.error: (6, 'Device not configured')` propagates out of `main`.

- [ ] **Step 3: Add `termios.error` to both handler tuples**

Inside the frame loop:

```python
                        except (TimeoutError, BenchmarkError, OSError, termios.error) as exc:
```

In `main`'s outer handler:

```python
    except (TimeoutError, BenchmarkError, ConnectionError, OSError, termios.error) as exc:
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests`
Expected: `OK` with 134 tests.

- [ ] **Step 5: Commit**

```bash
git add tools/bench_usb.py tests/test_bench_usb.py
git commit -m "fix(bench): treat termios errors as transport failures"
```

---

### Task 4: Mark completed records and name the smoke mode

**Files:**
- Modify: `tools/bench_usb.py:241`, `tools/bench_usb.py:297`, `tools/bench_usb.py:312`
- Test: `tests/test_bench_usb.py` (`test_main_smoke_terminates_cleanly`)

**Interfaces:**
- Consumes: nothing new.
- Produces: successful JSON records carry `"status": "complete"`, matching `"status": "incomplete"` on partial records; the smoke pass line names the mode actually used.

`--smoke` forces `size=16`, `show=0`, `frames=1`, `mode=S` regardless of `--mode`, `--show`, `--size` or `--frames`; the message must say so instead of silently disagreeing with the flags.

- [ ] **Step 1: Write the failing assertions**

In `test_main_smoke_terminates_cleanly`, replace the `rc = host.main(...)` line with a captured run and add the two new assertions:

```python
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    rc = host.main([os.ttyname(slave), '--smoke', '--json-out', output])
                self.assertEqual(rc, 0)
                self.assertIn("mode S", buffer.getvalue())
```

and after the existing `assertTrue(result["complete"] and result["device_stopped"])`:

```python
            self.assertEqual(result["results"][0]["status"], "complete")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_bench_usb.HostTransport.test_main_smoke_terminates_cleanly -v`
Expected: FAIL — `KeyError: 'status'` (or the `assertIn` on `mode S` fails first).

- [ ] **Step 3: Implement**

The configuration record in `main`:

```python
                    record = {"size_bytes": nbytes, "show": show, "mode": mode,
                              "status": "complete", **stats}
```

The smoke pass line:

```python
                print("Smoke test PASS (16 bytes, mode S, binary including 0x03, CRC matched)")
```

The `--smoke` help text:

```python
    parser.add_argument("--smoke", action="store_true",
                        help="one 16-byte no-show frame in safe mode S; ignores --size/--show/--frames/--mode")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests`
Expected: `OK` with 134 tests.

- [ ] **Step 5: Commit**

```bash
git add tools/bench_usb.py tests/test_bench_usb.py
git commit -m "fix(bench): label completed records and the smoke mode"
```

---

### Task 5: Correct the repeat-run precision claim

**Files:**
- Modify: `docs/hardware/bringup-log.md:21`
- Check: `docs/hardware/usb-benchmark.md:3`, `README.md`

**Interfaces:**
- Consumes: the measured table directly above the sentence in the same file.
- Produces: a spread claim that matches that table and does not contradict `usb-benchmark.md`.

Measured from the table in the same file: throughput deltas are 0.0%, 0.097%, 0.0%, 0.0%; mean-latency deltas are 0.1, 0.2, 0.5, 0.6 ms. `ms p95` has a single value per configuration, so no run-to-run claim about p95 is supported.

- [ ] **Step 1: Replace the sentence**

Current:

```markdown
Run-to-run spread is 0.01-0.06% on throughput and under 0.2 ms on p95, so the
numbers are repeatable, not a lucky pass.
```

Replace with:

```markdown
Run-to-run spread is at most 0.1% on throughput and at most 0.6 ms on mean
latency; `ms p95` was recorded once per configuration, so it carries no
run-to-run comparison. The numbers are repeatable, not a lucky pass.
```

- [ ] **Step 2: Check no other file repeats the old figures**

Run: `grep -rn "0.01-0.06\|under 0.2 ms" docs/ README.md`
Expected: no output.

- [ ] **Step 3: Check the other doc still agrees**

Run: `grep -n "within 0.1%" docs/hardware/usb-benchmark.md`
Expected: one match at line 3, unchanged — it is consistent with the new sentence.

- [ ] **Step 4: Commit**

```bash
git add docs/hardware/bringup-log.md
git commit -m "docs: use the measured repeat-run spread in the bring-up log"
```

---

## Handoff notes (no code)

- The PR body on GitHub still says "Run-to-run spread 0.01-0.06%" and "18 tests". After Task 5 the repo says "at most 0.1%" and `tests/test_bench_usb.py` defines 19 tests today, 22 after this plan (134 in the suite). Update the PR description by hand; it is not a repo file.
- `tests/test_bench_usb.py` lost the comment explaining that nearest-rank p95 over 20 samples is the 19th smallest, which is why one slow frame does not move `ms_p95`. It is asserted by `test_summarize`; restoring one line is optional and independent of these tasks.
- Nothing in this plan needs the board, a reflash, or a new hardware run. The measurements in the bring-up log stay as recorded.
