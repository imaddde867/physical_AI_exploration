# Buddy OS core (slices 0 and 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the hardware-free Mac-side core of the Buddy OS (slot arbiter, reconciler, presence, resync, module crash guard) and measure USB frame throughput on the real board to decide how far the frame-lease design can go.

**Architecture:** Modules each own one slot (`Slot`); a pure `pick()` layers the live slots into one desired device state; a `Reconciler` sends only the diff (plus a heartbeat ping); a `Host` ties slots, presence, pin, alert cooldown and resync together. The USB benchmark is independent of the core and only needs the board and a Mac script.

**Tech Stack:** Python 3.12 stdlib only (unittest, asyncio, termios), MicroPython 1.22 on the RP2040. No new dependencies.

Spec: `docs/superpowers/specs/2026-11-12-buddy-os-design.md`.

## Global Constraints

- Python stdlib only; tests run with `python3 -m unittest discover -s tests -v` (CI runs the same command on Python 3.12).
- Protocol: JSON line per message, `"v": 1`, max line 512 bytes including `\n`; the device rejects unknown fields and any `v` other than 1, so new fields are additive and optional (spec: "gated on `caps`, not version bumps").
- Host must send at least one valid message every 2 s; the device blanks after `WATCHDOG_S = 5` s of silence.
- `daemon/protocol.py` is copied to the board as `protocol.py`, so it must stay MicroPython-compatible (no `ensure_ascii`, no monotonic clock, no dataclasses).
- Single 134,400-byte framebuffer on the device; free heap about 29 KB with touch loaded. Measure heap after changes that touch firmware.
- Style: comments only for non-obvious why; conventional commits, one branch per task group, never push `main`, no attribution lines.
- Do not commit `cad/slab/exports/waveshare_case.step` (untracked, unrelated).

## File Structure

- Modify `daemon/protocol.py`: optional `hello` fields `proto`, `caps`, `boot_id`.
- Create `daemon/arbiter.py`: `Slot`, `visible_slots`, `pick`, `ALERT_GAP_S`. Pure, no I/O.
- Create `daemon/reconciler.py`: `Reconciler`, `PING`, `HEARTBEAT_S`. Pure, injectable clock.
- Create `daemon/host.py`: `Host` (slots, presence, pin, alert cooldown, link I/O, resync), `Ctx`, `supervise`.
- Modify `firmware/rp2040/main.py`: answer the first `ping` with `hello`.
- Create `firmware/rp2040/bench_usb.py`: device-side receive benchmark (copied to the board as `main.py` for the run).
- Create `tools/bench_usb.py`: Mac-side sender, stats, decision rule.
- Create `tests/test_arbiter.py`, `tests/test_reconciler.py`, `tests/test_host.py`, `tests/test_bench_usb.py`; extend `tests/test_protocol.py`, `tests/test_device_commands.py`.
- Modify `docs/protocol.md`, `docs/hardware/bringup-log.md`, `README.md` status row.

Branch: Task 1 creates `feat/buddy-os-core` from `docs/buddy-os-design` (which holds the spec and this plan). All tasks commit there.

---

### Task 1: `hello` carries `proto`, `caps`, `boot_id`

**Files:**
- Modify: `daemon/protocol.py` (SPEC `hello` entry, one new validator)
- Modify: `tests/test_protocol.py`
- Modify: `docs/protocol.md` (device -> host table, `hello` row)

**Interfaces:**
- Produces: `hello` messages may carry `proto` (int 1..99), `caps` (list of at most 16 strings of at most 16 chars), `boot_id` (str of at most 32 chars). All optional, so `{"v":1,"t":"hello","fw":"0.1","w":240,"h":280}` stays valid.

- [ ] **Step 1: Write the failing test** (append inside `ProtocolTest` in `tests/test_protocol.py`, before `test_max_line`)

```python
    def test_hello_capabilities_are_optional_and_validated(self):
        base = m("hello", fw="0.1", w=240, h=280)
        full = {**base, "proto": 1, "caps": ["frame", "touch"], "boot_id": "a1b2c3d4"}
        self.assertEqual(decode(encode(full)), full)
        self.assertEqual(decode(encode(base)), base)
        for bad in ({"caps": "frame"}, {"caps": [1]}, {"caps": ["x" * 17]},
                    {"caps": ["a"] * 17}, {"proto": 0}, {"proto": True},
                    {"boot_id": "x" * 33}, {"boot_id": 5}):
            with self.assertRaises(ValueError, msg=bad):
                encode({**base, **bad})
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m unittest tests.test_protocol.ProtocolTest.test_hello_capabilities_are_optional_and_validated -v`
Expected: FAIL with `ProtocolError: hello: unknown field 'proto'` (or `caps`).

- [ ] **Step 3: Implement** in `daemon/protocol.py`

Add after `_str`:

```python
def _str_list(max_items, max_chars):
    def ok(v):
        return (isinstance(v, list) and len(v) <= max_items
                and all(isinstance(c, str) and len(c) <= max_chars for c in v))
    return ok
```

Replace the `hello` line in `SPEC`:

```python
    "hello": ({"fw": _str(32), "w": _int(1, 10000), "h": _int(1, 10000)},
              {"proto": _int(1, 99), "caps": _str_list(16, 16), "boot_id": _str(32)}),
```

