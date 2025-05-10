import numpy as np
import cv2 as cv


class ArUcoDetector(object):
    def __init__(self, imsize, K, dictionary_id=cv.aruco.DICT_4X4_250):
        # charuco board
        self.dictionary_id = dictionary_id
        self.arucoDict = cv.aruco.getPredefinedDictionary(dictionary_id)
        self.arucoParams = cv.aruco.DetectorParameters()
        self.arucoDetector = cv.aruco.ArucoDetector(
            self.arucoDict, self.arucoParams)
        imsize = imsize
        self.K = K

    def cameraIntrinsics(self):
        return self.K

    def detectTarget(self, frame):
        """Detect the designed marker on the scene

        Args:
            frame (_type_): _description_
        """
        corners, ids, rejected = self.arucoDetector.detectMarkers(frame)

        #  if all markers detected
        if ids is not None and len(ids) == 4:
            # draw detected markers
            cv.aruco.drawDetectedMarkers(frame, corners, ids)

            rvecs, tvecs = cv.aruco.estimatePoseSingleMarkers(
                corners, 5, self.K, None)[:2]

            # take the average of the tvecs and rvecs
            tvecs = np.mean(tvecs, axis=0) * 5.0
            rvecs = rvecs[0]

            return tvecs.ravel(), rvecs.ravel()

        # unable to detect the designed marker
        return None, None
