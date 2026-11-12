import unreal

src = r"D:\ServOMorph\creation_3d\bench\ue_import\walk01.fbx"
opts = unreal.FbxImportUI()
opts.import_mesh = True
opts.import_as_skeletal = True
opts.import_animations = True
opts.import_materials = True
opts.import_textures = True
opts.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH

task = unreal.AssetImportTask()
task.filename = src
task.destination_path = "/Game/walk01"
task.automated = True
task.save = True
task.replace_existing = True
task.options = opts
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

reg = unreal.AssetRegistryHelpers.get_asset_registry()
assets = reg.get_assets_by_path("/Game/walk01", recursive=True)
summary = {}
for a in assets:
    cls = str(a.asset_class_path.asset_name)
    summary.setdefault(cls, []).append(str(a.asset_name))
for a in assets:
    if str(a.asset_class_path.asset_name) == "AnimSequence":
        seq = unreal.load_asset(str(a.package_name))
        summary["anim_length_s"] = round(seq.get_editor_property("sequence_length"), 2) if hasattr(seq, "sequence_length") else unreal.AnimationLibrary.get_sequence_length(seq)
    if str(a.asset_class_path.asset_name) == "Skeleton":
        sk = unreal.load_asset(str(a.package_name))
        summary["bones"] = len(unreal.AnimationLibrary.get_bones_in_skeleton(sk)) if hasattr(unreal.AnimationLibrary, "get_bones_in_skeleton") else "n/a"
unreal.log("UE_IMPORT " + str(summary))
