"""The macOS sender writes the two documented messages and nothing else."""
import os
import unittest

from daemon import protocol
from tools.send_blink import acks, blink_lines, send


OK = b'{"v":1,"t":"ok"}\n'


class SendBlinkTests(unittest.TestCase):
    def test_blink_lines_are_the_documented_face_messages(self):
        close, open_ = blink_lines()
        self.assertEqual(protocol.decode(close), {"v": 1, "t": "face", "blink": True})
        self.assertEqual(protocol.decode(open_), {"v": 1, "t": "face", "blink": False})

    def test_both_lines_reach_the_port(self):
        read_fd, write_fd = os.pipe()
        send(write_fd, blink_lines(), hold_s=0)
        os.close(write_fd)
        with os.fdopen(read_fd, "rb") as port:
            lines = port.read().splitlines()
        self.assertEqual([protocol.decode(line) for line in lines],
                         [{"v": 1, "t": "face", "blink": True},
                          {"v": 1, "t": "face", "blink": False}])

    def test_each_ok_counts_and_nothing_else_does(self):
        self.assertEqual(acks(OK * 2), 2)  # both commands acknowledged
        self.assertEqual(acks(OK), 1)  # a lost second acknowledgement is not success
        self.assertEqual(acks(OK + b'{"v":1,"t":"err","code":"unsupported"}\n'), 1)
        self.assertEqual(acks(b"MicroPython v1.22.2 on 2024-02-22\r\n" + OK * 2), 2)
        self.assertEqual(acks(b"MicroPython v1.22.2 on 2024-02-22\r\n"), 0)
        self.assertEqual(acks(b'{"v":1,"t":"o'), 0)  # a truncated line is not a reply


if __name__ == "__main__":
    unittest.main()
