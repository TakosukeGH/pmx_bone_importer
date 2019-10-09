import ctypes
import mathutils

BONE_FLAG_SPEC = 1
BONE_FLAG_ROTATE = 2
BONE_FLAG_LOCATION = 4
BONE_FLAG_VIEW = 8
BONE_FLAG_OPERATION = 16
BONE_FLAG_IK = 32
BONE_FLAG_LOCAL = 128
BONE_FLAG_ADD_RATATE = 1
BONE_FLAG_ADD_LOCATION = 2
BONE_FLAG_AXIS = 4
BONE_FLAG_LOCAL_AXIS = 8
BONE_FLAG_DEFORM_PHYSICS = 16
BONE_FLAG_DEFORM_PARENT = 32

P2B_MAT = mathutils.Matrix([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 1.0]])

ZERO_VEC = mathutils.Vector((0.0, 0.0, 0.0))
UNIT_VEC = mathutils.Vector((0.0, 0.0, 0.1))

def pmx_to_struct(filepath):
    pmx = PMX(filepath)
    pmx.read_pmx()
    return pmx

class PMX:
    def __init__(self, filepath):
        self.helper = BinaryHelper()

        self.filepath = filepath

        # header
        self.header = Header()
        self.added_uv = 0

        self.vart_index_size = 0
        self.texture_index_size = 0
        self.bone_index_size = 0

        self.obj_size = Int32()

        # info
        self.model_name = ""

        # bone
        self.bones = []

    def read_pmx(self):
        with open(self.filepath, "rb") as f:
            self.read_header(f)
            self.read_info(f)
            self.read_vart(f)
            self.read_face(f)
            self.read_texture(f)
            self.read_material(f)
            self.read_bones(f)

    def read_header(self, f):
        print("tell: " + str(f.tell()))
        f.readinto(self.header)

        self.added_uv = self.header.bytearray[1]
        self.vart_index_size = self.header.bytearray[2]
        self.texture_index_size = self.header.bytearray[3]
        self.bone_index_size = self.header.bytearray[5]

    def read_info(self, f):
        print("---- model info ----")
        print("tell: " + str(f.tell()))

        self.model_name = self.helper.read_text(f)
        print(self.model_name)

        self.helper.seek_text(f,3) # name eng, comment, comment eng

    def read_vart(self, f):
        print("---- vert ----")
        print("tell: " + str(f.tell()))

        f.readinto(self.obj_size)
        print("vert size: " + str(self.obj_size.value))

        weight_mode = Byte()
        for _ in range(self.obj_size.value):
            f.seek(12 + 12 + 8, 1)

            if self.added_uv > 0:
                f.seek(self.added_uv * 16, 1)

            f.readinto(weight_mode)
            if weight_mode.value == 0:
                f.seek(self.bone_index_size, 1)
            elif weight_mode.value == 1:
                f.seek(self.bone_index_size * 2 + 4, 1)
            elif weight_mode.value == 2:
                f.seek(self.bone_index_size * 4 + 16, 1)
            elif weight_mode.value == 3:
                f.seek(self.bone_index_size * 2 + 4 + 36, 1)

            f.seek(4, 1) # エッジ倍率

    def read_face(self, f):
        print("---- fase ----")
        print("tell: " + str(f.tell()))
        f.readinto(self.obj_size)
        print("fase size: " + str(self.obj_size.value/3))
        f.seek(self.vart_index_size * self.obj_size.value, 1)

    def read_texture(self, f):
        print("---- texture ----")
        print("tell: " + str(f.tell()))
        f.readinto(self.obj_size)
        print("texture size: " + str(self.obj_size.value))
        self.helper.seek_text(f, self.obj_size.value)

    def read_material(self, f):
        print("---- material ----") # 14760
        print("tell: " + str(f.tell()))
        f.readinto(self.obj_size)
        print("material size: " + str(self.obj_size.value))

        share_flag = Byte()
        for _ in range(self.obj_size.value):
            self.helper.seek_text(f, 2) # 材質名, 材質名英
            f.seek(16 + 12 + 4 + 12 + 1 + 16 + 4, 1)
            f.seek(self.texture_index_size * 2, 1)
            f.seek(1, 1)
            f.readinto(share_flag)
            if share_flag.value == 0:
                f.seek(self.texture_index_size, 1)
            if share_flag.value == 1:
                f.seek(1, 1)
            self.helper.seek_text(f) # メモ
            f.seek(4, 1)

    def read_bones(self, f):
        print("---- bone ----") # 14760
        print("tell: " + str(f.tell()))
        f.readinto(self.obj_size)
        print("number of bones: " + str(self.obj_size.value))

        for _ in range(self.obj_size.value):
            bone = Bone(self.bone_index_size)
            bone.name = self.helper.read_text(f)
            print("bone name: " + bone.name)
            self.helper.seek_text(f) # bone name engrish

            f.readinto(bone.location)
            f.readinto(bone.parent_bone_index)
            f.readinto(bone.deform_hierarchy)

            bone.read_bone_flag(f)

            if bone.select_bone_index: # 接続先(PMD子ボーン指定)表示方法:ボーンで指定
                f.readinto(bone.target_bone_index)
                if bone.target_bone_index.index < 0:
                    bone.is_empty_bone = True
            else: # 接続先(PMD子ボーン指定)表示方法:座標オフセットで指定
                f.readinto(bone.bone_coordinate_offset)
                if bone.bone_coordinate_offset.to_blender_vec() == ZERO_VEC:
                    bone.is_empty_bone = True

            if bone.rotateable: # 回転可能
                pass

            if bone.movable: # 移動可能
                pass

            if bone.view: # 表示
                pass

            if bone.operable: # 操作可
                pass

            if bone.ik: # IK
                f.readinto(bone.ik_target)
                f.readinto(bone.loop)
                f.readinto(bone.unit_angle)
                f.readinto(bone.link_count)
                for _ in range(bone.link_count.value):
                    ik = bone.new_ik()
                    f.readinto(ik.link_bone_index)
                    f.readinto(ik.angle_limit)
                    if ik.angle_limit.value == 1:
                        f.readinto(ik.lower_limit)
                        f.readinto(ik.upper_limit)

            if bone.add_local: # ローカル付与:親のローカル変形量
                pass

            if bone.add_rotate or bone.add_move: # 回転付与・移動付与
                f.readinto(bone.add_target_bone_index)
                f.readinto(bone.offset_rate)

            if bone.axis: # 軸固定
                f.readinto(bone.fixed_axes)

            if bone.local_axis: # ローカル軸
                f.readinto(bone.local_x_axes)
                f.readinto(bone.local_z_axes)

            if bone.deform_physics: # 物理後変形
                pass

            if bone.deform_parent: # 外部親変形
                f.readinto(bone.parent_key)

            self.bones.append(bone)

