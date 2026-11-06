"""Check actual planted mesh vertices, joint continuity, and grip/release behavior."""
import json
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from render_character import select_clip
from frame_timing import frame_times


def main():
    scene=bpy.context.scene
    rig=bpy.data.objects['Crying head 2 | source rig']
    mesh=next(o for o in rig.children if o.type=='MESH')
    data=json.loads(bpy.data.texts['CONTACT MAP'].as_string())
    catalog=json.loads(bpy.data.texts['STATE LIBRARY'].as_string())
    assert len(data['supports'])==8 and rig['contacts_enabled']==1
    for spec in data['supports']:
        control=bpy.data.objects[spec['control']]
        assert control.parent is None and control.animation_data is None
    report={}
    for state in catalog:
        select_clip(state)
        drift=gap=pixel_drift=0.
        for source_time in frame_times(1,193,24,30)+[193.]:
            frame=int(source_time);scene.frame_set(frame,subframe=source_time-frame)
            ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
            release=rig['scratch_release']
            for spec in data['supports']:
                names=spec['bones']
                wrist=rig.pose.bones[names[-1]];previous=rig.pose.bones[names[-2]]
                error=(wrist.head-previous.tail).length
                gap=max(gap,error)
                assert error<.0001,(state,source_time,spec['root'],'disconnected joint',error,release)
                planted=spec['root']!='Virus1.013.L' or release<1e-6
                if planted:
                    point=ev.matrix_world@ev.data.vertices[spec['tip_vertex']].co
                    reference=Vector(spec['tip_world'])
                    error=(point-reference).length;drift=max(drift,error)
                    assert error<.00001,(state,source_time,spec['root'],'sliding claw',error)
                    a=world_to_camera_view(scene,scene.camera,point)
                    b=world_to_camera_view(scene,scene.camera,reference)
                    error=Vector(((a.x-b.x)*240,(a.y-b.y)*280)).length
                    pixel_drift=max(pixel_drift,error)
                    assert error<.01,(state,source_time,spec['root'],'visible contact drift',error)
        report[state]={'max_world_tip_drift':drift,'max_projected_tip_drift_pixels':pixel_drift,'max_joint_gap':gap}
    (HERE/'contact-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: fixed actual tips, connected joints, controlled scratch release at30FPS')


if __name__=='__main__':main()
