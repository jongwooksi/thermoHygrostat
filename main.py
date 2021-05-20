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
from test import predict

init = [0.020, 0.040, 0.060, 0.140, 0.210, 0.238,0.286,0.334, 0.382, 0.430, 0.478, 0.526, 0.574, 0.622, 0.670, 0.718, 0.766, 0.814, 0.862, 0.910, 0.958, 1.006, 1.054, 1.102, 1.150, 1.198, 1.246, 1.294, 1.342, 1.390, 1.438, 1.486, 1.534, 1.582, 1.630, 1.678, 1.726, 1.774, 1.822, 1.870 ]
step = [0.010, 0.047, 0.063 ,0.077, 0.093, 0.131,0.149,0.177, 0.204, 0.232, 0.260, 0.287, 0.315, 0.343, 0.370, 0.398, 0.426, 0.453, 0.481, 0.509, 0.533, 0.560, 0.587, 0.614, 0.642, 0.669, 0.696, 0.723, 0.750, 0.777, 0.805, 0.832, 0.859, 0.886, 0.913, 0.941, 0.968, 0.995, 1.022, 1.049 ]

capture = cv2.VideoCapture(0, cv2.CAP_V4L)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

reverseFlag =False

def dataScan(angletopan, angletotilt):
    movehorizon = (angletopan- 320)/10 - 5
    moveverticle = (angletotilt- 240)/10 + 20  #-4 is finetuning
     
    updown_move(moveverticle)
    distance = scan(-movehorizon)
        
    
    dtpavalue = dtpaStart()
    res = np.reshape(dtpavalue,(32,32))
    cropDtpa = res[14:19 , 14:19]
    
    
    for row in range(5):
        for col in range(5):
            condition = int((cropDtpa[row][col]+1)/5)
            
            if condition < 0:
                continue
            
            else:
                modifyVal = cropDtpa[row][col] + init[condition] + (int(float(distance)*0.1) - 1)*step[condition] 
                cropDtpa[row][col] = modifyVal
            
   
    # modify temperature about distance
     
    maxVal = round(cropDtpa.max(),1)
    
    print(maxVal)
    print('pan', angletopan, 'tilt', angletotilt)
    print("current left-right(pan) angle: ", -movehorizon)
    print("current up-down(tilt) angle: ", moveverticle)
    return maxVal
                    
            
if __name__ == '__main__':
    #init()
    f = open('collect.csv','a', newline='')
    inputData = []
    
    while cv2.waitKey(33) < 0:
        ret, frame = capture.read()
        
        showdata = [[0 for row in range(32)] for col in range(24)]
    
        angletopan = 0
        angletotilt = 0
        maxVal = -1
        
        print('object POS- current :',angletopan, angletotilt)
        
        if reverseFlag is False:
            for angletotilt in range(0,480, 20):
                if((angletotilt/20)%2 ==0):
                    for angletopan in range(0,640,20):
                        maxVal = dataScan(angletopan, angletotilt)
                        showdata[int(float(angletotilt)/20)][int(float(angletopan)/20)] = maxVal
     
                else:
                    for angletopan in reversed(range(0,640,20)):
                        maxVal = dataScan(angletopan, angletotilt)                 
                        showdata[int(float(angletotilt)/20)][int(float(angletopan)/20)] = maxVal
           
            reverseFlag = True
            
        else:
            for angletotilt in reversed(range(0,480, 20)):
                if((angletotilt/20)%2 ==0):
                    for angletopan in reversed(range(0,640,20)):
                        maxVal = dataScan(angletopan, angletotilt)
                        showdata[int(float(angletotilt)/20)][int(float(angletopan)/20)] = maxVal
     
                else:
                    for angletopan in range(0,640,20):
                        maxVal = dataScan(angletopan, angletotilt)                 
                        showdata[int(float(angletotilt)/20)][int(float(angletopan)/20)] = maxVal
           
            reverseFlag = False
        
        
        
        print()
        print(showdata)
        image, value = showImage(frame, showdata)
        
        if value == -1:
            print("normal environment")
        else:
            if len(inputData) == 5:            
                del inputData[0]
                inputData.append(value)
                print("anomaly") if predict(inputData) else print("normal")
                
                
                wr = csv.writer(f)
                wr.writerow(inputData)
                f.close()
                
            else:
                inputData.append(value)
            
            print(inputData)
            
            cv2.imshow("VideoFrame", image)
        
       # with open('temperature.json', 'w') as file:
       #     json.dump(showdata, file)
        
capture.release()
cv2.destroyAllWindows()


        
        
    
           

       

       




