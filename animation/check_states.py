"""Verify state endpoints, gentle idle, jaw closure, and original bone lengths."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from render_character import select_clip


def main():
    scene = bpy.context.scene
    rig = bpy.data.objects['Crying head 2 | source rig']
    mesh = next(o for o in rig.children if o.type == 'MESH')
    catalog = json.loads(bpy.data.texts['STATE LIBRARY'].as_string())
    assert len(catalog) == 8
    select_clip('watch')
    lengths = {b.name: (b.tail-b.head).length for b in rig.pose.bones}
    def vertices():
        evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]
    reference = vertices()
    idle_boundary = {}
    for frame in (1, 3, 191, 193):
        scene.frame_set(frame)
        idle_boundary[frame] = vertices()
    report = {}
    for name in catalog:
        select_clip(name)
        assert (scene.frame_start, scene.frame_end) == (1, 193)
        motion = length_error = edge_error = 0.
        for frame in range(1, 194, 2):
            scene.frame_set(frame)
            jaw = rig.pose.bones['Jaw']
            assert jaw.location.length < 1e-6
            assert jaw.rotation_quaternion.rotation_difference((1, 0, 0, 0)).angle < 1e-5
            for bone in rig.pose.bones:
                error = abs((bone.tail-bone.head).length-lengths[bone.name])
                length_error = max(length_error, error)
                assert error < 2e-5, (name, frame, bone.name, 'stretched bone', error)
            if frame in (1, 3, 191, 193):
                points = vertices()
                error = max((p-q).length for p, q in zip(points, idle_boundary[frame]))
                edge_error = max(edge_error, error)
                assert error < 2e-5, (name, frame, 'boundary differs from idle', error)
            if frame % 24 == 1:
                motion = max(motion, max((p-q).length for p, q in zip(vertices(), reference)))
        assert motion > .0001, (name, 'static action')
        report[name] = {'max_motion': motion, 'max_bone_length_error': length_error,
                        'idle_boundary_error': edge_error}
    assert report['watch']['max_motion'] < .10, 'Idle motion is too strong'
    select_clip('watch')
    scene.frame_set(97)
    basic = rig.pose.bones['Basic']
    # Calm head travel should be smaller than the clearly intentional gestures.
    assert report['lean_back']['max_motion'] > 3 * report['watch']['max_motion']
    assert report['look_left']['max_motion'] > 3 * report['watch']['max_motion']
    (HERE/'state-checks.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: eight moving states, shared idle boundaries, closed jaw, unstretched bones')


if __name__ == '__main__':
    main()
