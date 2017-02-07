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

from time import sleep

# from stackoverflow J.F. Sebastian
def _twos_comp(val, bits=8):
    '''
    compute the 2's complement of int val with bits
    '''
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


class BMG160():
    '''
    Class for BMG160 gyroscope
    '''

    def __init__(self, i2c, addr):
        '''
        Initializes with an I2C object and address as arguments.
        '''

        self.buf = bytearray(64)
        self.i2c = i2c
        self.gyro_addr = addr
        self.chip_id = self.i2c.readfrom_mem(self.gyro_addr, 0x00, 1)[0]
        self.set_range(125)      # default range 2000deg/s
        self.set_filter_bw(116)    # default filter bandwith 64Hz
        self.compensation()

    def _read_gyro(self, addr):
        '''
        return gyro data from addr
        '''
        LSB, MSB = self.i2c.readfrom_mem(self.gyro_addr, addr, 2)
        LSB = _twos_comp(LSB)
        MSB = _twos_comp(MSB)
        return (LSB + (MSB<<4))*self._resolution

    def set_range(self, gyro_range: int):
        '''
        Sets the gyro range to 125, 250, 500, 1000 or 2000deg/s.
        '''
        ranges = {125:b'\x04', 250:b'\x03', 500:b'\x02', 1000:b'\x01', 2000:b'\x00'}
        try:
            range_byte = ranges[gyro_range]
        except KeyError:
            raise ValueError('invalid range, use 125, 250, 500, 1000 or 2000')
        self.i2c.writeto_mem(self.gyro_addr, 0x0F, range_byte)
        self._resolution = (2*gyro_range)/2**16

    def get_range(self) -> int:
        '''
        Returns the gyro range.
        '''
        return int(2000/2**self.i2c.readfrom_mem(self.gyro_addr, 0x0F, 1)[0])

    def set_filter_bw(self, freq: int):
        '''
        Sets the filter bandwith to 12, 23, 32, 47, 64, 116, 230 or 523Hz.
        '''
        freqs = {12:b'\x05', 23:b'\x04', 32:b'\x07', 47: b'\x03', 64:b'\x06', 116:b'\x02', 230:b'\x01', 523:b'\x00'}
        try:
            freq_byte = freqs[freq]
        except:
            raise ValueError('invalid filter bandwith, use 12, 23, 32, 47, 64, 116, 230 or 523')
        self.i2c.writeto_mem(self.gyro_addr, 0x10, freq_byte)

    def get_filter_bw(self) -> int:
        '''
        Returns the filter bandwith.
        '''
        return {0:523,1:230,2:116,3:47,4:23,5:12,6:64,7:32}[self.i2c.readfrom_mem(self.gyro_addr, 0x10, 1)[0]]

    def compensation(self, active=None) -> bool:
        '''
        With no arguments passed, runs fast compensation.
        With boolean argument passe, activates or deactivates slow compensation.
        '''
        gyro_range = self.get_range()
        self.set_range(125)
        self.i2c.writeto_mem(self.gyro_addr, 0x37, b'\x21') # settings x0y0z1 10Hz
        self.i2c.writeto_mem(self.gyro_addr, 0x36, b'\x80') # reset
        if active is None:  # trigger fast comp
            self.i2c.writeto_mem(self.gyro_addr, 0x36, b'\x00') # deactivate slow comp
            active = False
            #print(self.i2c.readfrom_mem(self.gyro_addr, 0x36, 1))
            self.i2c.writeto_mem(self.gyro_addr, 0x36, b'\x20') # x
            sleep(0.1)
            #print(self.i2c.readfrom_mem(self.gyro_addr, 0x36, 1))
            self.i2c.writeto_mem(self.gyro_addr, 0x36, b'\x40') # y
            sleep(0.1)
            #print(self.i2c.readfrom_mem(self.gyro_addr, 0x36, 1))
            self.i2c.writeto_mem(self.gyro_addr, 0x36, b'\x60') # z
            sleep(0.1)
            #print(self.i2c.readfrom_mem(self.gyro_addr, 0x36, 1))
        elif active:        # activate slow comp
            self.i2c.writeto_mem(self.gyro_addr, 0x36, b'\x07')
        elif not active:    # deactivate slow comp
            self.i2c.writeto_mem(self.gyro_addr, 0x36, b'\x00')
        else:
            raise TypeError('pass a boolean or no argument')
        self.set_range(gyro_range)
        return active

    def x(self) -> float:
        return self._read_gyro(0x02)

    def y(self) -> float:
        return self._read_gyro(0x04)

    def z(self) -> float:
        return self._read_gyro(0x06)

    def xyz(self) -> tuple:
        return (self.x(), self.y(), self.z())
