# main.py -- put your code here!

from machine import I2C, Pin
from bmx055 import BMX055
from attitude import angles
import time

# for atsamd21
i2c_bus = I2C(scl=Pin.board.SCL, sda=Pin.board.SDA, freq=400000)
i2c_bus.init()

imu = BMX055(i2c_bus)

print(imu.accel.i2c.readfrom_mem(imu.accel.acc_addr, 0, 63))

print('temperature:', imu.accel.temperature())
print('resolution:', imu.accel._resolution)
print('accel:', imu.accel.xyz())
print('set range 2:', imu.accel.set_range(2))
print('set filter 128:', imu.accel.set_filter_bw(128))

t_end = time.ticks_ms() + 100*1000
while time.ticks_ms() < t_end:
    imu_data = imu.accel.xyz()
    print(imu_data, angles(imu_data))
    time.sleep_ms(1000)

i2c_bus.deinit()
