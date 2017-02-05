from nativeio import I2C
from board import *
from time import sleep

from bma2x2 import BMA2X2
from bmg160 import BMG160

i2c = I2C(SCL, SDA)
i2c.try_lock()
addresses = [ int(address) for address in i2c.scan() ]

print('found devices on', addresses)

accel = BMA2X2(i2c, 25)
gyro = BMG160(i2c, 17)
