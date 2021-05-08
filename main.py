import time
import serial
import requests
import cv2
import copy
import sys
import numpy as np

from dtpa import *
from tfminiplus import *
from camera import *
from pantilt import *

#import tty
#import termios
#import pyautogui
#import json

capture = cv2.VideoCapture(0, cv2.CAP_V4L)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


def dataScan(angletopan, angletotilt):
    movehorizon = (angletopan- 320)/10 - 5
    moveverticle = (angletotilt- 240)/10 + 20  #-4 is finetuning
     
    updown_move(moveverticle)
    distance = scan(-movehorizon)
        
    
    dtpavalue = dtpaStart()
    res = np.reshape(dtpavalue,(32,32))
    last = res[14:19 , 14:19]
    
    
    for m in range(5):
        for n in range(5):
            if(last[m][n] > 24):
                for k in range(10):
                    if(int(float(distance)) >= k*100 and int(float(distance)) < (k+1) * 100):
                        last[m][n] += 1.6 * k # + 0.1 * k * k 
           
    # modify temperature about distance
     
    maxVal = round(last.max(),1)
    
    print(maxVal)
    print('pan', angletopan, 'tilt', angletotilt)
    print("current left-right(pan) angle: ", -movehorizon)
    print("current up-down(tilt) angle: ", moveverticle)
    return maxVal
                    
                    
if __name__ == '__main__':
    #init() 

    while cv2.waitKey(33) < 0:
        ret, frame = capture.read()
        
        showdata = [[0 for row in range(32)] for col in range(24)]
    
        angletopan = 0
        angletotilt = 0
        maxVal = -1
        
        print('object POS- current :',angletopan, angletotilt)
        
        
        for angletotilt in range(0,480, 20):
            if((angletotilt/20)%2 ==0):
                for angletopan in range(0,640,20):
                    maxVal = dataScan(angletopan, angletotilt)
                    showdata[int(float(angletotilt)/20)][int(float(angletopan)/20)] = maxVal
 
            else:
                for angletopan in reversed(range(0,640,20)):
                    maxVal = dataScan(angletopan, angletotilt)                 
                    showdata[int(float(angletotilt)/20)][int(float(angletopan)/20)] = maxVal
       
            
        print()
        print(showdata)
        image = showImage(frame, showdata)
        
        cv2.imshow("VideoFrame", image)
        
       # with open('temperature.json', 'w') as file:
       #     json.dump(showdata, file)
        
capture.release()
cv2.destroyAllWindows()


        
        
    
           

       

       



