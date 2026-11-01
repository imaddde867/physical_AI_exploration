"""Mount plate, screen part and cable for the slab buddy. Numbers live in params.py."""
import math
import build123d as bd
from params import *  # noqa: F401,F403
import params as P


def box(x0, x1, y0, y1, z0, z1, label, color):
    s = bd.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * bd.Box(x1 - x0, y1 - y0, z1 - z0)
    s.label, s.color = label, color
    return s


def cyl_y(x, z, d, y0, y1):
    """Cylinder along y from y0 to y1."""
    c = bd.Pos(x, (y0 + y1) / 2, z) * (bd.Rot(X=90) * bd.Cylinder(d / 2, y1 - y0))
    return c


def cable_path():
    """Lines + R-radius arcs: down the lid back, sideways off the lid edge at Z_OUT, forward past the
    base side, then down onto the plug's top. Returns (wire, free_span_extra_mm)."""
    R, y0, zc = P.CABLE_ARC_R, P.CABLE_Y, P.screen_z_center()
    xe, xs, xo = P.cable_x()
    yd, zo = P.port_y() + R, P.Z_OUT
    zt = P.PORT_Z + P.PLUG_H / 2 - 0.5
    k = R * (1 - math.sqrt(0.5))  # offset of a 45-degree arc midpoint from the corner's tangent lines
    with bd.BuildLine() as ln:
        bd.Line((xe, y0, zc - 12), (xe, y0, zo + R))
        bd.ThreePointArc((xe, y0, zo + R), (xe + k, y0, zo + k), (xe + R, y0, zo))
        bd.ThreePointArc((xs, y0, zo), (xs + R - k, y0 - k, zo), (xs + R, y0 - R, zo))
        bd.Line((xo, y0 - R, zo), (xo, yd, zo))
        bd.ThreePointArc((xo, yd, zo), (xo, yd - R + k, zo - k), (xo, yd - R, zo - R))
        bd.Line((xo, yd - R, zo - R), (xo, yd - R, zt))
    return ln.wire()


def cable_report(path):
    pts = [tuple(path @ (i / 2000)) for i in range(2001)]
    side = P.LID_W / 2
    free = [q for q in pts if q[0] > side]
    span = sum(math.dist(a, b) for a, b in zip(free, free[1:]))
    return {"length_mm": round(path.length, 1), "min_bend_r_mm": P.CABLE_ARC_R,
            "free_span_slack_mm": round(span - math.dist(free[0], free[-1]), 1),
            "slack_needed_mm": round(P.slack_needed(), 1)}


def build():
    zc, xc = P.screen_z_center(), P.screen_x_center()
    x0, x1 = P.plate_x_range()
    z0, z1 = zc - P.PLATE_H / 2, zc + P.PLATE_H / 2
    lid_edge = P.LID_W / 2
    # tape only under the lid-bonded strip; the plate overhang floats over the gap and under the screen part
    adh = box(x0, lid_edge, 0, P.ADH_T, z0, z1, "mount_adhesive", "#e8e4d8")
    plate = box(x0, x1, P.ADH_T, P.ADH_T + P.PLATE_T, z0, z1, "mount_plate", "#8d9096")
    pads = []
    for i in range(4):
        px = xc + (i - 1.5) * P.POGO_PITCH
        pads.append(box(px - P.POGO_PAD / 2, px + P.POGO_PAD / 2, P.ADH_T, P.ADH_T + 0.1,
                        zc - P.POGO_PAD / 2, zc + P.POGO_PAD / 2, "pad", "#d4af37"))
    for p in pads:
        plate = plate - p
    plate.label, plate.color = "mount_plate", "#8d9096"
    # screen part: shell + front glass, magnet pockets in the back
    shell = bd.fillet(box(lid_edge + P.GAP, lid_edge + P.GAP + P.W, -P.LID_T, P.ADH_T, zc - P.H / 2, zc + P.H / 2,
                          "screen_shell", "#c9ccd1").edges(), 1.0)
    mags = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            mx, mz = xc + sx * P.MAGNET_DX, zc + sz * P.MAGNET_DZ
            shell = shell - cyl_y(mx, mz, P.MAGNET_D + 0.2, P.ADH_T - P.MAGNET_POCKET, P.ADH_T)
            m = cyl_y(mx, mz, P.MAGNET_D, P.ADH_T - P.MAGNET_T, P.ADH_T)
            m.label, m.color = "magnet", "#444"
            mags.append(m)
    shell.label, shell.color = "screen_shell", "#c9ccd1"
    glass = box(lid_edge + P.GAP + 0.3, lid_edge + P.GAP + P.W - 0.3, -P.LID_T - P.GLASS_T, -P.LID_T,
                zc - P.H / 2 + 0.3, zc + P.H / 2 - 0.3, "screen_glass", "#050507")
    # cable + plug
    path = cable_path()
    port_y = P.port_y()
    prof = bd.Face(bd.Wire.make_circle(P.CABLE_D / 2, bd.Plane(origin=path @ 0, z_dir=path % 0)))
    cable = bd.sweep(prof, path)
    cable.label, cable.color = "cable", "#1b1b1d"
    side = P.LID_W / 2
    plug = box(side, side + P.PLUG_L, port_y - P.PLUG_W / 2, port_y + P.PLUG_W / 2,
               P.PORT_Z - P.PLUG_H / 2, P.PORT_Z + P.PLUG_H / 2, "plug", "#9aa0a6")
    return [shell, glass, *mags, adh, plate, *pads, cable, plug], cable_report(path)


if __name__ == "__main__":
    _, rep = build()
    print(rep)
    if rep["free_span_slack_mm"] < rep["slack_needed_mm"]:
        print("OPEN: free-span slack is short of what the lid swing needs; see DECISIONS.md")
