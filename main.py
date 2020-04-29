import cv2
import numpy as np
import matplotlib
import requests
import pyfakewebcam


# configure camera for 720p @ 60 FPS
cap = cv2.VideoCapture('/dev/video0')

height, width = 720, 1280

fake = pyfakewebcam.FakeWebcam('/dev/video20', width, height)
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
    mask = cv2.dilate(mask, np.ones((10,10), np.uint8) , iterations=1)
    mask = cv2.erode(mask, np.ones((10,10), np.uint8) , iterations=1) 
    mask = cv2.blur(mask.astype(float), (25,25))   
    
    return mask

# shift_img from: https://stackoverflow.com/a/53140617
def shift_img(img, dx, dy):
    img = np.roll(img, dy, axis=0)
    img = np.roll(img, dx, axis=1)
    if dy>0:
        img[:dy, :] = 0
    elif dy<0:
        img[dy:, :] = 0
    if dx>0:
        img[:, :dx] = 0
    elif dx<0:
        img[:, dx:] = 0
    return img

while True:
    success, frame = cap.read()
    mask = get_mask(frame)
    inv_mask = 1-mask
    # Uncomment this for dank holographic effects
    #holo = cv2.applyColorMap(frame, cv2.COLORMAP_WINTER)
    #bandLength, bandGap = 2, 3
    #for y in range(holo.shape[0]):
    #    if y % (bandLength+bandGap) < bandLength:
    #        holo[y,:,:] = holo[y,:,:] * np.random.uniform(0.1, 0.3)
#
    ## the first one is roughly: holo * 0.2 + shifted_holo * 0.8 + 0
    #holo2 = cv2.addWeighted(holo, 0.2, shift_img(holo.copy(), 5, 5), 0.8, 0)
    #holo2 = cv2.addWeighted(holo2, 0.4, shift_img(holo2.copy(), -5, -5), 0.6, 0)
#
    #holo_done = cv2.addWeighted(frame, 0.5, holo2, 0.6, 0)
    #
    #frame = holo_done
    for c in range(frame.shape[2]):
        frame[:,:,c] = frame[:,:,c]*mask + replacement_bg[:,:,c]*inv_mask
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    fake.schedule_frame(frame)
    #cv2.imwrite("test.jpg", frame)        