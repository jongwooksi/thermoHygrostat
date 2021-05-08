import pantilthat as pt
import time

def init():
    pt.servo_enable(1, True)
    pt.servo_enable(2, True)
    pt.tilt(0)
    pt.pan(0)
    
# enable the pan and tilt servos

def end():
    pt.servo_enable(1, False)
    pt.servo_enable(2, False)
    
    
def move(i):    
    pt.pan(i)
    time.sleep(0.02)
    
def updown_move(i):    
    pt.tilt(i)
    time.sleep(0.02)



