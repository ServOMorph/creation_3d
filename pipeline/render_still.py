import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out_png = Path(argv[0] if argv else "assets/mpfb_test/still.png")
device = argv[1] if len(argv) > 1 else "CPU"
samples = int(argv[2]) if len(argv) > 2 else 64
framing = argv[3] if len(argv) > 3 else "full"
frame = int(argv[4]) if len(argv) > 4 else None

scene = bpy.context.scene
if frame is not None:
    scene.frame_set(frame)
scene.render.engine = "CYCLES"
scene.cycles.device = device
if device == "GPU":
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
scene.cycles.samples = samples
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720 if framing == "full" else 1280
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -1.3

bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.active_object
mat = bpy.data.materials.new("Ground")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.32, 0.30, 0.28, 1)
bsdf.inputs["Roughness"].default_value = 0.85
ground.data.materials.append(mat)

world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
sky = world.node_tree.nodes.new("ShaderNodeTexSky")
sky.sky_type = "NISHITA"
sky.sun_elevation = 0.45
sky.sun_rotation = 2.3
world.node_tree.links.new(sky.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 0.35


def add_area(name, loc, energy, size, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    direction = Vector((0, 0, 1.2)) - Vector(loc)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(obj)


add_area("Key", (2.5, -3.0, 3.2), 900, 2.0, (1.0, 0.95, 0.88))
add_area("Fill", (-3.0, -2.0, 1.8), 250, 3.0, (0.85, 0.9, 1.0))
add_area("Rim", (-1.0, 3.0, 2.8), 600, 1.5)

if framing == "full":
    target, cam_loc, lens = Vector((0, 0, 0.95)), Vector((0.9, -4.6, 1.25)), 50
elif framing == "side":
    rig = next(o for o in scene.objects if o.type == "ARMATURE")
    p = rig.matrix_world @ rig.pose.bones["pelvis"].head
    target = Vector((p.x, p.y, 0.95))
    cam_loc, lens = target + Vector((4.6, -1.2, 0.3)), 50
else:
    target, cam_loc, lens = Vector((0, 0, 1.68)), Vector((0.25, -1.1, 1.70)), 85
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = lens
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = cam_loc
cam.rotation_euler = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(cam)
scene.camera = cam

if not globals().get("SETUP_ONLY"):
    scene.render.filepath = str(out_png.resolve())
    bpy.ops.render.render(write_still=True)
    print("RENDER_OK", out_png)
