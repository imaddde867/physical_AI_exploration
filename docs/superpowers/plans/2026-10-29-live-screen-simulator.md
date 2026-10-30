# Live Screen Simulator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run a mini-app (one Python file, `update(screen, t_ms)`) live in a tkinter window that shows the exact 456×280 landscape view with RGB565 quantized colors, so screen ideas can be explored without ESP hardware.

**Architecture:** `sim/screen.py` holds a plain-Python pixel buffer as 280 rows of 456 hex color strings, quantizing 8-bit RGB input through `tools.face_asset.rgb565` and the same round-reconstruction as `assets/amoled-preview.html`. `sim/runner.py` loads the mini-app by path, drives `update(screen, t_ms)` at the requested fps cap, and hands rows to a tkinter viewer (`PhotoImage` + `put`, lazily imported so headless CI stays green. `--scale` zooms each frame via `PhotoImage.zoom`). One demo mini-app under `experiments/`.

**Tech Stack:** Python 3 stdlib (tkinter 8.6), repo helpers `tools.face_asset.rgb565` / `indexed_png`, unittest.

**Spec:** `docs/superpowers/specs/2026-10-29-live-screen-simulator-design.md`

## Global Constraints

- Standard library only; no pip installs.
- `python3 -m unittest discover -s tests -v` must pass headless: **no tkinter or display dependency in `sim/screen.py` or any test import path**; tkinter import lives inside `sim/runner.py`'s viewer/main only.
- Display mapping: WIDTH=456, HEIGHT=280 (constants named `WIDTH`, `HEIGHT` in `sim/screen.py`; mirrors `tools/amoled_face.py`).
- Color contract: input 8-bit RGB → `tools.face_asset.rgb565(color)` → reconstruct channels as in `assets/amoled-preview.html`: `round((v>>11)*255/31), round(((v>>5)&63)*255/63), round((v&31)*255/31)` → store as `#%02x%02x%02x`. Quantize results cached in a dict keyed by the input tuple.
- Out-of-canvas pixels/blits clip silently (no exception, no corruption); zero/negative `w`/`h` are no-ops.
- Mini-app contract: module-level `update(screen, t_ms)`; missing → runner exits with message `mini-app must define update(screen, t_ms)`, not a traceback.
- Conventional commits; minimum change; firmware-v2 and firmware/ untouched.

## Review Focus

- Off-canvas write at e.g. (455,279) or (−3,−3) must clip, not shift/corrupt the buffer → `test_set_pixel_clips` / `test_fill_rect_clips` / `test_blit_clips` (Tasks 1–2).
- Wrong quantization parity: `(255,205,157)` must store exactly the HTML-preview-identical hex string, or hardware preview and sim diverge subtly → `test_quantized_color_matches_html_formula` (Task 1).
- `fill_rect` with `w=0` must not crash or wrap rows → `test_zero_size_noop` (Task 1).
- Mini-app missing `update` must exit with the exact contract message → `test_missing_update_message` (Task 3).
- Importing `sim.runner` must not pull in tkinter (headless CI) → `test_runner_import_is_headless` (Task 3).

---

### Task 1: Screen buffer, quantization, primitives

**Files:**
- Create: `sim/__init__.py` (empty)
- Create: `sim/screen.py`
- Test: `tests/test_sim_screen.py`

**Interfaces:**
- Consumes: `tools.face_asset.rgb565(color: tuple[int,int,int]) -> int`.
- Produces (used by Tasks 2–3 and mini-apps): `class Screen` with
  - `WIDTH = 456`, `HEIGHT = 280` (module constants)
  - `set_pixel(x: int, y: int, rgb: tuple[int,int,int]) -> None`
  - `fill_rect(x: int, y: int, w: int, h: int, rgb: tuple[int,int,int]) -> None`
  - `clear(rgb: tuple[int,int,int]) -> None`
  - `rows() -> list[list[str]]` (HEIGHT rows × WIDTH hex strings)
  - constructor takes no arguments; buffer starts all `"#000000"`.

- [ ] **Step 1: Write the failing tests** in `tests/test_sim_screen.py`:

