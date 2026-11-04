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

    def test_real_scale(self):
        from sim.runner import PANEL_WIDTH_MM, real_scale, zoom_steps
        from sim.screen import WIDTH
        self.assertAlmostEqual(real_scale(PANEL_WIDTH_MM, 127) * WIDTH / 127 * 25.4,
                               PANEL_WIDTH_MM)
        self.assertAlmostEqual(real_scale(25.4, 100, 100), 1.0)
        self.assertEqual(zoom_steps(0.658), (2, 3))
        self.assertEqual(zoom_steps(2.0), (2, 1))

    def test_native_frames_preserve_every_source_pixel(self):
        from sim.macos import frame_bytes
        from sim.screen import HEIGHT, WIDTH, Screen
        screen = Screen()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                screen.set_pixel(x, y, (255, 255, 255) if (x + y) % 2 else (0, 0, 0))
        data = frame_bytes(screen)
        self.assertEqual(len(data), WIDTH * HEIGHT * 3)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                offset = (y * WIDTH + x) * 3
                self.assertEqual(data[offset:offset + 3],
                                 b"\xff\xff\xff" if (x + y) % 2 else b"\0\0\0")

    def test_rejects_invalid_display_parameters(self):
        import contextlib
        import io
        from sim.runner import main
        for flag, value in (("--ppi", "0"), ("--ppi", "nan"), ("--width-mm", "-1"),
                            ("--scale", "inf"), ("--fps", "0"), ("--frames", "-1")):
            with self.subTest(flag=flag, value=value), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main([str(ROOT / "experiments/hello_buddy.py"), flag, value])
                self.assertEqual(error.exception.code, 2)

    def test_native_viewer_reports_application_errors(self):
        import contextlib
        import io
        from types import SimpleNamespace
        from unittest.mock import Mock, patch
        from sim.macos import run
        args = SimpleNamespace(width_mm=27.972, ppi=None, scale=0, fps=30, frames=1)
        for error in (ValueError("bad app"), BrokenPipeError("app I/O failed")):
            app = Mock()
            app.update.side_effect = error
            with patch("sim.macos.shutil.which", return_value="/usr/bin/swift"), \
                    patch("sim.macos.subprocess.Popen") as process:
                viewer = process.return_value.__enter__.return_value
                viewer.poll.return_value = None
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    self.assertEqual(run(app, args), 3)
                self.assertIn("mini-app raised", stderr.getvalue())
                viewer.terminate.assert_called_once()

    def test_face_fits_and_blinks_on_prototype_display(self):
        from sim.runner import load_app
        from sim.screen import HEIGHT, WIDTH, Screen
        app = load_app(str(ROOT / "experiments/hello_buddy.py"))
        screen = Screen()
        counts = []
        for t_ms in (200, 4000, 4200):  # open, blink, open again
            app.update(screen, t_ms)
            lit = [(x, y) for y, row in enumerate(screen.rows())
                   for x, color in enumerate(row) if color != "#000000"]
            self.assertTrue(lit)
            self.assertGreater(min(x for x, y in lit), 0)
            self.assertLess(max(x for x, y in lit), WIDTH - 1)
            self.assertGreater(min(y for x, y in lit), 0)
            self.assertLess(max(y for x, y in lit), HEIGHT - 1)
            left = sum(x < WIDTH // 2 for x, y in lit)
            self.assertEqual(left, len(lit) - left)
            self.assertTrue(all(row[WIDTH // 2] == "#000000" for row in screen.rows()))
            counts.append(len(lit))
        self.assertLess(counts[1], counts[0])
        self.assertEqual(counts[0], counts[2])

    def test_diagnostic_patterns_render_at_prototype_resolution(self):
        from sim.runner import load_app
        from sim.screen import HEIGHT, WIDTH, Screen
        for filename in ("toy_motion_demo.py", "toy_quality_ramp.py"):
            app = load_app(str(ROOT / "experiments" / filename))
            screen = Screen()
            for t_ms in (0, 3000, 6000, 9000):
                with self.subTest(app=filename, t_ms=t_ms):
                    app.update(screen, t_ms)
                    self.assertEqual(len(screen.rows()), HEIGHT)
                    self.assertTrue(all(len(row) == WIDTH for row in screen.rows()))
                    self.assertTrue(any(color != "#000000" for row in screen.rows()
                                        for color in row))

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
