import bpy
from bpy.props import PointerProperty, StringProperty, CollectionProperty, IntProperty, BoolProperty, IntVectorProperty, FloatVectorProperty, FloatProperty, EnumProperty, BoolVectorProperty
from . import importer
from bpy.app.translations import pgettext

class PBISceneProperties(bpy.types.PropertyGroup):
    test_prop: BoolProperty(name="test prop", description="test prop", default=False)


class VIEW3D_PT_pbi(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_pbi"
    bl_label = "PBI"
    bl_category = "PBI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_options = {'DEFAULT_OPEN'}

    def draw(self, context):
        pbi_scene_properties = context.scene.pbi_scene_properties

        row = self.layout.row()
        row.scale_y = 2.0
        row.operator(importer.ImportPMXBones.bl_idname, text=pgettext(importer.ImportPMXBones.bl_label), icon='IMPORT')

        layout = self.layout
        layout.prop(pbi_scene_properties, "test_prop")

translations = {
    "ja_JP": {
        ("*", "Base Settings"): "基本設定",
        ("*", "Slot operation"): "スロット操作",
    }
}

def register():
    bpy.types.Scene.pbi_scene_properties = PointerProperty(type=PBISceneProperties)
    bpy.app.translations.register(__name__, translations)

def unregister():
    bpy.app.translations.unregister(__name__)
    del bpy.types.Scene.pbi_scene_properties






