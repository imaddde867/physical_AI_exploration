"""The service sends gaze every beat and blinks on schedule; only documented messages are sent."""
import os
import unittest

from daemon import protocol
from tools.buddy_service import serve


class ServeTests(unittest.TestCase):
    def test_gazes_and_blinks_on_schedule(self):
        read_fd, write_fd = os.pipe()
        now = [0.0]
        beats = [0]

        def sleep(s):
            now[0] += s
            beats[0] += 1

        serve(write_fd, clock=lambda: now[0], sleep=sleep, until=lambda: beats[0] >= 5)
        os.close(write_fd)
        with os.fdopen(read_fd, "rb") as port:
            msgs = [protocol.decode(line) for line in port.read().splitlines()]
        gaze = [m for m in msgs if "x" in m]
        self.assertEqual(len(gaze), 5)
        self.assertTrue(all(-1 <= m["x"] <= 1 and -1 <= m["y"] <= 1 for m in gaze))
        self.assertEqual([m["blink"] for m in msgs if "blink" in m], [True, False])


if __name__ == "__main__":
    unittest.main()
