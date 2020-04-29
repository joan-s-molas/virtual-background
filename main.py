import cv2
import numpy as np
import matplotlib
import requests

# configure camera for 720p @ 60 FPS
cap = cv2.VideoCapture('/dev/video0')

height, width = 720, 1280
replacement_bg_raw = cv2.imread("background.jpg")
replacement_bg = cv2.resize(replacement_bg_raw, (width, height))

cap.set(cv2.CAP_PROP_FRAME_WIDTH ,width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
cap.set(cv2.CAP_PROP_FPS, 60)


def get_mask(frame, bodypix_url='http://localhost:9000'):
    _, data = cv2.imencode(".jpg", frame)
    r = requests.post(
        url=bodypix_url,
        data=data.tobytes(),
        headers={'Content-Type': 'application/octet-stream'})
    # convert raw bytes to a numpy array
    # raw data is uint8[width * height] with value 0 or 1
    mask = np.frombuffer(r.content, dtype=np.uint8)
    mask = mask.reshape((frame.shape[0], frame.shape[1]))
    return mask

while True:
    success, frame = cap.read()
    mask = get_mask(frame)
    inv_mask = 1-mask
    for c in range(frame.shape[2]):
        frame[:,:,c] = frame[:,:,c]*mask + replacement_bg[:,:,c]*inv_mask
    cv2.imwrite("test.jpg", frame)        