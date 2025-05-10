import numpy as np
import cv2 as cv


class ArUcoDetector(object):
    def __init__(self, imsize, K, dictionary_id=cv.aruco.DICT_4X4_250):
        # charuco board
        self.dictionary_id = dictionary_id
        self.dictionary = cv.aruco.getPredefinedDictionary(dictionary_id)
        self.params = cv.aruco.DetectorParameters()
        self.detector = cv.aruco.ArucoDetector(
            self.dictionary, self.params)
        imsize = imsize
        self.K = K

    def cameraIntrinsics(self):
        return self.K

    def detectTarget(self, frame):
        """Detect the designed marker on the scene

        Args:
            frame (_type_): _description_
        """
        corners, ids, rejected = self.detector.detectMarkers(frame)
        if ids is not None:
            cv.aruco.drawDetectedMarkers(frame, corners, ids)

            if len(ids) == 4:
                # in mm
                rvecs, tvecs = cv.aruco.estimatePoseSingleMarkers(
                    corners, 6, self.K, None)[:2]

                # take the average of the tvecs and rvecs
                tvecs = np.mean(tvecs, axis=0)
                rvecs = rvecs[0]

                return tvecs.ravel(), rvecs.ravel()

        # unable to detect the designed marker
        return None, None
