import sys
from pathlib import Path

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = Path(argv[0])
max_size = int(argv[1]) if len(argv) > 1 else 1024

for img in bpy.data.images:
    if img.size[0] > max_size or img.size[1] > max_size:
        ratio = max_size / max(img.size)
        img.scale(max(1, int(img.size[0] * ratio)), max(1, int(img.size[1] * ratio)))

bpy.ops.export_scene.gltf(filepath=str(out.resolve()), export_format="GLB", export_animations=True,
                          export_animation_mode="ACTIONS", export_apply=True, export_image_format="AUTO",
                          export_jpeg_quality=85, export_draco_mesh_compression_enable=False)
print("WEB_OK", out, out.stat().st_size)
