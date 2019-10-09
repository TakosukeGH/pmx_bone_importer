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
    importlib.reload(const)
else:
    from . import properties, importer, structs, const

import bpy
import logging

logger = logging.getLogger(const.ADDON_NAME)

if not logger.handlers:
    hdlr = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)-7s %(asctime)s %(message)s (%(funcName)s)", datefmt="%H:%M:%S")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG) # DEBUG, INFO, WARNING, ERROR, CRITICAL

logger.debug("init logger") # debug, info, warning, error, critical

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
