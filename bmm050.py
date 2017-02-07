'''
bmm050 is a micropython module for the Bosch BMM050 sensor.
It measures the magnetic field in three axis.

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

# from stackoverflow J.F. Sebastian
def _twos_comp(val, bits=8):
    """compute the 2's complement of int val with bits"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


class BMM050():
    '''magnetometer'''

    def __init__(self, i2c, addr):

        self.buf = bytearray(114)
        self.i2c = i2c
        self.mag_addr = addr
        self.chip_id = i2c.readfrom_mem(self.mag_addr, 0x40, 1)[0]

    def _read_mag(self, addr):
        """return accel data from addr"""
        LSB, MSB = self.i2c.readfrom_mem(self.mag_addr, addr, 2)
        LSB = _twos_comp(LSB)
        MSB = _twos_comp(MSB)
        return (LSB + (MSB<<5))/(2**15)

    def x(self):
        return self._read_mag(0x42)

    def y(self):
        return self._read_mag(0x44)

    def z(self):
        return self._read_mag(0x46)
