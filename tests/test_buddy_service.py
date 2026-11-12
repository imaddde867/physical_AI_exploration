"""The service pings every beat and blinks on schedule; only documented messages are sent."""
import os
import unittest

from daemon import protocol
from tools.buddy_service import serve


class ServeTests(unittest.TestCase):
    def test_pings_and_blinks_on_schedule(self):
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
        kinds = [(m["t"], m.get("blink")) for m in msgs]
        self.assertEqual(kinds.count(("ping", None)), 5)
        self.assertEqual([k for k in kinds if k[0] == "face"], [("face", True), ("face", False)])


if __name__ == "__main__":
    unittest.main()
