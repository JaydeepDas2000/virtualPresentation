import cv2
import os
from handTracker import HandDetector
import numpy as np

# variable
imageNumber = 0
widthSlide, heightSlide = 1280, 720
widthCam, heightCam = int(213*2), int(120*2)
gestureThreshold = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 30
annotations = [[]]
annotationNumber = -1
annotationStart = False


# define the path of the presentation folder
folderPath = 'presentation'

# cam setup
cap = cv2.VideoCapture(0)
cap.set(3,widthSlide)
cap.set(4,heightSlide)

# GET list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
# print(pathImages)

# Hand Detector
detector = HandDetector(detectionCon = 0.8, maxHands = 1)


while True:
    # importing Images
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath,pathImages[imageNumber])
    imgCurrent = cv2.imread(pathFullImage)

    hands, img = detector.findHands(img, flipType=False)
    # Gesture Position line
    cv2.line(img, (0, gestureThreshold), (widthSlide, gestureThreshold), (0,255,0,0.5), 5)

    if hands and buttonPressed == False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        # print(fingers)

        # Accept gesture
        cx, cy = hand['center'] # if the hand present inside gesture box
        lmList = hand['lmList']

        # Constrain values for easier drawing
        xVal = int(np.interp(lmList[8][0], [widthSlide//2, widthSlide], [0, widthSlide]))
        yVal = int(np.interp(lmList[8][1], [150, heightSlide-150], [0, heightSlide]))
        indexFinger = xVal, yVal

        if cy <= gestureThreshold:
            
            # Gesture 1
            if fingers == [0,0,0,0,0]: # thumb gesture/ previous slide
                annotations = [[]]
                annotationNumber = -1
                annotationStart = False
                """ 
                    print('left')
                    break
                """
                if imageNumber > 0:
                    buttonPressed = True
                    imageNumber -=1

            # Gesture 2
            if fingers == [1,0,0,0,1]: # little finger gesture/ next slide
                annotations = [[]]
                annotationNumber = -1
                annotationStart = False
                """
                    print('right')
                    break
                """
                if imageNumber < len(pathImages)-1:
                    buttonPressed = True
                    imageNumber +=1

        # Gesture 3
        if fingers == [1,1,1,0,0]: # index and middle finger gesture/ pointer
            cv2.circle(imgCurrent, indexFinger, 12, (0,0,255), cv2.FILLED)
        
        # Gesture 4
        if fingers == [1,1,0,0,0]: # only index finger gesture/ draw
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0,0,255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False
        
        # Gesture 5
        if fingers == [1,1,1,1,0]: # three finger gesture/ erase
            if annotations:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True
    else:
        annotationStart = False

    # buttonPressed iterations
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j!=0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0,0,200), 12)   

    # adding cam img in slide
    imgCam = cv2.resize(img,(widthCam,heightCam))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:heightCam, w - widthCam:w] = imgCam

    # cv2.imshow("Image",img)
    cv2.imshow("Slides",imgCurrent)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break