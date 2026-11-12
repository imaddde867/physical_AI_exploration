"""Printable case for the Waveshare RP2040-Touch-LCD-1.69 and a fit coupon. Numbers: params.py.
Local axes: x width, y height (portrait, as the firmware draws), z front (0) to back (+z)."""
import os
import build123d as bd
from cadgen import model
import params as P


def rbox(w, h, z0, z1, r):
    """Rounded-corner (about z) box from z0 to z1."""
    sk = bd.Rectangle(w, h)
    sk = bd.fillet(sk.vertices(), r)
    return bd.Pos(0, 0, z0) * bd.extrude(sk, z1 - z0)


def pocket_dims():
    return P.WS_GLASS[0] + 2 * P.WS_CLEAR, P.WS_GLASS[1] + 2 * P.WS_CLEAR


def usb_cut(z_mid, outer_w):
    cy, cz = P.WS_USB_CUT
    x = P.WS_USB_SIDE * (outer_w / 2 - P.CASE_WALL / 2)
    return bd.Pos(x, 0, z_mid) * bd.Box(P.CASE_WALL * 3, cy, cz)


def tray(depth, floor, label):
    """Open-back tray; the board's glass face sits on the floor. Used for the coupon and the case."""
    pw, ph = pocket_dims()
    ow, oh = pw + 2 * P.CASE_WALL, ph + 2 * P.CASE_WALL
    body = rbox(ow, oh, 0, floor + depth, P.WS_GLASS_R + P.WS_CLEAR + P.CASE_WALL)
    body -= rbox(pw, ph, floor, floor + depth + 1, P.WS_GLASS_R + P.WS_CLEAR)
    body -= usb_cut(floor + depth / 2, ow)
    body.label = label
    return body


@model
def case():
    """Shell with a front lip over the glass border, plus the back cover with a friction tongue."""
    pw, ph = pocket_dims()
    shell = tray(P.WS_STACK_T, P.CASE_LIP_T, "case_shell")
    win_w, win_h = P.WS_GLASS[0] - 2 * P.CASE_LIP, P.WS_GLASS[1] - 2 * P.CASE_LIP
    shell -= rbox(win_w, win_h, -1, P.CASE_LIP_T + 0.5, 3.0)
    shell.label, shell.color = "case_shell", "#2b2d31"
    ow, oh = pw + 2 * P.CASE_WALL, ph + 2 * P.CASE_WALL
    z_back = P.CASE_LIP_T + P.WS_STACK_T
    cover = rbox(ow, oh, z_back, z_back + P.COVER_T, P.WS_GLASS_R + P.WS_CLEAR + P.CASE_WALL)
    tongue = rbox(pw - 0.3, ph - 0.3, z_back - P.COVER_TONGUE, z_back, P.WS_GLASS_R + P.WS_CLEAR)
    cover = cover + tongue
    cover.label, cover.color = "case_cover", "#3a3d42"
    return bd.Compound(children=[shell, cover], label="waveshare_case")


@model
def coupon():
    """Three open trays at stack depths 6 / 7 / 8 mm: press the real board in and pick the one
    where it sits flush with the USB-C cutout lined up. Floor 1.2 mm, print flat."""
    pw, ph = pocket_dims()
    step = pw + 2 * P.CASE_WALL + 3
    trays = []
    for i, d in enumerate((6.0, 7.0, 8.0)):
        t = tray(d, 1.2, f"fit_{d:g}mm")
        trays.append(bd.Pos((i - 1) * step, 0, 0) * t)
        trays[-1].label = f"fit_{d:g}mm"
    return bd.Compound(children=trays, label="waveshare_fit_coupon")


if __name__ == "__main__":
    for m in (case().shape, coupon().shape):
        print(m.label, m.bounding_box().size, round(m.volume, 1))
    # self-check: the USB opening must remove material, and every part must be a valid solid
    cut = P.WS_USB_CUT
    with_cut = tray(P.WS_STACK_T, P.CASE_LIP_T, "t").volume
    P.WS_USB_CUT = (0.01, 0.01)
    assert tray(P.WS_STACK_T, P.CASE_LIP_T, "t").volume - with_cut > 0.9 * cut[0] * cut[1] * P.CASE_WALL
    assert all(p.is_valid for p in case().shape.children + coupon().shape.children)
    print("self-check ok")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports")
    for name, m in (("waveshare_fit_coupon", coupon().shape), *((c.label, c) for c in case().shape.children)):
        bd.export_stl(m, os.path.join(out, name + ".stl"), tolerance=0.02, angular_tolerance=0.1)
    bd.export_step(case().shape, os.path.join(out, "waveshare_case.step"))  # for Fusion
