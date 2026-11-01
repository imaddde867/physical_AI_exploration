"""1:1 scale comparison: 14" MacBook Pro (open, front) vs slim 'slab' buddy at several widths.
MacBook dims are public spec (312.6 x 221.2 mm base); lid height/bezels are approximations.
Buddy: aluminium shell + edge-to-edge black glass, ~1.3 mm visible border. Units mm, front = -Y."""
import build123d as bd
from cadgen import model

SILVER, BLACK, GLASS = "#c9ccd1", "#0b0b0d", "#050507"


def macbook():
    base = bd.Box(312.6, 221.2, 15.5 * 0.0 + 4, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN))
    base.color = SILVER
    lid = bd.Box(312.6, 4, 215, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN))
    lid.color = SILVER
    lid = bd.Pos(0, 221.2, 4) * lid
    scr = bd.Box(305.6, 0.5, 208, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN))
    scr.color = GLASS
    scr = bd.Pos(0, 221.2 - 4, 4 + 3.5) * scr  # front face of lid (toward viewer = -Y)
    return bd.Compound([base, lid, scr], label="macbook_pro_14")


def buddy(w, ratio=0.64, t=7.0, border=1.3, tilt=0.0):
    h = w * ratio
    shell = bd.Box(w, t, h, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN))
    shell = bd.fillet(shell.edges(), 1.2)
    shell.color = SILVER
    glass = bd.Box(w - 0.5, 0.4, h - 0.5, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN))
    glass = bd.Pos(0, 0, 0.25) * glass
    glass.color = GLASS
    foot = bd.Box(w * 0.5, t * 1.8, 3, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN))
    foot = bd.Pos(0, -t * 0.4, -3) * foot
    foot.color = SILVER
    return bd.Compound([shell, glass, foot], label=f"buddy_{int(w)}")


@model
def scale_compare():
    parts = [macbook()]
    x = 312.6 / 2 + 25
    for w in (60, 70, 80):
        x += w / 2
        parts.append(bd.Pos(x, 40, 4 + 3) * buddy(w))
        x += w / 2 + 12
    return bd.Compound(parts, label="scale_compare")


if __name__ == "__main__":
    d = scale_compare()
    print(d.shape.bounding_box().size)
