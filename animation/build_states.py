"""Author the first state library from checkpoint f44e690; normal edits use the saved scene."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FRAMES = tuple(range(1, 194, 2))
STATES = {
    'watch': 'Calm centered watching with slight living movement',
    'look_left': 'Look toward the viewer left, then return to watching',
    'look_right': 'Look toward the viewer right, then return to watching',
    'look_around': 'Look left, then right, then return to watching',
    'lean_back': 'Move away from the window, then return',
    'lean_in': 'Lean slightly toward the viewer, then return',
    'shift': 'Small side-to-side settling movement',
    'scratch': 'Raise an original claw to the side of the head, scratch, and return',
}


def smooth(value):
    value = max(0., min(1., value))
    return value ** 3 * (10 - 15 * value + 6 * value * value)


def envelope(t):
    return smooth((t - .12) / .22) * (1 - smooth((t - .66) / .22))


def pose_values(rig):
    return {b.name: (b.location.copy(), b.rotation_quaternion.normalized(), b.scale.copy())
            for b in rig.pose.bones}


def bake_action(rig, name, description, samples, frames):
    action = bpy.data.actions.new(name)
    slot = action.slots.new(rig.id_type, rig.name)
    strip = action.layers.new('Baked native pose').strips.new(type='KEYFRAME')
    bag = strip.channelbag(slot, ensure=True)
    for name, values in samples.items():
        # Match quaternion hemispheres to prevent interpolation flips.
        for previous, current in zip(values, values[1:]):
            if previous[1].dot(current[1]) < 0: current[1].negate()
        for kind, index, width in (('location', 0, 3), ('rotation_quaternion', 1, 4), ('scale', 2, 3)):
            for axis in range(width):
                ys = [value[index][axis] for value in values]
                constant = max(ys)-min(ys) < 1e-7
                points = [(frames[0], ys[0]), (frames[-1], ys[-1])] if constant else list(zip(frames, ys))
                curve = bag.fcurves.new(data_path=f'pose.bones["{name}"].{kind}', index=axis)
                curve.keyframe_points.add(len(points))
                curve.keyframe_points.foreach_set('co', [n for point in points for n in point])
                for key in curve.keyframe_points:
                    key.interpolation = 'BEZIER'
                    key.handle_left_type = key.handle_right_type = 'AUTO_CLAMPED'
                curve.update()
    action.use_fake_user = True
    action.asset_mark()
    action.asset_data.author = 'MacDesk Buddy; source character CommunicationNode'
    action.asset_data.description = description + '. Starts and ends on the shared calm-idle pose. CC BY-SA 4.0 source.'
    return action


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    assert 'STATE | watch' not in bpy.data.actions, 'Load the approved pre-state checkpoint'
    from scratch_pose import solve_scratch_pose
    scene = bpy.context.scene
    rig = bpy.data.objects['Crying head 2 | source rig']
    actor = rig.parent
    actor.animation_data.action = None
    actor.rotation_euler = actor['rest_rotation']
    source = bpy.data.actions['DERIVED | Watch rest']
    rig.animation_data.action = source
    rig.animation_data.action_slot = source.slots[0]
    cache = {}
    for frame in FRAMES:
        source_time = 1 + 76 * (frame - 1) / 192
        scene.frame_set(math.floor(source_time), subframe=source_time % 1)
        cache[frame] = pose_values(rig)
    reference = cache[1]
    rig.animation_data.action = None
    for bone in rig.pose.bones:
        bone.rotation_mode = 'QUATERNION'
    camera = bpy.data.objects['CAM | Window close-up']
    q = camera.rotation_euler.to_quaternion()
    right, up, toward = (q @ Vector(axis) for axis in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    # Use the selected, recentered camera from the direct-attention study.
    study = json.loads((HERE / 'tmp/idle-polish/grid.json').read_text())
    choice = next(item for item in study if item['label'] == 'A2')
    camera.location = choice['location']
    camera.rotation_euler = choice['rotation']
    q = camera.rotation_euler.to_quaternion()
    right, up, toward = (q @ Vector(axis) for axis in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    # The reference head matrix is the contact coordinate frame for the scratch.
    for b in rig.pose.bones:
        loc, rot, scale = reference[b.name]
        b.matrix_basis = Matrix.LocRotScale(loc, rot, scale)
    bpy.context.view_layer.update()
    reference_head = rig.pose.bones['Basic'].matrix.copy()
    catalog = {}
    for state, description in STATES.items():
        samples = {name: [] for name in reference}
        for frame in FRAMES:
            t = (frame - 1) / 192
            for bone in rig.pose.bones:
                loc0, q0, scale = reference[bone.name]
                loc1, q1, _ = cache[frame][bone.name]
                # Slow the source cycle to eight seconds and reduce its amplitude.
                amount = .18 if bone.name == 'Basic' else .12
                bone.matrix_basis = Matrix.LocRotScale(loc0.lerp(loc1, amount), q0.slerp(q1, amount).normalized(), scale)
                bone.scale = scale
            bpy.context.view_layer.update()
            if state == 'scratch':
                solve_scratch_pose(rig, max(0., min(1., (t-.12)/.76)), reference_head)
                bpy.context.view_layer.update()
            head = rig.pose.bones['Basic']
            head_world = rig.matrix_world @ head.matrix
            pivot = head_world.translation
            weight = envelope(t)
            yaw = roll = 0.
            offset = up * (.0025 * math.sin(2 * math.pi * t))
            if state == 'look_left': yaw = math.radians(-18) * weight
            elif state == 'look_right': yaw = math.radians(18) * weight
            elif state == 'look_around':
                yaw = math.radians(-17) * (smooth((t-.1)/.15)-smooth((t-.36)/.13))
                yaw += math.radians(17) * (smooth((t-.51)/.13)-smooth((t-.77)/.13))
            elif state == 'lean_back': offset -= toward * (.38 * weight)
            elif state == 'lean_in': offset += toward * (.12 * weight)
            elif state == 'shift':
                offset += right * (.055 * math.sin(2*math.pi*t) * weight)
                roll = math.radians(1.5) * math.sin(2*math.pi*t) * weight
            rotation = (Quaternion(up, yaw) @ Quaternion(toward, roll)).to_matrix().to_4x4()
            transform = Matrix.Translation(offset) @ Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot)
            desired_pose = rig.matrix_world.inverted() @ transform @ head_world
            head.matrix_basis = head.bone.convert_local_to_pose(desired_pose, head.bone.matrix_local, invert=True)
            head.scale = reference['Basic'][2]
            bpy.context.view_layer.update()
            for name, value in pose_values(rig).items():
                samples[name].append(value)
        action = bake_action(rig, 'STATE | ' + state, description, samples, FRAMES)
        catalog[state] = {'action': action.name, 'frames': [1, 193], 'fps': 24,
                          'seconds': 8, 'loop': state == 'watch', 'description': description}
    idle = bpy.data.actions['STATE | watch']
    rig.animation_data.action = idle
    rig.animation_data.action_slot = idle.slots[0]
    scene.frame_start, scene.frame_end = 1, 193
    scene.frame_set(1)
    notes = bpy.data.texts.new('STATE LIBRARY')
    notes.write(json.dumps(catalog, indent=2))
    bpy.data.texts['START HERE'].write('\nSTATE LIBRARY: watch, look_left, look_right, look_around, lean_back, lean_in, shift, scratch. Each is one complete rig Action, 1–193 at24fps. Default STATE | watch is calmer than the source demo. All states share the same idle phase and endpoint pose; use their phase-aligned full clips for transitions. Hardware scheduling is separate.\n')
    scene['state_idle_period_frames'] = 192
    scene.render.filepath = '//tmp/frames/'
    bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
    (HERE/'tmp/state-catalog.json').write_text(json.dumps(catalog, indent=2)+'\n')
    print('Saved eight native Action assets:', output)


if __name__ == '__main__':
    main()
