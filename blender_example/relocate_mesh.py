import bpy
import math
import mathutils
import numpy as np


def set_object_transform(ref_frame,
                         trans,
                         rot=mathutils.Matrix(),
                         scale=mathutils.Vector((0.005, 0.005, 0.005)),
                         object_name='r2d2'):
    mat = mathutils.Matrix.LocRotScale(trans, rot, scale)
    bpy.data.objects[object_name].matrix_world = ref_frame @ mat


def set_camera_view(trans: mathutils.Vector, rot: mathutils.Matrix):
    # euler to rotation matrix
    eul = mathutils.Euler(
        (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2])), 'XYZ')
    mat = eul.to_matrix().to_4x4()
    mat.translation = trans
    bpy.context.scene.camera.matrix_world = mat


def get_rot_matrix(R_cv: np.ndarray) -> mathutils.Matrix:
    R_cv = np.array([[0.76670474,  0.64062636,  0.04197281],
                     [0.43447562, -0.46962788, -0.76855747],
                     [-0.47264657,  0.60749282, -0.63840246]])
    R_cv2blender = np.array([[1, 0, 0],
                            [0, -1, 0],
                            [0, 0, -1]])
    R_rotx90 = np.array([[1, 0, 0],
                        [0, 0, -1],
                        [0, 1, 0]])
    return mathutils.Matrix(R_cv2blender @ R_cv @ R_rotx90)


if __name__ == "__main__":
    # default view point
    mat_cam = camera = bpy.context.scene.camera.matrix_world
    set_camera_view(mathutils.Vector((-1.8, 3, 6.5)), (55, 0, 200))

    # euler to rotation matrix
    t_b = mathutils.Vector((0.59428577, -0.43290842, -3.00550755))
    R_b = get_rot_matrix()
    set_object_transform(mat_cam, t_b, R_b)

    # debug print
    print("mat_cam")
    print(mat_cam)

    mat_obj = bpy.data.objects['r2d2'].matrix_world
    print("mat_obj")
    print(mat_obj)

    print("obj_T_cam")
    obj_T_cam = mat_cam.inverted() @ mat_obj
    print(obj_T_cam)
    print(obj_T_cam.to_euler().to_matrix())