- [ ] **Step 4: Run the whole protocol suite**

Run: `python3 -m unittest tests.test_protocol -v`
Expected: all PASS.

- [ ] **Step 5: Update `docs/protocol.md`**: in the device -> host table replace the `hello` row with

```
| `hello` | `fw` str, `w`, `h` int; optional `proto` int, `caps` list of str (<=16 items of <=16 chars), `boot_id` str (<=32) | sent on connect (and on host `ping` before first hello). A new `boot_id` or any reconnect means the host resends all state |
```

- [ ] **Step 6: Commit**

```bash
git checkout -b feat/buddy-os-core
git add daemon/protocol.py tests/test_protocol.py docs/protocol.md
git commit -m "feat(protocol): add optional proto, caps and boot_id to hello"
```

---

### Task 2: `pick`, the pure arbiter

**Files:**
- Create: `daemon/arbiter.py`
- Test: `tests/test_arbiter.py`

**Interfaces:**
- Produces:
  - `Slot(name: str, priority: str, state: dict, expires: float, hard: bool = False)`; `priority` is `"ambient"`, `"activity"` or `"alert"`; `state` maps a state key (`"face"`, `"bar3"`, `"text1"`, `"brightness"`, `"power"`) to a complete protocol message.
  - `visible_slots(slots: dict[str, Slot], presence: str, pin: str | None, now: float, alert_cooldown_until: float = 0.0) -> list[Slot]`, ordered lowest to highest rank.
  - `pick(slots, presence, pin, now, alert_cooldown_until=0.0) -> dict[str, dict]`: desired device state, key to message.
  - `ALERT_GAP_S = 30.0`, `PRESENCE = ("active", "idle", "locked", "asleep", "focus")`.

Rules (from the spec): higher priority wins per key and lower slots' other keys survive; expired slots are ignored; `locked`/`asleep` yield only `{"power": sleep}`; `focus` allows only hard alerts; soft alerts are suppressed while `now < alert_cooldown_until` (hard ones are not); a pinned slot outranks everything except a hard alert.

- [ ] **Step 1: Write the failing tests** `tests/test_arbiter.py`

```python
import unittest

from daemon.arbiter import Slot, pick, visible_slots

SLEEP = {"v": 1, "t": "sleep"}


def S(name, priority, keys, expires=100.0, hard=False):
    return Slot(name, priority, {k: {"by": name} for k in keys}, expires, hard)


def slots(*items):
    return {s.name: s for s in items}


class PickTests(unittest.TestCase):
    def test_higher_priority_wins_per_key_and_lower_keys_survive(self):
        out = pick(slots(S("idle", "ambient", ["face", "bar1"]), S("brk", "alert", ["face"])),
                   "active", None, now=0)
        self.assertEqual(out, {"face": {"by": "brk"}, "bar1": {"by": "idle"}})

    def test_expired_slot_is_ignored(self):
        out = pick(slots(S("a", "ambient", ["face"], expires=5)), "active", None, now=5)
        self.assertEqual(out, {})

    def test_pin_beats_soft_alert_but_not_hard_alert(self):
        music = S("music", "activity", ["text0"])
        self.assertEqual(
            pick(slots(music, S("ci", "alert", ["text0"])), "active", "music", 0),
            {"text0": {"by": "music"}})
        self.assertEqual(
            pick(slots(music, S("ci", "alert", ["text0"], hard=True)), "active", "music", 0),
            {"text0": {"by": "ci"}})

    def test_locked_and_asleep_send_only_sleep(self):
        s = slots(S("idle", "ambient", ["face"]), S("ci", "alert", ["text0"], hard=True))
        for presence in ("locked", "asleep"):
            self.assertEqual(pick(s, presence, None, 0), {"power": SLEEP})

    def test_focus_allows_only_hard_alerts(self):
        s = slots(S("idle", "ambient", ["face"]), S("brk", "alert", ["text1"]),
                  S("ci", "alert", ["text0"], hard=True))
        self.assertEqual(pick(s, "focus", None, 0), {"text0": {"by": "ci"}})

    def test_cooldown_hides_soft_alerts_only(self):
        s = slots(S("brk", "alert", ["text1"]), S("ci", "alert", ["text0"], hard=True))
        self.assertEqual(pick(s, "active", None, now=10, alert_cooldown_until=50),
                         {"text0": {"by": "ci"}})
        self.assertEqual(set(pick(s, "active", None, now=60, alert_cooldown_until=50)),
                         {"text0", "text1"})

    def test_visible_slots_are_ordered_lowest_rank_first(self):
        s = slots(S("a", "alert", ["x"]), S("i", "ambient", ["x"]), S("c", "activity", ["x"]))
        self.assertEqual([x.name for x in visible_slots(s, "active", None, 0)], ["i", "c", "a"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_arbiter -v`
Expected: ERROR `ModuleNotFoundError: No module named 'daemon.arbiter'`.

- [ ] **Step 3: Implement** `daemon/arbiter.py`

