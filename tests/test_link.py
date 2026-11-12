import io
import unittest

from daemon.link import DISCARD_READS, Link
from daemon.protocol import MAX_LINE


class LinkTests(unittest.TestCase):
    def test_roundtrip_eof_and_bad_line(self):
        out = io.BytesIO()
        Link(out).send({"v": 1, "t": "ping"})
        link = Link(io.BytesIO(out.getvalue() + b"not json\n"))
        self.assertEqual(link.recv(), {"v": 1, "t": "ping"})
        with self.assertRaises(ValueError):
            link.recv()
        self.assertIsNone(link.recv())

    def test_overlong_line_rejected(self):
        link = Link(io.BytesIO(b"x" * 600 + b"\n" + b'{"v":1,"t":"ping"}\n'))
        with self.assertRaises(ValueError):
            link.recv()
        self.assertEqual(link.recv(), {"v": 1, "t": "ping"})  # one error per overlong line

    def test_overlong_line_without_newline_stops_reading(self):
        link = Link(io.BytesIO(b"x" * 600))  # EOF where the newline should be
        with self.assertRaises(ValueError):
            link.recv()
        self.assertIsNone(link.recv())

        class Endless:  # would wait forever if recv() hunted for a newline
            reads = 0
            def readline(self, _limit):
                self.reads += 1
                return b"x" * (MAX_LINE + 1)

        stream = Endless()
        with self.assertRaises(ValueError):
            Link(stream).recv()
        self.assertEqual(stream.reads, 1 + DISCARD_READS)


if __name__ == "__main__":
    unittest.main()
