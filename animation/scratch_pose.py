"""Rotation-only scratch for the original rig; run in a separate master-file process."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


CHAIN = ("Virus1.013.L", "Virus1.014.L", "Virus1.015.L", "Virus1.016.L")
# Source mesh vertex 2751 extends beyond the terminal bone tail.
TIP_LOCAL = Vector((0.01196775, 0.84360152, 0.01588976))


def _ease(value):
    value = max(0.0, min(1.0, value))
    return value * value * value * (value * (value * 6 - 15) + 10)


def solve_scratch_pose(rig, progress, reference_head=None):
    """Apply to an evaluated baseline pose, returning local FK quaternion deltas.

    progress is 0..1 over one gesture. Reset/evaluate the baseline before each call.
    reference_head is Basic's frame-1 matrix, keeping scalp targets in head space.
    Only the four original chain rotations change; source locations/scales survive.
    """
    if not 0.0 <= progress <= 1.0:
        raise ValueError("Scratch progress must be between zero and one")
    bones = [rig.pose.bones[name] for name in CHAIN]
    initial = [bone.rotation_quaternion.copy() for bone in bones]
    if progress in (0.0, 1.0):
        return {name: [1.0, 0.0, 0.0, 0.0] for name in CHAIN}
    reference_head = reference_head or rig.pose.bones["Basic"].matrix.copy()
    head_motion = rig.pose.bones["Basic"].matrix @ reference_head.inverted()
    start = bones[-1].matrix @ TIP_LOCAL
    raised = head_motion @ Vector((0.72, 2.12, 0.50))
    contact = head_motion @ Vector((-0.245, 1.748, 0.770))
    if progress < 0.23:
        target = start.lerp(raised, _ease(progress / 0.23))
    elif progress < 0.38:
        target = raised.lerp(contact, _ease((progress - 0.23) / 0.15))
    elif progress <= 0.68:
        # Three short strokes, with zero velocity at entry and release.
        stroke = (progress - 0.38) / 0.30
        offset = 0.035 * math.sin(6 * math.pi * stroke) * math.sin(math.pi * stroke) ** 2
        target = contact + head_motion.to_3x3() @ Vector((0.0, offset, -0.35 * offset))
    elif progress < 0.82:
        target = contact.lerp(raised, _ease((progress - 0.68) / 0.14))
    else:
        target = raised.lerp(start, _ease((progress - 0.82) / 0.18))
    points = [bones[0].head.copy()] + [bone.tail.copy() for bone in bones[:-1]] + [start.copy()]
    root = points[0].copy()
    lengths = [(points[i + 1] - points[i]).length for i in range(len(bones))]
    # Bias the wrist toward the viewer so the shaft stays outside the scalp.
    front = min(_ease(progress / 0.38), _ease((1 - progress) / 0.32))
    wrist = target + head_motion.to_3x3() @ Vector((0.94, -0.25, 0.23)).normalized() * lengths[-1]
    points[-2] = points[-2].lerp(wrist, front)
    if (target - root).length >= sum(lengths):
        raise ValueError("Scratch target is outside the original chain reach")
    for _ in range(80):
        points[-1] = target.copy()
        for i in reversed(range(len(bones))):
            points[i] = points[i + 1] + (points[i] - points[i + 1]).normalized() * lengths[i]
        points[0] = root.copy()
        for i in range(len(bones)):
            points[i + 1] = points[i] + (points[i + 1] - points[i]).normalized() * lengths[i]
        if (points[-1] - target).length < 1e-6:
            break
    deltas = {}
    for i, bone in enumerate(bones):
        location, scale = bone.location.copy(), bone.scale.copy()
        current_tip = bone.matrix @ TIP_LOCAL if i == len(bones) - 1 else bone.tail
        rotation = (current_tip - bone.head).rotation_difference(points[i + 1] - points[i])
        pivot = bone.head.copy()
        bone.matrix = Matrix.Translation(pivot) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ bone.matrix
        bone.location, bone.scale = location, scale
        bpy.context.view_layer.update()
        deltas[bone.name] = list(initial[i].inverted() @ bone.rotation_quaternion)
    return deltas


def main():
    scene = bpy.context.scene
    rig = bpy.data.objects["Crying head 2 | source rig"]
    source = bpy.data.actions["DERIVED | Watch rest"]
    scene.frame_set(1)
    reference = rig.pose.bones["Basic"].matrix.copy()
    action = source.copy()
    action.name = "STUDY | Scratch head FK"
    samples, baseline, lengths = {}, {}, {}
    for frame in range(1, 78):
        rig.animation_data.action = source
        rig.animation_data.action_slot = source.slots[0]
        scene.frame_set(frame)
        baseline[frame] = {bone.name: bone.matrix.copy() for bone in rig.pose.bones}
        lengths[frame] = {bone.name: (bone.tail - bone.head).length for bone in rig.pose.bones}
        samples[frame] = solve_scratch_pose(rig, (frame - 1) / 76, reference)
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    for frame, deltas in samples.items():
        scene.frame_set(frame)
        for name, delta in deltas.items():
            bone = rig.pose.bones[name]
            # Start from the untouched source quaternion for each baked frame.
            rig.animation_data.action = source
            rig.animation_data.action_slot = source.slots[0]
            scene.frame_set(frame)
            quaternion = bone.rotation_quaternion.copy()
            rig.animation_data.action = action
            rig.animation_data.action_slot = action.slots[0]
            bone.rotation_quaternion = quaternion @ Quaternion(delta)
            bone.keyframe_insert("rotation_quaternion", frame=frame, group=name)
    max_length_error = max_other_error = max_endpoint_error = 0.0
    descendants = {bone.name for bone in rig.pose.bones if any(parent.name in CHAIN for parent in bone.parent_recursive)}
    for frame in range(1, 78):
        scene.frame_set(frame)
        for bone in rig.pose.bones:
            max_length_error = max(max_length_error, abs((bone.tail - bone.head).length - lengths[frame][bone.name]))
            error = max(abs(bone.matrix[i][j] - baseline[frame][bone.name][i][j]) for i in range(4) for j in range(4))
            if bone.name not in CHAIN and bone.name not in descendants:
                max_other_error = max(max_other_error, error)
            if frame in (1, 77):
                max_endpoint_error = max(max_endpoint_error, error)
    assert max_length_error < 1e-5, max_length_error
    assert max_other_error < 1e-6, max_other_error
    assert max_endpoint_error < 1e-6, max_endpoint_error
    output = Path(__file__).resolve().parent / "tmp"
    report = {"chain": CHAIN, "frames": [1, 77], "fps": 24, "source_action": source.name,
              "action": action.name, "max_bone_length_error": max_length_error,
              "max_other_bone_matrix_error": max_other_error, "max_endpoint_matrix_error": max_endpoint_error,
              "conventions": "Evaluate baseline each call; solve_scratch_pose returns baseline-local quaternion deltas. Postmultiply source rotation by each delta. No constraints, scale or hierarchy edits.",
              "samples": samples}
    (output / "scratch-study.json").write_text(json.dumps(report, indent=2) + "\n")
    scene.render.use_file_extension = True
    bpy.context.preferences.filepaths.save_version = 0
    scene.frame_start, scene.frame_end = 1, 77
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "scratch-study.blend"))
    for label, frame in (("start", 1), ("raise", 19), ("contact", 37), ("stroke", 43), ("return", 65), ("end", 77)):
        scene.frame_set(frame)
        scene.render.filepath = str(output / f"scratch-study-{label}.png")
        bpy.ops.render.render(write_still=True)
    print(json.dumps({key: value for key, value in report.items() if key != "samples"}))


if __name__ == "__main__":
    main()
