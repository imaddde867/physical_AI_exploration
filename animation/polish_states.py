"""Create a motion-polish candidate from saved native Actions; preserve the approved master."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_states import bake_action, pose_values, smooth


def warp(t, knots):
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if t <= x1:
            return y0 + (y1-y0) * (t-x0)/(x1-x0)
    return 1.


def bump(t, a, b, c, d):
    return smooth((t-a)/(b-a)) * (1-smooth((t-c)/(d-c)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():
        raise FileExistsError(args.output)
    scene = bpy.context.scene
    rig = bpy.data.objects['Crying head 2 | source rig']
    catalog = json.loads(bpy.data.texts['STATE LIBRARY'].as_string())
    old = {name: bpy.data.actions[entry['action']] for name, entry in catalog.items()}
    assert all(a.name.startswith('STATE | ') for a in old.values())
    q = scene.camera.rotation_euler.to_quaternion()
    up, toward = (q @ Vector(axis) for axis in ((0,1,0),(0,0,1)))
    cache = {}
    def evaluate(name, t):
        key = (name, round(t, 10))
        if key not in cache:
            action = old[name]
            rig.animation_data.action = action
            rig.animation_data.action_slot = action.slots[0]
            frame = 1 + 192*t
            scene.frame_set(math.floor(frame), subframe=frame % 1)
            cache[key] = (pose_values(rig), (rig.matrix_world @ rig.pose.bones['Basic'].matrix).copy())
        return cache[key]
    timings = {
        'look_left': [(0,0),(.10,.12),(.29,.34),(.52,.66),(.82,.88),(1,1)],
        'look_right': [(0,0),(.14,.12),(.33,.34),(.61,.66),(.86,.88),(1,1)],
        'look_around': [(0,0),(.08,.10),(.23,.25),(.41,.49),(.54,.51),(.71,.64),(.88,.90),(1,1)],
        'lean_back': [(0,0),(.10,.12),(.31,.34),(.57,.66),(.88,.88),(1,1)],
        'lean_in': [(0,0),(.15,.12),(.43,.34),(.56,.66),(.86,.88),(1,1)],
    }
    roots = [b for b in rig.pose.bones if b.parent and b.parent.name=='Basic' and b.name.startswith('Virus')]
    frames = tuple(range(1,194))
    for state, entry in catalog.items():
        samples = {b.name: [] for b in rig.pose.bones}
        knots = timings.get(state, [(0,0),(1,1)])
        for frame in frames:
            t = (frame-1)/192
            phase = warp(t, knots)
            base, _ = evaluate('watch', t)
            reference, ref_head = evaluate('watch', phase)
            gesture, gesture_head = evaluate(state, phase)
            lag = 0.
            if state.startswith('look_'):
                delayed = warp(max(0.,t-.11/8),knots)
                _, before_ref = evaluate('watch', delayed)
                _, before_head = evaluate(state, delayed)
                now = gesture_head.to_quaternion() @ ref_head.to_quaternion().inverted()
                before = before_head.to_quaternion() @ before_ref.to_quaternion().inverted()
                if now.w < 0: now.negate()
                if before.w < 0: before.negate()
                yaw_now = now.angle * (1 if now.axis.dot(up)>=0 else -1)
                yaw_before = before.angle * (1 if before.axis.dot(up)>=0 else -1)
                lag = max(-math.radians(2.5),min(math.radians(2.5),yaw_before-yaw_now))
            rig.animation_data.action = None
            for bone in rig.pose.bones:
                loc, rot, scale = base[bone.name]
                old_loc, old_q, _ = reference[bone.name]
                new_loc, new_q, _ = gesture[bone.name]
                delta = old_q.inverted() @ new_q
                bone.matrix_basis = Matrix.LocRotScale(loc+new_loc-old_loc, (rot@delta).normalized(), scale)
                bone.scale = scale
            bpy.context.view_layer.update()
            yaw = math.radians(.15) * math.sin(2*math.pi*t)
            roll = math.radians(.12) * math.sin(4*math.pi*t)
            offset = up * (.0008*math.sin(4*math.pi*t)) + toward * (.0015*(1-math.cos(2*math.pi*t)))
            if state in ('look_left','look_right'):
                sign = -1 if state=='look_left' else 1
                yaw -= sign*math.radians(.55)*bump(t,.055,.09,.105,.15)
                peak = .29 if state=='look_left' else .33
                u = (t-peak)/.18
                if 0<u<1:
                    yaw += sign*math.radians(.8)*math.sin(2*math.pi*u)*math.sin(math.pi*u)**2*math.exp(-2*u)
            if state=='scratch':
                roll += math.radians(.8)*bump(t,.34,.44,.62,.76)
            head = rig.pose.bones['Basic']
            world = rig.matrix_world @ head.matrix
            pivot = world.translation
            rotation = (Quaternion(up,yaw) @ Quaternion(toward,roll)).to_matrix().to_4x4()
            world = Matrix.Translation(offset) @ Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot) @ world
            head.matrix_basis = head.bone.convert_local_to_pose(rig.matrix_world.inverted()@world,head.bone.matrix_local,invert=True)
            head.scale = base['Basic'][2]
            bpy.context.view_layer.update()
            if lag:
                for i,bone in enumerate(roots):
                    world = rig.matrix_world @ bone.matrix
                    pivot = world.translation
                    correction = Quaternion(up,lag*(.45+.15*(i%3))).to_matrix().to_4x4()
                    pose = rig.matrix_world.inverted() @ Matrix.Translation(pivot) @ correction @ Matrix.Translation(-pivot) @ world
                    bone.matrix_basis = bone.bone.convert_local_to_pose(pose,bone.bone.matrix_local,parent_matrix=bone.parent.matrix,parent_matrix_local=bone.parent.bone.matrix_local,invert=True)
                    bone.scale = base[bone.name][2]
                    bpy.context.view_layer.update()
            for name, value in pose_values(rig).items():samples[name].append(value)
        description = entry['description']+'; asymmetrical timing, subtle settling and secondary motion'
        action = bake_action(rig,'POLISH | '+state,description,samples,frames)
        entry['source_action'] = old[state].name
        entry['action'] = action.name
        entry['revision'] = 'motion polish candidate 1'
    text=bpy.data.texts['STATE LIBRARY'];text.clear();text.write(json.dumps(catalog,indent=2))
    idle=bpy.data.actions['POLISH | watch'];rig.animation_data.action=idle;rig.animation_data.action_slot=idle.slots[0]
    scene.frame_set(1);scene.frame_start=1;scene.frame_end=193
    bpy.data.texts['START HERE'].write('\nMOTION POLISH CANDIDATE: approved STATE actions remain intact. POLISH actions add asymmetric timing, restrained anticipation/settling, eleven-hundredths-second claw follow-through, and breathing variation. Offline30FPS is a target, not a measured board rate.\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output.resolve()),compress=True)
    (HERE/'polish-states.json').write_text(json.dumps(catalog,indent=2)+'\n')
    print('Saved separate polish candidate:',args.output)


if __name__=='__main__':main()
