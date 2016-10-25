from bmx055 import BMX055
from servo import Servo
from machine import Pin, I2C

#imu = BMX055(I2C(sda=Pin(4), scl=Pin(5)))

#right = Servo(Pin(2))
#left = Servo(Pin(15))

for i in range(17):
    try:
        Servo(Pin(i)).write_angle(180)
    except:
        print(i)
#sgeht
