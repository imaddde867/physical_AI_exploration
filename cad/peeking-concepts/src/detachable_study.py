"""Throwaway study of a removable side-peeking face and rear dock, in mm."""
from __future__ import annotations

from cadgen import build123d as bd, step

from common import block, face_pod, laptop_reference, right_dock_pad


def removable_unit(x_offset: float = 0) -> bd.Compound:
    """Continuous concept carrier and face; x_offset places the loose unit."""
    arm = block(53, 2, 9, (154.8 + x_offset, 19, 178),
                "removable_arm", "#C47D52")
    # The stand-off links the rear carrier to the dock's shallow interface.
    stand_off = block(9, 15, 10, (148 + x_offset, 11.5, 178),
                      "rear_standoff", "#C47D52")
    tongue = block(7, 2, 8, (148 + x_offset, 3, 178),
                   "concept_mating_tongue", "#C47D52")
    pod = face_pod(181.3 + x_offset, 178)
    pod.label = "face_pod"
    return bd.Compound(children=[arm, stand_off, tongue, pod],
                       label="removable_face_arm_unit")


@step(out="../STEP/detachable_study.step")
def detachable_study():
    # The two computers are comparison references, not product geometry.
    attached_laptop = laptop_reference().moved(bd.Location((-220, 0, 0)))
    travel_laptop = laptop_reference().moved(bd.Location((220, 0, 0)))

    # A shallow raised socket indicates a concept interface; it is not a latch.
    attached_pad = right_dock_pad().moved(bd.Location((-220, 0, 0)))
    socket = block(9, 1, 10, (-220 + 148, 3.5, 178),
                   "concept_receptacle_region", "#303A40")
    attached_unit = removable_unit(-220)

    attached = bd.Compound(
        children=[attached_laptop, attached_pad, socket, attached_unit],
        label="attached_state",
    )

    travel_pad = right_dock_pad().moved(bd.Location((220, 0, 0)))
    travel_socket = block(9, 1, 10, (220 + 148, 3.5, 178),
                          "concept_receptacle_region", "#303A40")
    travel = bd.Compound(
        children=[travel_laptop, travel_pad, travel_socket],
        label="travel_state_dock_only",
    )

    # Pure X translation preserves identical removable geometry and alignment.
    removed = removable_unit(48.7).moved(bd.Location((220, 0, 0)))
    removed.label = "removed_face_and_arm"

    return bd.Compound(children=[attached, travel, removed],
                       label="detachable_peeking_concept_study")


if __name__ == "__main__":
    detachable_study()
