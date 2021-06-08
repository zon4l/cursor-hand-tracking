import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#variables
wCam, hCam = 640, 480
pTime = 0
area = 0
smoothening = 5
#variables

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon = 0.7, maxHands = 1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()

    #find Hands
    img = detector.findHandss(img)
    lmList, bbox = detector.findPosition(img, draw = True)
    if len(lmList) != 0:

        # Filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        if 250 < area < 1100:


            # Find distance between index and thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # Convert volume
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = np.interp(length, [50,300], [0, 100])

            # Smoothening
            volPer = smoothening * round(volPer / smoothening)

            # Check fingers up
            fingers = detector.fingersUp()

            # If pinky is down set volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)

            # drawings
            cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f"{int(volPer)}%", (52, 450), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 2)

    # FPS
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (40, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("img", img)
    cv2.waitKey(1)