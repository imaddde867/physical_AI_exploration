"""MacDesk Buddy host<->device protocol, DRAFT v1. See docs/protocol.md."""
import json
import time

VERSION = 1
MAX_LINE = 512  # bytes, including the trailing newline
MAX_STR = 200
WATCHDOG_S = 5.0  # device blanks after this long with no message

MOODS = ("neutral", "happy", "sad", "sleepy", "surprised", "angry")


def _num(lo, hi):
    def ok(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool) and lo <= v <= hi
    return ok


def _int(lo, hi):
    return lambda v: isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def _str(n):
    return lambda v: isinstance(v, str) and len(v) <= n


# type -> (required fields, optional fields); each field -> validator
SPEC = {
    "face": ({}, {"x": _num(-1, 1), "y": _num(-1, 1),
                  "blink": lambda v: isinstance(v, bool),
                  "mood": lambda v: v in MOODS}),
    "bar": ({"id": _int(0, 7), "value": _int(0, 100)}, {"label": _str(16)}),
    "text": ({"slot": _int(0, 3), "s": _str(MAX_STR)}, {}),
    "brightness": ({"value": _int(0, 100)}, {}),
    "sleep": ({}, {}), "wake": ({}, {}), "ping": ({}, {}),
    # device -> host
    "hello": ({"fw": _str(32), "w": _int(1, 10000), "h": _int(1, 10000)}, {}),
    "ok": ({}, {}),
    "err": ({"code": _str(32)}, {"msg": _str(MAX_STR)}),
}


class ProtocolError(ValueError):
    """A rejected message, carrying the documented `err` code for the reply."""

    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def _check(msg):
    if not isinstance(msg, dict):
        raise ProtocolError("bad_json", "message must be a JSON object")
    if type(msg.get("v")) is not int or msg["v"] != VERSION:
        raise ProtocolError("bad_version",
                            f"unsupported version {msg.get('v')!r}, expected {VERSION}")
    t = msg.get("t")
    if not isinstance(t, str) or t not in SPEC:
        raise ProtocolError("unknown_type", f"unknown type {t!r}")
    req, opt = SPEC[t]
    for k in req:
        if k not in msg:
            raise ProtocolError("bad_field", f"{t}: missing field {k!r}")
    for k, val in msg.items():
        if k in ("v", "t"):
            continue
        check = req.get(k) or opt.get(k)
        if check is None:
            raise ProtocolError("bad_field", f"{t}: unknown field {k!r}")
        if not check(val):
            raise ProtocolError("bad_field", f"{t}: bad value for {k!r}: {val!r}")
    return msg


def encode(msg: dict) -> bytes:
    _check(msg)
    # ASCII-escaped output: MicroPython's json.dumps has no ensure_ascii keyword,
    # and the device runs this same encoder. Escaping round-trips identically.
    line = json.dumps(msg, separators=(",", ":")).encode() + b"\n"
    if len(line) > MAX_LINE:
        raise ProtocolError("too_long", f"line is {len(line)} bytes, max {MAX_LINE}")
    return line


def decode(line: bytes) -> dict:
    if len(line) > MAX_LINE:
        raise ProtocolError("too_long", f"line is {len(line)} bytes, max {MAX_LINE}")
    try:
        msg = json.loads(line)
    except ValueError as e:  # includes UnicodeDecodeError
        raise ProtocolError("bad_json", f"invalid JSON: {e}") from None
    return _check(msg)


class Watchdog:
    """Liveness only: feed() after valid messages; explicit sleep is separate."""

    def __init__(self, timeout=WATCHDOG_S, clock=None):
        self.timeout = timeout
        # Host-side only. MicroPython has no time.monotonic; the ticks_ms fallback
        # exists so the device can import this module, not so it can time out.
        self.clock = clock or getattr(time, "monotonic", None) or time.ticks_ms
        self.last = self.clock()

    def feed(self):
        self.last = self.clock()

    def expired(self):
        return self.clock() - self.last > self.timeout
