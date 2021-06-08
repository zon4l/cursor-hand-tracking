import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#Resolution variables
wCam, hCam = 640, 480
frameR = 100    # Frame Reduction
wScr, hScr = autopy.screen.size()
smoothening = 5
#Resolution variables

#print(wScr, hScr)

#Start camera
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
#Start camera

#Volume Control variables
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
#Volume Control variables


#Hand Tracking variables
pTime = 0
plocX, plocY = 0,0
clocX, clocY = 0,0
#Hand Tracking variables

detector = htm.handDetector(maxHands = 1)

while True:

    #1. Find hand landmarks
    success, img = cap.read()
    img = detector.findHandss(img)
    lmList, bbox = detector.findPosition(img)

    #2. Get the tips of index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        #print(x1, y1, x2, y2)

        #3. Check which fingers are up
        fingers = detector.fingersUp()
        #print(fingers)

        #4. Only Index Finger: moving mode
        if fingers[1] == 1 and fingers[2] == 0:

            # Check if thumb is up: volume control mode
            if fingers[0] == 1:
                # Filter based on size
                area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
                if 250 < area < 1100:

                    # Find distance between index and thumb
                    length, img, lineInfo = detector.findDistance(4, 8, img)

                    # Convert volume
                    volBar = np.interp(length, [50, 300], [400, 150])
                    volPer = np.interp(length, [50, 300], [0, 100])

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
                    cv2.putText(img, f"{int(volPer)}%", (52, 450), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)

            # Else: continue cursor movement
            else:
                #5. Convert coordinates
                cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                #6. Smoothen values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                #7. Move Mouse
                autopy.mouse.move(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 10, (255,0,255), cv2.FILLED)
                plocX, plocY = clocX, clocY

        #8. when both index and middle fingers are up; clicking mode
        if fingers[1] == 1 and fingers[2] == 1:
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

            # 9. find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            #print(length)
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)

                # 10. Click mouse if distance short
                autopy.mouse.click()

    #11. frame rate
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20,50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)

    #12. display
    cv2.imshow("Image", img)
    cv2.waitKey(1)