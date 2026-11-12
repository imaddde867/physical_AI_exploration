# USB command channel for the RP2040 blink prototype

Status, 2026-11-12: approved by the project owner and implemented in the same
change. Small change, so this note records the decisions rather than a full plan.

## Intent

Let the MacBook drive the physical device over the same USB cable it powers it
with, without replacing the temporary Thonny experiment with a throwaway
interface. The wire format is the already-documented one in
[protocol.md](../../protocol.md), so this is the first real host/device
integration rather than a second, competing protocol.

Success: run a command on the Mac, see the eyes blink immediately, and confirm
the four-second autonomous blink continues afterwards.

## Goals

- Accept `{"v":1,"t":"face","blink":true|false}` and answer `ok` or `err`.
- Answer `ping` (liveness check without moving the eyes).
- Keep the 140 ms blink every four seconds when no host is talking.
- Read USB serial without blocking the animation loop.
- Bound memory: one line, no unbounded buffers.
- Survive malformed input, NUL bytes, overlong lines, and a sender that dies.
- A macOS sender with no new dependencies.

## Non-goals

- `hello`, `bar`, `text`, `brightness`, `sleep`, `wake` on the device. They are
  valid protocol messages and get `err: unsupported`.
- The `WATCHDOG_S` blanking rule and the sleep latch. Not implemented yet.
- Any reply-level framing beyond one JSON object per line.

## Decisions

**One protocol module, not a device copy.** `daemon/protocol.py` stays the single
source of truth and is copied to the board's root as `protocol.py` at deploy
time. Two edits make that possible without duplicating validators:

1. `Watchdog` resolves its default clock (`time.monotonic`) at construction, not
   at import, so the module imports on MicroPython, which lacks it. There is no
   `ticks_ms` fallback: it counts milliseconds and wraps, so it would silently
   break a seconds timeout. The class stays unused on the device.
2. `encode` drops `ensure_ascii=False`. ASCII-escaped output is still valid JSON
   and round-trips identically (covered by the existing `héllo ♪` test), and it
   is the one keyword MicroPython's `json.dumps` does not accept.

**Real error codes.** `protocol.ProtocolError` carries the documented `err` code
(`bad_json`, `bad_version`, `unknown_type`, `bad_field`, `too_long`) instead of
the device sniffing message text. It subclasses `ValueError`, so existing host
tests are unchanged.

**Blink is a latch with a 2 s release.** `blink:true` holds the eyelids closed
and `blink:false` releases them; the sender does true, 140 ms, false, which
reproduces the autonomous blink. A hold that lasts 2000 ms releases itself, so a
sender that dies mid-blink cannot leave the eyes shut. This timeout is a device
behaviour the protocol document now states explicitly.

**Bounded input.** `LineReader` keeps at most `MAX_LINE` bytes of UTF-8, drops the
rest of an overlong line to the next newline, and answers `too_long`. At most
256 characters are consumed per 20 ms tick, which bounds input work per tick;
frame timing under a flood is not measured. A partial line with no input for 1 s
is discarded so a dead sender cannot corrupt the next connection.

**Sender uses `termios` and `os`.** Same two messages the device accepts, no
`pyserial` dependency. It prints the device's reply so the link is confirmed
without watching the screen.

## Left to the builder

- Verify on the board that MicroPython 1.22.2 imports the copied `protocol.py`
  (f-strings with `!r`, `raise ... from`, `json.loads`), and that `select.poll`
  reports the USB serial stdin.
- Confirm the REPL does not swallow the first characters typed into the port
  while `main.py` runs.
