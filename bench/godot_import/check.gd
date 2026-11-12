extends SceneTree
func _init():
	var scene = load("res://walk01.glb")
	if scene == null:
		print("GODOT_FAIL load")
		quit(1)
		return
	var root = scene.instantiate()
	var players = root.find_children("*", "AnimationPlayer", true, false)
	var skels = root.find_children("*", "Skeleton3D", true, false)
	var meshes = root.find_children("*", "MeshInstance3D", true, false)
	var anims = []
	for p in players:
		for a in p.get_animation_list():
			anims.append("%s:%.2fs" % [a, p.get_animation(a).length])
	print("GODOT_OK version=%s skeletons=%d bones=%d meshes=%d anims=%s" % [Engine.get_version_info().string, skels.size(), skels[0].get_bone_count() if skels.size() > 0 else 0, meshes.size(), anims])
	quit(0)
