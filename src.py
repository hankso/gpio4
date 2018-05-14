# coding: utf-8
'''
@author Hank
@page https://github.com/hankso
'''
import os
from gpio4 import constants


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


class _GPIO(object):
    def __init__(self):
        self._pin_dict = {}
        self.IN = 'in'
        self.OUT = 'out'
        self.PULLUP = 'pullup'
        self.PULLDN = 'pulldn'
        self.HIGH = 1
        self.LOW = 0
        self.BOARD = constants.BOARD_SUNXI
        self.BCM = constants.BOARD_BCM
        self._mode = self.BOARD
        self.VERSION = 1.0

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, m):
        self._mode = m

    def setmode(self, m):
        self._mode = mode

    def getmode(self):
        return self._mode

    def setup(self, pin, state, initial=[None]):
        # convert all args to list
        for arg in [pin, state, initial]:
            if not isinstance(arg, [list, tuple]):
                arg = [arg]
        # pad state_list and initial_list in case someone
        # want to setup more than one pin at one time
        for arg in [state, initial]:
            if len(arg) < len(pin):
                arg = list(arg) + [arg[-1]] * ( len(pin)-len(arg) )
            elif len(arg) > len(pin):
                arg = arg[:len(pin)]
        # register all pins and init them
        for p, s, i in zip(pin, state, initial):
            try:
                p = self._mode[p]
            except:
                raise NameError(('Invalid pin({}) or unsupported mode!\n'
                                 'Reset mode and check pin num.').format(p))
            if s == self.PULLUP:
                s, i = self.IN, self.HIGH
            elif s == self.PULLDN:
                s, i = self.IN, self.LOW
            elif s not in [self.IN, self.OUT]:
                raise RuntimeError('Invalid state: {}!'.format(s))
            if p not in self._pin_dict:
                self._pin_dict[p] = SysfsGPIO(p)
                self._pin_dict[p].export = True
            self._pin_dict[p].direction = s
            if i in [self.HIGH, self.LOW]:
                self._pin_dict[p].value = i

    def input(self, pin):
        p = self._mode[pin]
        if p not in self._pin_dict:
            raise RuntimeError(('Pin {} is not setup yet, please run'
                                '`GPIO.setup({}, state)` first!').format(pin))
        return self._pin_dict[p].value

    def output(self, pin, value):
        for arg in [pin, value]:
            if not isinstance(arg, [list, tuple]):
                arg = [arg]
        if len(value) < len(pin):
            value = list(value) + [value[-1]] * ( len(pin)-len(value) )
        elif len(value) > len(pin):
            value = value[:len(pin)]
        for p, v in zip(pin, value):
            try:
                p = self._mode[p]
            except:
                raise NameError(('Invalid pin({}) or unsupported mode!\n'
                                 'Reset mode and check pin num.').format(p))
            if p not in self._pin_dict:
                raise RuntimeError(('Pin {} is not setup yet, please run'
                                    '`GPIO.setup({}, state)` first!'
                                    '').format(pin))
            if v not in [True, False, self.HIGH, self.LOW, 1, 0]:
                raise RuntimeError('Invalid value: {}'.format(v))
            self._pin_dict[p].value = int(v)

    def cleanup(self, pin=None):
        if pin == None:
            pin = list(self._pin_dict.keys()) # py2&py3 compatiable
        else:
            if not isinstance(pin, [list, tuple]):
                pin = [pin]
            try:
                pin = [self._mode[p] for p in pin]
            except:
                raise NameError(('Invalid pin({}) or unsupported mode!\n'
                                 'Reset mode and check pin num.').format(p))
        for p in pin:
            self._pin_dict.pop(p, None)


GPIO = _GPIO()
