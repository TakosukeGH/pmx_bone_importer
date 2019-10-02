import bpy
import ctypes
import mathutils
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from . import structs

class ImportPMXBones(bpy.types.Operator, ImportHelper):
    bl_idname = "pbi.importer"
    bl_label = "Import PMX Bones"
    bl_options = {'UNDO'}

    filename_ext = ".pmx"
    filter_glob: StringProperty(default="*.pmx", options={'HIDDEN'})

    def __init__(self):
        pass

    def execute(self, context):
        pmx = structs.pmx_to_struct(self.filepath)
        self.pmx_to_armature(pmx)
        print("end")
        return {"FINISHED"}

    def pmx_to_armature(self, pmx):
        if bpy.context.object != None:
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=(0,0,0))
        amt = bpy.context.object
        amt.name = pmx.model_name

        for pmx_bone in pmx.bones:
            if pmx_bone.select_bone_index and pmx_bone.target_bone_index.index < 0: # IKの先ボーンがこれに該当
                continue

            bone = amt.data.edit_bones.new(pmx_bone.name)
            bone.head = pmx_bone.location.to_blender_vec()

            if pmx_bone.select_bone_index: # 接続先(PMD子ボーン指定)表示方法:ボーンで指定
                target_bone = pmx.bones[pmx_bone.target_bone_index.index]
                bone.tail = target_bone.location.to_blender_vec()
            else: # 接続先(PMD子ボーン指定)表示方法:座標オフセットで指定
                bone.tail = bone.head + pmx_bone.bone_coordinate_offset.to_blender_vec()

        bpy.ops.object.mode_set(mode='OBJECT')

def menu_func_import(self, context):
    self.layout.operator(ImportPMXBones.bl_idname, text="PMX Bones (.pmx)")

def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)






