#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 3 16:36:26 2018

@author: hank
@page:   https://github.com/hankso


This gpio module is implemented on the basis of Sysfs gpio interface.
What is Sysfs?
Sysfs is a gpio access that been exposed to user space by kernel.

Paths in Sysfs
--------------
There are three kinds of entry in /sys/class/gpio:

   -	Control interfaces used to get userspace control over GPIOs;

   -	GPIOs themselves; and

   -	GPIO controllers ("gpio_chip" instances).

That's in addition to standard files including the "device" symlink.

The control interfaces are write-only:

    /sys/class/gpio/

    	"export" ... Userspace may ask the kernel to export control of
		a GPIO to userspace by writing its number to this file.

		Example:  "echo 19 > export" will create a "gpio19" node
		for GPIO #19, if that's not requested by kernel code.

    	"unexport" ... Reverses the effect of exporting to userspace.

		Example:  "echo 19 > unexport" will remove a "gpio19"
		node exported using the "export" file.

GPIO signals have paths like /sys/class/gpio/gpio42/ (for GPIO #42)
and have the following read/write attributes:

    /sys/class/gpio/gpioN/

	"direction" ... reads as either "in" or "out".  This value may
		normally be written.  Writing as "out" defaults to
		initializing the value as low.  To ensure glitch free
		operation, values "low" and "high" may be written to
		configure the GPIO as an output with that initial value.

		Note that this attribute *will not exist* if the kernel
		doesn't support changing the direction of a GPIO, or
		it was exported by kernel code that didn't explicitly
		allow userspace to reconfigure this GPIO's direction.

	"value" ... reads as either 0 (low) or 1 (high).  If the GPIO
		is configured as an output, this value may be written;
		any nonzero value is treated as high.

		If the pin can be configured as interrupt-generating interrupt
		and if it has been configured to generate interrupts (see the
		description of "edge"), you can poll(2) on that file and
		poll(2) will return whenever the interrupt was triggered. If
		you use poll(2), set the events POLLPRI and POLLERR. If you
		use select(2), set the file descriptor in exceptfds. After
		poll(2) returns, either lseek(2) to the beginning of the sysfs
		file and read the new value or close the file and re-open it
		to read the value.

	"edge" ... reads as either "none", "rising", "falling", or
		"both". Write these strings to select the signal edge(s)
		that will make poll(2) on the "value" file return.

		This file exists only if the pin can be configured as an
		interrupt generating input pin.

	"active_low" ... reads as either 0 (false) or 1 (true).  Write
		any nonzero value to invert the value attribute both
		for reading and writing.  Existing and subsequent
		poll(2) support configuration via the edge attribute
		for "rising" and "falling" edges will follow this
		setting.

GPIO controllers have paths like /sys/class/gpio/gpiochip42/ (for the
controller implementing GPIOs starting at #42) and have the following
read-only attributes:

    /sys/class/gpio/gpiochipN/

    	"base" ... same as N, the first GPIO managed by this chip

    	"label" ... provided for diagnostics (not always unique)

    	"ngpio" ... how many GPIOs this manges (N to N + ngpio - 1)

Board documentation should in most cases cover what GPIOs are used for
what purposes.  However, those numbers are not always stable; GPIOs on
a daughtercard might be different depending on the base board being used,
or other cards in the stack.  In such cases, you may need to use the
gpiochip nodes (possibly in conjunction with schematics) to determine
the correct GPIO number to use for a given signal.
"""
import os
import threading
import select
from . import constants


class SysfsGPIO(object):
    attributes = ('value', 'direction', 'active_low', 'edge')

    def __init__(self, pin):
        self.pin = pin
        self.path = '/sys/class/gpio/gpio{:d}'.format(pin)
        self._file = {}
        self._write_lock = threading.Lock()
        self._read_lock = threading.Lock()

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
            for h in list(self._file.values()):
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

    def fileno(self, attr='value'):
        return self._file[attr].fileno()

    def _read(self, attr):
        with self._read_lock:
            self._file[attr].seek(0)
            value = self._file[attr].read().strip()
        return value

    def _write(self, attr, data):
        with self._write_lock:
            self._file[attr].seek(0)
            self._file[attr].write(str(data))


class _GPIO(object):
    def __init__(self):
        self.IN = constants.INPUT
        self.OUT = constants.OUTPUT
        # self.PULLUP = constants.INPUT_PULLUP
        # self.PULLDN = constants.INPUT_PULLDN
        self.HIGH = constants.HIGH
        self.LOW = constants.LOW
        self.RISING = constants.RISING
        self.FALLING = constants.FALLING
        self.BOTH = constants.CHANGE
        self.BOARD = constants.BOARD_SUNXI
        self.BCM = constants.BCM
        self.VERSION = 1.0

        self._mode = self.BOARD  # default mode
        self._pin_dict = {}
        self._pwm_dict = {}
        self._irq_dict = {}
        self._flag_interrupts = threading.Event()
        self._epoll = select.epoll()

    def _time_ms(self):
        return time.time() * 1000

    def _get_pin_num(self, pin, must_in_dict=False):
        try:
            p = self._mode[pin]
        except:
            raise KeyError(('Invalid pin({}) or unsupported mode!\n'
                            'Reset mode and check pin num.').format(pin))
        if must_in_dict and (p not in self._pin_dict):
            raise NameError(('Pin {} is not setup yet, please run'
                             '`GPIO.setup({}, state)` first!'
                             '').format(pin, pin))
        return p

    def _listify(self, *args, **kwargs):
        # convert all args to list and pad them to a certain length
        args = list(args) # tuple to list
        for i, arg in enumerate(args):
            if not isinstance(arg, list):
                if isinstance(arg, tuple):
                    args[i] = list(arg)
                else:
                    args[i] = [arg]
            if 'padlen' in kwargs:
                padlen = kwargs['padlen']
                if len(args[i]) < padlen:
                    args[i] += [args[i][-1]] * (padlen - len(args[i]))
                elif len(args[i]) > padlen:
                    args[i] = args[i][:padlen]
        if len(args) == 1:
            return args[0]
        return args

    def setup(self, pin, state, initial=None):
        # listify pin for multichannel operation
        pins = [self._get_pin_num(p) for p in self._listify(pin)]
        # pad state_list and initial_list in case someone
        # want to setup more than one pin at one time
        states, initials = self._listify(state, initial, padlen=len(pin))

        # register all pins and init them
        for p, s, i in zip(pins, states, initials):
            # if s == self.PULLUP:
            #     s, i = self.IN, self.HIGH
            # elif s == self.PULLDN:
            #     s, i = self.IN, self.LOW
            if s not in [self.IN, self.OUT]:
                raise ValueError('Invalid state: {}!'.format(s))
            if p not in self._pin_dict:
                self._pin_dict[p] = SysfsGPIO(p)
                self._pin_dict[p].export = True
            self._pin_dict[p].direction = s
            if s == self.OUT and i in [self.HIGH, self.LOW]:
                self._pin_dict[p].value = i

    def input(self, pin):
        # single channel value
        if type(pin) not in [list, tuple]:
            return self._pin_dict[
                self._get_pin_num(pin, must_in_dict=True)].value
        # multichannel values
        pins = [self._get_pin_num(pin, must_in_dict=True)
                for p in self._listify(pin)]
        return [self._pin_dict[p].value for p in pins]

    def output(self, pin, value):
        pins = [self._get_pin_num(p, must_in_dict=True)
                for p in self._listify(pin)]
        values = self._listify(value, padlen=len(pins))
        for p, v in zip(pins, values):
            if v not in [True, False, self.HIGH, self.LOW]:
                raise ValueError('Invalid value: {}'.format(v))
            self._pin_dict[p].value = int(v)

    def cleanup(self, pin=None):
        if pin is None:
            pins = list(self._pin_dict.keys())  # py2&py3 compatiable
        else:
            pins = [self._get_pin_num(p) for p in self._listify(pin)]
        for p in pins:
            pin = self._pin_dict.pop(p, None)
            if pin:
                pin.export = False
            pwm = self._pwm_dict.pop(p, None)
            if pwm:
                pwm.clear()
            irq = self._irq_dict.pop(p, None)
            if irq:
                irq['flag_stop'].set()
                irq['flag_triggered'].clear()

    def enable_interrupts(self):
        if hasattr(self, '_thread_irq'):
            self._flag_interrupts_pause.clear()
            return
        self._thread_irq = threading.Thread(target=self._handle_interrupts)
        self._thread_irq.setDeamon(True)
        self._thread_irq.start()

    def disable_interrupts(self):
        self._flag_interrupts_pause.set()

    def close_interrupts(self):
        self._flag_interrupts_stop.set()

    def _handle_interrupts(self):
        while not self._flag_interrupts_stop.isSet():
            self._flag_interrupts_pause.wait()
            rst = self._epoll.poll(timeout=1)
            if not rst:
                continue
            for fd, event in rst:
                for p in self._irq_dict:
                    if self._irq_dict[p]['fd'] == fd:
                        bouncetime = self._irq_dict[p]['bouncetime']
                        break
                if bouncetime:
                    time.sleep(bouncetime / 1000.0)
                    edge, value = self._pin_dict[p].edge, self._pin_dict[p].value
                    if (edge == self.RISING and value != self.HIGH) \
                    or (edge == self.FALLING and value != self.LOW):
                        continue
                self._irq_dict[p]['interrupted'].set()
                for c in self._irq_dict[p]['callbacks']:
                    try:
                        c(self._irq_dict[p]['pin_name'])
                    except:
                        pass
        print('[GPIO interrupts handler] shutdown')

    def add_event_detect(self, pin, edge, func=None, bouncetime=None):
        p = self._get_pin_num(pin, must_in_dict=True)
        if edge not in [self.RISING, self.FALLING, self.BOTH]:
            raise ValueError('Invalid edge: {}'.format(edge))
        if p in self._irq_dict:
            raise NameError(('Pin {} is already been attached to an interrupt '
                             'on {} edge, if you want to reset it, please run '
                             '`GPIO.remove_event_detect({})` first'
                             '').format(pin, self._pin_dict[p].edge, pin))
        self._pin_dict[p].direction = 'in'
        self._pin_dict[p].edge = edge
        fd = self._pin_dict[p].fileno('value')
        self._irq_dict[p] = {
            'fd': fd, 'interrupted': threading.Event(), 'pin_name': pin,
            'bouncetime': bouncetime if bouncetime is not None else 0,
            'callbacks': self._listify(func) if func is not None else []
        }
        self._epoll.register(fd, select.EPOLLPRI | select.EPOLLET)

    def remove_event_detect(self, pin):
        p = self._get_pin_num(pin, must_in_dict=True)
        if p in self._irq_dict:
            self._epoll.unregister(self._irq_dict[p]['fd'])
            self._irq_dict.remove(p)

    def add_event_callback(self, pin, callback):
        p = self._get_pin_num(pin, must_in_dict=True)
        if p not in self._irq_dict:
            raise NameError(('Pin {} is not initialized with edge yet, please '
                             'run `GPIO.add_event_detect({}, edge)` first'
                             '').format(pin, pin))
        self._irq_dict[p]['callbacks'] += self._listify(callback)

    def wait_for_edge(self, pin, edge, timeout=constants.FOREVER_ms):
        p = self._get_pin_num(pin, must_in_dict=True)
        if edge not in [self.RISING, self.FALLING, self.BOTH]:
            raise ValueError('Invalid edge: {}'.format(edge))
        if p in self._irq_dict and edge != self._pin_dict[p].edge:
            raise NameError(('Pin {} is already been attached to an interrupt '
                             'on {} edge, if you want to reset it, please run '
                             '`GPIO.remove_event_detect({})` first'
                             '').format(pin, self._pin_dict[p].edge, pin))
        start = self._time_ms()
        while not self._irq_dict[p]['interrupted'].isSet():
            if (self._time_ms() - start) > timeout:
                return None
            time.sleep(1.0/10)  # sensibility: refresh 10 times per second
        self._irq_dict[p]['interrupted'].clear()
        return pin

    def setmode(self, m):
        self._mode = mode

    def getmode(self):
        return self._mode

    def PWM(self, pin, frequency=None):
        '''
        if pin is already initialized before:
            if frequency provided:
                update frequency and return PWM instance
            else:
                return PWM instance with no operation
        else:
            if frequency provided:
                initialize with this frequency and return PWM instance
            else:
                initialize with 1Hz(default) and return PWM instance
        '''
        pins = [self._get_pin_num(p) for p in self._listify(pin)]
        frequencys = self._listify(frequency, padlen = len(pins))
        return_list = []
        for p, f in zip(pins, frequencys):
            if p not in self._pwm_dict:
                self.setup(self._listify(pin)[pins.index(p)], self.OUT)
                if f is None:
                    raise NameError(('PWM on pin {} is not initialized yet, '
                                     'please provide pin num and freq'
                                     '').format(p))
                self._pwm_dict[p] = _PWM(self._pin_dict[p], f)
            elif f:
                self._pwm_dict[p].ChangeFrequency(f)
            return_list.append(self._pwm_dict[p])
        if len(pins) == 1:
            return return_list[0]
        else:
            return return_list

GPIO = _GPIO()

class _PWM:
    def __init__(self, sysfsgpio, frequency):
        self._sysfsgpio = sysfsgpio
        self.ChangeFrequency(frequency)
        self._flag_pause = threading.Event()
        self._flag_stop = threading.Event()
        self._t = threading.Thread(target=self._pwm)
        self._t.setDeamon(True)
        self._t.start()

    def _pwm(self):
        while not self._flag_stop.isSet():
            self._flag_pause.wait()
            self._sysfsgpio.value = 1
            time.sleep(self._high_time)
            self._sysfsgpio.value = 0
            time.sleep(self._low_time)

    def start(self, dc):
        self.ChangeDutyCycle(dc)
        self._flag_pause.set()

    def stop(self):
        self._flag_pause.clear()

    def ChangeFrequency(self, frequency):
        if frequency <= 0:
            raise ValueError('Invalid frequency: {}'.format(frequency))
        self._frequency = frequency
        self._period = 1.0/frequency
        if hasattr(self, 'dc'):
            self._high_time = self._dc * self._period
            self._low_time = (1 - self._dc) * self._period

    def ChangeDutyCycle(self, dc):
        if dc > 100 or dc < 0:
            raise ValueError('Invalid duty cycle: {}'.format(dc))
        self._dc = float(dc) / 100
        self._high_time = dc * self._period
        self._low_time = (1 - dc) * self._period

    def clear(self):
        self.stop()
        self._flag_stop.set()


from . import arduino

__all__ = ['arduino', 'constants', 'GPIO', 'SysfsGPIO']
