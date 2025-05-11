import numpy as np
import cv2
import bpy
import os
import mathutils
import math


def capture_scene():
    # tmp directory
    home_dir = os.path.expanduser('~')
    filepath = os.path.join(home_dir, 'tmp/blender_scene.png')

    # set render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = filepath

    # render camera view
    bpy.ops.render.render(write_still=True)

    # load cv2 image
    img = cv2.imread(filepath)
    return img


def get_calibration_matrix_K_from_blender(camd):
    # Refernce: https://blender.stackexchange.com/questions/15102/what-is-blenders-camera-projection-matrix-model
    # extract the blender camera matrix

    f_in_mm = camd.lens
    scene = bpy.context.scene
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    sensor_width_in_mm = camd.sensor_width
    sensor_height_in_mm = camd.sensor_height
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
    if (camd.sensor_fit == 'VERTICAL'):
        # the sensor height is fixed (sensor fit is horizontal),
        # the sensor width is effectively changed with the pixel aspect ratio
        s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio
        s_v = resolution_y_in_px * scale / sensor_height_in_mm
    else:  # 'HORIZONTAL' and 'AUTO'
        # the sensor width is fixed (sensor fit is horizontal),
        # the sensor height is effectively changed with the pixel aspect ratio
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        s_u = resolution_x_in_px * scale / sensor_width_in_mm
        s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm

    # Parameters of intrinsic calibration matrix K
    alpha_u = f_in_mm * s_u
    alpha_v = f_in_mm * s_v
    u_0 = resolution_x_in_px*scale / 2
    v_0 = resolution_y_in_px*scale / 2
    skew = 0  # only use rectangular pixels

    K = mathutils.Matrix(
        ((alpha_u, skew,    u_0),
         (0,  alpha_v, v_0),
         (0,    0,      1)))
    return K


class ArUcoDetector(object):
    def __init__(self, imsize, K, dictionary_id=cv2.aruco.DICT_4X4_250):
        # charuco board
        self.dictionary_id = dictionary_id
        self.dictionary = cv2.aruco.getPredefinedDictionary(dictionary_id)
        self.params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(
            self.dictionary, self.params)
        imsize = imsize
        self.K = K

        # constant for coordinates mapping
        self.R_cv2blender = np.array([[1, 0, 0],
                                      [0, -1, 0],
                                      [0, 0, -1]])
        self.R_rotx90 = np.array([[1, 0, 0],
                                  [0, 0, -1],
                                  [0, 1, 0]])

    def cameraIntrinsics(self):
        return self.K

    def detectFullTarget(self, frame):
        """Detect the full designed marker on the scene

        Args:
            frame (_type_): _description_
        Returns:
            tvecs: translation vector (in mm)
            rvecs: rotation vector
        """
        corners, ids, _ = self.detector.detectMarkers(frame)
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            if len(ids) == 4:
                rvecs, tvecs = cv2.aruco.estimatePoseSingleMarkers(
                    corners, 6, self.K, None)[:2]
                # take the average of the tvecs and rvecs
                tvecs = np.mean(tvecs, axis=0)
                rvecs = rvecs[0]
                return tvecs.ravel(), rvecs.ravel()
        # unable to detect the designed marker
        return None, None

    def detectMeanTarget(self, frame):
        """Support only detected subset of all AR codes
        and use the mean central pose for estimation.
        Output rotational matrix and translation vector mapped to Blender frame definition.

        Args:
            frame (_type_): _description_
        """
        corners, ids, _ = arDetector.detector.detectMarkers(frame)

        # sort the corners by id
        id_argsort = np.argsort(ids.ravel())
        id_sorted = ids.ravel()[id_argsort]
        corners_sorted = [corners[i] for i in id_argsort]

        params = cv2.aruco.EstimateParameters()
        params.pattern = cv2.aruco.ARUCO_CCW_CENTER

        rvecs, tvecs = cv2.aruco.estimatePoseSingleMarkers(
            corners_sorted, 6, self.K, None, None, None, None, params)[:2]
        rvecs = rvecs.reshape(-1, 3)
        tvecs = tvecs.reshape(-1, 3)

        # convert the rotation vector to rotation matrix
        # for simplicity, use the mean rotation
        R_cv = np.array(cv2.Rodrigues(np.mean(rvecs, axis=0))[0])
        R_b = self.R_cv2blender @ R_cv @ self.R_rotx90

        # compute the mean center of the tvecs
        t_cv = self.shiftedCenter(id_sorted, tvecs, rvecs)
        t_b = self.R_cv2blender @ t_cv
        t_b *= 0.04  # magic number for unit conversion
        return R_b, t_b

    @staticmethod
    def shiftedCenter(ids, tvecs, rvecs, markerLength=6):
        """
        Calculate the mean center of the full pattern of markers
        for id = 0, local shift -y axis by markerLength
        for id = 1, local shift +x axis by markerLength
        for id = 2, local shift +y axis by markerLength
        for id = 3, local shift -x axis by markerLength
        Args:
            ids (_type_): [n] ids of the markers
            tvecs (_type_): [n x 3] translation vectors
            rvecs (_type_): [n x 3] rotation vectors
            markerLength (_type_): length of the marker
        """
        tvecs_shifted = tvecs.copy()
        for i in range(len(ids)):
            id = ids[i]
            R = cv2.Rodrigues(rvecs[i])[0]
            local_shift = np.zeros(3)
            if id == 0:
                local_shift = np.array([0, -markerLength, 0])
            elif id == 1:
                local_shift = np.array([markerLength, 0, 0])
            elif id == 2:
                local_shift = np.array([0, markerLength, 0])
            elif id == 3:
                local_shift = np.array([-markerLength, 0, 0])
            tvecs_shifted[i] += R @ local_shift
        return np.mean(tvecs_shifted, axis=0)


def set_object_transform(ref_frame,
                         trans,
                         rot=mathutils.Matrix(),
                         scale=mathutils.Vector((0.005, 0.005, 0.005)),
                         object_name='r2d2'):
    mat = mathutils.Matrix.LocRotScale(trans, rot, scale)
    bpy.data.objects[object_name].matrix_world = ref_frame @ mat


def set_camera_view(trans, rot):
    # euler to rotation matrix
    eul = mathutils.Euler(
        (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2])), 'XYZ')
    mat = eul.to_matrix().to_4x4()
    mat.translation = trans
    bpy.context.scene.camera.matrix_world = mat


if __name__ == "__main__":
    # default view point
    mat_cam = camera = bpy.context.scene.camera.matrix_world
    set_camera_view(mathutils.Vector((-1.8, 3, 6.5)), (55, 0, 200))

    # camera intrinsic
    imsize = (1920, 1080)
    K = np.array(get_calibration_matrix_K_from_blender(
        bpy.data.objects['Camera'].data))
    print("Camera intrinsic matrix:")
    print(K)

    # init detector
    arDetector = ArUcoDetector(imsize, K)
    frame = capture_scene()  # capture the blender scene
    R_b, t_b = arDetector.detectMeanTarget(frame)

    print("Rotation matrix (blender frame):")
    print(R_b)
    print("Translation vector (blender frame):")
    print(t_b)

    # set the object transform
    set_object_transform(mat_cam, mathutils.Vector(t_b), mathutils.Matrix(R_b))
