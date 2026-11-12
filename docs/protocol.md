# MacDesk Buddy serial protocol (DRAFT v1)

Status, 2026-11-12: `daemon/protocol.py` is the shared codec, and the RP2040 prototype implements `face` (`blink`, `x`, `y`) and `ping` from it. `x`/`y` shift both eyes by up to 10 px, in whole pixels with no easing. Every other valid message, including any `face` carrying `mood`, is answered `err` (`unsupported`). The host daemon, keepalive scheduling, and reconnect behavior are still not implemented. The ordered bench prototype uses an integrated RP2040; see the [product brief](product-brief.md).

Proposed Mac service <-> display controller over USB CDC serial. One JSON object per line (UTF-8, `\n` terminated).
Every message has `v` (protocol version, currently `1`) and `t` (type). Reference: `daemon/protocol.py`.

## Host -> device

| t | fields | notes |
|---|---|---|
| `face` | `x`,`y` float -1..1 (gaze); `blink` bool; `mood` neutral/happy/sad/sleepy/surprised/angry | all optional; omitted fields keep their last value. Idle animation runs on the device. `blink:true` holds the eyelids closed; see the hold rule below |
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
- Valid messages the device cannot render yet are answered `err` (`unsupported`). The RP2040 blink prototype does this for `bar`, `text`, `brightness`, `sleep`, `wake`, and `face` fields other than `blink`.

## Device implementation, 2026-11-12

The RP2040 prototype reads lines from USB CDC with `select.poll(0)` in the same
20 ms loop that animates the eyes: the autonomous blink keeps running while a
host is connected, and input is consumed in bounded slices of at most 256
characters per tick, with at most one reply written per tick. This bounds the
work per tick; frame timing under a flood has not been measured. A partial line
with no input for 1 s is discarded, so a sender that dies mid-line does not
corrupt the next connection's first command (one that connects sooner than that
can still get a `bad_json` for it). A host that stays connected but
stops reading its port can still stall a single reply write for the USB transmit
timeout; nothing in the prototype can prevent that. `daemon/protocol.py` is
copied to the board's root as `protocol.py`, so validator and encoder behaviour
cannot drift between the two sides. Replies are ASCII JSON, one line per
received line.

### Blink hold rule

`blink:true` holds the eyes closed and `blink:false` releases them immediately:
the eyes reopen on the next 20 ms tick and the idle four-second cycle restarts
from the release. A hold that lasts **2000 ms** releases itself, so a sender that
dies mid-blink cannot leave the eyes shut. This timeout is a transport
safeguard, not part of the sender's blink: the sender still chooses the visible
duration by sending `true`, waiting, then `false`.

### Not implemented on the device yet

- `hello` on connect, and `hello` in reply to a first `ping`.
- The `WATCHDOG_S` blanking rule and the explicit `sleep`/`wake` latch.

## Failure behaviour

- Explicit sleep: `sleep` latches the panel off until `wake`. Valid `ping` messages update liveness without clearing this latch. Valid face/state commands may update hidden state while asleep. `wake` clears the latch and restores the stored desired brightness; it does not replace that brightness value.
- Link drop / daemon dead: the device separately blanks after no valid message for `WATCHDOG_S = 5` s. The daemon sends at least one valid message every 2 s. The next valid message clears timeout blanking, but an explicit sleep latch keeps the panel off. Invalid messages do not count as keepalive.
- The Python `Watchdog` only tracks liveness; it does not implement the sleep latch, display blanking, or brightness state. Its caller must feed it only after validation.
- Mac sleep: the daemon sends `sleep` before sleeping; on wake it sends `wake`.
- On (re)connect the device sends `hello`; the daemon then resends full state (face, bars, text, brightness).

## Out of scope

Raw frames or pixel data. USB 2.0 and the CDC link are for small commands only; the device renders the face and widgets locally.
