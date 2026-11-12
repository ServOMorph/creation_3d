import json
import sys
from pathlib import Path

import bpy
import addon_utils

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out_dir = Path(argv[0] if argv else "assets/mpfb_test")
skin_type = argv[1] if len(argv) > 1 else "ENHANCED_SSS"
out_dir.mkdir(parents=True, exist_ok=True)

addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.targetservice import TargetService

HUMAN = {
    "phenotype": {
        "gender": 1.0, "age": 0.5, "muscle": 0.6, "weight": 0.5,
        "proportions": 0.8, "height": 0.6, "cupsize": 0.5, "firmness": 0.5,
        "race": {"asian": 0.0, "caucasian": 1.0, "african": 0.0},
    },
    "rig": "game_engine",
    "skin_mhmat": "young_caucasian_male.mhmat",
    "skin_material_type": skin_type,
    "eyes": "high-poly.mhclo",
    "eyes_material_type": "MAKESKIN",
    "eyebrows": "eyebrow001.mhclo",
    "eyelashes": "eyelashes01.mhclo",
    "teeth": "teeth_base.mhclo",
    "tongue": "tongue01.mhclo",
    "hair": "short02.mhclo",
    "clothes": ["male_casualsuit03.mhclo", "shoes01.mhclo"],
    "clothes_material_type": "MAKESKIN",
    "proxy": "",
    "targets": [],
    "expressions": [],
    "skin_material_settings": {},
    "eyes_material_settings": {},
    "alternative_materials": {},
}

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

settings = HumanService.get_default_deserialization_settings()
basemesh = HumanService.deserialize_from_dict(HUMAN, settings)
armature = basemesh.parent

objects = [o for o in bpy.data.objects if o.type == "MESH"]
report = {
    "basemesh": basemesh.name,
    "height_m": round(basemesh.dimensions.z, 3),
    "armature": armature.name if armature else None,
    "bones": len(armature.data.bones) if armature else 0,
    "meshes": {o.name: len(o.data.polygons) for o in objects},
    "materials": sorted({m.name for o in objects for m in o.data.materials if m}),
}

bpy.ops.wm.save_as_mainfile(filepath=str((out_dir / "human.blend").resolve()))
(out_dir / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
print("MPFB_OK", json.dumps(report))
