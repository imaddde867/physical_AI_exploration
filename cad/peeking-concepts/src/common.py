"""Throwaway scale study in mm; not measured hardware or printable tooling."""
from __future__ import annotations

from cadgen import build123d as bd, srgb

# Apple 2024 14-inch M4 overall envelope. Lid dimensions below are assumptions.
MAC_WIDTH = 312.6
MAC_DEPTH = 221.2
MAC_CLOSED_HEIGHT = 15.5
LID_HEIGHT = 214.0
LID_THICKNESS = 4.5
BASE_THICKNESS = MAC_CLOSED_HEIGHT - LID_THICKNESS
HEAD_DIAMETER = 44.0
SCREEN_DIAMETER = 33.5
HEAD_DEPTH = 13.0
REAR_GAP = 1.0
HEAD_FRONT_Y = 5.0
EDGE_CLEARANCE = 3.0
RIGHT_HEAD_X = MAC_WIDTH / 2 + EDGE_CLEARANCE + HEAD_DIAMETER / 2
SIDE_HEAD_Z = LID_HEIGHT - 36.0


def colored(shape: bd.Shape, label: str, color: str) -> bd.Shape:
    shape.label = label
    shape.color = srgb(color)
    return shape


def block(width: float, depth: float, height: float,
          center: tuple[float, float, float], label: str,
          color: str = "#59636C", radius: float = 0) -> bd.Shape:
    shape = bd.Box(width, depth, height)
    if radius:
        shape = bd.fillet(shape.edges().filter_by(bd.Axis.Y), radius)
    return colored(shape.moved(bd.Location(center)), label, color)


def disc(diameter: float, depth: float, center: tuple[float, float, float],
         label: str, color: str) -> bd.Shape:
    shape = bd.Cylinder(diameter / 2, depth).rotate(bd.Axis.X, 90)
    return colored(shape.moved(bd.Location(center)), label, color)


def laptop_reference() -> bd.Compound:
    """Lid upright for comparing placements; front faces -Y, rear is Y=0."""
    lid = block(MAC_WIDTH, LID_THICKNESS, LID_HEIGHT,
                (0, -LID_THICKNESS / 2, LID_HEIGHT / 2),
                "reference_lid_assumed", "#7C8189", radius=7)
    display = block(302.4, 0.25, 196.4,
                    (0, -LID_THICKNESS - 0.13, LID_HEIGHT / 2 + 1),
                    "reference_display", "#131D28", radius=5)
    camera = disc(3, 0.3, (0, -LID_THICKNESS - 0.4, LID_HEIGHT - 7),
                  "reference_camera", "#050608")
    base = block(MAC_WIDTH, MAC_DEPTH, BASE_THICKNESS,
                 (0, -MAC_DEPTH / 2, -BASE_THICKNESS / 2),
                 "reference_base", "#7C8189", radius=4)
    keyboard = block(277, 92, 0.3, (0, -65, 0.15),
                     "reference_keyboard", "#222830")
    trackpad = block(129, 78, 0.3, (0, -161, 0.15),
                     "reference_trackpad", "#6A717B")
    return bd.Compound(children=[base, keyboard, trackpad, lid, display, camera],
                       label="macbook_scale_reference")


def face_pod(x: float, z: float, front_y: float = HEAD_FRONT_Y) -> bd.Compound:
    """Generic appearance envelope, not an exact Waveshare PCB enclosure."""
    shell = disc(HEAD_DIAMETER, HEAD_DEPTH,
                 (x, front_y + HEAD_DEPTH / 2, z), "pod_envelope", "#D8D3C8")
    screen = disc(SCREEN_DIAMETER, 0.5,
                  (x, front_y - 0.25, z), "screen_placeholder", "#090D12")
    eyes = [block(9, 0.35, 4.5, (x + offset, front_y - 0.7, z + 2),
                  label, "#F5CEA0", radius=1.4)
            for offset, label in ((-8, "left_eye"), (8, "right_eye"))]
    mouth = block(5, 0.35, 1.0, (x, front_y - 0.7, z - 8),
                  "mouth", "#D6AD85", radius=0.3)
    return bd.Compound(children=[shell, screen, *eyes, mouth], label="face_pod")


def rear_pad(x: float, z: float, label: str = "rear_pad") -> bd.Shape:
    return block(48, 2, 34, (x, REAR_GAP + 1, z), label,
                 "#4E5F66", radius=4)


def right_dock_pad() -> bd.Shape:
    return rear_pad(MAC_WIDTH / 2 - 28, SIDE_HEAD_Z)