```python
"""Which module's state reaches the device. Pure logic; see the buddy-os spec."""
from dataclasses import dataclass

PRIORITY = {"ambient": 0, "activity": 1, "alert": 2}
PRESENCE = ("active", "idle", "locked", "asleep", "focus")
ALERT_GAP_S = 30.0
SLEEP = {"v": 1, "t": "sleep"}


@dataclass
class Slot:
    name: str
    priority: str
    state: dict  # state key -> complete protocol message
    expires: float  # absolute, same clock as `now`
    hard: bool = False  # a hard alert breaks through Focus, the alert gap and a pin


def _rank(slot, pin):
    if slot.priority == "alert" and slot.hard:
        return 3
    if slot.name == pin:
        return 2.5
    return PRIORITY[slot.priority]


def visible_slots(slots, presence, pin, now, alert_cooldown_until=0.0):
    live = [s for s in slots.values() if s.expires > now]
    if presence in ("locked", "asleep"):
        return []
    if presence == "focus":
        live = [s for s in live if s.priority == "alert" and s.hard]
    elif now < alert_cooldown_until:
        live = [s for s in live if s.priority != "alert" or s.hard]
    return sorted(live, key=lambda s: _rank(s, pin))  # stable: later insertion wins ties


def pick(slots, presence, pin, now, alert_cooldown_until=0.0):
    if presence in ("locked", "asleep"):
        return {"power": dict(SLEEP)}
    state = {}
    for s in visible_slots(slots, presence, pin, now, alert_cooldown_until):
        state.update(s.state)
    return state
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m unittest tests.test_arbiter -v`
Expected: 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add daemon/arbiter.py tests/test_arbiter.py
git commit -m "feat(daemon): add pure slot arbiter with presence, pin and alert gap"
```

---

### Task 3: `Reconciler`, send only the diff

**Files:**
- Create: `daemon/reconciler.py`
- Test: `tests/test_reconciler.py`

**Interfaces:**
- Consumes: desired state dict from `arbiter.pick` (key to complete protocol message).
- Produces:
  - `PING = {"v": 1, "t": "ping"}`, `HEARTBEAT_S = 1.5`.
  - `revert(key) -> dict | None`: the message that undoes a removed key. `face` -> neutral gaze and eyes open; `power` -> `wake`; `barN` -> value 0; `textN` -> empty string; anything else -> `None` (kept as is).
  - `Reconciler(clock=time.monotonic)` with `.diff(desired) -> list[dict]` (messages to send now, reverts first), and `.resync()` (forget what was sent so the next `diff` resends everything).

- [ ] **Step 1: Write the failing tests** `tests/test_reconciler.py`

```python
import unittest

from daemon import protocol
from daemon.reconciler import HEARTBEAT_S, PING, Reconciler, revert

FACE = {"v": 1, "t": "face", "x": 0.5}
FACE2 = {"v": 1, "t": "face", "x": -0.5}
TEXT1 = {"v": 1, "t": "text", "slot": 1, "s": "hi"}
SLEEP = {"v": 1, "t": "sleep"}


def make():
    now = [0.0]
    return Reconciler(lambda: now[0]), now


class ReconcilerTests(unittest.TestCase):
    def test_sends_changes_only_then_heartbeats(self):
        r, now = make()
        self.assertEqual(r.diff({"face": FACE}), [FACE])
        self.assertEqual(r.diff({"face": FACE}), [])
        now[0] = HEARTBEAT_S
        self.assertEqual(r.diff({"face": FACE}), [PING])
        self.assertEqual(r.diff({"face": FACE}), [])  # the ping reset the timer

    def test_only_the_changed_key_is_resent(self):
        r, _ = make()
        r.diff({"face": FACE, "text1": TEXT1})
        self.assertEqual(r.diff({"face": FACE2, "text1": TEXT1}), [FACE2])

    def test_removed_keys_are_reverted(self):
        r, _ = make()
        r.diff({"face": FACE, "text1": TEXT1})
        self.assertEqual(r.diff({}), [revert("face"), revert("text1")])

    def test_wake_goes_out_before_new_state(self):
        r, _ = make()
        r.diff({"power": SLEEP})
        self.assertEqual(r.diff({"face": FACE}), [{"v": 1, "t": "wake"}, FACE])

    def test_resync_resends_everything(self):
        r, _ = make()
        r.diff({"face": FACE})
        r.resync()
        self.assertEqual(r.diff({"face": FACE}), [FACE])

    def test_unknown_keys_have_no_revert_and_every_message_is_valid(self):
        self.assertIsNone(revert("brightness"))
        for msg in (PING, revert("face"), revert("power"), revert("bar3"), revert("text0")):
            protocol.encode(msg)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_reconciler -v`
Expected: ERROR `ModuleNotFoundError: No module named 'daemon.reconciler'`.

- [ ] **Step 3: Implement** `daemon/reconciler.py`

```python
"""Diff the desired device state against what was last sent."""
import time

HEARTBEAT_S = 1.5  # protocol: at least one valid message every 2 s
PING = {"v": 1, "t": "ping"}


def revert(key):
    if key == "face":
        return {"v": 1, "t": "face", "x": 0, "y": 0, "blink": False}
    if key == "power":
        return {"v": 1, "t": "wake"}
    # ponytail: the protocol has no bar-hide, so value 0 is the closest; add a message if it matters
    if key.startswith("bar"):
        return {"v": 1, "t": "bar", "id": int(key[3:]), "value": 0}
    if key.startswith("text"):
        return {"v": 1, "t": "text", "slot": int(key[4:]), "s": ""}
    return None


