"""Check the saved foundation against the clean source import, without saving edits."""
import json
import math
from pathlib import Path

import bpy
from bpy_extras.anim_utils import animdata_get_channelbag_for_assigned_slot
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


def action_keys(action):
    return sorted(
        (curve.data_path, curve.array_index,
         tuple((tuple(key.co), key.interpolation) for key in curve.keyframe_points))
        for layer in action.layers for strip in layer.strips
        for bag in strip.channelbags for curve in bag.fcurves
    )


def main():
    base = Path(__file__).resolve().parent
    scene = bpy.context.scene
    rig = bpy.data.objects["Crying head 2 | source rig"]
    mesh = next(o for o in rig.children if o.type == "MESH")
    actions = {name: bpy.data.actions["SOURCE | " + name] for name in ("Idle", "move")}
    manifest = json.loads((base / "character.json").read_text())
    assert len(rig.data.bones) == manifest["bones"] == 95
    assert len(mesh.data.vertices) == manifest["vertices"] == 3322
    assert scene.render.fps == 24
    assert (scene.render.resolution_x, scene.render.resolution_y) == (240, 280)
    assert scene.camera.name == "CAM | Window close-up"
    assert rig.animation_data.action.name == "DERIVED | Watch rest"
    assert mesh.data.shape_keys is None
    for material in mesh.data.materials:
        for node in material.node_tree.nodes:
            if node.type == "TEX_IMAGE":
                assert node.image and node.image.packed_file and node.image.size[0] > 0
    with bpy.data.libraries.load(str(base / "crying-head-2-source.blend")) as (src, dst):
        dst.objects = [rig.name, mesh.name]
        dst.actions = list(src.actions)
    source_rig = dst.objects[0]
    source_object = dst.objects[1]
    source_mesh = source_object.data
    assert [(b.name, b.parent.name if b.parent else None, tuple(b.matrix_local))
            for b in rig.data.bones] == [
                (b.name, b.parent.name if b.parent else None, tuple(b.matrix_local))
                for b in source_rig.data.bones]
    assert [tuple(v.co) for v in mesh.data.vertices] == [tuple(v.co) for v in source_mesh.vertices]
    assert [tuple(p.vertices) for p in mesh.data.polygons] == [tuple(p.vertices) for p in source_mesh.polygons]
    assert [[(g.group, g.weight) for g in v.groups] for v in mesh.data.vertices] == [
        [(g.group, g.weight) for g in v.groups] for v in source_mesh.vertices]
    assert [g.name for g in mesh.vertex_groups] == [g.name for g in source_object.vertex_groups]
    for name, action in actions.items():
        original = next(a for a in dst.actions if "|" + name in a.name)
        assert action_keys(action) == action_keys(original), f"Source keys changed: {name}"
    rest = bpy.data.actions["DERIVED | Watch rest"]
    jaw_paths = {'pose.bones["Jaw"].location', 'pose.bones["Jaw"].rotation_quaternion'}
    assert [key for key in action_keys(rest) if key[0] not in jaw_paths] == [
        key for key in action_keys(actions["Idle"]) if key[0] not in jaw_paths]
    report = {"source_geometry_weights_bones_and_keys_preserved": True,
              "used_material_textures_packed": True, "clips": {}, "appendage_controls": {}}
    camera = bpy.data.objects["CAM | Full character"]
    for name, action in {**actions, "Watch rest": rest}.items():
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        bag = animdata_get_channelbag_for_assigned_slot(rig.animation_data)
        assert bag and bag.fcurves
        samples = []
        for frame in range(int(action.frame_range[0]), int(action.frame_range[1]) + 1):
            scene.frame_set(frame)
            if name == "Watch rest":
                jaw = rig.pose.bones["Jaw"]
                assert jaw.location.length < 1e-6
                assert abs(jaw.rotation_quaternion.w - 1) < 1e-6
                assert sum(component * component for component in jaw.rotation_quaternion[1:]) < 1e-12
            evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
            coords = [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]
            for point in coords:
                assert all(math.isfinite(x) for x in point)
                p = world_to_camera_view(scene, camera, point)
                assert 0 <= p.x <= 1 and 0 <= p.y <= 1 and p.z > 0, (name, frame, "wide camera clips")
            samples.append(coords)
        movement = max((p - q).length for p, q in zip(samples[0], samples[len(samples) // 2]))
        seam = max((p - q).length for p, q in zip(samples[0], samples[-1]))
        assert movement > .001, f"Static clip: {name}"
        report["clips"][name] = {"frames": len(samples), "max_midclip_displacement": movement,
                                  "endpoint_max_distance": seam}
    # Exercise each weighted appendage chain independently with a small FK rotation.
    rig.animation_data.action = None
    for bone in rig.pose.bones:
        bone.matrix_basis.identity()
    bpy.context.view_layer.update()
    def vertices():
        evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return [v.co.copy() for v in evaluated.data.vertices]
    rest = vertices()
    for chain in manifest["appendage_chains"]:
        bone = rig.pose.bones[chain["root"]]
        bone.rotation_mode = "XYZ"
        bone.rotation_euler.z = .08
        bpy.context.view_layer.update()
        displacement = max((p - q).length for p, q in zip(rest, vertices()))
        assert displacement > .001, f"Unresponsive chain: {bone.name}"
        report["appendage_controls"][bone.name] = displacement
        bone.matrix_basis.identity()
        bpy.context.view_layer.update()
    assert len(report["appendage_controls"]) == 12
    (base / "character-checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS: source preserved, packed textures, source clips + closed rest, wide camera, all 12 appendage chains")


if __name__ == "__main__":
    main()
