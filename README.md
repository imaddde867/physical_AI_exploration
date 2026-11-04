# MacDesk Buddy

A slim display companion beside a 14" MacBook Pro lid, with silver framing and black front glass. The first version is an animated companion; useful widgets can follow gradually.

Start with the [current product brief](docs/product-brief.md): approved direction, first-version scope, open decisions, and next steps. The physical appearance was approved on 2026-11-04; panel, controller, electronics fit, and print readiness remain unresolved.

Next session: [focused hardware shortlist handoff](docs/hardware/shortlist-handoff.md).

| Area | Current entry point | Status |
|---|---|---|
| Physical design | [CAD decisions and commands](cad/slab/DECISIONS.md) | Approved appearance; concept geometry |
| Face experiments | `sim/` and `experiments/hello_buddy.py` | Runnable simulator; placeholder face |
| Hardware | [Bring-up log](docs/hardware/bringup-log.md), [Mac measurements](docs/hardware/measure-mac.md) | Panel choice reopened; no recorded first light |
| Communication | [Draft protocol](docs/protocol.md), `daemon/protocol.py` | Codec and watchdog tests; no running daemon or firmware |

Older simulator plans in `docs/superpowers/`, the [November 1 slab record](docs/archive/2026-11-01-slab-decisions.md), and `cad/slab/src/scale_compare.py` are historical references. The removed 1.64" pod work remains in git history.

## Live desktop simulator

A mini-app is a Python file defining `update(screen, t_ms)`; it runs in a desktop window on an 800×600 RGB565 view. These are the current simulation defaults, not a final panel selection. Needs [uv](https://docs.astral.sh/uv/) with Python 3.12 (the system Python's Tk opens blank windows on macOS):

```sh
brew install uv && uv python install 3.12
sim/run.sh experiments/hello_buddy.py
```

The window opens at real physical size (54.6 mm panel width by default). Tk misreports screen density, so set your screen's points-per-inch with `--ppi` (default 127 = 14" MacBook Pro) and check it with a ruler. `--width-mm` changes the panel width, and `--scale 1` gives the pixel-exact view.

## CAD

`cad/slab/src/placement.py` is the current assembly (build123d via cadgen); it uses `mount.py` and `params.py`. Rebuild/export/render commands are in the [CAD decisions](cad/slab/DECISIONS.md). Files under `cad/slab/tmp/` are generated previews, not manufacturing deliverables.

## Tests

```sh
python3 -m unittest discover -s tests -v
```
