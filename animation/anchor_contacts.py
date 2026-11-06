"""Add native, non-stretch contact constraints to a separate character candidate."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_states import bake_action, pose_values, smooth


def release_at(t):
    return smooth((t-.12)/.10) * (1-smooth((t-.78)/.10))


def main():
    output = HERE/'crying-head-2-anchored.blend'
    if output.exists():
        raise FileExistsError(output)
    scene = bpy.context.scene
    rig = bpy.data.objects['Crying head 2 | source rig']
    mesh = next(o for o in rig.children if o.type == 'MESH')
    catalog = json.loads(bpy.data.texts['STATE LIBRARY'].as_string())
    manifest = json.loads((HERE/'character.json').read_text())
    chains = [c['weighted_bones'] for c in manifest['appendage_chains']
              if c['root'] not in {'Virus1.017.L','Virus1.021.L','Virus1.017.R','Virus1.021.R'}]
    assert len(chains) == 8 and not any(b.constraints for b in rig.pose.bones)
    frames = tuple(range(1,194))
    cache = {}
    for state, entry in catalog.items():
        action = bpy.data.actions[entry['action']]
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        rows = []
        for frame in frames:
            scene.frame_set(frame)
            basic = rig.pose.bones['Basic'].matrix.copy()
            roots = {chain[0]: basic.inverted() @ rig.pose.bones[chain[0]].head for chain in chains}
            rows.append((pose_values(rig), roots))
        cache[state] = rows
    reference = cache['watch'][0][0]
    # Restore reference before creating world-space grip controls.
    rig.animation_data.action = None
    for b in rig.pose.bones:
        b.matrix_basis = Matrix.LocRotScale(*reference[b.name])
    bpy.context.view_layer.update()
    anchors = bpy.data.collections.new('CONTACTS | fixed support grips')
    character=next(c for c in rig.users_collection if c.name.startswith('CHARACTER'))
    character.children.link(anchors)
    specs = []
    evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    for names in chains:
        last = rig.pose.bones[names[-1]]
        control = bpy.data.objects.new('GRIP | '+names[0], None)
        anchors.objects.link(control)
        control.empty_display_type = 'CUBE'
        control.empty_display_size = .035
        control.matrix_world = rig.matrix_world @ last.matrix
        control['note'] = 'Unparented world contact. Move to retarget the grip; do not parent to the head.'
        idx = mesh.vertex_groups[last.name].index
        candidates = []
        for vertex in mesh.data.vertices:
            groups = [g for g in vertex.groups if g.weight > .0001]
            if len(groups) == 1 and groups[0].group == idx:
                pos = rig.matrix_world.inverted() @ evaluated.matrix_world @ evaluated.data.vertices[vertex.index].co
                local = last.matrix.inverted() @ pos
                candidates.append((local.y, vertex.index))
        assert candidates, last.name
        tip = max(candidates)[1]
        lengths = [(rig.matrix_world.to_3x3() @ (rig.pose.bones[n].tail-rig.pose.bones[n].head)).length for n in names[:-1]]
        specs.append({'root': names[0], 'bones': names, 'control': control.name,
                      'wrist_world': list(control.location), 'matrix_world': [list(row) for row in control.matrix_world],
                      'tip_vertex': tip, 'tip_world': list(evaluated.matrix_world @ evaluated.data.vertices[tip].co),
                      'reach_max': sum(lengths)-.015, 'reach_min': max(0.,2*max(lengths)-sum(lengths))+.005})
    head_rest = rig.data.bones['Basic'].matrix_local
    scale0 = reference['Basic'][2]
    def head_basis(values, factor, baseline):
        loc0, q0, _ = baseline['Basic']
        loc, q, _ = values['Basic']
        return Matrix.LocRotScale(loc0.lerp(loc,factor),q0.slerp(q,factor).normalized(),scale0)
    def reachable(state, factor):
        for frame, (values, roots) in zip(frames,cache[state]):
            pose = head_rest @ head_basis(values,factor,cache['watch'][frame-1][0])
            world = rig.matrix_world @ pose
            for spec in specs:
                if state=='scratch' and spec['root']=='Virus1.013.L' and release_at((frame-1)/192)>0:
                    continue
                root = world @ roots[spec['root']]
                distance = (root-Vector(spec['wrist_world'])).length
                if not spec['reach_min'] <= distance <= spec['reach_max']:
                    return False
        return True
    factors = {}
    for state in catalog:
        assert reachable(state,0), state
        low, high = 0.,1.
        if reachable(state,1): low = 1.
        else:
            for _ in range(24):
                mid=(low+high)/2
                if reachable(state,mid):low=mid
                else:high=mid
            low *= .98
        factors[state] = low
    # Keep source FK takes as inputs. Native IK remains active between all sampled frames.
    rig['contacts_enabled'] = True
    rig.id_properties_ui('contacts_enabled').update(description='Disable to preview the free pose; enable to plant the supports')
    rig['scratch_release'] = 0.
    rig.id_properties_ui('scratch_release').update(min=0.,max=1.)
    for spec in specs:
        names=spec['bones'];control=bpy.data.objects[spec['control']]
        ik=rig.pose.bones[names[-2]].constraints.new('IK')
        ik.name='Support | fixed wrist';ik.target=control;ik.chain_count=len(names)-1
        ik.use_tail=True;ik.use_location=True;ik.use_rotation=False;ik.use_stretch=False;ik.iterations=1000
        lock=rig.pose.bones[names[-1]].constraints.new('COPY_ROTATION')
        lock.name='Support | stationary grip orientation';lock.target=control
        lock.target_space=lock.owner_space='WORLD'
        position=rig.pose.bones[names[-1]].constraints.new('COPY_LOCATION')
        position.name='Support | exact planted location';position.target=control
        position.target_space=position.owner_space='WORLD'
        for constraint in (ik,lock,position):
            driver=constraint.driver_add('influence').driver
            var=driver.variables.new();var.name='enabled';var.type='SINGLE_PROP'
            var.targets[0].id=rig;var.targets[0].data_path='["contacts_enabled"]'
            driver.expression='enabled'
            if names[0]=='Virus1.013.L':
                var=driver.variables.new();var.name='release';var.type='SINGLE_PROP'
                var.targets[0].id=rig;var.targets[0].data_path='["scratch_release"]'
                driver.expression='enabled*(release < 0.000001)' if constraint==position else 'enabled*(1-release)'
    for state,entry in catalog.items():
        samples={b.name:[] for b in rig.pose.bones}
        for index,(values,_) in enumerate(cache[state]):
            for name,value in values.items():
                if name=='Basic':
                    loc,q,scale=head_basis(values,factors[state],cache['watch'][index][0]).decompose()
                    samples[name].append((loc,q.normalized(),scale0.copy()))
                else:samples[name].append(value)
        action=bake_action(rig,'ANCHORED | '+state,entry['description']+' with planted support claws',samples,frames)
        bag=action.layers[0].strips[0].channelbag(action.slots[0])
        curve=bag.fcurves.new(data_path='["scratch_release"]',index=0)
        points=[(frame,release_at((frame-1)/192) if state=='scratch' else 0.) for frame in frames]
        curve.keyframe_points.add(len(points));curve.keyframe_points.foreach_set('co',[x for pair in points for x in pair])
        for key in curve.keyframe_points:
            key.interpolation='BEZIER';key.handle_left_type=key.handle_right_type='AUTO_CLAMPED'
        curve.update()
        entry['source_action']=entry['action'];entry['action']=action.name
        entry['head_motion_factor']=factors[state];entry['revision']='planted support candidate 1'
    idle=bpy.data.actions['ANCHORED | watch'];rig.animation_data.action=idle;rig.animation_data.action_slot=idle.slots[0]
    scene.frame_set(1);scene.frame_start=1;scene.frame_end=193
    text=bpy.data.texts['STATE LIBRARY'];text.clear();text.write(json.dumps(catalog,indent=2))
    data={'supports':specs,'head_motion_factors':factors,'scratch_release':'Only Virus1.013.L releases while scratching; other seven remain planted.'}
    text=bpy.data.texts.new('CONTACT MAP');text.write(json.dumps(data,indent=2))
    bpy.data.texts['START HERE'].write('\nPLANTED SUPPORTS: eight unparented GRIP controls pin the original distal claw segments. Native non-stretch IK bends the proximal joints. No walls or geometry added. Scratch releases only its active claw, then regrips. Head excursion is reduced where required by limb reach. CONTACT MAP records actual mesh-tip vertices.\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
    (HERE/'contacts.json').write_text(json.dumps(data,indent=2)+'\n')
    (HERE/'anchored-states.json').write_text(json.dumps(catalog,indent=2)+'\n')
    print('Saved planted candidate:',output,'head factors:',factors)


if __name__=='__main__':main()