class Reconciler:
    """Messages in `sent` are shared, not copied: callers must treat them as immutable."""

    def __init__(self, clock=time.monotonic):
        self.clock, self.sent, self.last_tx = clock, {}, None

    def resync(self):
        self.sent = {}

    def diff(self, desired):
        out = [m for k in sorted(self.sent.keys() - desired.keys()) if (m := revert(k))]
        out += [msg for k, msg in desired.items() if self.sent.get(k) != msg]
        self.sent = dict(desired)
        now = self.clock()
        if out:
            self.last_tx = now
        elif self.last_tx is None or now - self.last_tx >= HEARTBEAT_S:
            out.append(PING)
            self.last_tx = now
        return out
```

`sorted(...)` makes the revert order deterministic (`face` before `text1`), which the test relies on.

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m unittest tests.test_reconciler -v`
Expected: 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add daemon/reconciler.py tests/test_reconciler.py
git commit -m "feat(daemon): add reconciler that sends state diffs and heartbeats"
```

---

### Task 4: `Host` (slots, presence, resync) and `supervise`

**Files:**
- Create: `daemon/host.py`
- Test: `tests/test_host.py`

**Interfaces:**
- Consumes: `arbiter.Slot/pick/visible_slots/ALERT_GAP_S`, `reconciler.Reconciler`, and any `link` with `.send(msg: dict)` (the existing `daemon.link.Link`) that raises `OSError` when the port is gone.
- Produces:
  - `Host(link, clock=time.monotonic)` with attributes `presence: str = "active"`, `pin: str | None = None`, `boot_id`, `caps: set[str]`; methods `show(name, priority, state, ttl, hard=False)`, `clear(name)`, `step()` (pick, diff, send; on `OSError` it resyncs and re-raises), `on_message(msg: dict)` (a `hello` stores `boot_id`/`caps` and resyncs).
  - `Ctx(host, name)` with `show(priority, state, ttl, hard=False)` and `clear()`: what a module sees.
  - `async supervise(name, run, ctx, log=print, sleep=asyncio.sleep, clock=time.monotonic)`: runs `await run(ctx)`; on an exception logs and restarts after 1 s, doubling to a 30 s cap, resetting to 1 s when the module ran longer than 60 s; returns when `run` returns; never swallows `CancelledError`.

- [ ] **Step 1: Write the failing tests** `tests/test_host.py`

```python
import asyncio
import unittest

from daemon import protocol
from daemon.arbiter import ALERT_GAP_S
from daemon.host import Ctx, Host, supervise

FACE = {"v": 1, "t": "face", "x": 0.5}
TEXT0 = {"v": 1, "t": "text", "slot": 0, "s": "break"}
TEXT1 = {"v": 1, "t": "text", "slot": 1, "s": "ci"}
WAKE = {"v": 1, "t": "wake"}
SLEEP = {"v": 1, "t": "sleep"}
CLEAR0 = {"v": 1, "t": "text", "slot": 0, "s": ""}


class FakeLink:
    def __init__(self):
        self.sent, self.fail = [], False

    def send(self, msg):
        protocol.encode(msg)  # only valid messages may reach the wire
        if self.fail:
            raise OSError("unplugged")
        self.sent.append(msg)


def make():
    now, link = [0.0], FakeLink()
    return Host(link, lambda: now[0]), now, link


def drain(link):
    out, link.sent[:] = list(link.sent), []
    return out


class HostTests(unittest.TestCase):
    def test_slot_state_is_sent_once_then_reverted_on_expiry(self):
        h, now, link = make()
        h.show("idle", "ambient", {"face": FACE}, ttl=10)
        h.step()
        self.assertEqual(drain(link), [FACE])
        h.step()
        self.assertEqual(drain(link), [])
        now[0] = 10
        h.step()
        self.assertEqual(drain(link), [{"v": 1, "t": "face", "x": 0, "y": 0, "blink": False}])

    def test_show_copies_so_a_module_cannot_mutate_sent_state(self):
        h, _, link = make()
        msg = dict(FACE)
        h.show("idle", "ambient", {"face": msg}, ttl=10)
        h.step()
        msg["x"] = -1
        h.show("idle", "ambient", {"face": msg}, ttl=10)
        h.step()
        self.assertEqual([m["x"] for m in link.sent], [0.5, -1])

    def test_locked_sends_sleep_and_unlock_wakes_and_restores(self):
        h, _, link = make()
        h.show("idle", "ambient", {"face": FACE}, ttl=100)
        h.step()
        drain(link)
        h.presence = "locked"
        h.step()
        self.assertEqual(drain(link)[-1], SLEEP)
        h.presence = "active"
        h.step()
        self.assertEqual(drain(link), [WAKE, FACE])

    def test_hello_triggers_a_full_resend(self):
        h, _, link = make()
        h.show("idle", "ambient", {"face": FACE}, ttl=100)
        h.step()
        drain(link)
        h.on_message({"v": 1, "t": "hello", "fw": "0.2", "w": 240, "h": 280,
                      "boot_id": "ab12", "caps": ["touch"]})
        h.step()
        self.assertEqual(drain(link), [FACE])
        self.assertEqual((h.boot_id, h.caps), ("ab12", {"touch"}))

    def test_send_failure_resyncs_for_the_next_connection(self):
        h, _, link = make()
        h.show("idle", "ambient", {"face": FACE}, ttl=100)
        link.fail = True
        with self.assertRaises(OSError):
            h.step()
        link.fail = False
        h.step()
        self.assertEqual(drain(link), [FACE])

    def test_alert_gap_delays_the_next_soft_alert(self):
        h, now, link = make()
        h.show("brk", "alert", {"text0": TEXT0}, ttl=5)
        h.step()
        now[0] = 6
        h.step()  # alert gone: cooldown starts at t=6
        drain(link)
        h.show("ci", "alert", {"text1": TEXT1}, ttl=1000)
        now[0] = 7
        h.step()
        self.assertNotIn(TEXT1, drain(link))
        now[0] = 6 + ALERT_GAP_S
        h.step()
        self.assertIn(TEXT1, drain(link))

    def test_ctx_show_and_clear(self):
        h, _, link = make()
        c = Ctx(h, "brk")
        c.show("alert", {"text0": TEXT0}, ttl=5)
        h.step()
        self.assertEqual(drain(link), [TEXT0])
        c.clear()
        h.step()
        self.assertEqual(drain(link), [CLEAR0])


