import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SimRunnerTests(unittest.TestCase):
    def test_runner_import_is_headless(self):
        import sim.runner
        self.assertNotIn("tkinter", sys.modules)

    def test_missing_update_message(self):
        import tempfile
        from sim.runner import load_app
        tmp = Path(tempfile.gettempdir()) / "sim_no_update_test.py"
        tmp.write_text("x = 1\n")
        with self.assertRaises(ValueError) as ctx:
            load_app(str(tmp))
        self.assertEqual(str(ctx.exception), "mini-app must define update(screen, t_ms)")

    def test_frames_per_second(self):
        from sim.runner import frames_per_second
        self.assertEqual(frames_per_second([100.0, 1050.0, 1200.0], window_ms=600.0), 2)


if __name__ == "__main__":
    unittest.main()
