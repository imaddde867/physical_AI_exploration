"""1:1 Pico WH + Waveshare Pico-LCD-1.8 companion on the 14" MacBook Pro lid, with a 30 cm
LogiLink CU0240 (USB-C -> Micro-B) cable. Laptop numbers come from params.py.

Part sources and assumptions (mm):
- Pico W PCB 51 x 21 x 1.0, header rows 17.78 apart, 2.54 pitch: Raspberry Pi datasheet.
- Pico-LCD-1.8 PCB 52 x 34.5, active area 35.04 x 28.03: BerryBase/Waveshare listing.
- Stack heights (female header 8.5, male header spacer 2.5, LCD module 2.4, PCB 1.6, Micro-B
  receptacle 2.9) are typical catalogue values, not measured. LCD module 45.83 x 34.0 and its
  position (toward the end away from USB) are read from Waveshare photos: ASSUMED.
- CU0240 overmolds (22 mm long) and plug tongues are estimates; "0.3 m" is taken as
  tip-to-tip, the conservative reading.
Axes as params.py: x right, y back (+y behind the lid), z up; lid front plane y = -LID_T.
"""
import math
import build123d as bd
from cadgen import model
import params as P
from mount import box

# --- part dimensions -------------------------------------------------------------------------
PICO_L, PICO_W, PICO_T = 51.0, 21.0, 1.0
ROW_SPACING, PITCH = 17.78, 2.54
LCD_PCB = (52.0, 34.5, 1.6)
LCD_MOD = (45.83, 34.0, 2.4)          # ASSUMED module outline (glass + backlight)
ACTIVE = (35.04, 28.03)
F_HDR_H, M_HDR_H = 8.5, 2.5
USB_RX = (5.6, 8.0, 2.9)             # Micro-B receptacle: x length, z width, y height
USB_RX_OVERHANG = 1.3
COVER_T, WALL, CLEAR = 1.0, 1.2, 0.6

CABLE_TIP_TO_TIP = 300.0             # CU0240 "0.3 m"
CABLE_D = 3.0
TAN = 0.2
MICRO_OVERMOLD = (22.0, 11.0, 6.5)   # length, width, thickness (estimate)
C_OVERMOLD = (22.0, 12.0, 6.5)
MICRO_TONGUE, C_TONGUE = 6.8, 6.6
CABLE_FLEX_LEN = CABLE_TIP_TO_TIP - MICRO_OVERMOLD[0] - MICRO_TONGUE - C_OVERMOLD[0] - C_TONGUE

# --- stack along y (front to back) -----------------------------------------------------------
Y_FRONT = -P.LID_T                    # front glass flush with the Mac's display plane
Y_LCD = Y_FRONT + COVER_T             # LCD module front
Y_LCD_PCB = Y_LCD + LCD_MOD[2]
Y_FHDR = Y_LCD_PCB + LCD_PCB[2]
Y_MHDR = Y_FHDR + F_HDR_H
Y_PICO = Y_MHDR + M_HDR_H             # Pico PCB bottom
Y_PICO_TOP = Y_PICO + PICO_T
Y_BACK = Y_PICO_TOP + USB_RX[2] + CLEAR + WALL

# --- footprint along x / z -------------------------------------------------------------------
X0 = P.LID_W / 2 + P.GAP              # housing outer face toward the lid
X_RX_MOUTH = X0 + WALL + 0.5
X_PICO = X_RX_MOUTH + USB_RX_OVERHANG
X_LCD_PCB = X_PICO - 0.5
HOUSING_W = (X_LCD_PCB + LCD_PCB[0] + 0.5 + WALL) - X0
HOUSING_H = LCD_PCB[1] + 2 * (0.3 + WALL)
# The approved spot (top edge a quarter of the lid height down) leaves the 30 cm cable ~0.5 mm
# short; DROP lowers the housing until the route also covers the lid-swing slack.
DROP = 25.0
ZC = P.BASE_T + P.LID_H * 0.75 - HOUSING_H / 2 - DROP
X_MOD1 = X_LCD_PCB + LCD_PCB[0] - 0.5
X_ACTIVE1 = X_MOD1 - 3.0                         # ASSUMED active-area offset in the module

# mount: wing behind the lid joined to the housing, magnets onto a bonded steel plate
WING_L, WING_H, WING_T = 30.0, 24.0, 3.0
PLATE_X = (X0 - WING_L + 1.0, X0 - 1.6)

PORT = (P.LID_W / 2, P.port_y(), P.PORT_Z)


def named(shape, label, color):
    shape.label, shape.color = label, color
    return shape


