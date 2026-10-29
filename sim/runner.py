"""Run a mini-app live in a tkinter window shaped like the V2 AMOLED view.

tkinter imports lazily so headless test suites can import this module.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path

from sim.screen import WIDTH, HEIGHT, Screen

UPDATE_CONTRACT = "mini-app must define update(screen, t_ms)"


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


def frames_per_second(timestamps: list[float], window_ms: float = 1000.0) -> int:
    if not timestamps:
        return 0
    newest = timestamps[-1]
    return sum(t > newest - window_ms for t in timestamps)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a mini-app on a pixel-exact simulated V2 screen")
    parser.add_argument("app", help="path to the mini-app module (defining update(screen, t_ms))")
    parser.add_argument("--fps", type=int, default=30, help="frame cap, default 30")
    parser.add_argument("--scale", type=int, default=1, help="integer window zoom, default 1")
    parser.add_argument("--frames", type=int, default=0, help="stop after N frames; 0 = until window close")
    args = parser.parse_args(argv)
    args.scale = max(args.scale, 1)

    app = load_app(args.app)

    import tkinter as tk

    root = tk.Tk()
    root.title(f"sim · {Path(args.app).name}")
    viewer = tk.PhotoImage(width=WIDTH, height=HEIGHT)
    canvas = tk.Canvas(root, width=WIDTH * args.scale, height=HEIGHT * args.scale, highlightthickness=0)
    canvas.pack()
    status = tk.Label(root, text="fps 0 · t 0 ms")
    status.pack()

    screen = Screen()
    timestamps: list[float] = []
    t0 = time.perf_counter_ns()
    period = 1.0 / max(args.fps, 1)
    item: list[int] = []
    shown: list[object] = [viewer]  # hold the displayed PhotoImage or Tk GC repaints a dead name

    def draw(frame: int, t_ms: float) -> None:
        app.update(screen, t_ms)
        viewer.put("\n".join("{" + " ".join(r) + "}" for r in screen.rows()))
        image: object = viewer
        if args.scale > 1:
            image = viewer.zoom(args.scale)
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
        draw(len(timestamps), t_ms)
        timestamps.append(t_ms)
        slept = (time.perf_counter_ns() - start) / 1e9
        if slept < period:
            time.sleep(period - slept)
        if args.frames and len(timestamps) >= args.frames:
            root.destroy()
        else:
            root.after(1, tick)

    root.after(1, tick)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