class SuperviseTests(unittest.IsolatedAsyncioTestCase):
    async def test_restarts_with_growing_delay_then_returns(self):
        calls, delays = [], []

        async def flaky(ctx):
            calls.append(1)
            if len(calls) < 3:
                raise RuntimeError("boom")

        async def sleep(d):
            delays.append(d)

        await supervise("x", flaky, None, log=lambda m: None, sleep=sleep, clock=lambda: 0.0)
        self.assertEqual((len(calls), delays), (3, [1.0, 2.0]))

    async def test_a_long_run_resets_the_delay(self):
        calls, delays, t = [], [], [0.0]

        async def flaky(ctx):
            calls.append(1)
            t[0] += 100
            if len(calls) < 3:
                raise RuntimeError("boom")

        async def sleep(d):
            delays.append(d)

        await supervise("x", flaky, None, log=lambda m: None, sleep=sleep, clock=lambda: t[0])
        self.assertEqual(delays, [1.0, 1.0])

    async def test_cancellation_is_not_swallowed(self):
        async def forever(ctx):
            await asyncio.sleep(3600)

        task = asyncio.create_task(supervise("x", forever, None, log=lambda m: None))
        await asyncio.sleep(0)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_host -v`
Expected: ERROR `ModuleNotFoundError: No module named 'daemon.host'`.

- [ ] **Step 3: Implement** `daemon/host.py`

```python
"""Slots, presence and resync around one link; modules talk to Ctx, never to the port."""
import asyncio
import time

from daemon.arbiter import ALERT_GAP_S, Slot, pick, visible_slots
from daemon.reconciler import Reconciler

STABLE_S = 60.0  # a module that ran this long before crashing gets a fresh backoff
MAX_BACKOFF_S = 30.0


class Host:
    def __init__(self, link, clock=time.monotonic):
        self.link, self.clock = link, clock
        self.slots, self.presence, self.pin = {}, "active", None
        self.boot_id, self.caps = None, set()
        self.rec = Reconciler(clock)
        self.cooldown_until, self._alert_shown = 0.0, False

    def show(self, name, priority, state, ttl, hard=False):
        self.slots[name] = Slot(name, priority, {k: dict(v) for k, v in state.items()},
                                self.clock() + ttl, hard)

    def clear(self, name):
        self.slots.pop(name, None)

    def on_message(self, msg):
        if msg["t"] == "hello":  # a reconnect or a reboot: the device lost our state
            self.boot_id, self.caps = msg.get("boot_id"), set(msg.get("caps", ()))
            self.rec.resync()

    def step(self):
        now = self.clock()
        self.slots = {n: s for n, s in self.slots.items() if s.expires > now}
        args = (self.slots, self.presence, self.pin, now, self.cooldown_until)
        shown = any(s.priority == "alert" for s in visible_slots(*args))
        if self._alert_shown and not shown:
            self.cooldown_until = now + ALERT_GAP_S
        self._alert_shown = shown
        try:
            for msg in self.rec.diff(pick(*args)):
                self.link.send(msg)
        except OSError:
            self.rec.resync()
            raise


class Ctx:
    def __init__(self, host, name):
        self.host, self.name = host, name

    def show(self, priority, state, ttl, hard=False):
        self.host.show(self.name, priority, state, ttl, hard)

    def clear(self):
        self.host.clear(self.name)


