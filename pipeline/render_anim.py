import runpy
import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out_dir = Path(argv[0])
device = argv[1] if len(argv) > 1 else "GPU"
samples = argv[2] if len(argv) > 2 else "64"
out_dir.mkdir(parents=True, exist_ok=True)

sys.argv = [sys.argv[0], "--", str(out_dir / "_unused.png"), device, samples, "full"]
runpy.run_path(str(Path(__file__).with_name("render_still.py")), init_globals={"SETUP_ONLY": True}, run_name="__main__")

scene = bpy.context.scene
cam = scene.camera
rig = next(o for o in scene.objects if o.type == "ARMATURE")
offset = Vector((4.6, -1.2, 0.3))
smooth = None
for f in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(f)
    p = rig.matrix_world @ rig.pose.bones["pelvis"].head
    target = Vector((p.x, p.y, 0.95))
    smooth = target if smooth is None else smooth.lerp(target, 0.15)
    cam.location = smooth + offset
    cam.rotation_euler = (smooth - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)

scene.frame_set(scene.frame_start)
for light in [o for o in scene.objects if o.type == "LIGHT"]:
    light.parent = cam
    light.matrix_parent_inverse = cam.matrix_world.inverted()

scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str((out_dir / "frame_").resolve())
bpy.ops.render.render(animation=True)
print("ANIM_OK", out_dir)
