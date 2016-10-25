'''
bma2x2 is a micropython module for the Bosch BMA2X2 sensor.
It measures acceleration three axis.

The MIT License (MIT)

Copyright (c) 2016 Sebastian Plamauer oeplse@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import machine
from time import sleep_ms as sleep

# from stackoverflow J.F. Sebastian
def _twos_comp(val, bits=8):
    """compute the 2's complement of int val with bits"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


class BMA2X2():
    '''accelerometer'''

    def __init__(self, i2c):

        if type (i2c) == machine.I2C:
            self.i2c = i2c
        else:
            raise TypeError('passed argument is not an I2C object')
        self.acc_addr = 0x18
        try:
            self.chip_id = i2c.readfrom_mem(self.acc_addr, 0x00, 1)[0]
        except OSError:
            self.acc_addr = 0x19
            try:
                self.chip_id = i2c.readfrom_mem(self.acc_addr, 0x00, 1)[0]
            except OSError:
                raise OSError('no BMA2X2 connected')
        self.set_range(16)      # default range 16g
        self.set_filter_bw(128)    # default filter bandwith 125Hz

    def _read_accel(self, addr):
        """return accel data from addr"""
        LSB, MSB = self.i2c.readfrom_mem(self.acc_addr, addr, 2)
        LSB = _twos_comp(LSB)
        MSB = _twos_comp(MSB)
        return (LSB + (MSB<<4))*self._resolution/1000

    def temperature(self):
        return self.i2c.readfrom_mem(self.acc_addr, 0x08, 1)[0]/2 + 23

    def set_range(self, accel_range):
        """set accel range to 2, 4, 8 or 16g"""
        ranges = {2:b'\x03', 4:b'\x05', 8:b'\x08', 16:b'\x0C'}
        try:
            range_byte = ranges[accel_range]
        except KeyError:
            raise ValueError('invalid range, use 2, 4, 8 or 16')
        self.i2c.writeto_mem(self.acc_addr, 0x0F, range_byte)
        self._resolution = {2:0.98, 4:1.95, 8:3.91, 16:7.81}[accel_range]
        return self.get_range()

    def get_range(self):
        return {3:2,5:4,8:8,12:16}[self.i2c.readfrom_mem(self.acc_addr, 0x0F, 1)[0]]

    def set_filter_bw(self, freq):
        freqs = {8:b'\x08', 16:b'\x09', 32:b'\x0A', 64:b'\x0B', 128:b'\x0C', 256:b'\x0D', 512:b'\x0E', 1024:b'\x0F'}
        try:
            freq_byte = freqs[freq]
        except:
            raise ValueError('invalid filter bandwith, use 8, 16, 32, 64, 128, 256, 512 or 1024')
        self.i2c.writeto_mem(self.acc_addr, 0x10, freq_byte)
        return self.get_filter_bw()

    def get_filter_bw(self):
        return 2**(self.i2c.readfrom_mem(self.acc_addr, 0x10, 1)[0]-5)

    def compensation(self, active=None):
        accel_range = self.get_range()
        self.set_range(2)
        self.i2c.writeto_mem(self.acc_addr, 0x37, b'\x21') # settings x0y0z1 10Hz
        self.i2c.writeto_mem(self.acc_addr, 0x36, b'\x80') # reset
        if active is None:  # trigger fast comp
            active = 'compensated'
            print(self.i2c.readfrom_mem(self.acc_addr, 0x36, 1))
            self.i2c.writeto_mem(self.acc_addr, 0x36, b'\x20') # x
            sleep(100)
            print(self.i2c.readfrom_mem(self.acc_addr, 0x36, 1))
            self.i2c.writeto_mem(self.acc_addr, 0x36, b'\x40') # y
            sleep(100)
            print(self.i2c.readfrom_mem(self.acc_addr, 0x36, 1))
            self.i2c.writeto_mem(self.acc_addr, 0x36, b'\x60') # z
            sleep(100)
            print(self.i2c.readfrom_mem(self.acc_addr, 0x36, 1))
        elif active:        # activate slow comp
            self.i2c.writeto_mem(self.acc_addr, 0x36, b'\x07')
        elif not active:    # deactivate slow comp
            self.i2c.writeto_mem(self.acc_addr, 0x36, b'\x00')
        else:
            raise TypeError('pass a boolean or no argument')
        self.set_range(accel_range)
        return active

    def x(self):
        return self._read_accel(0x02)

    def y(self):
        return self._read_accel(0x04)

    def z(self):
        return self._read_accel(0x06)

    def xyz(self):
        return (self.x(), self.y(), self.z())
