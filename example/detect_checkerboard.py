import cv2
import numpy as np

imsize = (800, 600)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, imsize[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, imsize[1])


while True:
    ret, frame = cap.read()

    # Load the image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Set the dimensions of the checkerboard (number of inner corners per row and column)
    pattern_size = (5, 7)  # Example: 7x7 checkerboard

    # Find the checkerboard corners
    found, corners = cv2.findChessboardCorners(gray, pattern_size, None)

    # If the checkerboard is found, draw the corners
    if found:
        cv2.drawChessboardCorners(frame, pattern_size, corners, found)

    cv2.imshow('Checkerboard', frame)

    # input action
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
