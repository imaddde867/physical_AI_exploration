"""Exercise the real Python-to-AppKit frame stream, including EOF shutdown."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == "darwin", "requires macOS AppKit")
class MacOSSmokeTests(unittest.TestCase):
    def test_frame_render_and_shutdown(self):
        command = [sys.executable, "-m", "sim.runner", "experiments/hello_buddy.py",
                   "--frames", "1", "--scale", "1"]
        # The runner waits for the viewer and propagates its exit status.
        with subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, start_new_session=True) as runner:
            try:
                stdout, stderr = runner.communicate(timeout=120)
            except subprocess.TimeoutExpired:
                # Kill the whole session so a stuck Swift viewer cannot outlive the test.
                try:
                    os.killpg(runner.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                stdout, stderr = runner.communicate()
                self.fail(f"Runner/viewer did not exit within 120 seconds.\n{stdout}\n{stderr}")
            self.assertEqual(runner.returncode, 0, f"{stdout}\n{stderr}")
            self.assertIn("viewer: rendered 1 frame(s)", stdout.splitlines(),
                          f"Viewer did not confirm drawing the frame.\n{stdout}\n{stderr}")


if __name__ == "__main__":
    unittest.main()
