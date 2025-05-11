import os
import time
from ArucoDetector import *

# random calibration data
imsize = (1280, 720)
K = cv2.getDefaultNewCameraMatrix(
    np.diag([1280, 1280, 1]), imsize, True)
arDetector = ArUcoDetector(imsize, K)

# get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# AR scene
cv2.ovis.addResourceLocation(
    current_dir + "/r2d2")
win = cv2.ovis.createWindow("arucoAR", imsize, flags=0)
win.setCameraIntrinsics(K, imsize)
win.createEntity("figure", "Rtwo_low.mesh", (0, 0, 1), (1.57, 0, 0))
win.createLightEntity("sun", (0, 0, 2000))

# video capture
# video_path = 0 # for webcam
video_path = "dataset/laptop2_video.mp4"
cap = cv2.VideoCapture(video_path)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, imsize[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, imsize[1])

while cv2.ovis.waitKey(1) != "q":
    ret, frame = cap.read()
    tvecs, rvecs = arDetector.detectFullTarget(frame)
    if tvecs is not None:
        win.setCameraPose(tvecs * 5,
                          rvecs, invert=True)

    #  check input action
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

    win.setBackground(frame)

cap.release()