class Header(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('pmx', ctypes.c_char * 4),
        ('version', ctypes.c_float),
        ('bytesize', ctypes.c_byte),
        ('bytearray', ctypes.c_byte * 8),
    ]

class Bone:
    def __init__(self, bone_index_size):
        self.bone_index_size = bone_index_size

        if self.bone_index_size == 1:
            self.c_type = ctypes.c_int8
        elif self.bone_index_size == 2:
            self.c_type = ctypes.c_int16
        else:
            self.c_type = ctypes.c_int32

        self.name = ""
        self.location = Vector()
        self.parent_bone_index = self.new_bone_index()
        self.deform_hierarchy = Int32()

        # flag
        self.select_bone_index = None
        self.rotateable = None
        self.movable = None
        self.view = None
        self.operable = None
        self.ik = None
        self.add_local = None
        self.add_rotate = None
        self.add_move = None
        self.axis = None
        self.local_axis = None
        self.deform_physics = None
        self.deform_parent = None

        # flag value
        self.target_bone_index = self.new_bone_index()
        self.bone_coordinate_offset = Vector()
        self.add_target_bone_index = self.new_bone_index()
        self.offset_rate = Float()
        self.fixed_axes = Vector()
        self.local_x_axes = Vector()
        self.local_z_axes = Vector()
        self.parent_key = Int32()

        # ik
        self.iks = []
        self.ik_target = self.new_bone_index()
        self.loop = Int32()
        self.unit_angle = Float()
        self.link_count = Int32()

        # blender
        self.blender_bone_name = ""
        self.is_empty_bone = False

    def read_bone_flag(self, f):
            bone_flag = BoneFlag()
            f.readinto(bone_flag)

            self.select_bone_index = BONE_FLAG_SPEC & bone_flag.flag[0]
            self.rotateable = BONE_FLAG_ROTATE & bone_flag.flag[0]
            self.movable = BONE_FLAG_LOCATION & bone_flag.flag[0]
            self.view = BONE_FLAG_VIEW & bone_flag.flag[0]
            self.operable = BONE_FLAG_OPERATION & bone_flag.flag[0]
            self.ik = BONE_FLAG_IK & bone_flag.flag[0]
            self.add_local = BONE_FLAG_LOCAL & bone_flag.flag[0]
            self.add_rotate = BONE_FLAG_ADD_RATATE & bone_flag.flag[1]
            self.add_move = BONE_FLAG_ADD_LOCATION & bone_flag.flag[1]
            self.axis = BONE_FLAG_AXIS & bone_flag.flag[1]
            self.local_axis = BONE_FLAG_LOCAL_AXIS & bone_flag.flag[1]
            self.deform_physics =  BONE_FLAG_DEFORM_PHYSICS & bone_flag.flag[1]
            self.deform_parent = BONE_FLAG_DEFORM_PARENT & bone_flag.flag[1]

    def new_bone_index(self):
        class BoneIndex(ctypes.Structure):
            _pack_ = 1
            _fields_ = [
                ('index', self.c_type),
            ]
        return BoneIndex()

    def new_ik(self):
        ik = IK()
        ik.link_bone_index = self.new_bone_index()
        self.iks.append(ik)
        return ik

class IK:
    def __init__(self):
        self.link_bone_index = None
        self.angle_limit = Byte()
        self.upper_limit = Vector()
        self.lower_limit = Vector()

class BinaryHelper:
    def __init__(self):
        self.int_buf = Int32()

    def read_text(self, f):
        f.readinto(self.int_buf)
        if self.int_buf.value > 0:
            name = self.text_buf_factory(self.int_buf.value)()
            f.readinto(name)
            return ctypes.string_at(name.text, self.int_buf.value).decode('utf-16-le')
        else:
            return ""

    def seek_text(self, f, loop=1):
        for _ in range(loop):
            f.readinto(self.int_buf)
            f.seek(self.int_buf.value, 1)

    def text_buf_factory(self, buf_size):
        class TextBuf(ctypes.Structure):
            _pack_ = 1
            _fields_ = [
                ('text', ctypes.c_byte * buf_size),
            ]
        return TextBuf

class Int32(ctypes.Structure):
    _fields_ = [
        ('value', ctypes.c_int32),
    ]

class Byte(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('value', ctypes.c_byte),
    ]

class Vector(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float),
    ]

    def to_blender_vec(self):
        return mathutils.Vector((self.x, self.y, self.z)) @ P2B_MAT

class Float(ctypes.Structure):
    _fields_ = [
        ('value', ctypes.c_float),
    ]

class BoneFlag(ctypes.Structure):
    _fields_ = [
        ('flag', ctypes.c_byte * 2),
    ]








