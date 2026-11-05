"""Single source of numbers for the slab buddy + mount (mm). Pure Python so tests can import it.
Axes: x right, y back (+y is behind the lid), z up. Lid display plane y = -LID_T, lid back y = 0.
Values marked ASSUMED are unverified and need a tape-measure on the real laptop/part."""

# MacBook Pro 14 (M4, Nov 2024): width/depth/total closed height (15.5) are Apple's published figures.
# Lid height/thickness and port position are read from Apple's dimensions drawing (docs/hardware/measure-mac.md).
LID_W, LID_H = 312.6, 221.2      # lid outline equals the base footprint
LID_T = 4.0
DECK_D, DECK_T_TOTAL = 221.2, 15.5
BASE_T = DECK_T_TOTAL - LID_T    # base slab height; the lid hinges at its top (z = BASE_T)

# Screen part (detachable)
# Previous Good Display candidate dimensions preserve the approved preview; hardware selection is open.
PANEL_OUTLINE = (56.6, 47.25)    # glass outline
PANEL_SCREEN = (54.6, 40.95)     # visible area
FRAME_WALL = 1.2                 # ASSUMED aluminium frame wall; needs a design decision
W = PANEL_OUTLINE[0] + 2 * FRAME_WALL
H = PANEL_OUTLINE[1] + 2 * FRAME_WALL
GAP = 0.6                        # to the lid's right edge
ADH_T, PLATE_T = 0.4, 1.2        # VHB-type tape, 430 stainless plate (magnetic)
SCREEN_T = LID_T + ADH_T         # glass flush with the lid front, back sits on the plate's front face = 4.9
GLASS_T = 0.3
TARGET_STACK_T = 6.5             # screen + plate + tape behind the display plane we accept

# Mount plate: bonded to the lid back, cantilevers under the screen part
PLATE_BOND_W = 24.0              # strip glued to the lid
PLATE_H = 30.0
PLATE_REAR_MARGIN = 4.0          # plate stops this far short of the screen's far edge
MAGNET_D, MAGNET_T, MAGNET_POCKET = 5.0, 1.0, 1.2
MAGNET_DX, MAGNET_DZ = 18.0, 10.0
POGO_PITCH, POGO_PAD = 2.54, 1.8  # 4 pads: VBUS, GND, D+, D- (USB 2.0 + 5 V; plenty for a small display)

# Cable (fixed to the mount, USB-C plug into the Mac's right-side Thunderbolt port)
CABLE_D = 3.0
MIN_BEND_R = 4 * CABLE_D         # static; dynamic (lid swing) needs a flexible cable and a slack loop
PORT_FROM_REAR = 46.1            # right-side USB-C, 2nd from rear after HDMI; centre distance from the base's rear edge (Apple drawing)
PORT_Z = DECK_T_TOTAL / 2        # port is centred on the full body height (Apple drawing)
PLUG_L, PLUG_W, PLUG_H = 10.0, 8.5, 4.5  # right-angle overmold; sticks out of the side 10 mm
CABLE_ARC_R = MIN_BEND_R         # every bend in the route uses this radius
CABLE_Y = 1.5                    # cable axis on the lid back (cable lies on y = 0 .. 3)
Z_OUT = PORT_Z + PLUG_H / 2 + CABLE_ARC_R  # height where the cable leaves the lid sideways, so the last bend drops onto the plug
HINGE_AXIS_Y = -LID_T / 2        # ASSUMED hinge axis position (z = BASE_T)
HINGE_SWING_DEG = 135.0          # ASSUMED max lid opening


def screen_x_center() -> float:
    return LID_W / 2 + GAP + W / 2


def screen_z_center() -> float:
    """Screen top edge is 1/4 of lid height below the lid top."""
    return BASE_T + LID_H - LID_H / 4 - H / 2


def plate_x_range() -> tuple[float, float]:
    return LID_W / 2 - PLATE_BOND_W, screen_x_center() + W / 2 - PLATE_REAR_MARGIN


def hinge_lever() -> float:
    """Distance from the hinge axis to where the cable leaves the lid."""
    import math
    return math.hypot(CABLE_Y - HINGE_AXIS_Y, Z_OUT - BASE_T)


def slack_needed() -> float:
    """Extra free-span cable the lid swing eats (arc length at the hinge lever)."""
    import math
    return hinge_lever() * math.radians(HINGE_SWING_DEG)


def port_y() -> float:
    return 5.0 - PORT_FROM_REAR      # the deck's rear edge is y = 5


def cable_x() -> tuple[float, float, float]:
    """(xe, xs, x_end): where the cable drops out of the plate, starts the sideways bend, and meets the plug."""
    x_end = LID_W / 2 + PLUG_L - 2.5
    xs = x_end - CABLE_ARC_R
    return xs - CABLE_ARC_R, xs, x_end