```python
import unittest
from sim.screen import Screen, WIDTH, HEIGHT
from tools.face_asset import rgb565

def html_hex(color):
    v = rgb565(color)
    return "#%02x%02x%02x" % (round((v >> 11) * 255 / 31),
                              round(((v >> 5) & 63) * 255 / 63),
                              round((v & 31) * 255 / 31))

class SimScreenTests(unittest.TestCase):
    def test_dimensions_and_blank(self):
        s = Screen()
        self.assertEqual(WIDTH, 456); self.assertEqual(HEIGHT, 280)
        rows = s.rows()
        self.assertEqual(len(rows), 280)
        self.assertEqual(len(rows[0]), 456)
        self.assertEqual(rows[0][0], "#000000")

    def test_quantized_color_matches_html_formula(self):
        s = Screen()
        s.set_pixel(10, 10, (255, 205, 157))
        self.assertEqual(s.rows()[10][10], html_hex((255, 205, 157)))

    def test_set_pixel_clips(self):
        s = Screen()
        s.set_pixel(456, 279, (255, 255, 255))  # off right edge
        s.set_pixel(0, 280, (255, 255, 255))    # off bottom
        s.set_pixel(-3, -3, (255, 255, 255))
        self.assertEqual(s.rows()[279][455], "#000000")

    def test_fill_rect_and_zero_size_noop(self):
        s = Screen()
        s.fill_rect(100, 100, 50, 20, (0, 255, 0))
        r, c = html_hex((0, 255, 0)), s.rows()
        self.assertEqual(c[100][100], r); self.assertEqual(c[119][149], r)
        self.assertEqual(c[99][100], "#000000"); self.assertEqual(c[120][100], "#000000")
        s.fill_rect(5, 5, 0, 5, (255, 255, 255))   # w=0
        s.fill_rect(5, 5, 5, 0, (255, 255, 255))   # h=0
        self.assertEqual(s.rows()[5][5], "#000000")

    def test_clear(self):
        s = Screen()
        s.set_pixel(0, 0, (255, 255, 255)); s.clear((10, 20, 30))
        self.assertEqual(s.rows()[0][0], html_hex((10, 20, 30)))

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_sim_screen -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sim'`

- [ ] **Step 3: Implement `sim/screen.py`**

Buffer = list of `HEIGHT` lists of `WIDTH` hex strings, built lazily from a shared color cache; quantization exactly per the Global Constraints formula with a `dict[tuple[int,int,int], str]` cache. `clear` delegates to `fill_rect(0, 0, WIDTH, HEIGHT, rgb)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_sim_screen -v`
Expected: PASS (all)

- [ ] **Step 5: Commit**

```bash
git add sim/__init__.py sim/screen.py tests/test_sim_screen.py
git commit -m "feat(sim): quantized pixel screen primitives"
```

### Task 2: blit_image from repo indexed PNGs

**Files:**
- Modify: `sim/screen.py`
- Test: `tests/test_sim_screen.py` (append `SimBlitTests` class)

**Interfaces:**
- Consumes: `tools.face_asset.indexed_png(source: Path) -> tuple[list[RgbTuple], bytes]` (palette + per-pixel palette indices); `assets/face-idle-240.png` (existing 240×240 indexed PNG).
- Produces: `Screen.blit_image(path: str, x: int, y: int) -> None` — stamps the PNG's palette-mapped pixels at the offset; destination pixels beyond the screen are dropped; a fully off-canvas call is a no-op.

- [ ] **Step 1: Write the failing tests** (same file as Task 1):

```python
from pathlib import Path
from tools.face_asset import indexed_png

ROOT = Path(__file__).resolve().parents[1]

class SimBlitTests(unittest.TestCase):
    def test_blit_puts_face_asset_pixels(self):
        palette, source = indexed_png(ROOT / "assets/face-idle-240.png")
        s = Screen()
        s.blit_image(str(ROOT / "assets/face-idle-240.png"), 10, 20)
        rows = s.rows()
        # top-left pixel of the asset lands at (10,20), quantized like the HTML preview
        self.assertEqual(rows[20][10], html_hex(palette[source[0]]))
        touched = sum(hexv != "#000000" for r in rows for hexv in r)
        self.assertGreater(touched, 1000)

    def test_blit_clips(self):
        s = Screen()
        s.blit_image(str(ROOT / "assets/face-idle-240.png"), 400, 50)   # hangs off right
        s.blit_image(str(ROOT / "assets/face-idle-240.png"), -100, -100) # fully off-canvas
        self.assertLess(sum(hexv != "#000000" for hexv in s.rows()[49]), 456)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_sim_screen -v`
Expected: FAIL — `AttributeError: 'Screen' object has no attribute 'blit_image'`

- [ ] **Step 3: Implement `blit_image` in `sim/screen.py`**

