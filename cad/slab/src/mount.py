"""Nominal slab-buddy mount, isolated USB 2.0 contacts and sleeved cable exit.

CAD contact envelopes are conceptual: the electrical termination/FPC, current limits,
contact force, mating alignment and USB-C CC/ESD circuitry must still be designed/tested.
"""
import math
import build123d as bd
import params as P


def box(x0, x1, y0, y1, z0, z1, label, color):
    s = bd.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * bd.Box(x1 - x0, y1 - y0, z1 - z0)
    s.label, s.color = label, color
    return s


def cyl_y(x, z, d, y0, y1):
    """Cylinder along y from y0 to y1."""
    return bd.Pos(x, (y0 + y1) / 2, z) * (bd.Rot(X=90) * bd.Cylinder(d / 2, y1 - y0))


def cable_path():
    """Nominal static cable centreline; it is NOT a validated moving-hinge route."""
    R, y0, zc = P.CABLE_ARC_R, P.CABLE_Y, P.screen_z_center()
    xe, xs, xo = P.cable_x()
    yd, zo = P.port_y() + R, P.Z_OUT
    zt = P.PORT_Z + P.PLUG_H / 2 - 0.5
    k = R * (1 - math.sqrt(0.5))
    with bd.BuildLine() as ln:
        bd.Line((xe, y0, P.cable_entry_z()), (xe, y0, zo + R))
        bd.ThreePointArc((xe, y0, zo + R), (xe + k, y0, zo + k), (xe + R, y0, zo))
        bd.ThreePointArc((xs, y0, zo), (xs + R - k, y0 - k, zo), (xs + R, y0 - R, zo))
        bd.Line((xo, y0 - R, zo), (xo, yd, zo))
        bd.ThreePointArc((xo, yd, zo), (xo, yd - R + k, zo - k), (xo, yd - R, zo - R))
        bd.Line((xo, yd - R, zo - R), (xo, yd - R, zt))
    return ln.wire()


def cable_report(path):
    pts = [tuple(path @ (i / 2000)) for i in range(2001)]
    free = [q for q in pts if q[0] > P.LID_W / 2]
    span = sum(math.dist(a, b) for a, b in zip(free, free[1:]))
    # This chord excess is NOT a usable dynamic strain-relief loop.
    excess = span - math.dist(free[0], free[-1])
    demand = P.slack_needed()
    return {"length_mm": round(path.length, 1), "min_bend_r_mm": P.CABLE_ARC_R,
            "free_span_slack_mm": round(excess, 1), "slack_needed_mm": round(demand, 1),
            "nominal_proxy_deficit_mm": round(max(0, demand - excess), 1),
            "dynamic_hinge_fit_verified": False}