async def supervise(name, run, ctx, log=print, sleep=asyncio.sleep, clock=time.monotonic):
    delay = 1.0
    while True:
        started = clock()
        try:
            return await run(ctx)
        except Exception as e:  # CancelledError is a BaseException and passes through
            if clock() - started > STABLE_S:
                delay = 1.0
            log(f"module {name} crashed: {e!r}; restarting in {delay:.0f}s")
            await sleep(delay)
            delay = min(delay * 2, MAX_BACKOFF_S)
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m unittest tests.test_host -v`
Expected: 10 tests PASS.

- [ ] **Step 5: Run the full suite (no regressions)**

Run: `python3 -m unittest discover -s tests -v 2>&1 | tail -5`
Expected: `OK` (the macOS smoke test may skip off macOS; on this Mac it runs).

- [ ] **Step 6: Commit**

```bash
git add daemon/host.py tests/test_host.py
git commit -m "feat(daemon): add host with presence, resync and module crash guard"
```

---

### Task 5: The device answers the first `ping` with `hello`

**Files:**
- Modify: `firmware/rp2040/main.py` (`handle`, `run`)
- Modify: `tests/test_device_commands.py`
- Modify: `docs/protocol.md` ("Not implemented on the device yet")

**Interfaces:**
- Produces: `handle(text, gaze=None, hello=None)`: `hello` is a one-element list holding the hello message to send once; on a valid `ping` it is popped and replied instead of `ok`. `make_hello() -> dict` builds `{"v":1,"t":"hello","fw":"blink-0.3","w":240,"h":280,"proto":1,"caps":[],"boot_id":<8 hex chars>}`.
- The default `hello=None` keeps every existing `handle` call and test unchanged.

- [ ] **Step 1: Write the failing test** (add to `tests/test_device_commands.py` next to the other `handle` tests; `handle` and `protocol` are already imported there, add `make_hello` to the `from firmware.rp2040.main import ...` line)

```python
    def test_first_ping_is_answered_with_hello_then_ok(self):
        hello = [make_hello()]
        first, _ = handle('{"v":1,"t":"ping"}', None, hello)
        second, _ = handle('{"v":1,"t":"ping"}', None, hello)
        msg = protocol.decode(first)
        self.assertEqual((msg["t"], msg["w"], msg["h"], msg["proto"]), ("hello", 240, 280, 1))
        self.assertEqual(len(msg["boot_id"]), 8)
        self.assertEqual(protocol.decode(second)["t"], "ok")
        self.assertEqual(hello, [])
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_device_commands -v 2>&1 | tail -8`
Expected: ERROR `ImportError: cannot import name 'make_hello'`.

- [ ] **Step 3: Implement** in `firmware/rp2040/main.py`

Add after the `OVERFLOW = object()` line:

```python
FW = "blink-0.3"


def make_hello():
    try:
        import binascii
        import os
        boot_id = binascii.hexlify(os.urandom(4)).decode()
    except (ImportError, AttributeError):
        boot_id = "00000000"
    return {"v": 1, "t": "hello", "fw": FW, "w": WIDTH, "h": HEIGHT, "proto": 1,
            "caps": [], "boot_id": boot_id}
```

Change the `handle` signature and its ping branch:

```python
def handle(text, gaze=None, hello=None):
```

```python
    if msg["t"] == "ping":
        return _line(hello.pop() if hello else {"v": 1, "t": "ok"}), None
```

In `run()`, create `hello = [make_hello()]` next to `gaze = [0.0, 0.0]` and call `handle(line, gaze, hello)`.

- [ ] **Step 4: Run all device tests**

Run: `python3 -m unittest tests.test_device_commands tests.test_device_blink -v 2>&1 | tail -5`
Expected: `OK`.

- [ ] **Step 5: Docs.** In `docs/protocol.md` under "Not implemented on the device yet", change the first bullet to: "- `hello` on connect (it is sent in reply to the first `ping` after boot only; a host that connects later and pings gets `ok`, so the daemon resyncs on every connect anyway)." Keep the second bullet.

- [ ] **Step 6: Commit**

```bash
git add firmware/rp2040/main.py tests/test_device_commands.py docs/protocol.md
git commit -m "feat(rp2040): answer the first ping with hello carrying boot_id"
```

On the board: re-copy `main.py` (see firmware README step 3), then `python3 tools/send_blink.py` still passes (ping not involved) and the eyes still blink. Not run by the tests; record the heap line printed at boot in the bring-up log.

---

### Task 6: USB throughput benchmark (slice 0, needs the board)

**Files:**
- Create: `firmware/rp2040/bench_usb.py`
- Create: `tools/bench_usb.py`
- Test: `tests/test_bench_usb.py`
- Modify: `docs/hardware/bringup-log.md` (record results)

**Interfaces:**
- Wire format (private to the benchmark): the Mac sends the text line `BENCH <nbytes> <show>\n` (`show` is `1` to run `lcd.show()` after receiving, `0` to skip), then exactly `nbytes` raw bytes. The device replies `OK <crc32 as decimal> <free heap>\n`, or nothing if the stream stalls for 200 ms. `BENCH 0 0` ends the run. The device reads the bytes straight into the driver's framebuffer (`lcd.buffer`), so `nbytes` can be the full 134,400.
- `tools/bench_usb.py` produces: `payload(n) -> bytes` (deterministic, contains every byte value including 0x03 and 0x0A), `summarize(durations_s: list[float], nbytes: int, failures: int) -> dict` with keys `frames, failures, kb_s_mean, kb_s_p95_worst, ms_mean, ms_p95`, and `decide(kb_s: float) -> str`.
- Decision rule from the spec (KB = 1000 bytes): `>= 500` full regions; `150..500` dirty rectangles only; `< 150` the MicroPython CDC stack is the bottleneck.

- [ ] **Step 1: Write the failing tests** `tests/test_bench_usb.py`

```python
import unittest

