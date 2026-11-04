"""Millimetre-based appearance/fit study; not manufacturing CAD.

Run with Blender -b -P this_file. Measured outlines and assumed depths are
recorded in ../README.md. The approved slab model is intentionally untouched.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parents[1] / "tmp"
OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 0.001


def pbr(name, color, metal=0, rough=0.4):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes["Principled BSDF"]
    node.inputs["Base Color"].default_value = (*color, 1)
    node.inputs["Metallic"].default_value = metal
    node.inputs["Roughness"].default_value = rough
    return mat


silver = pbr("silver finish concept", (0.58, 0.61, 0.66), 0.8, 0.28)
black = pbr("black bezel", (0.009, 0.011, 0.014), 0.1, 0.17)
rubber = pbr("cable rubber", (0.015, 0.017, 0.021), 0, 0.65)
blue = pbr("LCD blue PCB", (0.015, 0.09, 0.21), 0.1, 0.4)
green = pbr("Pico green PCB", (0.015, 0.17, 0.08), 0, 0.43)
gold = pbr("connector gold", (0.72, 0.46, 0.10), 0.75, 0.3)
chip = pbr("IC packages", (0.025, 0.029, 0.035), 0, 0.55)
keymat = pbr("keyboard", (0.025, 0.028, 0.034), 0.1, 0.6)


def box(name, center, size, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("edge finish", "BEVEL")
        mod.width, mod.segments = bevel, 4
        obj.modifiers.new("weighted normals", "WEIGHTED_NORMAL")
    return obj


def face(name, x, y, z, width, height, material):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z))
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (math.pi / 2, 0, 0)
    obj.scale = (width, height, 1)
    obj.data.materials.append(material)
    return obj


def emission(name, color, strength=0.8):
    mat = pbr(name, color)
    n = mat.node_tree.nodes["Principled BSDF"]
    n.inputs["Emission Color"].default_value = (*color, 1)
    n.inputs["Emission Strength"].default_value = strength
    return mat


# Actual 160 x 128 pixel canvas; face art is an illustrative placeholder.
pixels = []
for row in range(128):
    for col in range(160):
        eye = any(((col - cx) / 14) ** 8 + ((row - 70) / 23) ** 8 < 1 for cx in (48, 111))
        pixels.extend((0.70, 0.88, 0.91, 1) if eye else (0.004, 0.007, 0.010, 1))
im = bpy.data.images.new("160x128 placeholder face", width=160, height=128)
im.pixels = pixels
screenmat = emission("LCD pixel face", (0.1, 0.1, 0.1))
nodes = screenmat.node_tree.nodes
tex = nodes.new("ShaderNodeTexImage")
tex.image, tex.interpolation = im, "Closest"
shader = nodes["Principled BSDF"]
screenmat.node_tree.links.new(tex.outputs["Color"], shader.inputs["Base Color"])
screenmat.node_tree.links.new(tex.outputs["Color"], shader.inputs["Emission Color"])

# Same axes and laptop envelope as cad/slab. Lid height/pose remain assumptions.
laptop = []
laptop.append(box("MacBook base 312.6 x 221.2", (0, -105.6, 5.5), (312.6, 221.2, 11), silver, 3))
laptop.append(box("MacBook lid 214 high assumed", (0, -2.25, 118), (312.6, 4.5, 214), silver, 2))
laptop.append(face("laptop black bezel", 0, -4.53, 118, 307, 208, black))
laptop.append(face("MacBook display", 0, -4.56, 118, 302.4, 196.4,
                   emission("muted blue desktop", (0.018, 0.045, 0.09), 0.5)))
for row in range(6):
    for col in range(14):
        laptop.append(box("keyboard key", (-122 + col * 18.6, -28 - row * 15.2, 11.15),
                          (16.5, 12.5, 0.7), keymat, 1.3))
laptop.append(box("trackpad", (0, -163, 11.13), (129, 79, 0.25), silver, 2))

X, Z = 186.4, 145.7
parts = {k: [] for k in ("front", "lcd", "headers", "pico", "rear")}


def part(group, name, x, depth, z, width, thick, height, mat, bevel=0):
    obj = box(name, (X + x, -5.3 + depth, Z + z), (width, thick, height), mat, bevel)
    parts[group].append(obj)
    return obj


# Envelope: old front proportions, conservative unverified depth for fitted headers.
part("front", "top frame", 0, 11, 23.825, 59, 22, 2, silver, 0.7)
part("front", "bottom frame", 0, 11, -23.825, 59, 22, 2, silver, 0.7)
part("front", "left frame", -28.5, 11, 0, 2, 22, 45.65, silver, 0.7)
# Split right wall leaves Micro-USB/cable access; exact cutout needs measurement.
part("front", "right wall above USB", 28.5, 11, 15, 2, 22, 15.65, silver, 0.7)
part("front", "right wall below USB", 28.5, 11, -15, 2, 22, 15.65, silver, 0.7)
part("front", "black front cover concept", 0, 0.5, 0, 56.6, 1, 47.25, black, 0.7)
part("lcd", "LCD carrier PCB 52 x 34.5", 0, 5.0, 0, 52, 1.6, 34.5, blue, 0.7)
part("lcd", "LCD module backing approximate", -2.57, 2.7, 0, 40.3, 3.0, 31.8, silver, 0.4)
active = face("visible LCD 35.04 x 28.03", X - 2.57, -5.34, Z, 35.04, 28.03, screenmat)
parts["lcd"].append(active)
# Header positions follow Pico 17.78 mm row spacing and 2.54 mm pin pitch.
for z in (-8.89, 8.89):
    part("headers", "female header body assumed 8.5mm", 0, 10.05, z, 50.8, 8.5, 2.54, chip, 0.25)
    for i in range(20):
        part("headers", "contact", (i - 9.5) * 2.54, 13.5, z, 0.64, 2, 0.64, gold)
part("pico", "Pico WH PCB 51 x 21 x 1", 0, 15.1, 0, 51, 1, 21, green, 0.5)
part("pico", "RP2040 approximate location", -2, 16.4, 0, 7, 1.6, 7, chip, 0.2)
part("pico", "wireless RF shield approximate", -15, 16.6, 0, 10, 2, 9, silver, 0.3)
part("pico", "Micro USB port simplified", 23.2, 16.9, 0, 6, 3, 8, silver, 0.4)
part("pico", "BOOTSEL approximate", 17, 16.6, 4, 3.5, 2, 3, black, 0.2)
part("rear", "removable rear cover concept", 0, 21.2, 0, 56.6, 1.6, 47.25, silver, 1)

# A simple rear bridge is a visual mounting proposal, not validated attachment.
mount = box("rear bridge concept", (157, 19, Z), (32, 3, 27), silver, 1)
# Direct Micro-B cable. Only an illustrative route, not a verified 300mm harness.
plug = box("Micro B overmold assumed", (X + 34.5, 11.6, Z), (18, 6, 9), rubber, 1)
bpy.ops.curve.primitive_bezier_curve_add()
cable = bpy.context.object
cable.name = "illustrative direct USB cable route"
curve = cable.data
curve.dimensions = "3D"
curve.bevel_depth, curve.bevel_resolution = 1.4, 4
spline = curve.splines[0]
points = [(X+43.5,11.6,Z),(244,15,141),(242,20,72),(222,8,24),(192,-20,11),(174,-40,6)]
spline.bezier_points.add(len(points)-2)
for point, co in zip(spline.bezier_points, points):
    point.co = co
    point.handle_left_type = point.handle_right_type = "AUTO"
curve.materials.append(rubber)
usbc = box("USB C overmold assumed", (166,-40,6), (20,8,5), rubber, 1)

bpy.context.view_layer.update()
# Checks use actual built object bounds, not just a restatement of constants.
lcdpcb = next(o for o in parts["lcd"] if o.name.startswith("LCD carrier"))
pico = next(o for o in parts["pico"] if o.name.startswith("Pico WH PCB"))
assert abs(lcdpcb.dimensions.x - 52) < 1e-6 and abs(lcdpcb.dimensions.z - 34.5) < 1e-6
assert abs(pico.dimensions.x - 51) < 1e-6 and abs(pico.dimensions.z - 21) < 1e-6
assert lcdpcb.dimensions.x < 55 and lcdpcb.dimensions.z < 45.65
assert abs(active.dimensions.x - 35.04) < 1e-6 and abs(active.dimensions.z - 28.03) < 1e-6
assert max(o.location.y + o.dimensions.y/2 for o in parts["pico"]) < 15.9
report = {"units":"mm", "enclosure_concept":[59,49.65,22],
          "lcd_board_verified_outline":[52,34.5], "active_verified":[35.04,28.03],
          "pico_verified_outline":[51,21,1], "depth_and_components":"ASSUMED",
          "cable":"illustrative routing only; no 30cm fit certification",
          "checks":"nominal board envelopes and active area passed"}
(OUT / "fit_assumptions.json").write_text(json.dumps(report, indent=2))

floor = box("studio desk", (0,0,-3), (2200,2200,5), pbr("desk",(0.16,0.18,0.21),0,0.75))
world = bpy.data.worlds.new("studio")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.55,0.62,0.75,1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.5
for loc, energy, size in [((120,-350,500),140000,350),((-350,-80,300),80000,300),((300,200,400),110000,250)]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.data.energy, light.data.shape, light.data.size = energy,"DISK",size
    light.rotation_euler = (Vector((30,0,100))-light.location).to_track_quat("-Z","Y").to_euler()
sc.render.engine = "CYCLES"
sc.cycles.samples, sc.cycles.use_denoising = 48, True
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "AgX"


def shot(name, loc, target, lens):
    bpy.ops.object.camera_add(location=loc)
    camera = bpy.context.object
    camera.data.lens = lens
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    sc.camera = camera
    sc.render.filepath = str(OUT/name)
    bpy.ops.render.render(write_still=True)


shot("budget_macbook.png", (370,-620,300), (38,-35,110), 48)
shot("budget_close.png", (X+105,-175,Z+70), (X,5,Z), 72)
# Exploded assembly exposes actual footprints and shows plug-on connection order.
for obj in [*laptop,mount,plug,cable,usbc]:
    obj.hide_render = True
for key, delta in {"front":(-30,-60,0),"lcd":(-14,-30,0),"headers":(0,0,0),"pico":(14,30,0),"rear":(30,60,0)}.items():
    for obj in parts[key]:
        obj.location += Vector(delta)
shot("budget_exploded.png", (X+170,250,Z+130), (X,7,Z), 65)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"budget_preview.blend"))
print("FIT_CHECKS", json.dumps(report))
