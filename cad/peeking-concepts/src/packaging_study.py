"""Provisional enclosure fit study around the public Waveshare board STEP."""
from __future__ import annotations

from pathlib import Path

from cadgen import build123d as bd, read_scene, step
from common import block

VENDOR_STEP = Path(__file__).resolve().parents[3] / "research_notes/Rectangular buddy engineering study/sources/waveshare/esp32-s3-touch-amoled-1_64.stp"

OUTER_W, OUTER_H = 33.12, 48.0
OUTER_DEPTH = 13.0
FRONT_Y, REAR_Y = 5.0, 18.0
WALL = 1.3
CAVITY_W, CAVITY_H = 30.12, 45.2
CAVITY_FRONT_Y, CAVITY_REAR_Y = 6.3, 16.7
WINDOW_W, WINDOW_H = 22.64, 36.36


def _board_no_headers() -> bd.Compound:
    # The public vendor STEP is a reference model, not proof of the purchased V2 revision;
    # assume its two optional PIN_HEADER leaves are unsoldered.
    scene = read_scene(str(VENDOR_STEP))
    board = []
    removed = []
    for leaf in scene.leaves():
        if "PIN_HEADER" in leaf.label:
            removed.append(leaf.label)
            continue
        # Center in X/Y, rotate the vendor +Z front toward -Y, then place front at Y=6.4.
        shape = leaf.shape().moved(bd.Location((0, 0.6, 0)))
        shape = shape.rotate(bd.Axis.X, 90).moved(bd.Location((0, 8, 0)))
        board.append(shape)
    if len(removed) != 2:
        raise ValueError(f"Expected exactly 2 optional PIN_HEADER leaves; removed {len(removed)}")
    result = bd.Compound(children=board, label="vendor_board_no_headers")
    if len(board) != 261:
        raise ValueError(f"Expected 261 retained vendor leaves; got {len(board)}")
    return result


def _case_front_shell() -> bd.Shape:
    outer = block(OUTER_W, OUTER_DEPTH - WALL, OUTER_H,
                  (0, (FRONT_Y + CAVITY_REAR_Y) / 2, 0),
                  "case_front_shell", "#59636C", radius=4)
    cavity_depth = CAVITY_REAR_Y - CAVITY_FRONT_Y + 0.3
    cavity = block(CAVITY_W, cavity_depth, CAVITY_H,
                   (0, (CAVITY_FRONT_Y + CAVITY_REAR_Y + 0.3) / 2, 0),
                   "cavity_tool", radius=2.5)
    # Active-area center is unknown; the centered aperture is an explicit placeholder.
    window = block(WINDOW_W, 2.5, WINDOW_H, (0, 5.75, 0),
                   "assumed_centered_display_window", radius=2)
    usb = block(12.5, 6.0, 3.5, (0, 13.0, -22.75),
                "usb_bottom_approach_placeholder")
    shell = outer - cavity - window - usb
    shell.label = "case_front_shell"
    shell.color = outer.color
    return shell


@step(out="../STEP/packaging_study.step")
def packaging_study():
    board = _board_no_headers()
    shell = _case_front_shell()
    back = block(OUTER_W, WALL, OUTER_H, (0, (CAVITY_REAR_Y + REAR_Y) / 2, 0),
                 "separate_back_cover", "#7A8288", radius=4)
    return bd.Compound(children=[board, shell, back], label="provisional_packaging_fit_study")


if __name__ == "__main__":
    packaging_study()
