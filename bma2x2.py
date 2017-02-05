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

#from machine import I2C
from nativeio import I2C
from time import sleep

# from stackoverflow J.F. Sebastian
def _twos_comp(val, bits=8):
    '''
    compute the 2's complement of int val with bits
    '''
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


class BMA2X2():
    '''
    Class for BMA2X2 accelerometer
    '''

    def __init__(self, i2c: I2C, addr):
        '''
        Initializes with an i2c object as argument.
        Checks if device is connected.
        Sets range to 16g and filter bandwith to 128Hz.
        '''

        self.buf = bytearray(64)

        if type (i2c) == I2C:
            self.i2c = i2c
        self.acc_addr = addr
        self.chip_id = self._readfrom_mem(self.acc_addr, 0x00, 1)[0]
        self.set_range(2)      # default range 16g
        self.set_filter_bw(128)    # default filter bandwith 125Hz
        self.compensation()

    def _readfrom_mem(self, dev_addr, addr, no):
        self.i2c.readfrom_into(dev_addr, self.buf)
        return self.buf[addr:addr+no]

    def _writeto_mem(self, dev_addr, addr, byte):
        self.i2c.readfrom_into(dev_addr, self.buf)
        self.buf[addr] = int(byte)
        self.i2c.readfrom_into(dev_addr, self.buf)

    def _read_accel(self, addr: int) -> float:
        '''
        Returns acceleromter data from address.
        '''
        LSB, MSB = self._readfrom_mem(self.acc_addr, addr, 2)
        LSB = _twos_comp(LSB)
        MSB = _twos_comp(MSB)
        return (LSB + (MSB<<4))*self._resolution/1000

    def temperature(self) -> float:
        '''
        Returns temperature in degrees C.
        '''
        return self._readfrom_mem(self.acc_addr, 0x08, 1)[0]/2 + 23

    def set_range(self, accel_range: int):
        '''
        Sets the accelerometer range to 2, 4, 8 or 16g.
        '''
        ranges = {2:0x03, 4:0x05, 8:0x08, 16:0x0C}
        try:
            range_byte = ranges[accel_range]
        except KeyError:
            raise ValueError('invalid range, use 2, 4, 8 or 16')
        self._writeto_mem(self.acc_addr, 0x0F, range_byte)
        self._resolution = {2:0.98, 4:1.95, 8:3.91, 16:7.81}[accel_range]

    def get_range(self) -> int:
        '''
        Returns the accelerometer range.
        '''
        return {3:2,5:4,8:8,12:16}[self._readfrom_mem(self.acc_addr, 0x0F, 1)[0]]

    def set_filter_bw(self, freq: int):
        '''
        Sets the filter bandwith to 8, 16, 32, 64, 128, 256, 512 or 1024Hz.
        '''
        freqs = {8:0x08, 16:0x09, 32:0x0A, 64:0x0B, 128:0x0C, 256:0x0D, 512:0x0E, 1024:0x0F}
        try:
            freq_byte = freqs[freq]
        except:
            raise ValueError('invalid filter bandwith, use 8, 16, 32, 64, 128, 256, 512 or 1024')
        self._writeto_mem(self.acc_addr, 0x10, freq_byte)

    def get_filter_bw(self) -> int:
        '''
        Returns the filter bandwith.
        '''
        return 2**(self._readfrom_mem(self.acc_addr, 0x10, 1)[0]-5)

    def compensation(self, active=None) -> bool:
        '''
        With no arguments passed, runs fast compensation.
        With boolean argument passe, activates or deactivates slow compensation.
        '''
        accel_range = self.get_range()
        self.set_range(2)
        self._writeto_mem(self.acc_addr, 0x37, 0x21) # settings x0y0z1 10Hz
        self._writeto_mem(self.acc_addr, 0x36, 0x80) # reset
        if active is None:  # trigger fast comp
            self._writeto_mem(self.acc_addr, 0x36, 0x00) # deactivate slow comp
            active = False
            #print(self._readfrom_mem(self.acc_addr, 0x36, 1))
            self._writeto_mem(self.acc_addr, 0x36, 0x20) # x
            sleep(0.1)
            #print(self._readfrom_mem(self.acc_addr, 0x36, 1))
            self._writeto_mem(self.acc_addr, 0x36, 0x40) # y
            sleep(0.1)
            #print(self._readfrom_mem(self.acc_addr, 0x36, 1))
            self._writeto_mem(self.acc_addr, 0x36, 0x60) # z
            sleep(0.1)
            #print(self._readfrom_mem(self.acc_addr, 0x36, 1))
        elif active:        # activate slow comp
            self._writeto_mem(self.acc_addr, 0x36, 0x07)
        elif not active:    # deactivate slow comp
            self._writeto_mem(self.acc_addr, 0x36, 0x00)
        else:
            raise TypeError('pass a boolean or no argument')
        self.set_range(accel_range)
        return active

    def x(self) -> float:
        '''
        Returns x acceleration in g.
        '''
        return self._read_accel(0x02)

    def y(self) -> float:
        '''
        Returns y acceleration in g.
        '''
        return self._read_accel(0x04)

    def z(self) -> float:
        '''
        Returns z acceleration in g.
        '''
        return self._read_accel(0x06)

    def xyz(self) -> tuple:
        '''
        Returns x,y and z accelerations in g as tuple.
        '''
        return (self.x(), self.y(), self.z())
