"""60 mm slab buddy flush against the lid's right edge on a permanent rear mount plate with a fixed
USB-C cable to the Mac's right-side Thunderbolt port. Numbers: params.py. Geometry: mount.py."""
import build123d as bd
from cadgen import model
import params as P
from mount import build, box


@model
def placement():
    lid = box(-P.LID_W / 2, P.LID_W / 2, -P.LID_T, 0, P.BASE_T, P.BASE_T + P.LID_H, "lid", "#c9ccd1")
    deck = box(-P.LID_W / 2, P.LID_W / 2, 5 - P.DECK_D, 5, 0, P.BASE_T, "deck", "#c9ccd1")
    parts, _ = build()
    return bd.Compound([lid, deck, *parts], label="mac_buddy_slab")


if __name__ == "__main__":
    print(placement().shape.bounding_box().size)
