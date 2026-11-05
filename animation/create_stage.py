"""One-time Blender stage setup. Pose and animate in the saved .blend afterward."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "occupant-stage.blend"
if not bpy.app.background:
    raise RuntimeError("Create the stage in a separate background Blender session")
if OUTPUT.exists():
    raise FileExistsError("Stage already exists; open it instead of rebuilding it")

bpy.ops.wm.read_homefile(use_empty=True, use_factory_startup=True)
scene = bpy.context.scene
scene.name = "Occupant animation stage"
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 240, 280
scene.render.resolution_percentage = 100
scene.render.fps, scene.render.fps_base = 12, 1.0
scene.frame_start, scene.frame_end = 1, 48
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.filepath = "//tmp/frames/"
scene.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("Black background")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0
scene.world = world

bpy.ops.object.camera_add(location=(0, -0.8, 1.65))
camera = bpy.context.object
camera.name = "Display camera 240x280"
camera.data.lens = 70
camera.rotation_euler = (Vector((0, 0, 1.65)) - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera
for name, position, energy, size in (
    ("Soft key", (-1.2, -1.8, 2.7), 180, 1.6),
    ("Dim fill", (1.4, -0.8, 1.8), 35, 1.0),
):
    bpy.ops.object.light_add(type="AREA", location=position)
    light = bpy.context.object
    light.name, light.data.energy, light.data.size = name, energy, size
    light.rotation_euler = (Vector((0, 0, 1.4)) - light.location).to_track_quat("-Z", "Y").to_euler()

image = bpy.data.images.load(str(HERE.parent / "experiments/assets/occupant-source.png"))
image.pack()
reference = bpy.data.objects.new("Approved LOOK reference — not a 3D model", None)
reference.empty_display_type = "IMAGE"
reference.data = image
reference.empty_display_size = 1.7
reference.location = (-1.5, 0, 1.45)
reference.rotation_euler.x = math.pi / 2
reference.hide_render = True
scene.collection.objects.link(reference)
subject = bpy.data.collections.new("CHARACTER — awaiting model selection")
scene.collection.children.link(subject)

notes = bpy.data.texts.new("START HERE")
notes.write("Stage only: no character or animation has been imported.\n"
            "Choose a rigged model together before modifying anatomy.\n"
            "Free head/face only: centered mugshot with readable eyes.\n"
            "First proof: calm gaze, blink and one head turn at 240x280.\n"
            "Work in this saved scene; do not regenerate it for pose changes.\n")
assert scene.render.resolution_x == 240 and scene.render.resolution_y == 280
assert scene.render.fps == 12 and image.packed_file
assert not any(obj.type == "MESH" for obj in scene.objects)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
assert OUTPUT.is_file()
print("Saved stage:", OUTPUT)
