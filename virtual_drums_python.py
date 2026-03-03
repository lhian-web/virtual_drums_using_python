import cv2
import numpy as np
from pygame import mixer
import time

webcam = cv2.VideoCapture(0)

ret,frame = webcam.read()
if ret == False:
    print("Unable to read video")
    exit()

mixer.init()
class Drum:
    def __init__(self,pos,type):
        self.position = pos
        self.type = type
        self.sound = mixer.Sound(self.type+"_sound.mp3")
        self.image = cv2.resize(cv2.imread(self.type+".png"),(self.position[2],self.position[3]))
        self.lastTime = time.time()-1

    def playSound(self):
        currentTime = time.time()
        if currentTime-self.lastTime < 0.5:
            return

        self.sound.play()
        self.lastTime = currentTime

    def addImage(self,frame):
        o = frame[self.position[1]:self.position[1]+self.position[3],
        self.position[0]:self.position[0]+self.position[2]]
        frame[self.position[1]:self.position[1] + self.position[3],
        self.position[0]:self.position[0] + self.position[2]] = cv2.addWeighted(self.image,0.6,o,0.4,0.0)
        return frame

    def checkHit(self,pos):
        if (pos[0] >= self.position[0] and pos[0] <= self.position[0] + self.position[2]) and (
                pos[1] >= self.position[1] and pos[1] <= self.position[1] + self.position[3] ):
            self.playSound()

snare_drum = Drum((100,200,100,100),"snare_drum")
bass_drum = Drum((200,300,100,100),"bass_drum")
hi_hat = Drum((500,200,100,100),"hi_hat")
tom_drum = Drum((400,300,100,100),"tom_drum")

drums_list = [snare_drum,bass_drum,hi_hat,tom_drum]

while True:
    ret,frame = webcam.read()
    if ret == False:
        print("Unable to read video")
        break
    frame = cv2.flip(frame,1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lowerlimit = np.array([90, 50, 70])
    upperlimit = np.array([128, 255, 255])
    blue_mask = cv2.inRange(hsv, lowerlimit, upperlimit)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_ERODE, np.ones((5, 5), np.uint8))
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_DILATE, np.ones((5, 5), np.uint8))
    cv2.imshow("Blue Mask",blue_mask)

    (contours, _) = cv2.findContours(blue_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours)>0:
        contour = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(contour)
        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)

        for drum in drums_list:
            drum.checkHit((int(x), int(y)))

    for drum in drums_list:
        frame = drum.addImage(frame)

    cv2.imshow("Magic Drum",frame)

    if cv2.waitKey(1)==ord("q"):
        break

webcam.release()
cv2.destroyAllWindows()