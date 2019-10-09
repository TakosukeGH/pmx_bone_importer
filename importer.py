import bpy
import ctypes
import logging
import mathutils
from . import const
from . import logutils
from . import structs
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

logger = logging.getLogger(const.ADDON_NAME)

class ImportPMXBones(bpy.types.Operator, ImportHelper):
    bl_idname = "pbi.importer"
    bl_label = "Import PMX Bones"
    bl_options = {'UNDO'}

    filename_ext = ".pmx"
    filter_glob: StringProperty(default="*.pmx", options={'HIDDEN'})

    def __init__(self):
        self.empty = None

    def execute(self, context):
        with logutils.LoggingToTextContext(logger):
            pmx = structs.pmx_to_struct(self.filepath)
            self.init_scene(context, pmx)
            self.pmx_to_armature(context, pmx)
            self.setting_pose_bones(context, pmx)
            logger.info("end")
        return {"FINISHED"}

    def init_scene(self, context, pmx):
        collection = context.scene.collection
        pmx_collection = bpy.data.collections.new("pmx_bones")
        collection.children.link(pmx_collection)
        context.view_layer.active_layer_collection = context.view_layer.layer_collection.children[pmx_collection.name]

        add_empty = False
        for pmx_bone in pmx.bones:
            if pmx_bone.is_empty_bone:
                bpy.ops.object.empty_add(type='SPHERE', radius=1.0, location=(0.0, 0.0, 0.0))
                self.empty = context.object
                break

    def pmx_to_armature(self, context, pmx):
        logger.info("start")

        if context.object != None:
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=(0,0,0))
        amt = context.object
        amt.name = pmx.model_name
        edit_bones = amt.data.edit_bones

        for pmx_bone in pmx.bones:
            bone = edit_bones.new(pmx_bone.name)
            pmx_bone.blender_bone_name = bone.name

            bone.head = pmx_bone.location.to_blender_vec()

            if pmx_bone.is_empty_bone:
                bone.tail = bone.head + structs.UNIT_VEC
            elif pmx_bone.select_bone_index: # 接続先(PMD子ボーン指定)表示方法:ボーンで指定
                target_bone = pmx.bones[pmx_bone.target_bone_index.index]
                bone.tail = target_bone.location.to_blender_vec()
            else: # 接続先(PMD子ボーン指定)表示方法:座標オフセットで指定
                bone.tail = bone.head + pmx_bone.bone_coordinate_offset.to_blender_vec()

        for pmx_bone in pmx.bones:
            bone = edit_bones[pmx_bone.blender_bone_name]
            bone.parent = edit_bones[pmx.bones[pmx_bone.parent_bone_index.index].name]

        bpy.ops.object.mode_set(mode='OBJECT')

        logger.info("end")

    def setting_pose_bones(self, context, pmx):
        logger.info("start")

        bpy.ops.object.mode_set(mode='POSE')
        amt = context.object
        bones = amt.pose.bones

        for pmx_bone in pmx.bones:
            bone = bones[pmx_bone.blender_bone_name]

            if pmx_bone.is_empty_bone:
                bone.custom_shape = self.empty

            if not pmx_bone.rotateable:
                bone.lock_rotation = (True, True, True)
                bone.lock_rotation_w = True

            if not pmx_bone.movable:
                bone.lock_location = (True, True, True)

            if not pmx_bone.view:
                bone.bone.hide = True
                bone.bone.layers = self.bone_layers(31)

            if pmx_bone.ik:
                pmx_ik_bone = pmx_bone.iks[0]
                ik_bone = bones[pmx.bones[pmx_ik_bone.link_bone_index.index].name]

                if pmx_ik_bone.angle_limit.value:
                    for axis in ["x", "y", "z"]:
                        setattr(ik_bone, "use_ik_limit_" + axis, True)
                        upper_limit = getattr(pmx_ik_bone.upper_limit, axis)
                        lower_limit = getattr(pmx_ik_bone.lower_limit, axis)
                        setattr(ik_bone, "ik_min_" + axis, -upper_limit if abs(upper_limit) > 0.0 else upper_limit)
                        setattr(ik_bone, "ik_max_" + axis, -lower_limit if abs(lower_limit) > 0.0 else lower_limit)

                const = ik_bone.constraints.new('IK')
                const.target = amt
                const.subtarget = bone.name
                const.chain_count = len(pmx_bone.iks)

        bpy.ops.object.mode_set(mode='OBJECT')

        logger.info("end")

    def bone_layers(self, layer):
        layers = [False] * 32
        layers[layer % 32] = True
        return layers

def menu_func_import(self, context):
    self.layout.operator(ImportPMXBones.bl_idname, text="PMX Bones (.pmx)")

def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)






