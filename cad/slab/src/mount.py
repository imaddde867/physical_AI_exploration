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
    """Static reference geometry, not a certified electrical or mechanical assembly."""
    zc, xc = P.screen_z_center(), P.screen_x_center()
    x0, x1 = P.plate_x_range()
    z0, z1 = P.plate_z_range()
    lid_edge = P.LID_W / 2
    plate_back = P.ADH_T + P.PLATE_T

    adh = box(x0, lid_edge, 0, P.ADH_T, z0, z1, "mount_adhesive", "#e8e4d8")
    plate = box(x0, x1, P.ADH_T, plate_back, z0, z1, "mount_plate", "#8d9096")

    # This is an OVERMOLDED carrier, not a push-in cartridge. Opposing shoulders
    # capture the steel from both faces under pogo compression and removal.
    ix0, ix1, iz0, iz1 = P.carrier_outline()
    fit, lip = P.CARRIER_FIT_CLEARANCE, P.CARRIER_FLANGE_OVERHANG
    plate -= box(ix0-fit, ix1+fit, P.ADH_T-0.1, plate_back+0.1,
                 iz0-fit, iz1+fit, "carrier_window", "#000000")
    carrier = box(ix0, ix1, P.ADH_T, plate_back, iz0, iz1,
                  "carrier_core", "#f5eee1")
    carrier += box(ix0-lip, ix1+lip, plate_back, plate_back+P.CARRIER_FLANGE_T,
                   iz0-lip, iz1+lip, "rear_capture_flange", "#f5eee1")
    carrier += box(ix0-lip, ix1+lip, P.ADH_T-P.CARRIER_FRONT_FLANGE_T, P.ADH_T,
                   iz0-lip, iz1+lip, "front_capture_flange", "#f5eee1")

    # A round primary locator and a slotted secondary locator give positive
    # x/z/yaw registration; their asymmetric spacing rules out 180-degree mating.
    for i, (ax, az) in enumerate(P.alignment_positions()):
        if i == 0:
            hole = cyl_y(ax, az, P.ALIGN_HOLE_D, P.ADH_T-0.1, plate_back+0.1)
        else:
            half = P.ALIGN_SLOT_EXTRA_X/2
            hole = cyl_y(ax-half, az, P.ALIGN_HOLE_D, P.ADH_T-0.1, plate_back+0.1)
            hole += cyl_y(ax+half, az, P.ALIGN_HOLE_D, P.ADH_T-0.1, plate_back+0.1)
            hole += box(ax-half, ax+half, P.ADH_T-0.1, plate_back+0.1,
                        az-P.ALIGN_HOLE_D/2, az+P.ALIGN_HOLE_D/2, "slot", "#000000")
        plate -= hole

    mount_contacts = []
    for name, px in zip(P.POGO_NAMES, P.contact_x_positions()):
        r, face = P.POGO_PAD/2, P.pad_face_y()
        pad = box(px-r, px+r, face, face+P.PAD_DEPTH,
                  zc-r, zc+r, "pad", "#d4af37")
        via = cyl_y(px, zc, P.PAD_VIA_D, face+P.PAD_DEPTH/2,
                    plate_back+P.CARRIER_FLANGE_T)
        contact = pad + via
        carrier -= box(px-r-P.PAD_WELL_CLEARANCE, px+r+P.PAD_WELL_CLEARANCE,
                       P.ADH_T-P.CARRIER_FRONT_FLANGE_T-0.1,
                       face+P.PAD_DEPTH+0.02,
                       zc-r-P.PAD_WELL_CLEARANCE, zc+r+P.PAD_WELL_CLEARANCE,
                       "contact_well", "#000000")
        carrier -= cyl_y(px, zc, P.PAD_VIA_D+2*P.PAD_WELL_CLEARANCE,
                         face+P.PAD_DEPTH/2, plate_back+P.CARRIER_FLANGE_T+0.1)
        contact.label, contact.color = f"mount_contact_{name}", "#d4af37"
        mount_contacts.append(contact)
    carrier.label, carrier.color = "insulating_contact_carrier", "#f5eee1"

    # Closed-hole molded snap heads and closely spaced rear collars constrain
    # nominal axial motion. Snap fatigue and cable grip are not tested.
    nx0, nx1, nz0, nz1 = P.cable_notch_bounds()
    plate -= box(nx0, nx1, P.ADH_T-0.1, plate_back+0.1, nz0, nz1,
                 "cable_exit_notch", "#000000")
    for ax, az in P.grommet_anchor_positions():
        plate -= cyl_y(ax, az, P.GROMMET_HOLE_D, P.ADH_T-0.1, plate_back+0.1)
        adh -= cyl_y(ax, az, P.GROMMET_HEAD_D+0.2, -0.05, P.ADH_T+0.05)
    plate.label, plate.color = "mount_plate", "#8d9096"
    adh.label, adh.color = "mount_adhesive", "#e8e4d8"

    sleeve_z0, sleeve_z1 = z0-P.CABLE_GROMMET_EXTENSION, P.cable_entry_z()
    sleeve_h = sleeve_z1-sleeve_z0
    xe = P.cable_x()[0]
    sleeve_pos = bd.Pos(xe, P.CABLE_Y, (sleeve_z0+sleeve_z1)/2)
    sleeve = sleeve_pos * bd.Cylinder(P.CABLE_D/2+P.CABLE_GROMMET_WALL, sleeve_h)
    sleeve -= sleeve_pos * bd.Cylinder(P.CABLE_D/2+P.CABLE_GROMMET_BORE_CLEARANCE,
                                       sleeve_h+0.2)
    for ax, az in P.grommet_anchor_positions():
        side = -1 if ax < xe else 1
        sleeve += cyl_y(ax, az, P.GROMMET_ANCHOR_D, 0.28, 3.2)
        sleeve += cyl_y(ax, az, P.GROMMET_HEAD_D,
                        P.GROMMET_FRONT_HEAD_Y0, P.GROMMET_FRONT_HEAD_Y1)
        # Rear collar sits adjacent to steel; the original arm was 1.05 mm away.
        collar_start = plate_back + P.GROMMET_REAR_COLLAR_GAP
        sleeve += cyl_y(ax, az, P.GROMMET_REAR_COLLAR_D,
                        collar_start, collar_start+P.GROMMET_REAR_COLLAR_T)
        xl, xr = sorted((xe+side*1.90, ax))
        sleeve += box(xl, xr, 2.65, 3.35, az-0.55, az+0.55,
                      "grommet_anchor_arm", "#2d2d31")
    sleeve.label, sleeve.color = "captive_cable_grommet", "#2d2d31"

    # The shell is still a solid ENVELOPE; panel and PCB cavity are not designed.
    bx0, bx1 = lid_edge+P.GAP, lid_edge+P.GAP+P.W
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

    # The screen must clear the front retaining shoulder of the overmold.
    rel = P.CARRIER_SHELL_RELIEF
    shell -= box(ix0-lip-rel, ix1+lip+rel,
                 P.ADH_T-P.CARRIER_FRONT_FLANGE_T-0.05, P.ADH_T+0.05,
                 iz0-lip-rel, iz1+lip+rel, "carrier_relief", "#000000")
    for ax, az in P.alignment_positions():
        shell += cyl_y(ax, az, P.ALIGN_D, P.ADH_T-0.20,
                       P.ADH_T+P.ALIGN_PROJECTION)

    magnets, bonds = [], []
    for sx in (-1, 1):
        for sz in (-1, 1):
            mx, mz = xc+sx*P.MAGNET_DX, zc+sz*P.MAGNET_DZ
            floor_y = P.ADH_T-P.MAGNET_POCKET
            pocket_d = P.MAGNET_D+2*P.MAGNET_ADHESIVE_T
            shell -= cyl_y(mx, mz, pocket_d, floor_y, P.ADH_T+0.05)
            magnet_min = floor_y+P.MAGNET_ADHESIVE_T
            magnet_max = magnet_min+P.MAGNET_T
            magnet = cyl_y(mx, mz, P.MAGNET_D, magnet_min, magnet_max)
            magnet.label, magnet.color = "magnet", "#444444"
            magnets.append(magnet)
            bond = cyl_y(mx, mz, pocket_d, floor_y, magnet_min)
            bond += (cyl_y(mx, mz, pocket_d, magnet_min, magnet_max) -
                     cyl_y(mx, mz, P.MAGNET_D, magnet_min, magnet_max))
            bond.label, bond.color = "magnet_bond", "#88888a"
            bonds.append(bond)

    screen_contacts, insulators = [], []
    pcb_y = P.pogo_pcb_y()
    for name, px in zip(P.POGO_NAMES, P.contact_x_positions()):
        # PCB-to-pad tip height = Harwin's 1.90mm nominal compressed height.
        shell -= cyl_y(px, zc, P.POGO_SHELL_BORE, pcb_y-0.25, P.ADH_T+0.05)
        bush = cyl_y(px, zc, P.POGO_SLEEVE_OD, pcb_y-0.05, P.ADH_T-P.CARRIER_FRONT_FLANGE_T-0.05)
        bush -= cyl_y(px, zc, P.POGO_SLEEVE_ID, pcb_y-0.15, P.ADH_T-P.CARRIER_FRONT_FLANGE_T+0.05)
        bush.label, bush.color = f"contact_insulator_{name}", "#f5eee1"
        insulators.append(bush)
        barrel_end = pcb_y+P.POGO_BARREL_H
        pin = cyl_y(px, zc, P.POGO_BARREL_D, pcb_y, barrel_end)
        pin += cyl_y(px, zc, P.POGO_TIP_D, barrel_end, P.pad_face_y())
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
    report = cable_report(path)
    report.update(P.dimensions())
    return ([shell, glass, *magnets, *bonds, *screen_contacts, *insulators,
             adh, plate, carrier, *mount_contacts, sleeve, cable, plug], report)


if __name__ == "__main__":
    _, report = build()
    print(report)
    print("BLOCKED: no verified electronics, USB CC/power protection, termination, "
          "magnet pull-out, moving cable or actual MacBook fit.")
