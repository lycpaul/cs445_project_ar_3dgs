import numpy as np
import cv2


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


if __name__ == "__main__":
    # camera intrinsic
    imsize = (1920, 1080)
    K = np.array([[1867, 0, 960], [0, 1575, 540], [0, 0, 1]])

    # init detector
    arDetector = ArUcoDetector(imsize, K)
    frame = cv2.imread("images/detected_marker_3.png")
    R_b, t_b = arDetector.detectMeanTarget(frame)

    print("Rotation matrix (blender frame):")
    print(R_b)
    print("Translation vector (blender frame):")
    print(t_b)
