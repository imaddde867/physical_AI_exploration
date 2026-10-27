"""Appearance envelopes; module depth/connector fit and lid profile unverified."""
from __future__ import annotations

from math import sqrt
from cadgen import build123d as bd, step
from common import (LID_HEIGHT, MAC_WIDTH, block, laptop_reference, rear_pad)

# Manufacturer outline; correspondence to the advertised V2 is unverified.
MODULE_W, MODULE_H = 29.12, 44.00
ACTIVE_W, ACTIVE_H = 22.34, 36.06
BEZEL_ALLOWANCE = 2.0
DEPTH_TARGET = 13.0
EDGE_GAP = 2.0
CONCEPTS = (
    ("portrait", MODULE_W + 2 * BEZEL_ALLOWANCE,
     MODULE_H + 2 * BEZEL_ALLOWANCE, ACTIVE_W, ACTIVE_H),
    ("landscape", MODULE_H + 2 * BEZEL_ALLOWANCE,
     MODULE_W + 2 * BEZEL_ALLOWANCE, ACTIVE_H, ACTIVE_W),
    ("square_unselected_panel", 35.0, 35.0,
     sqrt(ACTIVE_W * ACTIVE_H), sqrt(ACTIVE_W * ACTIVE_H)),
)


def concept_mount(name: str, width: float, height: float,
                  active_w: float, active_h: float) -> bd.Compound:
    x = MAC_WIDTH / 2 + EDGE_GAP + width / 2
    z = LID_HEIGHT - 8 - height / 2
    body = block(width, DEPTH_TARGET, height, (x, 5 + DEPTH_TARGET / 2, z),
                 "appearance_envelope", "#484D54", radius=4)
    display = block(active_w, 0.3, active_h, (x, 4.85, z),
                    "active_area_placeholder", "#080C10", radius=2)
    eye_w = active_w * 0.24
    eyes = [block(eye_w, 0.2, 3, (x + dx * active_w, 4.45, z + 1.5),
                  label, "#C7CBCB", radius=0.9)
            for dx, label in ((-0.23, "left_eye"), (0.23, "right_eye"))]
    mouth = block(3.5, 0.2, 0.7, (x, 4.45, z - 6),
                  "mouth", "#A1A9AD", radius=0.25)
    pod = bd.Compound(children=[body, display, *eyes, mouth], label="face_pod")
    dock_x = MAC_WIDTH / 2 - 28
    pad = rear_pad(dock_x, z)
    arm = block(x - dock_x + 12, 2, 10,
                ((x + dock_x) / 2, 6 + DEPTH_TARGET, z),
                "detachable_arm_envelope", "#59636B", radius=2)
    post = block(12, 15, 12, (dock_x, 10.5, z),
                 "rear_dock_interface_envelope", "#59636B", radius=2)
    return bd.Compound(children=[pad, post, arm, pod], label=name)


@step(out="../STEP/rectangular_study.step")
def rectangular_study():
    groups = []
    for (name, width, height, active_w, active_h), offset in zip(CONCEPTS, (-430, 0, 430)):
        reference = laptop_reference()
        mount = concept_mount(name, width, height, active_w, active_h)
        # 105-degree opening is a presentation pose, not measured hinge geometry.
        posed_lid = bd.Compound(children=[*reference.children[3:], mount],
                                label="lid_and_companion").rotate(bd.Axis.X, -15)
        laptop = bd.Compound(children=[*reference.children[:3], posed_lid], label=name)
        groups.append(laptop.moved(bd.Location((offset, 0, 0))))
    return bd.Compound(children=groups, label="rectangular_form_comparison")


if __name__ == "__main__":
    rectangular_study()