from tools.bench_usb import decide, payload, summarize


class BenchHelpers(unittest.TestCase):
    def test_payload_has_every_byte_including_ctrl_c_and_newline(self):
        p = payload(1000)
        self.assertEqual(len(p), 1000)
        self.assertTrue({0x03, 0x0A, 0x00, 0xFF} <= set(p))

    def test_summarize(self):
        s = summarize([0.1] * 19 + [0.3], 28800, failures=1)
        self.assertEqual((s["frames"], s["failures"]), (20, 1))
        self.assertAlmostEqual(s["ms_mean"], 110.0)
        # nearest-rank p95 of 20 samples is the 19th smallest, so one slow frame does not show
        self.assertAlmostEqual(s["ms_p95"], 100.0)
        self.assertAlmostEqual(s["kb_s_mean"], 28.8 / 0.11, places=1)
        self.assertAlmostEqual(s["kb_s_p95_worst"], 28.8 / 0.1, places=1)

    def test_decision_rule_thresholds(self):
        self.assertIn("full regions", decide(500))
        self.assertIn("dirty rectangles", decide(499.9))
        self.assertIn("dirty rectangles", decide(150))
        self.assertIn("bottleneck", decide(149.9))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_bench_usb -v`
Expected: ERROR `ModuleNotFoundError: No module named 'tools.bench_usb'`.

- [ ] **Step 3: Implement the Mac side** `tools/bench_usb.py`

```python
"""USB CDC throughput benchmark, Mac side (slice 0 of the buddy-os spec); stdlib only.

Usage: python3 tools/bench_usb.py [/dev/cu.usbmodemXXXX]
Needs firmware/rp2040/bench_usb.py running on the board as main.py. For each size and show
mode it sends BENCH frames and prints per-run stats and the spec's decision.
"""
import binascii
import os
import select
import sys
import termios
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.send_blink import open_raw

SIZES = (28800, 134400)  # a 120x120 region and a full frame, RGB565
FRAMES = 100
REPLY_TIMEOUT_S = 2.0


