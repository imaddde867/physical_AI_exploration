"""Selected appearance study only; not a fitted enclosure or printable mount."""
import math

import build123d as bd
from cadgen import model
from cadgen.geometry import overlap_volume


def block(width, depth, height, center, label, color, radius=0):
    shape = bd.Box(width, depth, height)
    if radius:
        shape = bd.fillet(shape.edges().filter_by(bd.Axis.Y), radius)
    shape = shape.moved(bd.Location(center))
    shape.label, shape.color = label, color
    return shape


@model
def selected_placement():
    # Width is Apple's overall dimension; lid height/thickness remain assumptions.
    lid = block(312.6, 4.5, 214, (0, -2.25, 107),
                "reference_lid_assumed", "#7C8189", 7)
    screen = block(302.4, 0.25, 196.4, (0, -4.63, 108),
                   "reference_display", "#131D28", 5)
    body = block(48, 13, 33.12, (0, 0, 0),
                 "appearance_envelope", "#484D54", 4)
    active = block(36.06, 0.3, 22.34, (0, -6.65, 0),
                   "active_area_placeholder", "#080C10", 2)
    eyes = [block(8.65, 0.2, 3, (x, -6.95, 1.5), name, "#C7CBCB", 0.9)
            for x, name in ((-8.3, "left_eye"), (8.3, "right_eye"))]
    pod = bd.Compound(children=[body, active, *eyes], label="face_pod")
    pod = pod.rotate(bd.Axis.Z, -10)
    bounds = pod.bounding_box()
    shift = bd.Location((156.3 + 2 - bounds.min.X, 1 - bounds.min.Y,
                         214 - 25 - bounds.max.Z))
    pod = pod.moved(shift)
    bounds = pod.bounding_box()
    z = bounds.center().Z
    dock = block(48, 2, 34, (128.3, 2, z),
                 "rear_dock_placeholder", "#59636B", 4)
    post = block(12, bounds.max.Y - 3, 12,
                 (128.3, (bounds.max.Y + 3) / 2, z),
                 "rear_dock_interface_placeholder", "#59636B", 2)
    arm = block(bounds.max.X - 122.3, 2, 10,
                ((bounds.max.X + 122.3) / 2, bounds.max.Y - 1, z),
                "detachable_arm_placeholder", "#59636B", 2)

    assert abs(bounds.min.X - lid.bounding_box().max.X - 2) < 0.001
    assert abs(lid.bounding_box().max.Z - bounds.max.Z - 25) < 0.001
    assert abs(bounds.min.Y - 1) < 0.001
    placed_active = next(child for child in pod.children
                         if child.label == "active_area_placeholder")
    placed_active = placed_active.located(pod.location * placed_active.location)
    front = max((face for face in placed_active.faces() if face.normal_at().Y < 0),
                key=lambda face: face.area)
    normal = front.normal_at()
    assert abs(math.degrees(math.atan2(-normal.X, -normal.Y)) - 10) < 0.001, normal
    for solid in pod.solids():
        assert solid.is_valid and solid.volume > 0
        assert overlap_volume(solid, lid.solids()[0]) < 0.001
    assembly = bd.Compound(children=[lid, screen, dock, post, arm, pod],
                           label="selected_landscape_placement")
    assert len(assembly.solids()) == 9
    assert all(solid.is_valid and solid.volume > 0 for solid in assembly.solids())
    return assembly


if __name__ == "__main__":
    selected_placement()
