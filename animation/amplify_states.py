"""Write a livelier copy of the anchored scene: stronger idle and gesture head motion, still planted.

Run: Blender --background animation/crying-head-2-anchored.blend --python animation/amplify_states.py -- \
       --output animation/tmp/lively.blend [--idle 3] [--gesture 1.6]

Only the head ('Basic') channels of each ANCHORED action change; the eight IK-planted limbs follow.
Each gesture gain is capped by the same reach test anchor_contacts.py used, so contacts stay valid.
The source scene is never modified.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from anchor_contacts import release_at

FRAMES = tuple(range(1, 194))


def scaled(q, k):
    """q ** k along the shortest arc."""
    q = q.normalized()
    if q.w < 0:
        q.negate()
    axis, angle = q.to_axis_angle()
    return Quaternion(axis, angle * k)


def compose(w0, w, s, idle, gain):
    """Head local basis: amplified idle drift, plus the gesture delta at `gain`."""
    loc = w0[0] + (w[0] - w0[0]) * idle + (s[0] - w[0]) * gain
    rot = w0[1] @ scaled(w0[1].inverted() @ w[1], idle) @ scaled(w[1].inverted() @ s[1], gain)
    return loc, rot.normalized()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--idle', type=float, default=3.0, help='idle living-motion gain (1 = unchanged)')
    parser.add_argument('--gesture', type=float, default=1.6, help='gesture amplitude gain (1 = unchanged)')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.output.exists():
        raise FileExistsError(args.output)
    scene = bpy.context.scene
    rig = bpy.data.objects['Crying head 2 | source rig']
    catalog = json.loads(bpy.data.texts['STATE LIBRARY'].as_string())
    contacts = json.loads(bpy.data.texts['CONTACT MAP'].as_string())
    head = rig.pose.bones['Basic']
    head_rest = rig.data.bones['Basic'].matrix_local

    def head_samples(action):
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        out = []
        for frame in FRAMES:
            scene.frame_set(frame)
            out.append((head.location.copy(), head.rotation_quaternion.normalized()))
        return out

    # Head-space position of each limb root at rest; they are rigid children of the head.
    scene.frame_set(1)
    rig.animation_data.action = bpy.data.actions[catalog['watch']['action']]
    scene.frame_set(1)
    basic = head.matrix.copy()
    roots = {s['root']: basic.inverted() @ rig.pose.bones[s['root']].head for s in contacts['supports']}

    polish = {n: head_samples(bpy.data.actions[e['source_action']]) for n, e in catalog.items()}
    watch = polish['watch']
    scale0 = head.scale.copy()

    def basis(state, i, gain):
        loc, rot = compose(watch[0], watch[i], polish[state][i], args.idle, gain)
        return Matrix.LocRotScale(loc, rot, scale0), (loc, rot)

    def reachable(state, gain):
        for i, frame in enumerate(FRAMES):
            world = rig.matrix_world @ head_rest @ basis(state, i, gain)[0]
            for spec in contacts['supports']:
                if state == 'scratch' and spec['root'] == 'Virus1.013.L' and release_at((frame - 1) / 192) > 0:
                    continue
                d = (world @ roots[spec['root']] - Vector(spec['wrist_world'])).length
                if not spec['reach_min'] <= d <= spec['reach_max']:
                    return False
        return True

    gains = {}
    for state in catalog:
        if state == 'watch':
            gains[state] = 0.0
            assert reachable('watch', 0.0), 'amplified idle leaves the limbs\' reach; lower --idle'
            continue
        assert reachable(state, 0.0), (state, 'idle gain too high for this state')
        want = args.gesture * catalog[state].get('head_motion_factor', 1.0)
        if reachable(state, want):
            gains[state] = want
        else:
            low, high = 0.0, want
            for _ in range(24):
                mid = (low + high) / 2
                low, high = (mid, high) if reachable(state, mid) else (low, mid)
            gains[state] = low * .98
    for state, entry in catalog.items():
        action = bpy.data.actions[entry['action']]
        bag = action.layers[0].strips[0].channelbag(action.slots[0])
        samples = [basis(state, i, gains[state] if state != 'watch' else 0.0)[1] for i in range(len(FRAMES))]
        for previous, current in zip(samples, samples[1:]):
            if previous[1].dot(current[1]) < 0:
                current[1].negate()
        for kind, index, width in (('location', 0, 3), ('rotation_quaternion', 1, 4)):
            for axis in range(width):
                path = f'pose.bones["Basic"].{kind}'
                for curve in [c for c in bag.fcurves if c.data_path == path and c.array_index == axis]:
                    bag.fcurves.remove(curve)
                curve = bag.fcurves.new(data_path=path, index=axis)
                curve.keyframe_points.add(len(FRAMES))
                curve.keyframe_points.foreach_set('co', [n for f, s in zip(FRAMES, samples) for n in (f, s[index][axis])])
                for key in curve.keyframe_points:
                    key.interpolation = 'BEZIER'
                    key.handle_left_type = key.handle_right_type = 'AUTO_CLAMPED'
                curve.update()
        entry['lively'] = {'idle_gain': args.idle, 'gesture_gain': gains[state]}
    text = bpy.data.texts['STATE LIBRARY']
    text.clear()
    text.write(json.dumps(catalog, indent=2))
    idle = bpy.data.actions['ANCHORED | watch']
    rig.animation_data.action = idle
    rig.animation_data.action_slot = idle.slots[0]
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output.resolve()), compress=True)
    print('LIVELY gains', {k: round(v, 3) for k, v in gains.items()}, 'saved', args.output)


if __name__ == '__main__':
    main()
