'''
bmg160 is a micropython module for the Bosch BMG160 sensor.
It measures turn rate in three axis.

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


class BMG160():
    '''gyroscope'''

    def __init__(self, i2c):

        if type (i2c) == machine.I2C:
            self.i2c = i2c
        else:
            raise TypeError('passed argument is not an I2C object')
        self.gyro_addr = 0x68
        try:
            self.chip_id = i2c.readfrom_mem(self.gyro_addr, 0x00, 1)[0]
        except OSError:
            self.acc_addr = 0x69
            try:
                self.chip_id = i2c.readfrom_mem(self.gyro_addr, 0x00, 1)[0]
            except OSError:
                raise OSError('no BMG160 connected')

    def _read_gyro(self, addr):
        """return accel data from addr"""
        LSB, MSB = self.i2c.readfrom_mem(self.gyro_addr, addr, 2)
        LSB = _twos_comp(LSB)
        MSB = _twos_comp(MSB)
        return 2000*(LSB + (MSB<<8))/(2**15)

    def x(self):
        return self._read_gyro(0x02)

    def y(self):
        return self._read_gyro(0x04)

    def z(self):
        return self._read_gyro(0x06)

    def xyz(self):
        return (self.x(), self.y(), self.z())
