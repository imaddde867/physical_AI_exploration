"""Feed the native macOS viewer without reducing the 240x280 source image."""
import shutil
import subprocess
import sys
import time
from pathlib import Path

from sim.screen import HEIGHT, WIDTH, Screen


def frame_bytes(screen: Screen) -> bytes:
    return bytes.fromhex("".join(color[1:] for row in screen.rows() for color in row))


def run(app, args) -> int:
    if not shutil.which("swift"):
        print("The Retina viewer needs Apple's Swift tools (xcode-select --install).", file=sys.stderr)
        return 2
    command = ["swift", str(Path(__file__).with_name("macos_viewer.swift")),
               str(WIDTH), str(HEIGHT), str(args.width_mm), str(args.ppi or 0), str(args.scale)]
    screen = Screen()
    with subprocess.Popen(command, stdin=subprocess.PIPE) as viewer:
        try:
            start = time.monotonic()
            count = 0
            while viewer.poll() is None:
                tick = time.monotonic()
                app.update(screen, (tick - start) * 1000)
                data = frame_bytes(screen)
                try:
                    viewer.stdin.write(data)
                    viewer.stdin.flush()
                except BrokenPipeError:
                    break  # Closing the window closes the frame stream.
                count += 1
                if args.frames and count >= args.frames:
                    break
                time.sleep(max(0, 1 / args.fps - (time.monotonic() - tick)))
        except Exception as exc:
            print(f"mini-app raised: {exc!r}", file=sys.stderr)
            viewer.terminate()
            return 3
        finally:
            try:
                viewer.stdin.close()
            except BrokenPipeError:
                pass
        return viewer.wait()
