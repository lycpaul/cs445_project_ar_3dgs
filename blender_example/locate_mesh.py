import bpy
import math
import mathutils
from mathutils import Vector


def set_object_trans(ref_frame, trans):
    obj = bpy.data.objects['r2d2']
    offset = mathutils.Matrix()
    # offset.translation = translation
    world_position = ref_frame @ trans
    # move object to new position
    obj.location = world_position


def set_object_mat(ref_frame, trans, rot):
    # euler to rotation matrix
    eul = mathutils.Euler(rot, 'XYZ')
    # mat = eul.to_matrix().to_4x4()
    # mat.translation = trans
    scale = Vector((0.005, 0.005, 0.005))
    
    mat = mathutils.Matrix.LocRotScale(trans, eul, scale)

    obj = bpy.data.objects['r2d2']
    obj.matrix_world = ref_frame @ mat


def set_camera_view(trans, rot):
    # euler to rotation matrix
    eul = mathutils.Euler(
        (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2])), 'XYZ')
    mat = eul.to_matrix().to_4x4()
    mat.translation = trans
    bpy.context.scene.camera.matrix_world = mat


# default view point
mat_cam = camera = bpy.context.scene.camera.matrix_world
set_camera_view(Vector((-1, 3, 8)), (40, 15, 175))

# OpenCV result
# set_object_view(mat_cam, Vector((0.312, -0.08372, -5.17)))

# Manual result
# set_object_trans(mat_cam, Vector((1.2989, -0.2734, -4.2197)))
set_object_mat(mat_cam, Vector((1.2989, -0.2734, -4.2197)), (1.0024, -0.4284, -0.1314))

# debug
print("mat_cam")
print(mat_cam)

mat_obj = bpy.data.objects['r2d2'].matrix_world
print("mat_obj")
print(mat_obj)

print("obj_T_cam")
obj_T_cam = mat_cam.inverted() @ mat_obj
print(obj_T_cam)
print(obj_T_cam.to_euler())
