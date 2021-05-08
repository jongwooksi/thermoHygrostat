import cv2
import json
import numpy as np
import copy

thresh = 35

def showImage(mask, new_list):

    show_image = copy.deepcopy(mask)
 
    #with open("temperature.json") as file:
    #    new_list = json.load(file)
       

    for row in range(0,24):
        for col in range(0,32):
            if(float(new_list[row][col]) >= thresh):    
                cv2.rectangle(mask, (col*10, row*10), (col*10+10, row*10+10), (255,255,255), -1)
 
            else:
                cv2.rectangle(mask, (col*10, row*10-10), (col*10+10, row*10+10), (0,0,0), -1)
    
    dst = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    
    ret, dst = cv2.threshold(dst,250,255, cv2.THRESH_BINARY)
    
    contours, hierachy = cv2.findContours(dst, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    object_number = 1

    for cnt in contours:
        
        x, y, w, h = cv2.boundingRect(cnt)
        
        
        if(w * h <= 1000):
            continue
        
        show_image = cv2.rectangle(show_image, (x, y), (x+w, y+h), (127,127,0), 2)
       
        center_x = int((2*x + w)/20)
        center_y = int((2*y + h)/20)
        
        area = np.array(new_list)
      
        area = area[int(y/10):int((y+h)/10), int(x/10):int((x+w)/10)]
        
        contour_temperature = round(np.mean(np.mean(area, 1), 0), 1)
        
        text = 'object'+ str(object_number)+ " " + str(contour_temperature )
        
        cv2.drawContours(show_image, cnt, -1, (255,0,0), -1)
        cv2.putText(show_image, text, (10*center_x-20,10*center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255,0,255), 1)
        object_number += 1

        print(text)
        print(10*center_x, 10*center_y)
        
    return show_image

    