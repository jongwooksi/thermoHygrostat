import cv2
import json
import numpy as np
import copy
capture = cv2.VideoCapture(0, cv2.CAP_V4L)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while cv2.waitKey(33) < 0:
    ret, frame = capture.read()
    show_image = copy.deepcopy(frame)
    #for i in range(20, 640, 20):
    #    for j in range(20, 480, 20):
    #        frame = cv2.rectangle(frame, (i-10, j-10), (i+10, j+10), (0,0,255), 1)
    with open("data.json") as file:
        new_list = json.load(file)
       
    for i in range(0, 64):
        for j in range(0, 48):
            if(float(new_list[i][j]) >= 45):
                frame = cv2.rectangle(frame, (i*10, j*10), (i*10+10, j*10+10), (255,255,255), -1)
   #         elif(float(new_list[i][j]) > 30 and float(new_list[i][j]) < 36):
   #             frame = cv2.rectangle(frame, (i*10, j*10-10), (i*10+10, j*10+10), (0,128,125), -1)
            else:
                frame = cv2.rectangle(frame, (i*10, j*10-10), (i*10+10, j*10+10), (0,0,0), -1)
    
    
    dst = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    ret, dst = cv2.threshold(dst,250,255, cv2.THRESH_BINARY)
    kernel = np.ones((21, 21), np.uint8)
    #dst = cv2.erode(dst, kernel,iterations = 1)
    
    contours, hierachy = cv2.findContours(dst, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    object_number = 0
    for cnt in contours:
        
        x, y, w, h = cv2.boundingRect(cnt)
        if(w*h<=100):
            continue
        show_image = cv2.rectangle(show_image, (x, y), (x+w, y+h), (127,127,0), 2)
        #obejct_temperature = 0
        #object_temperature = sum(new_list[int(x/10):int((x+w)/10)][int(y/10):int((y+h)/10)],[])
        #print(x, y, w, h, new_list[int(x/10):int((x+w)/10), int(y/10):int((y+h)/10)])
        cv2.putText(show_image, 'object'+str(object_number)+ " " +str(new_list[int((2*x+w)/20)][int((2*y+h)/20)]), (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255), 1)
        object_number += 1

    show_image = cv2.drawContours(show_image, contours, -1, (255,0,0), -1)
    

    #show_image = cv2.(show_image, contours, -1, (255,0,0), -1)
  
    # frame = cv2.rectangle(frame, (20-15, 20-15), (620+15, 20+15), (0,0,255), 3)
    cv2.imshow("VideoFrame", show_image)

capture.release()
cv2.destroyAllWindows()