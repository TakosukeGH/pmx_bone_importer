bl_info = {
    "name": "PMX bone importer",
    "description": "PMX bone importer.",
    "author": "Takosuke",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh",
    "support": "COMMUNITY",
    "category": "Add Mesh"
}

if "bpy" in locals():
    import importlib
    importlib.reload(properties)
    importlib.reload(importer)
    importlib.reload(structs)
else:
    from . import properties, importer, structs

import bpy

classes = (
    properties.PBISceneProperties,
    properties.VIEW3D_PT_pbi,
    importer.ImportPMXBones,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    properties.register()
    importer.register()

def unregister():
    importer.unregister()
    properties.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