def payload(n):
    return (bytes(range(256)) * (n // 256 + 1))[:n]


def decide(kb_s):
    if kb_s >= 500:
        return "adopt C: full regions"
    if kb_s >= 150:
        return "adopt C with dirty rectangles only"
    return ("MicroPython CDC is the bottleneck: add a C/viper module, "
            "or stay device-side with clips in flash")


def summarize(durations_s, nbytes, failures):
    ordered = sorted(durations_s)
    n = len(ordered)
    p95 = ordered[(95 * n + 99) // 100 - 1]
    mean = sum(ordered) / n
    return {"frames": n, "failures": failures,
            "ms_mean": mean * 1000, "ms_p95": p95 * 1000,
            "kb_s_mean": nbytes / mean / 1000, "kb_s_p95_worst": nbytes / p95 / 1000}


def write_all(fd, data):
    view = memoryview(data)
    while view:
        view = view[os.write(fd, view):]


def read_line(fd, timeout):
    end, buf = time.monotonic() + timeout, b""
    while not buf.endswith(b"\n"):
        left = end - time.monotonic()
        if left <= 0 or not select.select([fd], [], [], left)[0]:
            return None
        buf += os.read(fd, 256)
    return buf


def run_one(fd, nbytes, show):
    data = payload(nbytes)
    expect = binascii.crc32(data)
    durations, failures = [], 0
    for _ in range(FRAMES):
        start = time.monotonic()
        write_all(fd, f"BENCH {nbytes} {show}\n".encode() + data)
        line = read_line(fd, REPLY_TIMEOUT_S)
        elapsed = time.monotonic() - start
        parts = line.split() if line else []
        if len(parts) == 3 and parts[0] == b"OK" and int(parts[1]) == expect:
            durations.append(elapsed)
        else:
            failures += 1
    return summarize(durations, nbytes, failures) if durations else None, parts


def main(argv):
    path = argv[1] if len(argv) > 1 else "/dev/cu.usbmodem101"
    fd, saved = open_raw(path)
    try:
        for nbytes in SIZES:
            for show in (0, 1):
                stats, last = run_one(fd, nbytes, show)
                print(f"{nbytes} B show={show}:", stats or "no valid reply", "last reply:", last)
                if stats:
                    print("  ->", decide(stats["kb_s_mean"]))
        write_all(fd, b"BENCH 0 0\n")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
        os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

The `last reply` in the printed line is the final iteration's split reply, whose third field is the device's free heap in bytes; record it.

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m unittest tests.test_bench_usb -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Implement the device side** `firmware/rp2040/bench_usb.py`

```python
"""USB CDC receive benchmark, board side. Copy to the board as main.py for the run, then put the
real firmware/rp2040/main.py back. Pair with tools/bench_usb.py on the Mac. See the buddy-os spec."""
import binascii
import gc
import micropython
import select
import sys

from waveshare_lcd import LCD_1inch69

STALL_MS = 200


def recv_into(buf, n, poller):
    """Fill buf[:n] from stdin; False when the stream stalls for STALL_MS."""
    view, got = memoryview(buf), 0
    while got < n:
        if not poller.poll(STALL_MS):
            return False
        k = sys.stdin.buffer.readinto(view[got:n])
        if k:
            got += k
    return True


def run():
    lcd = LCD_1inch69()
    lcd.set_bl_pwm(8192)
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)
    gc.collect()
    print("bench ready; free heap:", gc.mem_free())
    try:
        while True:
            n, show = [int(x) for x in sys.stdin.readline().split()[1:3]]
            if n == 0:
                break
            micropython.kbd_intr(-1)  # 0x03 in the payload must not raise KeyboardInterrupt
            try:
                ok = recv_into(lcd.buffer, n, poller)
            finally:
                micropython.kbd_intr(3)
            if not ok:
                continue  # stalled: no reply, the host counts a failure
            if show:
                lcd.show()
            sys.stdout.write("OK %d %d\n" % (binascii.crc32(memoryview(lcd.buffer)[:n]), gc.mem_free()))
    finally:
        lcd.set_bl_pwm(0)
        micropython.kbd_intr(3)


run()
```

Header lines that fail to parse raise `ValueError`/`IndexError` and end the run with a traceback; Ctrl-C works between frames because `kbd_intr(3)` is restored.

- [ ] **Step 6: Run the benchmark on the board** (manual; do not skip, the spec's decision depends on it)

1. In Thonny, stop the blink (Ctrl-C). Copy `firmware/rp2040/bench_usb.py` to the board as `main.py`.
2. Close Thonny so it releases the port, unplug and replug the board. It boots into the benchmark.
3. Run: `python3 tools/bench_usb.py` (use the port from `ls /dev/cu.usbmodem*`).
4. Expected: four result lines (28,800 B and 134,400 B, each with show 0 and 1), each with `failures: 0` and a decision. A line of `no valid reply` means the device stalled or crashed: record it, replug, and note it as a finding rather than retrying blindly.
5. Cable-pull test: start `python3 tools/bench_usb.py`, unplug the cable mid-run, replug, wait 3 s, rerun. Expected: the rerun works without replugging twice (the 200 ms stall rule frees the device). Record the outcome either way.
6. Restore: copy `firmware/rp2040/main.py` back to the board as `main.py` and confirm the blink returns.

- [ ] **Step 7: Record results.** Append to `docs/hardware/bringup-log.md` a section `## 2026-11-13 USB CDC throughput (slice 0)` with: the four result lines verbatim, the decision each produced, the free-heap figure from the last reply, and the cable-pull outcome. State plainly what was not measured (anything skipped).

- [ ] **Step 8: Commit**

```bash
git add firmware/rp2040/bench_usb.py tools/bench_usb.py tests/test_bench_usb.py docs/hardware/bringup-log.md
git commit -m "feat(bench): measure USB CDC frame throughput on the RP2040"
```

---

### Task 7: Status docs

**Files:**
- Modify: `README.md` (the "Communication" row of the table)
- Modify: `docs/superpowers/specs/2026-11-12-buddy-os-design.md` (slice status line)

- [ ] **Step 1:** In `README.md`, change the Communication row's status cell to: "Codec, line transport and the Buddy OS core (`daemon/arbiter.py`, `reconciler.py`, `host.py`) tested without hardware; no module is wired to the real port yet. USB throughput result: see the bring-up log".
- [ ] **Step 2:** In the spec, add under "Build order and tests" the line: `Status 2026-11-13: slices 0 and 1 implemented per docs/superpowers/plans/2026-11-13-buddy-os-core.md; the slice 0 result and its decision are in docs/hardware/bringup-log.md.` Only add this after Task 6 step 7 actually recorded a result.
- [ ] **Step 3:** Run `python3 -m unittest discover -s tests -v 2>&1 | tail -3`; expected `OK`.
- [ ] **Step 4: Commit**

```bash
git add README.md docs/superpowers/specs/2026-11-12-buddy-os-design.md
git commit -m "docs: record Buddy OS core status"
```

---

## Out of scope (next plan, slice 2 onward)

Wiring `Host` to the real serial port with a reader loop and `asyncio` runner, the `idle` and `break_reminder` modules (replacing `tools/buddy_service.py`), touch events, frame leases, badges, and every later module. Slice 4's shape depends on the Task 6 result.

## Self-review notes

- Spec coverage: reconciler and `pick` (Tasks 2-3), presence (Task 2, 4), `hello`/`boot_id` resync and caps (Tasks 1, 4, 5), crash guard (Task 4), alert gap (Tasks 2, 4), pin (Task 2), benchmark with show timing and cable-pull (Task 6), docs updates (Tasks 1, 5, 7). Deferred by design: touch, leases, badges, modules (slices 2-5).
- Type names checked across tasks: `Slot`, `pick`, `visible_slots`, `ALERT_GAP_S` (Task 2) are used unchanged in Task 4; `Reconciler.diff/resync`, `revert`, `PING`, `HEARTBEAT_S` (Task 3) likewise; `handle(text, gaze, hello)` and `make_hello` (Task 5).
- Known corner: `revert("barN")` sets the value to 0 rather than hiding the bar (no such protocol message).
