import numpy as np
import cv2 as cv
import os
# charuco board
arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_250)
arucoParams = cv.aruco.DetectorParameters()
arucoDetector = cv.aruco.ArucoDetector(arucoDict, arucoParams)

# random calibration data. your mileage may vary.
imsize = (1280, 720)
K = cv.getDefaultNewCameraMatrix(np.diag([1280, 1280, 1]), imsize, True)

# get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# AR scene
cv.ovis.addResourceLocation(
    current_dir + "/../r2d2")

win = cv.ovis.createWindow("arucoAR", imsize, flags=0)
win.setCameraIntrinsics(K, imsize)
win.createEntity("figure", "Rtwo_low.mesh", (0, 0, 5), (1.57, 0, 0))
win.createLightEntity("sun", (0, 0, 2000))

# video capture
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, imsize[0])
cap.set(cv.CAP_PROP_FRAME_HEIGHT, imsize[1])

while cv.ovis.waitKey(1) != "q":
    ret, frame = cap.read()
    corners, ids, rejected = arucoDetector.detectMarkers(frame)

    #  if all markers detected
    if ids is not None and len(ids) == 4:
        # draw detected markers
        cv.aruco.drawDetectedMarkers(frame, corners, ids)

        rvecs, tvecs = cv.aruco.estimatePoseSingleMarkers(
            corners, 5, K, None)[:2]

        # take the average of the tvecs and rvecs
        tvecs = np.mean(tvecs, axis=0) * 5.0
        rvecs = rvecs[0]

        # enlarge the tvecs
        win.setCameraPose(tvecs.ravel(),
                          rvecs.ravel(), invert=True)

    #  check input action
    key = cv.waitKey(1)
    if key == ord("q"):
        break

    win.setBackground(frame)

cap.release()
