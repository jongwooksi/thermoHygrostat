import serial
import requests
import time


requestHeader = bytearray([0x11, 0x00, 0x00, 0x04, 0x01, 0x98])
requestLength = 2054
dtpaBaudrate = 115200
dtpaPort = "/dev/ttyUSB0"
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

	ser.write(bytearray(requestHeader))
	rx_data = ser.read(requestLength)

	dtpavalue = []
	
	for i in range(maxIndex+1):
		value = transData(rx_data, i)
		dtpavalue.append(value)
		
	ser.close()
	return dtpavalue
	
import numpy as np

if __name__ == "__main__":
    while True:
        dtpavalue = dtpaStart()
        res = np.reshape(dtpavalue,(32,32))
        #14 to 18
  #      print(res[14:19, 14:19])
        
        last = res[14:19 , 14:19]
   #     print('asd',last)
        i = 0
        j = 0
        f = open("distance.txt", 'r')
        distance = f.readline()
        print('distance____',distance)
        f.close()
        while i < 5:
            while j < 5:
                if(last[i][j] > 24):
                    '''
                    if(int(float(distance)) < 100):
                        last[i][j] += 5
                    elif(int(float(distance)) >= 100 & int(float(distance)) < 200):
                        last[i][j] += 7
                    elif(int(float(distance)) >= 200 & int(float(distance)) < 300):
                        last[i][j] += 9
                    elif(int(float(distance)) >= 300 & int(float(distance)) < 400):
                        last[i][j] += 7
                    elif(int(float(distance)) >= 400 & int(float(distance)) < 500):
                        last[i][j] += 35
                    elif(int(float(distance)) >= 500 & int(float(distance)) < 600):
                        last[i][j] += 14
                        '''
                    for k in range(10):
                        if(int(float(distance)) >= k*100 and int(float(distance)) < (k+1) * 100):
                            last[i][j] += 1.6 * k # + 0.1 * k * k 
                j += 1
            i += 1
            j = 0
                
                
        print('temperature',last.max())
        f= open("temperature.txt","w")
        f.write(str(float(last.max())))
        f.close()
        
              