def housing():
    x1, y0, y1 = X0 + HOUSING_W, Y_FRONT + COVER_T, Y_BACK
    outer = box(X0, x1, y0, y1, ZC - HOUSING_H / 2, ZC + HOUSING_H / 2, "h", "#000")
    outer = bd.fillet(outer.edges().filter_by(bd.Axis.Y), 2.0)
    inner = box(X0 + WALL, x1 - WALL, y0 - 1, y1 - WALL, ZC - HOUSING_H / 2 + WALL, ZC + HOUSING_H / 2 - WALL, "i", "#000")
    shell = outer - inner
    # opening in the lid-side wall so the Micro-B overmold reaches the receptacle
    mz, mt = MICRO_OVERMOLD[1] + 1.0, MICRO_OVERMOLD[2] + 1.0
    yu = Y_PICO_TOP + USB_RX[2] / 2
    shell -= box(X0 - 1, X0 + WALL + 1, yu - mt / 2, yu + mt / 2, ZC - mz / 2, ZC + mz / 2, "o", "#000")
    wing = box(X0 - WING_L, X0 + 0.01, P.ADH_T + P.PLATE_T, P.ADH_T + P.PLATE_T + WING_T,
               ZC - WING_H / 2, ZC + WING_H / 2, "w", "#000")
    wing = bd.fillet(wing.edges().filter_by(bd.Axis.Y).group_by(bd.Axis.X)[0], 2.0)
    return named(shell + wing, "housing", "#c9ccd1")


def front_glass():
    g = box(X0 + 0.3, X0 + HOUSING_W - 0.3, Y_FRONT, Y_FRONT + COVER_T,
            ZC - HOUSING_H / 2 + 0.3, ZC + HOUSING_H / 2 - 0.3, "front_glass", "#050507")
    return named(bd.fillet(g.edges().filter_by(bd.Axis.Y), 1.7), "front_glass", "#050507")


def lcd_board():
    pcb = box(X_LCD_PCB, X_LCD_PCB + LCD_PCB[0], Y_LCD_PCB, Y_FHDR, ZC - LCD_PCB[1] / 2, ZC + LCD_PCB[1] / 2,
              "lcd_pcb", "#1f4fa8")
    mod = box(X_MOD1 - LCD_MOD[0], X_MOD1, Y_LCD, Y_LCD_PCB, ZC - LCD_MOD[1] / 2, ZC + LCD_MOD[1] / 2,
              "lcd_module", "#d9dadc")
    active = box(X_ACTIVE1 - ACTIVE[0], X_ACTIVE1, Y_LCD - 0.05, Y_LCD, ZC - ACTIVE[1] / 2, ZC + ACTIVE[1] / 2,
                 "lcd_active", "#101418")
    hx = (X_PICO + X_PICO + PICO_L) / 2
    hdrs = [box(hx - 25.4, hx + 25.4, Y_FHDR, Y_MHDR, ZC + s * ROW_SPACING / 2 - 1.27, ZC + s * ROW_SPACING / 2 + 1.27,
                "female_header", "#151515") for s in (-1, 1)]
    return [pcb, mod, active, *hdrs]


def pico():
    pcb = box(X_PICO, X_PICO + PICO_L, Y_PICO, Y_PICO_TOP, ZC - PICO_W / 2, ZC + PICO_W / 2, "pico_pcb", "#2f8f4e")
    hx = X_PICO + PICO_L / 2
    spacers = [box(hx - 25.4, hx + 25.4, Y_MHDR, Y_PICO, ZC + s * ROW_SPACING / 2 - 1.27, ZC + s * ROW_SPACING / 2 + 1.27,
                   "male_header", "#151515") for s in (-1, 1)]
    pins = bd.Compound(children=[
        bd.Pos(hx + (i - 9.5) * PITCH, Y_PICO_TOP + 0.75, ZC + s * ROW_SPACING / 2) * bd.Box(0.64, 1.5, 0.64)
        for s in (-1, 1) for i in range(20)])
    pins = named(pins, "header_pins", "#c8a64b")
    rp2040 = box(hx - 3.5, hx + 3.5, Y_PICO_TOP, Y_PICO_TOP + 0.9, ZC - 3.5, ZC + 3.5, "rp2040", "#222")
    shield = box(X_PICO + PICO_L - 17, X_PICO + PICO_L - 6.5, Y_PICO_TOP, Y_PICO_TOP + 1.6, ZC - 5.5, ZC + 5.5,
                 "wifi_shield", "#b8bcc2")
    bootsel = box(X_PICO + 10, X_PICO + 14.5, Y_PICO_TOP, Y_PICO_TOP + 2.0, ZC + 3.5, ZC + 7.0, "bootsel", "#eeeeee")
    rx = box(X_RX_MOUTH, X_RX_MOUTH + USB_RX[0], Y_PICO_TOP, Y_PICO_TOP + USB_RX[2], ZC - USB_RX[1] / 2, ZC + USB_RX[1] / 2,
             "micro_usb_receptacle", "#b8bcc2")
    return [pcb, *spacers, pins, rp2040, shield, bootsel, rx]


def mount_plate():
    adh = box(*PLATE_X, 0, P.ADH_T, ZC - WING_H / 2 + 1, ZC + WING_H / 2 - 1, "mount_adhesive", "#e8e4d8")
    plate = box(*PLATE_X, P.ADH_T, P.ADH_T + P.PLATE_T, ZC - WING_H / 2 + 1, ZC + WING_H / 2 - 1, "mount_plate", "#8d9096")
    yb = P.ADH_T + P.PLATE_T
    mags = [named(bd.Pos(X0 - WING_L / 2 + sx * 8, yb + 0.5, ZC + sz * 6) * (bd.Rot(X=90) * bd.Cylinder(2.5, 1.0)),
                  "magnet", "#444") for sx in (-1, 1) for sz in (-1, 1)]
    return [adh, plate, *mags]


