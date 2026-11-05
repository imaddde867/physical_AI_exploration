import io
import unittest

from daemon.link import Link


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
        with self.assertRaises(ValueError):
            Link(io.BytesIO(b"x" * 600 + b"\n")).recv()


if __name__ == "__main__":
    unittest.main()
