import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SimRunnerTests(unittest.TestCase):
    def test_demo_app_loads(self):
        from sim.runner import load_app
        app = load_app(str(ROOT / "experiments/hello_buddy.py"))
        self.assertTrue(callable(app.update))

    def test_runner_import_is_headless(self):
        import sim.runner
        self.assertNotIn("tkinter", sys.modules)

    def test_missing_update_message(self):
        import tempfile
        from sim.runner import load_app
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir) / "sim_no_update_test.py"
            tmp.write_text("x = 1\n")
            with self.assertRaises(ValueError) as ctx:
                load_app(str(tmp))
        self.assertEqual(str(ctx.exception), "mini-app must define update(screen, t_ms)")

    def test_frames_per_second(self):
        from sim.runner import frames_per_second
        self.assertEqual(frames_per_second([100.0, 1050.0, 1200.0], window_ms=600.0), 2)

    def test_main_reports_missing_update_without_traceback(self):
        import contextlib
        import io
        import tempfile
        from sim.runner import UPDATE_CONTRACT
        from sim.runner import main
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir) / "sim_no_update_test.py"
            tmp.write_text("x = 1\n")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main([str(tmp)])
        self.assertEqual(exit_code, 2)
        self.assertEqual(stderr.getvalue(), UPDATE_CONTRACT + "\n")

    def test_main_reports_missing_app_file(self):
        import contextlib
        import io
        import tempfile
        from sim.runner import main
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = str(Path(tmp_dir) / "sim_absent_test.py")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main([missing])
        self.assertEqual(exit_code, 2)
        self.assertIn(missing, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
