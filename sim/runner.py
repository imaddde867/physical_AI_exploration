"""Run a mini-app live at the 240x280 prototype display's size.

tkinter imports lazily so headless test suites can import this module.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import sys
import time
from collections import deque
from fractions import Fraction
from pathlib import Path

from sim.screen import WIDTH, HEIGHT, Screen

UPDATE_CONTRACT = "mini-app must define update(screen, t_ms)"
FPS_WINDOW_MS = 1000.0  # reporting window; also the history slice kept in tick()


def load_app(path: str) -> object:
    spec = importlib.util.spec_from_file_location("sim_app", Path(path).resolve())
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load mini-app: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["sim_app"] = module
    spec.loader.exec_module(module)
    if not callable(getattr(module, "update", None)):
        raise ValueError(UPDATE_CONTRACT)
    return module


PANEL_WIDTH_MM = 27.972  # nominal active width of Waveshare's 1.69-inch panel; verify on delivery
MAC_PPI = 127.0  # fallback for non-macOS Tk; the native macOS viewer reads the active display


def real_scale(width_mm: float, ppi: float, width_px: int = WIDTH) -> float:
    """Window points per panel pixel so the panel shows at width_mm on a screen of ppi points/inch."""
    return width_mm / 25.4 * ppi / width_px


def zoom_steps(scale: float) -> tuple[int, int]:
    """(zoom, subsample) pair approximating scale; Tk only resizes photos by integer ratios."""
    f = Fraction(scale).limit_denominator(8)
    return f.numerator, f.denominator


def frames_per_second(timestamps: list[float], window_ms: float = FPS_WINDOW_MS) -> int:
    if not timestamps:
        return 0
    newest = timestamps[-1]
    return sum(t > newest - window_ms for t in timestamps)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a mini-app on a simulated 240x280 screen")
    parser.add_argument("app", help="path to the mini-app module (defining update(screen, t_ms))")
    parser.add_argument("--fps", type=int, default=30, help="frame cap, default 30")
    parser.add_argument("--width-mm", type=float, default=PANEL_WIDTH_MM, help="physical panel width, default 27.972")
    parser.add_argument("--ppi", type=float,
                        help="override logical points per inch for ruler calibration; macOS detects it automatically")
    parser.add_argument("--scale", type=float, default=0, help="override real size (1 = one logical point per source pixel)")
    parser.add_argument("--frames", type=int, default=0, help="stop after N frames; 0 = until window close")
    args = parser.parse_args(argv)
    if (args.fps <= 0 or args.frames < 0 or not math.isfinite(args.width_mm) or args.width_mm <= 0
            or not math.isfinite(args.scale) or args.scale < 0
            or (args.ppi is not None and (not math.isfinite(args.ppi) or args.ppi <= 0))):
        parser.error("fps and dimensions must be positive; scale and frames must be non-negative")

    try:
        app = load_app(args.app)
    except (ValueError, OSError) as exc:  # expected load failure: bad path or missing update
        print(exc, file=sys.stderr)
        return 2

    if sys.platform == "darwin":
        from sim.macos import run
        return run(app, args)

    args.ppi = args.ppi or MAC_PPI
    scale = args.scale if args.scale > 0 else real_scale(args.width_mm, args.ppi)
    zoom, sub = zoom_steps(scale)
    size = (round(WIDTH * zoom / sub), round(HEIGHT * zoom / sub))

    import tkinter as tk

    root = tk.Tk()
    root.title(f"sim · {Path(args.app).name} · {size[0] / args.ppi * 25.4:.0f} mm wide" if args.scale <= 0
               else f"sim · {Path(args.app).name} · x{scale:g}")
    viewer = tk.PhotoImage(width=WIDTH, height=HEIGHT)
    canvas = tk.Canvas(root, width=size[0], height=size[1], highlightthickness=0)
    canvas.pack()
    status = tk.Label(root, text="fps 0 · t 0 ms")
    status.pack()

    screen = Screen()
    timestamps: deque[float] = deque()  # only the last FPS_WINDOW_MS, pruned each tick
    frame_count = [0]  # total frames ever drawn; timestamps is a bounded window, not the count
    failure: list[BaseException] = []  # first mini-app error, reported after the window closes
    t0 = time.perf_counter_ns()
    period = 1.0 / max(args.fps, 1)
    item: list[int] = []
    shown: list[object] = [viewer]  # hold the displayed PhotoImage or Tk GC repaints a dead name

    def draw(frame: int, t_ms: float) -> None:
        app.update(screen, t_ms)
        viewer.put("\n".join("{" + " ".join(r) + "}" for r in screen.rows()))
        image: object = viewer
        if (zoom, sub) != (1, 1):
            image = viewer.zoom(zoom) if zoom > 1 else viewer
            image = image.subsample(sub) if sub > 1 else image
            shown[0] = image
        if item:
            canvas.itemconfigure(item[0], image=image)
        else:
            item.append(canvas.create_image(0, 0, image=image, anchor="nw"))
        if frame % 10 == 0:
            status.configure(text=f"fps {frames_per_second(timestamps)} · t {int(t_ms)} ms")

    def tick() -> None:
        start = time.perf_counter_ns()
        t_ms = (time.perf_counter_ns() - t0) / 1e6
        try:
            draw(frame_count[0], t_ms)
            timestamps.append(t_ms)
            frame_count[0] += 1
            while timestamps and timestamps[0] <= t_ms - FPS_WINDOW_MS:
                timestamps.popleft()
        except Exception as exc:
            failure.append(exc)
            root.destroy()
            return
        if args.frames and frame_count[0] >= args.frames:
            root.destroy()
        else:  # after(), not sleep(): keeps the window responsive between frames
            elapsed = (time.perf_counter_ns() - start) / 1e9
            root.after(max(1, round((period - elapsed) * 1000)), tick)

    root.after(1, tick)
    root.mainloop()
    if failure:
        print(f"mini-app raised: {failure[0]!r}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
