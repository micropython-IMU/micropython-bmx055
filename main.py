# main.py -- put your code here!

from machine import I2C, Pin
from bmx055 import BMX055
import time

# for atsamd21
i2c_bus = I2C(scl=Pin.board.SCL, sda=Pin.board.SDA, freq=400000)
i2c_bus.init()

# for esp8266 (if this doesn't work switch 4 and 5)
# i2c_bus = I2c(scl=Pin(4), sda=Pin(5))

imu = BMX055(i2c_bus)

print(imu.accel.i2c.readfrom_mem(imu.accel.acc_addr, 0, 63))

print('temperature:', imu.accel.temperature())
print('resolution:', imu.accel._resolution)
print('accel:', imu.accel.xyz())
print('gyro:', imu.gyro.xyz())
print('set range 4:', imu.accel.set_range(4))
print('get range:', imu.accel.get_range())
print('set range 8:', imu.accel.set_range(8))
print('set filter 8:', imu.accel.set_filter_bw(8))
print('get filter:', imu.accel.get_filter_bw())
print('set filter 250:', imu.accel.set_filter_bw(250))
print('accel:', imu.accel.xyz())

t_end = time.ticks_ms() + 10*1000
while time.ticks_ms() < t_end:
    print(imu.accel.xyz())
    time.sleep_ms(100)

i2c_bus.deinit()
