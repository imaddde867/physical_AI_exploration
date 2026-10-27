"""Throwaway left/right/top appearance study, not a printable attachment."""
from __future__ import annotations

from cadgen import build123d as bd, step

from common import (
    EDGE_CLEARANCE, HEAD_DIAMETER, LID_HEIGHT, MAC_WIDTH, SIDE_HEAD_Z,
    block, face_pod, laptop_reference, rear_pad,
)


def peeking_mount(side: str) -> bd.Compound:
    if side == "top":
        x, z = 92.0, LID_HEIGHT + EDGE_CLEARANCE + HEAD_DIAMETER / 2
        pad_x, pad_z = x, LID_HEIGHT - 25
        bridge = block(13, 2, z - pad_z + 12, (x, 19, (z + pad_z) / 2),
                       "removable_arm", "#5F9FA1", radius=2)
    else:
        direction = -1 if side == "left" else 1
        x = direction * (MAC_WIDTH / 2 + EDGE_CLEARANCE + HEAD_DIAMETER / 2)
        z = pad_z = SIDE_HEAD_Z
        pad_x = direction * (MAC_WIDTH / 2 - 28)
        bridge = block(abs(x - pad_x) + 14, 2, 13,
                       ((x + pad_x) / 2, 19, z),
                       "removable_arm", "#5F9FA1", radius=2)
    post = block(14, 15, 16, (pad_x, 10.5, pad_z),
                 "rear_connection", "#5F9FA1", radius=2)
    return bd.Compound(children=[rear_pad(pad_x, pad_z), post, bridge, face_pod(x, z)],
                       label=f"{side}_peek_mount")


@step(out="../STEP/placement_study.step")
def placement_study():
    groups = []
    for side, x_offset in (("left", -430), ("right", 0), ("top", 430)):
        group = bd.Compound(children=[laptop_reference(), peeking_mount(side)],
                            label=f"{side}_placement")
        groups.append(group.moved(bd.Location((x_offset, 0, 0))))
    return bd.Compound(children=groups, label="placement_comparison")


if __name__ == "__main__":
    placement_study()
