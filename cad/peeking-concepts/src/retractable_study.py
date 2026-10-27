"""Appearance-only study; sliding arrangement and dimensions are unvalidated."""
from __future__ import annotations

from cadgen import build123d as bd, step

from common import (
    MAC_WIDTH, SIDE_HEAD_Z, block, face_pod,
    laptop_reference, right_dock_pad,
)


def _assembly(head_x: float, offset_x: float, pose: str) -> bd.Compound:
    dock_x = MAC_WIDTH / 2 - 28
    z = SIDE_HEAD_Z
    laptop = laptop_reference().moved(bd.Location((offset_x, 0, 0)))
    pad = right_dock_pad()
    rail = block(114, 3, 6, (97.5, 5, z - 20), "fixed_guide_rail", "#33434B", 1)
    mount = block(8, 5, 6, (dock_x, 3.5, z - 20), "guide_mount", "#4E5F66", 1)
    slider_x = head_x - 38
    slider = block(18, 4, 9, (slider_x, 8.5, z - 20),
                   "sliding_carriage", "#A87545", 1)
    arm = block(72, 3, 5, (head_x - 36, 19, z - 20),
                "carrier_arm", "#59636C", 1)
    stem = block(8, 12, 5, (slider_x, 14, z - 20), "carriage_standoff", "#59636C", 1)
    link = block(8, 12, 28, (head_x, 14, z - 4), "pod_support_link", "#59636C", 1)
    pod = face_pod(head_x, z)
    # Translate mechanism pieces independently to retain their assembly labels.
    translated = [p.moved(bd.Location((offset_x, 0, 0)))
                  for p in (pad, mount, rail, slider, stem, arm, link, pod)]
    return bd.Compound(children=[laptop, *translated], label=pose)


@step(out="../STEP/retractable_study.step")
def retractable_study():
    deployed = _assembly(181.3, -220, "deployed_laptop")
    retracted = _assembly(110.0, 220, "retracted_laptop")
    return bd.Compound(children=[deployed, retracted], label="retractable_right_dock_study")


if __name__ == "__main__":
    retractable_study()
