import time
import serial
import requests
from pantilt import *
import sys
import tty
import termios
import pyautogui
import json
import numpy as np
# import keyboard
#import pygame
# from pynput.keyboard import Key,Listener
# from msvcrt import getch

###############################################################
dtparequestHeader = bytearray([0x11, 0x00, 0x00, 0x04, 0x01, 0x98])
dtparequestLength = 2054
dtpaBaudrate = 115200
dtpaPort = "/dev/ttyUSB1"
minRange = -10
maxRange = 200
maxIndex = 1023
minRangeSensor = -20
maxRangeSensor = 70

def is_Range(dex):
    if dex > minRange and dex < maxRange:
        return dex

    else:
        return "Out of Range"

def is_RangeSensor(dex):
    if dex > minRangeSensor and dex < maxRangeSensor:
        return dex

    else:
        return "Out of Range"

def deximal(high, low):
	dex = ((high << 8) + low)
	
	if high > 128: 
		byte_mask = ~0xFFFF
		result = ( ((high << 8) + low) | byte_mask ) >> 4
		return round(result * 0.1, 1)

	else:
		return round(dex * 0.1, 1)

def transData(rx_data, number):
	p_num = 2*number + 4

	dex = deximal(rx_data[p_num], rx_data[p_num+1])

	return is_Range(dex)

def transSensor(high, low):
	dex = deximal(high, low)
	return is_RangeSensor(dex)

def printfunction(value):
	if type(value) is float:
		print("{:.1f}".format(value))

	else:
		print("{err}".format(err=value))

def dtpaStart():	
	
	ser = serial.Serial(dtpaPort, baudrate = dtpaBaudrate, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout=1)

	ser.write(bytearray(dtparequestHeader))
	rx_data = ser.read(dtparequestLength)
	
	dtpavalue = []
	
	for i in range(maxIndex+1):
		value = transData(rx_data, i)
		dtpavalue.append(value)
		
	ser.close()
	return dtpavalue
	
###############################################################

requestHeader = bytearray([0x5A, 0x05, 0x05, 0x06, 0x6A])
responseHeader = bytearray([0x5A, 0x05, 0x05, 0x06, 0x6A])
DataHeader = bytearray([0x59, 0x59])
requestLength = 100
lidarBaudrate = 115200
lidarPort = "/dev/ttyUSB0"

def modify_header(rx_data):
    loc_index = rx_data.find(responseHeader)
    
    if rx_data[loc_index:loc_index+len(responseHeader)] == responseHeader:
        return loc_index

def calDistance(high, low): 
    calD = (low<<8) & 0xff00 | high & 0x00ff
  
    return calD * 0.1

def checkHeader(inputHeader):
    if responseHeader == inputHeader:
        return True

    else:
        return False

def checkDataHeader(inputHeader):
    if DataHeader == inputHeader:
        return True

    else:
        return False

def lidarstart():
    ser = serial.Serial(lidarPort, baudrate = lidarBaudrate, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout=1)   
    ser.write(requestHeader)
    rx_data = ser.read(requestLength)

    
    start_index = modify_header(rx_data)
    rx_data = rx_data[start_index:]
    rx_data = rx_data[:14]

    if checkHeader(rx_data[:5]):
        if not checkDataHeader(rx_data[5:7]):       
            print("Invalid Data Header")
            return -1
        

        for i in range(len(rx_data)):
            #print(hex(rx_data[i]), end=" ")
            if i == 4 :
                print()

        rx_data = rx_data[5:]

        distance = calDistance(rx_data[2], rx_data[3])
        print()
        

        print()

    else:
        if len(rx_data) == 0:
            print("Empty Data")
            return -1
        else:
            print("Invalid Response Header")
            return -1
    ser.close()
    return distance
   
def scan(deg):
    move(deg)
    time.sleep(0.02)
    distance = lidarstart()
    fix = 8
    map_d = (distance**2 - fix**2)**0.5 +3
    #print("deg:{} {:.1f} cm".format(deg-10,map_d))
    print("Distance {:.1f} cm".format(distance))
    f = open("distance.txt", 'w')
    f.write(str(distance))
    f.close()
    return round(distance, 1)

def updown(deg):
    updown_move(deg)
    time.sleep(0.02)
    
def getkey():
    fd = sys.stdin.fileno()
    original_attributes = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, original_attributes)
    return ch

if __name__ == '__main__':
    init()
    scanangle = 0
    updownangle = 0
    
    
    
    while True:

        scandata = []
        showdata = [[0 for col in range(48)] for row in range(64)]
        
        
        
 
        angletopan = 0
        angletotilt = 0
        print('object POS- current :',angletopan, angletotilt)
        
        
        for angletotilt in range(0,480, 10):
            if((angletotilt/10)%2 ==0):
                for angletopan in range(0,640,10):
                    templeftright = int(angletopan)- 320
                    movehorizon = templeftright/10 - 5
            
                    tempupdown = int(angletotilt)- 240
                    moveverticle = (tempupdown / 10) -10  #-4 is finetuning
                     
                    scanangle = -int(movehorizon) 
                    updownangle = int(moveverticle) 

                    updown(updownangle)
                    scandata.append(scan(scanangle))
                    
                        
                    
                    dtpavalue = dtpaStart()
                    res = np.reshape(dtpavalue,(32,32))
                    last = res[14:19 , 14:19]
                    distance = scan(scanangle)
                    m=0
                    n=0
                    while m<5:
                        while n<5:
                            if(last[m][n] > 24):
                                for k in range(10):
                                    if(int(float(distance)) >= k*100 and int(float(distance)) < (k+1) * 100):
                                        last[m][n] += 1.6 * k # + 0.1 * k * k 
                            n +=1
                        m +=1
                        n=0
                    
                    line = last.max()
                    print('pan', angletopan, 'tilt', angletotilt)
                    showdata[int(int(float(angletopan))/10)][int(int(float(angletotilt))/10)] = line
                    
                    
                    #f.close()
                    
                    print("current left-right(pan) angle: ", -scanangle)
                    print("current up-down(tilt) angle: ", updownangle)
            else:
                for angletopan in reversed(range(0,640,10)):
                    templeftright = int(angletopan)- 320
                    movehorizon = templeftright/10 - 5
            
                    # angletotilt = input()
                    tempupdown = int(angletotilt)- 240
                    moveverticle = (tempupdown / 10) -10  #-4 is finetuning
                     
                    scanangle = -int(movehorizon) 
                    updownangle = int(moveverticle) 

                    updown(updownangle)
                    scandata.append(scan(scanangle))
      
                    dtpavalue = dtpaStart()
                    res = np.reshape(dtpavalue,(32,32))
                    last = res[14:19 , 14:19]
                    distance = scan(scanangle)
                    m=0
                    n=0
                    while m<5:
                        while n<5:
                            if(last[m][n] > 24):
                                for k in range(10):
                                    if(int(float(distance)) >= k*100 and int(float(distance)) < (k+1) * 100):
                                        last[m][n] += 1.6 * k # + 0.1 * k * k 
                            n +=1
                        m +=1
                        n=0
                    
                    line = last.max()
                    print('pan', angletopan, 'tilt', angletotilt)                    
                    showdata[int(int(float(angletopan))/10)][int(int(float(angletotilt))/10)] = line
                    
                    print("current left-right(pan) angle: ", -scanangle)
                    print("current up-down(tilt) angle: ", updownangle)                    
                    
   

        #print(scandata)
        
        print()
        print(showdata)
        with open('data.json', 'w') as file:
            json.dump(showdata, file)
        end()
        
        
    
           

       

       


