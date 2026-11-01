"""60 mm slab buddy flush against the lid's right edge (0.6 mm gap), back and display plane flush
with the lid, top edge 1/4 of lid height below the lid top, thin rear arm + clip (placeholders).
Lid height/thickness are assumptions; 312.6 mm width is Apple's."""
import build123d as bd
from cadgen import model

W, H, T = 60.0, 38.4, 6.0
LID_W, LID_H, LID_T = 312.6, 214.0, 4.5
GAP = 0.6


def box(w, d, h, c, label, color, r=0):
    s = bd.Box(w, d, h)
    if r:
        s = bd.fillet(s.edges(), r)
    s = s.moved(bd.Location(c))
    s.label, s.color = label, color
    return s


@model
def placement():
    lid = box(LID_W, LID_T, LID_H, (0, -LID_T / 2, LID_H / 2 + 4), "lid", "#c9ccd1", 2)
    deck = box(LID_W, 221.2, 4, (0, -221.2 / 2 + 5, 2), "deck", "#c9ccd1", 1.5)
    # flush side-car: back flush with lid back, glass front flush with the lid's display plane, buddy top edge 1/4 of lid height below the lid top
    T = 4.25
    xc, zc = LID_W / 2 + GAP + W / 2, LID_H + 4 - LID_H / 4 - H / 2  # buddy top edge 1/4 of lid height below lid top
    shell = box(W, T, H, (xc, -T / 2, zc), "pod_shell", "#c9ccd1", 1.2)
    glass = box(W - 0.6, 0.3, H - 0.6, (xc, -T - 0.15 + 0.0, zc), "pod_glass", "#050507")
    arm = box(xc - (LID_W / 2 - 10), 1.6, 10, ((xc + LID_W / 2 - 10) / 2, 0.8, zc), "arm", "#9aa0a6", 0.5)
    clip = box(30, 3, 34, (LID_W / 2 - 25, 2.5, zc), "clip", "#9aa0a6", 1)
    return bd.Compound([lid, deck, shell, glass, arm, clip], label="mac_buddy_slab")


if __name__ == "__main__":
    print(placement().shape.bounding_box().size)
