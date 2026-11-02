"""Export the current nominal assembly as individual STL parts without cadgen.

The output directory is generated-only: remove its prior STLs first so the Blender
renderer cannot accidentally include retired parts from earlier designs.
"""
from pathlib import Path
import build123d as bd
from mount import box, build
import params as P


def main():
    out = Path(__file__).resolve().parents[1] / "tmp/parts"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.stl"):
        old.unlink()

    lid = box(-P.LID_W/2, P.LID_W/2, -P.LID_T, 0,
              P.BASE_T, P.BASE_T+P.LID_H, "lid", "#c9ccd1")
    deck = box(-P.LID_W/2, P.LID_W/2, 5-P.DECK_D, 5,
               0, P.BASE_T, "deck", "#c9ccd1")
    pieces, report = build()
    for index, solid in enumerate([lid, deck, *pieces]):
        name = f"{index:02d}_{solid.label or 'part'}"
        bd.export_stl(solid, str(out / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.1)
        print("part", name, round(solid.volume, 1))
    print("static model only; hinge motion, USB electrical compliance and fit are unverified", report)


if __name__ == "__main__":
    main()