def plugs():
    yu = Y_PICO_TOP + USB_RX[2] / 2
    ml, mw, mt = MICRO_OVERMOLD
    micro = box(X_RX_MOUTH - ml, X_RX_MOUTH, yu - mt / 2, yu + mt / 2, ZC - mw / 2, ZC + mw / 2, "micro_b_plug", "#f2f2f0")
    micro = named(bd.fillet(micro.edges().filter_by(bd.Axis.X), 1.5), "micro_b_plug", "#f2f2f0")
    cl, cw, ct = C_OVERMOLD
    px, py, pz = PORT
    c = box(px, px + cl, py - cw / 2, py + cw / 2, pz - ct / 2, pz + ct / 2, "usb_c_plug", "#f2f2f0")
    c = named(bd.fillet(c.edges().filter_by(bd.Axis.X), 1.5), "usb_c_plug", "#f2f2f0")
    return micro, c, (X_RX_MOUTH - ml, yu, ZC), (px + cl, py, pz)


def route(start, end, loop):
    """Micro-B tail -> past the mount wing -> down the lid back -> off the lid edge above the
    hinge -> forward to the USB-C tail. `loop` pushes the free span outward to take up surplus."""
    yb = CABLE_D / 2 + 2.4          # on the lid back (spline sag ~0.7), clear of the 1.6 mm plate stack
    pts = [start,
           (X0 - WING_L - 5, 10.0, ZC - 2),
           (X0 - WING_L - 8, yb, ZC - 24),
           (X0 - WING_L - 6, yb, 60),
           (P.LID_W / 2 - 16, yb, 24),
           (P.LID_W / 2 + 4 + loop * 0.5, 1.0, 15),
           (P.LID_W / 2 + 16 + loop, -22, 9),
           (end[0] + 14 + loop * 0.3, end[1] + 2, end[2] + 0.5),
           end]
    return bd.Spline(*pts, tangents=[(-1, 0, 0), (-1, 0, 0)], tangent_scalars=(TAN, TAN))


def min_bend_radius(path, n=600):
    pts = [path @ (i / n) for i in range(n + 1)]
    r = math.inf
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        ab, bc, ca = (b - a).length, (c - b).length, (a - c).length
        area2 = ((b - a).cross(c - a)).length
        if area2 > 1e-9:
            r = min(r, ab * bc * ca / (2 * area2))
    return r


def fitted_route(start, end):
    """Route at minimum length; if the cable is longer, grow the loop until it uses the full length."""
    base = route(start, end, 0.0)
    spare = CABLE_FLEX_LEN - base.length
    if spare <= 0:
        return base, spare, 0.0
    lo, hi = 0.0, 120.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if route(start, end, mid).length < CABLE_FLEX_LEN else (lo, mid)
    return route(start, end, lo), spare, lo


def cable_report():
    _, _, start, end = plugs()
    path, spare, loop = fitted_route(start, end)
    return {"cable_flex_mm": round(CABLE_FLEX_LEN, 1), "min_route_mm": round(CABLE_FLEX_LEN - spare, 1),
            "spare_mm": round(spare, 1), "loop_param": round(loop, 1),
            "min_bend_r_mm": round(min_bend_radius(path), 1), "slack_needed_lid_swing_mm": round(P.slack_needed(), 1),
            "housing_mm": (round(HOUSING_W, 1), round(HOUSING_H, 1), round(Y_BACK - Y_FRONT, 1)),
            "behind_lid_mm": round(Y_BACK, 1), "active_center_offset_x_mm": round(
                (X_ACTIVE1 - ACTIVE[0] / 2) - (X0 + HOUSING_W / 2), 1)}


@model
def pico_buddy():
    lid = box(-P.LID_W / 2, P.LID_W / 2, -P.LID_T, 0, P.BASE_T, P.BASE_T + P.LID_H, "lid", "#c9ccd1")
    deck = box(-P.LID_W / 2, P.LID_W / 2, 5 - P.DECK_D, 5, 0, P.BASE_T, "deck", "#c9ccd1")
    micro, cplug, start, end = plugs()
    path, spare, _ = fitted_route(start, end)
    assert spare >= P.slack_needed(), f"30 cm cable leaves {spare:.1f} mm spare, lid swing needs {P.slack_needed():.1f}"
    prof = bd.Face(bd.Wire.make_circle(CABLE_D / 2, bd.Plane(origin=path @ 0, z_dir=path % 0)))
    cable = named(bd.sweep(prof, path), "cable", "#f2f2f0")
    assert abs(path.length - CABLE_FLEX_LEN) < 1.0, path.length
    parts = [lid, deck, housing(), front_glass(), *lcd_board(), *pico(), *mount_plate(), micro, cplug, cable]
    return bd.Compound(children=parts, label="pico_buddy_on_mac")


if __name__ == "__main__":
    print(cable_report())
    pico_buddy()
