import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from daemon.protocol import (MAX_LINE, MAX_STR, ProtocolError, Watchdog, decode,
                             encode)


def m(t, **kw):
    return {"v": 1, "t": t, **kw}


class ProtocolTest(unittest.TestCase):
    def test_round_trip(self):
        for msg in (m("face", x=-0.5, y=1, blink=True, mood="happy"),
                    m("bar", id=2, label="Claude", value=73),
                    m("text", slot=0, s="héllo ♪"),
                    m("brightness", value=0), m("sleep"), m("wake"), m("ping"),
                    m("hello", fw="0.1", w=240, h=280), m("ok"),
                    m("err", code="unknown_type")):
            line = encode(msg)
            self.assertTrue(line.endswith(b"\n"))
            self.assertEqual(decode(line), msg)

    def test_rejects(self):
        bad = [
            m("face", x=1.5), m("face", x=True), m("face", mood="angryish"),
            m("face", blink=1), m("bar", id=8, value=1), m("bar", id=0),
            m("bar", id=0, value=101), m("bar", id=0, value=1, label="x" * 17),
            m("text", slot=4, s=""), m("text", slot=0, s="x" * (MAX_STR + 1)),
            m("brightness", value=-1), m("ping", extra=1),
            m("nope"), {"t": "ping"}, {"v": 2, "t": "ping"}, [1],
        ]
        for msg in bad:
            with self.assertRaises(ValueError, msg=msg):
                encode(msg)

    def test_max_line(self):
        # 200 chars of 3-byte UTF-8 passes the string check but busts 512 bytes
        with self.assertRaises(ValueError):
            encode(m("text", slot=0, s="€" * MAX_STR))
        with self.assertRaises(ValueError):
            decode(b"x" * (MAX_LINE + 1))

    def test_decode_garbage(self):
        for line in (b"not json\n", b"\xff\xfe\n", b'{"v":1,"t":"zzz"}\n'):
            with self.assertRaises(ValueError):
                decode(line)

    def test_rejects_malformed_envelope(self):
        for line in (b'{"v":true,"t":"ping"}\n', b'{"v":1.0,"t":"ping"}\n',
                     b'{"v":1,"t":[]}\n', b'{"v":1,"t":{}}\n',
                     b'{"v":1,"t":null}\n', b'{"v":1,"t":1}\n'):
            with self.subTest(line=line), self.assertRaises(ValueError):
                decode(line)

    def test_watchdog(self):
        now = [0.0]
        w = Watchdog(timeout=5, clock=lambda: now[0])
        now[0] = 5
        self.assertFalse(w.expired())
        now[0] = 5.1
        self.assertTrue(w.expired())
        w.feed()
        self.assertFalse(w.expired())

    def test_watchdog_refuses_a_millisecond_clock(self):
        # ticks_ms would make the timeout 1000x short and wraps; fail loudly instead.
        with patch("daemon.protocol.time", SimpleNamespace(ticks_ms=lambda: 0)):
            with self.assertRaises(AttributeError):
                Watchdog()

    def test_errors_carry_the_documented_reply_code(self):
        cases = [(b"not json\n", "bad_json"), (b'{"v":2,"t":"ping"}\n', "bad_version"),
                 (b'{"v":1,"t":"zzz"}\n', "unknown_type"),
                 (b'{"v":1,"t":"face","blink":1}\n', "bad_field"),
                 (b"x" * (MAX_LINE + 1), "too_long")]
        for line, code in cases:
            with self.subTest(code=code), self.assertRaises(ProtocolError) as caught:
                decode(line)
            self.assertEqual(caught.exception.code, code)

    def test_encoding_stays_ascii_so_the_device_shares_one_encoder(self):
        line = encode(m("text", slot=0, s="héllo ♪"))
        self.assertTrue(line.isascii())
        self.assertEqual(decode(line)["s"], "héllo ♪")


if __name__ == "__main__":
    unittest.main()
