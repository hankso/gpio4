# coding: utf-8
'''
@author Hank
@page https://github.com/hankso
'''
import os
import threading
from gpio4.constants import *


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
        self.IN      = INPUT
        self.OUT     = OUTPUT
        self.PULLUP  = INPUT_PULLUP
        self.PULLDN  = INPUT_PULLDN
        self.RISING  = RISING
        self.FALLING = FALLING
        self.HIGH    = HIGH
        self.LOW     = LOW
        self.BOARD   = BOARD_SUNXI
        self.BCM     = BCM
        self.VERSION = 1.0

        self._pin_dict = {}
        self._pwm_dict = {}
        self._mode = self.BOARD

    def setmode(self, m):
        self._mode = mode

    def getmode(self):
        return self._mode

    def _get_pin_num(self, pin, must_in_dict=False):
        try:
            p = self._mode[pin]
        except:
            raise KeyError(('Invalid pin({}) or unsupported mode!\n'
                            'Reset mode and check pin num.').format(pin))
        if must_in_dict and ( p not in self._pin_dict ):
            raise NameError(('Pin {} is not setup yet, please run'
                             '`GPIO.setup({}, state)` first!'
                             '').format(pin, pin))
        return p

    def _listify(self, *args, padlen=None):
        # convert all args to list and pad them to a certain length
        for arg in args:
            if not isinstance(arg, list):
                if isinstance(arg, tuple):
                    arg = list(arg)
                else:
                    arg = [arg]
            if padlen:
                if len(arg) < padlen:
                    arg += [arg[-1]] * ( padlen-len(arg) )
                elif len(arg) > padlen:
                    arg = arg[:padlen]
        return args

    def setup(self, pin, state, initial=None):
        # listify pin for multichannel operation
        pins = [self._get_pin_num(p) for p in self._listify(pin)]
        # pad state_list and initial_list in case someone
        # want to setup more than one pin at one time
        states, initials = self._listify(state, initial, padlen = len(pin))

        # register all pins and init them
        for p, s, i in zip(pins, states, initials):
            if s == self.PULLUP:
                s, i = self.IN, self.HIGH
            elif s == self.PULLDN:
                s, i = self.IN, self.LOW
            elif s not in [self.IN, self.OUT]:
                raise ValueError('Invalid state: {}!'.format(s))
            if p not in self._pin_dict:
                self._pin_dict[p] = SysfsGPIO(p)
                self._pin_dict[p].export = True
            self._pin_dict[p].direction = s
            if i in [self.HIGH, self.LOW]:
                self._pin_dict[p].value = i

    def input(self, pin):
        # single channel value
        if type(pin) not in [list, tuple]:
            return self._pin_dict[self._get_pin_num(pin, must_in_dict=True)].value
        # multichannel values
        pins = [self._get_pin_num(pin, must_in_dict=True) \
                for p in self._listify(pin)]
        return [self._pin_dict[p].value for p in pins]

    def output(self, pin, value):
        pins = [self._get_pin_num(p, must_in_dict=True) \
                for p in self._listify(pin)]
        values = self._listify(value, padlen=len(pins))
        for p, v in zip(pins, values):
            if v not in [True, False, self.HIGH, self.LOW]:
                raise ValueError('Invalid value: {}'.format(v))
            self._pin_dict[p].value = int(v)

    def cleanup(self, pin=None):
        if pin == None:
            pins = list(self._pin_dict.keys()) # py2&py3 compatiable
        else:
            pins = [self._get_pin_num(p) for p in self._listify(pin)]
        for p in pin:
            sysfsgpio = self._pin_dict.pop(p, None)
            if sysfsgpio:
                sysfsgpio.export = False
            pwm = self._pwm_dict.pop(p, None)
            if pwm:
                pwm.stop()


    def add_event_detect(self, pin, event, bouncetime=None):
        pass

    def add_event_callback(self, pin, ):
        pass

    def event_detected(self, pin):
        pass

    def wait_for_edge(self, pin, edge):
        pass

    def PWM(self, pin, frequency):
        self.setup(pin, self.OUT)
        pins = [self._get_pin_num(p) for p in self._listify(pin)]
        frequencys = self._listify(frequency)
        return_list = []
        for p, f in zip(pins, frequencys):
            self._pwm_dict[p] = PWM(self._pin_dict[p], f)
            return_list.append(self._pwm_dict[p])
        if len(pins) == 1:
            return return_list[0]
        else:
            return return_list


class PWM:
    def __init__(self, sysfsgpio, frequency):
        self.sysfsgpio = sysfsgpio
        self.ChangeFrequency(frequency)
        self._flag_stop = threading.Event()
        self.t = threading.Thread(target=self._pwm)
        self.t.setDeamon(True)

    def _pwm(self):
        while not self._flag_stop.isSet():
            self.sysfsgpio.value = 1
            time.sleep(self.high_time)
            self.sysfsgpio.value = 0
            time.sleep(self.low_time)

    def start(self, dc):
        self.ChangeDutyCycle(dc)
        self.t.start()

    def stop(self):
        self._flag_stop.set()

    def ChangeFrequency(self, frequency):
        self.frequency = frequency
        self.period = 1.0/frequency
        if hasattr(self, 'dc'):
            self.high_time = self.dc * self.period
            self.low_time = (1 - self.dc) * self.period

    def ChangeDutyCycle(self, dc):
        if dc > 1 or dc < 0:
            raise ValueError('Invalid duty cycle: {}'.format(dc))
        self.dc = dc
        self.high_time, self.low_time = dc * self.period, (1 - dc) * self.period
