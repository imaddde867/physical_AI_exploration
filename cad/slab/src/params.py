"""Slab buddy nominal dimensions (mm). Dimensions marked ASSUMED need physical measurement.

Coordinates: x right, y toward lid rear, z up. Lid front y=-LID_T; lid back y=0.
A geometric contact or clearance is not electrical, mechanical, or USB compliance certification.
"""

# Apple's published enclosure width and depth are known. Lid height/thickness and hinge are ASSUMED.
LID_W, LID_H = 312.6, 214.0
LID_T = 4.5
DECK_D, DECK_T_TOTAL = 221.2, 15.5
BASE_T = DECK_T_TOTAL - LID_T

# Detachable screen
W, H = 60.0, 38.4
GAP = 0.6
ADH_T, PLATE_T = 0.4, 1.2
SCREEN_T = LID_T + ADH_T       # nominal, with front glass seated inside this envelope
GLASS_T, GLASS_FIT_GAP = 0.3, 0.05
TARGET_STACK_T = 6.5          # including the rear carrier retention flange, excluding localized cable

# Permanent stainless mounting plate, magnets, and insulating blind-mate insert
PLATE_BOND_W = 24.0
PLATE_H = 30.0
PLATE_REAR_MARGIN = 4.0
MAGNET_D, MAGNET_T, MAGNET_POCKET = 5.0, 1.0, 1.2
MAGNET_DX, MAGNET_DZ = 18.0, 10.0
POGO_NAMES = ("VBUS", "GND", "D_PLUS", "D_MINUS")
POGO_PITCH, POGO_PAD = 2.54, 1.8
PAD_EDGE_INSULATION = 1.0     # minimum polymer between each pad perimeter and the insert edge
PAD_WELL_CLEARANCE = 0.05     # assembly allowance around the metal pad/lead
PAD_DEPTH, PAD_VIA_D = 0.25, 0.7
CARRIER_FIT_CLEARANCE = 0.15  # on each side of the insert inside the steel through-window
CARRIER_FLANGE_OVERHANG = 0.8 # rear lip overlap past the cutout, not total clearance
CARRIER_FLANGE_T = 0.35       # rear retaining lip, included in stack thickness
SCREEN_CONTACT_D = 1.0       # simplified pogo-pin envelope, NOT an off-the-shelf pin spec
SCREEN_CONTACT_BORE_D = 1.2
SCREEN_CONTACT_DEPTH = 1.3

# 3 mm cable and protected bottom exit
CABLE_D = 3.0
MIN_BEND_R = 4 * CABLE_D
PORT_FROM_REAR = 45.0         # ASSUMED: right-side Thunderbolt port distance from base rear
PORT_Z = BASE_T / 2
PLUG_L, PLUG_W, PLUG_H = 10.0, 8.5, 4.5
CABLE_ARC_R = MIN_BEND_R
CABLE_Y = 3.0                  # rear clearance as cable rounds the lid edge (nominal static model)
CABLE_ENTRY_BELOW_CENTRE = 12.0
CABLE_GROMMET_WALL = 0.5      # insulating sleeve inside plate notch
CABLE_GROMMET_BORE_CLEARANCE = 0.08
CABLE_NOTCH_CLEARANCE = 0.25  # between sleeve outside and steel edges
CABLE_GROMMET_EXTENSION = 1.5 # sleeve extends below steel plate for edge protection
Z_OUT = PORT_Z + PLUG_H / 2 + CABLE_ARC_R
HINGE_AXIS_Y = -LID_T / 2    # ASSUMED
HINGE_SWING_DEG = 135.0       # ASSUMED max lid sweep


def screen_x_center() -> float:
    return LID_W / 2 + GAP + W / 2


def screen_z_center() -> float:
    return BASE_T + LID_H - LID_H / 4 - H / 2


def plate_x_range() -> tuple[float, float]:
    return LID_W / 2 - PLATE_BOND_W, screen_x_center() + W / 2 - PLATE_REAR_MARGIN


def plate_z_range() -> tuple[float, float]:
    zc = screen_z_center()
    return zc - PLATE_H / 2, zc + PLATE_H / 2


def contact_x_positions() -> tuple[float, ...]:
    xc = screen_x_center()
    return tuple(xc + (i - 1.5) * POGO_PITCH for i in range(len(POGO_NAMES)))


def carrier_outline() -> tuple[float, float, float, float]:
    """Bounding rectangle of dielectric core (x0, x1, z0, z1)."""
    xc, zc = screen_x_center(), screen_z_center()
    half_x = 1.5 * POGO_PITCH + POGO_PAD / 2 + PAD_EDGE_INSULATION
    half_z = POGO_PAD / 2 + PAD_EDGE_INSULATION
    return xc - half_x, xc + half_x, zc - half_z, zc + half_z


def cable_entry_z() -> float:
    return screen_z_center() - CABLE_ENTRY_BELOW_CENTRE


def cable_notch_bounds() -> tuple[float, float, float, float]:
    """Through-plate open-bottom cable sleeve notch (x0, x1, z0, z1)."""
    x, _, _ = cable_x()
    r = CABLE_D / 2 + CABLE_GROMMET_WALL + CABLE_NOTCH_CLEARANCE
    return x - r, x + r, plate_z_range()[0] - 1.0, cable_entry_z() + CABLE_NOTCH_CLEARANCE


def hinge_lever(hinge_y: float | None = None, hinge_z: float | None = None) -> float:
    """Assumed hinge-exit distance. This is NOT a measured kinematic path."""
    import math
    if hinge_y is None:
        hinge_y = HINGE_AXIS_Y
    if hinge_z is None:
        hinge_z = BASE_T
    return math.hypot(CABLE_Y - hinge_y, Z_OUT - hinge_z)


def slack_needed(hinge_y: float | None = None, hinge_z: float | None = None,
                 angle_deg: float | None = None) -> float:
    """Arc-length proxy only; not a safe or sufficient dynamic cable clearance criterion."""
    import math
    if angle_deg is None:
        angle_deg = HINGE_SWING_DEG
    return hinge_lever(hinge_y, hinge_z) * math.radians(angle_deg)


def port_y() -> float:
    return 5.0 - PORT_FROM_REAR


def cable_x() -> tuple[float, float, float]:
    """(entry x, first horizontal bend end x, outboard plug connection x)."""
    x_end = LID_W / 2 + PLUG_L - 2.5
    xs = x_end - CABLE_ARC_R
    return xs - CABLE_ARC_R, xs, x_end