def build():
    zc, xc = P.screen_z_center(), P.screen_x_center()
    x0, x1 = P.plate_x_range()
    z0, z1 = P.plate_z_range()
    lid_edge = P.LID_W / 2
    plate_back = P.ADH_T + P.PLATE_T

    # Tape is only bonded to the lid strip; no tape on the detachable half.
    adh = box(x0, lid_edge, 0, P.ADH_T, z0, z1, "mount_adhesive", "#e8e4d8")
    plate = box(x0, x1, P.ADH_T, plate_back, z0, z1, "mount_plate", "#8d9096")

    # A *through-window* in conductive stainless isolates all four contacts.
    # The dielectric carrier has a rear lip that cannot pull forward through the opening.
    ix0, ix1, iz0, iz1 = P.carrier_outline()
    fit = P.CARRIER_FIT_CLEARANCE
    plate -= box(ix0-fit, ix1+fit, P.ADH_T-0.1, plate_back+0.1,
                 iz0-fit, iz1+fit, "carrier_window", "#000000")
    core = box(ix0, ix1, P.ADH_T, plate_back, iz0, iz1, "carrier_core", "#f5eee1")
    lip = P.CARRIER_FLANGE_OVERHANG
    rear_lip = box(ix0-lip, ix1+lip, plate_back, plate_back+P.CARRIER_FLANGE_T,
                   iz0-lip, iz1+lip, "carrier_rear_lip", "#f5eee1")
    carrier = core + rear_lip

    mount_contacts = []
    screen_contacts = []
    for name, px in zip(P.POGO_NAMES, P.contact_x_positions()):
        r = P.POGO_PAD / 2
        pad = box(px-r, px+r, P.ADH_T, P.ADH_T+P.PAD_DEPTH,
                  zc-r, zc+r, f"mount_contact_{name}", "#d4af37")
        # Metal via joins the pad to the carrier rear face, where insulated wiring/FPC can attach.
        via = cyl_y(px, zc, P.PAD_VIA_D, P.ADH_T+P.PAD_DEPTH/2,
                    plate_back+P.CARRIER_FLANGE_T)
        contact = pad + via
        carrier -= box(px-r-P.PAD_WELL_CLEARANCE, px+r+P.PAD_WELL_CLEARANCE,
                       P.ADH_T-0.05, P.ADH_T+P.PAD_DEPTH+0.02,
                       zc-r-P.PAD_WELL_CLEARANCE, zc+r+P.PAD_WELL_CLEARANCE,
                       "contact_well", "#000000")
        carrier -= cyl_y(px, zc, P.PAD_VIA_D + 2*P.PAD_WELL_CLEARANCE,
                         P.ADH_T+P.PAD_DEPTH/2, plate_back+P.CARRIER_FLANGE_T+0.1)
        contact.label, contact.color = f"mount_contact_{name}", "#d4af37"
        mount_contacts.append(contact)

    carrier.label, carrier.color = "insulating_contact_carrier", "#f5eee1"

    # A bottom-open cable notch and dielectric sleeve eliminate the cable/steel overlap.
    nx0, nx1, nz0, nz1 = P.cable_notch_bounds()
    plate -= box(nx0, nx1, P.ADH_T-0.1, plate_back+0.1, nz0, nz1,
                 "cable_exit_notch", "#000000")
    plate.label, plate.color = "mount_plate", "#8d9096"
    sleeve_z0, sleeve_z1 = z0-P.CABLE_GROMMET_EXTENSION, P.cable_entry_z()
    sleeve_h = sleeve_z1 - sleeve_z0
    sleeve_pos = bd.Pos(P.cable_x()[0], P.CABLE_Y, (sleeve_z0+sleeve_z1)/2)
    sleeve = sleeve_pos * bd.Cylinder(P.CABLE_D/2+P.CABLE_GROMMET_WALL, sleeve_h)
    sleeve -= sleeve_pos * bd.Cylinder(P.CABLE_D/2+P.CABLE_GROMMET_BORE_CLEARANCE,
                                       sleeve_h+0.2)
    sleeve.label, sleeve.color = "cable_insulating_grommet", "#2d2d31"

    # Screen shell and flush-mounted front glass: actual envelope equals SCREEN_T.
    bx0, bx1 = lid_edge + P.GAP, lid_edge + P.GAP + P.W
    bz0, bz1 = zc-P.H/2, zc+P.H/2
    shell = bd.fillet(box(bx0, bx1, -P.LID_T, P.ADH_T, bz0, bz1,
                          "screen_shell", "#c9ccd1").edges().filter_by(bd.Axis.Y), 1.0)
    glass_x0, glass_x1 = bx0+0.3, bx1-0.3
    glass_z0, glass_z1 = bz0+0.3, bz1-0.3
    shell -= box(glass_x0-P.GLASS_FIT_GAP, glass_x1+P.GLASS_FIT_GAP,
                 -P.LID_T-0.1, -P.LID_T+P.GLASS_T+0.02,
                 glass_z0-P.GLASS_FIT_GAP, glass_z1+P.GLASS_FIT_GAP,
                 "glass_recess", "#000000")
    glass = box(glass_x0, glass_x1, -P.LID_T, -P.LID_T+P.GLASS_T,
                glass_z0, glass_z1, "screen_glass", "#050507")
    magnets = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            mx, mz = xc + sx*P.MAGNET_DX, zc + sz*P.MAGNET_DZ
            shell -= cyl_y(mx, mz, P.MAGNET_D+0.2, P.ADH_T-P.MAGNET_POCKET, P.ADH_T)
            m = cyl_y(mx, mz, P.MAGNET_D, P.ADH_T-P.MAGNET_T, P.ADH_T)
            m.label, m.color = "magnet", "#444444"
            magnets.append(m)

    # Mating pogo envelopes are separate from the aluminum shell and face the insulated pads.
    # Their real contact spring travel/force and PCB connection are yet to be specified.
    for name, px in zip(P.POGO_NAMES, P.contact_x_positions()):
        shell -= cyl_y(px, zc, P.SCREEN_CONTACT_BORE_D,
                       P.ADH_T-P.SCREEN_CONTACT_DEPTH, P.ADH_T+0.05)
        pin = cyl_y(px, zc, P.SCREEN_CONTACT_D,
                    P.ADH_T-P.SCREEN_CONTACT_DEPTH+0.1, P.ADH_T)
        pin.label, pin.color = f"screen_contact_{name}", "#d4af37"
        screen_contacts.append(pin)
    shell.label, shell.color = "screen_shell", "#c9ccd1"

    path = cable_path()
    profile = bd.Face(bd.Wire.make_circle(P.CABLE_D/2,
                            bd.Plane(origin=path @ 0, z_dir=path % 0)))
    cable = bd.sweep(profile, path)
    cable.label, cable.color = "cable", "#1b1b1d"
    port_y = P.port_y()
    plug = box(lid_edge, lid_edge+P.PLUG_L,
               port_y-P.PLUG_W/2, port_y+P.PLUG_W/2,
               P.PORT_Z-P.PLUG_H/2, P.PORT_Z+P.PLUG_H/2,
               "plug", "#9aa0a6")
    return ([shell, glass, *magnets, *screen_contacts, adh, plate, carrier,
             *mount_contacts, sleeve, cable, plug], cable_report(path))


if __name__ == "__main__":
    _, report = build()
    print(report)
    if report["free_span_slack_mm"] < report["slack_needed_mm"]:
        print("OPEN: moving-lid cable clearance/strain relief unverified; measure and prototype.")
