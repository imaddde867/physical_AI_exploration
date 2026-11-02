import bpy, math, sys, os
from mathutils import Vector, Matrix
here = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
import glob
for f in sorted(glob.glob(os.path.join(here, "../tmp/parts", "*.stl"))):
    try: bpy.ops.wm.stl_import(filepath=f)
    except AttributeError: bpy.ops.import_mesh.stl(filepath=f)
    bpy.context.selected_objects[0].name = os.path.basename(f)[:-4]
sc = bpy.context.scene

def pbr(name, col, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    return m
alu = pbr("alu", (0.78, 0.79, 0.81, 1), 1, 0.30)
dark = pbr("glass", (0.008, 0.008, 0.01, 1), 0, 0.04)
arm = pbr("arm", (0.55, 0.57, 0.6, 1), 1, 0.4)
gold = pbr("contact_gold", (0.95, 0.65, 0.12, 1), 0.8, 0.28)
polymer = pbr("insulating_polymer", (0.88, 0.81, 0.66, 1), 0, 0.55)
magnet = pbr("magnet", (0.15, 0.16, 0.18, 1), 0.75, 0.37)
bond = pbr("bondline", (0.34, 0.38, 0.42, 1), 0, 0.62)
rubber = pbr("cable", (0.025, 0.028, 0.033, 1), 0, 0.72)

objs = [o for o in sc.objects if o.type == "MESH"]
print("OBJS", [o.name for o in objs])
# Static nominal CAD view only. Rotating the lid would require deforming the cable.
R = Matrix.Identity(4)
for o in objs:
    n = o.name.lower()
    o.data.materials.clear()
    mat = (dark if "glass" in n else
           bond if "magnet_bond" in n else
           magnet if "magnet" in n else
           polymer if ("insulator" in n or "carrier" in n or "grommet" in n) else
           gold if "contact_" in n else
           rubber if "cable" in n else
           arm if ("arm" in n or "clip" in n) else alu)
    o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = False
    if "deck" not in n:
        o.matrix_world = R @ o.matrix_world

glass = next(o for o in objs if "glass" in o.name.lower())

# lit display on the lid front
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -4.55, 112)); sp = bpy.context.active_object
sp.rotation_euler = (math.radians(90), 0, 0); sp.scale = (302.4, 196.4, 1)
sm = bpy.data.materials.new("screen"); sm.use_nodes = True; sn = sm.node_tree; sn.nodes.clear()
e = sn.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.05, 0.09, 0.2, 1); e.inputs["Strength"].default_value = 0.8
o2 = sn.nodes.new("ShaderNodeOutputMaterial"); sn.links.new(e.outputs[0], o2.inputs[0])
sp.data.materials.append(sm); bpy.context.view_layer.update(); sp.matrix_world = R @ sp.matrix_world
# floor + world
bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, -100, -0.1))
fl = bpy.context.active_object; fl.data.materials.append(pbr("floor", (0.55, 0.45, 0.35, 1), 0, 0.6))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.78, 0.85, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
for loc, e in (((250, -400, 500), 120000), ((-300, -200, 300), 40000),
               ((260, 240, 280), 60000)):
    bpy.ops.object.light_add(type='AREA', location=loc); L = bpy.context.active_object
    L.data.energy = e; L.data.size = 300
    L.rotation_euler = (Vector((0, 0, 100)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

smoke = os.environ.get("MACDESK_RENDER_SMOKE") == "1"
sc.render.engine = 'CYCLES'
sc.cycles.samples = 2 if smoke else 64
sc.cycles.use_denoising = not smoke
sc.render.resolution_x, sc.render.resolution_y = ((320, 200) if smoke else (1800, 1100))
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'
def shot(name, loc, target, lens):
    bpy.ops.object.camera_add(location=loc); c = bpy.context.active_object
    c.data.lens = lens; sc.camera = c
    c.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(here, "../tmp", name); bpy.ops.render.render(write_still=True)
pod_c = sum((glass.matrix_world @ Vector(c) for c in glass.bound_box), Vector()) / 8
shot("render_wide.png", (330, -650, 250), (40, 0, 115), 40)
shot("render_close.png", (260, -330, 235), tuple(pod_c), 85)

# The ordinary exterior views conceal the dock. Render each mating half alone.
# The mount front view shows the recessed contact carrier and the rear screen
# view shows pogo barrels, insulation, locating dowels, and magnet pockets.
sp.hide_render = True
fl.hide_render = True  # the floor otherwise obscures the lower docking features
# Ubuntu's headless Blender build lacks OpenImageDenoiser; use more
# samples instead of enabling unsupported denoising in smoke mode.
sc.cycles.samples = 32 if smoke else 64
sc.cycles.use_denoising = not smoke
sc.render.resolution_x, sc.render.resolution_y = ((800, 500) if smoke else (2000, 1250))
for o in objs:
    n = o.name.lower()
    o.hide_render = not any(k in n for k in (
        "mount_plate", "insulating_contact_carrier", "mount_contact_",
        "captive_cable_grommet"))
shot("render_mount_detail.png", (200, -150, 182), (177, 0.8, 151), 55)

for o in objs:
    n = o.name.lower()
    o.hide_render = not any(k in n for k in (
        "screen_shell", "screen_glass", "screen_contact_",
        "contact_insulator_", "magnet"))
shot("render_screen_back.png", (215, 145, 183), (187, 0, 152), 70)
