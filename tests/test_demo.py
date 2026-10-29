import contextlib
import io
import types
import unittest
from unittest.mock import MagicMock, patch
from macdesk.demo import run_device, run_simulated


class DemoTests(unittest.TestCase):
    def run_serial(self, reads, watch=False):
        device = MagicMock()
        device.__enter__.return_value = device
        device.readline.side_effect = reads
        serial = types.SimpleNamespace(Serial=MagicMock(return_value=device))
        stream = io.StringIO()
        with patch.dict("sys.modules", {"serial": serial}), patch("macdesk.demo.time.sleep"), contextlib.redirect_stdout(stream):
            run_device("test-port", "happy", watch=watch)
        return stream.getvalue()

    def test_device_ack_split_across_timeout(self):
        output = self.run_serial([b'{"type":"ack",', b'', b'"face":"happy"}\n'])
        self.assertIn("'type': 'ack', 'face': 'happy'", output)

    def test_watch_event_split_across_timeout(self):
        output = self.run_serial([
            b'{"type":"ack","face":"happy"}\n',
            b'{"type":"event",', b'', b'"name":"shake"}\n', KeyboardInterrupt,
        ], watch=True)
        self.assertIn("'type': 'event', 'name': 'shake'", output)
        self.assertIn("Stopped.", output)

    def test_oversize_response_rejected(self):
        with self.assertRaisesRegex(ValueError, "response exceeds"):
            self.run_serial([b'x' * 513])

    def test_incomplete_ack_times_out(self):
        with self.assertRaisesRegex(TimeoutError, "no matching acknowledgement"):
            self.run_serial([b'{"type":"ack",'] + [b''] * 7)

    def test_device_error_still_raises(self):
        with self.assertRaisesRegex(RuntimeError, "device error"):
            self.run_serial([b'{"type":"error","reason":"invalid_face"}\n'])

    def test_simulation_ack(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            run_simulated("happy")
        self.assertIn('"type": "ack", "face": "happy"', stream.getvalue())

    def test_simulated_imu_event_labeled(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            run_simulated("neutral", watch=True)
        self.assertIn('"name": "shake"', stream.getvalue())
        self.assertIn("Simulated event only", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
