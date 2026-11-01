# MacDesk Buddy

A slim aluminum-and-glass display buddy that sits flush against the edge of a 14" MacBook Pro lid: an always-on face, and later Claude/Codex usage meters, lyrics and an AI chat view.

Direction and open questions: [cad/slab/DECISIONS.md](cad/slab/DECISIONS.md). Old 1.64" pod designs and hardware plans were removed on 2026-11-01; see git history.

## Live desktop simulator

A mini-app is a Python file defining `update(screen, t_ms)`; it runs in a desktop window on a 456×280 quantized view. Needs [uv](https://docs.astral.sh/uv/) with Python 3.12 (the system Python's Tk opens blank windows on macOS):

```sh
brew install uv && uv python install 3.12
sim/run.sh experiments/hello_buddy.py
```

The window opens at real physical size (60 mm panel width by default). Tk misreports screen density, so set your screen's points-per-inch with `--ppi` (default 127 = 14" MacBook Pro) and check it with a ruler. `--width-mm` changes the panel width, and `--scale 1` gives the pixel-exact view.

## CAD

`cad/slab/` holds the slab buddy and MacBook scale/placement models (build123d via cadgen) and a Blender render script.

## Tests

```sh
python3 -m unittest discover -s tests -v
```
