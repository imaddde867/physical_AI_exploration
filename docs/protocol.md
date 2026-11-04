# MacDesk Buddy serial protocol (DRAFT v1)

Status, 2026-11-04: proposed interface, not a running host/device system. Only the Python codec and watchdog helper exist; transport, firmware, keepalive scheduling, and reconnect behavior below are not implemented. The ordered bench prototype uses an integrated RP2040; see the [product brief](product-brief.md).

Proposed Mac service <-> display controller over USB CDC serial. One JSON object per line (UTF-8, `\n` terminated).
Every message has `v` (protocol version, currently `1`) and `t` (type). Reference: `daemon/protocol.py`.

## Host -> device

| t | fields | notes |
|---|---|---|
| `face` | `x`,`y` float -1..1 (gaze); `blink` bool; `mood` neutral/happy/sad/sleepy/surprised/angry | all optional; omitted fields keep their last value. Idle animation runs on the device |
| `bar` | `id` 0..7, `value` int 0..100, `label` str <=16 (optional) | usage bars (Claude/Codex) |
| `text` | `slot` 0..3, `s` str <=200 chars | lyrics, chat; empty string clears the slot |
| `brightness` | `value` 0..100 | sets desired brightness, retained while blanked |
| `sleep` / `wake` | none | `sleep` latches the panel off until `wake`; `wake` restores desired brightness |
| `ping` | none | keepalive |

## Device -> host

| t | fields | notes |
|---|---|---|
| `hello` | `fw` str, `w`, `h` int | sent on connect (and on host `ping` before first hello) |
| `ok` | none | reply to each valid message |
| `err` | `code` str, `msg` str (optional) | reply to an invalid message |

## Limits

- Line max 512 bytes including `\n`. Longer lines are dropped up to the next `\n` and answered with `err` (`code: "too_long"`).
- Strings counted in characters (<=200 for `text`/`msg`, <=16 for `label`); the 512-byte line cap still applies, so multi-byte text can be shorter.
- Unknown `t`, unknown field, bad type, or out-of-range value: device ignores the message and replies `err` (`unknown_type`, `bad_field`, `bad_version`, `bad_json`). Never crash or blank on bad input.

## Failure behaviour

- Explicit sleep: `sleep` latches the panel off until `wake`. Valid `ping` messages update liveness without clearing this latch. Valid face/state commands may update hidden state while asleep. `wake` clears the latch and restores the stored desired brightness; it does not replace that brightness value.
- Link drop / daemon dead: the device separately blanks after no valid message for `WATCHDOG_S = 5` s. The daemon sends at least one valid message every 2 s. The next valid message clears timeout blanking, but an explicit sleep latch keeps the panel off. Invalid messages do not count as keepalive.
- The Python `Watchdog` only tracks liveness; it does not implement the sleep latch, display blanking, or brightness state. Its caller must feed it only after validation.
- Mac sleep: the daemon sends `sleep` before sleeping; on wake it sends `wake`.
- On (re)connect the device sends `hello`; the daemon then resends full state (face, bars, text, brightness).

## Out of scope

Raw frames or pixel data. USB 2.0 and the CDC link are for small commands only; the device renders the face and widgets locally.
