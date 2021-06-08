import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

wCam, hCam = 640, 480
frameR = 100    # Frame Reduction
wScr, hScr = autopy.screen.size()
smoothening = 5

#print(wScr, hScr)

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
plocX, plocY = 0,0
clocX, clocY = 0,0

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