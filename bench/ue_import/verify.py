import unreal
anim = unreal.load_asset("/Game/walk01/walk01_Anim")
mesh = unreal.load_asset("/Game/walk01/walk01")
skel = unreal.load_asset("/Game/walk01/walk01_Skeleton")
length = unreal.AnimationLibrary.get_sequence_length(anim) if anim else None
frames = unreal.AnimationLibrary.get_num_frames(anim) if anim else None
bones = len(skel.get_editor_property("bone_tree")) if skel else None
mats = len(mesh.get_editor_property("materials")) if mesh else None
unreal.log("UE_VERIFY anim=%s length=%s frames=%s mesh=%s bones=%s materials=%s" % (anim is not None, length, frames, mesh is not None, bones, mats))
