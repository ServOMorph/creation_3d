import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
bvh_path = Path(argv[0])
out_dir = Path(argv[1])
clip_name = argv[2] if len(argv) > 2 else "clip"
out_dir.mkdir(parents=True, exist_ok=True)

MAP = {
    "Hips": "pelvis", "Spine1": "spine_01", "Spine2": "spine_02", "Chest": "spine_03",
    "Neck1": "neck_01", "Head": "head",
    "LeftLeg": "thigh_l", "LeftShin": "calf_l", "LeftFoot": "foot_l", "LeftToeBase": "ball_l",
    "RightLeg": "thigh_r", "RightShin": "calf_r", "RightFoot": "foot_r", "RightToeBase": "ball_r",
}
for side, s in (("Left", "l"), ("Right", "r")):
    MAP.update({
        f"{side}Shoulder": f"clavicle_{s}", f"{side}Arm": f"upperarm_{s}",
        f"{side}ForeArm": f"lowerarm_{s}", f"{side}Hand": f"hand_{s}",
    })
    for i in range(3):
        MAP[f"{side}HandThumb{i + 1}"] = f"thumb_0{i + 1}_{s}"
        for finger, ue in (("Index", "index"), ("Middle", "middle"), ("Ring", "ring"), ("Pinky", "pinky")):
            MAP[f"{side}Hand{finger}{i + 2}"] = f"{ue}_0{i + 1}_{s}"

target = next(o for o in bpy.data.objects if o.type == "ARMATURE")
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.import_anim.bvh(filepath=str(bvh_path), global_scale=0.01, axis_forward="-Z", axis_up="Y",
                        update_scene_fps=True, update_scene_duration=True, rotate_mode="NATIVE")
source = bpy.context.selected_objects[0]
scene = bpy.context.scene
action = source.animation_data.action
f_start, f_end = (int(round(v)) for v in action.frame_range)

src_mw = source.matrix_world
tgt_mw = target.matrix_world
tgt_mw_inv = tgt_mw.inverted()
inv_map = {v: k for k, v in MAP.items()}


def rot(m):
    return m.to_quaternion().to_matrix().to_4x4()


DIR_CHILD = {"Hips": "Spine1", "Chest": "Neck1", "Head": "HeadEnd",
             "LeftHand": "LeftHandMiddle1", "RightHand": "RightHandMiddle1"}
ARM_SPREAD_DEG = float(argv[3]) if len(argv) > 3 else 6.0

src_rest = {b.name: rot(src_mw @ b.matrix_local) for b in source.data.bones}
src_dir = {}
for b in source.data.bones:
    child = source.data.bones.get(DIR_CHILD.get(b.name, ""))
    tip = child.head_local if child else b.tail_local
    src_dir[b.name] = (src_mw.to_3x3() @ (tip - b.head_local)).normalized()
tgt_ref = {}
for b in target.data.bones:
    rest_w = rot(tgt_mw @ b.matrix_local)
    src_name = inv_map.get(b.name)
    if src_name and src_name in src_dir:
        cur_dir = (tgt_mw.to_3x3() @ (b.tail_local - b.head_local)).normalized()
        swing = cur_dir.rotation_difference(src_dir[src_name]).to_matrix().to_4x4()
        rest_w = swing @ rest_w
    tgt_ref[b.name] = rest_w

src_hips = source.data.bones["Hips"]
tgt_pelvis = target.data.bones["pelvis"]
scale = (tgt_mw @ tgt_pelvis.head_local).z / (src_mw @ src_hips.head_local).z

order = []
def walk(bone):
    order.append(bone)
    for c in bone.children:
        walk(c)
for b in target.data.bones:
    if b.parent is None:
        walk(b)

target.animation_data_create()
tgt_action = bpy.data.actions.new(clip_name)
target.animation_data.action = tgt_action
for pb in target.pose.bones:
    pb.rotation_mode = "QUATERNION"

for f in range(f_start, f_end + 1):
    scene.frame_set(f)
    arm_space = {}
    for b in order:
        pb = target.pose.bones[b.name]
        src_name = inv_map.get(b.name)
        parent_arm = arm_space[b.parent.name] if b.parent else Matrix.Identity(4)
        rest_rel = (b.parent.matrix_local.inverted() @ b.matrix_local) if b.parent else b.matrix_local
        if src_name and src_name in source.pose.bones:
            spb = source.pose.bones[src_name]
            src_w = rot(src_mw @ spb.matrix)
            want_w = src_w @ src_rest[src_name].inverted() @ tgt_ref[b.name]
            if b.name in ("upperarm_l", "upperarm_r") and ARM_SPREAD_DEG:
                hips = source.pose.bones["Hips"]
                fwd = (rot(src_mw @ hips.matrix) @ src_rest["Hips"].inverted()).to_3x3() @ Vector((0, -1, 0))
                sign = 1.0 if b.name.endswith("_l") else -1.0
                want_w = Matrix.Rotation(math.radians(sign * ARM_SPREAD_DEG), 4, fwd) @ want_w
            want_arm = tgt_mw_inv @ want_w
            if b.name == "pelvis":
                pos_w = (src_mw @ spb.matrix).translation * scale
                want_arm.translation = tgt_mw_inv @ pos_w
            else:
                want_arm.translation = (parent_arm @ rest_rel).translation
            basis = (parent_arm @ rest_rel).inverted() @ want_arm
        else:
            basis = Matrix.Identity(4)
            want_arm = parent_arm @ rest_rel
        arm_space[b.name] = want_arm
        loc, q, _ = basis.decompose()
        pb.rotation_quaternion = q
        pb.keyframe_insert("rotation_quaternion", frame=f)
        if b.name == "pelvis":
            pb.location = loc
            pb.keyframe_insert("location", frame=f)

bpy.data.objects.remove(source, do_unlink=True)
bpy.data.actions.remove(action)
scene.frame_start, scene.frame_end = f_start, f_end
scene.frame_set(f_start)

blend = out_dir / f"{clip_name}.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
bpy.ops.export_scene.gltf(filepath=str((out_dir / f"{clip_name}.glb").resolve()), export_format="GLB",
                          export_animations=True, export_animation_mode="ACTIONS", export_apply=True)
bpy.ops.export_scene.fbx(filepath=str((out_dir / f"{clip_name}.fbx").resolve()), use_selection=False,
                         apply_scale_options="FBX_SCALE_UNITS", add_leaf_bones=False, bake_anim=True, mesh_smooth_type="FACE",
                         bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                         path_mode="COPY", embed_textures=True)
info = {"frames": f_end - f_start + 1, "fps": scene.render.fps, "scale": round(scale, 4),
        "mapped": sum(1 for v in MAP.values() if v in target.data.bones)}
(out_dir / f"{clip_name}.json").write_text(json.dumps(info), encoding="utf-8")
print("RETARGET_OK", json.dumps(info))
