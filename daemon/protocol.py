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


def _check(msg):
    if not isinstance(msg, dict):
        raise ValueError("message must be a JSON object")
    if type(msg.get("v")) is not int or msg["v"] != VERSION:
        raise ValueError(f"unsupported version {msg.get('v')!r}, expected {VERSION}")
    t = msg.get("t")
    if not isinstance(t, str) or t not in SPEC:
        raise ValueError(f"unknown type {t!r}")
    req, opt = SPEC[t]
    for k in req:
        if k not in msg:
            raise ValueError(f"{t}: missing field {k!r}")
    for k, val in msg.items():
        if k in ("v", "t"):
            continue
        check = req.get(k) or opt.get(k)
        if check is None:
            raise ValueError(f"{t}: unknown field {k!r}")
        if not check(val):
            raise ValueError(f"{t}: bad value for {k!r}: {val!r}")
    return msg


def encode(msg: dict) -> bytes:
    _check(msg)
    line = json.dumps(msg, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
    if len(line) > MAX_LINE:
        raise ValueError(f"line is {len(line)} bytes, max {MAX_LINE}")
    return line


def decode(line: bytes) -> dict:
    if len(line) > MAX_LINE:
        raise ValueError(f"line is {len(line)} bytes, max {MAX_LINE}")
    try:
        msg = json.loads(line)
    except ValueError as e:  # includes UnicodeDecodeError
        raise ValueError(f"invalid JSON: {e}") from None
    return _check(msg)


class Watchdog:
    """Device-side rule, mirrored here for tests/sim: feed() on every message."""

    def __init__(self, timeout=WATCHDOG_S, clock=time.monotonic):
        self.timeout, self.clock = timeout, clock
        self.last = clock()

    def feed(self):
        self.last = self.clock()

    def expired(self):
        return self.clock() - self.last > self.timeout
