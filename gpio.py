# coding: utf-8
'''
Python module gpio4
IMporoved gpio module based on sysfs combining with OPi.GPIO and gpio3 features
@author Hank
@page https://github.com/hankso

Want something like RPi.GPIO?
    >>> import gpio4.GPIO as GPIO
    >>> GPIO.setmode(GPIO.BOARD_orangepi_zero_plus)
    >>> GPIO.setup(12, GPIO.OUTPUT)

or call functions as you are using Arduino?
    >>> from gpio4.Arduino import *
    >>> pinMode(13, OUTPUT)
    >>> digitalWrite(13, HIGH)
    >>> if digitalRead(13):
    ...     digitalWrite(12, LOW)

or most basic and fastest sysfs class?
    >>> import gpio4
    >>> pin = gpio4.SysfsGPIO(gpio4.BOARD_nanopi[6])
    >>> pin.export = True # regist pin by sysfs, same as pinMode()
    >>> pin.direction = 'out'
    >>> print(pin.value)
    >>> pin.value = 1
'''
import os

class SysfsGPIO(object):
    attributes = ('value', 'direction', 'active_low', 'edge')
    def __init__(self, pin):
        self.pin = pin
        self.path = '/sys/class/gpio/gpio{:d}'.format(pin)
        self._file = {}

    @property
    def export(self):
        return os.path.exists(self.path)

    @property
    def value(self):
        return int(self._read('value'))

    @property
    def direction(self):
        return self._read('direction')

    @property
    def active_low(self):
        return int(self._read('active_low'))

    @property
    def edge(self):
        return self._read('edge')

    @export.setter
    def export(self, value):
        # open or reopen attr files
        # gpio pin will be registed if it is not yet
        if value:
            if not self.export:
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(str(self.pin))
            for attr in self.attributes:
                self._file[attr] = open(
                        os.path.join(self.path, attr),
                        'wb+', buffering=0)
        # close attr files
        # gpio will be unexported if it exists
        else:
            if self.export:
                with open('/sys/class/gpio/unexport', 'w') as f:
                    f.write(str(self.pin))
            for h in self._file.values():
                h.close()
            self._file.clear()

    @value.setter
    def value(self, data):
        self._write('value', data)

    @direction.setter
    def direction(self, data):
        self._write('direction', data)

    @active_low.setter
    def active_low(self, data):
        self._write('active_low', data)

    @edge.setter
    def edge(self, data):
        self._write('edge', data)

    def _read(self, attr):
        self._file[attr].seek(0)
        return self._file[attr].read().strip()

    def _write(self, attr, data):
        self._file[attr].seek(0)
        self._file[attr].write(str(data))