Decode once via `tools.face_asset.indexed_png(Path(path))` (no cache needed for v1; mini-apps may hold the Screen and call repeatedly — caching is this task's only discretionary choice, keep it out).

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_sim_screen -v`
Expected: PASS (all)

- [ ] **Step 5: Commit**

```bash
git add sim/screen.py tests/test_sim_screen.py
git commit -m "feat(sim): blit indexed PNGs onto screen"
```

### Task 3: Runner, tkinter viewer, fps label, demo mini-app

**Files:**
- Create: `sim/runner.py`
- Create: `experiments/__init__.py`? No — plain `experiments/` folder without package marker; demos are loaded by path only.
- Create: `experiments/hello_buddy.py`
- Test: `tests/test_sim_runner.py`

**Interfaces:**
- Consumes: `Screen` API (Tasks 1–2).
- Produces:
  - `sim/runner.load_app(path: str) -> object` — module loaded by absolute path (importlib); raises `ValueError("mini-app must define update(screen, t_ms)")` when module `update` is absent.
  - `sim/runner.frames_per_second(timestamps: list[float], window_ms: float = 1000.0) -> int` — frames whose timestamps fall in the trailing window counted relative to the newest timestamp (`t > max(timestamps) - window_ms`).
  - CLI: `python3 -m sim.runner <app.py> [--fps N] [--scale S] [--frames N]` (`--frames`: stop after N frames; 0 = unlimited. Default fps 30, scale 1.)
  - Window label format: `fps {n} · t {t_ms} ms` (sanity display only).

- [ ] **Step 1: Write the failing tests**

```python
import sys
import unittest
from pathlib import Path

class SimRunnerTests(unittest.TestCase):
    def test_runner_import_is_headless(self):
        import sim.runner
        self.assertNotIn("tkinter", sys.modules)

    def test_missing_update_message(self):
        import tempfile, os
        from sim.runner import load_app
        tmp = Path(tempfile.gettempdir()) / "sim_no_update_test.py"
        tmp.write_text("x = 1\n")
        with self.assertRaises(ValueError) as ctx:
            load_app(str(tmp))
        self.assertEqual(str(ctx.exception), "mini-app must define update(screen, t_ms)")

    def test_frames_per_second(self):
        from sim.runner import frames_per_second
        self.assertEqual(frames_per_second([100.0, 1050.0, 1200.0], window_ms=600.0), 2)
```

(`test_frames_per_second` pins the reference: the trailing window counts frames newer than `max(timestamps) - window_ms`, so [1050.0, 1200.0] are the 2.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_sim_runner -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sim.runner'`

- [ ] **Step 3: Implement `sim/runner.py`**

Structure: `load_app`, `frames_per_second` at module top (stdlib imports only — tkinter stays inside `main()` / `_TkViewer`). Viewer loop: build `PhotoImage(width=WIDTH, height=HEIGHT)`, per frame run `app.update(screen, t_ms)` then for each row `img.put("{" + " ".join(row) + "}", to=(0, y, WIDTH, y + 1))`. `--scale S > 1` zooms the image after each put via `PhotoImage.zoom(S)` into a per-frame displayed copy (slow but simple; scale=1 default path untouched). Pacing: `time.sleep` to cap fps; `t_ms` is wall-clock since start; label updated every ~10 frames. Stop: window close button or Ctrl+C.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_sim_runner -v`
Expected: PASS (all)

- [ ] **Step 5: Add demo `experiments/hello_buddy.py`**

Mini-app per contract: blit the approved face centered `((456-240)//2, (280-240)//2) = (108, 20)`, plus a procedurally pulsing warm square border driven by `t_ms` (color from the spec's warm tone `(255,205,157)`; alternates a clearly visible dim/bright pulse ~ every 500 ms). Contains no commentary beyond one `why` line.

- [ ] **Step 6: Smoke-run (manual, on the Mac)**

Run: `python3 -m sim.runner experiments/hello_buddy.py --frames 5`
Expected: window opens, 5 frames render, exits cleanly with code 0. Then full run: `python3 -m sim.runner experiments/hello_buddy.py` — animation pulses, fps label shows ~30.

- [ ] **Step 7: Full suite + repository check**

Run: `python3 -m unittest discover -s tests -v && python3 tools/check_repository.py` (also `python3 tools/check_repository.py` — if the checker requires no new entries, leave as-is; if it enforces a manifest, add the new files per its error message).
Expected: PASS, exit 0.

- [ ] **Step 8: Commit**

```bash
git add sim/runner.py experiments/hello_buddy.py tests/test_sim_runner.py docs/superpowers/plans/2026-10-29-live-screen-simulator.md
git commit -m "feat(sim): live tkinter runner with fps label and demo app"
```
