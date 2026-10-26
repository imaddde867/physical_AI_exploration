import contextlib
import io
import unittest
from macdesk.demo import run_simulated


class DemoTests(unittest.TestCase):
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
